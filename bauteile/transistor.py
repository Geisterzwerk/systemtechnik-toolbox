"""
transistor.py  –  Etappe 3: Bipolartransistor (NPN) als Schalter

AUFBAU
    1. Rechenfunktionen (ohne GUI, einzeln testbar)
    2. create(parent)   (Seite aus responsive.py-Bausteinen)

Vereinfachtes Modell (reicht für Schalteranwendungen und die Prüfung):
    U_BE ≈ 0.7 V   wenn der Transistor leitet
    U_CE,sat ≈ 0.2 V   wenn er voll durchgeschaltet (gesättigt) ist
    I_C = B · I_B   nur im aktiven Bereich (B = Stromverstärkung, auch β / hFE)
"""

import customtkinter as ctk

from gui.responsive import (ScrollPage, Card, ResponsiveGrid, ResponsiveCanvas,
                            InfoText, WrapLabel, form_row, FONT,
                            Table, Callout, SeeAlso)
from bauteile.dioden import naechster_e12

U_BE = 0.7
U_CE_SAT = 0.2


# =============================================================================
# 1) RECHENFUNKTIONEN
# =============================================================================
def schalter_dimensionieren(u_b, r_last, u_steuer, b_min, ue_faktor=3):
    """Basiswiderstand für einen NPN-Schalter berechnen.

    I_C   = (UB − U_CE,sat) / R_Last        Strom durch die Last
    I_B   = ü · I_C / B_min                 ü = Übersteuerungsfaktor (2…5)
    R_B   = (U_Steuer − U_BE) / I_B         -> auf E12 ABrunden (mehr Basisstrom = sicherer)
    P_T   = U_CE,sat · I_C                  Verlustleistung im Transistor
    """
    if u_steuer <= U_BE:
        raise ValueError("Steuerspannung muss > 0.7 V sein")
    i_c = (u_b - U_CE_SAT) / r_last
    i_b = ue_faktor * i_c / b_min
    r_b = (u_steuer - U_BE) / i_b
    r_b_e12 = naechster_e12(r_b, aufrunden=False)
    p_t = U_CE_SAT * i_c
    return i_c, i_b, r_b, r_b_e12, p_t


def arbeitspunkt(u_b, r_last, u_steuer, r_b, b):
    """Zustand des Transistors bestimmen.
    Rückgabe: (zustand, I_B, I_C, U_CE, P_T)
        "gesperrt"  : U_Steuer < 0.7 V -> kein Strom
        "aktiv"     : I_C = B · I_B, Transistor wirkt wie ein Stromregler (wird warm!)
        "gesättigt" : B · I_B wäre grösser als die Last erlaubt -> voll durchgeschaltet
    """
    if u_steuer <= U_BE:
        return "gesperrt", 0.0, 0.0, u_b, 0.0
    i_b = (u_steuer - U_BE) / r_b
    i_c_max = (u_b - U_CE_SAT) / r_last          # mehr lässt die Last nicht zu
    i_c = b * i_b
    if i_c >= i_c_max:
        return "gesättigt", i_b, i_c_max, U_CE_SAT, U_CE_SAT * i_c_max
    u_ce = u_b - i_c * r_last
    return "aktiv", i_b, i_c, u_ce, u_ce * i_c


# =============================================================================
# 2) GUI
# =============================================================================
def _z(entry):
    t = entry.get().strip().replace(",", ".")
    return float(t) if t else None


