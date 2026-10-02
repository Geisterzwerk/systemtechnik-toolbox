# =============================================================================
# gui/server_gui.py
# -----------------------------------------------------------------------------
# Die SERVER-SEITE (Linux-/Ubuntu-Server-Wiki): Konsole, Befehle, sudo,
# Dienste, Netzwerk, Sicherheit - alles, was man mit nur einer Konsole braucht.
#
#   ┌──────────────────────────────────────────────────────────────────────┐
#   │ ⬅  🏠  ◀   🔍 [ Suche ........ z.B. chmod, ssh, firewall ....... ]   │
#   ├───────────────────┬──────────────────────────────────────────────────┤
#   │ Navigation        │  Inhalt: Erklärung · ⌨️ Befehle (📋 pro Zeile)   │
#   │                   │  · Beispiele · 🔒 Sicherheit · Tipps · Fehler     │
#   └───────────────────┴──────────────────────────────────────────────────┘
#
# Es gibt hier KEINE eigene Wiki-Maschine: Die Seite benutzt genau dieselbe
# Klasse wie der Programmieren-Tab (gui/programmieren_gui.py ProgrammierSeite),
# nur mit anderem Inhalts-Ordner und nur einer "Sprache" (Bash).
#
# INHALTE:  server/inhalte/<NN_kategorie>/<thema>.py  (Vorlage: server/inhalte/_vorlage.py)
#
# WER RUFT DAS AUF?  main.py -> server_gui.create(tab, app)
# =============================================================================

import config                                           # -> config.py
from gui.programmieren_gui import ProgrammierSeite      # -> gui/programmieren_gui.py


def create(parent, app):
    """Wird von main.py aufgerufen (parent = Tab "Server / Linux")."""
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(0, weight=1)
    seite = ProgrammierSeite(parent, app,
                             inhalte_pfad=config.INHALTE_SERVER,
                             sprachen=[config.SERVER_SPRACHE],
                             titel="🐧 Server / Linux",
                             such_platzhalter="🔍  Suchen ... z.B. chmod, ssh, firewall, dienst neu starten  (Ctrl+F)")
    seite.grid(row=0, column=0, sticky="nsew")
    return seite
