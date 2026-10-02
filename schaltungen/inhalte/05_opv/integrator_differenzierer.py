# Seite "Integrator und Differenzierer"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Integrator und Differenzierer",
    "reihenfolge": 50,
    "kurz": "Mit C in der Gegenkopplung wird integriert, mit C im Eingang differenziert – Rechteck ↔ Dreieck.",
    "stichworte": ["Integrator", "Differenzierer", "Integrierer", "Differentiator", "Rampengenerator", "Dreieck",
                   "Rechteck", "R_p", "Drift", "Offset", "Funktionsgenerator", "PI-Regler", "aktives Filter"],

    "grafiken": ["schaltung_integrator"],

    "erklaerung": """
## Funktion
Beide Schaltungen sind invertierende Verstärker, bei denen ein Widerstand durch einen Kondensator ersetzt wird. Der − Eingang ist virtuelle Masse.

**Integrator** (R im Eingang, C in der Gegenkopplung): Der Eingangsstrom `Ue / R` lädt C.
- `Ua = −1 / (R · C) · ∫Ue dt`;  konstantes Ue → Rampe mit `dUa/dt = −Ue / (R · C)`
- Rechteck → Dreieck,  Sinus → Kosinus (−90°), Verstärkung `1 / (2π · f · R · C)` (Tiefpass mit −20 dB/Dekade)

**Differenzierer** (C im Eingang, R in der Gegenkopplung): Der Strom durch C ist `C · dUe/dt`.
- `Ua = −R · C · dUe/dt`;  Dreieck → Rechteck, Verstärkung `2π · f · R · C` (Hochpass, +20 dB/Dekade)

## Dimensionierung
1. Integrator: `τ = R · C` aus der gewünschten Steigung, z.B. Dreieck mit Spitze-Spitze `ΔU = Ue / (R · C) · T/2`.
2. **R_p parallel zu C** (Praxis): begrenzt die Gleichspannungsverstärkung auf `−R_p / R`, sonst wird jeder Offset (µV … mV) mitintegriert und der Ausgang läuft in die Begrenzung. Integriert wird erst über `f_u = 1 / (2π · R_p · C)` → R_p ≈ 10 … 100 · R.
3. Differenzierer: `R · C` aus der gewünschten Ausgangsamplitude, `|Ua| = R · C · dUe/dt`.
4. **R_s in Reihe zu C** (Praxis): begrenzt die Verstärkung hoher Frequenzen auf `R / R_s` (oberhalb `1 / (2π · R_s · C)`) – gegen Rauschen und Schwingen. Oft zusätzlich ein kleiner C parallel zu R.
5. Kondensator: Folie oder C0G (kein Elko – Leckstrom wirkt wie R_p, Toleranz gross).

## Betriebszustände
- **Integrator, Rechteck am Eingang**: Ausgang Dreieck; ohne R_p wandert das Dreieck mit jedem Offset langsam weg.
- **Integrator, Ue = 0 lange Zeit**: idealer Integrator hält den Wert (Speicher), realer driftet; mit R_p entlädt sich C über R_p.
- **Differenzierer, Dreieck am Eingang**: Ausgang Rechteck; an jedem Knick ein Sprung, mit R_s abgerundet.
- **Differenzierer, Rechteck am Eingang**: ideal unendlich hohe Spitzen → Ausgang schlägt an die Grenzen an.

## Messpunkte
- **M1** (Ausgang) und Eingang mit dem Oszilloskop: Steigung der Rampe = −Ue / (R · C) prüfen.
- Integrator ohne Signal: Ausgang beobachten – langsames Weglaufen = Offset × Zeit / (R · C).
- Rücksetzen für Messungen: Schalter (oder Transistor) parallel zu C entlädt den Integrator.

## Grenzfälle
- R_p → ∞: idealer Integrator, Gleichspannungsverstärkung = Leerlaufverstärkung → läuft weg.
- R_p → 0: kein Integrator mehr, nur noch invertierender Verstärker −R_p / R.
- f ≫ 1 / (2π · R · C) beim Differenzierer: Verstärkung wird riesig, GBW des OPV begrenzt sie und der Kreis kann schwingen.
- Anwendungen: Dreieck-/Rechteckgenerator (Integrator + Schmitt-Trigger), I-Anteil eines PI-Reglers, Ladungsverstärker.
""",

    "tipps": [
        "Integrator + Schmitt-Trigger im Kreis = Funktionsgenerator: Der Schmitt-Trigger liefert das Rechteck, der Integrator das Dreieck.",
        "Den Differenzierer braucht man selten – das passive RC-Hochpassglied genügt meistens, wenn keine Verstärkung nötig ist.",
    ],
    "fehler": [
        "Integrator ohne R_p oder Reset aufgebaut – nach kurzer Zeit klebt der Ausgang an der Versorgung.",
        "Differenzierer ohne R_s – rauscht stark oder schwingt.",
        "Vorzeichen vergessen: Beide Schaltungen invertieren (Rampe fällt bei positivem Ue).",
    ],
    "siehe_auch": ["rc_tiefpass_hochpass", "komparator_schmitt_trigger", "opv_verstaerker"],
    "rechner": ["integrator", "rc_frequenzgang"],
}
