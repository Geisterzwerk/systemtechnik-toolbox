# =============================================================================
# SystemLab.spec  -  Bauplan für die Desktop-EXE (PyInstaller)
# -----------------------------------------------------------------------------
# Starten:  build_exe.bat   (oder: python -m PyInstaller SystemLab.spec --noconfirm --clean)
#
# KOMMT REIN:   main.py, config.py, die Desktop-Ordner unten (ORDNER), images/ (nur .png),
#               images/systemlab.ico (Icon), customtkinter-Themes
# KOMMT NICHT:  web/, pruefung/, uebungen/, pruefen*.py, benutzerdaten.json,
#               haenger_log.txt, datentypen_bits.json, .git, __pycache__, dist/
# =============================================================================
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

PROJEKT = os.path.abspath(SPECPATH)
sys.path.insert(0, PROJEKT)               # damit collect_submodules die Projekt-Pakete findet

EINE_DATEI = False      # False = Ordner mit SystemLab.exe (schneller Start, empfohlen)
                        # True  = eine einzelne SystemLab.exe (entpackt sich bei jedem Start)

# Desktop-Bereiche -> neuer Bereich = hier ergänzen
ORDNER = ["bauteile", "core", "digitaltechnik", "gui", "messtechnik",
          "programmieren", "schaltungen", "server"]


def dateien_sammeln(ordner, nur_endungen=None):
    """Alle Dateien eines Ordners (ohne __pycache__) als (quelle, ziel) für PyInstaller."""
    paare = []
    for wurzel, unterordner, dateien in os.walk(os.path.join(PROJEKT, ordner)):
        unterordner[:] = [d for d in unterordner if d != "__pycache__"]
        for datei in dateien:
            if datei.endswith((".pyc", ".pyo")):
                continue
            if nur_endungen and not datei.lower().endswith(nur_endungen):
                continue
            paare.append((os.path.join(wurzel, datei), os.path.relpath(wurzel, PROJEKT)))
    return paare


# ---- Daten: Wiki-Seiten (werden zur Laufzeit aus Ordnern geladen) + Bilder ----
datas = collect_data_files("customtkinter")          # Themes/JSON von customtkinter
for o in ORDNER:
    datas += dateien_sammeln(o)
datas += dateien_sammeln("images", (".png", ".ico"))      # .ico = Fenster-Icon (config.APP_ICON)

# ---- Module, die nur per Name/Ordner geladen werden (Rechner-Registry, Inhalte) ----
# Entwickler-Werkzeuge (z. B. Bilder erzeugen) nicht in die EXE
hiddenimports = []
for o in ORDNER:
    hiddenimports += collect_submodules(o, filter=lambda name: ".werkzeuge" not in name)

a = Analysis(
    ["main.py"],
    pathex=[PROJEKT],
    datas=datas,
    hiddenimports=hiddenimports,
    excludes=["django"],
    noarchive=False,
)
pyz = PYZ(a.pure)
ICON = os.path.join(PROJEKT, "images", "systemlab.ico")       # EXE-Icon (Logo: gui/werkzeuge/icon_erstellen.py)

if EINE_DATEI:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [],
              name="SystemLab", console=False, upx=False, icon=ICON)
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True,
              name="SystemLab", console=False, upx=False, icon=ICON)
    coll = COLLECT(exe, a.binaries, a.datas, name="SystemLab", upx=False)
