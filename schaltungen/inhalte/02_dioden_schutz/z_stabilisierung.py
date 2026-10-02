# Seite "Z-Dioden-Stabilisierung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Z-Dioden-Stabilisierung",
    "reihenfolge": 60,
    "kurz": "Vorwiderstand und Z-Diode halten eine Spannung konstant – für kleine Ströme.",
    "stichworte": ["Z-Diode", "Zener", "Zenerdiode", "Stabilisierung", "Parallelstabilisierung", "Vorwiderstand",
                   "Spannungsreferenz", "Glättungsfaktor"],

    "grafiken": ["schaltung_zstabi"],

    "erklaerung": """
## Funktion
Die Z-Diode leitet in Sperrrichtung ab U_Z und hält dann ihre Spannung fast konstant (differentieller Widerstand r_z, typ. 5 … 30 Ω). Der **Vorwiderstand R_V** nimmt die Differenz `Ue − U_Z` auf. Sein Strom teilt sich auf:
- `I_RV = (Ue − U_Z) / R_V = I_Z + I_L`

Ändert sich Ue oder die Last, ändert sich nur I_Z – Ua bleibt (fast) gleich. Die Z-Diode liegt **parallel** zur Last (Parallelstabilisierung).

## Dimensionierung
1. **R_V** so, dass im ungünstigsten Fall (Ue minimal, Last maximal) noch `I_Z,min` (ca. 1 … 5 mA) fliesst:
   `R_V ≤ (Ue,min − U_Z) / (I_Z,min + I_L,max)` – nächst kleineren Normwert wählen.
2. **Leistung der Z-Diode** im anderen Extrem (Ue maximal, Last minimal oder abgeklemmt):
   `I_Z,max = (Ue,max − U_Z) / R_V − I_L,min`,   `P_Z = U_Z · I_Z,max` – mit Reserve (Faktor 1.5).
3. **Leistung R_V**: `(Ue,max − U_Z)² / R_V`.
4. Glättung: `ΔUa / ΔUe ≈ r_z / (R_V + r_z)` – je grösser R_V, desto besser, aber desto weniger Laststrom ist möglich.

## Betriebszustände
- **Stabilisiert**: Z-Diode leitet (I_Z ≥ I_Z,min), Ua ≈ U_Z.
- **Überlastet**: Last zieht zu viel, I_Z fällt unter den Knick – Ua sinkt, die Schaltung ist nur noch ein Spannungsteiler.
- **Leerlauf**: der ganze Strom fliesst durch die Z-Diode – höchste Verlustleistung.

## Messpunkte
- **M1** (Ua) bei kleiner und grosser Last: Ua darf sich nur um wenige 10 mV ändern.
- Spannung an R_V messen → I_RV; Laststrom getrennt messen → I_Z = I_RV − I_L.
- Temperatur der Z-Diode im Leerlauf mit dem Finger/Thermometer prüfen (Achtung: bis 100 °C möglich).

## Grenzfälle
- Ue < U_Z: Z-Diode sperrt, Ua = belasteter Spannungsteiler aus R_V und R_L.
- Kurzschluss am Ausgang: Strom `Ue / R_V` – nur R_V wird belastet, die Z-Diode ist stromlos.
- U_Z ≈ 5.6 V hat fast keinen Temperaturkoeffizienten; darunter wird U_Z bei Wärme kleiner, darüber grösser.
""",

    "tipps": [
        "Für mehr als ein paar mA: Längsregler (78xx, LDO) verwenden – die Z-Diode verheizt sonst ständig Leistung.",
        "Z-Diode + Emitterfolger (Transistor) ergibt einen einfachen Längsregler: Die Z-Diode liefert nur den Basisstrom.",
        "Als genaue Referenz statt Z-Diode eine Referenz-IC verwenden (z.B. TL431, LM4040).",
    ],
    "fehler": [
        "R_V mit dem Normwert nach OBEN gerundet – dann reicht der Strom bei Ue,min und Volllast nicht mehr.",
        "Verlustleistung nur bei Nennlast gerechnet – im Leerlauf wird die Z-Diode am heissesten.",
        "Z-Diode in Durchlassrichtung eingebaut – Ua ist dann nur 0.7 V.",
    ],
    "siehe_auch": ["gleichrichter_ladeelko", "diodenbegrenzung"],
    "rechner": ["zdiode_stabi", "e_reihe", "kuehlkoerper"],
}
