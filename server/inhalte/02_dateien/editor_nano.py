# =============================================================================
# Thema: Editor nano (+ vim-Notfallwissen)  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Editor: nano (und vim im Notfall)",
    "reihenfolge": 4,
    "kurz": "Konfigurationsdateien direkt auf dem Server bearbeiten – und wie man aus vim wieder herauskommt.",
    "stichworte": ["editor", "nano", "vim", "vi", "bearbeiten", "speichern", "beenden", "texteditor",
                   "konfiguration bearbeiten", "sudoedit", ":wq", ":q!", "aus vim raus"],

    "erklaerung": """
## nano – der einfache Editor
`nano datei` öffnet die Datei. Unten stehen die wichtigsten Kürzel – **^** bedeutet **Ctrl**, **M-** bedeutet **Alt**.
- **Ctrl + O**, Enter – speichern („Write Out“)
- **Ctrl + X** – beenden (fragt, falls noch nicht gespeichert)
- Systemdateien brauchen Admin-Rechte: `sudo nano /etc/…`
## Systemdateien sicher bearbeiten
- 1. Sicherung: `sudo cp datei datei.bak`
- 2. Bearbeiten: `sudo nano datei`
- 3. **Prüfen**, wenn der Dienst das kann (`sudo nginx -t`, `sudo sshd -t`, `sudo visudo -c`)
- 4. Erst dann den Dienst neu laden/starten
## vim – falls man darin landet
Manche Befehle (z.B. `crontab -e` beim ersten Mal, `git commit`) öffnen **vim**. vim hat Modi: Man startet im **Befehlsmodus** – Tippen fügt nichts ein!
- **i** → Einfügemodus (jetzt kann man schreiben)
- **Esc** → zurück in den Befehlsmodus
- **:wq** + Enter → speichern und beenden
- **:q!** + Enter → beenden **ohne** Speichern (der Notausgang)
Standard-Editor dauerhaft auf nano stellen: `sudo update-alternatives --config editor` bzw. `select-editor`.
""",

    "befehle": [
        {"titel": "nano", "zeilen": [
            ("nano notizen.txt", "Datei öffnen (oder neu anlegen)"),
            ("sudo nano /etc/hosts", "Systemdatei als Admin bearbeiten"),
            ("nano -l datei.conf", "Mit Zeilennummern (hilft bei Fehlermeldungen „line 42“)"),
            ("sudo nano +42 /etc/ssh/sshd_config", "Direkt zu Zeile 42 springen"),
            ("select-editor", "Standard-Editor wählen (für crontab -e usw.)"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 nano-Tastenkürzel",
            "kopf": ["Kürzel", "Wirkung"],
            "zeilen": [
                ["Ctrl + O, Enter", "speichern"],
                ["Ctrl + X", "beenden"],
                ["Ctrl + W", "suchen (Alt + W: weitersuchen)"],
                ["Ctrl + \\", "suchen und ersetzen"],
                ["Ctrl + K / Ctrl + U", "Zeile ausschneiden / einfügen"],
                ["Alt + U / Alt + E", "rückgängig / wiederholen"],
                ["Ctrl + _", "zu Zeile springen"],
                ["Alt + #", "Zeilennummern ein/aus"],
                ["Ctrl + A / Ctrl + E", "Zeilenanfang / Zeilenende"],
            ],
        },
        {
            "titel": "📊 vim-Notfallkarte",
            "kopf": ["Eingabe", "Wirkung"],
            "zeilen": [
                ["Esc", "immer zuerst: zurück in den Befehlsmodus"],
                ["i", "Einfügemodus – jetzt tippen"],
                [":w", "speichern"],
                [":wq  (oder :x)", "speichern und beenden"],
                [":q!", "beenden OHNE Speichern"],
                ["u", "rückgängig"],
                ["/wort", "suchen"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Sicherer Ablauf am Beispiel SSH-Konfiguration",
         "code": {"Bash": r'''sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak
sudo nano /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl reload ssh     # nur neu laden, wenn der Test ok ist'''}},
    ],

    "sicherheit": [
        "Nie `/etc/sudoers` mit nano bearbeiten – immer `sudo visudo`. Ein Tippfehler dort sperrt sonst **alle** sudo-Rechte.",
        "Nie eine wichtige Konfiguration ohne Sicherungskopie ändern.",
        "Nach Änderungen an SSH, Firewall oder Netzwerk die **aktuelle Sitzung offen lassen** und in einer zweiten testen, ob man noch hineinkommt.",
    ],
    "tipps": [
        "Windows-Editoren fügen oft `\\r\\n` (CRLF) ein – Skripte dann mit nano direkt auf dem Server schreiben, oder `dos2unix datei` benutzen.",
        "Einrückungen in **YAML** (netplan, docker-compose) nur mit **Leerzeichen**, nie mit Tab.",
        "Nur lesen? Dann `less` statt `nano` – kein Risiko, etwas zu verändern.",
    ],
    "fehler": [
        "Mit `nano` statt `sudo nano` bearbeitet → beim Speichern `Permission denied`, Änderungen weg. (Ctrl+O mit anderem Namen z.B. in /tmp speichern und danach mit sudo kopieren.)",
        "In vim gefangen → **Esc**, dann `:q!` und Enter.",
        "Nach dem Bearbeiten Dienst nicht neu geladen → Änderung wirkt nicht.",
    ],
    "siehe_auch": ["dateien_anzeigen", "sudo_root", "dienste_systemctl", "ssh_absichern"],
}
