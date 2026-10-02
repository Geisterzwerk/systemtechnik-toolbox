# =============================================================================
# _vorlage.py   <-  KOPIERVORLAGE für eine neue Seite der DIGITALTECHNIK
# -----------------------------------------------------------------------------
# Wird NICHT angezeigt (Dateien mit "_" am Anfang werden ignoriert).
#
# 1. Datei in den passenden Kategorie-Ordner kopieren, z.B. 01_zahlen_codes/gray_code.py
#    (Dateiname = ID, eindeutig über ALLE Bereiche, nur klein + _)
# 2. ALLE Pflichtabschnitte ausfüllen - pruefen_rechner.py meldet fehlende:
#       ## Grundlagen  ## Vorgehen  ## Beispiel  ## Praxis
#       "fehler" (typische Fehler), "rechner" (mind. einer)
# 3. Toolbox neu starten -> erscheint automatisch (auch in der Suche)
#
# FORMATIERUNG in Texten:  ## Überschrift   - Punkt   **fett**   `formel`
# NEUE KATEGORIE: Ordner z.B. 03_logik/ mit _kategorie.py (NAME, ICON, BESCHREIBUNG)
# INTERAKTIVES WERKZEUG: Klasse in digitaltechnik/grafiken.py (Basis: Karte),
#                        in digitaltechnik/rechner.py registrieren, in rechner_info.py beschreiben
# =============================================================================

THEMA = {
    "titel": "Name des Themas",
    "reihenfolge": 10,                                   # Position in der Kategorie
    "kurz": "Ein Satz: Worum geht es?",
    "stichworte": ["suchwort", "englisch", "abkürzung"],

    "grafiken": ["werkzeug_..."],                        # interaktives Werkzeug (Wissen-Ansicht), optional

    "erklaerung": """
## Grundlagen
Begriffe und Regeln.

## Vorgehen
Schritt für Schritt: Wie rechnet / entwirft man?

## Beispiel
Ein vollständig durchgerechnetes Beispiel.

## Praxis
Wo begegnet man dem (µC, Bus, Datenblatt), worauf achten?
""",

    "tipps": ["Kniff aus der Praxis"],
    "fehler": ["Typischer Fehler"],
    "siehe_auch": ["anderes_thema"],                     # IDs anderer Seiten dieses Bereichs
    "rechner": ["zahlensystem"],                         # IDs aus der Rechner-Registry
}
