# =============================================================================
# config.py
# -----------------------------------------------------------------------------
# Zentrale Einstellungen der ganzen Toolbox (Pfade, Farben, Schriften, Layout).
# Hier ändern -> wirkt überall.   Zugriff:  import config  ->  config.FARBEN["akzent"]
# =============================================================================

import os
import sys

# -----------------------------------------------------------------------------
# PFADE (funktionieren egal von wo das Programm gestartet wird)
# -----------------------------------------------------------------------------

# Programmdateien (nur lesen) -> in der EXE der entpackte Ordner
if getattr(sys, "frozen", False):
    BASIS_PFAD = sys._MEIPASS
else:
    BASIS_PFAD = os.path.dirname(os.path.abspath(__file__))

# Schreibbare Dateien (z.B. haenger_log.txt) -> EXE: %LOCALAPPDATA%\SystemLab
if getattr(sys, "frozen", False):
    DATEN_PFAD = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "SystemLab")
else:
    DATEN_PFAD = BASIS_PFAD
os.makedirs(DATEN_PFAD, exist_ok=True)

BILDER_PFAD = os.path.join(BASIS_PFAD, "images")
BILDER_PROGRAMMIEREN = os.path.join(BILDER_PFAD, "programmieren")
INHALTE_PROGRAMMIEREN = os.path.join(BASIS_PFAD, "programmieren", "inhalte")
INHALTE_SERVER = os.path.join(BASIS_PFAD, "server", "inhalte")          # -> Tab "Server / Linux"
# -----------------------------------------------------------------------------
# APP
# -----------------------------------------------------------------------------
APP_NAME = "SystemLab"               # EINZIGE Stelle für den Namen (Fenstertitel, Banner, Hilfe ...)
APP_VERSION = "0.2 Beta"            # bei neuer Version hier UND in der Tester-Anleitung anpassen
APP_TITEL = APP_NAME                # alter Name der Konstante (wird noch an einigen Stellen gelesen)
APP_UNTERTITEL = "Dein Begleiter für Studium und Praxis"
APP_ICON = os.path.join(BASIS_PFAD, "images", "systemlab.ico")       # Fenster-Icon (Windows)
APP_LOGO = os.path.join(BASIS_PFAD, "images", "systemlab.png")       # dasselbe Logo als PNG

TEXT_ZURUECKSETZEN = "↺ Zurücksetzen"   # Knopf bei Rechnern und Schaltungen: alles auf die Startwerte

# Mausrad: so viele Pixel pro Raststufe (Windows: 1 Raststufe = delta 120). customtkinter allein: 20 px
SCROLL_PIXEL_PRO_RAST = 60

# Zoom (Ctrl + Mausrad, Ctrl + Plus / Minus, Ctrl + 0) - Stufen in Prozent
ZOOM_STUFEN = (50, 67, 75, 90, 100, 110, 125, 150, 175, 200)
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
    "gefahr":        ("#FDECEC", "#3B1A1A"),       # 🔒 Sicherheits-Box (Server-Wiki)
    "tabelle_kopf":  ("#DCE6F5", "#2C3A52"),
    "tabelle_zeile": ("#F7F8FA", "#262A31"),
}

# Code-Blöcke (tk.Text kennt keine Tupel -> getrennt)
CODE_FARBEN = {
    "Dark": {
        "hintergrund": "#0F1117", "text": "#E6E8EC", "keyword": "#C792EA",
        "typ": "#82AAFF", "string": "#C3E88D", "kommentar": "#6A7383",
        "zahl": "#F78C6C", "funktion": "#FFCB6B", "zeilennr": "#4B5263",
        "gefahr": "#FFB4AB", "gefahr_bg": "#5C1F1F",          # gefährliche Befehle (rm -rf ...)
    },
    "Light": {
        "hintergrund": "#F6F8FA", "text": "#24292F", "keyword": "#8250DF",
        "typ": "#0550AE", "string": "#0A7B35", "kommentar": "#6E7781",
        "zahl": "#CF222E", "funktion": "#953800", "zeilennr": "#A0A7B1",
        "gefahr": "#B42318", "gefahr_bg": "#FEE4E2",
    },
}

def code_paar(name):
    """Code-Farbe als Paar (Light, Dark) -> customtkinter wechselt sie beim Umschalten selbst."""
    return (CODE_FARBEN["Light"][name], CODE_FARBEN["Dark"][name])


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

# -----------------------------------------------------------------------------
# SERVER-SEITE  (gleiche Wiki-Maschine, aber nur eine "Sprache" -> kein Umschalter)
# -----------------------------------------------------------------------------
SERVER_SPRACHE = "Bash"
