# =============================================================================
# _vorlage.py   <-  KOPIERVORLAGE für eine neue SCHALTUNG
# -----------------------------------------------------------------------------
# Wird NICHT angezeigt (Dateien mit "_" am Anfang werden ignoriert).
#
# 1. Datei in den passenden Kategorie-Ordner kopieren, z.B. 02_dioden_schutz/verpolschutz.py
#    (Dateiname = ID, eindeutig über ALLE Bereiche, nur klein + _)
# 2. ALLE Pflichtabschnitte ausfüllen - pruefen_rechner.py meldet fehlende:
#       ## Funktion  ## Dimensionierung  ## Betriebszustände  ## Messpunkte  ## Grenzfälle
#       "fehler" (typische Fehler), "rechner" (mind. einer), "grafiken" (interaktiver Schaltplan)
# 3. Toolbox neu starten -> erscheint automatisch (auch in der Suche)
#
# Eine Schaltung ist KEINE Bildergalerie: Funktion, Dimensionierung, Zustände,
# Messpunkte, Grenzfälle, typische Fehler und passende Rechner gehören dazu.
#
# FORMATIERUNG in Texten:  ## Überschrift   - Punkt   **fett**   `formel`
# NEUE KATEGORIE: Ordner z.B. 02_dioden_schutz/ mit _kategorie.py (NAME, ICON, BESCHREIBUNG)
# INTERAKTIVER SCHALTPLAN: Klasse in schaltungen/grafiken.py (Basis: SchaltungsKarte),
#                          in schaltungen/rechner.py registrieren, in rechner_info.py beschreiben
# =============================================================================

THEMA = {
    "titel": "Name der Schaltung",
    "reihenfolge": 10,                                   # Position in der Kategorie
    "kurz": "Ein Satz: Wozu dient die Schaltung?",
    "stichworte": ["suchwort", "englisch", "abkürzung"],

    "grafiken": ["schaltung_..."],                       # interaktiver Schaltplan (Wissen-Ansicht)

    "erklaerung": """
## Funktion
Wie arbeitet die Schaltung? Welche Regel (Ohm, Kirchhoff ...) steckt dahinter?

## Dimensionierung
Schritt für Schritt mit Formeln und Einheiten.

## Betriebszustände
Was passiert in den typischen Zuständen (ein/aus, Leerlauf/Last ...)?

## Messpunkte
Wo misst man was, womit, und was muss herauskommen?

## Grenzfälle
Was passiert bei 0, unendlich, Kurzschluss, Unterbrechung?
""",

    "tipps": ["Kniff aus der Praxis"],
    "fehler": ["Typischer Fehler"],
    "siehe_auch": ["andere_schaltung"],                  # IDs anderer Schaltungen
    "rechner": ["spannungsteiler"],                      # IDs aus der Rechner-Registry
}
