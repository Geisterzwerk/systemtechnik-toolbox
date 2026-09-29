# =============================================================================
# gui/formel_gui.py
# -----------------------------------------------------------------------------
# Bereich FORMELN (noch im Aufbau).
# WER RUFT DAS AUF?  main.py -> formel_gui.create(tab, app)
#
# ERWEITERN (gleiches Prinzip wie gui/bauteile_gui.py):
#   1. Seite anlegen, z.B. formeln/rc_glied.py  mit  create(parent)
#   2. Hier importieren und  bereich.eintrag_hinzufuegen("RC-Glied", rc_glied.create)
# =============================================================================

from core.widgets import SeitenBereich, platzhalter_seite     # -> core/widgets.py


def _uebersicht(parent):
    platzhalter_seite(parent, "📐 Formeln", "Hier kommt die Formelsammlung mit Rechnern hin. Dieser Bereich ist noch im Aufbau. 🚧")


def create(parent, app):
    bereich = SeitenBereich(parent, app)
    bereich.eintrag_hinzufuegen("Übersicht", _uebersicht, text_kurz="📐")
    bereich.seite_zeigen("Übersicht")
    return bereich
