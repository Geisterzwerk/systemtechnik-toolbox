"""
dioden.py  –  Etappe 3: Dioden (LED, Z-Diode, Gleichrichter, Kennlinie)

AUFBAU DIESER DATEI (gilt für alle Bauteilseiten)
    1. Rechenfunktionen  -> reine Mathematik, KEIN GUI-Code
                            (kann man einzeln testen: python -c "from bauteile.dioden import *; print(led_vorwiderstand(5, 2, 0.02))")
    2. create(parent)    -> baut die Seite aus den Bausteinen von responsive.py

    Warum getrennt? Rechnen und Anzeigen sind zwei verschiedene Aufgaben.
    C#-Vergleich: wie Logik-Klasse vs. Form/Window (Code-Behind).
"""

import math
import customtkinter as ctk

from gui.responsive import (ScrollPage, Card, ResponsiveGrid, ResponsiveCanvas,
                            InfoText, WrapLabel, form_row, FONT,
                            Table, Callout, SeeAlso)

# E12-Normreihe: reale Widerstände gibt es nur in diesen Stufen
E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]


# =============================================================================
# 1) RECHENFUNKTIONEN
# =============================================================================
def naechster_e12(r, aufrunden=True):
    """Nächster E12-Wert. Aufrunden = sichere Seite (Strom wird kleiner)."""
    dekade = 10 ** math.floor(math.log10(r))
    kandidaten = [w * dekade for w in E12] + [10 * dekade]
    if aufrunden:
        return min(w for w in kandidaten if w >= r - 1e-9)
    return max(w for w in kandidaten if w <= r + 1e-9)


def led_vorwiderstand(u_b, u_led, i_led):
    """R = (UB - U_LED) / I_LED  ->  (R_exakt, R_E12, I_mit_E12, P_R)"""
    if u_b <= u_led:
        raise ValueError("UB muss grösser als die LED-Spannung sein")
    r = (u_b - u_led) / i_led
    r_e12 = naechster_e12(r)
    i_real = (u_b - u_led) / r_e12
    p_r = (u_b - u_led) * i_real
    return r, r_e12, i_real, p_r


def z_diode_vorwiderstand(u_e_min, u_e_max, u_z, i_last_max, i_z_min, p_tot):
    """Z-Diode als Spannungsstabilisierung.

    R_V,max: bei kleinster Eingangsspannung + grösstem Laststrom muss noch
             I_Z,min durch die Z-Diode fliessen.
    Danach prüfen: bei grösster Eingangsspannung + Leerlauf fliesst ALLES
             durch die Z-Diode -> P_Z darf P_tot nicht überschreiten.
    """
    if u_e_min <= u_z:
        raise ValueError("UE,min muss grösser als UZ sein")
    r_max = (u_e_min - u_z) / (i_last_max + i_z_min)
    r_wahl = naechster_e12(r_max, aufrunden=False)       # abrunden -> genug Strom
    i_z_max = (u_e_max - u_z) / r_wahl                   # Leerlauf
    p_z = u_z * i_z_max
    p_r = (u_e_max - u_z) ** 2 / r_wahl
    return r_max, r_wahl, i_z_max, p_z, p_r, p_z <= p_tot


def gleichrichter(u_eff, art, u_f=0.7, i_last=None, c=None, f_netz=50):
    """Spitzenspannung nach dem Gleichrichter + Brummspannung mit Ladekondensator.

    art: "Einweg" (1 Diode im Strompfad, Brumm mit f)
         "Brücke" (2 Dioden im Strompfad, Brumm mit 2f)
    Näherung Brummspannung: U_Br,ss ≈ I / (f_Brumm · C)
    """
    u_spitze = u_eff * math.sqrt(2)
    n_dioden = 1 if art == "Einweg" else 2
    f_brumm = f_netz if art == "Einweg" else 2 * f_netz
    u_dc = u_spitze - n_dioden * u_f
    u_brumm = i_last / (f_brumm * c) if (i_last and c) else None
    return u_spitze, u_dc, f_brumm, u_brumm


def shockley(u, i_s=1e-12, n=1.8, u_t=0.02585):
    """Diodengleichung I = I_S · (e^(U / (n·U_T)) - 1)"""
    return i_s * (math.exp(u / (n * u_t)) - 1)


