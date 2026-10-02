# =============================================================================
# bauteile/einheiten.py
# -----------------------------------------------------------------------------
# EINHEITEN für alle Rechner: welche Einheiten es gibt, Eingaben verstehen,
# Ergebnisse schön formatieren.
#
# EINGABE - das versteht text_zu_zahl():
#   "4.7"  "4,7"            -> Zahl × gewählte Einheit im Dropdown
#   "4.7k"  "4k7"  "2M2"    -> Vorsatz direkt im Text (Dropdown wird ignoriert)
#   "470m"  "4R7"  "R47"    -> m = milli, R = Komma (wie auf Bauteilen)
#   "1e-3"                  -> Exponent-Schreibweise
#   "1A"  "5V"              -> Einheit mitgetippt: gilt statt Dropdown (1A im mA-Feld = 1 A)
#   "inf"  "nan"            -> werden abgelehnt (damit kann kein Rechner rechnen)
#
# AUSGABE - formatieren(0.0047, "widerstand") -> "4.7 mΩ"
#   Der Vorsatz (m, k, M ...) wird automatisch passend gewählt.
#
# NEUE EINHEIT? Unten in EINHEITEN eine Zeile ergänzen - fertig.
# =============================================================================

import math
import re

# typ -> Einstellungen
#   stufen      Auswahl im Dropdown: (Anzeige, Faktor zur Basiseinheit)
#   standard    vorausgewählte Stufe
#   vorsatz     True = Eingaben wie "4k7" / "10m" erlaubt (nur bei SI-Grössen sinnvoll)
EINHEITEN = {
    "widerstand":    {"stufen": [("mΩ", 1e-3), ("Ω", 1), ("kΩ", 1e3), ("MΩ", 1e6)], "standard": "Ω", "vorsatz": True},
    "spannung":      {"stufen": [("µV", 1e-6), ("mV", 1e-3), ("V", 1), ("kV", 1e3)], "standard": "V", "vorsatz": True},
    "strom":         {"stufen": [("µA", 1e-6), ("mA", 1e-3), ("A", 1), ("kA", 1e3)], "standard": "A", "vorsatz": True},
    "leistung":      {"stufen": [("µW", 1e-6), ("mW", 1e-3), ("W", 1), ("kW", 1e3)], "standard": "W", "vorsatz": True},
    "kapazitaet":    {"stufen": [("pF", 1e-12), ("nF", 1e-9), ("µF", 1e-6), ("mF", 1e-3), ("F", 1)], "standard": "µF", "vorsatz": True},
    "induktivitaet": {"stufen": [("nH", 1e-9), ("µH", 1e-6), ("mH", 1e-3), ("H", 1)], "standard": "mH", "vorsatz": True},
    "zeit":          {"stufen": [("ns", 1e-9), ("µs", 1e-6), ("ms", 1e-3), ("s", 1)], "standard": "ms", "vorsatz": True},
    "frequenz":      {"stufen": [("Hz", 1), ("kHz", 1e3), ("MHz", 1e6), ("GHz", 1e9)], "standard": "Hz", "vorsatz": True},
    "energie":       {"stufen": [("µJ", 1e-6), ("mJ", 1e-3), ("J", 1), ("kJ", 1e3)], "standard": "J", "vorsatz": True},
    "ladung":        {"stufen": [("nC", 1e-9), ("µC", 1e-6), ("mC", 1e-3), ("C", 1)], "standard": "µC", "vorsatz": True},
    "flussdichte":   {"stufen": [("mT", 1e-3), ("T", 1)], "standard": "T", "vorsatz": True},
    "laenge":        {"stufen": [("mm", 1e-3), ("cm", 1e-2), ("m", 1), ("km", 1e3)], "standard": "m", "vorsatz": False},
    "flaeche":       {"stufen": [("mm²", 1e-6), ("cm²", 1e-4), ("m²", 1)], "standard": "mm²", "vorsatz": False},
    "temperatur":    {"stufen": [("°C", 1)], "standard": "°C", "vorsatz": False},
    "prozent":       {"stufen": [("%", 0.01)], "standard": "%", "vorsatz": False},
    "zahl":          {"stufen": [("", 1)], "standard": "", "vorsatz": False},
}

# SI-Vorsätze, die man direkt eintippen darf (R = Komma, Faktor 1)
_VORSATZ = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3,
            "R": 1, "r": 1, "k": 1e3, "K": 1e3, "M": 1e6, "G": 1e9}

# Einheitenzeichen, die jemand mittippt ("4.7kΩ", "10mA") -> werden entfernt
_EINHEIT_AM_ENDE = re.compile(r"(ohm|Ω|Hz|hz|V|A|W|F|H|J|C|s)$")

_ZAHL = r"\d+(?:\.\d*)?|\.\d+"


