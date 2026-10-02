# =============================================================================
# Thema: Erste Schritte für Einsteiger  (Kategorie: Schnellstart)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# Für alle, die noch nie mit einem Linux-Server gearbeitet haben: Begriffe, Platzhalter, erste Befehle.
# =============================================================================

THEMA = {
    "titel": "Erste Schritte: noch nie mit Linux gearbeitet?",
    "reihenfolge": 0,
    "kurz": "Was ist ein Server, was ist das Terminal, wie verbinde ich mich – und wie lese ich die Beispiele in dieser Toolbox?",
    "stichworte": ["einsteiger", "anfänger", "erste schritte", "einführung", "grundlagen", "was ist linux",
                   "was ist ein server", "terminal", "konsole", "platzhalter", "glossar", "begriffe", "start"],

    "erklaerung": """
## Was ist ein Server?
Ein **Server** ist ein Computer, der Dienste für andere bereitstellt: eine Webseite, Dateien, eine Datenbank, eine Hausautomation. Meist hat er **keinen Bildschirm** – man bedient ihn über das Netzwerk von seinem eigenen PC aus.
Auf den meisten Servern läuft **Linux** (z.B. Ubuntu oder Debian). Statt mit der Maus arbeitet man mit **Befehlen**, die man im **Terminal** eintippt.

## Was ist das Terminal?
Das Terminal (auch Konsole oder Shell) ist ein Fenster, in das man Befehle schreibt und mit **Enter** ausführt. Der Server antwortet mit Text.
- **Windows:** Programm „Terminal“ oder „PowerShell“ öffnen
- **macOS:** Programm „Terminal“
- **Linux:** meist Ctrl + Alt + T

Mit `ssh` verbindest du dieses Fenster mit dem Server. Ab dann landet alles, was du tippst, auf dem Server.

## So liest du die Beispiele
Alle Beispiele in dieser Toolbox verwenden **Platzhalter**. Ersetze sie durch deine eigenen Werte:
- `benutzer` – dein Benutzername auf dem Server
- `srv01` oder `server` – der Name deines Servers
- `192.168.1.50` – die IP-Adresse deines Servers (findest du mit `ip a` oder im Router)
- `datei.txt`, `ordner/`, `dienst`, `paket` – der Name der Datei, des Ordners, Dienstes oder Programms, um das es geht

Der Text vor dem Befehl (z.B. `benutzer@srv01:~$`) ist der **Prompt** – den tippst du nicht mit.

## Keine Angst vor Fehlern
- Ein Befehl läuft und hört nicht auf? **Ctrl + C** bricht ab.
- In einer Anzeige gefangen (man, less)? **q** beendet.
- Im Editor nano? **Ctrl + X** beendet.
- Vom Server abmelden: `exit`
- Lesende Befehle (`ls`, `pwd`, `cat`, `df -h`) können nichts kaputt machen – damit kannst du gefahrlos üben.
- Vorsicht nur bei `sudo`, `rm` und allem, was in der Toolbox **rot mit ⚠** markiert ist.

## Wie geht es weiter?
1. Diese Seite lesen, dann den **Spickzettel** öffnen.
2. Kategorie **Konsole & SSH**: Terminal, Verbinden, Hilfe finden.
3. Kategorie **Dateien & Navigation**: navigieren, anzeigen, bearbeiten.
4. Erst danach Benutzer, Rechte, Dienste und Sicherheit.
""",

    "befehle": [
        {"titel": "🟢 Gefahrlos ausprobieren (nur lesen)", "zeilen": [
            ("ssh benutzer@192.168.1.50", "Mit dem Server verbinden (Benutzer und IP-Adresse durch deine ersetzen)"),
            ("whoami", "Als wer bin ich angemeldet?"),
            ("hostname", "Auf welchem Computer bin ich?"),
            ("pwd", "In welchem Ordner bin ich?"),
            ("ls -l", "Was liegt in diesem Ordner?"),
            ("df -h", "Wie voll sind die Festplatten?"),
            ("free -h", "Wie viel Arbeitsspeicher ist frei?"),
            ("uptime", "Wie lange läuft der Server schon?"),
            ("ls --help", "Hilfe zu einem Befehl anzeigen"),
            ("exit", "Abmelden und Verbindung beenden"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Die wichtigsten Begriffe",
            "kopf": ["Begriff", "Bedeutung"],
            "zeilen": [
                ["Linux / Ubuntu / Debian", "Betriebssystem des Servers (Ubuntu und Debian sind Linux-Varianten)"],
                ["Terminal, Konsole, Shell", "Textfenster, in das man Befehle tippt (die Shell heisst meist bash)"],
                ["SSH", "verschlüsselte Verbindung vom eigenen PC zum Server"],
                ["Befehl, Option, Argument", "`ls -l /etc`: Befehl ls, Option -l (wie?), Argument /etc (womit?)"],
                ["Home-Verzeichnis (~)", "dein persönlicher Ordner, z.B. /home/benutzer"],
                ["root", "der Administrator mit allen Rechten"],
                ["sudo", "einen einzelnen Befehl mit Administratorrechten ausführen"],
                ["Paket", "ein Programm, das man mit apt installiert"],
                ["Dienst", "ein Programm, das im Hintergrund dauerhaft läuft (z.B. Webserver)"],
                ["Port", "„Tür“ eines Dienstes im Netzwerk, z.B. 22 für SSH, 443 für HTTPS"],
            ],
        },
    ],

    "sicherheit": [
        "Befehle aus dem Internet nie blind kopieren – erst verstehen (`man befehl`), dann ausführen.",
        "Nicht dauerhaft als root arbeiten. Nur einzelne Befehle mit `sudo` ausführen.",
    ],
    "tipps": [
        "Mit der **Tab-Taste** vervollständigt das Terminal Befehle und Dateinamen – spart Tippen und Tippfehler.",
        "Mit **↑** holst du den letzten Befehl zurück.",
        "Zum Üben eignet sich eine virtuelle Maschine (z.B. VirtualBox mit Ubuntu Server) – dort kann nichts Wichtiges kaputtgehen.",
    ],
    "fehler": [
        "Platzhalter wie `benutzer` oder `192.168.1.50` unverändert übernommen.",
        "Den Prompt (`benutzer@srv01:~$`) mit abgetippt.",
        "Gross- und Kleinschreibung missachtet – unter Linux sind `Datei.txt` und `datei.txt` zwei verschiedene Dateien.",
    ],
    "siehe_auch": ["spickzettel", "terminal_shell", "ssh_verbinden", "hilfe_finden", "verzeichnisstruktur"],
}
