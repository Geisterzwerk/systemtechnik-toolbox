# Seite "RC-Glied laden und entladen"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Die Lernansicht "rc_ladekurve" gibt es schon (bauteile/grafiken/kurven.py) - hier nur wiederverwendet.

THEMA = {
    "titel": "RC-Glied: Laden und Entladen",
    "reihenfolge": 20,
    "kurz": "Kondensator über einen Widerstand laden und entladen – Verzögerung, Zeitkonstante τ = R · C.",
    "stichworte": ["Laden", "Entladen", "Zeitkonstante", "tau", "RC-Glied", "Verzögerung", "Power-on-Reset",
                   "Ladekurve", "e-Funktion", "Einschaltverzögerung"],

    "grafiken": ["rc_ladekurve"],

    "erklaerung": """
## Funktion
Wird ein RC-Glied an eine Spannung geschaltet, liegt im ersten Moment die ganze Differenz am Widerstand – der Strom ist am grössten. Je voller der Kondensator, desto kleiner die Differenz und der Strom:
- Laden: `u_C(t) = U · (1 − e^(−t/τ))`,  Entladen: `u_C(t) = U_0 · e^(−t/τ)`
- Strom: `i(t) = (U − U_0) / R · e^(−t/τ)`  (Vorzeichen: positiv = Kondensator lädt)
- `τ = R · C`: nach 1 τ 63 %, nach 3 τ 95 %, nach 5 τ > 99 % der Änderung

Anwendungen: Einschaltverzögerung, Power-on-Reset eines µC, Zeitglied (NE555), Soft-Start, Glättung.

## Dimensionierung
1. Gewünschte Zeit bis zu einer Schaltschwelle U_S festlegen.
2. Laden: `t = τ · ln(U / (U − U_S))`, Entladen: `t = τ · ln(U_0 / U_S)`.
3. τ = t / ln(...) → R und C aufteilen: R so, dass der Ladestrom die Quelle nicht überlastet und Leckströme (Elko: µA!) klein dagegen bleiben.
4. Elkos haben grosse Toleranz (−20 … +80 %) – für genaue Zeiten Folien- oder Keramik-C (C0G) und eine Schwelle mit Hysterese.

## Betriebszustände
- **Einschalten** (Laden): Strom springt auf U / R und klingt ab, Spannung steigt an.
- **Ausschalten** (Entladen über R): Strom kehrt die Richtung um, Spannung fällt ab.
- **Nach ≈ 5 τ**: eingeschwungen – kein Strom mehr (idealer C), Spannung = Endwert.
- **Kurzes Schalten** (Pulse kürzer als τ): Der Kondensator erreicht den Endwert nie – er mittelt (Tiefpass).

## Messpunkte
- **M1** (am Kondensator) mit dem Oszilloskop, Trigger auf die Schaltflanke: Zeit bis 63 % = τ.
- Strom indirekt: Spannung am R messen, `i = u_R / R`.
- Multimeter (10 MΩ) entlädt hochohmige RC-Glieder spürbar – für τ > 1 s mit grossem R ein Elektrometer oder Oszilloskop mit 10:1 nehmen.

## Grenzfälle
- R → 0: unendlich grosser Ladestrom im Modell – in Wirklichkeit begrenzen ESR, Leitungen und die Quelle (Einschaltstromstoss bei grossen Elkos!).
- Elko mit Leckstrom: lädt nie ganz voll, wenn R sehr gross ist (Spannungsteiler aus R und Leckwiderstand).
- Ladung bleibt nach dem Ausschalten erhalten – grosse Elkos über einen Entladewiderstand entladen (Berührungsschutz).
""",

    "tipps": [
        "Faustregel: Nach 5 τ ist der Vorgang praktisch fertig, nach 0.7 τ ist die Hälfte erreicht (ln 2).",
        "Power-on-Reset: Viele µC haben ihn eingebaut – ein externes RC am Reset-Pin braucht eine Diode zum schnellen Entladen beim Abschalten.",
    ],
    "fehler": [
        "τ in Sekunden mit 5 τ = „5 Sekunden“ verwechselt – τ hängt von R · C ab.",
        "Toleranz des Elkos vergessen – die Zeit streut leicht um ±50 %.",
        "Schaltschwelle ohne Hysterese: Bei langsamer Flanke schwingt der nachfolgende Eingang (Schmitt-Trigger verwenden).",
    ],
    "siehe_auch": ["rc_tiefpass_hochpass", "tasterentprellung", "rl_ein_ausschalten"],
    "rechner": ["rc_zeit", "rc_ladekurve", "energie_c"],
}