def text_zu_zahl(text, typ, faktor=1.0):
    """
    Wandelt eine Eingabe in einen Wert in der BASIS-Einheit um (Ω, V, A, F ...).
    text    was im Feld steht
    typ     Schlüssel aus EINHEITEN
    faktor  Faktor der Dropdown-Auswahl (z.B. 1000 bei kΩ)
    Rückgabe: float oder None (Feld leer).  Fehler -> ValueError mit Erklärung.
    """
    t = (text or "").strip().replace(" ", "").replace(",", ".").replace("'", "")
    if not t:
        return None

    # 1) ganz normale Zahl (auch 1e-3) -> × Dropdown
    try:
        zahl = float(t)
    except ValueError:
        zahl = None
    if zahl is not None:
        # float() versteht auch "inf", "nan" und "1e999" (= unendlich) - damit kann niemand rechnen
        if not math.isfinite(zahl):
            raise ValueError(f"„{text}“ ist keine gültige Zahl")
        return zahl * faktor

    if not EINHEITEN[typ]["vorsatz"]:
        raise ValueError(f"„{text}“ ist keine gültige Zahl")

    ohne_einheit = _EINHEIT_AM_ENDE.sub("", t)  # "4.7kΩ" -> "4.7k"
    einheit_getippt = ohne_einheit != t
    t = ohne_einheit
    vz = "".join(re.escape(v) for v in _VORSATZ)

    # 2) Zahl + Vorsatz:  4.7k   470m   10u
    m = re.fullmatch(rf"([+-]?(?:{_ZAHL}))([{vz}])", t)
    if m:
        return float(m.group(1)) * _VORSATZ[m.group(2)]
    # 3) Vorsatz als Komma:  4k7   2M2   4R7
    m = re.fullmatch(rf"([+-]?\d+)([{vz}])(\d+)", t)
    if m:
        return float(f"{m.group(1)}.{m.group(3)}") * _VORSATZ[m.group(2)]
    # 4) Vorsatz vorne:  R47  (= 0.47)
    m = re.fullmatch(rf"([{vz}])(\d+)", t)
    if m:
        return float(f"0.{m.group(2)}") * _VORSATZ[m.group(1)]
    # 5) nur Zahl ohne Vorsatz, aber mit Einheit ("5V", "1A")
    #    -> die Einheit gilt, NICHT das Dropdown: "1A" im mA-Feld ist 1 A, nicht 1 mA
    try:
        return float(t) * (1.0 if einheit_getippt else faktor)
    except ValueError:
        raise ValueError(f"„{text}“ verstehe ich nicht (Beispiele: 4.7  4k7  2.2M  470m)") from None


def text_zu_liste(text, typ, faktor=1.0):
    """'1k, 2k2; 470' -> [1000.0, 2200.0, 470.0]  (Trennzeichen: Komma, Semikolon, Leerzeichen)"""
    if not (text or "").strip():
        return None
    # Kommas zwischen Werten vs. Dezimalkomma: Werte mit ; oder Leerzeichen trennen ist eindeutig.
    # Wenn nur Kommas vorkommen, gelten sie als Trennzeichen (Dezimalpunkt benutzen!).
    teile = re.split(r"[;\s]+", text.strip()) if re.search(r"[;\s]", text.strip()) else text.split(",")
    return [text_zu_zahl(t, typ, faktor) for t in teile if t.strip()]


def formatieren(wert, typ, stellen=4):
    """0.0047 Ω -> '4.7 mΩ'.  Wählt die passende Stufe aus EINHEITEN automatisch."""
    if wert is None:
        return "–"
    stufen = EINHEITEN[typ]["stufen"]
    if len(stufen) == 1:
        name, faktor = stufen[0]
        return f"{_zahl_text(wert / faktor, stellen)} {name}".strip()
    if wert == 0:
        basis = next((n for n, f in stufen if f == 1), stufen[0][0])
        return f"0 {basis}"
    # grösste Stufe, bei der die Zahl >= 1 ist
    name, faktor = stufen[0]
    for n, f in stufen:
        if abs(wert) / f >= 1 - 1e-12:
            name, faktor = n, f
    return f"{_zahl_text(wert / faktor, stellen)} {name}"


def _zahl_text(zahl, stellen):
    if abs(zahl) >= 10 ** stellen:
        return f"{zahl:,.0f}".replace(",", "'")          # 12'345 (Schweizer Tausendertrennung)
    text = f"{zahl:.{stellen}g}"
    if "e" in text:                                      # sehr kleine Zahl ausserhalb der Stufen
        return f"{zahl:.3e}"
    return text


def stufe_waehlen(wert, typ):
    """Beste Dropdown-Stufe für einen Wert: (name, zahl_in_dieser_stufe)."""
    stufen = EINHEITEN[typ]["stufen"]
    name, faktor = stufen[0]
    for n, f in stufen:
        if wert and abs(wert) / f >= 1 - 1e-12:
            name, faktor = n, f
    if wert == 0 and any(f == 1 for _, f in stufen):
        name, faktor = next((n, f) for n, f in stufen if f == 1)
    return name, wert / faktor
