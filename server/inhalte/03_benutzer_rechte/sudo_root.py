# =============================================================================
# Thema: sudo & root  (Kategorie: Benutzer & Rechte)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "sudo & root – Admin-Rechte",
    "reihenfolge": 1,
    "kurz": "Warum man nicht als root arbeitet und wie sudo genau funktioniert.",
    "stichworte": ["sudo", "root", "admin", "administrator", "superuser", "su", "sudo -i", "sudo -s", "visudo",
                   "sudoers", "sudoers.d", "nopasswd", "rechte", "berechtigung", "permission denied",
                   "sudo gruppe", "sudo -l"],

    "erklaerung": """
## Stell dir vor …
In einem Hotel gibt es einen **Generalschlüssel**, der alle Türen öffnet. Den trägt niemand den ganzen Tag herum – man holt ihn an der Rezeption, öffnet die eine Tür und gibt ihn zurück. `sudo` ist genau das: Admin-Rechte nur für einen einzelnen Befehl, und jede Ausleihe wird notiert.
## root – der allmächtige Benutzer
**root** (Benutzer-ID 0) darf auf einem Linux-System **alles**: jede Datei löschen, jeden Prozess beenden, jede Einstellung ändern. Es gibt keine Sicherheitsabfrage. Auf Ubuntu ist der root-Login deshalb **standardmässig gesperrt**.
## sudo – Admin-Rechte nur für einen Befehl
`sudo befehl` führt **einen** Befehl mit root-Rechten aus.
- Es wird nach **deinem eigenen** Passwort gefragt (nicht nach dem von root).
- Danach merkt sich sudo das ca. **15 Minuten** lang.
- Jeder sudo-Aufruf wird protokolliert (`/var/log/auth.log`) – man sieht später, wer was gemacht hat.
- Wer sudo darf, steht in `/etc/sudoers` – auf Ubuntu: alle Mitglieder der Gruppe **sudo**.
## Warum nicht einfach immer root?
- Ein Tippfehler als root kann das ganze System zerstören.
- Programme, die du startest, laufen mit vollen Rechten – auch fehlerhafte oder bösartige.
- Keine Nachvollziehbarkeit, wer was gemacht hat.
**Regel:** Normal arbeiten, `sudo` nur dort, wo es nötig ist.
## Wann braucht es sudo?
Wenn man etwas **ausserhalb des eigenen Home-Verzeichnisses** ändert: Pakete installieren, Dateien in `/etc` bearbeiten, Dienste steuern, Logs in `/var/log` lesen, Ports unter 1024 öffnen.
## 🔬 Genauer hingeschaut
- **sudo merkt sich dich kurz:** Nach der Passworteingabe fragt sudo eine Weile nicht erneut (bei Ubuntu standardmässig 15 Minuten). `sudo -k` beendet diese Frist sofort.
- **Alles wird protokolliert:** Jeder sudo-Befehl landet im Log (`journalctl` bzw. `/var/log/auth.log`). So lässt sich nachvollziehen, wer wann was als Admin gemacht hat.
- **Root-Shell sparsam:** `sudo -i` öffnet eine Shell als root. Praktisch für viele Admin-Schritte nacheinander – aber jeder Tippfehler hat dann volle Wirkung. Danach mit `exit` sofort verlassen.
## 💡 Wusstest du?
- Ein bekannter Comic (xkcd 149) zeigt, wie jemand „Mach mir ein Sandwich“ verweigert bekommt – und mit „sudo mach mir ein Sandwich“ sofort Erfolg hat.
""",

    "befehle": [
        {"titel": "sudo benutzen", "zeilen": [
            ("sudo apt update", "Einen Befehl als root"),
            ("sudo !!", "Letzten Befehl mit sudo wiederholen"),
            ("sudo -l", "Was darf ich mit sudo?"),
            ("sudo -i", "Root-Shell (mit root-Umgebung) – nur für längere Admin-Arbeiten, danach exit!"),
            ("sudo -u www-data ls /var/www", "Befehl als ANDERER Benutzer ausführen (hier: Webserver)"),
            ("sudo -k", "Gespeichertes Passwort vergessen (sudo fragt beim nächsten Mal wieder)"),
            ("id", "Mein Benutzer und meine Gruppen (steht sudo dabei?)"),
        ]},
        {"titel": "sudo-Rechte verwalten", "zeilen": [
            ("sudo usermod -aG sudo name", "Benutzer darf sudo verwenden"),
            ("sudo deluser name sudo", "sudo-Recht wieder entziehen"),
            ("sudo visudo", "sudoers sicher bearbeiten (prüft auf Fehler)"),
            ("sudo visudo -f /etc/sudoers.d/backup", "Eigene Regel in separater Datei"),
            ("sudo grep sudo /var/log/auth.log | tail", "Wer hat zuletzt sudo benutzt?"),
        ]},
    ],

    "beispiele": [
        {"titel": "Eng begrenzte Regel: Ein Backup-Benutzer darf NUR rsync als root",
         "text": "Datei mit `sudo visudo -f /etc/sudoers.d/backup` anlegen. So bekommt ein Dienstkonto nicht gleich alle Rechte.",
         "code": {"Bash": r'''# /etc/sudoers.d/backup
backup ALL=(root) NOPASSWD: /usr/bin/rsync'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 sudo, sudo -i, su – was ist der Unterschied?",
            "kopf": ["Befehl", "Wirkung", "Empfehlung"],
            "zeilen": [
                ["sudo befehl", "ein Befehl als root, dein Passwort, protokolliert", "✅ Standard"],
                ["sudo -i", "Login-Shell als root (Umgebung von root)", "⚠ nur kurz, danach exit"],
                ["sudo -s", "Shell als root, aber deine Umgebung", "⚠ nur kurz"],
                ["su -", "wird zu root mit ROOT-Passwort (auf Ubuntu gesperrt)", "❌ nicht verwenden"],
                ["sudo su", "Umweg zu einer root-Shell", "❌ unnötig – sudo -i nehmen"],
            ],
        },
    ],

    "sicherheit": [
        "Nie `/etc/sudoers` direkt mit nano bearbeiten – nur mit `sudo visudo`. Ein Syntaxfehler sperrt sonst **jedes** sudo, und man kommt nur noch über den Rettungsmodus rein.",
        "Nie `NOPASSWD: ALL` für normale Benutzer – dann reicht ein gestohlener SSH-Zugang für volle Kontrolle.",
        "Nie dem root-Konto ein Passwort geben und root-Login per SSH erlauben.",
        "Nie in einer `sudo -i`-Shell „vergessen“ und weiterarbeiten – der Prompt zeigt **#**. Nach der Admin-Arbeit sofort `exit`.",
        "Nie Befehle aus Anleitungen mit sudo ausführen, die du nicht verstehst.",
    ],
    "tipps": [
        "`-a` bei `usermod -aG` ist entscheidend: ohne `-a` wird der Benutzer aus allen anderen Gruppen **entfernt**.",
        "Neue Gruppenzugehörigkeit wirkt erst nach **neuem Anmelden** (SSH trennen und neu verbinden).",
        "Immer mindestens **zwei** Benutzer mit sudo-Rechten – falls einer ausgesperrt ist.",
    ],
    "fehler": [
        "`name is not in the sudoers file. This incident will be reported.` → Benutzer ist nicht in der Gruppe sudo.",
        "`sudo cd /root` → funktioniert nicht, cd ist ein Shell-Befehl. Stattdessen `sudo ls /root` oder kurz `sudo -i`.",
        "Dateien mit `sudo` im eigenen Home erstellt → gehören dann root, und man kann sie selbst nicht mehr bearbeiten. Mit `sudo chown name:name datei` zurückholen.",
    ],
    "siehe_auch": ["benutzer_gruppen", "dateirechte", "todsuenden", "ssh_absichern"],
}
