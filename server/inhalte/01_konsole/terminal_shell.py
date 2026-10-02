# =============================================================================
# Thema: Terminal, Shell & Befehlsaufbau  (Kategorie: Konsole & SSH)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Terminal, Shell & Befehlsaufbau",
    "reihenfolge": 1,
    "kurz": "Was passiert eigentlich, wenn man etwas in die Konsole tippt – und wie ist ein Befehl aufgebaut?",
    "stichworte": ["terminal", "konsole", "shell", "bash", "prompt", "befehl", "option", "argument", "cli",
                   "kommandozeile", "exit code", "rückgabewert", "gross klein", "leerzeichen", "anführungszeichen"],

    "erklaerung": """
## Terminal, Konsole, Shell – was ist was?
- **Terminal / Konsole:** das Fenster, in dem man tippt (Windows Terminal, PuTTY, die Proxmox-Konsole, der Monitor am Server).
- **Shell:** das Programm, das deine Eingabe liest und ausführt. Auf Ubuntu ist das **Bash** (Bourne Again Shell).
- **Server ohne Oberfläche:** Ein Ubuntu Server hat keine Maus und keine Fenster – alles läuft über Befehle. Das ist Absicht: weniger Software = weniger Angriffsfläche, weniger Ressourcen.
## Der Prompt
`jorick@srv01:~$` zeigt: Benutzer **jorick**, Server **srv01**, Ordner **~** (Home), **$** = normaler Benutzer. Steht dort **#**, bist du **root** – dann ist alles erlaubt, auch jeder Fehler.
## Aufbau eines Befehls
`befehl  -optionen  argumente` – z.B. `ls -la /etc`
- **Befehl:** das Programm (`ls`)
- **Optionen:** ändern das Verhalten. Kurz mit einem Strich (`-l -a` = `-la`), lang mit zwei (`--all`).
- **Argumente:** worauf der Befehl wirkt (`/etc`)
## Regeln, die man kennen muss
- Linux unterscheidet **Gross/Klein**: `Datei.txt` und `datei.txt` sind zwei verschiedene Dateien.
- **Leerzeichen trennen** Argumente. Namen mit Leerzeichen in Anführungszeichen: `cd "Meine Dateien"` – oder besser gar keine Leerzeichen in Dateinamen verwenden.
- **Keine Nachricht = Erfolg.** Linux-Befehle sind still, wenn alles geklappt hat. Nur Fehler werden gemeldet.
- **Exit-Code:** Jeder Befehl gibt eine Zahl zurück – `0` = Erfolg, alles andere = Fehler. Anzeigen mit `echo $?`.
## Befehle verketten
- `befehl1 ; befehl2` – nacheinander, egal ob Erfolg
- `befehl1 && befehl2` – befehl2 **nur**, wenn befehl1 geklappt hat (typisch: `sudo apt update && sudo apt upgrade`)
- `befehl1 || befehl2` – befehl2 **nur**, wenn befehl1 fehlgeschlagen ist
""",

    "befehle": [
        {"titel": "Grundlagen", "zeilen": [
            ("echo $SHELL", "Welche Shell läuft? (meist /bin/bash)"),
            ("echo $?", "Exit-Code des letzten Befehls (0 = Erfolg)"),
            ("clear", "Bildschirm leeren (oder Ctrl+L)"),
            ("exit", "Shell / SSH-Sitzung beenden"),
            ("type ls", "Was ist ls? Programm, Alias oder eingebauter Befehl?"),
            ("alias ll='ls -la'", "Eigene Abkürzung anlegen (gilt bis zum Abmelden)"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Anführungszeichen",
            "kopf": ["Schreibweise", "Wirkung", "Beispiel"],
            "zeilen": [
                ["\"doppelt\"", "Variablen werden ersetzt, Leerzeichen bleiben zusammen", "echo \"Hallo $USER\" → Hallo jorick"],
                ["'einfach'", "alles wörtlich, nichts wird ersetzt", "echo 'Hallo $USER' → Hallo $USER"],
                ["\\ (Backslash)", "nächstes Zeichen wörtlich / Zeile fortsetzen", "cd Meine\\ Dateien"],
                ["$(befehl)", "Ausgabe eines Befehls einsetzen", "echo \"Heute: $(date +%F)\""],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Optionen kombinieren und Exit-Code prüfen",
         "code": {"Bash": r'''ls -l -a /etc      # Optionen einzeln
ls -la /etc        # dasselbe, zusammengefasst
ls --all -l /etc   # lange Schreibweise

ls /gibtsnicht
echo $?            # Fehler -> Zahl ungleich 0'''},
         "ausgabe": "ls: cannot access '/gibtsnicht': No such file or directory\n2"},
        {"titel": "Verketten mit && – nur weiter, wenn es geklappt hat",
         "code": {"Bash": r'''sudo apt update && sudo apt upgrade -y
mkdir -p ~/backup && cd ~/backup'''}},
    ],

    "sicherheit": [
        "Arbeite **nicht dauerhaft als root** (Prompt mit #). Jeder Tippfehler wirkt dann auf das ganze System.",
        "Nie Befehle blind aus Foren/KI kopieren und mit `sudo` ausführen – erst jeden Teil verstehen (`man befehl`).",
        "Vor Befehlen mit Wildcards (`*`) oder Variablen erst mit `echo` bzw. `ls` testen, was wirklich ersetzt wird.",
    ],
    "tipps": [
        "`man befehl` oder `befehl --help` zeigt alle Optionen – siehe Seite „Hilfe finden“.",
        "Keine Rückmeldung ist unter Linux eine **gute** Nachricht.",
        "Mehrere SSH-Fenster offen? Immer auf den **Hostnamen im Prompt** schauen, bevor du Enter drückst.",
        "Eigene Aliase dauerhaft speichern: Zeile in `~/.bashrc` eintragen, dann `source ~/.bashrc`.",
    ],
    "fehler": [
        "`command not found` → Tippfehler, falsche Gross-/Kleinschreibung oder Programm nicht installiert (`sudo apt install …`).",
        "`Permission denied` → fehlende Rechte; überlegen, ob `sudo` wirklich nötig ist, statt es reflexartig davorzusetzen.",
        "Dateinamen mit Leerzeichen ohne Anführungszeichen → Befehl bekommt zwei Argumente statt einem.",
        "Windows-Gewohnheit: `\\` statt `/` in Pfaden, oder `dir`/`cls` statt `ls`/`clear`.",
    ],
    "siehe_auch": ["hilfe_finden", "tastenkuerzel", "ssh_verbinden", "sudo_root", "spickzettel"],
}
