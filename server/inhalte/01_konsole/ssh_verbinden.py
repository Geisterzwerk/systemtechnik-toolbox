# =============================================================================
# Thema: Per SSH verbinden  (Kategorie: Konsole & SSH)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Per SSH verbinden",
    "reihenfolge": 2,
    "kurz": "Von Windows aus sicher auf den Server – mit Passwort oder (besser) mit SSH-Schlüssel.",
    "stichworte": ["ssh", "secure shell", "verbinden", "remote", "fernzugriff", "putty", "windows terminal",
                   "powershell", "schlüssel", "key", "ed25519", "public key", "private key", "authorized_keys",
                   "known_hosts", "fingerprint", "ssh config", "port 22", "tmux"],

    "erklaerung": """
## Was ist SSH?
**SSH (Secure Shell)** ist eine **verschlüsselte** Verbindung zu einer Konsole auf einem anderen Rechner – Standard-Port **22**. Alles, was du tippst, läuft verschlüsselt übers Netz. Windows 10/11 hat den SSH-Client schon eingebaut: einfach PowerShell oder Windows Terminal öffnen.
## Die erste Verbindung
`ssh benutzer@192.168.1.50` – beim allerersten Mal fragt SSH, ob du dem **Fingerprint** des Servers vertraust. Mit `yes` wird er in `~/.ssh/known_hosts` gespeichert. Ab dann erkennt SSH, falls sich jemand als dein Server ausgibt.
## Passwort oder Schlüssel?
- **Passwort:** einfach, aber angreifbar (Bots probieren rund um die Uhr Passwörter aus).
- **SSH-Schlüssel:** ein Schlüsselpaar – der **private Schlüssel** bleibt auf deinem PC (nie weitergeben!), der **öffentliche** (`.pub`) kommt auf den Server in `~/.ssh/authorized_keys`. Deutlich sicherer und bequemer.
- Empfehlung: Schlüssel vom Typ **ed25519**, mit **Passphrase** geschützt. Danach Passwort-Login abschalten (Seite „SSH absichern“).
## Schlüssel einrichten – der Ablauf
- 1. Auf **deinem PC** (PowerShell): `ssh-keygen -t ed25519` → erzeugt `id_ed25519` (privat) und `id_ed25519.pub` (öffentlich)
- 2. Öffentlichen Schlüssel auf den Server kopieren (Linux/Mac: `ssh-copy-id`, Windows: siehe Beispiel)
- 3. Testen: `ssh benutzer@server` → fragt nur noch nach der Passphrase des Schlüssels
- 4. **Erst wenn das klappt**, Passwort-Login auf dem Server abschalten
## Verbindung abgebrochen?
Bricht SSH ab, wird alles beendet, was in der Sitzung lief (z.B. ein langes Update!). Für lange Arbeiten **tmux** benutzen: `tmux` starten, arbeiten, bei Abbruch neu verbinden und mit `tmux attach` weitermachen.
""",

    "befehle": [
        {"titel": "Verbinden", "zeilen": [
            ("ssh benutzer@192.168.1.50", "Verbinden (Standard-Port 22)"),
            ("ssh -p 2222 benutzer@server", "Verbinden über anderen Port"),
            ("ssh -i ~/.ssh/id_ed25519 benutzer@server", "Bestimmten Schlüssel verwenden"),
            ("exit", "Verbindung sauber beenden (oder Ctrl+D)"),
        ]},
        {"titel": "Schlüssel (auf deinem PC)", "zeilen": [
            ("ssh-keygen -t ed25519 -C \"benutzer@laptop\"", "Neues Schlüsselpaar erzeugen (mit Passphrase!)"),
            ("ssh-copy-id benutzer@server", "Öffentlichen Schlüssel auf den Server kopieren (Linux/Mac)"),
            ("ssh-keygen -R 192.168.1.50", "Alten Fingerprint löschen (nach Neuinstallation des Servers)"),
        ]},
        {"titel": "tmux – Sitzungen, die einen Abbruch überleben", "zeilen": [
            ("tmux new -s arbeit", "Neue Sitzung mit Namen starten"),
            ("tmux attach -t arbeit", "Nach Verbindungsabbruch wieder anhängen"),
            ("tmux ls", "Laufende Sitzungen anzeigen"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 tmux-Tastenkürzel (zuerst Ctrl+B, dann Taste)",
            "kopf": ["Kürzel", "Wirkung"],
            "zeilen": [
                ["Ctrl+B, d", "Sitzung abhängen (läuft im Hintergrund weiter)"],
                ["Ctrl+B, c", "Neues Fenster"],
                ["Ctrl+B, n / p", "Nächstes / vorheriges Fenster"],
                ["Ctrl+B, %  bzw.  \"", "Fenster senkrecht / waagrecht teilen"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Windows: Schlüssel erzeugen und auf den Server kopieren (in PowerShell)",
         "text": "Windows hat kein `ssh-copy-id`. Diese Zeile macht dasselbe: öffentlichen Schlüssel lesen und auf dem Server an `authorized_keys` anhängen – mit den richtigen Rechten.",
         "code": {"Bash": r'''ssh-keygen -t ed25519 -C "benutzer@laptop"

type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh benutzer@192.168.1.50 "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"'''}},
        {"titel": "Abkürzungen: ~/.ssh/config (auf deinem PC)",
         "text": "Danach reicht `ssh srv01` statt der ganzen Zeile. Unter Windows: `C:\\Users\\<name>\\.ssh\\config`.",
         "code": {"Bash": r'''Host srv01
    HostName 192.168.1.50
    User benutzer
    Port 22
    IdentityFile ~/.ssh/id_ed25519'''}},
    ],

    "sicherheit": [
        "Den **privaten Schlüssel** (`id_ed25519` ohne .pub) **nie** kopieren, verschicken, in Git hochladen oder auf den Server legen.",
        "Warnung **REMOTE HOST IDENTIFICATION HAS CHANGED** nicht einfach wegklicken: Entweder wurde der Server neu installiert (dann `ssh-keygen -R` ok) – oder jemand hängt dazwischen (Man-in-the-Middle).",
        "Passwort-Login erst abschalten, wenn der Schlüssel-Login **getestet** ist – und dabei immer eine zweite Sitzung offen lassen.",
        "SSH nie ungeschützt mit Passwort ins Internet stellen – mindestens Schlüssel + fail2ban, besser nur über VPN (z.B. WireGuard).",
    ],
    "tipps": [
        "Schlüssel mit **Passphrase** schützen – mit `ssh-agent` muss man sie trotzdem nur einmal pro Sitzung eingeben.",
        "Mehrere Server? `~/.ssh/config` mit Abkürzungen spart viel Tipparbeit.",
        "Hängt eine SSH-Sitzung komplett? Nacheinander **Enter**, **~**, **.** tippen – beendet die Verbindung sofort.",
        "Lange Updates oder Kopieraktionen immer in **tmux** starten.",
    ],
    "fehler": [
        "`Permission denied (publickey)` → Schlüssel nicht auf dem Server, falscher Benutzer oder falsche Rechte auf `~/.ssh` (700) / `authorized_keys` (600).",
        "`Connection refused` → SSH-Dienst läuft nicht oder falscher Port. `Connection timed out` → Firewall oder falsche IP.",
        "Öffentlichen und privaten Schlüssel verwechselt – auf den Server gehört nur die **.pub**-Datei.",
    ],
    "siehe_auch": ["ssh_absichern", "firewall_ufw", "dateien_uebertragen", "dateirechte", "terminal_shell"],
}
