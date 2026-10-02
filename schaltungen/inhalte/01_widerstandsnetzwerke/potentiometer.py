# Seite "Potentiometer als Spannungsteiler"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Potentiometer als Teiler",
    "reihenfolge": 40,
    "kurz": "Einstellbarer Spannungsteiler – mit Last wird die Kennlinie krumm.",
    "stichworte": ["Potentiometer", "Poti", "Schleifer", "Trimmer", "einstellbarer Spannungsteiler",
                   "Lastfehler", "Kennlinie", "linear", "logarithmisch"],

    "grafiken": ["schaltung_poti"],

    "erklaerung": """
## Funktion
Ein Potentiometer ist ein Widerstand R_P mit einem **Schleifer**, der ihn in zwei Teile trennt: oben `(1 − α) · R_P`, unten `α · R_P` (α = Stellung 0 … 1). Es ist ein Spannungsteiler, dessen Verhältnis man drehen kann:
- unbelastet: `Ua = α · Ue`   (lineares Poti → gerade Kennlinie)
- belastet: R_L liegt parallel zum **unteren** Teil → `Ua = Ue · (α·R_P || R_L) / ((1 − α)·R_P + α·R_P || R_L)`

## Dimensionierung
1. **R_P im Verhältnis zur Last** wählen. Der grösste Fehler liegt bei ca. 2/3 Stellung und beträgt näherungsweise `ΔUa,max ≈ 4/27 · R_P / R_L · Ue ≈ 0.15 · R_P / R_L · Ue`. Mit `R_L ≥ 10 · R_P` bleibt er unter ca. 1.5 % von Ue.
2. **Strom und Leistung**: `I = Ue / R_P` fliesst dauernd. Belastbarkeit des Potis (oft nur 0.1 … 0.5 W) und vor allem des **Schleifers** (wenige mA!) beachten.
3. **Kennlinie** wählen: linear (B) für Spannungen/Sollwerte, logarithmisch (A) für Lautstärke (das Ohr empfindet logarithmisch).
4. Für feine Einstellung: Trimmer klein wählen und mit Festwiderständen in Reihe ergänzen (nur der nötige Bereich ist einstellbar).

## Betriebszustände
- **Unbelastet / hochohmige Last** (OPV-Eingang, ADC mit Puffer): Ua genau proportional zur Stellung.
- **Belastet**: Kennlinie „hängt durch“, an den Enden stimmt sie, dazwischen ist Ua zu klein.
- **Endstellungen**: α = 0 → Ua = 0, α = 1 → Ua = Ue – unabhängig von der Last.

## Messpunkte
- Schleifer gegen GND: Ua. Beim Drehen soll sie stetig, ohne Sprünge steigen – Aussetzer oder Kratzen deuten auf einen verschmutzten oder abgenutzten Schleifer.
- Gesamtwiderstand **ohne Spannung** zwischen den äusseren Anschlüssen messen: soll R_P ergeben, unabhängig von der Stellung.

## Grenzfälle
- `R_L → ∞`: ideale Gerade.
- `R_L ≪ R_P`: Ua bleibt fast überall klein und steigt erst kurz vor Anschlag steil an.
- Schleifer an den Anschlag bei kleiner Last: Der ganze Strom `Ue / R_L` fliesst über ein winziges Stück Widerstandsbahn und den Schleifer → Poti brennt durch. Abhilfe: Schutzwiderstand in Reihe zum Schleifer.
""",

    "tipps": [
        "Ein Spannungsfolger (OPV) hinter dem Schleifer macht die Last unendlich gross – die Kennlinie bleibt exakt linear.",
        "Poti als einstellbarer Widerstand (Rheostat): unbenutzten Anschluss mit dem Schleifer verbinden – bei Kontaktaussetzern ist dann nicht sofort der ganze Kreis offen.",
    ],
    "fehler": [
        "Poti als Vorwiderstand für eine Last mit grossem Strom (Motor, Lampe) – Schleifer und Bahn sind dafür nicht gemacht.",
        "Logarithmisches Poti für einen linearen Sollwert verwendet – die Einstellung wirkt fast nur am Ende.",
        "Last zu klein im Verhältnis zum Poti (R_L < 10 · R_P) – Anzeige/Einstellung stimmt nur an den Enden.",
    ],
    "siehe_auch": ["spannungsteiler"],
    "rechner": ["poti_last", "spannungsteiler"],
}
