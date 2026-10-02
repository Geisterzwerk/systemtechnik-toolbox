# Seite "Diodenbegrenzung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Diodenbegrenzung (Clipper)",
    "reihenfolge": 10,
    "kurz": "Dioden schneiden ein Signal oberhalb (und unterhalb) einer festen Spannung ab.",
    "stichworte": ["Begrenzer", "Clipper", "Diodenbegrenzung", "Amplitudenbegrenzung", "antiparallel",
                   "Z-Diode", "Klemmschaltung", "Pegelbegrenzung"],

    "grafiken": ["schaltung_begrenzer"],

    "erklaerung": """
## Funktion
Ein Vorwiderstand R_V und eine oder mehrere Dioden vom Ausgang nach GND bilden einen spannungsabhängigen Spannungsteiler:
- Solange die Ausgangsspannung unter der Schwelle liegt, **sperren** die Dioden – fast kein Strom, `u_a = u_e`.
- Erreicht sie die Schwelle, **leiten** die Dioden, die Spannung bleibt dort stehen, der Rest fällt an R_V ab.

Schwellen: eine Si-Diode `+0.7 V`, zwei antiparallel `±0.7 V`, zwei Z-Dioden gegeneinander `±(U_Z + 0.7 V)` (eine arbeitet im Durchbruch, die andere in Durchlassrichtung).

## Dimensionierung
1. **Begrenzungspegel** wählen: Si 0.7 V, Schottky 0.3 V, LED 1.8 … 3 V, Z-Diode U_Z + 0.7 V.
2. **R_V** begrenzt den Diodenstrom im schlimmsten Fall: `R_V ≥ (Û_max − U_Begrenzung) / I_D,max` (1N4148: Dauerstrom max. 200 mA, besser ≤ 10 mA).
3. **Leistung** in R_V prüfen: im Begrenzungsfall `P = (Û − U_B)² / R_V` (Spitze), bei Sinus etwa die Hälfte im Mittel.
4. **Nicht zu gross**: R_V bildet mit der Eingangskapazität der nächsten Stufe einen Tiefpass.

## Betriebszustände
- **Kleines Signal** (Û < Schwelle): Dioden sperren, Signal läuft unverändert durch.
- **Grosses Signal**: Spitzen werden abgeschnitten – aus einem grossen Sinus wird fast ein Rechteck.
- **Einseitig**: Nur die positive Halbwelle wird begrenzt, die negative läuft voll durch.

## Messpunkte
- **M1** (Ausgang) mit dem Oszilloskop: abgeflachte Spitzen bei ±0.7 V bzw. ±(U_Z + 0.7 V).
- Eingang u_e mit einem zweiten Kanal gleichzeitig ansehen: Zeigt, ab wann begrenzt wird.
- Diodenstrom indirekt: Spannung an R_V messen und durch R_V teilen.

## Grenzfälle
- `R_V → 0`: Die Diode schliesst die Quelle kurz – Diode oder Quelle wird zerstört.
- `R_V` sehr gross: Die Begrenzung wirkt noch, aber jede Last am Ausgang verschiebt den Pegel.
- Diodenkennlinie ist nicht ideal: Bei kleinen Strömen setzt die Begrenzung „weich“ schon ab ca. 0.5 V ein, bei grossen Strömen liegt sie über 0.7 V.
""",

    "tipps": [
        "Zum Schutz eines Messeingangs: zwei Schottky-Dioden gegen die Versorgung und GND klemmen (siehe Eingangsschutz) – genauer als eine Z-Diode.",
        "Ein Begrenzer mit zwei antiparallelen Dioden ist auch ein einfacher Gehörschutz am Kopfhörer-Ausgang eines Messgeräts.",
    ],
    "fehler": [
        "Vorwiderstand vergessen – die Diode leitet direkt an der Quelle und brennt durch.",
        "Z-Diode allein statt zwei gegeneinander: In der anderen Richtung begrenzt sie schon bei −0.7 V.",
        "Begrenzung im Signalpfad eines Audio- oder Messsignals ohne es zu merken – das Signal wird verzerrt (Oberwellen).",
    ],
    "siehe_auch": ["eingangsschutz", "z_stabilisierung", "tvs_schutz"],
    "rechner": ["diode_verlust", "ohm_leistung"],
}
