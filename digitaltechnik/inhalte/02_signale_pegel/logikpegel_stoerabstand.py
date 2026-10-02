# Seite "Logikpegel und Störabstand"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Logikpegel, Störabstand und Pegelwandlung",
    "reihenfolge": 20,
    "kurz": "Ab welcher Spannung ist HIGH wirklich HIGH? Datenblattgrenzen, Störabstand und wann 3.3 V und 5 V zusammenpassen.",
    "stichworte": ["Logikpegel", "Pegel", "Störabstand", "Noise Margin", "U_OH", "U_OL", "U_IH", "U_IL", "TTL",
                   "CMOS", "74HC", "74HCT", "LVCMOS", "3.3 V", "5 V", "Pegelwandler", "Level Shifter", "5-V-tolerant"],

    "grafiken": ["werkzeug_logikpegel"],

    "erklaerung": """
## Grundlagen
Jede Logikfamilie garantiert im Datenblatt vier Grenzwerte:
- Ausgang: HIGH mindestens **U_OH,min**, LOW höchstens **U_OL,max** (bei einem bestimmten Laststrom!)
- Eingang: erkennt HIGH sicher ab **U_IH,min**, LOW sicher bis **U_IL,max**
- dazwischen: **undefiniert** – der Eingang kann beides erkennen oder schwingen (und CMOS-Eingänge ziehen dort Querstrom)

**Störabstand** (Noise Margin) = Reserve für Störungen auf der Leitung:
- `S_H = U_OH,min − U_IH,min`
- `S_L = U_IL,max − U_OL,max`
- beide müssen ≥ 0 sein, besser einige 100 mV.

Zusätzlich: Ein Eingang verträgt nur bis **U_E,max** (meist U_B + 0.3 … 0.5 V). Darüber leiten die Schutzdioden gegen U_B – Strom fliesst in die Versorgung des Empfängers, im schlimmsten Fall Latch-up.

## Vorgehen
1. Datenblatt von Sender und Empfänger: U_OH/U_OL (beim tatsächlichen Strom) und U_IH/U_IL (bei der tatsächlichen Versorgung).
2. S_H und S_L berechnen.
3. Spannungsfestigkeit prüfen: U_B(Sender) ≤ U_E,max(Empfänger)?
4. Wenn nicht passend:
   - 3.3 V → 5 V: Empfänger mit TTL-Eingang (74HCT, 74AHCT) – U_IH = 2.0 V
   - 5 V → 3.3 V: Spannungsteiler (langsame Signale), 5-V-toleranter Puffer (74LVC), Pegelwandler-IC
   - bidirektional (I²C): MOSFET-Pegelwandler (BSS138) oder spezielle ICs; Open-Drain mit Pull-ups auf jeder Seite
5. Gemeinsame Masse nicht vergessen.

## Beispiel
ESP32 (3.3 V) treibt 74HC bei 5 V:
- `S_H = 2.64 V − 3.15 V = −0.51 V` → HIGH wird **nicht sicher** erkannt
- Abhilfe 74HCT: `S_H = 2.64 V − 2.0 V = +0.64 V`, `S_L = 0.8 V − 0.33 V = +0.47 V` → passt

Arduino Uno (5 V) treibt ESP32-Eingang:
- 5 V > 3.6 V erlaubt → Pegelwandler nötig (z.B. Teiler 1 kΩ / 2 kΩ: 5 V → 3.33 V)

## Praxis
- TTL (74LS) ist veraltet, aber seine Schwellen (0.8 V / 2.0 V) leben als „TTL-kompatibel“ weiter (74HCT, LVTTL).
- CMOS-Schwellen hängen von der Versorgung ab (z.B. 0.3 · U_B / 0.7 · U_B) – bei 3.3 V andere Werte als bei 5 V.
- Offene CMOS-Eingänge nie offen lassen: Pull-up/-down, sonst undefiniert und Querstrom.
- Unter Last sinkt U_OH (Datenblatt-Tabelle beachten): Ein µC-Pin, der eine LED treibt, liefert vielleicht nur noch 2.5 V.
""",

    "tipps": [
        "Viele 3.3-V-µC haben 5-V-tolerante Pins (STM32: „FT“ im Datenblatt) – dann darf 5 V direkt an den Eingang.",
        "Schnelle Signale (SPI > 10 MHz) nicht über Spannungsteiler wandeln – die Eingangskapazität rundet die Flanken ab.",
    ],
    "fehler": [
        "Typische statt garantierte Werte verglichen – es funktioniert im Labor, aber nicht bei jedem Exemplar.",
        "5-V-Signal direkt an einen 3.3-V-Eingang – Schutzdioden speisen den 3.3-V-Zweig (Spannung steigt, Bauteil stirbt).",
        "Masse zwischen den Baugruppen vergessen – die Pegel haben keinen gemeinsamen Bezug.",
    ],
    "siehe_auch": ["analog_digital", "bitmasken"],
    "rechner": ["logikpegel", "spannungsteiler"],
}
