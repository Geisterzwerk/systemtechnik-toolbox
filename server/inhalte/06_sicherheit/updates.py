# =============================================================================
# Thema: Updates & automatische Sicherheitsupdates  (Kategorie: Sicherheit)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Updates & automatische Sicherheitsupdates",
    "reihenfolge": 5,
    "kurz": "Sicherheitslücken schliessen, bevor sie ausgenutzt werden – automatisch und kontrolliert.",
    "stichworte": ["update", "updates", "sicherheitsupdate", "unattended-upgrades", "automatische updates",
                   "patch", "kernel", "reboot required", "needrestart", "lts", "do-release-upgrade",
                   "release upgrade", "ubuntu pro", "esm", "livepatch", "support ende"],

    "erklaerung": """
## Warum Updates Sicherheit sind
Sobald eine Lücke veröffentlicht ist, suchen Bots **innerhalb von Stunden** nach verwundbaren Servern. Ein Update ist oft der einzige Schutz. Deshalb: **Sicherheitsupdates automatisch**, den Rest regelmässig von Hand.
## unattended-upgrades
Auf Ubuntu Server ist **unattended-upgrades** vorinstalliert und installiert täglich **Sicherheitsupdates** selbständig. Prüfen, ob es aktiv ist – und entscheiden, ob der Server bei Bedarf **automatisch neu starten** darf (z.B. nachts um 03:30).
## Neustart nach Updates
Kernel-Updates wirken erst nach einem Neustart. Ubuntu zeigt beim Login `*** System restart required ***`. **needrestart** meldet nach `apt upgrade`, welche Dienste neu gestartet werden sollten.
## Release-Upgrade (z.B. 22.04 → 24.04)
Ein Wechsel der Ubuntu-Version (`do-release-upgrade`) ist ein grosser Eingriff: **vorher Backup/Snapshot**, in **tmux**, und am besten erst, wenn die neue Version ein paar Monate alt ist (ab x.04.1). LTS-Versionen haben 5 Jahre Standard-Support (mit Ubuntu Pro bis 10+ Jahre).
""",

    "befehle": [
        {"titel": "Von Hand", "zeilen": [
            ("sudo apt update && sudo apt upgrade", "Alle Updates"),
            ("apt list --upgradable", "Was steht an?"),
            ("cat /var/run/reboot-required.pkgs", "Welche Pakete verlangen einen Neustart?"),
            ("sudo needrestart", "Welche Dienste sollten neu gestartet werden?"),
        ]},
        {"titel": "Automatische Sicherheitsupdates", "zeilen": [
            ("systemctl status unattended-upgrades", "Läuft der Dienst?"),
            ("sudo dpkg-reconfigure -plow unattended-upgrades", "Ein-/ausschalten (Dialog)"),
            ("sudo unattended-upgrade --dry-run --debug", "Testlauf: was würde installiert?"),
            ("less /var/log/unattended-upgrades/unattended-upgrades.log", "Was wurde automatisch installiert?"),
            ("sudo nano /etc/apt/apt.conf.d/50unattended-upgrades", "Einstellungen (Auto-Reboot, Mail …)"),
        ]},
        {"titel": "Version & Support", "zeilen": [
            ("lsb_release -a", "Ubuntu-Version"),
            ("pro status", "Ubuntu-Pro-Status (ESM, Livepatch) – für Privat bis 5 Rechner gratis"),
            ("sudo do-release-upgrade", "Auf neue Ubuntu-Version wechseln (nur mit Backup + tmux!)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Automatischen Neustart nachts erlauben",
         "text": "In `/etc/apt/apt.conf.d/50unattended-upgrades` diese Zeilen suchen, `//` am Anfang entfernen und Werte anpassen:",
         "code": {"Bash": r'''Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "03:30";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";'''}},
        {"titel": "Wöchentliche Wartungs-Routine",
         "code": {"Bash": r'''sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
systemctl --failed
df -h /
[ -f /var/run/reboot-required ] && echo "⚠ Neustart nötig" || echo "✅ kein Neustart nötig"'''}},
    ],

    "sicherheit": [
        "Nie automatische Sicherheitsupdates abschalten, „weil sie stören“ – lieber das Zeitfenster anpassen.",
        "Nie Server mit einer Ubuntu-Version ohne Support betreiben (z.B. 20.04 ohne Pro nach Mai 2025) – es gibt keine Sicherheitsupdates mehr.",
        "Nie ein Release-Upgrade ohne Backup/Snapshot und ohne tmux starten.",
        "Neustarts nicht ewig aufschieben: ein neuer Kernel schützt erst nach dem Reboot.",
    ],
    "tipps": [
        "Bei Proxmox-VMs vor grossen Updates einen **Snapshot** machen – in 10 Sekunden zurück, falls etwas bricht.",
        "Mehrere Server? Erst auf einem Testserver aktualisieren, dann auf den wichtigen.",
        "Die Login-Nachricht (MOTD) zeigt, wie viele Updates anstehen – gewöhn dir an, sie zu lesen.",
    ],
    "fehler": [
        "`Could not get lock` direkt nach dem Booten → unattended-upgrades läuft gerade. Warten.",
        "Nach Kernel-Update nicht neu gestartet → `uname -r` zeigt noch den alten Kernel.",
        "Dienst-Konfigurationen bei Update-Rückfragen überschrieben („install the package maintainer's version“) → eigene Änderungen weg. Im Zweifel „keep the local version“ wählen und später vergleichen.",
    ],
    "siehe_auch": ["pakete_apt", "todsuenden", "ersteinrichtung", "backups"],
}
