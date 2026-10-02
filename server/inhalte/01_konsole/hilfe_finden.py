# =============================================================================
# Thema: Hilfe finden  (Kategorie: Konsole & SSH)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Hilfe finden (man, --help, tldr)",
    "reihenfolge": 3,
    "kurz": "Ohne Internet und ohne Google: Die Konsole erklärt sich selbst.",
    "stichworte": ["hilfe", "help", "man", "manpage", "handbuch", "tldr", "apropos", "whatis", "info",
                   "dokumentation", "was macht", "optionen"],

    "erklaerung": """
## Drei Wege zur Hilfe
- **`befehl --help`** – kurze Übersicht aller Optionen, direkt in der Konsole. Der schnellste Weg.
- **`man befehl`** – das ausführliche Handbuch (Manual Page). Blättern mit Leertaste, suchen mit `/wort`, beenden mit **q**.
- **`tldr befehl`** – „too long; didn't read“: nur die häufigsten Beispiele. Muss einmal installiert werden.
## Den richtigen Befehl finden
Du weisst, **was** du willst, aber nicht **wie** der Befehl heisst? `apropos stichwort` durchsucht alle Handbuch-Titel (z.B. `apropos firewall`).
## So liest man eine Man-Page
- **SYNOPSIS:** Aufbau des Befehls. `[ ]` = optional, `...` = mehrere möglich
- **DESCRIPTION:** was der Befehl macht, alle Optionen
- **EXAMPLES:** (ganz unten, nicht immer vorhanden) – oft der hilfreichste Teil: `G` springt ans Ende
- Die Zahl in Klammern ist der Abschnitt: `passwd(1)` = Befehl, `passwd(5)` = Aufbau der Datei /etc/passwd → `man 5 passwd`
""",

    "befehle": [
        {"titel": "Hilfe", "zeilen": [
            ("ls --help", "Kurzhilfe mit allen Optionen"),
            ("man ls", "Ausführliches Handbuch (q = beenden)"),
            ("man 5 passwd", "Handbuch-Abschnitt 5 (Dateiformate) statt Befehl"),
            ("sudo apt install tldr && tldr --update", "tldr installieren (Beispiel-Sammlung)"),
            ("tldr tar", "Die häufigsten Beispiele für tar"),
            ("apropos firewall", "Befehle zu einem Stichwort finden"),
            ("whatis ss", "Einzeilige Beschreibung eines Befehls"),
        ]},
    ],

    "tabellen": [
        {
            "titel": "📊 Tasten in man und less",
            "kopf": ["Taste", "Wirkung"],
            "zeilen": [
                ["Leertaste / b", "eine Seite vor / zurück"],
                ["↑ ↓", "zeilenweise"],
                ["/wort", "vorwärts suchen – n = nächster Treffer, N = vorheriger"],
                ["g / G", "an den Anfang / ans Ende"],
                ["q", "beenden"],
            ],
        },
    ],

    "beispiele": [
        {"titel": "Nur die interessanten Zeilen der Hilfe",
         "text": "Die Hilfe ist lang? Mit `grep` nur nach der gesuchten Option filtern.",
         "code": {"Bash": r'''ls --help | grep -i "sort"
man rsync | grep -A2 -- "--delete"'''}},
    ],

    "tipps": [
        "`tldr` ist ideal zum Lernen: statt 30 Seiten Handbuch die 8 Befehle, die man wirklich braucht.",
        "Die Man-Pages sind auf dem Server installiert – funktioniert auch ohne Internet.",
        "Unbekannte Befehle aus Anleitungen **erst mit `man` nachschlagen**, dann ausführen.",
    ],
    "fehler": [
        "In `man` festgesteckt – einfach **q** drücken.",
        "`No manual entry for …` → Programm nicht installiert oder bringt keine Man-Page mit; dann `befehl --help` versuchen.",
    ],
    "siehe_auch": ["terminal_shell", "tastenkuerzel", "dateien_anzeigen", "spickzettel"],
}
