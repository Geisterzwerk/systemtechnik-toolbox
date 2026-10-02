# =============================================================================
# Thema: Offene Ports & Angriffsfläche  (Kategorie: Sicherheit)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Offene Ports & Angriffsfläche",
    "reihenfolge": 4,
    "kurz": "Was ist von aussen erreichbar? Warum Datenbanken nie offen sein dürfen – und die Docker-Falle.",
    "stichworte": ["port", "ports", "offen", "angriffsfläche", "exposed", "0.0.0.0", "127.0.0.1", "bind",
                   "listen", "ss -tulpn", "nmap", "docker", "docker ufw", "portweiterleitung", "port forwarding",
                   "datenbank offen", "vpn", "wireguard", "reverse proxy", "shodan"],

    "erklaerung": """
## Jeder offene Port ist eine Tür
Ein Dienst, der auf einem Port lauscht **und** von aussen erreichbar ist, kann angegriffen werden – mit Passwort-Raten, bekannten Sicherheitslücken oder Fehlkonfigurationen. Suchmaschinen wie Shodan listen offene Datenbanken, Proxmox-Oberflächen und Webcams weltweit auf. **Weniger offene Ports = weniger Angriffsfläche.**
## Drei Stellen entscheiden, ob ein Port erreichbar ist
- 1. **Worauf lauscht der Dienst?** `127.0.0.1` = nur lokal, `0.0.0.0` / `::` = alle Netzwerke
- 2. **Server-Firewall** (ufw) – blockiert oder erlaubt
- 3. **Router / Cloud / Proxmox-Firewall** – Portweiterleitungen ins Internet
Am sichersten ist ein Dienst, der **schon auf 127.0.0.1 lauscht** – dann ist er auch bei einem Firewall-Fehler nicht erreichbar.
## Die Docker-Falle
Docker schreibt **eigene Firewall-Regeln** vor die von ufw. `docker run -p 5432:5432 postgres` macht die Datenbank **für die ganze Welt** erreichbar – obwohl `ufw status` nichts davon zeigt!
- Lösung: an localhost binden: `-p 127.0.0.1:5432:5432`
- Oder den Port gar nicht veröffentlichen und Container über ein Docker-Netzwerk verbinden
## Interne Dienste richtig erreichbar machen
- **VPN** (WireGuard, Tailscale): nur ein UDP-Port offen, alles andere nur im VPN erreichbar – die beste Lösung für SSH, Proxmox, Datenbanken, Admin-Oberflächen
- **Reverse Proxy** (nginx, Caddy, Traefik) mit HTTPS für Web-Anwendungen – nur 80/443 offen
- **SSH-Tunnel** für einzelne Zugriffe (siehe Beispiel)
""",

    "befehle": [
        {"titel": "Auf dem Server", "zeilen": [
            ("sudo ss -tulpn", "Alle lauschenden Ports mit Programm"),
            ("sudo ss -tulpn | grep -v '127.0.0' | grep -v '::1'", "Nur Ports, die NICHT nur lokal sind"),
            ("sudo ufw status verbose", "Was lässt die Firewall durch?"),
            ("docker ps --format '{{.Names}}  {{.Ports}}'", "Welche Ports veröffentlichen Container? (0.0.0.0 = offen!)"),
        ]},
        {"titel": "Von einem ANDEREN Rechner prüfen (nur eigene Systeme!)", "zeilen": [
            ("nmap -Pn 192.168.1.50", "Häufige Ports scannen (sudo apt install nmap)"),
            ("nmap -Pn -p 22,80,443,3306,5432,8006 192.168.1.50", "Bestimmte Ports prüfen"),
            ("nc -zv 192.168.1.50 5432", "Ein einzelner Port offen?"),
        ]},
    ],

    "beispiele": [
        {"titel": "ss -tulpn richtig lesen",
         "code": {"Bash": r'''sudo ss -tulpn'''},
         "ausgabe": "Netid State  Local Address:Port  Process\ntcp   LISTEN 0.0.0.0:22          sshd       ← von überall (ok, wenn gewollt + abgesichert)\ntcp   LISTEN 127.0.0.1:3306      mysqld     ← nur lokal ✅\ntcp   LISTEN 0.0.0.0:6379        redis      ← ❌ PROBLEM: Redis offen für alle\ntcp   LISTEN [::]:80             nginx      ← IPv6, von überall"},
        {"titel": "Docker: Port nur lokal veröffentlichen",
         "code": {"Bash": r'''# FALSCH – Datenbank für die ganze Welt, ufw hilft nicht:
#   docker run -d -p 5432:5432 postgres
# RICHTIG – nur vom Server selbst erreichbar:
docker run -d -p 127.0.0.1:5432:5432 postgres

# docker-compose.yml:
#   ports:
#     - "127.0.0.1:5432:5432"'''}},
        {"titel": "Sicher auf einen internen Dienst zugreifen: SSH-Tunnel (vom PC aus)",
         "text": "Leitet `localhost:8006` auf deinem PC verschlüsselt zum Proxmox-Host weiter – Port 8006 muss nirgends offen sein. Danach im Browser `https://localhost:8006` öffnen.",
         "code": {"Bash": r'''ssh -L 8006:127.0.0.1:8006 jorick@proxmox-host'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 Dienste und wie sie erreichbar sein sollten",
            "kopf": ["Dienst", "Port", "Richtig"],
            "zeilen": [
                ["MySQL / MariaDB", "3306", "bind-address = 127.0.0.1 oder nur internes Netz"],
                ["PostgreSQL", "5432", "listen_addresses = 'localhost'"],
                ["Redis", "6379", "bind 127.0.0.1 + Passwort"],
                ["MongoDB", "27017", "bindIp: 127.0.0.1 + Authentifizierung"],
                ["Proxmox Web-GUI", "8006", "nur Admin-Netz / VPN"],
                ["Docker-API", "2375 / 2376", "nie über Netzwerk (gibt root-Zugriff)"],
                ["Webmin / Cockpit", "10000 / 9090", "nur VPN"],
                ["SSH", "22", "Schlüssel + fail2ban, idealerweise nur VPN"],
                ["Webserver", "80 / 443", "öffentlich ok (dafür ist er da)"],
            ],
        },
    ],

    "sicherheit": [
        "**Nie** Datenbanken, Redis, MongoDB, Docker-API, Proxmox, Webmin/Cockpit, SMB oder RDP per Router-Portweiterleitung ins Internet stellen.",
        "Nie Docker-Ports ohne `127.0.0.1:` veröffentlichen, wenn sie nicht öffentlich sein sollen – **ufw schützt hier nicht**.",
        "Nie „nur kurz zum Testen“ einen Port öffnen und es dann vergessen – nach dem Test sofort Regel löschen und mit `nmap` von aussen nachprüfen.",
        "Nie fremde IP-Adressen oder Netze scannen – nur eigene Systeme.",
    ],
    "tipps": [
        "Regelmässig (z.B. monatlich) `sudo ss -tulpn` anschauen: Kenne ich jeden Dienst in der Liste?",
        "Von aussen prüfen ist Pflicht: Was `ss` und `ufw` sagen, ist nur die halbe Wahrheit (Router, Docker, IPv6).",
        "Nicht benötigte Dienste deinstallieren statt nur zu blockieren.",
    ],
    "fehler": [
        "Datenbank auf `0.0.0.0` konfiguriert, „weil sonst die App nicht verbindet“ – dabei läuft die App auf demselben Server (dann reicht 127.0.0.1).",
        "IPv6 vergessen: Dienst lauscht auf `[::]`, und der Router leitet IPv6 ohne NAT direkt weiter.",
        "Nach Umstellung auf 127.0.0.1 den Dienst nicht neu gestartet.",
    ],
    "siehe_auch": ["firewall_ufw", "netzwerk_diagnose", "todsuenden", "ssh_absichern"],
}
