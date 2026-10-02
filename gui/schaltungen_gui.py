# =============================================================================
# gui/schaltungen_gui.py
# -----------------------------------------------------------------------------
# Der Bereich SCHALTUNGEN - ein Wiki wie Bauteile, Messtechnik und Schaltungen.
#
# Der ganze Aufbau (Suche, Kategorie-Baum, Seite) steckt im gemeinsamen Baustein
#   bauteile/engine/wiki_bereich.py  -> WikiBereich
# Hier steht nur, WELCHER Ordner angezeigt wird und wie der Bereich heisst.
#
# WER RUFT DAS AUF?  main.py -> schaltungen_gui.create(tab, app)
#
# NEUE SEITE: Datei in schaltungen/inhalte/<kategorie>/ anlegen (Vorlage: schaltungen/inhalte/_vorlage.py)
#             -> erscheint automatisch. Hier muss nichts geändert werden.
# =============================================================================

import os

import config                                                          # -> config.py
from bauteile.engine.wiki_bereich import WikiBereich                   # -> bauteile/engine/wiki_bereich.py

INHALTE_PFAD = os.path.join(config.BASIS_PFAD, 'schaltungen', 'inhalte')


def create(parent, app):
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    wiki = WikiBereich(parent, app, INHALTE_PFAD, titel="🔌 Schaltungen",
                       beschreibung="Funktion, Dimensionierung, Messpunkte und typische Fehler – mit interaktivem Schaltplan",
                       suchtext="z.B. Spannungsteiler, Pull-up, Brücke, Stromteiler")
    wiki.grid(row=0, column=0, sticky="nsew")
    return wiki
