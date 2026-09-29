# =============================================================================
# _vorlage.py   <-  KOPIERVORLAGE für ein neues Bauteil
# -----------------------------------------------------------------------------
# Wird NICHT angezeigt (Dateien mit "_" am Anfang werden ignoriert).
#
# 1. Datei in den passenden Kategorie-Ordner kopieren, z.B. 03_transistoren/mosfet.py
#    (Dateiname = ID, eindeutig, nur klein + _)
# 2. Felder ausfüllen, Unbenötigtes löschen
# 3. Toolbox neu starten -> erscheint automatisch (auch in der Suche)
#
# FORMATIERUNG in Texten:  ## Überschrift   - Punkt   **fett**   `formel`
# NEUE KATEGORIE: Ordner z.B. 05_ics/ mit _kategorie.py (NAME, ICON, BESCHREIBUNG)
# =============================================================================

THEMA = {
    "titel": "Name des Bauteils",
    "reihenfolge": 10,                                   # Position in der Kategorie
    "kurz": "Ein Satz, was das Bauteil macht.",
    "stichworte": ["suchwort", "englisch", "abkürzung"],

    "steckbrief": {
        "symbol": "widerstand",                          # Schlüssel aus bauteile/grafiken/symbole.py
        "zeilen": [("Formelzeichen", "R"), ("Einheit", "Ω")],
    },

    "erklaerung": """
## Was macht es?
Text ...
""",

    "bilder": [{"titel": "🖼 Titel", "datei": "bild.png", "text": "Bildunterschrift", "max_breite": 600}],

    "tabellen": [{"titel": "📊 Tabelle", "kopf": ["A", "B"], "zeilen": [["1", "2"]], "hinweis": "optional"}],

    "tipps": ["Kniff, den man gern vergisst"],           # -> "💡 Kniffe & Praxis"
    "fehler": ["Häufiger Fehler"],                        # -> "⚠️ Häufige Fehler"
    "siehe_auch": ["widerstand"],                         # IDs anderer Bauteile

    "rechner": ["ohm_leistung"],                          # IDs aus bauteile/rechner/*_rechner.py
}
