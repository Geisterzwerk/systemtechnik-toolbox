# =============================================================================
# digitaltechnik/grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Digitaltechnik (Grundlagen) - MODELLE OHNE FENSTER (Desktop-App UND Web):
#
#   ZahlensystemKarte      Zahl eintippen (Basis wählen) -> Bits, Dez/Bin/Hex/Okt/BCD/Gray/ASCII
#   ZweierkomplementKarte  Zahlenkreis (4 / 8 Bit), a + b mit Carry- und Overflow-Flag
#   BitmaskenKarte         Register x + Maske eintippen, AND / OR / XOR / NOT / Schieben, C-Ausdruck
#   LogikpegelKarte        Sender- und Empfängerfamilie wählen -> Pegelbänder und Störabstände
#
#   bitreihe(...)          Baustein: Reihe von Bits (Bit n-1 … 0) mit Wertigkeiten, gezeichnet
#
# Rechnung: digitaltechnik/zahlen_mathe.py, digitaltechnik/pegel_mathe.py
# Die Modell-Grundlage (Regler, Auswahl, Textfelder, Varianten) steht in bauteile/grafiken/schaltplan.py.
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_zahlensystem"), Web und Desktop
# =============================================================================

import math

import config                                                            # -> config.py
from bauteile.grafiken.schaltplan import OK, WARN, SchaltungsModell, farbe_waehlen   # -> grafiken/schaltplan.py
from digitaltechnik import pegel_mathe as pm                             # -> digitaltechnik/pegel_mathe.py
from digitaltechnik import zahlen_mathe as zm                            # -> digitaltechnik/zahlen_mathe.py

FEHLER = ("#B91C1C", "#EF4444")
ORANGE = "#F59E0B"
BLAU, ROT, GRUEN, GELB = "#3B82F6", "#EF4444", "#22C55E", "#EAB308"


def farben(p):
    """(text, leise, linie, akzent) passend zu hell/dunkel"""
    return (farbe_waehlen(config.FARBEN["text"], p.dunkel), farbe_waehlen(config.FARBEN["text_leise"], p.dunkel),
            farbe_waehlen(config.FARBEN["rahmen"], p.dunkel), farbe_waehlen(config.FARBEN["akzent"], p.dunkel))


