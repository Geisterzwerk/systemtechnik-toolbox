# =============================================================================
# gui/messtechnik_gui.py
# -----------------------------------------------------------------------------
# Der Bereich MESSTECHNIK - ein Wiki wie Bauteile, Messtechnik und Schaltungen.
#
# Der ganze Aufbau (Suche, Kategorie-Baum, Seite) steckt im gemeinsamen Baustein
#   bauteile/engine/wiki_bereich.py  -> WikiBereich
# Hier steht nur, WELCHER Ordner angezeigt wird und wie der Bereich heisst.
#
# WER RUFT DAS AUF?  main.py -> messtechnik_gui.create(tab, app)
#
# NEUE SEITE: Datei in messtechnik/inhalte/<kategorie>/ anlegen (Vorlage: messtechnik/inhalte/_vorlage.py)
#             -> erscheint automatisch. Hier muss nichts geändert werden.
# =============================================================================

import os

import config                                                          # -> config.py
from bauteile.engine.wiki_bereich import WikiBereich                   # -> bauteile/engine/wiki_bereich.py

INHALTE_PFAD = os.path.join(config.BASIS_PFAD, 'messtechnik', 'inhalte')


def create(parent, app):
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    wiki = WikiBereich(parent, app, INHALTE_PFAD, titel="📏 Messtechnik",
                       beschreibung="Messgeräte, Messfehler, Sensoren, AD-Wandler",
                       suchtext="z.B. Pt100, Oszilloskop, True RMS, Aliasing")
    wiki.grid(row=0, column=0, sticky="nsew")
    return wiki