def _si(wert, einheit):
    for f, p in ((1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ")):
        if abs(wert) >= f:
            return f"{wert / f:.3g} {p}{einheit}"
    return f"{wert:.3g} {einheit}"


ZUSTAND_FARBE = {"gesperrt": "#6b7280", "aktiv": "#f59e0b", "gesättigt": "#22c55e"}


def create(parent):
    page = ScrollPage(parent, title="Transistor (NPN)",
                      subtitle="Bipolartransistor als Schalter – dimensionieren und live ausprobieren")

    # --- Interaktiver Simulator (volle Breite) ------------------------------
    sim = page.add(Card(page.body, title="Simulator: Transistor schaltet eine Lampe",
                        subtitle="Steuerspannung mit dem Slider verändern und beobachten, was passiert"))
    werte = {"ub": 12.0, "rl": 120.0, "rb": 2200.0, "b": 100.0, "ue": 0.0}

    def zeichne(c, w, h):
        zustand, i_b, i_c, u_ce, p_t = arbeitspunkt(werte["ub"], werte["rl"], werte["ue"],
                                                    werte["rb"], werte["b"])
        hell = i_c / ((werte["ub"] - U_CE_SAT) / werte["rl"])    # 0…1
        linie, lw = "gray70", 2
        tx, ty = 0.42 * w, 0.62 * h                                 # Transistor-Mitte
        r = 0.07 * h + 0.03 * w

        # Versorgung oben
        c.create_line(0.2 * w, 0.08 * h, 0.8 * w, 0.08 * h, fill="#ef4444", width=lw)
        c.create_text(0.2 * w, 0.04 * h, text=f"+UB = {werte['ub']:.0f} V", fill="#ef4444",
                      anchor="w", font=(FONT, 10, "bold"))
        # Lampe (Last)
        lx, ly = tx + r * 0.6, 0.27 * h
        glow = int(40 + 215 * hell)
        farbe = f"#{glow:02x}{int(glow * 0.85):02x}{int(20 + 40 * hell):02x}"
        if hell > 0.05:
            c.create_oval(lx - 34, ly - 34, lx + 34, ly + 34, fill=farbe, outline="")
        c.create_line(lx, 0.08 * h, lx, ly - 18, fill=linie, width=lw)
        c.create_oval(lx - 18, ly - 18, lx + 18, ly + 18, outline=linie, width=lw, fill=farbe if hell > 0.05 else "")
        c.create_line(lx - 12, ly - 12, lx + 12, ly + 12, fill=linie, width=lw)
        c.create_line(lx - 12, ly + 12, lx + 12, ly - 12, fill=linie, width=lw)
        c.create_text(lx + 26, ly, text=f"Last {werte['rl']:.0f} Ω", fill=linie, anchor="w", font=(FONT, 9))
        # Kollektor-Leitung
        c.create_line(lx, ly + 18, lx, ty - r * 0.55, fill=linie, width=lw)
        # Transistor-Symbol
        c.create_oval(tx - r, ty - r, tx + r, ty + r, outline=ZUSTAND_FARBE[zustand], width=3)
        c.create_line(tx - r * 0.3, ty - r * 0.5, tx - r * 0.3, ty + r * 0.5, fill=linie, width=4)
        c.create_line(tx - r * 0.3, ty - r * 0.2, lx, ty - r * 0.55, fill=linie, width=lw)
        c.create_line(tx - r * 0.3, ty + r * 0.2, lx, ty + r * 0.55, fill=linie, width=lw, arrow="last")
        # Emitter -> Masse
        c.create_line(lx, ty + r * 0.55, lx, 0.93 * h, fill=linie, width=lw)
        c.create_line(0.2 * w, 0.93 * h, 0.8 * w, 0.93 * h, fill="#60a5fa", width=lw)
        c.create_text(0.2 * w, 0.97 * h, text="GND", fill="#60a5fa", anchor="w", font=(FONT, 9))
        # Basis-Leitung mit RB
        bx = 0.12 * w
        c.create_line(bx, ty, tx - r * 0.3, ty, fill=linie, width=lw)
        c.create_rectangle(0.2 * w, ty - 8, 0.3 * w, ty + 8, outline=linie, width=lw, fill="gray20")
        c.create_text(0.25 * w, ty - 18, text=f"RB {_si(werte['rb'], 'Ω')}", fill=linie, font=(FONT, 9))
        # Basisstrom-Pfeil (Dicke ~ Strom)
        if i_b > 0:
            c.create_line(0.31 * w, ty + 16, tx - r * 0.45, ty + 16, fill="#a78bfa",
                          width=min(6, 1 + i_b * 2000), arrow="last")
        c.create_text(bx, ty - 18, text=f"U Steuer\n{werte['ue']:.2f} V", fill="#a78bfa", font=(FONT, 9, "bold"))
        # Messwerte rechts
        mx = 0.72 * w
        zeilen = [(f"Zustand: {zustand.upper()}", ZUSTAND_FARBE[zustand]),
                  (f"I B  = {_si(i_b, 'A')}", "gray80"),
                  (f"I C  = {_si(i_c, 'A')}", "gray80"),
                  (f"U CE = {u_ce:.2f} V", "gray80"),
                  (f"P T  = {_si(p_t, 'W')}", "#ef4444" if p_t > 0.5 else "gray80")]
        for k, (txt, col) in enumerate(zeilen):
            c.create_text(mx, 0.3 * h + k * 0.09 * h, text=txt, fill=col, anchor="w",
                          font=(FONT, 11, "bold" if k == 0 else "normal"))
        if zustand == "aktiv":
            c.create_text(mx, 0.3 * h + 5 * 0.09 * h, text="⚠ Transistor heizt!\n(halb offen)",
                          fill="#f59e0b", anchor="nw", font=(FONT, 9))

    canvas = ResponsiveCanvas(sim.body, zeichne, width=840, height=360)
    canvas.grid(row=0, column=0, columnspan=4, sticky="w")

    ue_label = ctk.CTkLabel(sim.body, text="0.00 V", width=60, anchor="w")

    def slider_bewegt(v):
        werte["ue"] = float(v)
        ue_label.configure(text=f"{float(v):.2f} V")
        canvas.redraw()

    ctk.CTkLabel(sim.body, text="U Steuer", anchor="w").grid(row=1, column=0, sticky="w", pady=(10, 4))
    slider = ctk.CTkSlider(sim.body, from_=0, to=5, number_of_steps=250, command=slider_bewegt)
    slider.set(0)
    slider.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=(10, 4))
    ue_label.grid(row=1, column=3, sticky="w", pady=(10, 4))

    # Parameter des Simulators
    param = ctk.CTkFrame(sim.body, fg_color="transparent")
    param.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 0))
    felder = {}
    for k, (key, text) in enumerate([("ub", "UB (V)"), ("rl", "R Last (Ω)"),
                                     ("rb", "RB (Ω)"), ("b", "B (hFE)")]):
        ctk.CTkLabel(param, text=text).grid(row=0, column=2 * k, padx=(0 if k == 0 else 12, 4))
        e = ctk.CTkEntry(param, width=70)
        e.insert(0, f"{werte[key]:g}")
        e.grid(row=0, column=2 * k + 1)
        e.bind("<Return>", lambda _e: uebernehmen())
        felder[key] = e

    def uebernehmen():
        try:
            for key, e in felder.items():
                v = _z(e)
                if v and v > 0:
                    werte[key] = v
            canvas.redraw()
        except ValueError:
            pass

    ctk.CTkButton(param, text="Übernehmen", width=100, command=uebernehmen) \
        .grid(row=0, column=8, padx=(12, 0))
    sim.body.grid_columnconfigure(1, weight=1)

    # --- Rechner -----------------------------------------------------------------
    grid = page.add(ResponsiveGrid(page.body, min_col_width=360, max_cols=2))

    dim = grid.add(Card(grid, title="Schalter dimensionieren",
                        subtitle="Basiswiderstand RB mit Übersteuerung berechnen"))
    d_ub, _ = form_row(dim.body, 0, "UB (V)", "z.B. 12")
    d_rl, _ = form_row(dim.body, 1, "R Last (Ω)", "z.B. 120")
    d_us, _ = form_row(dim.body, 2, "U Steuer (V)", "z.B. 3.3 (µC-Pin)")
    d_b, _ = form_row(dim.body, 3, "B min", "Datenblatt, z.B. 100")
    d_ue, _ = form_row(dim.body, 4, "ü (2…5)", "z.B. 3")
    d_res = WrapLabel(dim.body, text="", font=(FONT, 13, "bold"))

    def calc_dim():
        try:
            ue = _z(d_ue) or 3
            i_c, i_b, r_b, r_e12, p_t = schalter_dimensionieren(_z(d_ub), _z(d_rl), _z(d_us), _z(d_b), ue)
            d_res.configure(text=f"I C = {_si(i_c, 'A')}\n"
                                 f"I B = {_si(i_b, 'A')}   (ü = {ue:g})\n"
                                 f"RB = {_si(r_b, 'Ω')}  →  E12: {_si(r_e12, 'Ω')}\n"
                                 f"P Transistor ≈ {_si(p_t, 'W')}")
        except (TypeError, ValueError, ZeroDivisionError) as f:
            d_res.configure(text=f"Ungültige Eingabe ({f})" if str(f) else "Ungültige Eingabe")

    ctk.CTkButton(dim.body, text="Berechnen", command=calc_dim) \
        .grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 4))
    d_res.grid(row=6, column=0, columnspan=4, sticky="ew")

    ap = grid.add(Card(grid, title="Arbeitspunkt prüfen",
                       subtitle="Ist der Transistor gesperrt, aktiv oder gesättigt?"))
    a_ub, _ = form_row(ap.body, 0, "UB (V)", "z.B. 12")
    a_rl, _ = form_row(ap.body, 1, "R Last (Ω)", "z.B. 120")
    a_us, _ = form_row(ap.body, 2, "U Steuer (V)", "z.B. 5")
    a_rb, _ = form_row(ap.body, 3, "RB (Ω)", "z.B. 4700")
    a_b, _ = form_row(ap.body, 4, "B", "z.B. 100")
    a_res = WrapLabel(ap.body, text="", font=(FONT, 13, "bold"))

    def calc_ap():
        try:
            z, i_b, i_c, u_ce, p_t = arbeitspunkt(_z(a_ub), _z(a_rl), _z(a_us), _z(a_rb), _z(a_b))
            hinweis = {"gesperrt": "Aus – kein Strom",
                       "aktiv": "⚠ Nur halb offen: RB verkleinern!",
                       "gesättigt": "✅ Voll durchgeschaltet"}[z]
            a_res.configure(text=f"Zustand: {z.upper()} – {hinweis}\n"
                                 f"I B = {_si(i_b, 'A')},  I C = {_si(i_c, 'A')}\n"
                                 f"U CE = {u_ce:.2f} V,  P T = {_si(p_t, 'W')}",
                            text_color=ZUSTAND_FARBE[z])
        except (TypeError, ValueError, ZeroDivisionError):
            a_res.configure(text="Ungültige Eingabe", text_color=("gray10", "gray90"))

    ctk.CTkButton(ap.body, text="Berechnen", command=calc_ap) \
        .grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 4))
    a_res.grid(row=6, column=0, columnspan=4, sticky="ew")

    # --- Wiki --------------------------------------------------------------------
    info = page.add(Card(page.body))
    InfoText(info.body, """
        ## Bipolartransistor – Grundlagen
        Ein Bipolartransistor hat drei Anschlüsse: **Basis (B)**, **Kollektor (C)** und **Emitter (E)**. Ein kleiner **Basisstrom** steuert einen grossen **Kollektorstrom**. Beim NPN zeigt der Pfeil am Emitter **nach aussen** ("**N**icht **P**feil **N**ach innen"), beim PNP nach innen.
        - **Stromverstärkung:** `B = I_C / I_B` (Datenblatt: hFE, typ. 50…500, stark streuend → immer **B min** verwenden)
        - **Basis-Emitter-Spannung:** `U_BE ≈ 0.7 V` (wie eine Si-Diode)
        - **Knotenregel:** `I_E = I_B + I_C`
        ## Die drei Zustände
        - **Gesperrt:** `U_BE < 0.7 V` → kein Strom, Schalter offen
        - **Aktiver Bereich:** `I_C = B · I_B` → Verstärker; als Schalter schlecht, weil `P = U_CE · I_C` hoch ist
        - **Sättigung:** Basisstrom grösser als nötig → `U_CE ≈ 0.2 V`, Schalter geschlossen, wenig Verlust
        ## Transistor als Schalter – Vorgehen
        - 1. Laststrom: `I_C = (U_B − U_CE,sat) / R_Last`
        - 2. Basisstrom mit Übersteuerung: `I_B = ü · I_C / B_min` (ü = 2…5)
        - 3. Basiswiderstand: `R_B = (U_Steuer − 0.7 V) / I_B` → nächsten **kleineren** E12-Wert wählen
        - 4. Grenzwerte prüfen: `I_C,max`, `U_CE0`, `P_tot` aus dem Datenblatt
        ## Grundschaltungen (Verstärker)
        - **Emitterschaltung:** Spannungs- und Stromverstärkung, invertiert → Standard-Verstärker
        - **Kollektorschaltung (Emitterfolger):** `U_A ≈ U_E − 0.7 V`, Verstärkung ≈ 1, hoher Eingangs-, kleiner Ausgangswiderstand → Impedanzwandler
        - **Basisschaltung:** hohe Grenzfrequenz → HF-Technik
        ## Praxis & Prüfung
        - Bei **induktiven Lasten** (Relais, Motor) **immer eine Freilaufdiode** parallel zur Last
        - Mikrocontroller-Pins liefern nur wenige mA → Transistor als Treiber
        - Für grosse Ströme besser ein **Logic-Level-MOSFET** (spannungsgesteuert, fast kein Steuerstrom)
        - Typische Kleinsignaltypen: **BC547** (NPN), **BC557** (PNP), **2N2222** (NPN)
        - Abgerundete Flanken beim schnellen Schalten: Sättigung → Ladungsspeicherung in der Basis. Abhilfe: nicht zu stark übersteuern, Speed-up-Kondensator parallel zu RB oder Basis-Emitter-Widerstand
    """).grid(row=0, column=0, sticky="ew")

    page.add(Table(page.body, "Die drei Zustände",
        ["Zustand", "Bedingung", "Verhalten"],
        [["Gesperrt", "U_BE < 0.7 V", "kein Strom, Schalter offen, U_CE = U_B"],
         ["Aktiv", "I_C = B · I_B < I_C,max", "Verstärker; als Schalter schlecht → wird heiss"],
         ["Gesättigt", "B · I_B > I_C,max", "voll durchgeschaltet, U_CE ≈ 0.2 V, wenig Verlust"]]))

    page.add(Table(page.body, "Grundschaltungen",
        ["Schaltung", "Verstärkung", "Typischer Einsatz"],
        [["Emitterschaltung", "Spannung + Strom gross, invertiert", "Standard-Verstärker, Schalter"],
         ["Kollektorschaltung", "Spannung ≈ 1, Strom gross", "Impedanzwandler (Emitterfolger)"],
         ["Basisschaltung", "Spannung gross, Strom ≈ 1", "HF-Verstärker"]]))

    page.add(Table(page.body, "Typische Kleinsignal-Transistoren",
        ["Typ", "Daten", "Bemerkung"],
        [["BC547 (NPN)", "I_C 100 mA, U_CE0 45 V, B 110…800", "Standard für Schalter & Verstärker"],
         ["BC557 (PNP)", "I_C 100 mA, U_CE0 45 V", "Gegenstück zum BC547"],
         ["2N2222 (NPN)", "I_C 600 mA, U_CE0 40 V", "etwas mehr Strom"],
         ["BD139 (NPN)", "I_C 1.5 A, U_CE0 80 V", "Leistung, mit Kühlkörper"],
         ["IRLZ44N (MOSFET)", "Logic-Level, sehr kleiner R_DS(on)", "grosse Ströme direkt vom µC"]],
        note="Richtwerte. B streut stark – für Rechnungen immer B min aus dem Datenblatt."))

    page.add(Callout(page.body, "tipp", "Kniffe & Praxis", [
        "Als Schalter immer mit Übersteuerung **ü = 2 … 5** rechnen → sicher gesättigt.",
        "R_B auf den nächst **kleineren** Normwert runden (mehr Basisstrom).",
        "Pull-down (z.B. `10 kΩ`) Basis → Emitter: Transistor sperrt sicher, wenn der µC-Pin noch offen ist.",
        "Last immer auf der **Kollektorseite** (Low-Side-Schalter), Emitter direkt an GND.",
        "Langsame Ausschaltflanke? Zu stark übersteuert → Speed-up-Kondensator parallel zu R_B.",
        "Ab ca. 0.5 A oder hoher Schaltfrequenz: Logic-Level-MOSFET statt Bipolartransistor.",
    ]))

    page.add(Callout(page.body, "fehler", "Häufige Fehler", [
        "Basis ohne Widerstand direkt an 5 V → Basis-Emitter-Strecke brennt durch.",
        "Mit typischem statt minimalem B gerechnet → Transistor bleibt im aktiven Bereich und wird heiss.",
        "Freilaufdiode bei Relais / Motor vergessen → Spannungsspitze zerstört den Transistor.",
        "NPN auf der High-Side eingesetzt → U_E folgt der Basis, Transistor schaltet nicht voll durch.",
        "Pinbelegung (E-B-C) nicht im Datenblatt geprüft – je nach Typ unterschiedlich.",
    ]))

    page.add(SeeAlso(page.body, parent, [("Diode", "dioden"), ("Relais", "relais"),
                                         ("Widerstand", "widerstand"), ("Spule", "spule")]))