# =============================================================================
# BAUSTEIN: BITREIHE (gezeichnet)
# =============================================================================
def bitreihe(p, x0, y0, breite, muster, bits, titel="", markiert=0, signed=False):
    """
    [Titel]  128  64  32  16   8   4   2   1    <- Wertigkeit (bei signed: MSB = −2^(n−1))
             [1] [0] [1] [0] [0] [1] [0] [1]    <- Kästchen: 1 = Akzentfarbe, markiert = orange
    Höchstens 16 Bit pro Reihe; mehr -> weitere Reihen darunter. Rückgabe: y unter der letzten Reihe.
    """
    c = p.c
    text, leise, linie, akzent = farben(p)
    pro_reihe = min(bits, 16)
    titel_breite = 0.13 * breite if titel else 0
    feld = (breite - titel_breite) / (pro_reihe + 0.5)
    hoehe = min(feld * 0.9, 34)
    klein = (config.SCHRIFT, max(7, int(feld / 4.4)))
    fett = (config.SCHRIFT_CODE, max(8, int(hoehe / 2.2)), "bold")
    y = y0
    for index, nummer in enumerate(range(bits - 1, -1, -1)):
        reihe, spalte = divmod(index, pro_reihe)
        luecke = feld * 0.15 * (spalte // 4)                             # kleine Lücke alle 4 Bit (Nibble)
        x = x0 + titel_breite + spalte * feld + luecke
        y = y0 + reihe * (hoehe + feld * 0.55)
        gewicht = -(2 ** nummer) if (signed and nummer == bits - 1) else 2 ** nummer
        c.create_text(x + feld * 0.45, y + feld * 0.12, text=str(gewicht) if abs(gewicht) < 10000 else f"2^{nummer}",
                      fill=leise, font=klein)
        gesetzt = (muster >> nummer) & 1
        farbe = ORANGE if (markiert >> nummer) & 1 else (akzent if gesetzt else "")
        c.create_rectangle(x + feld * 0.05, y + feld * 0.28, x + feld * 0.85, y + feld * 0.28 + hoehe,
                           fill=farbe, outline=linie if not farbe else farbe, width=1)
        c.create_text(x + feld * 0.45, y + feld * 0.28 + hoehe / 2, text=str(gesetzt),
                      fill="#FFFFFF" if farbe else leise, font=fett)
    if titel:
        c.create_text(x0, y0 + feld * 0.28 + hoehe / 2, text=titel, anchor="w", fill=text,
                      font=(config.SCHRIFT, max(8, int(feld / 3.6))))
    return y + feld * 0.28 + hoehe


# =============================================================================
# ZAHLENSYSTEME
# =============================================================================
class ZahlensystemKarte(SchaltungsModell):
    TITEL = "🔢 Zahlensysteme umrechnen (interaktiv)"
    UNTERTITEL = "Zahl eintippen, Basis und Bitbreite wählen"
    VARIANTEN = ["8 Bit", "16 Bit", "32 Bit"]
    AUSWAHL = [("basis", "Eingabe ist", list(zm.BASEN), "Dezimal")]
    TEXTFELDER = [("zahl", "Zahl", "200", {"max": 40, "platzhalter": "z.B. 200, -5, 0xC8, 1100 1000"})]
    SEITENVERHAELTNIS = 0.22
    MAX_HOEHE = 220
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Dieselbe Zahl in verschiedenen Schreibweisen. Jedes Bit hat die "
                  "Wertigkeit 2^n (Bit 0 rechts = 1). Eine Hex-Ziffer fasst genau 4 Bit zusammen, eine Oktalziffer "
                  "3 Bit. BCD speichert jede Dezimalziffer einzeln in 4 Bit (Anzeigen, Uhren-ICs), der Gray-Code "
                  "ändert von Zahl zu Zahl nur EIN Bit (Drehgeber). Ob ein Bitmuster eine positive oder negative Zahl "
                  "ist, steht nicht im Muster – das legt der Datentyp fest (unsigned / signed).")

    def sk_rechnen(self, w, v):
        bits = int((v or "8 Bit").split()[0])
        wert = zm.einlesen(w["zahl"], zm.BASEN.get(w["basis"], 10))       # ValueError mit Erklärung
        if wert < -(2 ** (bits - 1)):
            raise ValueError(f"{wert} passt nicht in {bits} Bit (signed min. {-(2 ** (bits - 1))})")
        if wert >= 2 ** bits:
            raise ValueError(f"{wert} passt nicht in {bits} Bit (max. {2 ** bits - 1}) – grössere Bitbreite wählen")
        muster = zm.zweierkomplement(wert, bits)["muster"] if wert < 0 else wert
        return {"bits": bits, "muster": muster, "d": zm.darstellungen(muster, bits)}

    def sk_info(self, w, e, v):
        d = e["d"]
        zeilen = [f"Dezimal      {d['unsigned']}   (als signed: {d['signed']})", f"Binär        {d['bin']}",
                  f"Hexadezimal  0x{d['hex']}        Oktal  0o{d['okt']}", f"BCD          {d['bcd']}",
                  f"Gray-Code    {d['gray']}"]
        if d["ascii"]:
            zeilen.append(f"ASCII        '{d['ascii']}'")
        return zeilen, config.FARBEN["akzent"]

    def sk_zeichnen(self, p, w, e, v):
        bitreihe(p, 0.02 * p.breite, 0.08 * p.hoehe, 0.96 * p.breite, e["muster"], e["bits"])


