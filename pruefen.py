# =============================================================================
# pruefen.py  -  prüft, ob die neuen Bauteil-Dateien wirklich aktiv sind
# Starten im Projektordner:   python pruefen.py
# =============================================================================
import os, sys
basis = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, basis)

def check(text, ok):
    print(("  OK    " if ok else "  FEHLT ") + text)
    return ok

print("Projektordner:", basis)
alles = True
alles &= check("gui/bauteile_gui.py ist die NEUE Version (gemeinsamer WikiBereich)",
               "WikiBereich" in open(os.path.join(basis, "gui", "bauteile_gui.py"), encoding="utf-8").read())
for pfad in ["bauteile/einheiten.py", "bauteile/engine/seite.py", "bauteile/rechner/basis.py",
             "bauteile/inhalte/01_passiv/widerstand.py", "bauteile/grafiken/trafo_animation.py",
             "bauteile/inhalte/03_transistoren/bipolartransistor.py", "bauteile/rechner/halbleiter_rechner.py",
             "bauteile/inhalte/02_dioden/diode.py", "bauteile/rechner/transistor_rechner.py",
             "messtechnik/rechner.py", "gui/messtechnik_gui.py",
             "bauteile/inhalte/04_schalten/relais.py", "bauteile/rechner/relais_rechner.py",
             "core/layout.py", "programmieren/engine/lader.py",
             "gui/server_gui.py", "programmieren/engine/befehlsliste.py",
             "server/inhalte/00_schnellstart/spickzettel.py",
             "pruefen_rechner.py", "pruefung/rechner_faelle.py",
             "gui/rechner_gui.py", "bauteile/rechner/rechner_info.py",
             "bauteile/engine/wiki_bereich.py", "bauteile/grafiken/schaltplan.py",
             "schaltungen/rechner.py", "schaltungen/inhalte/_vorlage.py",
             "schaltungen/rc_mathe.py", "schaltungen/grafiken_rc.py",
             "schaltungen/opv_mathe.py", "schaltungen/grafiken_opv.py",
             "schaltungen/netzteil_mathe.py", "schaltungen/grafiken_netzteil.py",
             "gui/digitaltechnik_gui.py", "digitaltechnik/rechner.py", "digitaltechnik/zahlen_mathe.py",
             "digitaltechnik/pegel_mathe.py", "digitaltechnik/grafiken.py", "digitaltechnik/inhalte/_vorlage.py",
             "digitaltechnik/logik_mathe.py", "digitaltechnik/grafiken_logik.py",
             "digitaltechnik/schaltnetze_mathe.py", "digitaltechnik/grafiken_schaltnetze.py",
             "digitaltechnik/schaltwerke_mathe.py", "digitaltechnik/grafiken_schaltwerke.py",
             "digitaltechnik/busse_mathe.py", "digitaltechnik/grafiken_busse.py",
             "schaltungen/filter_mathe.py", "schaltungen/grafiken_filter.py", "bauteile/grafiken/skala.py"]:
    alles &= check(pfad, os.path.exists(os.path.join(basis, pfad)))
doppelt = os.path.join(basis, "SystemtechnikToolbox")
if os.path.isdir(doppelt):
    print("  FEHLT  Es gibt einen doppelten Ordner SystemtechnikToolbox\\SystemtechnikToolbox -> Inhalt eine Ebene hoch verschieben!")
    alles = False
print("\nAlles bereit – python main.py starten" if alles else "\nBitte die markierten Punkte beheben")