# =============================================================================
# 2) GUI
# =============================================================================
def _z(entry):
    """Eingabe -> float (Komma erlaubt). Leer -> None."""
    t = entry.get().strip().replace(",", ".")
    return float(t) if t else None


def _si(wert, einheit):
    """12000 -> '12 kΩ',  0.02 -> '20 mA'"""
    for faktor, praefix in ((1e6, "M"), (1e3, "k"), (1, ""), (1e-3, "m"), (1e-6, "µ")):
        if abs(wert) >= faktor:
            return f"{wert / faktor:.3g} {praefix}{einheit}"
    return f"{wert:.3g} {einheit}"


LED_FARBEN = {"Rot (≈1.8 V)": 1.8, "Gelb (≈2.1 V)": 2.1, "Grün (≈2.2 V)": 2.2,
              "Blau (≈3.0 V)": 3.0, "Weiss (≈3.2 V)": 3.2, "Infrarot (≈1.3 V)": 1.3}


def create(parent):
    page = ScrollPage(parent, title="Dioden",
                      subtitle="LED-Vorwiderstand, Z-Diode, Gleichrichter und Kennlinie")
    grid = page.add(ResponsiveGrid(page.body, min_col_width=360, max_cols=2))

    # --- LED-Vorwiderstand ---------------------------------------------------
    led = grid.add(Card(grid, title="LED-Vorwiderstand", subtitle="R = (UB − U_LED) / I_LED"))
    e_ub, _ = form_row(led.body, 0, "UB (V)", "z.B. 5")
    ctk.CTkLabel(led.body, text="LED", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
    farbe = ctk.CTkOptionMenu(led.body, values=list(LED_FARBEN), width=200)
    farbe.grid(row=1, column=1, sticky="w", pady=4)
    e_iled, _ = form_row(led.body, 2, "I (mA)", "z.B. 20")
    led_res = WrapLabel(led.body, text="", font=(FONT, 13, "bold"))

    def calc_led():
        try:
            r, r12, i, p = led_vorwiderstand(_z(e_ub), LED_FARBEN[farbe.get()], _z(e_iled) / 1000)
            led_res.configure(text=f"R exakt = {_si(r, 'Ω')}\n"
                                   f"Normwert E12 = {_si(r12, 'Ω')}  →  I = {_si(i, 'A')}\n"
                                   f"Verlustleistung R = {_si(p, 'W')}"
                                   + ("   ⚠ ≥ 0.25 W-Widerstand wählen" if p > 0.125 else ""))
        except (TypeError, ValueError, ZeroDivisionError) as fehler:
            led_res.configure(text=f"Ungültige Eingabe ({fehler})" if str(fehler) else "Ungültige Eingabe")

    ctk.CTkButton(led.body, text="Berechnen", command=calc_led) \
        .grid(row=3, column=0, columnspan=2, sticky="w", pady=(10, 4))
    led_res.grid(row=4, column=0, columnspan=4, sticky="ew")

    # --- Z-Diode -------------------------------------------------------------
    zd = grid.add(Card(grid, title="Z-Diode: Stabilisierung",
                       subtitle="Vorwiderstand bestimmen und Verlustleistung prüfen"))
    e_uemin, _ = form_row(zd.body, 0, "UE min (V)", "z.B. 11")
    e_uemax, _ = form_row(zd.body, 1, "UE max (V)", "z.B. 14")
    e_uz, _ = form_row(zd.body, 2, "UZ (V)", "z.B. 5.1")
    e_il, _ = form_row(zd.body, 3, "IL max (mA)", "z.B. 20")
    e_izmin, _ = form_row(zd.body, 4, "IZ min (mA)", "z.B. 5")
    e_ptot, _ = form_row(zd.body, 5, "Ptot (W)", "z.B. 0.5")
    zd_res = WrapLabel(zd.body, text="", font=(FONT, 13, "bold"))

    def calc_zd():
        try:
            r_max, r, iz, pz, pr, ok = z_diode_vorwiderstand(
                _z(e_uemin), _z(e_uemax), _z(e_uz),
                _z(e_il) / 1000, _z(e_izmin) / 1000, _z(e_ptot))
            zd_res.configure(text=f"RV max = {_si(r_max, 'Ω')}  →  gewählt E12: {_si(r, 'Ω')}\n"
                                  f"Leerlauf: IZ = {_si(iz, 'A')},  PZ = {_si(pz, 'W')}\n"
                                  f"Leistung RV = {_si(pr, 'W')}\n"
                                  + ("✅ Z-Diode hält das aus" if ok else "❌ PZ > Ptot – grössere Z-Diode wählen!"))
        except (TypeError, ValueError, ZeroDivisionError) as fehler:
            zd_res.configure(text=f"Ungültige Eingabe ({fehler})" if str(fehler) else "Ungültige Eingabe")

    ctk.CTkButton(zd.body, text="Berechnen", command=calc_zd) \
        .grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 4))
    zd_res.grid(row=7, column=0, columnspan=4, sticky="ew")

    # --- Gleichrichter -------------------------------------------------------
    gr = grid.add(Card(grid, title="Gleichrichter + Ladekondensator",
                       subtitle="Spitzenwert, DC-Spannung und Brummspannung"))
    e_ueff, _ = form_row(gr.body, 0, "U eff (V)", "z.B. 12")
    ctk.CTkLabel(gr.body, text="Schaltung", anchor="w").grid(row=1, column=0, sticky="w", pady=4)
    art = ctk.CTkSegmentedButton(gr.body, values=["Einweg", "Brücke"])
    art.set("Brücke")
    art.grid(row=1, column=1, sticky="w", pady=4)
    e_ilast, _ = form_row(gr.body, 2, "I Last (mA)", "optional, z.B. 100")
    e_c, unit_c = form_row(gr.body, 3, "C", "optional, z.B. 2200", unit_values=["µF", "mF"])
    gr_res = WrapLabel(gr.body, text="", font=(FONT, 13, "bold"))

    def calc_gr():
        try:
            i = _z(e_ilast) / 1000 if _z(e_ilast) else None
            c = _z(e_c) * (1e-6 if unit_c.get() == "µF" else 1e-3) if _z(e_c) else None
            us, udc, fb, ubr = gleichrichter(_z(e_ueff), art.get(), i_last=i, c=c)
            text = (f"Û = U eff · √2 = {us:.2f} V\n"
                    f"U DC (ohne Last) ≈ {udc:.2f} V   (f Brumm = {fb} Hz)")
            if ubr is not None:
                text += f"\nBrummspannung U Br,ss ≈ {ubr:.2f} V  →  U min ≈ {udc - ubr:.2f} V"
            gr_res.configure(text=text)
        except (TypeError, ValueError, ZeroDivisionError):
            gr_res.configure(text="Ungültige Eingabe")

    ctk.CTkButton(gr.body, text="Berechnen", command=calc_gr) \
        .grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 4))
    gr_res.grid(row=5, column=0, columnspan=4, sticky="ew")

    # --- Kennlinie (interaktiv) ----------------------------------------------
    kl = grid.add(Card(grid, title="Kennlinien-Vergleich",
                       subtitle="Durchlassbereich (rechts) und Z-Durchbruch (links)"))
    typen = {"Ge (0.3 V)": (0.3, "#a78bfa"), "Si (0.7 V)": (0.7, "#60a5fa"),
             "LED rot (1.8 V)": (1.8, "#ef4444"), "LED blau (3.0 V)": (3.0, "#3b82f6")}
    uz_slider_wert = [5.1]

    def zeichne_kennlinie(c, w, h):
        x0, y0 = 0.45 * w, 0.8 * h                       # Nullpunkt
        sx = (w - x0 - 15) / 3.5                         # Pixel pro Volt (rechts bis 3.5 V)
        sy = (y0 - 15)                                   # Pixel pro "voller Strom"
        achse = "gray55"
        c.create_line(10, y0, w - 5, y0, fill=achse, arrow="last")
        c.create_line(x0, h - 5, x0, 8, fill=achse, arrow="last")
        c.create_text(w - 12, y0 - 10, text="U", fill=achse)
        c.create_text(x0 + 12, 12, text="I", fill=achse)
        for v in (1, 2, 3):
            c.create_text(x0 + v * sx, y0 + 10, text=f"{v} V", fill=achse, font=(FONT, 8))
        # Durchlasskurven: vereinfacht als Exponentialkurve ab Schwellspannung
        for name, (us, farbe) in typen.items():
            pts = []
            for k in range(0, 120):
                u = k * 3.5 / 120
                i = min(1.0, math.exp((u - us) * 12) * 0.05) if u > us - 0.4 else 0
                pts += [x0 + u * sx, y0 - i * sy]
            c.create_line(*pts, fill=farbe, width=2, smooth=True)
        # Z-Diode: Sperrbereich nach links, Durchbruch bei -UZ
        uz = uz_slider_wert[0]
        sx_neg = (x0 - 15) / 12                           # links bis -12 V
        pts = []
        for k in range(0, 120):
            u = -k * 12 / 120
            i = -min(0.2, math.exp((-u - uz) * 8) * 0.01) if -u > uz - 0.6 else 0
            pts += [x0 + u * sx_neg, y0 - i * sy]
        c.create_line(*pts, fill="#f59e0b", width=2, smooth=True)
        c.create_text(x0 - uz * sx_neg, y0 + 12, text=f"−{uz:.1f} V", fill="#f59e0b", font=(FONT, 8))
        # Legende
        for n, (name, (_, farbe)) in enumerate(list(typen.items()) + [("Z-Diode", (0, "#f59e0b"))]):
            c.create_text(12, 14 + n * 15, text="■ " + name, fill=farbe, anchor="w", font=(FONT, 9))

    canvas = ResponsiveCanvas(kl.body, zeichne_kennlinie, width=380, height=250)
    canvas.grid(row=0, column=0, columnspan=3, sticky="w")

    uz_label = ctk.CTkLabel(kl.body, text="UZ = 5.1 V", anchor="w", width=90)

    def uz_geaendert(wert):
        uz_slider_wert[0] = float(wert)
        uz_label.configure(text=f"UZ = {float(wert):.1f} V")
        canvas.redraw()

    ctk.CTkLabel(kl.body, text="Z-Spannung", anchor="w").grid(row=1, column=0, sticky="w", pady=6)
    slider = ctk.CTkSlider(kl.body, from_=2.7, to=11, command=uz_geaendert)
    slider.set(5.1)
    slider.grid(row=1, column=1, sticky="ew", padx=8)
    uz_label.grid(row=1, column=2, sticky="w")
    kl.body.grid_columnconfigure(1, weight=1)

    # --- Wiki ------------------------------------------------------------------
    info = page.add(Card(page.body))
    InfoText(info.body, """
        ## Diode – Grundlagen
        Eine Diode ist ein **PN-Übergang**: Sie lässt Strom nur in eine Richtung durch – von der **Anode (A)** zur **Kathode (K)**. Die Kathode ist am Bauteil mit einem Ring markiert.
        - **Durchlassrichtung:** ab der Schwellspannung steigt der Strom exponentiell (Si ≈ `0.7 V`, Ge ≈ `0.3 V`, Schottky ≈ `0.3 V`)
        - **Sperrrichtung:** nur ein winziger Sperrstrom fliesst – bis zur Durchbruchspannung
        - **Diodengleichung (Shockley):** `I = I_S · (e^(U / (n·U_T)) − 1)`, mit `U_T ≈ 26 mV` bei 25 °C
        - **Temperatur:** die Schwellspannung sinkt um ca. `2 mV/K`
        ## Diodentypen
        - **Gleichrichterdiode** (z.B. 1N4007): Netzteile, Verpolschutz
        - **Schottky-Diode** (z.B. 1N5819): kleine Durchlassspannung, sehr schnell → Schaltnetzteile
        - **Z-Diode:** wird bewusst in **Sperrrichtung** betrieben, hält die Spannung bei `U_Z` konstant
        - **LED:** leuchtet in Durchlassrichtung, Spannung abhängig von der Farbe, braucht **immer** einen Vorwiderstand
        - **Freilaufdiode:** antiparallel zu Spulen/Relais, schützt den Transistor vor der Abschaltspannungsspitze
        ## Gleichrichter
        - **Einweg:** nutzt nur eine Halbwelle, Brummfrequenz = `f`
        - **Brücke (Graetz):** nutzt beide Halbwellen, 2 Dioden im Strompfad (`2 · 0.7 V` Verlust), Brummfrequenz = `2f`
        - **Ladekondensator:** glättet; Brummspannung `U_Br ≈ I / (f_Br · C)`
        ## Merkpunkte für die Prüfung
        - Z-Diode: `R_V` für den **schlechtesten Fall** rechnen (UE min + Laststrom max), dann **Leerlauf** prüfen (UE max, alles fliesst durch die Z-Diode)
        - LED nie direkt an Spannung – Strom wird nur durch den Vorwiderstand begrenzt
        - Sperrspannung der Gleichrichterdiode ≥ `Û` (bei Einweg mit Ladekondensator sogar `2 · Û`)
    """).grid(row=0, column=0, sticky="ew")

    page.add(Table(page.body, "Diodentypen",
        ["Typ", "Besonderheit", "Typischer Einsatz"],
        [["1N4007", "Gleichrichter, 1 A, 1000 V Sperrspannung", "Netzteile, Verpolschutz"],
         ["1N4148", "Schaltdiode, sehr schnell, kleine Ströme", "Signale, Freilaufdiode bei kleinen Relais"],
         ["1N5819 (Schottky)", "U_F ≈ 0.3 V, sehr schnell, höherer Sperrstrom", "Schaltnetzteile, Verpolschutz mit wenig Verlust"],
         ["Z-Diode (BZX55…)", "in Sperrrichtung betrieben, hält U_Z konstant", "Referenzspannung, Überspannungsschutz"],
         ["LED", "U_F 1.8 … 3.3 V je nach Farbe", "Anzeige, Beleuchtung, Optokoppler"],
         ["TVS-Diode", "sehr schnelle Klemmung hoher Spitzen", "ESD- und Überspannungsschutz an Leitungen"],
         ["Brückengleichrichter", "4 Dioden in einem Gehäuse", "Netzteile (Graetz-Schaltung)"]]))

    page.add(Table(page.body, "Typische Durchlassspannungen",
        ["Diode", "U_F", "Bemerkung"],
        [["Germanium", "≈ 0.3 V", "selten, alte Schaltungen"],
         ["Schottky", "0.2 … 0.45 V", "steigt mit dem Strom"],
         ["Silizium", "0.6 … 0.7 V", "Standard für Rechnungen"],
         ["LED rot / gelb", "1.8 … 2.1 V", ""],
         ["LED grün", "2.0 … 3.2 V", "je nach Technologie"],
         ["LED blau / weiss", "3.0 … 3.3 V", ""]],
        note="Richtwerte. Genaue Werte im Datenblatt (abhängig von Strom und Temperatur)."))

    page.add(Callout(page.body, "tipp", "Kniffe & Praxis", [
        "Kathode = Seite mit dem **Ring**, bei LEDs das **kürzere Bein** bzw. die abgeflachte Gehäuseseite.",
        "Diodentest mit dem Multimeter: Durchlass zeigt ca. `0.5 … 0.7 V`, Sperrrichtung **OL**.",
        "Z-Dioden um **5 … 6 V** haben den kleinsten Temperaturkoeffizienten → beste Referenz.",
        "Verpolschutz: Schottky in Serie (wenig Verlust) oder Diode parallel + Sicherung.",
        "Mehrere LEDs **nie** parallel an einem Vorwiderstand – jede LED bekommt ihren eigenen.",
    ]))

    page.add(Callout(page.body, "fehler", "Häufige Fehler", [
        "LED ohne Vorwiderstand angeschlossen → LED brennt sofort durch.",
        "Diode verkehrt eingebaut → Schaltung ohne Funktion oder Kurzschluss (Verpolschutz parallel).",
        "Z-Diode in Durchlassrichtung eingebaut → nur `0.7 V` statt `U_Z`.",
        "Z-Diode im Leerlauf nicht geprüft → P_Z zu gross, Diode überhitzt.",
        "Sperrspannung zu klein gewählt: bei Einweg mit Ladekondensator muss sie ≥ `2 · Û` sein.",
        "Freilaufdiode bei Relais vergessen → Abschaltspitze zerstört den Transistor.",
    ]))

    page.add(SeeAlso(page.body, parent, [("Transistor", "transistor"), ("Kondensator", "kondensator"),
                                         ("Widerstand", "widerstand"), ("Relais", "relais")]))
