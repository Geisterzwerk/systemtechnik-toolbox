# =============================================================================
# Thema: Systeminfo, Hostname, Zeit, Neustart  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Systeminfo, Hostname, Zeit & Neustart",
    "reihenfolge": 6,
    "kurz": "Welche Version läuft, wie viel RAM, wie heisst der Server – und wie startet man sauber neu?",
    "stichworte": ["systeminfo", "version", "ubuntu version", "kernel", "uname", "os-release", "hostname",
                   "hostnamectl", "zeit", "zeitzone", "timedatectl", "ntp", "ram", "arbeitsspeicher", "free",
                   "swap", "cpu", "lscpu", "reboot", "neustart", "shutdown", "herunterfahren", "poweroff"],

    "erklaerung": """
## Den Server kennenlernen
Bevor man etwas ändert, sollte man wissen, womit man es zu tun hat: Ubuntu-Version, Kernel, RAM, CPU, Laufzeit. Die Befehle unten zeigen das alles in Sekunden.
## Arbeitsspeicher richtig lesen
`free -h` zeigt oft wenig **free** – das ist normal! Linux nutzt freien RAM als Cache. Entscheidend ist die Spalte **available**. Wird **Swap** stark benutzt, ist der RAM wirklich zu knapp.
## Zeit und Zeitzone
Richtige Zeit ist wichtig für Logs, Zertifikate, Cron und 2FA. Ubuntu synchronisiert automatisch per NTP (`systemd-timesyncd`), die **Zeitzone** muss man aber meist selbst setzen: `Europe/Zurich`.
## Neustart und Herunterfahren
`sudo reboot` bzw. `sudo shutdown -h now`. Per SSH bricht die Verbindung sofort ab – nach einem Neustart einfach 1–2 Minuten warten und neu verbinden.
""",

    "befehle": [
        {"titel": "System", "zeilen": [
            ("cat /etc/os-release", "Ubuntu-Version (z.B. 24.04 LTS)"),
            ("uname -r", "Kernel-Version"),
            ("hostnamectl", "Hostname, Betriebssystem, Kernel, Virtualisierung"),
            ("uptime -p", "Wie lange läuft der Server schon?"),
            ("free -h", "RAM und Swap (wichtig: Spalte „available“)"),
            ("lscpu", "Prozessor: Modell, Kerne, Virtualisierung"),
            ("nproc", "Anzahl CPU-Kerne"),
            ("systemd-detect-virt", "Läuft er in einer VM / einem Container? (none = Hardware)"),
        ]},
        {"titel": "Name & Zeit", "zeilen": [
            ("sudo hostnamectl set-hostname srv01", "Hostnamen ändern"),
            ("timedatectl", "Zeit, Zeitzone, NTP-Synchronisation"),
            ("sudo timedatectl set-timezone Europe/Zurich", "Zeitzone Schweiz"),
            ("timedatectl list-timezones | grep Europe", "Verfügbare Zeitzonen"),
            ("date", "Aktuelles Datum und Uhrzeit"),
        ]},
        {"titel": "Neustart & Aus", "zeilen": [
            ("sudo reboot", "Neu starten"),
            ("sudo shutdown -r +5 \"Wartung in 5 Minuten\"", "Neustart in 5 Min. mit Nachricht an alle"),
            ("sudo shutdown -c", "Geplanten Shutdown abbrechen"),
            ("sudo shutdown -h now", "Herunterfahren (per SSH: nur mit physischem/Konsolen-Zugang wieder an!)"),
            ("last reboot | head", "Wann wurde neu gestartet?"),
        ]},
    ],

    "beispiele": [
        {"titel": "Schnell-Check nach dem Login",
         "code": {"Bash": r'''hostnamectl | grep -E "Static hostname|Operating System|Kernel"
uptime -p
free -h
df -h /'''},
         "ausgabe": " Static hostname: srv01\nOperating System: Ubuntu 24.04.1 LTS\n          Kernel: Linux 6.8.0-45-generic\nup 12 days, 3 hours\n               total   used   free  shared  buff/cache  available\nMem:           7.7Gi  1.9Gi  0.8Gi   12Mi       5.3Gi      5.8Gi\n..."},
        {"titel": "Hostname ändern – auch in /etc/hosts",
         "code": {"Bash": r'''sudo hostnamectl set-hostname srv01
sudo nano /etc/hosts        # Zeile "127.0.1.1 altername" auf "127.0.1.1 srv01" ändern'''}},
    ],

    "sicherheit": [
        "Nie `sudo shutdown -h now` (Ausschalten) auf einem entfernten Server ohne Möglichkeit, ihn wieder einzuschalten (IPMI/iLO, Proxmox-Konsole, jemand vor Ort).",
        "Vor einem Neustart prüfen, ob `/etc/fstab` und Netzwerk-Konfiguration fehlerfrei sind – sonst kommt er nicht wieder hoch.",
        "Ubuntu-Version im Blick behalten: Nur **LTS**-Versionen mit Support einsetzen (24.04 LTS: Standard-Support bis 2029).",
    ],
    "tipps": [
        "Andere angemeldete Benutzer? `who` – vor einem Neustart Bescheid geben (`shutdown -r +5 \"Nachricht\"`).",
        "Wenig „free“ in `free -h` ist kein Problem, solange „available“ genug zeigt.",
        "Der Hostname erscheint im Prompt – eindeutige Namen (`srv-web01`, `srv-db01`) verhindern Befehle auf dem falschen Server.",
    ],
    "fehler": [
        "Hostname geändert, aber `/etc/hosts` vergessen → `sudo` meldet „unable to resolve host“ und ist langsam.",
        "Zeitzone nicht gesetzt → Log-Zeiten und Cron-Jobs laufen in UTC (2 h Verschiebung im Sommer).",
    ],
    "siehe_auch": ["prozesse", "festplatten", "ersteinrichtung", "updates"],
}
