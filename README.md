# eMudhra Certificate Check

Entwickelt von **Stanislav Stolberg** für die technische Bewertung des eMudhra-CA-Vorfalls vom Oktober 2026.

[![Checks](https://github.com/stanistolberg/emudhra-certificate-check/actions/workflows/checks.yml/badge.svg)](https://github.com/stanistolberg/emudhra-certificate-check/actions/workflows/checks.yml)

Das Werkzeug prüft, ob ausgewählte TLS-Clients betroffene Zertifikatsketten noch akzeptieren. Es liefert Befunde und Handlungshinweise für Security Professionals. Der **Check arbeitet lesend** und verändert keine Zertifikatsspeicher. Ein **separater Windows-Updater** aktualisiert ausdrücklich ausgewählte Anwendungen erst mit `-Apply`.

## Schnellstart

[ZIP herunterladen](https://github.com/stanistolberg/emudhra-certificate-check/archive/refs/heads/main.zip), entpacken und ein Terminal bzw. PowerShell **im entpackten Repository-Ordner** öffnen. Alternativ: `git clone https://github.com/stanistolberg/emudhra-certificate-check.git` und `cd emudhra-certificate-check`.

**macOS / Linux — Bash:**

```bash
shasum -a 256 -c SHA256SUMS
bash certificate-check-v6.sh
```

**Windows — PowerShell 5.1 oder 7:**

```powershell
.\windows\Test-Emudhra.ps1
```

Der Check benötigt keine Administratorrechte. Er kann mehrere Minuten dauern. Bei einer Ausführungssperre die betriebliche Freigabe bzw. erforderliche Signierung klären; Ausführungsrichtlinien bleiben bestehen.

Optional unter macOS/Linux zusätzliche Python-Projektumgebungen und Hinweise auf deaktivierte TLS-Verifikation suchen:

```bash
bash certificate-check-v6.sh --scan "/pfad/zum/projekt"
bash certificate-check-v6.sh --help
```

`--scan` ist mehrfach möglich; Virtualenvs werden bis Tiefe 6 gesucht. Quelltexttreffer zeigen nur Dateiname und Zeile, keinen Quelltext. Prüfausgaben können lokale Pfade und Softwareversionen enthalten; vor dem Teilen prüfen.

## Prüfumfang

| Plattform | Live-TLS-Tests | Weitere Prüfungen |
| --- | --- | --- |
| macOS / Linux | curl, Git, entdeckte Python-Interpreter, requests, Node; Java mit Compiler | SHA-256 der betroffenen Wurzeln in gefundenen CA-Bundles; ausgewählte Laufzeit- und App-Versionen |
| Windows | Windows/.NET und `curl.exe` | Git, Node, uv und ausgewählte Desktop-Apps per Version |

Live-Tests kontaktieren vier öffentliche Incident-Testserver, `pypi.org` und beim Bash-Git-Test `github.com`. Es werden keine lokalen Prüfberichte hochgeladen. curl ignoriert `.curlrc`; Python folgt keinen HTTP-Weiterleitungen und sendet keine `.netrc`-Zugangsdaten. Git übernimmt gezielt TLS-/Proxy-Einstellungen, unterdrückt weitere Benutzerkonfiguration, Zugangsdaten, Cookies und URL-Umschreibungen. Proxy-/CA-Umgebungsvariablen gelten weiterhin; Windows/.NET verbindet direkt. Proxyfilter können die Aussagekraft beeinflussen.

## Windows-Anwendungen aktualisieren

WinGet muss verfügbar sein. Zunächst den Plan prüfen, anschließend dieselbe Auswahl anwenden:

```powershell
.\windows\Update-EmudhraWindows.ps1 -PackageId Git.Git,Microsoft.VisualStudioCode
.\windows\Update-EmudhraWindows.ps1 -PackageId Git.Git,Microsoft.VisualStudioCode -Apply
.\windows\Test-Emudhra.ps1
```

`-Apply -WhatIf` simuliert den Start; `-Help` zeigt alle unterstützten Paket-IDs. Nur ausgewählte, bereits installierte Pakete werden aktualisiert. WinGet kann zusätzliche Abhängigkeiten aktualisieren oder Installationsdialoge anzeigen; Paketupdates können Majorversionen ändern. Kein pauschales `--all`, keine Umgehung von Hashprüfungen.

Windows selbst über **Einstellungen → Windows Update** bzw. den zentralen Unternehmenskanal pflegen. Microsoft verteilt Zertifikatssperren über Trust-List-Updates; Anwendungen mit eigenen CA-Bundles benötigen zusätzliche Pflege. Die Skripte ändern keine Windows-Zertifikatsspeicher. [Windows-Hintergrund](https://emudhra.we-have-a-problem.com/#windows), [WinGet-Dokumentation](https://learn.microsoft.com/en-us/windows/package-manager/winget/upgrade).

## Ergebnisse

| Status | Bedeutung |
| --- | --- |
| `OK` | Jeweilige Prüfung bestanden; bei TLS: alle vier Ketten abgelehnt und Kontrollserver erreichbar |
| `VERSION_OK` | Versionsabgleich bestanden; kein Live-TLS-Nachweis für diese Anwendung |
| `VULNERABLE` | Betroffene Kette akzeptiert oder problematische CA im geprüften Bundle vorhanden |
| `OUTDATED` | Veraltet oder manuell zu prüfen |
| `INCONCLUSIVE` / `BROKEN` | Unvollständig bzw. nicht ausführbar; Ursache prüfen und erneut starten |

**Check-Exit-Codes:** `0` bestanden, `1` verwundbar, `2` Aufruffehler, `3` unvollständig/defekt, `4` veraltet oder Review nötig. Verwundbare Befunde haben Vorrang vor unvollständigen Prüfungen.

**Updater-Exit-Codes:** `0` Plan/Simulation bzw. ausgewählte Updates abgeschlossen, `2` Aufruffehler, `3` Updatefehler, `4` kein anwendbares Update. WinGet verwendet den letzten Fall auch bei unbekannten Versionen oder Einschränkungen; er beweist keinen Schutz. Die WinGet-Ausgabe prüfen und den Check wiederholen. [Microsoft-Implementierung](https://github.com/microsoft/winget-cli/blob/master/src/AppInstallerCLICore/Workflows/UpdateFlow.cpp).

## Grenzen und Codeprüfung

Gezielte TLS-Diagnose; kein Nachweis, dass ein Rechner frei von Kompromittierung ist. Browser, Container und unabhängige Trust-Stores sind nicht vollständig abgedeckt. Unter Windows werden eigene Python-/Java-CA-Bundles und Projektumgebungen nicht untersucht. Versionsgrenzen: **24.10.2026**; vor späterer Nutzung mit den Quellen abgleichen. Für einen Einsatz bei OVB ist die interne Bewertung/Freigabe erforderlich.

GitHub Actions prüft Bash auf macOS/Linux und Windows-Code mit PowerShell 5.1 und 7: Syntax, ShellCheck, PSScriptAnalyzer, Regressionstests, reale lokale TLS-Ablehnung sowie isolierte Update-Simulationen. Die CI installiert keine Anwendungsupdates auf dem eigenen Rechner und ersetzt keinen Live-Scan.

Lokale Tests: `python3 tests/check.py`, `shellcheck certificate-check-v6.sh`; unter Windows `./tests/windows.ps1` (Python und OpenSSL erforderlich).

<details>
<summary>SHA-256-Prüfung unter Windows</summary>

Im Repository-Ordner ausführen; bei einer Abweichung das Paket erneut beziehen:

```powershell
foreach ($line in Get-Content SHA256SUMS) {
    $parts = $line -split '  ', 2
    if ((Get-FileHash -Algorithm SHA256 $parts[1]).Hash -ne $parts[0]) {
        throw ('Checksum mismatch: ' + $parts[1])
    }
}
```

Die Prüfsummen erkennen Dateiänderungen; sie sind keine digitale Signatur.
</details>

Grundlagen: [Incident-Seite und Testketten](https://emudhra.we-have-a-problem.com/), [Apple-Hinweise](https://support.apple.com/en-us/149555). Mit KI-Unterstützung überarbeitet und geprüft.
