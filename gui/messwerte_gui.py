# =============================================================================
# gui/messwerte_gui.py
# -----------------------------------------------------------------------------
# Bereich MESSWERTE (noch im Aufbau).
# WER RUFT DAS AUF?  main.py -> messwerte_gui.create(tab, app)
#
# ERWEITERN (gleiches Prinzip wie gui/bauteile_gui.py):
#   1. Seite anlegen, z.B. messwerte/rc_glied.py  mit  create(parent)
#   2. Hier importieren und  bereich.eintrag_hinzufuegen("RC-Glied", rc_glied.create)
# =============================================================================

from core.widgets import SeitenBereich, platzhalter_seite     # -> core/widgets.py


def _uebersicht(parent):
    platzhalter_seite(parent, "📊 Messwerte", "Hier können später Messwerte erfasst und ausgewertet werden. Dieser Bereich ist noch im Aufbau. 🚧")


def create(parent, app):
    bereich = SeitenBereich(parent, app)
    bereich.eintrag_hinzufuegen("Übersicht", _uebersicht, text_kurz="📊")
    bereich.seite_zeigen("Übersicht")
    return bereich