# =============================================================================
# ZWEIERKOMPLEMENT MIT ZAHLENKREIS
# =============================================================================
class ZweierkomplementKarte(SchaltungsModell):
    TITEL = "🔄 Zweierkomplement und Überlauf (interaktiv)"
    UNTERTITEL = "Zahlenkreis: a einstellen, b dazuzählen – wann stimmt das Ergebnis nicht mehr?"
    VARIANTEN = ["4 Bit", "8 Bit"]
    REGLER = [("a", "a", "zahl", -8.0, 15.0, 5.0, {"ganzzahl": True, "grenzen": (-128, 255)}),
              ("b", "b (dazuzählen)", "zahl", -8.0, 15.0, 4.0, {"ganzzahl": True, "grenzen": (-128, 255)})]
    STARTWERTE = {"4 Bit": {"a": 5.0, "b": 4.0}, "8 Bit": {"a": 100.0, "b": 50.0}}
    SEITENVERHAELTNIS = 0.55
    MAX_HOEHE = 420
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Mit n Bit gibt es 2^n Muster – im Kreis angeordnet. Aussen steht die Deutung "
                  "als unsigned (0 … 2^n − 1), innen als signed im Zweierkomplement (−2^(n−1) … 2^(n−1) − 1): Das MSB "
                  "zählt negativ. Addieren heisst im Kreis weiterdrehen. Über die ORANGE Grenze (1111 → 0000) gibt es "
                  "einen Übertrag C – falsch, wenn man unsigned rechnet. Über die ROTE Grenze (0111 → 1000) springt das "
                  "Vorzeichen: Overflow V – falsch, wenn man signed rechnet. Negativ machen: alle Bits invertieren und "
                  "1 addieren. (a und b dürfen signed oder unsigned eingegeben werden.)")

    def sk_rechnen(self, w, v):
        bits = int((v or "4 Bit").split()[0])
        tief, hoch = -(2 ** (bits - 1)), 2 ** bits - 1                     # signed ODER unsigned erlaubt
        a, b = round(w["a"]), round(w["b"])
        for name, x in (("a", a), ("b", b)):
            if not tief <= x <= hoch:
                raise ValueError(f"{name} = {x} passt nicht in {bits} Bit (erlaubt {tief} … {hoch})")
        return {"bits": bits, "a": a, **zm.addieren(a, b, bits)}

    def sk_info(self, w, e, v):
        bits = e["bits"]
        sa, sb = zm.als_vorzeichen(e["muster_a"], bits), zm.als_vorzeichen(e["muster_b"], bits)
        ua, ub = e["muster_a"], e["muster_b"]
        zeilen = [f"  a = {e['bin_a']}   unsigned {ua:>4}   signed {sa:>4}",
                  f"+ b = {e['bin_b']}   unsigned {ub:>4}   signed {sb:>4}",
                  f"  = {'1 ' if e['carry'] else '  '}{e['bin_summe']}   unsigned {e['unsigned']:>4}   signed {e['signed']:>4}",
                  f"C (Carry) = {int(e['carry'])}  → unsigned " + (f"FALSCH (richtig wäre {ua + ub})" if e["carry"] else "stimmt"),
                  f"V (Overflow) = {int(e['overflow'])}  → signed " + (f"FALSCH (richtig wäre {sa + sb})" if e["overflow"] else "stimmt")]
        if e["a"] < 0:
            z = zm.zweierkomplement(e["a"], bits)
            zeilen.append(f"−{-e['a']}:  {z['betrag']}  → invertiert {z['invertiert']}  → +1 = {z['plus_eins']}")
        return zeilen, (WARN if (e["carry"] or e["overflow"]) else OK)

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        bits = e["bits"]
        n = 2 ** bits
        text, leise, linie, _ = farben(p)
        mx, my = wb * 0.36, h * 0.5
        aussen = 1.68 if bits == 4 else 1.28
        r = min(wb * 0.27, (h * 0.5 - 10) / aussen)
        schrift = (config.SCHRIFT_CODE, max(7, int(r / 13)))
        klein = (config.SCHRIFT, max(7, int(r / 16)))

        def punkt(k, radius):                     # Muster k: 0 oben, im Uhrzeigersinn
            winkel = 2 * math.pi * k / n - math.pi / 2
            return mx + radius * math.cos(winkel), my + radius * math.sin(winkel)

        c.create_oval(mx - r, my - r, mx + r, my + r, outline=linie, width=2)
        for k, farbe in ((0, ORANGE), (n // 2, ROT)):                     # Grenzen für C und V
            x0, y0 = punkt(k - 0.5, r * 0.55)
            x1, y1 = punkt(k - 0.5, r * 1.12)
            c.create_line(x0, y0, x1, y1, fill=farbe, width=3)
        for k in range(0, n, 1 if bits == 4 else 16):
            x, y = punkt(k, r)
            c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=leise, outline="")
            xa, ya = punkt(k, r * 1.2)
            if bits == 4:
                c.create_text(xa, ya, text=format(k, "04b"), fill=leise, font=schrift)
                xu, yu = punkt(k, r * 1.58)
                c.create_text(xu, yu, text=str(k), fill=text, font=klein)
            else:
                c.create_text(xa, ya, text=str(k), fill=text, font=klein)
            xi, yi = punkt(k, r * 0.78)
            c.create_text(xi, yi, text=str(zm.als_vorzeichen(k, bits)), fill=BLAU, font=klein)
        schritte = e["muster_b"]                                            # Bogen von a bis Summe
        if schritte:
            punkte = [q for t in range(41) for q in punkt(e["muster_a"] + schritte * t / 40, r * 0.62)]
            c.create_line(*punkte, fill=ORANGE if e["carry"] else GRUEN, width=3, arrow="last", arrowshape=(10, 12, 4))
        for k, farbe in ((e["muster_a"], BLAU), (e["summe"], ROT if e["overflow"] or e["carry"] else GRUEN)):
            x, y = punkt(k, r)
            c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=farbe, outline="")
        lx, ly = wb * 0.72, h * 0.18                                        # Legende rechts
        for i, (farbe, t) in enumerate(((leise, "aussen: unsigned"), (BLAU, "innen: signed"),
                                         (ORANGE, "Grenze für C (unsigned)"), (ROT, "Grenze für V (signed)"))):
            c.create_line(lx, ly + i * h * 0.1, lx + 18, ly + i * h * 0.1, fill=farbe, width=4)
            c.create_text(lx + 24, ly + i * h * 0.1, text=t, anchor="w", fill=text, font=klein)


