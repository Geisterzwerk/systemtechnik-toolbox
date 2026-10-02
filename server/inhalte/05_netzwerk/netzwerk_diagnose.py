# =============================================================================
# Thema: Netzwerk-Diagnose  (Kategorie: Netzwerk)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Netzwerk-Diagnose: ping, ss, curl, dig",
    "reihenfolge": 2,
    "kurz": "Geht das Netz? Läuft der Dienst? Kommt man durch die Firewall? Schritt für Schritt prüfen.",
    "stichworte": ["netzwerk diagnose", "ping", "traceroute", "tracepath", "mtr", "ss", "netstat", "port",
                   "lauschen", "listen", "curl", "wget", "dig", "nslookup", "dns", "nc", "netcat", "erreichbar",
                   "verbindung", "timeout", "connection refused"],

    "erklaerung": """
## Von innen nach aussen prüfen
Netzwerkprobleme findet man am schnellsten, wenn man **Schicht für Schicht** vorgeht:
- 1. **Eigene IP da?** `ip a`
- 2. **Gateway erreichbar?** `ping -c 3 192.168.1.1`
- 3. **Internet per IP?** `ping -c 3 9.9.9.9`
- 4. **DNS geht?** `ping -c 3 ubuntu.com` bzw. `dig ubuntu.com`
- 5. **Dienst lauscht?** `sudo ss -tulpn`
- 6. **Dienst antwortet?** `curl -I http://localhost`
- 7. **Von aussen erreichbar?** vom anderen Rechner `nc -zv server 443` / Firewall prüfen
Wo es zum ersten Mal scheitert, liegt das Problem.
## Die Fehlermeldungen unterscheiden
- **Connection refused** – Rechner erreichbar, aber auf dem Port **lauscht nichts** (Dienst aus, falscher Port, lauscht nur auf 127.0.0.1)
- **Connection timed out** – keine Antwort: **Firewall** blockiert, falsche IP oder Rechner aus
- **Name or service not known** – **DNS**-Problem
## ss -tulpn lesen
Zeigt alle Ports, auf denen etwas lauscht. Wichtig ist die Spalte **Local Address**:
- `127.0.0.1:3306` – nur lokal erreichbar ✅ (Datenbank soll so sein)
- `0.0.0.0:80` bzw. `*:80` bzw. `[::]:80` – von **allen** Netzwerken erreichbar (nur wenn gewollt!)
""",

    "befehle": [
        {"titel": "Erreichbarkeit", "zeilen": [
            ("ping -c 4 192.168.1.1", "Gateway erreichbar? (4 Pakete, sonst endlos → Ctrl+C)"),
            ("ping -c 4 9.9.9.9", "Internet per IP erreichbar?"),
            ("tracepath ubuntu.com", "Über welche Stationen geht es? Wo hört es auf?"),
            ("mtr ubuntu.com", "ping + traceroute live (sudo apt install mtr-tiny)"),
        ]},
        {"titel": "DNS", "zeilen": [
            ("dig ubuntu.com +short", "IP-Adresse eines Namens"),
            ("dig @9.9.9.9 ubuntu.com +short", "Bestimmten DNS-Server fragen"),
            ("dig -x 192.168.1.50 +short", "Rückwärts: Name zu einer IP"),
            ("resolvectl query ubuntu.com", "So löst der Server selbst auf (inkl. Cache)"),
        ]},
        {"titel": "Ports & Dienste", "zeilen": [
            ("sudo ss -tulpn", "Welche Programme lauschen auf welchen Ports? (t=TCP u=UDP l=listen p=Programm n=Zahlen)"),
            ("sudo ss -tulpn | grep :22", "Lauscht etwas auf Port 22?"),
            ("ss -tn state established", "Aktive Verbindungen (wer ist gerade verbunden?)"),
            ("nc -zv 192.168.1.50 22", "Ist Port 22 auf dem Ziel offen? (vom anderen Rechner)"),
            ("curl -I http://localhost", "Webserver lokal testen (nur Header)"),
            ("curl -v https://example.com", "Ganze Verbindung inkl. TLS-Zertifikat anzeigen"),
            ("curl ifconfig.me", "Meine öffentliche IP-Adresse"),
        ]},
    ],

    "beispiele": [
        {"titel": "Webseite geht nicht – systematisch",
         "code": {"Bash": r'''systemctl is-active nginx          # läuft der Dienst?
sudo ss -tulpn | grep -E ':80|:443' # lauscht er?
curl -I http://localhost            # antwortet er lokal?
sudo ufw status | grep -E '80|443'  # lässt die Firewall durch?'''},
         "ausgabe": "active\ntcp LISTEN 0 511 0.0.0.0:80 0.0.0.0:* users:((\"nginx\",pid=812,fd=6))\nHTTP/1.1 200 OK\n80/tcp ALLOW Anywhere"},
    ],

    "tabellen": [
        {
            "titel": "📊 Standard-Ports, die man kennen sollte",
            "kopf": ["Port", "Dienst", "Ins Internet?"],
            "zeilen": [
                ["22/tcp", "SSH", "nur mit Schlüssel + fail2ban, besser nur per VPN"],
                ["80 / 443/tcp", "HTTP / HTTPS", "ja, wenn Webserver"],
                ["53/udp+tcp", "DNS", "nein (ausser eigener DNS-Server)"],
                ["51820/udp", "WireGuard VPN", "ja – der sichere Weg für alles andere"],
                ["3306 / 5432", "MySQL / PostgreSQL", "❌ nie"],
                ["6379 / 27017", "Redis / MongoDB", "❌ nie"],
                ["8006", "Proxmox Web-GUI", "❌ nie"],
                ["445 / 3389", "SMB / RDP (Windows)", "❌ nie"],
            ],
        },
    ],

    "sicherheit": [
        "Jeder Port mit `0.0.0.0` bzw. `*` in `ss -tulpn` ist potentiell von aussen erreichbar. Nur Dienste, die wirklich öffentlich sein müssen, dürfen so lauschen.",
        "Keine fremden Netze oder Server mit `nmap` scannen – ohne Erlaubnis ist das in der Schweiz und fast überall rechtlich heikel. Nur eigene Systeme.",
        "Nie `curl … | sudo bash` zur „schnellen Installation“ ohne das Skript vorher gelesen zu haben.",
    ],
    "tipps": [
        "`ping` ohne Antwort heisst nicht zwingend „offline“ – manche Server/Firewalls blockieren ICMP. Dann Port mit `nc -zv` testen.",
        "`curl -k` ignoriert Zertifikatsfehler – nur zum Testen, nie in Skripten.",
        "Unter Windows gibt es `Test-NetConnection 192.168.1.50 -Port 22` als Gegenstück zu `nc -zv`.",
    ],
    "fehler": [
        "Dienst lauscht nur auf `127.0.0.1` → von aussen „Connection refused“. In der Konfiguration des Dienstes die Bind-Adresse anpassen (wenn gewollt).",
        "Firewall des Servers ok, aber Router/Proxmox-Firewall/Cloud-Firewall blockiert → Timeout.",
        "`netstat` nicht gefunden → veraltet, `ss` benutzen.",
    ],
    "siehe_auch": ["netzwerk_konfig", "offene_ports", "firewall_ufw", "fehlersuche"],
}
