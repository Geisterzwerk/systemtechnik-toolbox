# =============================================================================
# gui/schaltungen_gui.py
# -----------------------------------------------------------------------------
# Bereich SCHALTUNGEN (noch im Aufbau).
# WER RUFT DAS AUF?  main.py -> schaltungen_gui.create(tab, app)
#
# ERWEITERN (gleiches Prinzip wie gui/bauteile_gui.py):
#   1. Seite anlegen, z.B. schaltungen/rc_glied.py  mit  create(parent)
#   2. Hier importieren und  bereich.eintrag_hinzufuegen("RC-Glied", rc_glied.create)
# =============================================================================

from core.widgets import SeitenBereich, platzhalter_seite     # -> core/widgets.py


def _uebersicht(parent):
    platzhalter_seite(parent, "🔌 Schaltungen", "Hier kommen Grundschaltungen hin, z.B. Spannungsteiler, RC-Glied, OPV-Schaltungen. Dieser Bereich ist noch im Aufbau. 🚧")


def create(parent, app):
    bereich = SeitenBereich(parent, app)
    bereich.eintrag_hinzufuegen("Übersicht", _uebersicht, text_kurz="🔌")
    bereich.seite_zeigen("Übersicht")
    return bereich
