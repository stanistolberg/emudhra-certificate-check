# eMudhra Certificate Check

Entwickelt von **Stanislav Stolberg**.

[![Checks](https://github.com/stanistolberg/emudhra-certificate-check/actions/workflows/checks.yml/badge.svg)](https://github.com/stanistolberg/emudhra-certificate-check/actions/workflows/checks.yml)

Ein rein lesender TLS-Check für macOS/Linux (Bash) und Windows (PowerShell) zum eMudhra-CA-Vorfall vom Oktober 2026. Das Skript kombiniert Verbindungstests gegen vier Testketten, SHA-256-Prüfungen von CA-Bundles und Versionsabgleiche. Es zeigt Befunde und Reparaturhinweise; es installiert nichts und ändert keine Zertifikatsspeicher.

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

## Windows: prüfen und gezielt aktualisieren

PowerShell 5.1 oder 7, im heruntergeladenen Repository:

```powershell
.\windows\Test-Emudhra.ps1
```

Windows/.NET und `curl.exe` erhalten Live-TLS-Tests; Git, Node, uv und ausgewählte Desktop-Apps einen Versionsabgleich. Eigene Python-/Java-CA-Bundles und Projektumgebungen sind im Windows-Einstieg nicht vollständig abgedeckt.

Für ausgewählte, bereits installierte Anwendungen zunächst den Updateplan anzeigen; erst `-Apply` startet WinGet:

```powershell
.\windows\Update-EmudhraWindows.ps1 -PackageId Git.Git,Microsoft.VisualStudioCode
.\windows\Update-EmudhraWindows.ps1 -PackageId Git.Git,Microsoft.VisualStudioCode -Apply
```

`-Apply -WhatIf` simuliert den Start. Nur freigegebene Paket-IDs sind zulässig; kein pauschales `--all`, kein Umgehen von Hashprüfungen oder Ausführungsrichtlinien. WinGet muss vorhanden sein. Paketupdates können Majorversionen ändern; Auswahl vorab prüfen. Anschließend den Check erneut ausführen.

Windows selbst über **Einstellungen → Windows Update** bzw. den zentralen Unternehmenskanal aktualisieren. Microsoft verteilt die Zertifikatssperren über Trust-List-Updates; Anwendungen mit eigenen CA-Bundles benötigen zusätzliche Pflege. Die Skripte verändern keine Windows-Zertifikatsspeicher. Bestehende Unternehmensrichtlinien und Anforderungen an signierte Skripte bleiben maßgeblich. [Windows-Hintergrund](https://emudhra.we-have-a-problem.com/#windows), [WinGet-Dokumentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/upgrade).

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

Gezielte TLS-Diagnose, kein vollständiger Sicherheitscheck oder Nachweis einer Kompromittierung. Erkannte Werkzeuge werden geprüft; Browser, Container und unabhängige Trust-Stores sind nicht vollständig abgedeckt. Versionsgrenzen sind eine Momentaufnahme vom **24.10.2026** und müssen vor späterer Nutzung abgeglichen werden. Keine bestätigte Unternehmensfreigabe.

GitHub Actions prüft Bash auf macOS/Linux und Windows-Code auf Windows mit PowerShell 5.1 und 7. Dazu kommen ShellCheck, PSScriptAnalyzer sowie Offline-Regressionstests einschließlich einer realen TLS-Ablehnung und isolierter Update-Simulationen. Diese Codeprüfungen sind von einem Live-Scan des eigenen Rechners getrennt. Lokal: `python3 tests/check.py`; zusätzlich `shellcheck certificate-check-v6.sh`.

Grundlagen: [Incident-Seite und Testketten](https://emudhra.we-have-a-problem.com/), [Apple-Hinweise](https://support.apple.com/en-us/149555). Mit KI-Unterstützung überarbeitet und geprüft.
