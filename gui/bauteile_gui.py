# =============================================================================
# gui/bauteile_gui.py
# -----------------------------------------------------------------------------
# Der Bereich BAUTEILE - ein Wiki wie Bauteile, Messtechnik und Schaltungen.
#
# Der ganze Aufbau (Suche, Kategorie-Baum, Seite) steckt im gemeinsamen Baustein
#   bauteile/engine/wiki_bereich.py  -> WikiBereich
# Hier steht nur, WELCHER Ordner angezeigt wird und wie der Bereich heisst.
#
# WER RUFT DAS AUF?  main.py -> bauteile_gui.create(tab, app)
#
# NEUE SEITE: Datei in bauteile/inhalte/<kategorie>/ anlegen (Vorlage: bauteile/inhalte/_vorlage.py)
#             -> erscheint automatisch. Hier muss nichts geändert werden.
# =============================================================================

import os

import config                                                          # -> config.py
from bauteile.engine.wiki_bereich import WikiBereich                   # -> bauteile/engine/wiki_bereich.py

INHALTE_PFAD = os.path.join(config.BASIS_PFAD, 'bauteile', 'inhalte')


def create(parent, app):
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    wiki = WikiBereich(parent, app, INHALTE_PFAD, titel="🔧 Bauteile",
                       beschreibung="Wissen, Kniffe und Rechner  ·  Suche oben oder links wählen",
                       suchtext="z.B. Farbcode, Spannungsteiler, SMD, LED")
    wiki.grid(row=0, column=0, sticky="nsew")
    return wiki
