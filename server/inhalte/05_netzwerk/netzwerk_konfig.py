# =============================================================================
# Thema: Netzwerk konfigurieren (ip, netplan)  (Kategorie: Netzwerk)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "IP-Adresse & netplan",
    "reihenfolge": 1,
    "kurz": "IP-Adresse anzeigen und eine feste IP einrichten – ohne sich dabei auszusperren.",
    "stichworte": ["netzwerk", "ip", "ip adresse", "ip a", "ip r", "gateway", "route", "dns", "netplan",
                   "statische ip", "feste ip", "dhcp", "yaml", "netplan try", "netplan apply", "interface",
                   "netzwerkkarte", "ens18", "eth0", "subnetz", "cidr", "resolvectl"],

    "erklaerung": """
## Netzwerkkarte, IP, Gateway, DNS
- **Interface:** die Netzwerkkarte, z.B. `ens18` (Proxmox-VM), `enp3s0`, `eth0`
- **IP-Adresse / Präfix:** z.B. `192.168.1.50/24` → /24 = Subnetzmaske 255.255.255.0
- **Gateway:** der Router, über den es ins Internet geht (meist `.1`)
- **DNS:** übersetzt Namen in IP-Adressen (Router, `1.1.1.1`, `9.9.9.9`)
## ip – anzeigen und kurzzeitig ändern
`ip a` zeigt Adressen, `ip r` die Routen. Änderungen mit `ip` gelten nur bis zum Neustart.
## netplan – dauerhafte Konfiguration
Ubuntu Server konfiguriert das Netzwerk über **YAML-Dateien in `/etc/netplan/`** (z.B. `50-cloud-init.yaml`). netplan erzeugt daraus die eigentliche Konfiguration für systemd-networkd.
- **YAML ist pingelig:** Einrückung nur mit **Leerzeichen**, keine Tabs. Ein falsches Leerzeichen = Fehler.
- Die Datei sollte Rechte **600** haben (netplan warnt sonst).
## netplan try – der Rettungsschirm
**`sudo netplan try`** wendet die neue Konfiguration an und wartet **120 Sekunden** auf eine Bestätigung (Enter). Kommt keine – weil du dich ausgesperrt hast –, wird automatisch die alte Konfiguration zurückgeholt. Per SSH **immer `try` statt `apply`**.
""",

    "befehle": [
        {"titel": "Anzeigen", "zeilen": [
            ("ip a", "Alle Interfaces und IP-Adressen"),
            ("ip -br a", "Kurzform: eine Zeile pro Interface"),
            ("ip r", "Routen – „default via …“ ist das Gateway"),
            ("resolvectl status", "Welche DNS-Server werden benutzt?"),
            ("ls /etc/netplan/", "netplan-Konfigurationsdateien"),
            ("sudo netplan get", "Aktuelle netplan-Konfiguration zusammengefasst"),
        ]},
        {"titel": "Ändern", "zeilen": [
            ("sudo cp /etc/netplan/50-cloud-init.yaml ~/netplan.bak", "Sicherung (nicht in /etc/netplan ablegen!)"),
            ("sudo nano /etc/netplan/50-cloud-init.yaml", "Konfiguration bearbeiten"),
            ("sudo netplan generate", "Nur prüfen, ob die YAML gültig ist"),
            ("sudo netplan try", "Anwenden mit automatischem Zurücksetzen nach 120 s"),
            ("sudo chmod 600 /etc/netplan/*.yaml", "Richtige Rechte (Warnung „too open“ beheben)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Feste IP-Adresse (statt DHCP)",
         "text": "Interface-Name (hier `ens18`) mit `ip a` herausfinden. Einrückung exakt so – nur Leerzeichen!",
         "code": {"Bash": r'''network:
  version: 2
  ethernets:
    ens18:
      dhcp4: false
      addresses:
        - 192.168.1.50/24
      routes:
        - to: default
          via: 192.168.1.1
      nameservers:
        addresses: [192.168.1.1, 9.9.9.9]'''}},
        {"titel": "Sicher anwenden",
         "code": {"Bash": r'''sudo netplan generate          # Syntax ok?
sudo netplan try               # anwenden, 120 s Zeit zum Bestätigen
# neue SSH-Verbindung auf die NEUE IP testen, erst dann in der alten Sitzung Enter drücken'''},
         "ausgabe": "Do you want to keep these settings?\n\nPress ENTER before the timeout to accept the new configuration\n\nChanges will revert in 118 seconds"},
    ],

    "sicherheit": [
        "Per SSH **nie `sudo netplan apply`** bei Änderungen an der IP, dem Gateway oder dem Interface – ein Fehler, und der Server ist nur noch über die Konsole erreichbar. Immer `netplan try`.",
        "Vor jeder Änderung eine Kopie der YAML anlegen – aber **ausserhalb** von `/etc/netplan/` (sonst liest netplan die Kopie mit!).",
        "Feste IPs so wählen, dass sie nicht im DHCP-Bereich des Routers liegen – sonst doppelte IP-Adressen.",
        "Bei Servern mit Internetzugang: Nicht einfach „irgendeinen“ DNS eintragen – vertrauenswürdige Resolver (Router, Provider, 9.9.9.9, 1.1.1.1).",
    ],
    "tipps": [
        "In Proxmox-VMs heisst das Interface meist `ens18`.",
        "Alternative zur festen IP: **DHCP-Reservierung** im Router (IP fest an die MAC-Adresse gebunden) – dann bleibt der Server auf DHCP.",
        "Nach der Änderung: `ip a`, `ip r`, `ping -c 3 192.168.1.1`, `ping -c 3 ubuntu.com` – Adresse, Gateway, DNS nacheinander prüfen.",
    ],
    "fehler": [
        "Tabs oder falsche Einrückung in der YAML → `Invalid YAML` / `Error in network definition`.",
        "Alte Schreibweise `gateway4:` – veraltet, heute `routes: - to: default via: …`.",
        "Cloud-init überschreibt die Datei beim Neustart → `/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg` mit `network: {config: disabled}` anlegen.",
    ],
    "siehe_auch": ["netzwerk_diagnose", "firewall_ufw", "ssh_verbinden", "ersteinrichtung"],
}
