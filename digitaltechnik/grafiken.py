# =============================================================================
# digitaltechnik/grafiken.py
# -----------------------------------------------------------------------------
# INTERAKTIVE WERKZEUGE der Digitaltechnik (Grundlagen):
#
#   ZahlensystemKarte      Zahl eintippen ODER Bits anklicken -> Dez/Bin/Hex/Okt/BCD/Gray/ASCII
#   ZweierkomplementKarte  Zahlenkreis (4 / 8 Bit), a + b mit Carry- und Overflow-Flag
#   BitmaskenKarte         Register + Maske anklicken, AND / OR / XOR / NOT / Schieben, C-Ausdruck
#   LogikpegelKarte        Sender- und Empfängerfamilie wählen -> Pegelbänder und Störabstände
#
#   BitLeiste              Baustein: Reihe von Bit-Knöpfen (Bit n-1 … 0) mit Wertigkeiten
#
# Rechnung: digitaltechnik/zahlen_mathe.py, digitaltechnik/pegel_mathe.py
# WER RUFT DAS AUF?  digitaltechnik/rechner.py (Registrierung, z.B. "werkzeug_zahlensystem")
# Eigene Namen beginnen mit dg_ (keine Kollision mit tkinter).
# =============================================================================

import math

import customtkinter as ctk

import config                                                          # -> config.py
from bauteile.grafiken.schaltplan import OK, WARN                      # -> bauteile/grafiken/schaltplan.py
from bauteile.rechner.basis import Auswahl, WertRegler                 # -> bauteile/rechner/basis.py
from core.layout import Karte, ResponsiveCanvas, WrapLabel             # -> core/layout.py
from digitaltechnik import pegel_mathe as pm                           # -> digitaltechnik/pegel_mathe.py
from digitaltechnik import zahlen_mathe as zm                          # -> digitaltechnik/zahlen_mathe.py

FEHLER = ("#B91C1C", "#EF4444")
ORANGE = "#F59E0B"
BLAU, ROT, GRUEN, GELB = "#3B82F6", "#EF4444", "#22C55E", "#EAB308"


def _farbe(paar):
    return paar[1] if ctk.get_appearance_mode() == "Dark" else paar[0]


def _ergebnis_label(master):
    return WrapLabel(master, text="", font=(config.SCHRIFT_CODE, 13, "bold"), text_color=config.FARBEN["akzent"],
                     justify="left", anchor="w")


def _erklaerung(master, text):
    return WrapLabel(master, text=text, font=config.FONT_KLEIN, text_color=config.FARBEN["text_leise"])


# =============================================================================
# BAUSTEIN: BIT-LEISTE
# =============================================================================
class BitLeiste(ctk.CTkFrame):
    """
    [ 128  64  32  16   8   4   2   1 ]   <- Wertigkeit (bei signed: MSB = −128)
    [  1   0   1   0   0   1   0   1 ]   <- Knöpfe (klickbar oder nur Anzeige)
    bits ≤ 16 in einer Reihe, sonst in Reihen zu 16.
    bei_klick(nummer) wird mit der Bitnummer (0 = LSB) aufgerufen.
    """

    def __init__(self, master, bits, bei_klick=None, signed=False, titel=""):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self.dg_knoepfe = {}
        self.dg_bits = bits
        pro_reihe = min(bits, 16)
        if titel:
            ctk.CTkLabel(self, text=titel, font=config.FONT_KLEIN, anchor="w", width=90).grid(
                row=0, column=0, rowspan=2, sticky="w", padx=(0, 6))
        for index, nummer in enumerate(range(bits - 1, -1, -1)):
            reihe, spalte = divmod(index, pro_reihe)
            spalte += 1                                                      # Spalte 0 = Titel
            gewicht = -(2 ** nummer) if (signed and nummer == bits - 1) else 2 ** nummer
            text = f"{gewicht}" if abs(gewicht) < 10000 else f"2^{nummer}"
            ctk.CTkLabel(self, text=text, font=(config.SCHRIFT, 9), text_color=config.FARBEN["text_leise"],
                         width=32).grid(row=reihe * 2, column=spalte, padx=(4 if nummer % 4 == 3 else 1, 1))
            knopf = ctk.CTkButton(self, text="0", width=32, height=30, font=(config.SCHRIFT_CODE, 14, "bold"),
                                  command=(lambda n=nummer: bei_klick(n)) if bei_klick else None,
                                  state="normal" if bei_klick else "disabled")
            knopf.grid(row=reihe * 2 + 1, column=spalte, padx=(4 if nummer % 4 == 3 else 1, 1), pady=(0, 4))
            self.dg_knoepfe[nummer] = knopf

    def zeigen(self, muster, markiert=0):
        """Bits anzeigen; 'markiert' = Bits, die orange hervorgehoben werden (z.B. geändert)."""
        for nummer, knopf in self.dg_knoepfe.items():
            gesetzt = (muster >> nummer) & 1
            if (markiert >> nummer) & 1:
                farbe = ORANGE
            else:
                farbe = config.FARBEN["akzent"] if gesetzt else config.FARBEN["rahmen"]
            knopf.configure(text=str(gesetzt), fg_color=farbe,
                            text_color=("#FFFFFF", "#FFFFFF") if gesetzt or (markiert >> nummer) & 1
                            else config.FARBEN["text_leise"],
                            text_color_disabled=("#FFFFFF", "#FFFFFF") if gesetzt else config.FARBEN["text_leise"])


