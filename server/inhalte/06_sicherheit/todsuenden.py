# =============================================================================
# Thema: Die Todsünden - was man NIE tun darf  (Kategorie: Sicherheit)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# Rot markierte Befehle: programmieren/engine/syntax.py GEFAHR_MUSTER
# =============================================================================

THEMA = {
    "titel": "Die Todsünden – was man NIE tun darf",
    "reihenfolge": 1,
    "kurz": "Die Fehler, die einen Server zerstören, aussperren oder für Angreifer öffnen. Einmal lesen, nie machen.",
    "stichworte": ["todsünden", "verboten", "niemals", "nie", "gefährlich", "gefahr", "sicherheit", "fehler",
                   "security", "härtung", "hardening", "rm -rf", "chmod 777", "port öffnen", "datenbank offen",
                   "root login", "curl bash", "aussperren", "best practice"],

    "erklaerung": """
## Warum diese Seite?
Ein Server im Internet wird **innerhalb von Minuten** nach dem Einschalten von Bots gescannt und angegriffen. Die meisten Einbrüche passieren nicht durch geniale Hacker, sondern durch **eine** der Todsünden unten. Und die meisten zerstörten Server hat der eigene Admin mit **einem** Befehl kaputt gemacht.
## A – Sich selbst aussperren
- **Firewall einschalten, ohne SSH zu erlauben.** Immer zuerst `sudo ufw allow OpenSSH`, dann `sudo ufw enable`.
- **SSH-Konfiguration ändern und die einzige Sitzung schliessen.** Immer eine zweite Sitzung testen, bevor die erste zugeht.
- **Netzwerk per SSH mit `netplan apply` ändern.** Immer `netplan try`.
- **fstab ändern und ohne Test neu starten.** Immer `findmnt --verify` und `mount -a` vorher.
- **sudoers mit nano bearbeiten.** Immer `visudo`.
## B – Das System zerstören
- **`rm -rf` mit Variablen, `*` oder als root in `/`.** Erst `ls` mit demselben Muster, dann `rm`.
- **`chmod -R` / `chown -R` auf Systemordner** (`/`, `/etc`, `/usr`, `/var`).
- **`dd`, `mkfs`, `fdisk` auf das falsche Gerät.** Mit `lsblk -f` dreifach prüfen.
- **`>` statt `>>`** auf Systemdateien (überschreibt statt anhängen).
## C – Die Tür für Angreifer öffnen
- **Datenbank-, Admin- und Management-Ports ins Internet** (MySQL 3306, PostgreSQL 5432, Redis 6379, MongoDB 27017, Proxmox 8006, Docker-API 2375, SMB 445, RDP 3389). Diese Dienste gehören **nur ins interne Netz oder hinter ein VPN**.
- **SSH mit Passwort-Login im Internet**, schlimmer noch **root-Login erlaubt**.
- **`chmod 777`** – jeder Prozess darf die Datei verändern, auch ein gehackter Webserver.
- **`curl … | sudo bash`** mit Skripten, die man nicht gelesen hat.
- **Keine Updates** – bekannte Lücken werden automatisiert ausgenutzt.
- **Standard-Passwörter** von Anwendungen (admin/admin) nicht geändert.
- **Docker-Ports mit `-p 3306:3306` veröffentlicht** – Docker umgeht dabei ufw! Siehe Seite „Offene Ports“.
- **Private Schlüssel oder `.env`-Dateien** in Git, im Webordner oder per Mail verschickt.
## D – Ohne Netz und doppelten Boden
- **Kein Backup** – oder ein Backup, dessen Wiederherstellung nie getestet wurde.
- **Backup auf demselben Server/derselben Platte** – Ransomware und Plattendefekt nehmen beides mit.
- **Als root arbeiten** statt mit sudo.
""",

    "beispiele": [
        {"titel": "So sehen die gefährlichen Befehle aus (rot markiert – NICHT ausführen)",
         "text": "Diese Befehle erkennt die Toolbox automatisch und hinterlegt sie rot – auch auf allen anderen Seiten.",
         "code": {"Bash": r'''rm -rf /$ORDNER             # ist $ORDNER leer: löscht alles
sudo chmod -R 777 /var/www  # jeder darf alles
sudo ufw disable            # Firewall aus
curl -fsSL https://irgendwas.sh | sudo bash
sudo dd if=image.iso of=/dev/sda   # falsches Gerät = System weg
PermitRootLogin yes         # in sshd_config
PasswordAuthentication yes  # in sshd_config (im Internet)'''}},
        {"titel": "… und so macht man es richtig",
         "code": {"Bash": r'''ls /pfad/zum/ordner/ && rm -r /pfad/zum/ordner/     # erst schauen
sudo chown -R www-data:www-data /var/www/seite       # richtiger Besitzer statt 777
sudo ufw allow OpenSSH && sudo ufw enable            # SSH zuerst erlauben
curl -fsSLO https://seite/install.sh && less install.sh   # erst lesen
lsblk -f                                             # Gerät dreimal prüfen'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 Checkliste vor gefährlichen Aktionen",
            "kopf": ["Frage", "Warum"],
            "zeilen": [
                ["Auf welchem Server bin ich? (Prompt!)", "Befehl auf Produktion statt Testserver"],
                ["Habe ich ein aktuelles Backup / einen Snapshot?", "Rückweg, falls es schiefgeht"],
                ["Habe ich eine zweite Sitzung / Konsolenzugang?", "Rückweg, falls ich mich aussperre"],
                ["Habe ich mit ls / --dry-run / -t / -n getestet?", "sehen, was passieren WÜRDE"],
                ["Verstehe ich jeden Teil des Befehls?", "kopierte Befehle aus dem Internet"],
                ["Muss das wirklich mit sudo?", "Schaden begrenzen"],
            ],
        },
    ],

    "sicherheit": [
        "Nie Datenbank-/Admin-Ports (3306, 5432, 6379, 27017, 8006, 2375, 445, 3389) ins Internet freigeben – weder per Router-Portweiterleitung noch per Cloud-Firewall noch per Docker `-p`.",
        "Nie SSH mit Passwort-Login oder root-Login ins Internet.",
        "Nie `ufw enable` ohne vorheriges `ufw allow OpenSSH`.",
        "Nie `chmod 777`, nie `chmod -R`/`chown -R` auf Systemordner.",
        "Nie `rm -rf` mit Variablen/Wildcards ohne vorheriges `ls` mit exakt demselben Pfad.",
        "Nie fremde Skripte ungelesen mit sudo ausführen.",
        "Nie ohne getestetes Backup an einem wichtigen Server arbeiten.",
    ],
    "tipps": [
        "Vor jeder riskanten Arbeit an einer **Proxmox-VM**: **Snapshot** machen. Das ist der schnellste Rückweg.",
        "Wichtige Befehle erst auf einem **Testserver** (VM) ausprobieren.",
        "Eigene Merkliste führen: Jeder Fehler, den man einmal gemacht hat, kommt auf die Liste.",
    ],
    "fehler": [
        "„Nur kurz zum Testen“ einen Port geöffnet und vergessen, ihn wieder zu schliessen.",
        "„Permission denied“ mit `chmod 777` gelöst statt den Besitzer zu korrigieren.",
        "Anleitung aus dem Internet 1:1 kopiert, ohne zu verstehen, was sie macht.",
    ],
    "siehe_auch": ["firewall_ufw", "ssh_absichern", "offene_ports", "updates", "backups", "dateirechte"],
}
