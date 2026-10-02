# =============================================================================
# Thema: SSH absichern  (Kategorie: Sicherheit)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "SSH absichern (Schlüssel, Konfiguration, fail2ban)",
    "reihenfolge": 3,
    "kurz": "Passwort-Login aus, root-Login aus, Angreifer automatisch sperren – ohne sich auszusperren.",
    "stichworte": ["ssh absichern", "härten", "hardening", "sshd_config", "sshd_config.d", "passwordauthentication",
                   "permitrootlogin", "pubkeyauthentication", "allowusers", "fail2ban", "brute force", "port ändern",
                   "ssh.socket", "cloud-init", "sshd -t", "2fa"],

    "erklaerung": """
## Das Ziel
Nur **bestimmte Benutzer**, nur mit **SSH-Schlüssel**, **kein root**, und wer es mit falschen Passwörtern probiert, wird **automatisch gesperrt**.
## Wo steht die Konfiguration?
- `/etc/ssh/sshd_config` – Hauptdatei
- `/etc/ssh/sshd_config.d/*.conf` – Zusatzdateien, werden **zuerst** gelesen. Bei SSH gilt: **der erste Treffer gewinnt!**
- **Falle:** Ubuntu-Cloud-Images legen oft `50-cloud-init.conf` mit `PasswordAuthentication yes` an – das überstimmt deine Einstellung in der Hauptdatei. Deshalb die eigene Datei mit niedriger Nummer anlegen: `00-haertung.conf`.
## Der sichere Ablauf
- 1. SSH-Schlüssel eingerichtet und **Login mit Schlüssel getestet** (Seite „Per SSH verbinden“)
- 2. Konfiguration schreiben
- 3. **`sudo sshd -t`** – Syntax prüfen (keine Ausgabe = ok)
- 4. `sudo systemctl reload ssh`
- 5. **Alte Sitzung offen lassen**, in einem neuen Fenster verbinden
- 6. Erst wenn das klappt, die alte Sitzung schliessen
## Port ändern?
Ein anderer Port als 22 reduziert den Lärm im Log (weniger Bots), ist aber **keine echte Sicherheit**. Wichtiger sind Schlüssel + fail2ban. Auf **Ubuntu 24.04** läuft SSH über `ssh.socket` – nach einer Port-Änderung braucht es `sudo systemctl daemon-reload` und `sudo systemctl restart ssh.socket`.
## fail2ban
Liest die Logs und sperrt IPs per Firewall, die sich zu oft falsch anmelden. Auf Ubuntu ist die SSH-Überwachung nach der Installation schon aktiv. Eigene Einstellungen in **`/etc/fail2ban/jail.local`** (nie `jail.conf` bearbeiten – wird bei Updates überschrieben).
""",

    "befehle": [
        {"titel": "Prüfen", "zeilen": [
            ("sudo sshd -t", "Konfiguration auf Fehler prüfen (keine Ausgabe = ok)"),
            ("sudo sshd -T | grep -Ei 'passwordauth|permitroot|pubkey|port'", "Was gilt WIRKLICH? (alle Dateien zusammen)"),
            ("ls /etc/ssh/sshd_config.d/", "Zusatzdateien (cloud-init-Falle!)"),
            ("sudo grep \"Failed password\" /var/log/auth.log | wc -l", "Wie viele Angriffsversuche?"),
        ]},
        {"titel": "Anwenden", "zeilen": [
            ("sudo nano /etc/ssh/sshd_config.d/00-haertung.conf", "Eigene Härtungs-Datei anlegen"),
            ("sudo systemctl reload ssh", "Konfiguration neu laden (bestehende Sitzungen bleiben)"),
        ]},
        {"titel": "fail2ban", "zeilen": [
            ("sudo apt install fail2ban", "Installieren (SSH-Schutz ist danach aktiv)"),
            ("sudo fail2ban-client status", "Welche Jails sind aktiv?"),
            ("sudo fail2ban-client status sshd", "Gesperrte IPs für SSH"),
            ("sudo fail2ban-client set sshd unbanip 192.168.1.20", "Eine (eigene!) IP wieder entsperren"),
        ]},
    ],

    "beispiele": [
        {"titel": "/etc/ssh/sshd_config.d/00-haertung.conf",
         "text": "`benutzer` durch deinen Benutzer ersetzen. **Vorher** Schlüssel-Login testen!",
         "code": {"Bash": r'''# Nur Schlüssel, kein Passwort
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes

# Kein direkter root-Login
PermitRootLogin no

# Nur diese Benutzer dürfen sich anmelden
AllowUsers benutzer

# Weniger Versuche, schneller Timeout
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no'''}},
        {"titel": "Prüfen und anwenden – mit Sicherheitsnetz",
         "code": {"Bash": r'''sudo sshd -t && sudo systemctl reload ssh
# JETZT: neues Terminal öffnen und  ssh benutzer@srv01  testen
# erst wenn das klappt, dieses Fenster schliessen'''}},
        {"titel": "fail2ban anpassen: /etc/fail2ban/jail.local",
         "code": {"Bash": r'''[DEFAULT]
bantime  = 1h
findtime = 10m
maxretry = 5
ignoreip = 127.0.0.1/8 192.168.1.0/24    # eigenes Netz nie sperren

[sshd]
enabled = true'''}},
    ],

    "sicherheit": [
        "Nie `PasswordAuthentication no` setzen, bevor der Schlüssel-Login **getestet** ist – sonst bist du ausgesperrt.",
        "Nie die einzige SSH-Sitzung schliessen, bevor eine neue erfolgreich aufgebaut wurde.",
        "Nie `PermitRootLogin yes` – Angreifer kennen den Benutzernamen root bereits.",
        "Nie `restart ssh` ohne vorheriges `sshd -t` – eine fehlerhafte Konfiguration verhindert den Start.",
        "SSH-Zugang für das Internet am besten gar nicht öffnen, sondern nur über **VPN** (WireGuard/Tailscale) erreichbar machen.",
        "Bei fail2ban das eigene Netz in `ignoreip` eintragen – sonst sperrst du dich nach ein paar Tippfehlern selbst.",
    ],
    "tipps": [
        "`sshd -T` zeigt die **tatsächlich** geltenden Werte – so entdeckt man die cloud-init-Falle sofort.",
        "Zusätzliche Sicherheit: 2-Faktor mit `libpam-google-authenticator` – aber erst, wenn die Grundlagen sitzen.",
        "Ausgesperrt? Über die **Proxmox-Konsole** oder direkt am Bildschirm anmelden (dort gilt die SSH-Konfiguration nicht) und korrigieren.",
    ],
    "fehler": [
        "Einstellung in `sshd_config` geändert, wirkt aber nicht → eine Datei in `sshd_config.d/` setzt den Wert vorher anders.",
        "`systemctl restart sshd` → auf Ubuntu heisst der Dienst **ssh**.",
        "Port in sshd_config geändert, aber auf 24.04 `ssh.socket` nicht neu gestartet, oder ufw nicht angepasst → ausgesperrt oder Port wirkt nicht.",
    ],
    "siehe_auch": ["ssh_verbinden", "firewall_ufw", "todsuenden", "benutzer_gruppen", "logs"],
}