# =============================================================================
# BITMASKEN
# =============================================================================
class BitmaskenKarte(SchaltungsModell):
    TITEL = "🎭 Bitmasken: Bits setzen, löschen, umschalten, prüfen (interaktiv)"
    UNTERTITEL = "Register x und Maske eintippen (Hex, oder 0b… binär), Operation wählen"
    KURZ = ["AND", "OR", "AND NOT", "XOR", "NOT", "<<", ">>"]
    VARIANTEN = ["OR", "AND", "AND NOT", "XOR", "NOT", "<<", ">>"]
    TEXTFELDER = [("x", "Register x", "A5", {"max": 20, "platzhalter": "Hex, z.B. A5 oder 0b1010 0101"}),
                  ("m", "Maske", "08", {"max": 20, "platzhalter": "Hex, z.B. 08"})]
    REGLER = [("schieben", "Schieben um (nur << und >>)", "zahl", 0.0, 7.0, 1.0, {"ganzzahl": True})]
    SEITENVERHAELTNIS = 0.34
    MAX_HOEHE = 300
    ERKLAERUNG = ("Was zeigt das Werkzeug?  In Mikrocontroller-Registern steuert jedes Bit etwas anderes (Pin, "
                  "Interrupt, Takt). Mit einer Maske ändert man nur die gewünschten Bits: OR setzt, AND NOT löscht, XOR "
                  "schaltet um, AND prüft (Ergebnis ≠ 0 → Bit gesetzt). Schieben um n Stellen multipliziert bzw. teilt "
                  "durch 2^n – herausgeschobene Bits gehen verloren. Orange = Bits, die sich gegenüber x geändert "
                  "haben. Masken schreibt man meist als (1 << n).")

    @staticmethod
    def _byte(text, name):
        wert = zm.einlesen(text, None if str(text).strip().lower().startswith(("0b", "0o")) else 16)
        if not 0 <= wert <= 255:
            raise ValueError(f"{name} muss zwischen 0x00 und 0xFF liegen (8 Bit)")
        return wert

    def sk_rechnen(self, w, v):
        x, m = self._byte(w["x"], "Register x"), self._byte(w["m"], "Maske")
        op_kurz = v if v in self.KURZ else "OR"
        schritte = round(w["schieben"])
        e = zm.bitoperation(x, m, zm.OPERATIONEN[self.KURZ.index(op_kurz)], 8, schritte)
        return {**e, "x": x, "m": m, "op": op_kurz, "schritte": schritte}

    def sk_info(self, w, e, v):
        bits_m = [n for n in range(8) if (e["m"] >> n) & 1]
        maske_c = " | ".join(f"(1 << {n})" for n in reversed(bits_m)) or "0"
        zeilen = [f"x = 0x{e['x']:02X} = {zm.binaer(e['x'], 8)}     Maske = 0x{e['m']:02X} = {maske_c}",
                  f"C:  {e['c']}   →   0x{e['ergebnis']:02X} = {e['bin']}  ({e['ergebnis']})"]
        if e["op"] == "AND":
            zeilen.append("Prüfen: " + ("Ergebnis ≠ 0 → mindestens ein Bit der Maske ist gesetzt" if e["ergebnis"]
                                        else "Ergebnis = 0 → kein Bit der Maske ist gesetzt"))
        elif e["op"] in ("<<", ">>"):
            faktor = f"× {2 ** e['schritte']}" if e["op"] == "<<" else f"÷ {2 ** e['schritte']} (abgerundet)"
            zeilen.append(f"entspricht {faktor}" + (f"   ·   verlorene Bits: {e['verloren']:b}" if e["verloren"] else ""))
        return zeilen, config.FARBEN["akzent"]

    def sk_zeichnen(self, p, w, e, v):
        x0, breite, zeile = 0.02 * p.breite, 0.7 * p.breite, p.hoehe / 3.3
        y = bitreihe(p, x0, 0.04 * p.hoehe, breite, e["x"], 8, "Register x")
        if e["op"] not in ("NOT", "<<", ">>"):
            y = bitreihe(p, x0, y + 0.02 * p.hoehe, breite, e["m"], 8, "Maske")
        bitreihe(p, x0, max(y + 0.02 * p.hoehe, 2 * zeile), breite, e["ergebnis"], 8, "Ergebnis", markiert=e["geaendert"])


