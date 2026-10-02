# =============================================================================
# Thema: Firewall mit ufw  (Kategorie: Sicherheit)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Firewall: ufw",
    "reihenfolge": 2,
    "kurz": "Alles zu, nur das Nötige auf – und dabei SSH nicht vergessen.",
    "stichworte": ["firewall", "ufw", "uncomplicated firewall", "port öffnen", "port schliessen", "freigeben",
                   "allow", "deny", "limit", "iptables", "nftables", "regel", "eingehend", "ausgehend",
                   "default deny", "portfreigabe", "subnetz", "ipv6"],

    "erklaerung": """
## Das Prinzip: Standardmässig alles zu
Eine gute Firewall-Konfiguration ist eine **Positivliste**: Eingehend ist **alles verboten**, und man erlaubt gezielt nur, was gebraucht wird (z.B. SSH, HTTP/HTTPS). Ausgehend darf der Server normal ins Internet (Updates).
## ufw = uncomplicated firewall
Auf Ubuntu installiert, aber **ausgeschaltet**. ufw ist eine einfache Bedienung für die Linux-Firewall (nftables/iptables).
## Die richtige Reihenfolge – sonst bist du ausgesperrt
- 1. Standard-Regeln setzen (eingehend deny, ausgehend allow)
- 2. **SSH erlauben** (`sudo ufw allow OpenSSH` bzw. deinen eigenen Port)
- 3. Weitere Dienste erlauben (80, 443 …)
- 4. **Erst jetzt** `sudo ufw enable`
- 5. In einer **neuen** SSH-Sitzung testen
## So eng wie möglich
Statt „Port 22 für die ganze Welt“ besser nur aus dem eigenen Netz: `sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp`. Mit `limit` statt `allow` werden IPs mit zu vielen Verbindungsversuchen kurz gesperrt (Schutz gegen Passwort-Raten).
""",

    "befehle": [
        {"titel": "Status", "zeilen": [
            ("sudo ufw status verbose", "An/aus, Standard-Regeln, alle Regeln"),
            ("sudo ufw status numbered", "Regeln mit Nummer (zum Löschen)"),
            ("sudo ufw app list", "Vordefinierte Profile (OpenSSH, Nginx Full …)"),
        ]},
        {"titel": "Einrichten (in dieser Reihenfolge!)", "zeilen": [
            ("sudo ufw default deny incoming", "Eingehend alles verbieten"),
            ("sudo ufw default allow outgoing", "Ausgehend erlauben"),
            ("sudo ufw allow OpenSSH", "SSH erlauben (Port 22) – VOR enable!"),
            ("sudo ufw enable", "Firewall einschalten"),
        ]},
        {"titel": "Regeln", "zeilen": [
            ("sudo ufw allow 443/tcp", "HTTPS für alle"),
            ("sudo ufw allow \"Nginx Full\"", "Profil: 80 und 443"),
            ("sudo ufw allow from 192.168.1.0/24 to any port 22 proto tcp", "SSH nur aus dem Heimnetz"),
            ("sudo ufw limit OpenSSH", "SSH mit Bremse gegen Brute-Force"),
            ("sudo ufw deny from 203.0.113.7", "Eine IP komplett sperren"),
            ("sudo ufw delete 3", "Regel Nr. 3 löschen (Nummer aus status numbered)"),
            ("sudo ufw delete allow 8080/tcp", "Regel über ihren Inhalt löschen"),
            ("sudo ufw logging low", "Blockierte Verbindungen protokollieren (/var/log/ufw.log)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Webserver sicher einrichten",
         "code": {"Bash": r'''sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow "Nginx Full"
sudo ufw enable
sudo ufw status verbose'''},
         "ausgabe": "Status: active\nDefault: deny (incoming), allow (outgoing), deny (routed)\n\nTo                  Action      From\n--                  ------      ----\n22/tcp (OpenSSH)    ALLOW IN    Anywhere\n80,443/tcp (Nginx Full) ALLOW IN Anywhere\n..."},
        {"titel": "SSH läuft auf einem anderen Port?",
         "text": "Dann **diesen** Port erlauben – `OpenSSH` meint immer Port 22.",
         "code": {"Bash": r'''sudo ufw allow 2222/tcp
sudo ufw delete allow OpenSSH      # erst nachdem der Login über 2222 getestet ist'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 Welche Ports für welchen Server?",
            "kopf": ["Server-Typ", "Öffnen", "NICHT öffnen"],
            "zeilen": [
                ["jeder", "22 (SSH) – möglichst nur aus eigenem Netz/VPN", "–"],
                ["Webserver", "80, 443", "Datenbank-Port"],
                ["VPN (WireGuard)", "51820/udp", "–"],
                ["Datenbank", "nichts von aussen – nur vom App-Server: allow from IP to any port 5432", "3306/5432 für Anywhere"],
                ["Proxmox-Host", "8006 und 22 nur aus dem Admin-Netz", "8006 ins Internet"],
            ],
        },
    ],

    "sicherheit": [
        "**Nie `sudo ufw enable` per SSH, ohne vorher SSH erlaubt zu haben.** Die Verbindung bricht nicht sofort ab – aber jede neue wird blockiert. Beim nächsten Trennen bist du draussen.",
        "Nie `sudo ufw disable`, um „kurz etwas zu testen“ – stattdessen gezielt eine Regel hinzufügen und danach wieder löschen.",
        "Nie ganze Portbereiche (`ufw allow 1000:9000/tcp`) oder `allow from any` für interne Dienste öffnen.",
        "**Docker umgeht ufw!** Ein Container mit `-p 5432:5432` ist trotz ufw von aussen erreichbar. Ports in Docker immer an `127.0.0.1` binden (`-p 127.0.0.1:5432:5432`). Siehe „Offene Ports“.",
        "Die Server-Firewall ist nur eine Schicht: Auch Router-Portweiterleitungen und Proxmox-/Cloud-Firewall prüfen.",
    ],
    "tipps": [
        "Regeln kann man **vor** `enable` hinzufügen – so ist beim Einschalten schon alles richtig.",
        "ufw regelt IPv4 **und** IPv6 automatisch (in `/etc/default/ufw` IPV6=yes).",
        "In Proxmox-VMs: Wer die Proxmox-Firewall nutzt, sollte trotzdem ufw in der VM haben (zwei Schichten).",
        "Ausgesperrt? Über die **Proxmox-Konsole** / den Bildschirm anmelden und `sudo ufw allow OpenSSH` nachholen.",
    ],
    "fehler": [
        "Nach Ändern des SSH-Ports nur die sshd_config angepasst, aber nicht ufw → ausgesperrt.",
        "Regeln hinzugefügt, aber ufw ist gar nicht aktiv (`Status: inactive`).",
        "`ufw allow 443` ohne `/tcp` → öffnet TCP **und** UDP (meist harmlos, aber ungenau).",
    ],
    "siehe_auch": ["offene_ports", "ssh_absichern", "todsuenden", "netzwerk_diagnose"],
}
