# Seite "OPV als Verstärker"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "OPV-Verstärker: Folger, nichtinvertierend, invertierend",
    "reihenfolge": 10,
    "kurz": "Die drei Grundschaltungen mit Gegenkopplung – Verstärkung allein durch das Widerstandsverhältnis.",
    "stichworte": ["OPV", "Operationsverstärker", "Op-Amp", "Spannungsfolger", "Impedanzwandler", "Puffer",
                   "nichtinvertierender Verstärker", "invertierender Verstärker", "virtuelle Masse", "Gegenkopplung",
                   "GBW", "Rail-to-Rail", "Verstärkung"],

    "grafiken": ["schaltung_opv_verstaerker"],

    "erklaerung": """
## Funktion
Ein OPV verstärkt die Spannung zwischen + und − Eingang sehr stark (Leerlaufverstärkung 10⁵ … 10⁶). Mit **Gegenkopplung** (Ausgang über einen Widerstand zurück an −) regelt er seinen Ausgang so, dass die Eingangsdifferenz praktisch 0 wird:
- **Goldene Regeln** (idealer OPV mit Gegenkopplung): `U+ = U−` (virtueller Kurzschluss) und in die Eingänge fliesst kein Strom.

Daraus folgen die drei Grundschaltungen:
- **Spannungsfolger** (Ausgang direkt an −, Signal an +): `Vu = 1`, Eingang extrem hochohmig, Ausgang niederohmig → Impedanzwandler/Puffer.
- **Nichtinvertierend** (Signal an +, Teiler R2/R1 vom Ausgang an −): `Vu = 1 + R2 / R1`, Eingang hochohmig.
- **Invertierend** (Signal über R1 an −, R2 vom Ausgang an −, + an GND): `Vu = −R2 / R1`. Der − Eingang liegt auf 0 V (**virtuelle Masse**), der Eingangswiderstand ist nur R1.

## Dimensionierung
1. Schaltung wählen: Quelle hochohmig oder Phase muss bleiben → nichtinvertierend; Phase egal, Vu < 1 oder Addition gewünscht → invertierend.
2. Widerstände 1 … 100 kΩ: kleiner belastet den Ausgang, grösser macht Rauschen und Fehler durch Eingangsströme.
3. `R2 = R1 · (Vu − 1)` (nichtinvertierend) bzw. `R2 = R1 · |Vu|` (invertierend), Normwert wählen.
4. **Bandbreite**: `f_g ≈ GBW / (1 + R2/R1)` – ein 1-MHz-OPV mit Vu = 100 schafft nur 10 kHz. Grosse Verstärkung auf zwei Stufen verteilen.
5. **Aussteuerung**: Klassische OPV kommen nur bis ≈ 1.5 V an die Versorgung heran; bei 3.3 / 5 V einen **Rail-to-Rail**-Typ nehmen. Auch der Eingangsspannungsbereich (Gleichtaktbereich) ist begrenzt.
6. Abblockkondensator 100 nF direkt an jeden Versorgungspin.

## Betriebszustände
- **Linear**: Ua = Vu · Ue, U+ = U− (auf wenige µV genau).
- **Übersteuert**: Ua erreicht die Aussteuergrenze, die Regelung „reisst ab“, U+ ≠ U− – das Signal wird abgeschnitten.
- **Zu schnell**: Bei hoher Frequenz oder grossen Sprüngen begrenzen GBW und Slew-Rate (V/µs) – der Ausgang wird verzerrt (Dreieck statt Sinus).

## Messpunkte
- **M1**: invertierend: − Eingang muss ≈ 0 V sein (virtuelle Masse); nichtinvertierend: Eingangssignal.
- **M2** (Ausgang) und Eingang gleichzeitig mit dem Oszilloskop: Vu = û_a / û_e, Phase 0° bzw. 180°.
- Fehlersuche: Ist U+ ≠ U− deutlich (> mV), ist der OPV übersteuert, falsch versorgt oder defekt.

## Grenzfälle
- R2 → 0 bzw. R1 → ∞ (nichtinvertierend): Vu → 1, die Schaltung wird zum Spannungsfolger.
- R1 → 0 (invertierend): Vu → ∞, der Eingang wird kurzgeschlossen – nur die Leerlaufverstärkung begrenzt.
- Kapazitive Last am Ausgang (lange Kabel, > 100 pF): OPV kann schwingen → 50 … 100 Ω in Reihe zum Ausgang.
- Gegenkopplung versehentlich an + (Mitkopplung): Ausgang springt an eine Grenze und bleibt dort (Schmitt-Trigger statt Verstärker).
""",

    "tipps": [
        "„Was der OPV tut“ in einem Satz: Er stellt seinen Ausgang so ein, dass seine beiden Eingänge gleich sind – mehr muss man zum Rechnen nicht wissen.",
        "Der Spannungsfolger ist der beste Puffer hinter einem Spannungsteiler oder vor einem ADC-Eingang.",
        "LM358 / LM324 sind günstig und vertragen GND am Eingang (Single-Supply), kommen aber nicht bis an U_B heran.",
    ],
    "fehler": [
        "+ und − vertauscht – aus der Gegenkopplung wird Mitkopplung, der Ausgang klebt an einer Grenze.",
        "Klassischen OPV an 5 V betrieben und Rail-to-Rail-Verhalten erwartet – der Ausgang erreicht 0 V und 5 V nicht.",
        "Bandbreite vergessen: Vu = 1000 mit einem 1-MHz-OPV gibt nur noch 1 kHz Bandbreite.",
    ],
    "siehe_auch": ["opv_addierer", "differenz_instrumentenverstaerker", "emitterfolger", "spannungsteiler"],
    "rechner": ["opv_verstaerker", "spannungsteiler"],
}
