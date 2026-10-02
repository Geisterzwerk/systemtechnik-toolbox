# Seite "Differenz- und Instrumentenverstärker"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Differenz- und Instrumentenverstärker",
    "reihenfolge": 30,
    "kurz": "Verstärkt nur die Differenz zweier Spannungen und unterdrückt, was auf beiden gleich ist (Gleichtakt).",
    "stichworte": ["Differenzverstärker", "Subtrahierer", "Instrumentenverstärker", "INA", "INA128", "AD620",
                   "Gleichtakt", "Gleichtaktunterdrückung", "CMRR", "Messbrücke", "Shunt", "High-Side", "R_G"],

    "grafiken": ["schaltung_differenz"],

    "erklaerung": """
## Funktion
Viele Sensoren liefern ihr Signal als kleine **Differenz** auf einer grossen **Gleichtaktspannung**: Messbrücke (2.5 V ± einige mV), Shunt auf der High-Side (12 V ± 50 mV), symmetrische Leitungen.
- Differenz `U_d = U2 − U1`, Gleichtakt `U_cm = (U1 + U2) / 2`

**Differenzverstärker** (ein OPV, vier Widerstände, R1 an beiden Eingängen, R2 als Gegenkopplung bzw. nach GND):
- `Ua = R2 / R1 · (U2 − U1)` – aber nur, wenn die Widerstandsverhältnisse exakt gleich sind.
- Eingangswiderstände ungleich und klein (− Eingang: R1, + Eingang: R1 + R2).

**Instrumentenverstärker** (3 OPV): Zwei nichtinvertierende Verstärker vor einem Differenzverstärker, dazwischen R_G.
- `G = (1 + 2 · R / R_G) · R2 / R1`  – die Verstärkung wird mit EINEM Widerstand eingestellt.
- Beide Eingänge hochohmig, der Gleichtakt läuft mit Verstärkung 1 durch die Eingangsstufe, die Differenz wird schon dort verstärkt.

## Dimensionierung
1. Gleichtaktbereich und Differenz bestimmen, gewünschte Verstärkung festlegen.
2. Differenzverstärker: R2/R1 = Verstärkung, Widerstände **0.1 %** oder ein abgeglichenes Netzwerk.
3. Gleichtaktunterdrückung abschätzen: `CMRR ≈ (1 + R2/R1) / (4 · Toleranz)` – 1 % Toleranz bei Vu = 10 ergibt nur ≈ 49 dB.
4. Fehler am Ausgang = `U_cm / CMRR · A_d`, mit dem Nutzsignal vergleichen.
5. Für kleine Signale (Brücke, Thermoelement, EKG) einen **integrierten INA** nehmen (INA128, AD620: `G = 1 + 50 kΩ / R_G`, CMRR > 100 dB).
6. Gleichtaktbereich und Aussteuerung der inneren OPV prüfen: Die Ausgänge der Eingangsstufe liegen bei `U_cm ± G1 · U_d / 2`.

## Betriebszustände
- **Nur Differenz** (U_cm = 0): Ausgang = Verstärkung · U_d.
- **Nur Gleichtakt** (U_d = 0): Ausgang sollte 0 V sein – was übrig bleibt, ist der Gleichtaktfehler.
- **Übersteuert**: Bei grossem Gleichtakt kann eine INNERE Stufe an die Grenze kommen, obwohl der Ausgang klein ist – darum steht im Datenblatt ein Diagramm „Common-Mode vs. Output Voltage“.

## Messpunkte
- U1 und U2 gegen GND einzeln messen, Differenz rechnen – nicht mit einem geerdeten Oszilloskop „zwischen“ die Eingänge gehen.
- **M1** (Ausgang) bei kurzgeschlossenen Eingängen (U_d = 0) an Gleichtakt legen → Gleichtaktfehler direkt messbar.
- Beim INA die Ausgänge der Eingangsstufe prüfen, wenn das Ergebnis unplausibel ist (innere Übersteuerung).

## Grenzfälle
- Toleranz 0 (ideal): CMRR → ∞, nur die Differenz zählt.
- Quelle mit Innenwiderstand am einfachen Differenzverstärker: R_i liegt in Reihe zu R1 → Verhältnis stimmt nicht mehr, CMRR bricht ein. Abhilfe: Puffer davor = Instrumentenverstärker.
- R_G → ∞ (offen): Eingangsstufe hat Verstärkung 1 → G = R2/R1.
- Gleichtakt ausserhalb der Versorgung (z.B. 48-V-Shunt): Spezielle Strommessverstärker (INA240, INA219) verwenden.
""",

    "tipps": [
        "R_G kann man mit einem Schalter oder Poti umschalten – die Gleichtaktunterdrückung bleibt dabei erhalten.",
        "Bei langen Sensorleitungen eingestreuter Netzbrumm ist Gleichtakt – genau das, was der INA unterdrückt.",
    ],
    "fehler": [
        "Normale 1-%-Widerstände im Differenzverstärker – der Gleichtakt kommt zu einem guten Teil durch.",
        "Hochohmige Quelle direkt an den einfachen Differenzverstärker – Verstärkung und CMRR stimmen nicht.",
        "Gleichtaktbereich nicht geprüft – innere Stufen übersteuern, obwohl die Formel ein kleines Ergebnis liefert.",
    ],
    "siehe_auch": ["wheatstone_bruecke", "opv_verstaerker", "opv_addierer"],
    "rechner": ["differenzverstaerker", "bruecke"],
}
