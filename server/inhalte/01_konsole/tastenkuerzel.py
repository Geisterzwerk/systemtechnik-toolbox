# =============================================================================
# Thema: Tastenkürzel & History  (Kategorie: Konsole & SSH)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Tastenkürzel & Befehls-History",
    "reihenfolge": 4,
    "kurz": "Schneller tippen, weniger Fehler: Tab, Ctrl+R, !! und Co.",
    "stichworte": ["tastenkürzel", "shortcut", "tab", "autovervollständigung", "history", "verlauf", "ctrl+r",
                   "ctrl+c", "abbrechen", "ctrl+z", "hintergrund", "fg", "bg", "jobs", "sudo !!"],

    "erklaerung": """
## Die drei wichtigsten Tasten
- **Tab:** vervollständigt Befehle, Pfade und Dateinamen. Passiert nichts, gibt es mehrere Möglichkeiten → **2× Tab** zeigt sie an. Verhindert Tippfehler in Pfaden!
- **Ctrl + C:** bricht den laufenden Befehl ab (**nicht** Kopieren wie unter Windows!).
- **Ctrl + R:** durchsucht alle früheren Befehle. Tippe ein Stück, wiederholt Ctrl+R für ältere Treffer, Enter führt aus, → übernimmt zum Bearbeiten.
## Kopieren und Einfügen in der Konsole
- **Windows Terminal / PowerShell:** markieren = kopiert, **Rechtsklick** oder **Ctrl+Shift+V** fügt ein.
- **PuTTY:** markieren = kopiert, **Rechtsklick** fügt ein.
- Achtung: Beim Einfügen mehrerer Zeilen wird jede Zeile **sofort ausgeführt**.
## History – die Befehlsgeschichte
Bash merkt sich die letzten Befehle in `~/.bash_history`. Mit `history` siehst du sie nummeriert, mit `!123` führst du Nummer 123 erneut aus.
## Jobs: Vordergrund und Hintergrund
- **Ctrl + Z** hält einen laufenden Befehl an (z.B. nano) – er ist **nicht** beendet!
- `bg` lässt ihn im Hintergrund weiterlaufen, `fg` holt ihn zurück, `jobs` zeigt alle.
- `befehl &` startet direkt im Hintergrund. Achtung: Beim Abmelden wird er beendet → dafür **tmux** nehmen.
""",

    "befehle": [
        {"titel": "History", "zeilen": [
            ("history", "Alle gespeicherten Befehle nummeriert"),
            ("history | grep apt", "Frühere Befehle mit „apt“ finden"),
            ("!!", "Letzten Befehl wiederholen"),
            ("sudo !!", "Letzten Befehl mit sudo wiederholen („Permission denied“ vergessen?)"),
            ("!123", "Befehl Nummer 123 aus der History ausführen"),
            ("!$", "Letztes Argument des vorherigen Befehls einsetzen (z.B. mkdir x → cd !$)"),
        ]},
        {"titel": "Jobs", "zeilen": [
            ("jobs", "Angehaltene / Hintergrund-Jobs anzeigen"),
            ("fg", "Letzten Job zurück in den Vordergrund"),
            ("bg", "Angehaltenen Job im Hintergrund weiterlaufen lassen"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Tastenkürzel der Bash",
            "kopf": ["Kürzel", "Wirkung"],
            "zeilen": [
                ["Tab / Tab Tab", "vervollständigen / alle Möglichkeiten zeigen"],
                ["↑ / ↓", "frühere Befehle"],
                ["Ctrl + C", "Befehl abbrechen"],
                ["Ctrl + D", "Eingabe beenden / abmelden (wie exit)"],
                ["Ctrl + R", "rückwärts in der History suchen"],
                ["Ctrl + L", "Bildschirm leeren"],
                ["Ctrl + A / Ctrl + E", "an den Zeilenanfang / ans Zeilenende"],
                ["Ctrl + U / Ctrl + K", "alles links / rechts vom Cursor löschen"],
                ["Ctrl + W", "Wort links vom Cursor löschen"],
                ["Alt + . ", "letztes Argument des vorherigen Befehls einfügen"],
                ["Ctrl + Z", "Befehl anhalten (nicht beenden!) → fg / bg"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Typischer Ablauf: sudo vergessen",
         "code": {"Bash": r'''apt install htop
# E: Could not open lock file ... (Permission denied)
sudo !!          # wird zu: sudo apt install htop'''}},
    ],

    "sicherheit": [
        "Nie Passwörter oder Tokens direkt in einen Befehl schreiben (z.B. `mysql -pGeheim`) – sie landen im Klartext in `~/.bash_history`.",
        "Mehrzeiligen Text aus dem Internet nicht direkt in die Konsole einfügen – jede Zeile wird sofort ausgeführt. Erst in einen Editor kopieren und lesen.",
        "`!!` und `!123` erst nach kurzem Blick in `history` benutzen – sonst führst du etwas anderes aus als gedacht.",
    ],
    "tipps": [
        "Ein Leerzeichen **vor** einem Befehl → wird (bei Ubuntu-Standardeinstellung) nicht in der History gespeichert.",
        "Ctrl+R ist der schnellste Weg zu langen Befehlen, die man vor Wochen einmal gebraucht hat.",
        "Tab funktioniert auch bei Paketnamen (`apt install ngi` + Tab) und bei `systemctl`-Diensten.",
    ],
    "fehler": [
        "Ctrl+C zum Kopieren gedrückt → bricht den laufenden Befehl ab.",
        "Ctrl+Z statt Ctrl+C gedrückt → Programm läuft angehalten weiter, Datei evtl. noch gesperrt. Mit `fg` zurückholen und sauber beenden.",
        "Ctrl+S gedrückt → Konsole scheint eingefroren. **Ctrl+Q** gibt sie wieder frei.",
    ],
    "siehe_auch": ["terminal_shell", "ssh_verbinden", "hilfe_finden", "spickzettel"],
}
