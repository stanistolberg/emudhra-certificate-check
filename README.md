# eMudhra Certificate Check

Entwickelt von **Stanislav Stolberg**.

[![Checks](https://github.com/stanistolberg/emudhra-certificate-check/actions/workflows/checks.yml/badge.svg)](https://github.com/stanistolberg/emudhra-certificate-check/actions/workflows/checks.yml)

Ein rein lesender TLS-Check für macOS und Linux zum eMudhra-CA-Vorfall vom Oktober 2026. Das Skript kombiniert Verbindungstests gegen vier Testketten, SHA-256-Prüfungen von CA-Bundles und Versionsabgleiche. Es zeigt Befunde und Reparaturhinweise; es installiert nichts und ändert keine Zertifikatsspeicher.

## Anwendung

[Bash-Skript herunterladen](https://github.com/stanistolberg/emudhra-certificate-check/blob/main/certificate-check-v6.sh) oder das Repository klonen:

```bash
git clone https://github.com/stanistolberg/emudhra-certificate-check.git
cd emudhra-certificate-check
shasum -a 256 -c SHA256SUMS
bash certificate-check-v6.sh
```

Zusätzliche Projektumgebungen und deaktivierte TLS-Prüfung suchen:

```bash
bash certificate-check-v6.sh --scan /pfad/zum/projekt
bash certificate-check-v6.sh --help
```

Keine Administratorrechte nötig. Das Skript kontaktiert öffentliche eMudhra-Testserver sowie `pypi.org` und `github.com`. Prüfausgaben können lokale Pfade und Softwareversionen enthalten; vor dem Teilen prüfen.

## Ergebnisse

| Status | Bedeutung |
| --- | --- |
| `OK` | Jeweilige Prüfung bestanden; bei TLS: vier Ketten abgelehnt und Kontrollserver erreichbar |
| `VERSION_OK` | Versionsabgleich bestanden; kein TLS-Nachweis für diese Anwendung |
| `VULNERABLE` | Betroffene Kette akzeptiert oder problematische CA im geprüften Bundle vorhanden |
| `OUTDATED` | Veraltet oder manuell zu prüfen |
| `INCONCLUSIVE` / `BROKEN` | Unvollständig bzw. nicht ausführbar |

Exit-Codes: `0` bestanden, `1` verwundbar, `2` Aufruffehler, `3` unvollständig/defekt, `4` veraltet oder Review nötig.

## Grenzen und Prüfung

Gezielte TLS-Diagnose, kein vollständiger Sicherheitscheck oder Nachweis einer Kompromittierung. Erkannte Werkzeuge werden geprüft; Browser, Container und Windows sind nicht vollständig abgedeckt. Versionsgrenzen sind eine Momentaufnahme vom **24.10.2026** und müssen vor späterer Nutzung abgeglichen werden. Keine bestätigte Unternehmensfreigabe.

GitHub Actions prüft Bash-Syntax, ShellCheck und Regressionstests auf macOS und Linux. Diese Codeprüfungen sind von einem Live-Scan des eigenen Rechners getrennt. Lokal: `python3 tests/check.py`; zusätzlich `shellcheck certificate-check-v6.sh`.

Grundlagen: [Incident-Seite und Testketten](https://emudhra.we-have-a-problem.com/), [Apple-Hinweise](https://support.apple.com/en-us/149555). Mit KI-Unterstützung überarbeitet und geprüft.
