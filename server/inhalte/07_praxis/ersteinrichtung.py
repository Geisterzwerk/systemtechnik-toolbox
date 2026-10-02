# =============================================================================
# Thema: Ersteinrichtung eines Ubuntu-Servers  (Kategorie: Praxis)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Checkliste: Neuer Ubuntu-Server",
    "reihenfolge": 1,
    "kurz": "Die ersten 30 Minuten auf einem frischen Server – Schritt für Schritt, in der richtigen Reihenfolge.",
    "stichworte": ["ersteinrichtung", "neuer server", "checkliste", "setup", "einrichten", "installation",
                   "grundkonfiguration", "erste schritte", "härtung", "baseline", "ubuntu server installieren",
                   "proxmox vm", "qemu-guest-agent"],

    "erklaerung": """
## Die Reihenfolge ist wichtig
Erst **Zugang sichern** (Benutzer, Schlüssel), dann **zumachen** (SSH härten, Firewall), dann **einrichten**. Wer die Firewall vor dem SSH-Schlüssel einschaltet oder den Passwort-Login abschaltet, bevor der Schlüssel funktioniert, sperrt sich aus.
## Die Checkliste
- ☐ 1. **Updates** installieren und neu starten
- ☐ 2. **Hostname** und **Zeitzone** setzen
- ☐ 3. **Eigener Admin-Benutzer** mit sudo (falls bei der Installation nicht angelegt)
- ☐ 4. **SSH-Schlüssel** hinterlegen und Login damit **testen**
- ☐ 5. **SSH härten:** kein Passwort, kein root (zweite Sitzung offen lassen!)
- ☐ 6. **Firewall:** SSH erlauben, dann ufw einschalten
- ☐ 7. **fail2ban** installieren
- ☐ 8. **Automatische Sicherheitsupdates** prüfen
- ☐ 9. Bei Proxmox-VM: **qemu-guest-agent** installieren
- ☐ 10. **Backup** einrichten und **Snapshot** des sauberen Grundzustands
- ☐ 11. Alles dokumentieren: IP, Zweck, Benutzer, offene Ports
""",

    "beispiele": [
        {"titel": "Schritt 1–3: Updates, Name, Zeit, Benutzer",
         "code": {"Bash": r'''sudo apt update && sudo apt full-upgrade -y
sudo hostnamectl set-hostname srv-web01
sudo nano /etc/hosts                               # 127.0.1.1 srv-web01
sudo timedatectl set-timezone Europe/Zurich
sudo apt install -y htop curl git tmux ncdu unzip
# nur falls noch kein eigener Admin existiert:
sudo adduser jorick && sudo usermod -aG sudo jorick
sudo reboot'''}},
        {"titel": "Schritt 4: Schlüssel vom PC hinterlegen (auf dem PC, PowerShell)",
         "code": {"Bash": r'''ssh-keygen -t ed25519 -C "jorick@laptop"
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh jorick@192.168.1.50 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
ssh jorick@192.168.1.50            # muss OHNE Server-Passwort klappen'''}},
        {"titel": "Schritt 5: SSH härten (Sitzung offen lassen!)",
         "code": {"Bash": r'''sudo tee /etc/ssh/sshd_config.d/00-haertung.conf > /dev/null <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
AllowUsers jorick
MaxAuthTries 3
EOF
sudo sshd -t && sudo systemctl reload ssh
sudo sshd -T | grep -Ei 'passwordauthentication|permitrootlogin'
# -> neues Fenster: ssh jorick@srv-web01  testen!'''}},
        {"titel": "Schritt 6–9: Firewall, fail2ban, Updates, Guest-Agent",
         "code": {"Bash": r'''sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw enable
sudo apt install -y fail2ban
systemctl is-enabled unattended-upgrades
sudo apt install -y qemu-guest-agent && sudo systemctl enable --now qemu-guest-agent   # nur Proxmox-VM'''}},
        {"titel": "Kontrolle am Schluss",
         "code": {"Bash": r'''sudo ufw status verbose
sudo ss -tulpn
sudo fail2ban-client status sshd
timedatectl | grep "Time zone"
systemctl --failed'''}},
    ],

    "sicherheit": [
        "Nie Passwort-Login abschalten, bevor der Schlüssel-Login getestet ist.",
        "Nie `ufw enable` vor `ufw allow OpenSSH`.",
        "Nie einen frisch installierten Server mit Passwort-SSH direkt ins Internet hängen – erst die Checkliste abarbeiten.",
        "Standard-Passwörter von vorinstallierten Images (Cloud-Anbieter, Vorlagen) sofort ändern.",
    ],
    "tipps": [
        "In Proxmox: Nach der Checkliste die VM als **Template** speichern – jeder neue Server startet dann schon gehärtet.",
        "Die Befehle als eigenes Skript `setup.sh` speichern – beim nächsten Server nur noch prüfen und ausführen.",
        "Ubuntu-Installer: „Install OpenSSH server“ ankreuzen und dort direkt den **GitHub-/Launchpad-Schlüssel importieren** – spart Schritt 4.",
    ],
    "fehler": [
        "`AllowUsers` mit falschem Benutzernamen → niemand kommt mehr rein.",
        "Nach `hostnamectl` die `/etc/hosts` vergessen → sudo meldet „unable to resolve host“.",
        "Snapshot vergessen → bei späterem Fehler kein sauberer Rückweg.",
    ],
    "siehe_auch": ["ssh_verbinden", "ssh_absichern", "firewall_ufw", "updates", "backups", "todsuenden"],
}