# =============================================================================
# ZAHLENSYSTEME
# =============================================================================
class ZahlensystemKarte(Karte):
    BREITEN = ["8 Bit", "16 Bit", "32 Bit"]

    def __init__(self, master):
        super().__init__(master, titel="🔢 Zahlensysteme umrechnen (interaktiv)",
                         untertitel="Zahl eintippen + Enter – oder einzelne Bits anklicken")
        b = self.body
        self.dg_muster, self.dg_leiste = 200, None
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        self.dg_feld = ctk.CTkEntry(oben, width=200, font=(config.SCHRIFT_CODE, 14))
        self.dg_feld.grid(row=0, column=0, padx=(0, 8), pady=2)
        self.dg_feld.insert(0, "200")
        self.dg_feld.bind("<Return>", lambda _e: self._dg_eingabe())
        self.dg_basis = Auswahl(oben, list(zm.BASEN), "Dezimal", breite=140, bei_aenderung=self._dg_basis_neu)
        self.dg_basis.grid(row=0, column=1, padx=(0, 8), pady=2)
        self.dg_breite = ctk.CTkSegmentedButton(oben, values=self.BREITEN, command=lambda _v: self._dg_breite_neu())
        self.dg_breite.set(self.BREITEN[0])
        self.dg_breite.grid(row=0, column=2, pady=2)
        self.dg_leisten_rahmen = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        self.dg_leisten_rahmen.grid(row=1, column=0, sticky="w", pady=(10, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Dieselbe Zahl in verschiedenen Schreibweisen. Jedes Bit hat die "
                       "Wertigkeit 2^n (Bit 0 rechts = 1). Eine Hex-Ziffer fasst genau 4 Bit zusammen, eine "
                       "Oktalziffer 3 Bit. BCD speichert jede Dezimalziffer einzeln in 4 Bit (Anzeigen, Uhren-ICs), "
                       "der Gray-Code ändert von Zahl zu Zahl nur EIN Bit (Drehgeber). Ob ein Bitmuster eine "
                       "positive oder negative Zahl ist, steht nicht im Muster – das legt der Datentyp fest "
                       "(unsigned / signed).").grid(row=3, column=0, sticky="ew", pady=(8, 0))
        self._dg_breite_neu()

    def _dg_bits(self):
        return int(self.dg_breite.get().split()[0])

    def _dg_breite_neu(self):
        for kind in self.dg_leisten_rahmen.winfo_children():
            kind.destroy()
        bits = self._dg_bits()
        self.dg_muster &= 2 ** bits - 1
        self.dg_leiste = BitLeiste(self.dg_leisten_rahmen, bits, self._dg_klick)
        self.dg_leiste.grid(row=0, column=0, sticky="w")
        self._dg_anzeigen()

    def _dg_klick(self, nummer):
        self.dg_muster ^= 1 << nummer
        self._dg_feld_schreiben()
        self._dg_anzeigen()

    def _dg_basis_neu(self):
        self._dg_feld_schreiben()

    def _dg_feld_schreiben(self):
        basis = zm.BASEN[self.dg_basis.wert()]
        bits = self._dg_bits()
        text = {2: zm.binaer(self.dg_muster, bits), 16: f"{self.dg_muster:X}", 8: f"{self.dg_muster:o}",
                10: str(self.dg_muster)}[basis]
        self.dg_feld.delete(0, "end")
        self.dg_feld.insert(0, text)

    def _dg_eingabe(self):
        bits = self._dg_bits()
        try:
            wert = zm.einlesen(self.dg_feld.get(), zm.BASEN[self.dg_basis.wert()])
            if wert < 0:
                self.dg_muster = zm.zweierkomplement(wert, bits)["muster"]
            elif wert >= 2 ** bits:
                raise ValueError(f"{wert} passt nicht in {bits} Bit (max. {2 ** bits - 1}) – grössere Bitbreite wählen")
            else:
                self.dg_muster = wert
        except ValueError as fehler:
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN)
            return
        self._dg_anzeigen()

    def _dg_anzeigen(self):
        bits = self._dg_bits()
        e = zm.darstellungen(self.dg_muster, bits)
        self.dg_leiste.zeigen(self.dg_muster)
        zeilen = [f"Dezimal      {e['unsigned']}   (als signed: {e['signed']})",
                  f"Binär        {e['bin']}",
                  f"Hexadezimal  0x{e['hex']}        Oktal  0o{e['okt']}",
                  f"BCD          {e['bcd']}",
                  f"Gray-Code    {e['gray']}"]
        if e["ascii"]:
            zeilen.append(f"ASCII        '{e['ascii']}'")
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])


