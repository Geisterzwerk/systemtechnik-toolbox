"""widerstand.py – Widerstand: Ohm, Leistung, Farbcode + Wiki (stabiles Layout)"""
import os
import customtkinter as ctk
from PIL import Image

from gui.responsive import (ScrollPage, Card, ResponsiveGrid, InfoText, WrapLabel, FONT,
                            Table, Callout, SeeAlso)


def _zahl(entry):
    t = entry.get().strip().replace(",", ".")
    return float(t) if t else None


def create(parent):
    page = ScrollPage(parent, title="Widerstand", subtitle="Grundlagen, Rechner und Farbcode")
    grid = page.add(ResponsiveGrid(page.body, max_cols=2))

    # --- Ohm ---
    ohm = grid.add(Card(grid, title="Ohm'sches Gesetz", subtitle="Zwei Werte eingeben, ein Feld leer lassen"))
    e_u = ctk.CTkEntry(ohm.body, placeholder_text="Spannung U (V)", width=220)
    e_i = ctk.CTkEntry(ohm.body, placeholder_text="Strom I (A)", width=220)
    e_r = ctk.CTkEntry(ohm.body, placeholder_text="Widerstand R (Ω)", width=220)
    for r, e in enumerate((e_u, e_i, e_r)):
        e.grid(row=r, column=0, sticky="w", pady=4)
    ohm_res = WrapLabel(ohm.body, text="", font=(FONT, 14, "bold"))

    def calc_ohm():
        try:
            u, i, r = _zahl(e_u), _zahl(e_i), _zahl(e_r)
            if u is None:
                ohm_res.configure(text=f"U = {r * i:.2f} V")
            elif i is None:
                ohm_res.configure(text=f"I = {u / r:.4g} A")
            elif r is None:
                ohm_res.configure(text=f"R = {u / i:.2f} Ω")
            else:
                ohm_res.configure(text="Bitte ein Feld leer lassen")
        except (TypeError, ValueError, ZeroDivisionError):
            ohm_res.configure(text="Ungültige Eingabe")

    ctk.CTkButton(ohm.body, text="Berechnen", command=calc_ohm).grid(row=3, column=0, sticky="w", pady=(10, 4))
    ohm_res.grid(row=4, column=0, sticky="w")

    # --- Leistung (eigene Variablennamen!) ---
    lei = grid.add(Card(grid, title="Leistung", subtitle="Zwei beliebige Werte eingeben"))
    p_u = ctk.CTkEntry(lei.body, placeholder_text="Spannung U (V)", width=220)
    p_i = ctk.CTkEntry(lei.body, placeholder_text="Strom I (A)", width=220)
    p_r = ctk.CTkEntry(lei.body, placeholder_text="Widerstand R (Ω)", width=220)
    for r, e in enumerate((p_u, p_i, p_r)):
        e.grid(row=r, column=0, sticky="w", pady=4)
    lei_res = WrapLabel(lei.body, text="", font=(FONT, 14, "bold"))

    def calc_lei():
        try:
            u, i, r = _zahl(p_u), _zahl(p_i), _zahl(p_r)
            if u is not None and i is not None:
                p = u * i
            elif i is not None and r is not None:
                p = i ** 2 * r
            elif u is not None and r is not None:
                p = u ** 2 / r
            else:
                lei_res.configure(text="Bitte zwei Werte eingeben"); return
            lei_res.configure(text=f"P = {p:.2f} W")
        except (ValueError, ZeroDivisionError):
            lei_res.configure(text="Ungültige Eingabe")

    ctk.CTkButton(lei.body, text="Berechnen", command=calc_lei).grid(row=3, column=0, sticky="w", pady=(10, 4))
    lei_res.grid(row=4, column=0, sticky="w")

    # --- Farbcode ---
    farben = {"Schwarz": 0, "Braun": 1, "Rot": 2, "Orange": 3, "Gelb": 4,
              "Grün": 5, "Blau": 6, "Violett": 7, "Grau": 8, "Weiss": 9}
    mult = {"Schwarz": 1, "Braun": 10, "Rot": 100, "Orange": 1_000, "Gelb": 10_000,
            "Grün": 100_000, "Blau": 1_000_000, "Gold": 0.1, "Silber": 0.01}
    tol = {"Braun": "±1%", "Rot": "±2%", "Grün": "±0.5%", "Blau": "±0.25%",
           "Violett": "±0.1%", "Grau": "±0.05%", "Gold": "±5%", "Silber": "±10%"}

    fc = grid.add(Card(grid, title="Farbcode (4 Ringe)"))
    ringe = []
    for r, (name, werte) in enumerate([("Ring 1 (Ziffer)", farben), ("Ring 2 (Ziffer)", farben),
                                       ("Ring 3 (Multiplikator)", mult), ("Ring 4 (Toleranz)", tol)]):
        ctk.CTkLabel(fc.body, text=name, anchor="w").grid(row=r, column=0, sticky="w", pady=4)
        box = ctk.CTkOptionMenu(fc.body, values=list(werte), width=140)
        box.set("wählen")
        box.grid(row=r, column=1, sticky="w", padx=(10, 0), pady=4)
        ringe.append(box)
    fc_res = WrapLabel(fc.body, text="", font=(FONT, 14, "bold"))

    def calc_fc():
        try:
            w = (farben[ringe[0].get()] * 10 + farben[ringe[1].get()]) * mult[ringe[2].get()]
            fc_res.configure(text=f"R = {w:g} Ω   {tol[ringe[3].get()]}")
        except KeyError:
            fc_res.configure(text="Bitte alle Farben wählen")

    ctk.CTkButton(fc.body, text="Berechnen", command=calc_fc).grid(row=4, column=0, sticky="w", pady=(10, 4))
    fc_res.grid(row=5, column=0, columnspan=2, sticky="w")

    # --- Bild: FESTE Grösse -> verzieht nichts ---
    bild = grid.add(Card(grid, title="Farbcode-Tabelle"))
    pfad = os.path.join(os.path.dirname(__file__), "..", "images", "farbcode.png")
    if os.path.exists(pfad):
        img = Image.open(pfad)
        breite = 340
        ctk.CTkLabel(bild.body, text="",
                     image=ctk.CTkImage(img, size=(breite, int(breite * img.height / img.width)))) \
            .grid(row=0, column=0, sticky="w")
    else:
        WrapLabel(bild.body, text=f"Bild fehlt: {pfad}").grid(row=0, column=0, sticky="w")

    # --- Wiki ---
    info = page.add(Card(page.body))
    InfoText(info.body, """
        ## Widerstände – Grundlagen
        Ein Widerstand ist ein passives Bauteil, das den Stromfluss begrenzt. Er wandelt elektrische Energie in Wärme um.
        **Ohm'sches Gesetz:** `R = U / I`     **Leistung:** `P = U · I = I² · R = U² / R`
        ## Typen
        - **Festwiderstände:** Kohleschicht, Metallschicht, Draht
        - **Veränderbare Widerstände:** Potentiometer, Trimmer
        - **Spezialwiderstände:** NTC/PTC (temperaturabhängig), LDR (lichtabhängig), VDR (spannungsabhängig)
        ## Anwendungen
        - Strombegrenzung (z.B. Vorwiderstand LED)
        - Spannungsteiler
        - Pull-up / Pull-down in digitalen Schaltungen
        - Entladen von Kondensatoren
    """).grid(row=0, column=0, sticky="ew")

    page.add(Table(page.body, "Widerstandsarten",
        ["Art", "Besonderheit", "Typischer Einsatz"],
        [["Kohleschicht", "günstig, Toleranz 5 %, rauscht mehr", "einfache Schaltungen"],
         ["Metallschicht", "Toleranz 1 %, rauscharm, temperaturstabil", "Standard, Messtechnik"],
         ["Drahtwiderstand", "hohe Leistung, induktiv", "Lastwiderstände, Shunts"],
         ["SMD (0603, 0805 …)", "klein, Aufdruck statt Farbcode", "Leiterplatten"],
         ["Potentiometer / Trimmer", "einstellbar", "Abgleich, Lautstärke"],
         ["NTC / PTC", "Widerstand ändert mit Temperatur", "Temperaturmessung, Einschaltstrombegrenzung"],
         ["LDR", "Widerstand sinkt bei Licht", "Dämmerungsschalter"],
         ["VDR (Varistor)", "leitet ab einer Spannung", "Überspannungsschutz"]]))

    page.add(Table(page.body, "Normreihen",
        ["Reihe", "Toleranz", "Werte pro Dekade"],
        [["E6", "± 20 %", "1.0  1.5  2.2  3.3  4.7  6.8"],
         ["E12", "± 10 %", "1.0  1.2  1.5  1.8  2.2  2.7  3.3  3.9  4.7  5.6  6.8  8.2"],
         ["E24", "± 5 %", "24 Werte"],
         ["E96", "± 1 %", "96 Werte"]],
        note="Berechnete Werte immer auf den passenden Normwert runden."))

    page.add(Callout(page.body, "tipp", "Kniffe & Praxis", [
        "SMD-Code: `472` = 47 · 10² = **4.7 kΩ**, `4R7` = **4.7 Ω**.",
        "Leistung immer mit Reserve wählen: mindestens **Faktor 2** zur berechneten Leistung.",
        "Reihenschaltung: `R = R1 + R2`, Parallel: `R = R1 · R2 / (R1 + R2)`.",
        "Im eingebauten Zustand messen verfälscht den Wert – mindestens ein Bein auslöten.",
    ]))

    page.add(Callout(page.body, "fehler", "Häufige Fehler", [
        "Farbcode von der falschen Seite gelesen – der Toleranzring (Gold/Silber) ist rechts.",
        "Leistung nicht berechnet → Widerstand wird heiss und verfärbt sich.",
        "Einheiten verwechselt (kΩ / Ω, mA / A) → Faktor 1000 daneben.",
        "Widerstand unter Spannung gemessen → falscher Messwert oder defektes Multimeter.",
    ]))

    page.add(SeeAlso(page.body, parent, [("Kondensator", "kondensator"), ("Diode", "dioden"),
                                         ("Transistor", "transistor"), ("Spule", "spule")]))
