# =============================================================================
# Thema: Dienste mit systemctl  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Dienste steuern: systemctl",
    "reihenfolge": 2,
    "kurz": "Dienste starten, stoppen, neu laden und beim Booten automatisch starten lassen.",
    "stichworte": ["dienst", "service", "daemon", "systemd", "systemctl", "start", "stop", "restart", "reload",
                   "enable", "disable", "status", "failed", "unit", "autostart", "boot", "mask", "daemon-reload",
                   "eigener dienst", "service datei"],

    "erklaerung": """
## Was ist ein Dienst?
Ein **Dienst (Service, Daemon)** ist ein Programm, das im Hintergrund läuft – ohne dass jemand angemeldet ist: SSH-Server, Webserver, Datenbank, Firewall. Auf Ubuntu verwaltet **systemd** alle Dienste, bedient wird es mit **`systemctl`**.
## Laufen jetzt vs. beim Booten
Das sind zwei **unabhängige** Dinge:
- **start / stop** – jetzt sofort
- **enable / disable** – beim nächsten Booten automatisch (oder nicht)
- `enable --now` macht beides auf einmal
## restart oder reload?
- **restart** – Dienst stoppen und neu starten (kurze Unterbrechung, alle Verbindungen weg)
- **reload** – nur die Konfiguration neu einlesen, ohne Unterbrechung (nicht jeder Dienst kann das)
Bei Diensten, die man selbst gerade benutzt (z.B. **ssh**), ist **reload** der sichere Weg.
## Status lesen
`systemctl status nginx` zeigt: **Active: active (running)** = läuft · **inactive (dead)** = gestoppt · **failed** = abgestürzt. Darunter stehen die letzten Log-Zeilen – oft steht der Fehler direkt da.
""",

    "befehle": [
        {"titel": "Status", "zeilen": [
            ("systemctl status nginx", "Läuft er? Mit den letzten Log-Zeilen (q = beenden)"),
            ("systemctl is-active nginx", "Nur: active / inactive"),
            ("systemctl is-enabled nginx", "Startet er beim Booten?"),
            ("systemctl --failed", "Alle abgestürzten Dienste"),
            ("systemctl list-units --type=service --state=running", "Alle laufenden Dienste"),
        ]},
        {"titel": "Steuern", "zeilen": [
            ("sudo systemctl start nginx", "Starten"),
            ("sudo systemctl stop nginx", "Stoppen"),
            ("sudo systemctl restart nginx", "Neu starten"),
            ("sudo systemctl reload nginx", "Konfiguration neu laden (ohne Unterbrechung)"),
            ("sudo systemctl enable --now nginx", "Jetzt starten + beim Booten"),
            ("sudo systemctl disable --now nginx", "Jetzt stoppen + nicht mehr beim Booten"),
            ("sudo systemctl mask dienst", "Komplett sperren – kann auch nicht als Abhängigkeit starten"),
            ("sudo systemctl daemon-reload", "Nach Änderungen an .service-Dateien"),
        ]},
    ],

    "beispiele": [
        {"titel": "Nach einer Konfigurationsänderung: prüfen, neu laden, kontrollieren",
         "code": {"Bash": r'''sudo nginx -t && sudo systemctl reload nginx
systemctl status nginx --no-pager'''},
         "ausgabe": "nginx: configuration file /etc/nginx/nginx.conf test is successful\n● nginx.service - A high performance web server\n     Active: active (running) since Mon 2026-09-29 10:02:11 CEST; 2h ago"},
        {"titel": "Eigenes Programm als Dienst (z.B. ein Python-Skript)",
         "text": "Datei `/etc/systemd/system/meinapp.service` anlegen. Der Dienst läuft als eigener Benutzer (nicht root) und startet nach einem Absturz neu.",
         "code": {"Bash": r'''[Unit]
Description=Meine Python-App
After=network-online.target

[Service]
User=meinapp
WorkingDirectory=/opt/meinapp
ExecStart=/usr/bin/python3 /opt/meinapp/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target'''}},
        {"titel": "… und aktivieren",
         "code": {"Bash": r'''sudo systemctl daemon-reload
sudo systemctl enable --now meinapp
journalctl -u meinapp -f'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 Wichtige Dienste auf Ubuntu Server",
            "kopf": ["Dienst", "Wofür"],
            "zeilen": [
                ["ssh", "SSH-Server (heisst auf Ubuntu „ssh“, nicht „sshd“)"],
                ["systemd-networkd", "Netzwerk (von netplan konfiguriert)"],
                ["systemd-resolved", "DNS-Auflösung"],
                ["ufw", "Firewall"],
                ["cron", "Zeitgesteuerte Aufgaben"],
                ["unattended-upgrades", "Automatische Sicherheitsupdates"],
                ["fail2ban", "Sperrt Angreifer (wenn installiert)"],
                ["nginx / apache2", "Webserver (wenn installiert)"],
            ],
        },
    ],

    "sicherheit": [
        "`sudo systemctl stop ssh` per SSH → du bist sofort draussen (bestehende Sitzung bleibt zwar meist, aber keine neue Verbindung mehr). SSH nie stoppen oder deaktivieren, wenn du nur SSH-Zugang hast.",
        "Nach Änderungen an **ssh** immer erst `sudo sshd -t` und dann nur `reload` – und die alte Sitzung offen lassen, bis eine neue klappt.",
        "Eigene Dienste nie als root laufen lassen (`User=` in der .service-Datei setzen).",
        "Nicht benötigte Dienste mit `disable --now` abschalten – jeder laufende Netzwerkdienst ist Angriffsfläche.",
    ],
    "tipps": [
        "`systemctl status` zeigt nur die letzten Zeilen – das volle Log mit `journalctl -u dienst`.",
        "`--no-pager` hinter status/journalctl verhindert, dass `less` aufgeht (gut für Skripte und Copy/Paste).",
        "Tab-Vervollständigung funktioniert: `systemctl status ng` + Tab.",
    ],
    "fehler": [
        "Dienst gestartet, aber nach Neustart wieder aus → `enable` vergessen.",
        "`.service`-Datei geändert, aber `daemon-reload` vergessen → systemd benutzt noch die alte Version (Warnung im Status).",
        "`Unit nginx.service not found` → Programm nicht installiert oder Dienst heisst anders (`systemctl list-unit-files | grep name`).",
    ],
    "siehe_auch": ["logs", "prozesse", "pakete_apt", "cron", "fehlersuche"],
}
