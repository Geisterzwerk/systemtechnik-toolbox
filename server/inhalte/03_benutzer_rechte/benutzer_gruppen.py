# =============================================================================
# Thema: Benutzer & Gruppen  (Kategorie: Benutzer & Rechte)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Benutzer & Gruppen verwalten",
    "reihenfolge": 2,
    "kurz": "Benutzer anlegen, in Gruppen aufnehmen, sperren und löschen.",
    "stichworte": ["benutzer", "user", "gruppe", "group", "adduser", "useradd", "usermod", "deluser", "userdel",
                   "passwd", "passwort", "groups", "id", "whoami", "who", "last", "/etc/passwd", "/etc/shadow",
                   "/etc/group", "sperren", "lock", "dienstkonto", "chage"],

    "erklaerung": """
## Benutzer
Jeder Benutzer hat einen **Namen**, eine **Nummer (UID)**, ein **Home-Verzeichnis** und eine **Shell**. Neben echten Menschen gibt es viele **Systembenutzer** für Dienste (`www-data` für den Webserver, `mysql` …) – die können sich nicht einloggen und haben nur die Rechte, die der Dienst braucht.
## Gruppen
Eine Gruppe fasst Benutzer zusammen, damit man Rechte nicht jedem einzeln geben muss. Beispiele: **sudo** (darf Admin-Befehle), **adm** (darf Logs lesen), **docker** (darf Docker steuern – ist praktisch root!).
## adduser oder useradd?
- **`adduser`** (Ubuntu/Debian) – freundlich: legt Home an, fragt nach Passwort. **Für Menschen nehmen.**
- **`useradd`** – das Low-Level-Werkzeug, macht ohne Optionen fast nichts (kein Home, kein Passwort). Eher für Skripte.
## Wo stehen die Daten?
- `/etc/passwd` – alle Benutzer (Name, UID, Home, Shell) – für alle lesbar
- `/etc/shadow` – Passwort-Hashes – **nur root** darf lesen
- `/etc/group` – alle Gruppen und ihre Mitglieder
""",

    "befehle": [
        {"titel": "Wer bin ich, wer ist da?", "zeilen": [
            ("whoami", "Aktueller Benutzer"),
            ("id", "UID, Gruppen – steht sudo dabei?"),
            ("groups name", "Gruppen eines Benutzers"),
            ("who", "Wer ist gerade angemeldet?"),
            ("last -n 10", "Die letzten 10 Anmeldungen (mit IP)"),
            ("getent passwd | cut -d: -f1", "Alle Benutzernamen auflisten"),
        ]},
        {"titel": "Anlegen & ändern", "zeilen": [
            ("sudo adduser anna", "Neuen Benutzer anlegen (fragt Passwort und Infos)"),
            ("sudo usermod -aG sudo anna", "Zur Gruppe sudo hinzufügen (-a = anhängen!)"),
            ("sudo usermod -aG adm anna", "Darf Logs lesen"),
            ("sudo gpasswd -d anna sudo", "Aus einer Gruppe entfernen"),
            ("sudo passwd anna", "Passwort eines anderen Benutzers setzen"),
            ("sudo addgroup entwickler", "Neue Gruppe anlegen"),
            ("sudo adduser --system --group --no-create-home meindienst", "Systembenutzer für einen Dienst (kein Login)"),
        ]},
        {"titel": "Sperren & löschen", "zeilen": [
            ("sudo passwd -l anna", "Passwort sperren (SSH-Schlüssel gehen evtl. noch!)"),
            ("sudo usermod -s /usr/sbin/nologin anna", "Login komplett verhindern"),
            ("sudo chage -E 0 anna", "Konto ablaufen lassen (sicherste Sperre)"),
            ("sudo deluser --remove-home anna", "Benutzer inkl. Home-Verzeichnis löschen"),
        ]},
    ],

    "beispiele": [
        {"titel": "Neuer Admin-Kollege mit SSH-Schlüssel",
         "code": {"Bash": r'''sudo adduser anna
sudo usermod -aG sudo anna
sudo mkdir -p /home/anna/.ssh
echo "ssh-ed25519 AAAA...schluessel... anna@laptop" | sudo tee /home/anna/.ssh/authorized_keys
sudo chown -R anna:anna /home/anna/.ssh
sudo chmod 700 /home/anna/.ssh && sudo chmod 600 /home/anna/.ssh/authorized_keys'''}},
        {"titel": "Eine Zeile aus /etc/passwd lesen",
         "code": {"Bash": r'''grep anna /etc/passwd'''},
         "ausgabe": "anna:x:1001:1001:Anna Muster,,,:/home/anna:/bin/bash\n(Name : x=Passwort in shadow : UID : GID : Info : Home : Shell)"},
    ],

    "sicherheit": [
        "Nie Benutzer ohne Passwort oder mit schwachem Passwort anlegen, solange Passwort-Login per SSH erlaubt ist.",
        "Die Gruppe **docker** ist gleichwertig zu root – nur vertrauenswürdige Admins hinzufügen.",
        "Nie mehrere Personen mit **einem** gemeinsamen Konto arbeiten lassen – jeder bekommt ein eigenes (Nachvollziehbarkeit im auth.log).",
        "Wer geht, wird **sofort** gesperrt – inkl. Löschen seiner Schlüssel in `~/.ssh/authorized_keys`. `passwd -l` allein reicht bei SSH-Schlüsseln nicht!",
        "Nie `/etc/passwd`, `/etc/shadow` oder `/etc/group` von Hand bearbeiten – dafür gibt es `usermod`, `vipw` und `vigr`.",
    ],
    "tipps": [
        "Nach `usermod -aG` muss sich der Benutzer **neu anmelden**, damit die Gruppe wirkt.",
        "`last` und `sudo lastb` (fehlgeschlagene Logins) zeigen schnell, ob jemand Fremdes dran war.",
        "Dienste immer unter eigenem Systembenutzer laufen lassen, nie als root.",
    ],
    "fehler": [
        "`usermod -G sudo anna` ohne `-a` → Anna fliegt aus allen anderen Gruppen.",
        "`useradd anna` statt `adduser` → kein Home-Verzeichnis, kein Passwort, Login geht nicht.",
        "Benutzer gelöscht, aber seine Cron-Jobs, Dienste oder Dateien bleiben → vorher `sudo find / -user anna 2>/dev/null` prüfen.",
    ],
    "siehe_auch": ["sudo_root", "dateirechte", "ssh_verbinden", "ssh_absichern"],
}
