# =============================================================================
# _vorlage.py   <-  KOPIERVORLAGE für ein neues Thema
# -----------------------------------------------------------------------------
# Diese Datei wird NICHT angezeigt (Dateien mit "_" am Anfang werden ignoriert).
#
# SO LEGST DU EIN NEUES THEMA AN:
#   1. Diese Datei kopieren in den passenden Kategorie-Ordner,
#      z.B.  programmieren/inhalte/02_kontrollstrukturen/
#   2. Umbenennen, z.B.  ternaerer_operator.py
#      (Der Dateiname ist die ID des Themas -> muss EINDEUTIG sein,
#       nur Kleinbuchstaben, Zahlen und _ benutzen)
#   3. Felder ausfüllen, nicht benötigte Felder einfach löschen.
#   4. Toolbox neu starten -> das Thema erscheint automatisch (auch in der Suche).
#
# NEUE KATEGORIE?
#   Neuen Ordner anlegen, z.B.  07_netzwerk/
#   Darin eine Datei  _kategorie.py  mit NAME, ICON, BESCHREIBUNG (siehe andere Ordner).
#
# FORMATIERUNG in "erklaerung", "text", "tipps", "fehler", "unterschiede":
#   ## Überschrift
#   - Aufzählungspunkt
#   **fett**
#   `code im Text`
#
# CODE: Immer als r'''...''' schreiben (r = "raw"), damit z.B. "\n" im
#       Beispielcode nicht als Zeilenumbruch interpretiert wird.
# =============================================================================

THEMA = {
    # ---- Pflicht ----
    "titel": "Titel der Seite",

    # ---- Optional ----
    "reihenfolge": 10,                     # Position in der Kategorie (klein = weiter oben)
    "kurz": "Ein Satz, worum es geht.",    # Untertitel
    "stichworte": ["suchwort1", "suchwort2", "englischer begriff"],   # für die Suche!

    "erklaerung": """
## Was ist das?
Hier kommt die Erklärung. **Wichtiges fett**, Code im Text so: `x = 5`
- Punkt 1
- Punkt 2
""",

    # Bild aus images/programmieren/ (optional)
    "bild": "dateiname.png",
    "bild_text": "Bildunterschrift",

    # Tabelle (optional). Für mehrere Tabellen: "tabellen": [ {...}, {...} ]
    "tabelle": {
        "titel": "📊 Tabelle",
        "kopf": ["Spalte 1", "Spalte 2", "Spalte 3"],
        "zeilen": [
            ["a", "b", "c"],
            ["d", "e", "f"],
        ],
        "hinweis": "Optionaler Text unter der Tabelle",
    },

    # Code-Beispiele: pro Beispiel Code für jede Sprache (fehlende Sprache -> "hinweis")
    "beispiele": [
        {
            "titel": "Beispiel 1",
            "text": "Optionaler Text über dem Code.",
            "code": {
                "Python": r'''print("Hallo")''',
                "C++": r'''std::cout << "Hallo" << std::endl;''',
                "C#": r'''Console.WriteLine("Hallo");''',
            },
            "ausgabe": "Hallo",                                    # optional
            "hinweis": {"Python": "Nur nötig, wenn Code fehlt."},  # optional
        },
    ],

    "unterschiede": """
- **Python:** ...
- **C++:** ...
- **C#:** ...
""",

    "tipps": ["Tipp 1", "Tipp 2"],
    "fehler": ["Häufiger Fehler 1"],

    # IDs (= Dateinamen ohne .py) von verwandten Themen
    "siehe_auch": ["variablen", "datentypen"],
}