# =============================================================================
# ZWEIERKOMPLEMENT MIT ZAHLENKREIS
# =============================================================================
class ZweierkomplementKarte(Karte):
    BREITEN = ["4 Bit", "8 Bit"]

    def __init__(self, master):
        super().__init__(master, titel="🔄 Zweierkomplement und Überlauf (interaktiv)",
                         untertitel="Zahlenkreis: a einstellen, b dazuzählen – wann stimmt das Ergebnis nicht mehr?")
        b = self.body
        self.dg_regler = {}
        self.dg_breite = ctk.CTkSegmentedButton(b, values=self.BREITEN, command=lambda _v: self._dg_breite_neu())
        self.dg_breite.set(self.BREITEN[0])
        self.dg_breite.grid(row=0, column=0, sticky="w")
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.55, max_hoehe=420)
        self.dg_canvas.grid(row=1, column=0, sticky="ew", pady=(6, 4))
        for zeile, (name, text, start) in enumerate((("a", "a", 5), ("b", "b (dazuzählen)", 4)), start=2):
            regler = WertRegler(b, text, "zahl", -8, 15, start, ganzzahl=True, bei_aenderung=self._dg_neu,
                                text_breite=130)
            regler.grid(row=zeile, column=0, sticky="ew")
            self.dg_regler[name] = regler
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Mit n Bit gibt es 2^n Muster – im Kreis angeordnet. Aussen steht die "
                       "Deutung als unsigned (0 … 2^n − 1), innen als signed im Zweierkomplement (−2^(n−1) … "
                       "2^(n−1) − 1): Das MSB zählt negativ. Addieren heisst im Kreis weiterdrehen. Über die "
                       "ORANGE Grenze (1111 → 0000) gibt es einen Übertrag C – falsch, wenn man unsigned rechnet. "
                       "Über die ROTE Grenze (0111 → 1000) springt das Vorzeichen: Overflow V – falsch, wenn man "
                       "signed rechnet. Negativ machen: alle Bits invertieren und 1 addieren."
                  ).grid(row=5, column=0, sticky="ew", pady=(8, 0))
        self.dg_e = None
        self._dg_breite_neu()

    def _dg_bits(self):
        return int(self.dg_breite.get().split()[0])

    def _dg_breite_neu(self):
        bits = self._dg_bits()
        tief, hoch = -(2 ** (bits - 1)), 2 ** bits - 1           # signed ODER unsigned erlaubt
        for regler in self.dg_regler.values():
            regler.bereich_setzen(tief, hoch)
        self._dg_neu()

    def _dg_neu(self):
        if len(self.dg_regler) < 2:
            return
        bits = self._dg_bits()
        a, b = round(self.dg_regler["a"].wert()), round(self.dg_regler["b"].wert())
        try:
            self.dg_e = zm.addieren(a, b, bits)
        except ValueError as fehler:
            self.dg_e = None
            self.dg_ergebnis.configure(text=f"⚠ {fehler}", text_color=WARN)
            return
        e = self.dg_e
        sa, sb = zm.als_vorzeichen(e["muster_a"], bits), zm.als_vorzeichen(e["muster_b"], bits)
        ua, ub = e["muster_a"], e["muster_b"]
        zeilen = [f"  a = {e['bin_a']}   unsigned {ua:>4}   signed {sa:>4}",
                  f"+ b = {e['bin_b']}   unsigned {ub:>4}   signed {sb:>4}",
                  f"  = {'1 ' if e['carry'] else '  '}{e['bin_summe']}   unsigned {e['unsigned']:>4}   signed {e['signed']:>4}",
                  f"C (Carry) = {int(e['carry'])}  → unsigned " + (f"FALSCH (richtig wäre {ua + ub})" if e["carry"] else "stimmt"),
                  f"V (Overflow) = {int(e['overflow'])}  → signed " + (f"FALSCH (richtig wäre {sa + sb})" if e["overflow"] else "stimmt")]
        if a < 0:
            z = zm.zweierkomplement(a, bits)
            zeilen.append(f"−{-a}:  {z['betrag']}  → invertiert {z['invertiert']}  → +1 = {z['plus_eins']}")
        farbe = WARN if (e["carry"] or e["overflow"]) else OK
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=farbe)
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        if self.dg_e is None:
            return
        bits = self._dg_bits()
        n = 2 ** bits
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        linie = _farbe(config.FARBEN["rahmen"])
        mx, my = w * 0.36, h * 0.5
        aussen = 1.68 if bits == 4 else 1.28                 # äusserste Beschriftung in Vielfachen von r
        r = min(w * 0.27, (h * 0.5 - 10) / aussen)
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
        schritt = 1 if bits == 4 else 16
        for k in range(0, n, schritt):
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
        e = self.dg_e
        # Bogen von a bis Summe (b Schritte im Uhrzeigersinn, mod n)
        schritte = e["muster_b"]
        punkte = []
        for t in range(41):
            punkte += punkt(e["muster_a"] + schritte * t / 40, r * 0.62)
        if schritte:
            c.create_line(*punkte, fill=ORANGE if e["carry"] else GRUEN, width=3, arrow="last",
                          arrowshape=(10, 12, 4))
        for k, farbe, name in ((e["muster_a"], BLAU, "a"), (e["summe"], ROT if e["overflow"] or e["carry"] else GRUEN, "a+b")):
            x, y = punkt(k, r)
            c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=farbe, outline="")
        # Legende rechts
        lx, ly = w * 0.72, h * 0.18
        for i, (farbe, t) in enumerate(((leise, "aussen: unsigned"), (BLAU, "innen: signed"),
                                         (ORANGE, "Grenze für C (unsigned)"), (ROT, "Grenze für V (signed)"))):
            c.create_line(lx, ly + i * h * 0.1, lx + 18, ly + i * h * 0.1, fill=farbe, width=4)
            c.create_text(lx + 24, ly + i * h * 0.1, text=t, anchor="w", fill=text, font=klein)


