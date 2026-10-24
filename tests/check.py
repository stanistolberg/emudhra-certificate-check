#!/usr/bin/env python3
"""Offline regression checks for diagnostics, malformed input and redacted output."""
import base64
import hashlib
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'certificate-check-v6.sh'
SOURCE = SCRIPT.read_text()
ROOTS = re.search(r'^DISTRUSTED_ROOTS="(.*?)"', SOURCE, re.M | re.S).group(1)
PROBE = SOURCE.split("<<'PY'\n", 1)[1].split('\nPY\n', 1)[0]
FIXTURES = ROOT / 'tests' / 'fixtures'


def function(name):
    return re.search(r'^' + re.escape(name) + r'\(\) \{.*?^\}', SOURCE, re.M | re.S).group(0)


def bash(code, *args, timeout=10):
    return subprocess.run(['bash', '-c', code, '--', *args], capture_output=True,
                          text=True, timeout=timeout)


class Diagnostics(unittest.TestCase):
    def test_help_is_available_without_network(self):
        p = subprocess.run(['bash', str(SCRIPT), '--help'], capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 0)
        self.assertIn('read-only', p.stdout)

    def test_invalid_cli_is_usage_error(self):
        for args in (['--unknown'], ['--scan'], ['--scan', '/nonexistent-emudhra-test']):
            with self.subTest(args=args):
                p = subprocess.run(['bash', str(SCRIPT), *args], capture_output=True, timeout=5)
                self.assertEqual(p.returncode, 2)

    def test_verdicts(self):
        cases = [(['4', '0', '0', '1'], 'OK'),
                 (['3', '1', '0', '1'], 'VULNERABLE'),
                 (['3', '0', '1', '1'], 'INCONCLUSIVE'),
                 (['4', '0', '0', '0'], 'INCONCLUSIVE'),
                 (['5', '0', '0', '1'], 'INCONCLUSIVE'),
                 (['garbage', '0', '0', '1'], 'INCONCLUSIVE'),
                 ([], 'INCONCLUSIVE')]
        for args, expected in cases:
            with self.subTest(args=args):
                p = bash('NH=4\n' + function('verdict') + '\nverdict "$@"', *args)
                self.assertEqual(p.returncode, 0, p.stderr)
                self.assertEqual(p.stdout.strip(), expected)

    def test_summary_exit_codes(self):
        # Run the actual summary gates, without probing the host or network.
        gates = SOURCE[SOURCE.rindex('[ "$VULN" -gt 0 ] && exit 1'):]
        for vulnerable, inconclusive, warnings, expected in ((0, 0, 0, 0), (1, 0, 0, 1),
                                                           (0, 1, 0, 3), (0, 0, 1, 4), (1, 1, 1, 1)):
            with self.subTest(expected=expected):
                p = bash(f'VULN={vulnerable}; INCONC={inconclusive}; WARN={warnings}\n' + gates)
                self.assertEqual(p.returncode, expected)

    def test_timeout_has_no_delayed_command_substitution(self):
        start = time.monotonic()
        p = bash(function('run_timed') + '\nout=$(run_timed 20 printf done); printf "%s" "$out"', timeout=5)
        self.assertEqual(p.stdout, 'done')
        self.assertLess(time.monotonic() - start, 5)

    def test_timeout_terminates_stalled_command(self):
        p = bash(function('run_timed') + '\nrun_timed 1 sleep 20', timeout=6)
        self.assertNotEqual(p.returncode, 0)


class Bundles(unittest.TestCase):
    def check_bundles(self, contents):
        with tempfile.TemporaryDirectory() as d:
            probe = Path(d) / 'probe.py'
            probe.write_text(PROBE)
            paths = []
            for i, value in enumerate(contents):
                p = Path(d) / f'bundle-{i}.pem'
                p.write_text(value)
                paths.append(str(p))
            env = dict(os.environ, DISTRUSTED_ROOTS=ROOTS)
            out = subprocess.run([sys.executable, '-I', str(probe), '--bundles', *paths],
                                 env=env, capture_output=True, text=True, check=True, timeout=10)
            return [line.split('\t')[1] for line in out.stdout.splitlines()]

    def test_public_affected_fixture_identity(self):
        import ssl
        der = ssl.PEM_cert_to_DER_cert((FIXTURES / 'emsign-ecc-g3.pem').read_text())
        self.assertEqual(hashlib.sha256(der).hexdigest(),
                         '86a1ecba089c4a8d3bbe2734c612ba341d813e043cf9e8a862cd5c57a36bbe6b')

    def test_affected_and_clean_bundles(self):
        self.assertEqual(self.check_bundles([(FIXTURES / 'emsign-ecc-g3.pem').read_text(),
                                            (FIXTURES / 'control-root.pem').read_text()]),
                         ['emSign-ECC-G3', 'clean'])

    def test_empty_invalid_and_mixed_bundles_never_pass(self):
        invalid = '-----BEGIN CERTIFICATE-----\n' + base64.b64encode(b'not X.509').decode() + '\n-----END CERTIFICATE-----\n'
        mixed = (FIXTURES / 'control-root.pem').read_text() + invalid
        self.assertEqual(self.check_bundles(['', invalid, mixed]), ['empty', 'empty', 'empty'])

    def test_openssl_fallback_rejects_partial_parse(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'mixed.pem'
            p.write_text((FIXTURES / 'control-root.pem').read_text() +
                         '\n-----BEGIN CERTIFICATE-----\nbm90IFguNTA5\n-----END CERTIFICATE-----\n')
            (Path(d) / 'distrusted.txt').write_text(ROOTS + '\n')
            code = 'set -o pipefail\nTMP=$1\n' + function('roots_in_fps') + '\n' + function('bundle_roots_openssl')
            out = bash(code + '\nbundle_roots_openssl "$2"', d, str(p))
            self.assertEqual(out.stdout.strip(), 'empty', out.stderr)


class Redaction(unittest.TestCase):
    def run_scan(self, root, tmp):
        start = SOURCE.index('    scan_status=0\n')
        end = SOURCE.index('    hits=$(wc -l', start)
        code = ('set -o pipefail\nTMP=$1\nd=$2\n'
                'row(){ printf "%s\\n" "$1"; }\n' + SOURCE[start:end] + '\ncat "$TMP/insecure"')
        return bash(code, str(tmp), str(root))

    def test_source_content_is_redacted_and_spaces_work(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'source'; root.mkdir()
            p = root / 'settings with spaces.py'
            p.write_text('verify=False; SECRET="must-not-be-printed"\n')
            out = self.run_scan(root, Path(d))
            self.assertEqual(out.stdout.strip(), str(p) + ':1')
            self.assertNotIn('SECRET', out.stdout)
            self.assertNotIn('must-not-be-printed', out.stdout)

    def test_empty_scan_has_no_error(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'source'; root.mkdir()
            self.assertEqual(self.run_scan(root, Path(d)).stdout.strip(), '')

    def test_unreadable_root_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertIn('INCONCLUSIVE', self.run_scan(Path(d) / 'missing', Path(d)).stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
