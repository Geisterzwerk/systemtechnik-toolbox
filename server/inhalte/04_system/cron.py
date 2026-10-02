# =============================================================================
# Thema: Zeitgesteuerte Aufgaben (cron, systemd-Timer)  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Zeitpläne: cron & systemd-Timer",
    "reihenfolge": 7,
    "kurz": "Backups, Aufräumen, Berichte – automatisch zu festen Zeiten ausführen.",
    "stichworte": ["cron", "crontab", "cronjob", "zeitplan", "automatisch", "planen", "timer", "systemd timer",
                   "list-timers", "täglich", "nachts", "@reboot", "anacron", "cron.d", "cron.daily"],

    "erklaerung": """
## crontab – ein Stundenplan für Befehle
Jeder Benutzer hat eine eigene **crontab** (`crontab -e`). Jede Zeile = ein Auftrag:
`Minute  Stunde  Tag  Monat  Wochentag  Befehl`
- `*` = jeder Wert · `*/15` = alle 15 · `1-5` = von bis · `1,15` = Liste
- Wochentag: 0 oder 7 = Sonntag, 1 = Montag … 6 = Samstag
Root-Aufgaben: `sudo crontab -e` (laufen als root).
## Die drei Cron-Fallen
- **Andere Umgebung:** cron kennt deinen `PATH` nicht. Immer **absolute Pfade** verwenden (`/usr/bin/rsync`, `/home/jorick/skript.sh`).
- **Keine Ausgabe:** Fehler sieht man nicht. Ausgabe in eine Log-Datei umleiten: `>> /var/log/meinjob.log 2>&1`.
- **Zeitzone:** Cron benutzt die Zeitzone des Systems – vorher `timedatectl` prüfen.
## systemd-Timer – die moderne Alternative
Timer sind aufwändiger einzurichten (zwei Dateien), haben aber Vorteile: Log im Journal, `Persistent=true` holt verpasste Läufe nach (Server war aus), Abhängigkeiten. `systemctl list-timers` zeigt alle – Ubuntu nutzt sie selbst (apt, logrotate).
""",

    "befehle": [
        {"titel": "cron", "zeilen": [
            ("crontab -e", "Eigene Aufgaben bearbeiten (beim ersten Mal Editor wählen: nano)"),
            ("crontab -l", "Eigene Aufgaben anzeigen"),
            ("sudo crontab -e", "Aufgaben von root bearbeiten"),
            ("sudo crontab -l -u anna", "Aufgaben eines anderen Benutzers anzeigen"),
            ("ls /etc/cron.d /etc/cron.daily", "Systemweite Cron-Aufgaben (von Paketen)"),
            ("grep CRON /var/log/syslog | tail", "Wann hat cron zuletzt was gestartet?"),
        ]},
        {"titel": "systemd-Timer", "zeilen": [
            ("systemctl list-timers", "Alle Timer: nächster und letzter Lauf"),
            ("sudo systemctl enable --now backup.timer", "Eigenen Timer aktivieren"),
            ("journalctl -u backup.service", "Log des letzten Laufs"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Cron-Zeitangaben – Beispiele",
            "kopf": ["Eintrag", "Bedeutung"],
            "zeilen": [
                ["0 2 * * *", "jeden Tag um 02:00"],
                ["30 23 * * 1-5", "Montag bis Freitag um 23:30"],
                ["*/15 * * * *", "alle 15 Minuten"],
                ["0 3 * * 0", "jeden Sonntag um 03:00"],
                ["0 4 1 * *", "am 1. jedes Monats um 04:00"],
                ["@reboot", "einmal nach jedem Neustart"],
                ["@daily / @weekly", "täglich / wöchentlich um Mitternacht"],
            ],
            "hinweis": "Prüfen, ob die Zeitangabe stimmt: Seite **crontab.guru** im Browser – oder im Zweifel lieber nachrechnen als raten.",
        },
    ],

    "beispiele": [
        {"titel": "Tägliches Backup um 02:00 mit Log-Datei",
         "code": {"Bash": r'''# crontab -e   (als root: sudo crontab -e)
# m  h  Tag Mon WT  Befehl
0  2  *   *   *   /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1'''}},
        {"titel": "Dasselbe als systemd-Timer (zwei Dateien)",
         "text": "`/etc/systemd/system/backup.service` und `/etc/systemd/system/backup.timer`, danach `sudo systemctl daemon-reload && sudo systemctl enable --now backup.timer`.",
         "code": {"Bash": r'''# backup.service
[Unit]
Description=Nächtliches Backup

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup.sh

# backup.timer
[Unit]
Description=Backup jeden Tag um 02:00

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target'''}},
    ],

    "sicherheit": [
        "Skripte, die cron als **root** ausführt, dürfen nur für root schreibbar sein (`chmod 700`, Besitzer root). Sonst kann jeder, der das Skript ändern darf, Befehle als root ausführen.",
        "Nie Passwörter direkt in die crontab schreiben – in eine Datei mit Rechten 600 auslagern.",
        "Cron-Jobs mit `rm` oder `find -delete` besonders gründlich testen – sie laufen jede Nacht, auch wenn etwas schiefgeht.",
    ],
    "tipps": [
        "Einen Job erst **von Hand** mit genau derselben Zeile testen, bevor er in die crontab kommt.",
        "Jobs, die länger laufen könnten, gegen doppelte Starts schützen: `flock -n /tmp/backup.lock /usr/local/bin/backup.sh`.",
        "Zeitpläne leicht versetzen (02:17 statt 02:00), damit nicht alle Jobs gleichzeitig laufen.",
    ],
    "fehler": [
        "Skript läuft von Hand, aber nicht per cron → relativer Pfad oder fehlender PATH. Absolute Pfade verwenden.",
        "Skript nicht ausführbar (`chmod +x` fehlt) oder Windows-Zeilenenden (CRLF).",
        "`%` in der crontab muss als `\\%` geschrieben werden (z.B. bei `date +\\%F`) – sonst wird die Zeile abgeschnitten.",
    ],
    "siehe_auch": ["backups", "bash_skripte", "dienste_systemctl", "logs"],
}