# =============================================================================
# LOGIKPEGEL
# =============================================================================
class LogikpegelKarte(SchaltungsModell):
    TITEL = "📶 Logikpegel und Störabstand (interaktiv)"
    UNTERTITEL = "Passt ein Ausgang zu einem Eingang? Sender und Empfänger wählen"
    AUSWAHL = [("sender", "Sender (Ausgang)", list(pm.FAMILIEN), "ESP32 (3.3 V)"),
               ("empf", "Empfänger (Eingang)", list(pm.FAMILIEN), "74HC (5 V, Werte bei 4.5 V)")]
    SEITENVERHAELTNIS = 0.5
    MAX_HOEHE = 420
    ERKLAERUNG = ("Was zeigt das Werkzeug?  Links garantiert der Ausgang: HIGH liegt mindestens bei U_OH, LOW höchstens "
                  "bei U_OL. Rechts erkennt der Eingang sicher HIGH ab U_IH und sicher LOW bis U_IL – dazwischen ist der "
                  "Zustand undefiniert. Der Störabstand ist die Reserve dazwischen: S_H = U_OH − U_IH, S_L = U_IL − U_OL. "
                  "Ist er negativ, wird der Pegel nicht sicher erkannt. Liegt der Ausgang über der maximalen "
                  "Eingangsspannung, leiten die Schutzdioden – Pegelwandler nötig. Werte: garantierte "
                  "Datenblatt-Grenzwerte.")

    def sk_rechnen(self, w, v):
        return pm.kompatibel(w["sender"], w["empf"])

    def sk_info(self, w, e, v):
        s, r = e["sender"], e["empfaenger"]
        zeilen = [f"Störabstand HIGH  S_H = U_OH − U_IH = {s['u_oh']:.2f} V − {r['u_ih']:.2f} V = {e['s_h']:+.2f} V",
                  f"Störabstand LOW   S_L = U_IL − U_OL = {r['u_il']:.2f} V − {s['u_ol']:.2f} V = {e['s_l']:+.2f} V",
                  f"Ausgang bis {s['u_b']:.1f} V, Eingang verträgt {r['u_e_max']:.1f} V",
                  ("✓ " if e["ok"] else "❌ ") + e["rat"]]
        return zeilen, (OK if e["ok"] else FEHLER)

    def sk_zeichnen(self, p, w, e, v):
        c, wb, h = p.c, p.breite, p.hoehe
        s, r = e["sender"], e["empfaenger"]
        text, leise, _, _ = farben(p)
        u_top = max(s["u_b"], r["u_e_max"]) * 1.12
        oben, unten = h * 0.08, h * 0.9
        schrift = (config.SCHRIFT, max(8, int(h / 30)))
        fett = (config.SCHRIFT, max(8, int(h / 28)), "bold")

        def y(u):
            return unten - (unten - oben) * u / u_top

        def band(x0, x1, u0, u1, farbe, beschriftung):
            c.create_rectangle(x0, y(u1), x1, y(u0), fill=farbe, outline="")
            if beschriftung and y(u0) - y(u1) > 14:
                c.create_text((x0 + x1) / 2, (y(u0) + y(u1)) / 2, text=beschriftung, fill="#FFFFFF", font=schrift)

        c.create_line(wb * 0.08, y(0), wb * 0.08, y(u_top), fill=leise)
        for u in [x / 2 for x in range(0, int(u_top * 2) + 1)]:
            c.create_line(wb * 0.075, y(u), wb * 0.08, y(u), fill=leise)
            if u == int(u):
                c.create_text(wb * 0.07, y(u), text=f"{u:.0f} V", anchor="e", fill=leise, font=schrift)
        xs0, xs1 = wb * 0.28, wb * 0.42                                     # Sender
        band(xs0, xs1, s["u_oh"], s["u_b"], "#15803D", "HIGH")
        band(xs0, xs1, 0, s["u_ol"], "#1D4ED8", "LOW")
        band(xs0, xs1, s["u_ol"], s["u_oh"], farbe_waehlen(("#D0D5DD", "#3A3F4A"), p.dunkel), "")
        c.create_text((xs0 + xs1) / 2, oben - 2, text="Ausgang (Sender)", anchor="s", fill=text, font=fett)
        xe0, xe1 = wb * 0.66, wb * 0.80                                     # Empfänger
        band(xe0, xe1, r["u_ih"], r["u_e_max"], "#15803D", "HIGH")
        band(xe0, xe1, 0, r["u_il"], "#1D4ED8", "LOW")
        band(xe0, xe1, r["u_il"], r["u_ih"], "#A16207", "undefiniert")
        if u_top > r["u_e_max"]:
            band(xe0, xe1, r["u_e_max"], u_top, "#B91C1C", "zu hoch")
        c.create_text((xe0 + xe1) / 2, oben - 2, text="Eingang (Empfänger)", anchor="s", fill=text, font=fett)
        for x, anker, werte in ((xs0 - 4, "e", (("U_OH", s["u_oh"]), ("U_OL", s["u_ol"]))),
                                (xe1 + 4, "w", (("U_IH", r["u_ih"]), ("U_IL", r["u_il"]), ("U_E,max", r["u_e_max"])))):
            for name, u in werte:
                c.create_text(x, y(u), text=f"{name} {u:.2f} V", anchor=anker, fill=text, font=schrift)
        xm = xs1 + wb * 0.04                                                # Störabstände als Pfeile
        for (u_von, u_bis, name, wert) in ((s["u_oh"], r["u_ih"], "S_H", e["s_h"]), (s["u_ol"], r["u_il"], "S_L", e["s_l"])):
            farbe = GRUEN if wert >= 0 else ROT
            c.create_line(xs1, y(u_von), xm, y(u_von), xm, y(u_bis), xe0, y(u_bis), fill=farbe, width=2, dash=(4, 3))
            y_text = max(y(u_von), y(u_bis)) + 3 if name == "S_H" else min(y(u_von), y(u_bis)) - 3
            c.create_text(xm + 5, y_text, text=f"{name} {wert:+.2f} V", anchor="nw" if name == "S_H" else "sw",
                          fill=farbe, font=schrift)
        if e["ueberspannung"]:
            c.create_line(xs1, y(s["u_b"]), xe0, y(s["u_b"]), fill=ROT, width=3, arrow="last")
            c.create_text((xs1 + xe0) / 2, y(s["u_b"]) - 4, text="zu hoch!", anchor="s", fill=ROT, font=fett)
