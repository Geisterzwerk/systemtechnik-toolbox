# Seite "ADC-Eingang beschalten"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Schutz vor Überspannung: Seite "eingangsschutz" (02_dioden_schutz); Aliasing: "anti_aliasing_filter" (04_rc_rl).

THEMA = {
    "titel": "ADC-Eingang beschalten und schützen",
    "reihenfolge": 50,
    "kurz": "Warum ein hochohmiger Sensor am µC-ADC falsch misst – Abtastkondensator, C_ext am Pin, Schutz und Filter.",
    "stichworte": ["ADC-Eingang", "Abtastkondensator", "Sample and Hold", "SAR-ADC", "Quellimpedanz",
                   "Quellwiderstand", "Abtastzeit", "Sampling Time", "C_ext", "Ladungsteilung", "Kickback",
                   "ADC-Schutz", "Klemmdiode", "Analogeingang", "µC-ADC"],

    "grafiken": ["schaltung_adc_eingang"],

    "erklaerung": """
## Stell dir vor …
Ein ADC misst wie jemand, der mit einem **kleinen Becher** kurz Wasser aus einem Fass schöpft und dann den Füllstand im Becher abliest. Ist der Zulauf zum Fass zu dünn (hochohmige Quelle), ist der Becher nach der kurzen Zeit noch nicht voll – der Messwert ist zu klein. Ein Kondensator am Pin ist ein grosser Vorratskrug direkt daneben, aus dem der Becher sofort voll wird.
## Funktion
Ein SAR-ADC (in fast jedem µC) misst nicht dauernd. Er verbindet beim **Abtasten** für die Zeit t_s einen kleinen Kondensator C_S (einige pF) über einen Schalter (R_sw ≈ 1 kΩ) mit dem Pin. C_S hat noch die Spannung der letzten Messung und muss bis auf **½ LSB** an die Eingangsspannung herankommen.
- **Ohne externen Kondensator** lädt C_S über Quelle + R_sw: Fehler `≈ ΔU · e^(−t_s / τ)`, `τ = (R_Quelle + R_sw) · C_S`. Für ½ LSB braucht es `ln(2^(N+1))` Zeitkonstanten (12 Bit: 9 τ).
- **Mit C_ext direkt am Pin** liefert dieser die Ladung sofort (Ladungsteilung). Er muss gross genug sein: `C_ext ≥ (2^(N+1) − 1) · C_S` (12 Bit, 10 pF: ≥ 82 nF). Danach lädt die Quelle C_ext langsam nach → zusammen ein Tiefpass `fg = 1 / (2π · R · C_ext)`.

## Dimensionierung
1. Abtastzeit t_s und C_S aus dem µC-Datenblatt (oft einstellbar, z.B. 1.5 … 640 ADC-Takte).
2. Ohne C_ext: `R_Quelle ≤ t_s / (C_S · ln 2^(N+1)) − R_sw` (Rechner „ADC-Eingang“). Sonst t_s verlängern oder Quelle puffern (OPV-Folger).
3. Mit C_ext: Kondensator ≥ (2^(N+1) − 1) · C_S direkt am Pin (C0G/X7R), und die Abtastrate so niedrig, dass R · C_ext zwischen zwei Messungen nachladen kann.
4. Schutz: Serienwiderstand (begrenzt den Strom durch die internen Klemmdioden auf < 1 … 5 mA) – er zählt aber zum Quellwiderstand!
5. Anti-Aliasing: R und C_ext bilden gleichzeitig den Tiefpass vor dem ADC.

## Betriebszustände
- **Quelle niederohmig** (z.B. OPV-Ausgang): C_S lädt schnell, kein Problem.
- **Quelle hochohmig ohne C_ext** (z.B. 100-kΩ-Teiler): Messwerte zu klein bzw. abhängig vom vorher gemessenen Kanal („Übersprechen“).
- **Mit C_ext, langsame Abtastung**: genau.
- **Mit C_ext, schnelle Abtastung**: C_ext lädt nicht nach → Messwert sinkt mit steigender Abtastrate.

## Messpunkte
- Testen: Zwei Kanäle abwechselnd messen (einer auf 0 V, einer auf dem Signal). Ändert sich der Wert gegenüber Einzelmessung → Quelle zu hochohmig.
- Abtastzeit verdoppeln: Ändert sich der Messwert, ist C_S nicht fertig geladen.
- Mit dem Oszilloskop am Pin: kleine Einbrüche (Kickback) bei jeder Abtastung.

## Grenzfälle
- Sehr grosse Widerstände (MΩ, z.B. Spannungsteiler für hohe Spannungen): nur mit grossem C_ext oder Puffer-OPV.
- Überspannung am Pin: Klemmdioden leiten in die Versorgung → Messwerte anderer Kanäle verfälscht (Injektionsstrom).
- Sehr schnelle Signale: C_ext begrenzt die Bandbreite – dann treibender OPV mit kleinem R-C-Filter nach Datenblatt.
## 🔬 Genauer hingeschaut
- **Mehrere Kanäle, ein Wandler:** Die meisten µC haben nur einen ADC und schalten die Pins über einen Multiplexer um. Im Abtastkondensator bleibt etwas Ladung vom vorherigen Kanal – bei hochohmigen Quellen „sieht“ ein Kanal dann den Nachbarn (Übersprechen). Abhilfe: Kondensator an jedem Pin oder eine Wandlung verwerfen.
- **Mitteln hilft gegen Rauschen:** Mehrere Messungen mitteln verkleinert zufälliges Rauschen um den Faktor √n. Gegen einen systematischen Fehler (zu hoher Quellwiderstand) hilft Mitteln aber nicht.
- **Referenz nicht vergessen:** Der Messwert ist immer relativ zur Referenzspannung. Ist sie die verrauschte Versorgung, ist auch der Messwert verrauscht.
## 💡 Wusstest du?
- Das Datenblatt des ATmega328P (Arduino Uno) empfiehlt für seinen ADC eine Quellimpedanz von höchstens 10 kΩ – genau die Faustregel aus den Tipps.
""",

    "tipps": [
        "Faustregel für 12-Bit-µC-ADCs: Quellwiderstand ≤ 10 kΩ, sonst 100 nF direkt an den Pin und langsam abtasten.",
        "Ein OPV als Spannungsfolger vor dem ADC löst fast alle Probleme – der OPV muss aber schnell genug sein.",
    ],
    "fehler": [
        "Hochohmigen Spannungsteiler (z.B. 1 MΩ) ohne Kondensator an den ADC – die Messwerte sind zu klein und schwanken.",
        "Kleinen Kondensator (z.B. 1 nF) am Pin gewählt – Ladungsteilung grösser als ½ LSB.",
        "Schutzwiderstand nachträglich vergrössert, ohne die Abtastzeit anzupassen.",
    ],
    "siehe_auch": ["eingangsschutz", "anti_aliasing_filter", "ntc_spannungsteiler", "opv_verstaerker"],
    "rechner": ["adc_eingang", "eingangsschutz", "adc"],
}
