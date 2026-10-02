# Seite "Komparator und Schmitt-Trigger"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Komparator und Schmitt-Trigger",
    "reihenfolge": 40,
    "kurz": "Vergleichen statt verstärken: Der Ausgang springt um – mit Hysterese genau einmal, auch bei Störungen.",
    "stichworte": ["Komparator", "Schmitt-Trigger", "Hysterese", "Mitkopplung", "Schaltschwelle", "U_T+", "U_T-",
                   "Schwellwertschalter", "Flattern", "Offset", "Referenzspannung", "LM393", "Open-Collector"],

    "grafiken": ["schaltung_schmitt"],

    "erklaerung": """
## Funktion
**Komparator** (keine Gegenkopplung): Ist U+ > U−, geht der Ausgang an die obere Grenze, sonst an die untere. Eine Spannung wird mit einer Referenz verglichen (Temperatur zu hoch? Batterie leer?).

Problem: Wackelt das Signal nahe der Schwelle (Rauschen, Brumm, langsame Flanke), schaltet der Ausgang bei jedem Durchgang – er **flattert**.

**Schmitt-Trigger**: Über R_f wird ein Teil des Ausgangs auf den + Eingang **mitgekoppelt**. Nach dem Umschalten springt die Schwelle weg – es gibt zwei Schwellen (Hysterese):
- **invertierend** (Signal an −, R1 von + nach U_ref): `U_T± = (U_ref · R_f ± U_sat · R1) / (R1 + R_f)`,  Hysterese `2 · U_sat · R1 / (R1 + R_f)`
- **nichtinvertierend** (Signal über R1 an +, − an U_ref): `U_T± = U_ref · (1 + R1/R_f) ± U_sat · R1/R_f`,  Hysterese `2 · U_sat · R1 / R_f`
- **mit Offset**: U_ref ≠ 0 verschiebt die Mitte der Schwellen (z.B. Schaltpunkt bei 2.5 V statt 0 V).

## Dimensionierung
1. Gewünschte Schwellen U_T+ und U_T− festlegen; Hysterese grösser als die Störung Spitze-Spitze (Faustregel 2 × Rauschen).
2. Verhältnis aus der Hysterese: invertierend `R1/(R1 + R_f) = ΔU / (2 · U_sat)`, nichtinvertierend `R1/R_f = ΔU / (2 · U_sat)`.
3. U_ref aus der Mitte: invertierend `U_ref = Mitte / (1 − R1/(R1 + R_f))`, nichtinvertierend `U_ref = Mitte / (1 + R1/R_f)`.
4. U_sat realistisch einsetzen (klassischer OPV: U_B − 1.5 V; Rail-to-Rail: ≈ U_B).
5. Für schnelle Signale einen echten **Komparator-IC** (LM393, TLV3501) statt eines OPV nehmen: kurze Schaltzeit, oft Open-Collector-Ausgang (Pull-up nötig, Pegel frei wählbar).

## Betriebszustände
- **Unter U_T−**: Ausgang in der einen Endlage (nichtinvertierend: unten).
- **Zwischen den Schwellen**: Ausgang bleibt, wo er war (Gedächtnis!).
- **Über U_T+**: Ausgang springt in die andere Endlage.
- **Komparator ohne Hysterese**: schaltet an der einen Schwelle beliebig oft hin und her.

## Messpunkte
- Eingang und **M1** (Ausgang) gleichzeitig mit dem Oszilloskop: Schaltzeitpunkte ablesen → U_T+ und U_T−.
- XY-Darstellung (X = Eingang, Y = Ausgang) bei langsamem Dreieck: zeigt die Hystereseschleife direkt.
- Flattern sichtbar machen: Zeitbasis um den Schaltpunkt vergrössern, Trigger auf die Flanke.

## Grenzfälle
- R_f → ∞ (keine Mitkopplung): Hysterese 0 → normaler Komparator.
- R1 → 0 (invertierend): beide Schwellen = U_ref, ebenfalls keine Hysterese.
- Hysterese grösser als das Signal: Eine Schwelle wird nie erreicht – der Ausgang schaltet nie um.
- OPV als Komparator: viele OPV sind langsam aus der Sättigung (µs) und manche vertragen keine grosse Differenzspannung an den Eingängen – Datenblatt prüfen.
""",

    "tipps": [
        "Eine Dämmerungsschaltung oder ein Thermostat braucht IMMER Hysterese, sonst flackert das Licht bzw. taktet die Heizung.",
        "Die Eingänge vieler µC haben eingebaute Schmitt-Trigger – für Taster und langsame Signale genügt das oft.",
    ],
    "fehler": [
        "OPV ohne Mitkopplung als Komparator an einem verrauschten Signal – der Ausgang flattert.",
        "Mitkopplung an den − Eingang gelegt – das ist Gegenkopplung, die Schaltung verstärkt nur.",
        "U_sat = U_B gerechnet, obwohl der OPV nur bis U_B − 1.5 V kommt – die Schwellen stimmen nicht.",
    ],
    "siehe_auch": ["tasterentprellung", "opv_verstaerker"],
    "rechner": ["schmitt_trigger", "spannungsteiler"],
}
