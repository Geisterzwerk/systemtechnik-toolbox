# Seite "Pegelwandler"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Logikpegel und Störabstände: Digitaltechnik "logikpegel_stoerabstand"; I²C: Digitaltechnik "i2c".

THEMA = {
    "titel": "Pegelwandler 5 V ↔ 3.3 V",
    "reihenfolge": 10,
    "kurz": "Verschiedene Logikspannungen verbinden: Teiler für eine Richtung, N-MOSFET für bidirektionale Leitungen wie I²C.",
    "stichworte": ["Pegelwandler", "Level Shifter", "Pegelumsetzer", "5 V", "3.3 V", "BSS138", "bidirektional",
                   "I²C", "Spannungsteiler", "TXS0108", "74LVC", "5-V-tolerant", "Logikpegel"],

    "grafiken": ["schaltung_pegelwandler"],

    "erklaerung": """
## Funktion
Ein 5-V-Ausgang an einem 3.3-V-Eingang treibt Strom über die Schutzdioden in die 3.3-V-Versorgung – der Baustein kann Schaden nehmen. Umgekehrt erkennt ein 5-V-CMOS-Eingang (V_IH = 0.7 · 5 V = 3.5 V) ein 3.3-V-HIGH nicht sicher.
- **Spannungsteiler** (nur 5 V → 3.3 V): `U = 5 V · R2 / (R1 + R2)`. Mit der Eingangskapazität entsteht ein Tiefpass: `t_r = 2.2 · (R1 ∥ R2) · C`.
- **N-MOSFET** (bidirektional, Open Drain): Gate an 3.3 V, Source an der 3.3-V-Seite (A), Drain an der 5-V-Seite (B), beide Seiten mit Pull-up.
  - Ruhe: `U_GS = 0`, MOSFET sperrt, jede Seite liegt über ihren Pull-up auf ihrem HIGH.
  - A zieht LOW: `U_GS = 3.3 V` → MOSFET leitet → B wird LOW.
  - B zieht LOW: Die Body-Diode zieht A auf ≈ 0.6 V, dann ist `U_GS > U_th` → Kanal leitet → A wird LOW.
- **Pegelwandler-IC**: 74LVC/74LVC1T45 (mit Richtungseingang) für schnelle Push-Pull-Signale, TXS/TXB-Typen automatisch.

## Dimensionierung
Teiler:
1. R1 wählen (1 … 10 kΩ), `R2 = R1 · U_Ziel / (U_hoch − U_Ziel)` (5 V → 3.3 V: 10 kΩ / 20 kΩ).
2. Anstiegszeit prüfen: Für schnelle Signale (SPI mit MHz) kleinere Widerstände.

MOSFET-Wandler:
1. MOSFET mit kleinem `U_GS(th)` (z.B. BSS138: max. 1.5 V) – die niedrige Spannung muss deutlich darüber liegen.
2. Pull-ups wie bei I²C (z.B. 4.7 … 10 kΩ, Rechner „Pull-up für Open Drain / I²C“).
3. Anstieg: `t_r = 2.2 · R · C` je Seite – begrenzt die Frequenz auf einige 100 kHz.

## Betriebszustände
- **Beide frei**: A = U_A, B = U_B, MOSFET aus.
- **A zieht LOW**: B folgt fast auf 0 V (nur R_on · I).
- **B zieht LOW**: A folgt über Diode + Kanal.
- **Beide ziehen LOW**: kein Problem (Open Drain) – das nutzt I²C für Arbitrierung und Clock Stretching.

## Messpunkte
- Beide Seiten gleichzeitig mit dem Oszilloskop: LOW-Pegel (< 0.4 V) und die Anstiegsflanken prüfen.
- Gate-Spannung = U_A messen.
- Teiler: HIGH-Pegel am 3.3-V-Eingang sollte zwischen 0.7 · 3.3 V und 3.3 V + 0.3 V liegen.

## Grenzfälle
- U_A zu klein für den MOSFET (z.B. 1.8 V mit U_th = 1.5 V): Kanal leitet nicht sicher.
- Push-Pull-Signal mit hoher Frequenz über den MOSFET-Wandler: Die Pull-ups sind zu langsam → IC-Wandler nehmen.
- Teiler in Gegenrichtung (3.3 V → 5 V): funktioniert nicht.
- Viele Pull-ups parallel (mehrere Module mit eigenen Pull-ups): zu kleiner Gesamtwiderstand, LOW wird nicht erreicht.
""",

    "tipps": [
        "Viele 3.3-V-µC haben „5-V-tolerante“ Pins (im Datenblatt mit FT markiert) – dann reicht ggf. ein Serienwiderstand.",
        "Für I²C ist der MOSFET-Wandler Standard (Philips-Applikation AN10441), für SPI eher ein 74LVC-Puffer.",
    ],
    "fehler": [
        "MOSFET-Wandler für schnelle Push-Pull-Signale verwendet – Flanken werden durch die Pull-ups langsam.",
        "Gate an die hohe statt an die niedrige Spannung angeschlossen.",
        "5-V-Ausgang direkt an einen nicht 5-V-toleranten 3.3-V-Eingang.",
    ],
    "siehe_auch": ["pull_up_down", "eingangsschutz", "optokoppler_schaltung"],
    "rechner": ["pegelteiler", "open_drain_pullup", "logikpegel"],
}
