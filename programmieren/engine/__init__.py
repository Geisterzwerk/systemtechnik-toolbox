# =============================================================================
# programmieren/engine/  -> Die "Maschine" hinter der Programmier-Seite
#
#   lader.py      findet & lädt alle Themen-Dateien aus programmieren/inhalte/
#   suche.py      Suchfunktion (mit Tippfehler-Toleranz)
#   syntax.py     färbt Code ein (Syntax-Highlighting)
#   codeblock.py  GUI-Baustein: Code-Kasten mit Kopieren-Button
#   seite.py      zeichnet EINE Themen-Seite (Titel, Text, Bild, Tabelle, Code, ...)
#
# Der Ablauf:
#   gui/programmieren_gui.py
#       -> lader.alle_laden()            (Daten holen)
#       -> Suchmaschine(themen)          (Suche vorbereiten)
#       -> seite.ThemenSeite(...)        (Seite anzeigen, wenn man klickt)
#               -> codeblock.CodeBlock   (für jedes Codebeispiel)
#                       -> syntax.zerlegen() (Farben)
# =============================================================================