# =============================================================================
# BITMASKEN
# =============================================================================
class BitmaskenKarte(Karte):
    KURZ = ["AND", "OR", "AND NOT", "XOR", "NOT", "<<", ">>"]

    def __init__(self, master):
        super().__init__(master, titel="🎭 Bitmasken: Bits setzen, löschen, umschalten, prüfen (interaktiv)",
                         untertitel="Register x und Maske anklicken, Operation wählen")
        b = self.body
        self.dg_x, self.dg_m = 0b10100101, 0b00001000
        self.dg_op = ctk.CTkSegmentedButton(b, values=self.KURZ, command=lambda _v: self._dg_neu())
        self.dg_op.set("OR")
        self.dg_op.grid(row=0, column=0, sticky="w")
        self.dg_x_leiste = BitLeiste(b, 8, lambda n: self._dg_klick("x", n), titel="Register x")
        self.dg_x_leiste.grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.dg_m_leiste = BitLeiste(b, 8, lambda n: self._dg_klick("m", n), titel="Maske")
        self.dg_m_leiste.grid(row=2, column=0, sticky="w")
        self.dg_e_leiste = BitLeiste(b, 8, None, titel="Ergebnis")
        self.dg_e_leiste.grid(row=3, column=0, sticky="w")
        self.dg_schieben = WertRegler(b, "Schieben um", "zahl", 0, 7, 1, ganzzahl=True, bei_aenderung=self._dg_neu,
                                      text_breite=130)
        self.dg_schieben.grid(row=4, column=0, sticky="ew", pady=(6, 0))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=5, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  In Mikrocontroller-Registern steuert jedes Bit etwas anderes (Pin, "
                       "Interrupt, Takt). Mit einer Maske ändert man nur die gewünschten Bits: OR setzt, AND NOT "
                       "löscht, XOR schaltet um, AND prüft (Ergebnis ≠ 0 → Bit gesetzt). Schieben um n Stellen "
                       "multipliziert bzw. teilt durch 2^n – herausgeschobene Bits gehen verloren. Orange = Bits, "
                       "die sich gegenüber x geändert haben. Masken schreibt man meist als (1 << n)."
                  ).grid(row=6, column=0, sticky="ew", pady=(8, 0))
        self._dg_neu()

    def _dg_klick(self, wer, nummer):
        if wer == "x":
            self.dg_x ^= 1 << nummer
        else:
            self.dg_m ^= 1 << nummer
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        op = zm.OPERATIONEN[self.KURZ.index(self.dg_op.get())]
        schritte = round(self.dg_schieben.wert())
        e = zm.bitoperation(self.dg_x, self.dg_m, op, 8, schritte)
        self.dg_x_leiste.zeigen(self.dg_x)
        self.dg_m_leiste.zeigen(self.dg_m)
        self.dg_e_leiste.zeigen(e["ergebnis"], e["geaendert"])
        bits_m = [n for n in range(8) if (self.dg_m >> n) & 1]
        maske_c = " | ".join(f"(1 << {n})" for n in reversed(bits_m)) or "0"
        zeilen = [f"x = 0x{self.dg_x:02X} = {zm.binaer(self.dg_x, 8)}     Maske = 0x{self.dg_m:02X} = {maske_c}",
                  f"C:  {e['c']}   →   0x{e['ergebnis']:02X} = {e['bin']}  ({e['ergebnis']})"]
        if self.dg_op.get() == "AND":
            zeilen.append("Prüfen: " + ("Ergebnis ≠ 0 → mindestens ein Bit der Maske ist gesetzt" if e["ergebnis"]
                                        else "Ergebnis = 0 → kein Bit der Maske ist gesetzt"))
        elif self.dg_op.get() in ("<<", ">>"):
            faktor = f"× {2 ** schritte}" if self.dg_op.get() == "<<" else f"÷ {2 ** schritte} (abgerundet)"
            zeilen.append(f"entspricht {faktor}" + (f"   ·   verlorene Bits: {e['verloren']:b}" if e["verloren"] else ""))
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=config.FARBEN["akzent"])


