# =============================================================================
# config.py
# -----------------------------------------------------------------------------
# Zentrale Einstellungen der ganzen Toolbox (Pfade, Farben, Schriften, Layout).
# Hier ändern -> wirkt überall.   Zugriff:  import config  ->  config.FARBEN["akzent"]
# =============================================================================

import os

# -----------------------------------------------------------------------------
# PFADE (funktionieren egal von wo das Programm gestartet wird)
# -----------------------------------------------------------------------------
BASIS_PFAD = os.path.dirname(os.path.abspath(__file__))
BILDER_PFAD = os.path.join(BASIS_PFAD, "images")
BILDER_PROGRAMMIEREN = os.path.join(BILDER_PFAD, "programmieren")
INHALTE_PROGRAMMIEREN = os.path.join(BASIS_PFAD, "programmieren", "inhalte")

# -----------------------------------------------------------------------------
# APP
# -----------------------------------------------------------------------------
APP_TITEL = "Systemtechnik HF Toolbox"
APP_UNTERTITEL = "Dein Begleiter für Studium und Praxis"
FENSTER_GROESSE = "1300x820"
FENSTER_MIN = (900, 600)          # kleiner wird das Fenster nicht

# -----------------------------------------------------------------------------
# LAYOUT  (-> core/layout.py)
# -----------------------------------------------------------------------------
INHALT_MAX_BREITE = 1200          # breiter wird Inhalt nicht (wird dann zentriert). None = immer volle Breite
SEITEN_RAND = 20                  # Abstand links/rechts im Inhaltsbereich
RESIZE_VERZOEGERUNG_MS = 60       # Neuberechnung nach Grössenänderung (gebündelt)
MAX_BILD_BREITE = 900             # Bilder im Wiki höchstens so breit

# -----------------------------------------------------------------------------
# FARBEN  (Tupel = (Light Mode, Dark Mode))
# -----------------------------------------------------------------------------
FARBEN = {
    "hintergrund":   ("#F2F4F7", "#1B1D22"),
    "flaeche":       ("#FFFFFF", "#23262D"),
    "sidebar":       ("#E7EAF0", "#16181C"),
    "rahmen":        ("#D0D5DD", "#343842"),
    "text":          ("#1D2939", "#E6E8EC"),
    "text_leise":    ("#667085", "#9AA1AD"),
    "akzent":        ("#1F6FEB", "#3B82F6"),
    "akzent_hover":  ("#1858BC", "#2563EB"),
    "tipp":          ("#E8F3FF", "#16283F"),
    "warnung":       ("#FFF4E5", "#3A2A12"),
    "tabelle_kopf":  ("#DCE6F5", "#2C3A52"),
    "tabelle_zeile": ("#F7F8FA", "#262A31"),
}

# Code-Blöcke (tk.Text kennt keine Tupel -> getrennt)
CODE_FARBEN = {
    "Dark": {
        "hintergrund": "#0F1117", "text": "#E6E8EC", "keyword": "#C792EA",
        "typ": "#82AAFF", "string": "#C3E88D", "kommentar": "#6A7383",
        "zahl": "#F78C6C", "funktion": "#FFCB6B", "zeilennr": "#4B5263",
    },
    "Light": {
        "hintergrund": "#F6F8FA", "text": "#24292F", "keyword": "#8250DF",
        "typ": "#0550AE", "string": "#0A7B35", "kommentar": "#6E7781",
        "zahl": "#CF222E", "funktion": "#953800", "zeilennr": "#A0A7B1",
    },
}

# Fliesstexte (FormatText)
TEXT_FARBEN = {
    "Dark":  {"hintergrund": "#23262D", "text": "#E6E8EC", "code_bg": "#343842", "ueberschrift": "#8AB4F8"},
    "Light": {"hintergrund": "#FFFFFF", "text": "#1D2939", "code_bg": "#EEF1F5", "ueberschrift": "#1F6FEB"},
}

# -----------------------------------------------------------------------------
# SCHRIFTEN
# -----------------------------------------------------------------------------
SCHRIFT = "Segoe UI"
SCHRIFT_CODE = "Consolas"

FONT_TITEL = (SCHRIFT, 26, "bold")
FONT_UNTERTITEL = (SCHRIFT, 15)
FONT_SEKTION = (SCHRIFT, 17, "bold")
FONT_TEXT = (SCHRIFT, 13)
FONT_KLEIN = (SCHRIFT, 11)
FONT_CODE = (SCHRIFT_CODE, 12)

# -----------------------------------------------------------------------------
# PROGRAMMIER-SEITE
# -----------------------------------------------------------------------------
SPRACHEN = ["Python", "C++", "C#"]
STANDARD_SPRACHE = "Python"
