# =============================================================================
# programmieren/engine/suche.py
# -----------------------------------------------------------------------------
# Die SUCHFUNKTION der Programmier-Seite.
#
# ZIEL:  "if schleife", "ifelse", "wile", "datentyp int" ... sollen alle
#        die richtige Seite finden - auch mit Tippfehlern.
#
# SO WIRD GESUCHT (Punkte-System):
#   Für jedes Thema wird ein "Suchtext" gebaut aus:
#       Titel + Stichworte + Dateiname + Kurzbeschreibung
#       (+ im Server-Wiki: der Befehlsname jeder Zeile aus "befehle")
#   Dann bekommt jedes Thema Punkte:
#       - Suchbegriff ist genau ein Stichwort / Titel   -> viele Punkte
#       - Suchbegriff kommt als Teil vor ("schleif")    -> mittlere Punkte
#       - Suchbegriff ist ÄHNLICH (Tippfehler "wile")   -> wenige Punkte
#   Die Themen mit den meisten Punkten stehen oben.
#
# Kein tkinter hier -> kann man auch ohne GUI testen.
# =============================================================================

import difflib
import re

# Wörter, die bei der Suche ignoriert werden (bringen keine Information)
_FUELLWOERTER = {"in", "der", "die", "das", "wie", "was", "ist", "mit", "und", "ein", "eine", "man", "zu", "von"}


def _normalisieren(text):
    """Kleinschreibung, Umlaute vereinheitlichen, Sonderzeichen -> Leerzeichen."""
    text = text.lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(alt, neu)
    # C++ und C# sollen als Wörter erhalten bleiben
    text = text.replace("c++", " cpp ").replace("c#", " csharp ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


class Suchmaschine:
    """
    Benutzung:
        suche = Suchmaschine(themen)          # themen = dict aus lader.alle_laden()
        treffer = suche.suchen("while")       # -> Liste von Thema-Objekten
    """

    def __init__(self, themen):
        # Für jedes Thema einmalig die Wörter vorbereiten (schneller beim Tippen)
        self._index = []
        for thema in themen.values():
            haupt = {_normalisieren(thema.titel), thema.id.replace("_", " ")}
            haupt |= {_normalisieren(s) for s in thema.stichworte}
            alle_woerter = set()
            for eintrag in haupt | {_normalisieren(thema.kurz)}:
                alle_woerter |= set(eintrag.split())
            # Server-Wiki: Befehle aus "befehle" sind eigene, SCHWÄCHERE Suchwörter
            # ("sudo chmod 755 x" -> "chmod"), damit Titel und Stichworte vorne bleiben.
            befehle = set()
            for gruppe in thema.daten.get("befehle", []):
                for befehl, _erklaerung in gruppe.get("zeilen", []):
                    teile = [t for t in befehl.split() if t != "sudo"]
                    if teile:
                        befehle |= set(_normalisieren(teile[0]).split())
            # zusammengeschriebene Varianten ("if else" -> "ifelse")
            zusammen = {h.replace(" ", "") for h in haupt}
            self._index.append((thema, haupt, alle_woerter | zusammen, befehle))

    def suchen(self, anfrage, max_treffer=12):
        """Gibt die passendsten Themen zurück (beste zuerst)."""
        anfrage_norm = _normalisieren(anfrage)
        if not anfrage_norm:
            return []

        begriffe = [w for w in anfrage_norm.split() if w not in _FUELLWOERTER] or anfrage_norm.split()
        ergebnisse = []

        for thema, haupt, woerter, befehle in self._index:
            punkte = 0.0

            # 1) Ganze Anfrage ist genau ein Titel/Stichwort -> viele Punkte,
            #    kommt nur als Wort darin vor ("chmod" in "chmod 777") -> etwas weniger
            if anfrage_norm in haupt:
                punkte += 100
            elif anfrage_norm.replace(" ", "") in woerter:
                punkte += 60

            # 2) Jeden einzelnen Suchbegriff bewerten
            for begriff in begriffe:
                if begriff in woerter:
                    punkte += 30                                         # exaktes Wort
                elif any(w.startswith(begriff) for w in woerter) and len(begriff) >= 2:
                    punkte += 18                                         # Wortanfang ("schlei")
                elif any(begriff in w for w in woerter) and len(begriff) >= 3:
                    punkte += 10                                         # irgendwo enthalten
                elif begriff in befehle:
                    punkte += 12                                         # nur in einer Befehlsliste
                else:
                    # Tippfehler-Toleranz: ähnliche Wörter suchen (z.B. "wile" ~ "while")
                    aehnlich = difflib.get_close_matches(begriff, woerter, n=1, cutoff=0.75)
                    if aehnlich:
                        punkte += 8

            if punkte > 0:
                ergebnisse.append((punkte, thema))

        # Sortieren: meiste Punkte zuerst, dann nach Titel
        ergebnisse.sort(key=lambda p: (-p[0], p[1].reihenfolge, p[1].titel))
        return [thema for _, thema in ergebnisse[:max_treffer]]
