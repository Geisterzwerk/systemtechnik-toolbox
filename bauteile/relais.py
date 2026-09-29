# =============================================================================
# bauteile/relais.py  -  Seite RELAIS (noch im Aufbau)
# WER RUFT DAS AUF?  gui/bauteile_gui.py -> bereich.eintrag_hinzufuegen("Relais", relais.create, ...)
# Vorlage für eine fertige Seite: bauteile/widerstand.py
# =============================================================================

from core.widgets import platzhalter_seite      # -> core/widgets.py


def create(parent):
    platzhalter_seite(parent, "Relais", "Hier kommen Aufbau, Freilaufdiode und Ansteuerung mit Transistor hin. Diese Seite ist noch im Aufbau. 🚧")
