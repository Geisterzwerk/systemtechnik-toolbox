# Seite "Ungeregeltes Netzteil"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Der Plan "schaltung_gleichrichter" (schaltungen/grafiken_dioden.py) wird wiederverwendet.

THEMA = {
    "titel": "Netzteil: Trafo + Gleichrichter + Elko auslegen",
    "reihenfolge": 20,
    "kurz": "Vom gewünschten Ausgang rückwärts: Welche Trafospannung, welcher Elko, welche Trafoleistung?",
    "stichworte": ["Netzteil", "Trafonetzteil", "ungeregelt", "Trafo", "Brückengleichrichter", "Ladeelko",
                   "Welligkeit", "Netztoleranz", "Leerlaufspannung", "Scheinleistung", "VA", "Formfaktor"],

    "grafiken": ["schaltung_gleichrichter"],

    "erklaerung": """
## Funktion
Der Trafo setzt die Netzspannung herunter und trennt galvanisch, der Brückengleichrichter klappt die negative Halbwelle um, der Ladeelko glättet:
- Spitze am Elko: `Û = U_sek · √2 − 2 · U_F` (zwei Dioden leiten gleichzeitig)
- Zwischen den Spitzen versorgt nur der Elko die Last → Welligkeit `ΔU ≈ I / (2 · f · C)` (Brücke: 100 Hz)
- Der Trafo liefert nur in kurzen Spitzen Strom (Stromflusswinkel klein) → sein Effektivstrom ist deutlich grösser als der Gleichstrom: `I_sek,eff ≈ 1.6 … 1.8 · I_DC`.

## Dimensionierung
Rückwärts vom Ausgang her (mit Regler dahinter):
1. Im **Wellental** muss noch `U_aus + Dropout` anliegen (78xx: 2 V, LDO: 0.3 V).
2. Welligkeit wählen (z.B. 10 % oder 1 … 2 V) → `C = I / (2 · f · ΔU)`.
3. Spitze bei Netz −10 %: `Û_min = U_Tal + ΔU + 2 · U_F` → `U_sek = Û_min / (√2 · 0.9)` (Trafo-Nennspannung, eff).
4. Trafoleistung: `S ≈ U_sek · 1.8 · I_DC` (in VA) – Typenschild gilt für ohmsche Last!
5. Elko-Spannungsfestigkeit: Netz +10 % UND Leerlaufüberhöhung kleiner Trafos (+10 … 25 %) → nächste Reihe (16/25/35/50 V).
6. Brückengleichrichter: I_F ≥ 2 · I_DC (Einschaltstromstoss!), U_RRM ≥ 2 · Û.

## Betriebszustände
- **Leerlauf**: Elko lädt auf die volle Spitze (+ Trafo-Leerlaufüberhöhung) – höchste Spannung am Regler.
- **Volllast bei Netz −10 %**: tiefstes Wellental – hier muss der Regler noch regeln.
- **Einschalten**: leerer Elko wirkt wie ein Kurzschluss → grosser Einschaltstrom (NTC oder Softstart bei grossen Elkos).

## Messpunkte
- Am Elko mit dem Oszilloskop (DC-Kopplung, dann AC-Kopplung für die Welligkeit): Spitze, Tal, ΔU.
- Trafo-Sekundärspannung im Leerlauf und unter Last vergleichen (Leerlaufüberhöhung).
- Netz: nur mit Trenntrafo und Differenztastkopf messen – NIE mit geerdetem Oszilloskop an der Primärseite.

## Grenzfälle
- Kein Elko: pulsierende Gleichspannung (100 Hz), Mittelwert `0.9 · U_sek − 2 · U_F`.
- Riesiger Elko: kleine Welligkeit, aber sehr kurze, hohe Stromspitzen → Trafo und Dioden werden heiss.
- Einweg statt Brücke: nur 50 Hz Nachladen → doppelte Welligkeit, Gleichstromvormagnetisierung des Trafos.
""",

    "tipps": [
        "Faustregel für 5 V / 1 A mit 7805: Trafo 9 V / 15 VA, Elko 4700 µF / 25 V.",
        "Heute meist: Steckernetzteil (Schaltnetzteil) mit 12 V oder 5 V und dahinter Regler/Schaltregler – kleiner, leichter, effizienter.",
    ],
    "fehler": [
        "Trafospannung mit dem Effektivwert statt der Spitze gerechnet – oder umgekehrt.",
        "Netztoleranz vergessen: Bei −10 % Netz fällt der Regler aus der Regelung (Brummen am Ausgang).",
        "Trafo nach Gleichstrom-Leistung gewählt – er wird wegen der Stromspitzen zu heiss.",
    ],
    "siehe_auch": ["gleichrichter_ladeelko", "linearregler", "quellenmodell"],
    "rechner": ["netzteil_auslegen", "netzteil", "gleichrichter", "leistung_trafo"],
}
