# Seite "H-Brücke"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "H-Brücke (Motor in beide Richtungen)",
    "reihenfolge": 30,
    "kurz": "Vier Schalter um einen Motor: vorwärts, rückwärts, bremsen, Freilauf – und warum es eine Totzeit braucht.",
    "stichworte": ["H-Brücke", "H-Bridge", "Vollbrücke", "Motortreiber", "DC-Motor", "Drehrichtung", "PWM",
                   "Shoot-through", "Brückenkurzschluss", "Totzeit", "Dead Time", "Freilauf", "Bremsen",
                   "DRV8871", "L298", "Halbbrücke"],

    "grafiken": ["schaltung_h_bruecke"],

    "erklaerung": """
## Funktion
Vier Schalter (MOSFETs) bilden ein „H“, der Motor ist der Querbalken. Je nachdem, welche zwei Schalter leiten, fliesst der Strom in die eine oder andere Richtung durch den Motor:
- **Vorwärts**: S1 (oben links) + S4 (unten rechts)
- **Rückwärts**: S3 (oben rechts) + S2 (unten links)
- **Bremsen**: S2 + S4 (oder S1 + S3) – der Motor ist kurzgeschlossen, seine Gegenspannung treibt einen bremsenden Strom
- **Freilauf**: alle aus – der Motorstrom fliesst kurz über die Body-Dioden zurück, der Motor läuft aus
- **Verboten**: S1 + S2 (oder S3 + S4) – Kurzschluss direkt über die Versorgung (**Shoot-through**)

Mit **PWM** an einem Schalterpaar stellt man die mittlere Motorspannung ein: `U_M = D · U_B` (D = Tastgrad).

## Dimensionierung
1. Schalter nach Strom und Spannung: `U_DS,max ≥ 1.5 · U_B`, Dauerstrom ≥ Motorstrom, **Anlaufstrom** beachten (`U_B / R_M`, oft das 5- bis 10-Fache des Nennstroms).
2. Verluste: Leitverluste `I² · 2 · R_DS(on)` plus Schaltverluste `≈ U_B · I · t_sw · f` (Rechner „H-Brücke: Verluste“).
3. **Totzeit** zwischen Aus- und Einschalten der Schalter einer Seite: länger als die Ausschaltzeit (typ. 100 ns … 1 µs). Treiber-ICs machen das automatisch.
4. High-Side-N-MOSFETs brauchen eine Gate-Spannung über U_B → Bootstrap-Treiber (Seite „Gate-Treiber“).
5. PWM-Frequenz über dem Hörbereich (≥ 20 kHz) oder tief genug, dass die Schaltverluste klein bleiben.
6. Pufferkondensator (Elko + Keramik) direkt an der Brücke – beim Bremsen und im Freilauf fliesst Energie zurück in die Versorgung.

## Betriebszustände
- **Anlauf**: Motor steht, keine Gegenspannung → `I = U_B / (R_M + 2 · R_DS)` – der grösste Strom.
- **Drehen**: Gegenspannung U_EMK wächst mit der Drehzahl, der Strom sinkt.
- **Bremsen**: Strom kehrt sich um, Energie wird im Motor und den Schaltern in Wärme umgesetzt.
- **Freilauf**: Strom über Dioden zurück in die Versorgung (Spannung kann ansteigen!).

## Messpunkte
- Beide Brückenmitten gegen Masse mit dem Oszilloskop: PWM-Rechteck, Totzeit sichtbar als kurzer Diodenleitungs-Absatz.
- Motorstrom mit Stromzange oder über einen Shunt in der Masseleitung.
- Temperatur der Schalter unter Last.

## Grenzfälle
- Totzeit zu kurz: kurze Stromspitzen bei jedem Umschalten → heisse MOSFETs, Störungen.
- Blockierter Motor: dauernd Anlaufstrom → Strombegrenzung im Treiber nötig.
- Bipolare Treiber (L298) verlieren 2 … 4 V – bei kleinen Spannungen bleibt kaum etwas für den Motor.
- Rückspeisung beim Bremsen in ein Netzteil ohne Rücklastfestigkeit: Versorgungsspannung steigt.
""",

    "tipps": [
        "Für Einsteiger: fertige Motortreiber-ICs (z.B. DRV8871) haben Totzeit, Strombegrenzung und Übertemperaturschutz eingebaut.",
        "„Bremsen“ hält einen drehenden Motor schneller an als „Freilauf“ – im Stillstand hat es aber keine Haltewirkung.",
    ],
    "fehler": [
        "Beide Schalter einer Seite gleichzeitig eingeschaltet (Software-Fehler beim Richtungswechsel) – Kurzschluss.",
        "Nur nach Nennstrom ausgelegt – der Anlaufstrom zerstört die Schalter.",
        "High-Side-N-MOSFET direkt vom µC angesteuert – die Gate-Spannung liegt nicht über der Source (Motoranschluss).",
    ],
    "siehe_auch": ["gate_treiber", "mosfet_schalter", "lasten_ansteuern", "freilaufdiode"],
    "rechner": ["h_bruecke", "mosfet_gate"],
}
