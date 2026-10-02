# =============================================================================
# Thema: Systematische Fehlersuche  (Kategorie: Praxis)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Fehlersuche: systematisch statt raten",
    "reihenfolge": 4,
    "kurz": "Server langsam, Dienst tot, Webseite weg? Eine Checkliste, die fast immer zum Fehler führt.",
    "stichworte": ["fehlersuche", "troubleshooting", "debug", "problem", "geht nicht", "langsam", "absturz",
                   "dienst startet nicht", "speicher voll", "ram voll", "oom", "checkliste", "notfall",
                   "ausgesperrt", "rettungsmodus", "recovery", "emergency mode"],

    "erklaerung": """
## Die Grundregel
**Erst messen, dann ändern.** Nicht fünf Dinge gleichzeitig ausprobieren, sondern Schritt für Schritt eingrenzen – und **eine** Änderung nach der anderen machen. Jede Änderung notieren.
## Die 5-Minuten-Checkliste
- 1. **Was hat sich geändert?** (Update, Konfiguration, Neustart?) → `less /var/log/apt/history.log`, `last reboot`
- 2. **Platte voll?** → `df -h` (bei 100 % stürzen Dienste ab, Datenbanken zuerst)
- 3. **RAM voll?** → `free -h`, `journalctl -k | grep -i oom` (der Kernel beendet Prozesse bei RAM-Mangel)
- 4. **Last?** → `uptime`, `htop`
- 5. **Dienst tot?** → `systemctl --failed`, `systemctl status dienst`
- 6. **Was sagt das Log?** → `journalctl -u dienst -n 100`, `journalctl -p err -b`
- 7. **Netzwerk?** → Seite „Netzwerk-Diagnose“ (IP → Gateway → DNS → Port)
## Notfall: ausgesperrt
- **Proxmox-VM:** Konsole im Webinterface öffnen – dort gilt weder SSH-Konfiguration noch Firewall.
- **Physischer Server:** Bildschirm + Tastatur.
- **Bootet nicht (fstab-Fehler):** Emergency Mode → root-Passwort bzw. Enter → `nano /etc/fstab` korrigieren (evtl. vorher `mount -o remount,rw /`).
- **Passwort vergessen:** Im GRUB-Menü den Recovery Mode wählen → „root“ → `passwd benutzer`.
""",

    "befehle": [
        {"titel": "Überblick in 1 Minute", "zeilen": [
            ("uptime", "Last und Laufzeit"),
            ("df -h", "Platte voll?"),
            ("free -h", "RAM voll? Swap?"),
            ("systemctl --failed", "Abgestürzte Dienste"),
            ("journalctl -p err -b --no-pager | tail -30", "Die letzten Fehler seit dem Booten"),
            ("sudo journalctl -k | grep -i -E \"oom|killed process\"", "Hat der Kernel wegen RAM-Mangel Prozesse beendet?"),
            ("sudo dmesg -T | grep -i -E \"error|fail|i/o\"", "Hardware-/Festplattenfehler"),
        ]},
        {"titel": "Was hat sich geändert?", "zeilen": [
            ("less /var/log/apt/history.log", "Letzte Installationen und Updates"),
            ("last reboot | head -5", "Letzte Neustarts"),
            ("sudo find /etc -mtime -2 -type f", "In den letzten 2 Tagen geänderte Konfigurationen"),
            ("journalctl -b -1 -e", "Ende des vorherigen Boots (Absturz?)"),
        ]},
        {"titel": "Dienst im Detail", "zeilen": [
            ("systemctl status dienst --no-pager", "Status + letzte Zeilen"),
            ("journalctl -u dienst -n 100 --no-pager", "Letzte 100 Log-Zeilen"),
            ("sudo nginx -t", "Konfiguration testen (viele Dienste haben so einen Test: sshd -t, apache2ctl -t …)"),
            ("sudo ss -tulpn | grep dienst", "Lauscht er auf dem erwarteten Port?"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Symptom → erster Verdacht",
            "kopf": ["Symptom", "Zuerst prüfen"],
            "zeilen": [
                ["„No space left on device“", "df -h, df -i, dann du / ncdu"],
                ["Dienst stirbt ohne Fehlermeldung", "journalctl -k | grep -i oom (RAM)"],
                ["Server sehr langsam, wenig CPU", "htop: Prozesse im Status D → Festplatte/Netzlaufwerk"],
                ["SSH: Connection refused", "Dienst ssh läuft? Port? (über Konsole)"],
                ["SSH: Timeout", "Firewall (ufw, Router, Proxmox), IP geändert?"],
                ["Webseite 502 Bad Gateway", "Backend (PHP-FPM, App, Container) läuft nicht"],
                ["Webseite nicht erreichbar", "systemctl status nginx, ss -tulpn, ufw status"],
                ["Namen werden nicht aufgelöst", "resolvectl status, dig @9.9.9.9 name"],
                ["sudo sehr langsam", "Hostname fehlt in /etc/hosts"],
                ["Bootet in Emergency Mode", "Fehler in /etc/fstab"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Schnell-Diagnose in einem Rutsch",
         "code": {"Bash": r'''echo "== Last ==";   uptime
echo "== Platte =="; df -h / /var 2>/dev/null
echo "== RAM ==";    free -h
echo "== Dienste =="; systemctl --failed --no-legend
echo "== Fehler =="; journalctl -p err -b --no-pager | tail -10'''}},
    ],

    "sicherheit": [
        "In der Hektik nicht zu „schnellen Lösungen“ greifen: `chmod 777`, `ufw disable`, Dienst als root laufen lassen – das „löst“ das Problem und schafft ein neues, grösseres.",
        "Vor Reparaturen an einer Produktiv-VM: **Snapshot**.",
        "Ungewöhnliche Prozesse, neue Benutzer, unbekannte Cron-Jobs oder volle `/tmp`-Ordner mit Programmen = möglicher **Einbruch**. Dann nicht „aufräumen“, sondern Server vom Netz nehmen und neu aufsetzen (aus sauberem Backup).",
    ],
    "tipps": [
        "Fehlermeldung **exakt** kopieren und suchen – mit Anführungszeichen in der Suchmaschine.",
        "Ein zweites SSH-Fenster mit `journalctl -f` offen haben, während man etwas ausprobiert.",
        "Ein kleines Betriebsbuch führen (Datum, Änderung, Grund) – bei der nächsten Störung Gold wert.",
    ],
    "fehler": [
        "Mehrere Dinge gleichzeitig geändert → man weiss nicht, was geholfen (oder geschadet) hat.",
        "Nur `systemctl status` gelesen, den eigentlichen Fehler weiter oben im Journal übersehen.",
        "Server neu gestartet, bevor man die Logs angeschaut hat → Hinweise im RAM-Zustand sind weg (Journal vom vorherigen Boot mit `-b -1` trotzdem lesen).",
    ],
    "siehe_auch": ["logs", "netzwerk_diagnose", "festplatten", "prozesse", "dienste_systemctl"],
}
