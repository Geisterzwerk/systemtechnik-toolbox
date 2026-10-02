# =============================================================================
# _vorlage.py   <-  KOPIERVORLAGE für eine neue Server-/Linux-Seite
# -----------------------------------------------------------------------------
# Diese Datei wird NICHT angezeigt (Dateien mit "_" am Anfang werden ignoriert).
#
# SO LEGST DU EINE NEUE SEITE AN:
#   1. Datei kopieren in den passenden Kategorie-Ordner, z.B. server/inhalte/04_system/
#   2. Umbenennen, z.B. docker.py   (Dateiname = ID, eindeutig, nur klein + _)
#   3. Felder ausfüllen, nicht benötigte löschen
#   4. Toolbox neu starten -> erscheint automatisch im Tab "Server / Linux" (auch in der Suche)
#
# NEUE KATEGORIE? Ordner z.B. 08_proxmox/ mit _kategorie.py (NAME, ICON, BESCHREIBUNG)
#
# DARGESTELLT VON: programmieren/engine/seite.py (gleiche Maschine wie Programmieren)
#
# FORMATIERUNG in Texten:  ## Überschrift   - Punkt   **fett**   `befehl`
# CODE: immer als r'''...''' schreiben. Sprache ist "Bash".
# GEFÄHRLICHE BEFEHLE (rm -rf, chmod 777, ufw disable ...) werden automatisch
# rot markiert -> Muster in programmieren/engine/syntax.py GEFAHR_MUSTER
# =============================================================================

THEMA = {
    "titel": "Titel der Seite",
    "reihenfolge": 10,                       # Position in der Kategorie
    "kurz": "Ein Satz, worum es geht.",
    "stichworte": ["suchwort", "englisch"],  # Befehle aus "befehle" sind automatisch Suchwörter

    "erklaerung": """
## Was ist das?
Text ...
""",

    # Befehlsliste: jede Zeile bekommt einen 📋-Knopf  (-> programmieren/engine/befehlsliste.py)
    "befehle": [
        {"titel": "Gruppe", "zeilen": [
            ("befehl --option", "Was der Befehl macht"),
        ]},
    ],

    "tabellen": [{"titel": "📊 Tabelle", "kopf": ["A", "B"], "zeilen": [["1", "2"]], "hinweis": "optional"}],

    # Code-Beispiele (ganzer Block wird mit 📋 Kopieren kopiert)
    "beispiele": [
        {"titel": "Beispiel", "text": "Optionaler Text.",
         "code": {"Bash": r'''sudo apt update'''},
         "ausgabe": "optional: was die Konsole anzeigt"},
    ],

    "sicherheit": ["Was man hier auf KEINEN Fall tun darf"],   # -> rote Box 🔒
    "tipps": ["Kniff"],
    "fehler": ["Häufiger Fehler"],
    "siehe_auch": ["spickzettel"],           # IDs anderer Server-Seiten
}
