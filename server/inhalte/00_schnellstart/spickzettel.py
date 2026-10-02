# =============================================================================
# Thema: Spickzettel - die 60 wichtigsten Befehle  (Kategorie: Schnellstart)
# -----------------------------------------------------------------------------
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# Jede Zeile in "befehle" bekommt einen 📋-Knopf (programmieren/engine/befehlsliste.py).
# GENAU 60 Befehle: 6 + 8 + 7 + 8 + 9 + 9 + 8 + 5
# =============================================================================

THEMA = {
    "titel": "Spickzettel: 60 wichtigste Befehle",
    "reihenfolge": 1,
    "kurz": "Alles, was man auf einem Ubuntu-Server täglich braucht – nach Thema sortiert, jeder Befehl mit 📋.",
    "stichworte": ["spickzettel", "cheatsheet", "übersicht", "befehle", "kommandos", "wichtigste", "liste",
                   "linux", "ubuntu", "server", "konsole", "terminal", "bash"],

    "erklaerung": """
## So liest du die Befehle
- Wörter in **spitzen Klammern** oder deutsche Platzhalter wie `datei`, `ordner`, `dienst`, `name` durch deine eigenen Werte ersetzen.
- `sudo` davor = als Administrator ausführen (fragt nach **deinem** Passwort, nicht nach dem von root).
- Rot mit ⚠ markierte Befehle sind **gefährlich** – erst denken, dann Enter.
- Jeder Befehl hat eine eigene Seite mit Details – einfach oben in die Suche tippen (z.B. `chmod`, `ufw`, `rsync`).
""",

    "befehle": [
        {"titel": "🧭 Orientierung", "zeilen": [
            ("pwd", "Wo bin ich? (aktueller Ordner)"),
            ("ls -la", "Alles im Ordner anzeigen – auch versteckte Dateien, mit Rechten und Grösse"),
            ("cd /etc", "In einen Ordner wechseln (absoluter Pfad)"),
            ("cd ..", "Eine Ebene nach oben"),
            ("cd ~", "Ins eigene Home-Verzeichnis (/home/name)"),
            ("cd -", "Zurück in den vorherigen Ordner"),
        ]},
        {"titel": "📁 Dateien & Ordner", "zeilen": [
            ("mkdir -p projekte/test", "Ordner anlegen (-p: auch alle Zwischenordner)"),
            ("touch datei.txt", "Leere Datei anlegen (oder Zeitstempel aktualisieren)"),
            ("cp -r quelle/ ziel/", "Kopieren (-r: ganze Ordner)"),
            ("mv alt.txt neu.txt", "Verschieben oder umbenennen"),
            ("rm datei.txt", "Datei löschen – es gibt KEINEN Papierkorb!"),
            ("rm -r ordner/", "Ordner mit Inhalt löschen – vorher mit ls prüfen"),
            ("ln -s /pfad/ziel verknuepfung", "Symbolischen Link (Verknüpfung) anlegen"),
            ("cat datei.txt", "Kurze Datei komplett ausgeben"),
        ]},
        {"titel": "🔎 Anzeigen, Bearbeiten & Suchen", "zeilen": [
            ("less datei.log", "Lange Datei seitenweise lesen (q = beenden, / = suchen)"),
            ("tail -f /var/log/syslog", "Log live mitlesen (Ctrl+C beendet)"),
            ("head -n 20 datei.txt", "Die ersten 20 Zeilen"),
            ("nano datei.txt", "Datei im Editor öffnen (Ctrl+O speichern, Ctrl+X beenden)"),
            ("grep -rni \"text\" /etc", "Text in allen Dateien eines Ordners suchen"),
            ("find / -name \"*.conf\" 2>/dev/null", "Dateien nach Namen suchen (Fehlermeldungen ausblenden)"),
            ("wc -l datei.txt", "Zeilen zählen"),
        ]},
        {"titel": "👤 Benutzer & Rechte", "zeilen": [
            ("sudo befehl", "Befehl als Administrator ausführen"),
            ("sudo -i", "Root-Shell öffnen (mit exit wieder verlassen!)"),
            ("whoami", "Als wer bin ich angemeldet?"),
            ("sudo adduser name", "Neuen Benutzer anlegen (fragt Passwort und Infos ab)"),
            ("sudo usermod -aG sudo name", "Benutzer zur Gruppe sudo hinzufügen (-a nie vergessen!)"),
            ("passwd", "Eigenes Passwort ändern"),
            ("chmod 644 datei.txt", "Rechte setzen: Besitzer lesen+schreiben, alle anderen nur lesen"),
            ("sudo chown name:gruppe datei.txt", "Besitzer und Gruppe ändern"),
        ]},
        {"titel": "📦 Pakete & Dienste", "zeilen": [
            ("sudo apt update", "Paketlisten aktualisieren (installiert noch nichts)"),
            ("sudo apt upgrade", "Alle Updates installieren"),
            ("sudo apt install paket", "Programm installieren"),
            ("sudo apt remove paket", "Programm entfernen (Konfiguration bleibt)"),
            ("sudo apt autoremove", "Nicht mehr benötigte Pakete aufräumen"),
            ("systemctl status dienst", "Läuft der Dienst? Mit letzten Log-Zeilen"),
            ("sudo systemctl restart dienst", "Dienst neu starten (z.B. nach Konfig-Änderung)"),
            ("sudo systemctl enable --now dienst", "Dienst jetzt starten UND beim Booten automatisch"),
            ("systemctl --failed", "Welche Dienste sind abgestürzt?"),
        ]},
        {"titel": "⚙️ System & Prozesse", "zeilen": [
            ("df -h", "Freier Speicher pro Laufwerk (-h = lesbar in G/M)"),
            ("du -sh *", "Grösse jedes Ordners/jeder Datei hier"),
            ("free -h", "Arbeitsspeicher und Swap"),
            ("htop", "Prozesse und Auslastung live (F10 / q = beenden)"),
            ("ps aux | grep name", "Bestimmten Prozess finden"),
            ("kill PID", "Prozess höflich beenden (PID aus ps/htop)"),
            ("uptime", "Laufzeit und Last (load average)"),
            ("sudo journalctl -u dienst -f", "Log eines Dienstes live mitlesen"),
            ("sudo reboot", "Neu starten – per SSH: Verbindung bricht ab"),
        ]},
        {"titel": "🌐 Netzwerk", "zeilen": [
            ("ip a", "IP-Adressen aller Netzwerkkarten"),
            ("ip r", "Routen – wo ist das Gateway?"),
            ("ping -c 4 8.8.8.8", "Erreichbarkeit testen (4 Pakete)"),
            ("sudo ss -tulpn", "Welche Programme lauschen auf welchen Ports?"),
            ("curl -I https://example.com", "Webserver testen (nur HTTP-Kopfzeilen)"),
            ("dig example.com", "DNS-Auflösung prüfen"),
            ("ssh name@server", "Auf einen anderen Server verbinden"),
            ("rsync -avz quelle/ name@server:/ziel/", "Ordner effizient kopieren/synchronisieren"),
        ]},
        {"titel": "🔒 Sicherheit", "zeilen": [
            ("sudo ufw status verbose", "Firewall-Status und alle Regeln"),
            ("sudo ufw allow OpenSSH", "SSH erlauben – IMMER vor ufw enable!"),
            ("sudo ufw enable", "Firewall einschalten"),
            ("sudo fail2ban-client status sshd", "Gesperrte Angreifer-IPs anzeigen"),
            ("sudo sshd -t", "SSH-Konfiguration auf Fehler prüfen, BEVOR man neu startet"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Die Konsole lesen: der Prompt",
            "kopf": ["Teil", "Beispiel", "Bedeutung"],
            "zeilen": [
                ["Benutzer", "benutzer", "als wer du angemeldet bist (hier steht dein Name)"],
                ["@Host", "@srv01", "auf welchem Server du bist – wichtig bei mehreren SSH-Fenstern!"],
                [":Pfad", ":~/projekte", "aktueller Ordner (~ = Home)"],
                ["$ oder #", "$  /  #", "$ = normaler Benutzer · # = root (Vorsicht, alles erlaubt!)"],
            ],
            "hinweis": "Beispiel: `benutzer@srv01:~/projekte$` – angemeldet als benutzer (steht für deinen Benutzernamen), auf dem Server srv01, im Ordner /home/benutzer/projekte.",
        },
        {
            "titel": "📊 Tastenkürzel, die man sofort braucht",
            "kopf": ["Taste", "Wirkung"],
            "zeilen": [
                ["Tab", "Befehl / Pfad automatisch vervollständigen (2× Tab = alle Möglichkeiten)"],
                ["↑ / ↓", "Frühere Befehle durchblättern"],
                ["Ctrl + C", "Laufenden Befehl abbrechen"],
                ["Ctrl + R", "In früheren Befehlen suchen"],
                ["Ctrl + L", "Bildschirm leeren (wie clear)"],
                ["Ctrl + D", "Abmelden / SSH-Sitzung beenden (wie exit)"],
            ],
        },
    ],

    "sicherheit": [
        "Nie `ufw enable` per SSH, ohne vorher `sudo ufw allow OpenSSH` – sonst sperrst du dich selbst aus.",
        "Nie `rm -rf` mit Variablen oder `*` ausführen, ohne vorher mit `ls` genau dasselbe anzuzeigen.",
        "Nie `chmod 777` – egal wie dringend. Richtige Rechte setzen (siehe Seite Dateirechte).",
        "Nie Befehle aus dem Internet mit `sudo` ausführen, die du nicht verstehst – besonders `curl … | sudo bash`.",
        "Nie Datenbank- oder Admin-Ports (3306, 5432, 6379, 27017, 8006 …) direkt ins Internet öffnen.",
        "Alle Regeln im Detail: Kategorie 🔒 Sicherheit → „Die Todsünden“.",
    ],
    "tipps": [
        "**Tab drücken, Tab drücken, Tab drücken** – spart Tipparbeit und verhindert Tippfehler in Pfaden.",
        "Vor jedem Löschen/Überschreiben mit demselben Muster erst `ls` ausführen – zeigt, was betroffen wäre.",
        "Befehl vergessen? `history | grep suchwort` oder Ctrl+R.",
        "Bei langen Arbeiten per SSH `tmux` benutzen – bricht die Verbindung ab, läuft alles weiter.",
    ],
    "siehe_auch": ["todsuenden", "terminal_shell", "tastenkuerzel", "ersteinrichtung", "fehlersuche"],
}
