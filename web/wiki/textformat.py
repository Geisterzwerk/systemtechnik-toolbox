# =============================================================================
# web/wiki/textformat.py
# -----------------------------------------------------------------------------
# TEXT DER INHALTE -> HTML. Dieselben Regeln wie in der Desktop-App (core/widgets.py FormatText):
#
#   ## Überschrift          -> <h2>        ### Unterüberschrift -> <h3>
#   - Punkt                 -> Aufzählung  (2 Leerzeichen davor = eine Stufe tiefer)
#   1. Schritt              -> nummerierte Liste
#   **fett**  `code`        -> <strong>  <code>
#   leere Zeile             -> neuer Absatz
#
# SICHERHEIT: Zuerst wird ALLES escaped (< > & werden harmlos), erst dann setzen wir
# eigene Tags. So kann kein Text aus einer Inhaltsdatei HTML oder JavaScript einschleusen.
#
# WER RUFT DAS AUF?  web/wiki/templatetags/systemlab.py (Filter "format" und "inline")
# =============================================================================

import html
import re

_INLINE = re.compile(r"(\*\*.+?\*\*|`.+?`)")
_NUMMER = re.compile(r"^(\d+)\.\s+(.*)$")


def inline(text):
    """**fett** und `code` in einer Zeile -> HTML (alles andere escaped)."""
    teile = []
    for teil in _INLINE.split(str(text)):
        if not teil:
            continue
        if teil.startswith("**") and teil.endswith("**") and len(teil) > 4:
            teile.append(f"<strong>{inline(teil[2:-2])}</strong>")
        elif teil.startswith("`") and teil.endswith("`") and len(teil) > 2:
            teile.append(f"<code>{html.escape(teil[1:-1])}</code>")
        else:
            teile.append(html.escape(teil))
    return "".join(teile)


def als_html(text):
    """Ganzer Text (mehrere Zeilen) -> HTML mit Überschriften, Listen und Absätzen."""
    ausgabe = []
    offen = []                   # offene Listen: [("ul", tiefe), ...]
    absatz = []                  # Zeilen des aktuellen Absatzes

    def absatz_schliessen():
        if absatz:
            ausgabe.append("<p>" + "<br>".join(absatz) + "</p>")
            absatz.clear()

    def listen_schliessen(bis_tiefe=-1):
        while offen and offen[-1][1] > bis_tiefe:
            art, _ = offen.pop()
            ausgabe.append(f"</li></{art}>")

    for roh in str(text).strip("\n").split("\n"):
        einzug = len(roh) - len(roh.lstrip(" "))
        zeile = roh.strip()
        if not zeile:
            absatz_schliessen()
            listen_schliessen()
            continue
        if zeile.startswith("### ") or zeile.startswith("## "):
            absatz_schliessen()
            listen_schliessen()
            stufe = "h3" if zeile.startswith("### ") else "h2"
            ausgabe.append(f"<{stufe}>{inline(zeile.split(' ', 1)[1])}</{stufe}>")
            continue
        nummer = _NUMMER.match(zeile)
        if zeile.startswith("- ") or nummer:
            absatz_schliessen()
            art = "ol" if nummer else "ul"
            tiefe = einzug // 2
            inhalt = inline(nummer.group(2) if nummer else zeile[2:])
            listen_schliessen(tiefe)                                         # tiefere Listen zu
            if offen and offen[-1][1] == tiefe and offen[-1][0] != art:      # gleiche Tiefe, andere Art
                listen_schliessen(tiefe - 1)
            if offen and offen[-1] == (art, tiefe):
                ausgabe.append(f"</li><li>{inhalt}")                         # nächster Punkt, gleiche Liste
            else:                                                            # neue Liste (auch verschachtelt)
                start = f' start="{nummer.group(1)}"' if nummer and nummer.group(1) != "1" else ""
                ausgabe.append(f"<{art}{start}><li>{inhalt}")
                offen.append((art, tiefe))
            continue
        if offen and einzug > 0:                                             # Fortsetzung eines Punkts
            ausgabe.append("<br>" + inline(zeile))
            continue
        listen_schliessen()
        absatz.append(inline(zeile))
    absatz_schliessen()
    listen_schliessen()
    return "".join(ausgabe)
