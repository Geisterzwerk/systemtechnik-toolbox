# =============================================================================
# bauteile/spule.py  -  Seite SPULE (noch im Aufbau)
# WER RUFT DAS AUF?  gui/bauteile_gui.py -> bereich.eintrag_hinzufuegen("Spule", spule.create, ...)
# Vorlage für eine fertige Seite: bauteile/widerstand.py
# =============================================================================

from core.widgets import platzhalter_seite      # -> core/widgets.py


def create(parent):
    platzhalter_seite(parent, "Spule", "Hier kommen Induktivität, τ = L / R, Magnetfeld und Induktion hin. Diese Seite ist noch im Aufbau. 🚧")
