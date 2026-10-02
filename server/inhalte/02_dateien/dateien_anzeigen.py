# =============================================================================
# Thema: Dateien anzeigen (cat, less, head, tail)  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Dateien anzeigen: cat, less, head, tail",
    "reihenfolge": 3,
    "kurz": "Dateien lesen, ohne sie zu verändern – und Logs live mitverfolgen.",
    "stichworte": ["anzeigen", "lesen", "cat", "less", "more", "head", "tail", "tail -f", "live", "log lesen",
                   "wc", "zeilen zählen", "diff", "vergleichen", "file", "stat"],

    "erklaerung": """
## Welcher Befehl wofür?
- **`cat`** – gibt die ganze Datei aus. Gut für kurze Dateien, bei langen rauscht alles durch.
- **`less`** – seitenweise lesen, suchen, blättern. **Standard für alles, was länger ist.** Verändert nichts.
- **`head`** / **`tail`** – nur Anfang / Ende einer Datei (Standard: 10 Zeilen).
- **`tail -f`** – „follow“: zeigt neue Zeilen **live**, sobald sie geschrieben werden. Perfekt, um ein Log zu beobachten, während man einen Dienst neu startet.
## Lesen statt Bearbeiten
Zum **Anschauen** immer `less` oder `cat` verwenden, nicht `nano`. So kann man eine Konfiguration nicht aus Versehen verändern.
""",

    "befehle": [
        {"titel": "Anzeigen", "zeilen": [
            ("cat /etc/hostname", "Kurze Datei ausgeben"),
            ("cat -n datei.txt", "Mit Zeilennummern"),
            ("less /var/log/syslog", "Seitenweise lesen (q = beenden, /wort = suchen)"),
            ("head -n 20 datei.txt", "Die ersten 20 Zeilen"),
            ("tail -n 50 /var/log/syslog", "Die letzten 50 Zeilen"),
            ("tail -f /var/log/syslog", "Live mitlesen (Ctrl+C beendet)"),
            ("sudo tail -f /var/log/auth.log", "Anmeldungen und sudo-Aufrufe live beobachten"),
        ]},
        {"titel": "Infos & Vergleich", "zeilen": [
            ("wc -l datei.txt", "Anzahl Zeilen"),
            ("file datei", "Was für eine Datei ist das? (Text, Programm, Bild …)"),
            ("stat datei.txt", "Alle Infos: Grösse, Rechte, Zeitstempel"),
            ("diff alt.conf neu.conf", "Zwei Dateien zeilenweise vergleichen"),
            ("grep -v '^#' /etc/ssh/sshd_config | grep -v '^$'", "Konfiguration ohne Kommentare und Leerzeilen"),
        ]},
    ],

    "beispiele": [
        {"titel": "Fehlersuche: Log beobachten, während man den Dienst neu startet",
         "text": "In **einer** SSH-Sitzung das Log live anzeigen, in einer **zweiten** den Dienst neu starten – man sieht sofort, was passiert.",
         "code": {"Bash": r'''# Fenster 1
sudo tail -f /var/log/nginx/error.log

# Fenster 2
sudo systemctl restart nginx'''}},
        {"titel": "Was hat sich an der Konfiguration geändert?",
         "code": {"Bash": r'''diff /etc/ssh/sshd_config.2026-09-29.bak /etc/ssh/sshd_config'''},
         "ausgabe": "33c33\n< #PasswordAuthentication yes\n---\n> PasswordAuthentication no"},
    ],

    "tipps": [
        "In `less`: `G` springt ans Ende (neueste Log-Einträge), `/error` sucht, `n` nächster Treffer.",
        "`less +F datei` funktioniert wie `tail -f`, aber mit Ctrl+C kann man danach normal blättern.",
        "Für Dienst-Logs ist oft `journalctl -u dienst -f` besser als `tail -f` (Seite „Logs“).",
    ],
    "fehler": [
        "`cat` auf eine riesige Log-Datei → Konsole minutenlang voll. Ctrl+C und `less` nehmen.",
        "`cat` auf eine Binärdatei → Zeichensalat, Konsole spinnt. Mit `reset` wieder herstellen.",
        "Log lesen ohne sudo → `Permission denied` (viele Logs gehören root/adm).",
    ],
    "siehe_auch": ["logs", "suchen", "editor_nano", "pipes_umleitung"],
}
