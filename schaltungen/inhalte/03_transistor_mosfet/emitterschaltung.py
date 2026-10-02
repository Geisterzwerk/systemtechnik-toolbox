# Seite "Emitterschaltung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Emitterschaltung (Spannungsverstärker)",
    "reihenfolge": 40,
    "kurz": "Grundschaltung zum Verstärken kleiner Wechselspannungen – invertierend, mit einstellbarer Verstärkung.",
    "stichworte": ["Emitterschaltung", "Verstärker", "Arbeitspunkt", "Basisspannungsteiler", "Gegenkopplung",
                   "Emitterkondensator", "C_E", "Kleinsignal", "Verstärkung", "Phasendrehung"],

    "grafiken": ["schaltung_emitter"],

    "erklaerung": """
## Funktion
Der Emitter ist der gemeinsame Bezugspunkt von Ein- und Ausgang. Eine kleine Änderung der Basisspannung ändert I_C, und R_C setzt diese Stromänderung in eine grosse Spannungsänderung um – **umgekehrt** zum Eingang (180° Phasendrehung).
- Basisteiler R1/R2 stellt den **Arbeitspunkt** (Ruhestrom) ein, Koppelkondensatoren trennen den Gleichanteil ab.
- `Vu ≈ −R_C / (r_e + R_E)` mit `r_e = U_T / I_E ≈ 26 mV / I_E`
- ohne C_E: `Vu ≈ −R_C / R_E` (klein, aber stabil – Stromgegenkopplung)
- mit C_E: R_E ist für Wechselstrom überbrückt, `Vu ≈ −R_C / r_e` (gross, aber abhängig von Temperatur und Strom)

## Dimensionierung
1. Ruhestrom I_C wählen (z.B. 1 … 2 mA bei Kleinsignal).
2. U_E ≈ 1 … 2 V (≈ 10 … 20 % von U_B) für eine stabile Gegenkopplung: `R_E = U_E / I_E`.
3. Kollektor in die Mitte zwischen U_E und U_B legen: `R_C ≈ (U_B − U_E) / (2 · I_C)`.
4. Basisteiler: `U_B,Basis = U_E + 0.7 V`, Querstrom ≥ 10 × I_B (damit β kaum eine Rolle spielt).
5. Koppelkondensatoren so gross, dass ihr Blindwiderstand bei der tiefsten Frequenz ≪ r_ein bzw. R_Last ist; C_E ≫ 1 / (2π · f · r_e).

## Betriebszustände
- **Arbeitspunkt richtig**: Ausgang kann symmetrisch nach oben und unten aussteuern.
- **Übersteuert oben**: Transistor sperrt in der Spitze – Ausgang bleibt bei U_B stehen.
- **Übersteuert unten**: Transistor sättigt – Ausgang bleibt bei U_E + U_CE,sat stehen.
- **Arbeitspunkt daneben**: Schon kleine Signale werden einseitig abgeschnitten.

## Messpunkte
- Gleichspannungen ohne Signal mit dem Multimeter: U_B,Basis, U_E (≈ U_B,Basis − 0.7 V), **M1** U_C ≈ Mitte.
- Mit Signal und Oszilloskop: Eingang und Ausgang gleichzeitig → Verstärkung = û_a / û_e, Phasendrehung sichtbar, abgeflachte Spitzen = Übersteuerung.
- I_C aus dem Spannungsfall an R_C berechnen (nicht den Kreis auftrennen).

## Grenzfälle
- R_E = 0 und ohne Gegenkopplung: Arbeitspunkt läuft mit Temperatur weg (thermisches Weglaufen).
- Last am Ausgang: liegt parallel zu R_C → kleinere Verstärkung (Emitterfolger als Puffer dahinter).
- Hohe Frequenzen: Miller-Effekt (Basis-Kollektor-Kapazität × Verstärkung) begrenzt die Bandbreite.
""",

    "tipps": [
        "Kompromiss aus stabil und viel Verstärkung: R_E aufteilen, nur einen Teil mit C_E überbrücken.",
        "In der Praxis wird die Emitterschaltung für Spannungsverstärkung oft durch einen OPV ersetzt – das Prinzip (Arbeitspunkt, Gegenkopplung) bleibt das gleiche.",
    ],
    "fehler": [
        "Arbeitspunkt nicht in der Mitte – das Signal wird schon bei kleiner Aussteuerung einseitig abgeschnitten.",
        "Querstrom im Basisteiler zu klein – der Arbeitspunkt hängt von β ab und streut von Exemplar zu Exemplar.",
        "C_E vergessen oder zu klein: Verstärkung viel kleiner als erwartet (oder frequenzabhängig).",
    ],
    "siehe_auch": ["emitterfolger", "konstantstromquelle"],
    "rechner": ["bjt_arbeitspunkt", "blindwiderstand_c"],
}
