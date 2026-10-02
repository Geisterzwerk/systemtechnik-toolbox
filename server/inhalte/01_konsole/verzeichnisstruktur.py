# =============================================================================
# Thema: Verzeichnisstruktur  (Kategorie: Konsole & SSH)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Verzeichnisstruktur (wo liegt was?)",
    "reihenfolge": 5,
    "kurz": "Kein C:\\ – unter Linux beginnt alles bei / . Welche Ordner man als Admin kennen muss.",
    "stichworte": ["verzeichnis", "ordner", "struktur", "fhs", "root verzeichnis", "/etc", "/var", "/var/log",
                   "/home", "/tmp", "/opt", "/srv", "/usr", "/dev", "/proc", "/mnt", "/boot", "pfad", "absolut",
                   "relativ", "home", "tilde"],

    "erklaerung": """
## Alles beginnt bei /
Linux hat **keine Laufwerksbuchstaben**. Es gibt einen einzigen Baum, der bei **/** (Root, „Wurzel“) beginnt. Weitere Festplatten und USB-Sticks werden in einen Ordner **eingehängt** (gemountet), z.B. `/mnt/daten`.
## Alles ist eine Datei
Einstellungen sind Textdateien (meist in `/etc`), Festplatten erscheinen als Dateien in `/dev` (`/dev/sda`), Infos über laufende Prozesse als Dateien in `/proc`. Darum kann man unter Linux fast alles mit denselben Werkzeugen (`cat`, `nano`, `grep`) erledigen.
## Absolute und relative Pfade
- **Absolut** – beginnt mit `/`, gilt von überall: `/etc/ssh/sshd_config`
- **Relativ** – ausgehend vom aktuellen Ordner: `projekte/test`
- `.` = aktueller Ordner · `..` = eine Ebene höher · `~` = dein Home (`/home/jorick`)
## Die wichtigsten Orte für Admins
- **Konfiguration ändern?** → `/etc`
- **Etwas geht nicht?** → Logs in `/var/log` (bzw. `journalctl`)
- **Speicher voll?** → meist `/var` (Logs, Docker, Datenbanken) oder `/home`
""",

    "tabellen": [
        {
            "titel": "📊 Die wichtigsten Verzeichnisse",
            "kopf": ["Ordner", "Inhalt", "Beispiel"],
            "zeilen": [
                ["/", "Wurzel – alles liegt darunter", "–"],
                ["/etc", "Konfigurationsdateien des Systems und der Dienste", "/etc/ssh/sshd_config, /etc/netplan/"],
                ["/home", "Home-Verzeichnisse der Benutzer", "/home/jorick"],
                ["/root", "Home-Verzeichnis von root (NICHT /home/root)", "–"],
                ["/var", "variable Daten: Logs, Caches, Datenbanken, Webseiten", "/var/log, /var/www, /var/lib/docker"],
                ["/var/log", "Log-Dateien", "/var/log/syslog, /var/log/auth.log"],
                ["/tmp", "temporäre Dateien, wird beim Neustart geleert", "–"],
                ["/usr/bin, /usr/sbin", "Programme (sbin = Admin-Programme)", "/usr/bin/ls"],
                ["/opt", "zusätzliche Software, die nicht aus apt kommt", "/opt/meinprogramm"],
                ["/srv", "Daten für Dienste, die der Server anbietet", "/srv/ftp, /srv/daten"],
                ["/mnt, /media", "Einhängepunkte für Laufwerke / USB", "/mnt/backup"],
                ["/dev", "Geräte als Dateien", "/dev/sda (Festplatte), /dev/null"],
                ["/proc, /sys", "virtuelle Dateien mit Kernel- und Prozess-Infos", "/proc/cpuinfo"],
                ["/boot", "Kernel und Bootloader", "–"],
            ],
            "hinweis": "Diese Aufteilung heisst **FHS** (Filesystem Hierarchy Standard) – sie ist auf allen Linux-Distributionen fast gleich.",
        },
    ],

    "befehle": [
        {"titel": "Umschauen", "zeilen": [
            ("ls /", "Die Ordner der obersten Ebene"),
            ("ls /etc | less", "Alle Konfigurationen durchblättern"),
            ("cat /etc/os-release", "Welche Ubuntu-Version läuft?"),
            ("cat /proc/cpuinfo | grep \"model name\"", "Prozessor anzeigen (Datei aus /proc)"),
            ("sudo apt install tree && tree -L 1 /", "Ordnerbaum anzeigen (1 Ebene tief)"),
        ]},
    ],

    "sicherheit": [
        "In `/etc`, `/boot`, `/usr` und `/dev` nichts löschen oder verschieben, dessen Zweck du nicht genau kennst.",
        "Vor Änderungen an Dateien in `/etc` immer eine Sicherung anlegen: `sudo cp datei datei.bak`.",
        "Nie wichtige Daten in `/tmp` ablegen – wird beim Neustart gelöscht.",
    ],
    "tipps": [
        "`/root` ist das Home von root – `/home/root` gibt es nicht.",
        "`cd` ohne alles bringt dich immer nach Hause (~).",
        "Die Tab-Taste funktioniert auch bei Pfaden: `/et` + Tab → `/etc/`.",
    ],
    "fehler": [
        "Pfade mit `\\` wie unter Windows geschrieben – Linux braucht `/`.",
        "Relativer statt absoluter Pfad in Skripten/cron → funktioniert nur, wenn man zufällig im richtigen Ordner ist.",
    ],
    "siehe_auch": ["navigieren", "festplatten", "logs", "terminal_shell"],
}
