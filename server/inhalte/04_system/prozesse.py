# =============================================================================
# Thema: Prozesse (ps, htop, kill)  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Prozesse: ps, htop, kill",
    "reihenfolge": 3,
    "kurz": "Was läuft gerade, was frisst CPU und RAM – und wie beendet man hängende Programme?",
    "stichworte": ["prozess", "process", "ps", "top", "htop", "kill", "pkill", "killall", "pgrep", "pid",
                   "signal", "sigterm", "sigkill", "kill -9", "cpu", "last", "load average", "auslastung",
                   "nice", "nohup", "zombie", "hängt"],

    "erklaerung": """
## Prozess und PID
Jedes laufende Programm ist ein **Prozess** mit einer eindeutigen Nummer, der **PID**. Mit der PID kann man den Prozess gezielt ansprechen.
## htop – der Task-Manager der Konsole
`htop` zeigt live CPU, RAM und alle Prozesse. Muss evtl. erst installiert werden (`sudo apt install htop`). Mit den Pfeiltasten auswählen, **F9** beendet einen Prozess, **F6** sortiert, **F10** oder **q** beendet htop.
## Load Average verstehen
`uptime` und htop zeigen drei Zahlen, z.B. `load average: 0.52, 0.80, 1.10` – durchschnittliche Last der letzten **1, 5 und 15 Minuten**. Faustregel: Last ≈ Anzahl CPU-Kerne (`nproc`) = voll ausgelastet. Deutlich darüber = überlastet.
## Prozesse beenden – höflich zuerst
- `kill PID` schickt **SIGTERM (15)**: „Bitte beende dich“. Das Programm kann aufräumen (Dateien speichern, Verbindungen schliessen).
- `kill -9 PID` schickt **SIGKILL**: sofortiger Abbruch durch den Kernel, kein Aufräumen → Datenverlust möglich. **Nur als letztes Mittel.**
- Dienste nie mit kill beenden, sondern mit `systemctl stop` – sonst startet systemd sie evtl. sofort neu.
""",

    "befehle": [
        {"titel": "Anzeigen", "zeilen": [
            ("htop", "Live-Übersicht (q = beenden)"),
            ("top", "Wie htop, immer installiert (q = beenden, M = nach RAM sortieren)"),
            ("ps aux", "Alle Prozesse aller Benutzer"),
            ("ps aux --sort=-%mem | head", "Die 10 grössten RAM-Fresser"),
            ("ps aux --sort=-%cpu | head", "Die 10 grössten CPU-Fresser"),
            ("pgrep -a nginx", "PIDs und Befehlszeile aller nginx-Prozesse"),
            ("pstree -p", "Prozesse als Baum (wer hat wen gestartet?)"),
            ("uptime", "Laufzeit und Load Average"),
            ("nproc", "Anzahl CPU-Kerne"),
        ]},
        {"titel": "Beenden", "zeilen": [
            ("kill 1234", "Prozess 1234 höflich beenden (SIGTERM)"),
            ("pkill -f meinskript.py", "Nach Name / Befehlszeile beenden"),
            ("kill -9 1234", "Erzwingen – nur wenn kill nicht wirkt"),
        ]},
        {"titel": "Im Hintergrund laufen lassen", "zeilen": [
            ("nohup ./langes_skript.sh > ausgabe.log 2>&1 &", "Läuft weiter, auch wenn SSH getrennt wird"),
            ("nice -n 10 tar -czf backup.tar.gz /daten", "Mit niedriger Priorität (bremst den Rest nicht)"),
            ("lsof -p 1234", "Welche Dateien/Verbindungen hat der Prozess offen?"),
        ]},
    ],

    "beispiele": [
        {"titel": "Der Server ist langsam – wer ist schuld?",
         "code": {"Bash": r'''uptime                                  # Last im Vergleich zu nproc
free -h                                 # RAM voll? Swap in Benutzung?
ps aux --sort=-%cpu | head -5           # wer rechnet?
ps aux --sort=-%mem | head -5           # wer frisst Speicher?'''},
         "ausgabe": " 11:20:03 up 12 days,  3:10,  1 user,  load average: 3.92, 3.80, 2.10\n(4 Kerne → voll ausgelastet)"},
    ],

    "tabellen": [
        {
            "titel": "📊 Spalten in ps aux / htop",
            "kopf": ["Spalte", "Bedeutung"],
            "zeilen": [
                ["USER", "wem der Prozess gehört"],
                ["PID", "Prozessnummer"],
                ["%CPU / %MEM", "Anteil CPU / Arbeitsspeicher"],
                ["VSZ / RSS", "virtueller / tatsächlich belegter Speicher (RSS ist der wichtige)"],
                ["STAT", "R = läuft, S = schläft, D = wartet auf Festplatte, Z = Zombie"],
                ["COMMAND", "Befehlszeile"],
            ],
        },
    ],

    "sicherheit": [
        "Nie `kill -9 -1` oder `kill -9 1` als root – beendet alle Prozesse bzw. systemd → Server stürzt ab.",
        "Nicht „auf Verdacht“ unbekannte Root-Prozesse killen – erst mit `ps`, `pstree` und `systemctl status PID` herausfinden, was es ist.",
        "Unbekannter Prozess mit hoher CPU-Last unter `www-data` oder einem Dienstkonto (z.B. „xmrig“, zufälliger Name in /tmp) = Verdacht auf **Krypto-Miner nach Einbruch** → Server vom Netz, untersuchen, neu aufsetzen.",
    ],
    "tipps": [
        "Erst `kill`, 5–10 Sekunden warten, erst dann `kill -9`.",
        "Status **D** bei vielen Prozessen + hohe Last, aber wenig CPU → die Festplatte (oder ein Netzlaufwerk) ist der Engpass.",
        "Für lange Aufgaben ist `tmux` angenehmer als `nohup` – man kann später wieder zuschauen.",
    ],
    "fehler": [
        "Dienst mit `kill` beendet → systemd startet ihn sofort neu (Restart=…). Richtig: `sudo systemctl stop dienst`.",
        "`kill` ohne sudo auf einen Prozess eines anderen Benutzers → `Operation not permitted`.",
        "Zombie-Prozesse (Z) mit kill beenden wollen – geht nicht, sie sind schon tot. Der Eltern-Prozess muss aufräumen.",
    ],
    "siehe_auch": ["dienste_systemctl", "systeminfo", "fehlersuche", "ssh_verbinden"],
}
