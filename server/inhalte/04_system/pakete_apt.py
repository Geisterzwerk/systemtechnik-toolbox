# =============================================================================
# Thema: Pakete mit apt  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Software installieren: apt",
    "reihenfolge": 1,
    "kurz": "Programme installieren, aktualisieren und entfernen – aus den offiziellen Ubuntu-Quellen.",
    "stichworte": ["apt", "apt-get", "paket", "paketverwaltung", "installieren", "deinstallieren", "update",
                   "upgrade", "full-upgrade", "remove", "purge", "autoremove", "search", "dpkg", "snap", "ppa",
                   "repository", "quellen", "sources", "held", "lock"],

    "erklaerung": """
## Stell dir vor …
Ein **App-Store mit geprüften Lieferanten**: Statt Programme irgendwo im Internet herunterzuladen, holst du sie aus einer bekannten Quelle, die sie geprüft und unterschrieben hat. apt kümmert sich ausserdem darum, dass alles mitkommt, was das Programm braucht.
## Wie funktioniert apt?
Ubuntu holt Software aus **Paketquellen (Repositories)** – geprüften Servern von Ubuntu. `apt` lädt die Pakete herunter, installiert sie **mit allen Abhängigkeiten** und hält sie später aktuell. Kein „Setup.exe aus dem Internet“!
## update ist nicht upgrade!
- **`sudo apt update`** – lädt nur die **Liste**, welche Versionen es gibt. Installiert nichts.
- **`sudo apt upgrade`** – installiert alle verfügbaren **Updates**.
- **`sudo apt full-upgrade`** – wie upgrade, darf aber auch Pakete entfernen/neu hinzufügen (z.B. bei neuen Kernel-Versionen).
Darum immer zusammen: `sudo apt update && sudo apt upgrade`
## remove oder purge?
- `remove` – Programm weg, **Konfigurationsdateien bleiben** (praktisch bei Neuinstallation)
- `purge` – Programm **und** Konfiguration weg
- `autoremove` – räumt Pakete weg, die nur als Abhängigkeit installiert wurden und keiner mehr braucht (z.B. alte Kernel)
## Neustart nötig?
Nach Kernel- oder Bibliotheks-Updates meldet Ubuntu `*** System restart required ***`. Die Datei `/var/run/reboot-required` existiert dann.
## 🔬 Genauer hingeschaut
- **Unterschriebene Pakete:** Die Paketlisten der Quellen sind digital signiert. apt prüft die Signatur und verweigert Pakete, deren Herkunft nicht stimmt – so kann niemand unterwegs manipulierte Software unterschieben.
- **Fremde Quellen sind Vertrauenssache:** Jede zusätzliche Paketquelle (z.B. ein PPA) darf Software mit Root-Rechten installieren. Darum nur Quellen hinzufügen, denen man wirklich vertraut.
- **Aufräumen:** `sudo apt autoremove` entfernt Pakete, die nur als Abhängigkeit installiert wurden und nicht mehr gebraucht werden.
## 💡 Wusstest du?
- apt stammt aus **Debian**, einer der ältesten Linux-Distributionen (seit 1993). Ubuntu baut auf Debian auf und übernimmt darum dasselbe Paketsystem.
""",

    "befehle": [
        {"titel": "Aktualisieren", "zeilen": [
            ("sudo apt update", "Paketlisten neu laden"),
            ("apt list --upgradable", "Was würde aktualisiert?"),
            ("sudo apt upgrade", "Updates installieren"),
            ("sudo apt full-upgrade", "Updates inkl. neuer Abhängigkeiten / Kernel"),
            ("ls /var/run/reboot-required", "Existiert die Datei → Neustart nötig"),
        ]},
        {"titel": "Suchen & installieren", "zeilen": [
            ("apt search nginx", "Paket suchen"),
            ("apt show nginx", "Infos: Version, Grösse, Beschreibung"),
            ("sudo apt install nginx", "Installieren"),
            ("sudo apt install htop curl git", "Mehrere auf einmal"),
            ("apt list --installed | grep nginx", "Ist es installiert?"),
            ("apt policy nginx", "Installierte und verfügbare Version, aus welcher Quelle"),
        ]},
        {"titel": "Entfernen & aufräumen", "zeilen": [
            ("sudo apt remove nginx", "Entfernen, Konfiguration behalten"),
            ("sudo apt purge nginx", "Entfernen inkl. Konfiguration"),
            ("sudo apt autoremove", "Nicht mehr benötigte Pakete entfernen"),
            ("sudo apt clean", "Heruntergeladene Paketdateien löschen (Platz schaffen)"),
        ]},
        {"titel": "Probleme", "zeilen": [
            ("sudo apt --fix-broken install", "Kaputte Abhängigkeiten reparieren"),
            ("sudo dpkg --configure -a", "Abgebrochene Installation fertig machen"),
            ("sudo apt-mark hold paket", "Paket NICHT aktualisieren (Version festhalten)"),
            ("sudo apt-mark unhold paket", "Wieder freigeben"),
        ]},
    ],

    "beispiele": [
        {"titel": "Die tägliche Routine",
         "code": {"Bash": r'''sudo apt update && sudo apt upgrade -y
sudo apt autoremove -y
[ -f /var/run/reboot-required ] && echo "Neustart nötig!"'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 apt, apt-get, snap, dpkg",
            "kopf": ["Werkzeug", "Wofür"],
            "zeilen": [
                ["apt", "für Menschen: schöne Ausgabe, Fortschrittsbalken – im Alltag verwenden"],
                ["apt-get", "für Skripte: stabile Ausgabe, die sich nicht ändert"],
                ["dpkg", "installiert einzelne .deb-Dateien, löst KEINE Abhängigkeiten"],
                ["snap", "Container-Pakete von Canonical (manche Programme gibt es nur so)"],
            ],
        },
    ],

    "sicherheit": [
        "Nur Software aus den **offiziellen Quellen** oder von vertrauenswürdigen Herstellern mit Signatur installieren. Fremde PPAs und `.deb`-Dateien haben volle root-Rechte bei der Installation.",
        "Nie Updates wochenlang liegen lassen – Sicherheitslücken werden aktiv ausgenutzt. Automatische Sicherheitsupdates einschalten (Seite „Updates“).",
        "Nie `sudo rm /var/lib/dpkg/lock*` bei „Could not get lock“ – meist läuft gerade ein automatisches Update. Warten oder mit `ps aux | grep -i apt` nachsehen.",
        "Nie ein Update-Upgrade per SSH ohne **tmux** starten, wenn die Verbindung wackelig ist – bricht es mittendrin ab, kann das System halb aktualisiert sein.",
    ],
    "tipps": [
        "`-y` beantwortet die Rückfrage automatisch mit Ja – in Skripten praktisch, von Hand lieber lesen, was entfernt wird.",
        "Nach dem Installieren eines Dienstes: `systemctl status dienst` – läuft er, und startet er beim Booten?",
        "Wer hat welches Paket wann installiert? `less /var/log/apt/history.log`",
    ],
    "fehler": [
        "`apt upgrade` ohne vorheriges `apt update` → es wird nichts Neues gefunden.",
        "`E: Could not get lock /var/lib/dpkg/lock-frontend` → anderer apt-Prozess läuft (oft unattended-upgrades). Einige Minuten warten.",
        "`Unable to locate package` → Tippfehler, kein `apt update` gemacht, oder das Paket heisst anders (`apt search`).",
    ],
    "siehe_auch": ["updates", "dienste_systemctl", "ersteinrichtung", "fehlersuche"],
}