# =============================================================================
# LOGIKPEGEL
# =============================================================================
class LogikpegelKarte(Karte):

    def __init__(self, master):
        super().__init__(master, titel="📶 Logikpegel und Störabstand (interaktiv)",
                         untertitel="Passt ein Ausgang zu einem Eingang? Sender und Empfänger wählen")
        b = self.body
        oben = ctk.CTkFrame(b, fg_color="transparent", corner_radius=0)
        oben.grid(row=0, column=0, sticky="w")
        namen = list(pm.FAMILIEN)
        ctk.CTkLabel(oben, text="Sender (Ausgang)").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.dg_sender = Auswahl(oben, namen, "ESP32 (3.3 V)", breite=230, bei_aenderung=self._dg_neu)
        self.dg_sender.grid(row=0, column=1, pady=2)
        ctk.CTkLabel(oben, text="Empfänger (Eingang)").grid(row=1, column=0, sticky="w", padx=(0, 8))
        self.dg_empf = Auswahl(oben, namen, "74HC (5 V, Werte bei 4.5 V)", breite=230, bei_aenderung=self._dg_neu)
        self.dg_empf.grid(row=1, column=1, pady=2)
        self.dg_e = None
        self.dg_canvas = ResponsiveCanvas(b, self._dg_zeichnen, seitenverhaeltnis=0.5, max_hoehe=420)
        self.dg_canvas.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        self.dg_ergebnis = _ergebnis_label(b)
        self.dg_ergebnis.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        _erklaerung(b, "Was zeigt das Werkzeug?  Links garantiert der Ausgang: HIGH liegt mindestens bei U_OH, LOW "
                       "höchstens bei U_OL. Rechts erkennt der Eingang sicher HIGH ab U_IH und sicher LOW bis U_IL – "
                       "dazwischen ist der Zustand undefiniert. Der Störabstand ist die Reserve dazwischen: "
                       "S_H = U_OH − U_IH, S_L = U_IL − U_OL. Ist er negativ, wird der Pegel nicht sicher erkannt. "
                       "Liegt der Ausgang über der maximalen Eingangsspannung, leiten die Schutzdioden – "
                       "Pegelwandler nötig. Werte: garantierte Datenblatt-Grenzwerte.").grid(
            row=3, column=0, sticky="ew", pady=(8, 0))
        self._dg_neu()

    def _dg_neu(self):
        if not hasattr(self, "dg_ergebnis"):
            return
        self.dg_e = e = pm.kompatibel(self.dg_sender.wert(), self.dg_empf.wert())
        s, r = e["sender"], e["empfaenger"]
        zeilen = [f"Störabstand HIGH  S_H = U_OH − U_IH = {s['u_oh']:.2f} V − {r['u_ih']:.2f} V = {e['s_h']:+.2f} V",
                  f"Störabstand LOW   S_L = U_IL − U_OL = {r['u_il']:.2f} V − {s['u_ol']:.2f} V = {e['s_l']:+.2f} V",
                  f"Ausgang bis {s['u_b']:.1f} V, Eingang verträgt {r['u_e_max']:.1f} V",
                  ("✓ " if e["ok"] else "❌ ") + e["rat"]]
        self.dg_ergebnis.configure(text="\n".join(zeilen), text_color=OK if e["ok"] else FEHLER)
        w, h = self.dg_canvas.winfo_width(), self.dg_canvas.winfo_height()
        if w > 1:
            self.dg_canvas.delete("all")
            self._dg_zeichnen(self.dg_canvas, w, h)

    def _dg_zeichnen(self, c, w, h):
        e = self.dg_e
        if e is None:
            return
        s, r = e["sender"], e["empfaenger"]
        text, leise = _farbe(config.FARBEN["text"]), _farbe(config.FARBEN["text_leise"])
        u_top = max(s["u_b"], r["u_e_max"]) * 1.12
        oben, unten = h * 0.08, h * 0.9
        schrift = (config.SCHRIFT, max(8, int(h / 30)))
        fett = (config.SCHRIFT, max(8, int(h / 28)), "bold")

        def y(u):
            return unten - (unten - oben) * u / u_top

        def band(x0, x1, u0, u1, farbe, beschriftung):
            c.create_rectangle(x0, y(u1), x1, y(u0), fill=farbe, outline="", stipple="")
            if beschriftung and y(u0) - y(u1) > 14:
                c.create_text((x0 + x1) / 2, (y(u0) + y(u1)) / 2, text=beschriftung, fill="#FFFFFF", font=schrift)

        # Achse
        c.create_line(w * 0.08, y(0), w * 0.08, y(u_top), fill=leise)
        for u in [x / 2 for x in range(0, int(u_top * 2) + 1)]:
            c.create_line(w * 0.075, y(u), w * 0.08, y(u), fill=leise)
            if u == int(u):
                c.create_text(w * 0.07, y(u), text=f"{u:.0f} V", anchor="e", fill=leise, font=schrift)
        # Sender
        xs0, xs1 = w * 0.28, w * 0.42
        band(xs0, xs1, s["u_oh"], s["u_b"], "#15803D", "HIGH")
        band(xs0, xs1, 0, s["u_ol"], "#1D4ED8", "LOW")
        band(xs0, xs1, s["u_ol"], s["u_oh"], _farbe(("#D0D5DD", "#3A3F4A")), "")
        c.create_text((xs0 + xs1) / 2, oben - 2, text="Ausgang (Sender)", anchor="s", fill=text, font=fett)
        # Empfänger
        xe0, xe1 = w * 0.66, w * 0.80
        band(xe0, xe1, r["u_ih"], r["u_e_max"], "#15803D", "HIGH")
        band(xe0, xe1, 0, r["u_il"], "#1D4ED8", "LOW")
        band(xe0, xe1, r["u_il"], r["u_ih"], "#A16207", "undefiniert")
        if u_top > r["u_e_max"]:
            band(xe0, xe1, r["u_e_max"], u_top, "#B91C1C", "zu hoch")
        c.create_text((xe0 + xe1) / 2, oben - 2, text="Eingang (Empfänger)", anchor="s", fill=text, font=fett)
        # Grenzwerte beschriften
        for x, anker, werte in ((xs0 - 4, "e", (("U_OH", s["u_oh"]), ("U_OL", s["u_ol"]))),
                                (xe1 + 4, "w", (("U_IH", r["u_ih"]), ("U_IL", r["u_il"]), ("U_E,max", r["u_e_max"])))):
            for name, u in werte:
                c.create_text(x, y(u), text=f"{name} {u:.2f} V", anchor=anker, fill=text, font=schrift)
        # Störabstände als Pfeile zwischen den Säulen
        xm = xs1 + w * 0.04                                   # senkrechter Teil nahe beim Sender, Text rechts daneben
        for (u_von, u_bis, name, wert) in ((s["u_oh"], r["u_ih"], "S_H", e["s_h"]), (s["u_ol"], r["u_il"], "S_L", e["s_l"])):
            farbe = GRUEN if wert >= 0 else ROT
            c.create_line(xs1, y(u_von), xm, y(u_von), xm, y(u_bis), xe0, y(u_bis), fill=farbe, width=2, dash=(4, 3))
            # S_H unter die untere Linie, S_L über die obere -> die beiden Texte kommen sich nie in die Quere
            y_text = max(y(u_von), y(u_bis)) + 3 if name == "S_H" else min(y(u_von), y(u_bis)) - 3
            c.create_text(xm + 5, y_text, text=f"{name} {wert:+.2f} V", anchor="nw" if name == "S_H" else "sw",
                          fill=farbe, font=schrift)
        if e["ueberspannung"]:
            c.create_line(xs1, y(s["u_b"]), xe0, y(s["u_b"]), fill=ROT, width=3, arrow="last")
            c.create_text((xs1 + xe0) / 2, y(s["u_b"]) - 4, text="zu hoch!", anchor="s", fill=ROT, font=fett)
