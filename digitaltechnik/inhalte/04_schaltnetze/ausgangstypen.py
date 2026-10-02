# Seite "Ausgangstypen"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Ausgangstypen: Push-Pull, Open Drain, Tri-State",
    "reihenfolge": 40,
    "kurz": "Wie ein Ausgang die Leitung treibt – und welche Ausgänge man zusammenschalten darf (Bus, Wired-AND, I²C).",
    "stichworte": ["Push-Pull", "Totem-Pole", "Gegentakt", "Open Drain", "Open Collector", "Wired-AND",
                   "Tri-State", "hochohmig", "Z", "Bus", "Buskonflikt", "Pull-up", "I²C", "74HC125", "74HC244",
                   "TTL", "CMOS", "Anstiegszeit"],

    "grafiken": ["werkzeug_ausgang"],

    "erklaerung": """
## Grundlagen
- **Push-Pull** (Gegentakt, bei TTL „Totem-Pole“): ein Transistor nach U_B, einer nach GND. Treibt aktiv HIGH und LOW, schnelle Flanken. Zwei Push-Pull-Ausgänge an einer Leitung → bei verschiedenen Pegeln **Kurzschluss** (Buskonflikt).
- **Open Drain** (MOSFET) / **Open Collector** (bipolar): nur der Transistor nach GND. HIGH erzeugt ein **Pull-up**-Widerstand. Mehrere Ausgänge an einer Leitung sind erlaubt: **Wired-AND** – die Leitung ist nur HIGH, wenn ALLE loslassen. Anwendungen: I²C, Interrupt- und Reset-Leitungen, Pegelanpassung (Pull-up an eine andere Spannung).
- **Tri-State**: Push-Pull mit Freigabe (Output Enable). Gesperrt ist der Ausgang **hochohmig (Z)** und belastet die Leitung nicht – Grundlage von Datenbussen. Es darf immer nur EIN Treiber freigegeben sein.

TTL (bipolar) und CMOS unterscheiden sich in Pegeln, Eingangsströmen und Stromaufnahme – die Ausgangstypen gibt es bei beiden.

## Vorgehen
Pull-up für eine Open-Drain-Leitung (I²C):
1. `R_min = (U_B − U_OL,max) / I_OL` (I²C: U_OL ≤ 0.4 V bei 3 mA) – kleiner würde der Ausgang die Leitung nicht tief genug ziehen.
2. Buskapazität schätzen (≈ 10 pF pro Teilnehmer + Leitung ≈ 50 … 100 pF/m).
3. `R_max = t_r / (0.847 · C_Bus)` – t_r = Anstieg von 30 % auf 70 % (Standard-Mode 1000 ns, Fast-Mode 300 ns).
4. R zwischen R_min und R_max wählen (meist 2.2 … 10 kΩ); geht es nicht → langsamer Modus, Bus-Puffer, Stromquelle als Pull-up.

## Beispiel
I²C Fast-Mode, 3.3 V, 200 pF:
- `R_min = (3.3 V − 0.4 V) / 3 mA = 967 Ω`
- `R_max = 300 ns / (0.847 · 200 pF) = 1.77 kΩ` → z.B. 1.5 kΩ
- Mit den üblichen 4.7 kΩ: t_r ≈ 800 ns → nur für Standard-Mode (100 kHz) geeignet.

Buskonflikt zweier 74HC-Ausgänge bei 5 V (R_on ≈ 50 Ω je Transistor): `I ≈ 5 V / 100 Ω = 50 mA` – weit über dem zulässigen Ausgangsstrom.

## Praxis
- µC-Pins lassen sich meist als Push-Pull oder Open Drain konfigurieren (z.B. STM32 `GPIO_MODE_OUTPUT_OD`) – für I²C immer Open Drain.
- Bus-Treiber: 74HC125 (4 × Tri-State-Puffer), 74HC244/245 (8 Bit, 245 bidirektional für Datenbusse).
- Open-Drain-Pull-up an 5 V bei einem 3.3-V-µC nur, wenn der Pin 5-V-tolerant ist.
- Oszilloskop: Open-Drain-Leitungen zeigen schnelle fallende und langsame, abgerundete steigende Flanken (RC).
""",

    "tipps": [
        "Wired-AND ist praktisch für „irgendwer meldet Fehler“: Jeder Baustein darf die gemeinsame ¬INT-Leitung LOW ziehen.",
        "Kleinerer Pull-up = schnellere Flanken, aber mehr Strom bei LOW – immer ein Kompromiss.",
    ],
    "fehler": [
        "Zwei Push-Pull-Ausgänge direkt verbunden – bei verschiedenen Pegeln fliesst ein Kurzschlussstrom.",
        "I²C ohne Pull-ups aufgebaut – die Leitungen werden nie HIGH.",
        "Pull-up zu gross für Fast-Mode gewählt – die Flanken sind zu langsam, Daten werden falsch gelesen.",
    ],
    "siehe_auch": ["logikpegel_stoerabstand", "decoder_encoder"],
    "rechner": ["open_drain_pullup", "logikpegel", "pull_widerstand"],
}
