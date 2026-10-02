# =============================================================================
# Thema: Navigieren (pwd, ls, cd)  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Navigieren: pwd, ls, cd",
    "reihenfolge": 1,
    "kurz": "Wo bin ich, was liegt hier, wie komme ich woanders hin?",
    "stichworte": ["navigieren", "pwd", "ls", "cd", "ordner wechseln", "auflisten", "dir", "versteckte dateien",
                   "punkt datei", "ls -la", "ls -lh", "pfad", "home", "tilde"],

    "erklaerung": """
## Die drei Grundbefehle
- **`pwd`** (print working directory) – zeigt, wo du gerade bist.
- **`ls`** (list) – zeigt, was im Ordner liegt.
- **`cd`** (change directory) – wechselt den Ordner.
## ls -l lesen
`-rw-r--r-- 1 jorick jorick 4096 Sep 29 10:12 notizen.txt`
- **-rw-r--r--** – Typ und Rechte (erstes Zeichen: `-` Datei, `d` Ordner, `l` Link) → Seite „Dateirechte“
- **jorick jorick** – Besitzer und Gruppe
- **4096** – Grösse in Byte (mit `-h` lesbar: 4.0K)
- **Sep 29 10:12** – letzte Änderung
## Versteckte Dateien
Dateien, deren Name mit **Punkt** beginnt (`.bashrc`, `.ssh`), sind versteckt. `ls` zeigt sie nicht – `ls -a` schon. Viele Einstellungen im Home-Verzeichnis sind solche Punkt-Dateien.
""",

    "befehle": [
        {"titel": "Wo bin ich, was ist hier?", "zeilen": [
            ("pwd", "Aktuellen Ordner anzeigen"),
            ("ls", "Inhalt anzeigen"),
            ("ls -la", "Alles inkl. versteckter Dateien, mit Details"),
            ("ls -lh", "Details mit lesbaren Grössen (K, M, G)"),
            ("ls -lt", "Nach Änderungszeit sortiert (neueste oben)"),
            ("ls -lS", "Nach Grösse sortiert (grösste oben)"),
            ("ls -ld /etc", "Infos über den Ordner selbst statt seinen Inhalt"),
        ]},
        {"titel": "Wechseln", "zeilen": [
            ("cd /var/log", "Absoluter Pfad – funktioniert von überall"),
            ("cd projekte", "Relativer Pfad – Unterordner des aktuellen Ordners"),
            ("cd ..", "Eine Ebene hoch"),
            ("cd ../..", "Zwei Ebenen hoch"),
            ("cd ~", "Ins Home-Verzeichnis (nur „cd“ geht auch)"),
            ("cd -", "Zurück zum vorherigen Ordner (hin und her springen)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Ein kleiner Rundgang",
         "code": {"Bash": r'''pwd
cd /var/log
ls -lht | head -5     # die 5 zuletzt geänderten Logs
cd -                  # zurück, wo ich vorher war
pwd'''},
         "ausgabe": "/home/jorick\ntotal 8.4M\n-rw-r----- 1 syslog adm 1.2M Sep 29 10:14 syslog\n-rw-r----- 1 syslog adm  88K Sep 29 10:13 auth.log\n...\n/home/jorick\n/home/jorick"},
    ],

    "tipps": [
        "Tab-Vervollständigung benutzen: `cd /v` + Tab + `l` + Tab → `cd /var/log/`.",
        "`ls -la` ist so häufig, dass Ubuntu dafür schon den Alias **`ll`** mitbringt.",
        "Ordner mit Leerzeichen: `cd \"Neuer Ordner\"` – oder Tab drücken, Bash setzt die `\\` selbst.",
    ],
    "fehler": [
        "`cd` in eine Datei statt einen Ordner → `Not a directory`.",
        "`No such file or directory` → Tippfehler oder Gross-/Kleinschreibung (`/Var/Log` gibt es nicht).",
        "`ls` zeigt `.ssh` nicht → versteckt, `ls -a` benutzen.",
    ],
    "siehe_auch": ["verzeichnisstruktur", "dateien_verwalten", "dateirechte", "suchen"],
}
