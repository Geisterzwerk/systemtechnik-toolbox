# =============================================================================
# Thema: Pipes & Umleitung  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Pipes & Umleitung: |  >  >>  2>",
    "reihenfolge": 6,
    "kurz": "Befehle zusammenstecken und Ausgaben in Dateien schreiben – das Herz der Linux-Konsole.",
    "stichworte": ["pipe", "pipes", "umleitung", "redirect", "stdout", "stderr", "stdin", ">", ">>", "2>",
                   "2>&1", "/dev/null", "tee", "sudo tee", "xargs", "sort", "uniq", "cut", "awk", "sed"],

    "erklaerung": """
## Drei Datenströme
Jedes Programm hat drei „Kanäle“:
- **stdin (0)** – Eingabe (normal: Tastatur)
- **stdout (1)** – normale Ausgabe (normal: Bildschirm)
- **stderr (2)** – Fehlermeldungen (normal: auch Bildschirm)
## Pipe |
`befehl1 | befehl2` – die Ausgabe von befehl1 wird zur Eingabe von befehl2. So baut man aus kleinen Werkzeugen grosse Lösungen: `ps aux | grep nginx | wc -l`.
## Umleitung in Dateien
- `> datei` – Ausgabe in Datei schreiben, **Datei wird überschrieben!**
- `>> datei` – an Datei **anhängen**
- `2> datei` – nur Fehlermeldungen in Datei
- `> datei 2>&1` bzw. `&> datei` – alles in eine Datei
- `> /dev/null` – wegwerfen („das schwarze Loch“)
## Die sudo-Falle
`sudo echo "text" > /etc/datei` **funktioniert nicht**: sudo gilt nur für `echo`, die Umleitung `>` macht deine Shell – ohne Admin-Rechte. Lösung: **`tee`**, das mit sudo läuft: `echo "text" | sudo tee /etc/datei` (bzw. `tee -a` zum Anhängen).
""",

    "befehle": [
        {"titel": "Umleitung", "zeilen": [
            ("ls -la > liste.txt", "Ausgabe in Datei (überschreibt!)"),
            ("date >> protokoll.txt", "Anhängen"),
            ("befehl 2> fehler.txt", "Nur Fehler in Datei"),
            ("befehl > alles.log 2>&1", "Ausgabe und Fehler in dieselbe Datei"),
            ("befehl > /dev/null 2>&1", "Alles wegwerfen (z.B. in cron-Jobs)"),
            ("echo \"192.168.1.60 nas\" | sudo tee -a /etc/hosts", "Mit Admin-Rechten an Systemdatei anhängen"),
        ]},
        {"titel": "Werkzeuge für Pipes", "zeilen": [
            ("sort", "Zeilen sortieren (-n numerisch, -r rückwärts, -h für 1K/2M)"),
            ("uniq -c", "Gleiche aufeinanderfolgende Zeilen zählen (vorher sort!)"),
            ("wc -l", "Zeilen zählen"),
            ("head -n 10", "Nur die ersten 10 Zeilen"),
            ("cut -d: -f1 /etc/passwd", "Spalte 1 bei Trennzeichen : (alle Benutzernamen)"),
            ("awk '{print $1}'", "Erstes Wort jeder Zeile (Leerzeichen-getrennt)"),
            ("tee datei.txt", "Ausgabe anzeigen UND gleichzeitig in Datei schreiben"),
            ("xargs", "Zeilen als Argumente an einen Befehl übergeben"),
        ]},
        {"titel": "Verketten", "zeilen": [
            ("befehl1 && befehl2", "befehl2 nur bei Erfolg von befehl1"),
            ("befehl1 || befehl2", "befehl2 nur bei Fehler von befehl1"),
            ("befehl1 ; befehl2", "Nacheinander, egal was passiert"),
        ]},
    ],

    "beispiele": [
        {"titel": "Welche Ordner fressen den Speicher?",
         "code": {"Bash": r'''sudo du -h --max-depth=1 /var 2>/dev/null | sort -rh | head -10'''},
         "ausgabe": "6.1G\t/var\n4.8G\t/var/lib\n1.1G\t/var/log\n..."},
        {"titel": "Top 5 der häufigsten Fehlermeldungen heute",
         "code": {"Bash": r'''sudo journalctl -p err --since today --no-pager | awk '{$1=$2=$3=""; print}' | sort | uniq -c | sort -rn | head -5'''}},
        {"titel": "Ausgabe gleichzeitig sehen und protokollieren",
         "code": {"Bash": r'''sudo apt upgrade -y 2>&1 | tee ~/update-$(date +%F).log'''}},
    ],

    "sicherheit": [
        "**`>` überschreibt ohne Rückfrage.** `> /etc/fstab` statt `>> /etc/fstab` = Datei leer = Server bootet nicht mehr. Bei Systemdateien immer vorher `.bak`-Kopie.",
        "Nie `curl … | bash` oder `wget … | sh` mit Skripten, die du nicht vorher gelesen hast – das Skript läuft mit deinen Rechten (oder mit sudo mit allen). Erst herunterladen, lesen, dann ausführen.",
        "Vorsicht mit `xargs rm` – Dateinamen mit Leerzeichen werden zerlegt. Sicherer: `find … -print0 | xargs -0 …` und erst ohne rm testen.",
    ],
    "tipps": [
        "`set -o noclobber` verhindert, dass `>` bestehende Dateien überschreibt (`>|` erzwingt es dann bewusst).",
        "`sort | uniq -c | sort -rn` ist die klassische „Hitliste“ – zählt, wie oft etwas vorkommt.",
        "Lange Pipes Schritt für Schritt aufbauen: erst `befehl1`, dann `| befehl2` dazu, Ausgabe prüfen, weiter.",
    ],
    "fehler": [
        "`sudo echo text > /etc/datei` → Permission denied. Lösung: `| sudo tee`.",
        "`befehl 2>&1 > datei` (falsche Reihenfolge) → Fehler landen trotzdem auf dem Bildschirm. Richtig: `> datei 2>&1`.",
        "`uniq` ohne vorheriges `sort` → gleiche Zeilen werden nicht zusammengefasst, wenn sie nicht nebeneinander stehen.",
    ],
    "siehe_auch": ["suchen", "dateien_anzeigen", "bash_skripte", "logs"],
}
