# =============================================================================
# Thema: Bash-Skripte Grundlagen  (Kategorie: Praxis)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# Vergleich zu Python/C++/C#: Tab "Programmieren"
# =============================================================================

THEMA = {
    "titel": "Bash-Skripte: Grundlagen",
    "reihenfolge": 2,
    "kurz": "Befehle, die man oft braucht, in eine Datei schreiben – mit Variablen, if, for und Fehlerprüfung.",
    "stichworte": ["bash", "skript", "script", "shellskript", "shebang", "#!/bin/bash", "variable", "if", "for",
                   "while", "argumente", "$1", "exit code", "set -e", "pipefail", "chmod +x", "funktion",
                   "automatisieren", "shellcheck"],

    "erklaerung": """
## Aufbau eines Skripts
- **1. Zeile: Shebang** `#!/bin/bash` – sagt, welches Programm das Skript ausführt
- **Sicherheitsgurt:** `set -euo pipefail` – bricht bei Fehlern ab, statt blind weiterzumachen
- Ausführbar machen: `chmod +x skript.sh`, starten mit `./skript.sh`
- Eigene Skripte systemweit: nach `/usr/local/bin/` legen (ohne .sh), dann überall aufrufbar
## Variablen
- Setzen **ohne Leerzeichen**: `NAME="srv01"` (mit Leerzeichen um `=` geht es nicht!)
- Benutzen **immer in Anführungszeichen**: `"$NAME"` – sonst zerfallen Werte mit Leerzeichen
- Befehlsausgabe: `DATUM=$(date +%F)`
- Argumente: `$1`, `$2` … · Anzahl: `$#` · alle: `"$@"` · Exit-Code des letzten Befehls: `$?`
## if – Bedingungen
`[ -f datei ]` Datei existiert · `[ -d ordner ]` Ordner existiert · `[ -z "$VAR" ]` Variable leer · `[ "$A" = "$B" ]` Texte gleich · `[ "$X" -gt 5 ]` Zahl grösser (`-eq -ne -lt -le -ge`)
## Vergleich zum Programmieren
Bash ist für das **Verketten von Befehlen** gemacht, nicht für Berechnungen oder grosse Programme. Faustregel: Ab ca. 100 Zeilen, Datenstrukturen oder Rechnerei → **Python** nehmen (Tab „Programmieren“).
""",

    "beispiele": [
        {"titel": "Vorlage für jedes Skript",
         "code": {"Bash": r'''#!/bin/bash
# backup-web.sh – sichert /var/www nach /mnt/backup
set -euo pipefail          # bei Fehler, leerer Variable oder Pipe-Fehler abbrechen

QUELLE="/var/www"
ZIEL="/mnt/backup"
DATUM=$(date +%F)

if [ ! -d "$ZIEL" ]; then
    echo "Fehler: $ZIEL ist nicht eingehängt" >&2
    exit 1
fi

tar -czf "$ZIEL/web-$DATUM.tar.gz" "$QUELLE"
echo "Backup fertig: $ZIEL/web-$DATUM.tar.gz"'''}},
        {"titel": "Argumente und Schleife",
         "code": {"Bash": r'''#!/bin/bash
# pinge.sh – prüft mehrere Hosts:  ./pinge.sh 192.168.1.1 192.168.1.50 ubuntu.com
set -euo pipefail

if [ $# -eq 0 ]; then
    echo "Benutzung: $0 host1 [host2 ...]"
    exit 1
fi

for HOST in "$@"; do
    if ping -c 1 -W 2 "$HOST" > /dev/null 2>&1; then
        echo "✅ $HOST erreichbar"
    else
        echo "❌ $HOST NICHT erreichbar"
    fi
done'''},
         "ausgabe": "✅ 192.168.1.1 erreichbar\n✅ 192.168.1.50 erreichbar\n❌ ubuntu.com NICHT erreichbar"},
        {"titel": "Sicheres Löschen mit Variablen",
         "text": "`${VAR:?}` bricht ab, wenn die Variable leer ist – so wird aus `rm -r \"$ORDNER/\"` nie `rm -r /`.",
         "code": {"Bash": r'''ALTE_BACKUPS="/mnt/backup/alt"
find "${ALTE_BACKUPS:?}" -name "*.tar.gz" -mtime +30 -print   # erst anzeigen
find "${ALTE_BACKUPS:?}" -name "*.tar.gz" -mtime +30 -delete'''}},
    ],

    "befehle": [
        {"titel": "Skripte ausführen & prüfen", "zeilen": [
            ("chmod +x skript.sh", "Ausführbar machen"),
            ("./skript.sh", "Ausführen (im aktuellen Ordner)"),
            ("bash -n skript.sh", "Nur Syntax prüfen, nicht ausführen"),
            ("bash -x skript.sh", "Jede Zeile beim Ausführen anzeigen (Fehlersuche)"),
            ("sudo apt install shellcheck && shellcheck skript.sh", "Findet typische Fehler automatisch"),
            ("sudo install -m 755 skript.sh /usr/local/bin/meinbefehl", "Als eigenen Befehl installieren"),
        ]},
    ],

    "sicherheit": [
        "Nie `rm -rf $VARIABLE/` ohne Anführungszeichen und `${VARIABLE:?}` – ist sie leer, löscht das Skript `/`.",
        "Nie Passwörter im Skript speichern – in eine eigene Datei mit Rechten 600 auslagern und einlesen.",
        "Skripte, die als root laufen (cron, sudo), dürfen nur für root schreibbar sein (`chmod 700`, Besitzer root).",
        "Skripte aus dem Internet vor dem Ausführen lesen (und durch `shellcheck` laufen lassen).",
    ],
    "tipps": [
        "Immer `set -euo pipefail` an den Anfang – spart viele Stunden Fehlersuche.",
        "Fehlermeldungen nach stderr schreiben: `echo \"Fehler\" >&2`, und mit `exit 1` beenden – cron und systemd erkennen dann den Fehler.",
        "Skripte mit Windows-Zeilenenden (CRLF) laufen nicht: `bad interpreter: /bin/bash^M` → `sed -i 's/\\r$//' skript.sh`.",
    ],
    "fehler": [
        "`NAME = \"x\"` mit Leerzeichen → `NAME: command not found`.",
        "`$DATEI` ohne Anführungszeichen → Dateinamen mit Leerzeichen werden zerlegt.",
        "`[$A = $B]` ohne Leerzeichen innen → Syntaxfehler. Richtig: `[ \"$A\" = \"$B\" ]`.",
        "Skript mit `sh skript.sh` statt `./skript.sh` gestartet → läuft mit sh (dash) statt bash, Bash-Befehle fehlen.",
    ],
    "siehe_auch": ["cron", "backups", "pipes_umleitung", "terminal_shell"],
}
