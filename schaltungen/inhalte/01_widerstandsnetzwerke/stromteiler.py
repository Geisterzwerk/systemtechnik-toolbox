# Seite "Stromteiler"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Stromteiler",
    "reihenfolge": 20,
    "kurz": "Parallele Widerstände teilen einen Strom auf – umgekehrt zu ihren Widerstandswerten.",
    "stichworte": ["Stromteiler", "Parallelschaltung", "Knotenregel", "current divider", "Shunt", "Zweigstrom"],

    "grafiken": ["schaltung_stromteiler"],

    "erklaerung": """
## Funktion
Alle parallelen Zweige liegen an **derselben Spannung** U. Nach dem Ohm'schen Gesetz fliesst durch jeden Zweig `I_k = U / R_k`. Die Summe der Zweigströme ist wieder der Gesamtstrom (**Knotenregel**, 1. Kirchhoff'sches Gesetz):
- `I = I1 + I2 + …`
- `I1 / I2 = R2 / R1`   (der kleinere Widerstand bekommt den grösseren Strom)
- zwei Zweige: `I1 = I · R2 / (R1 + R2)`   (Achtung: im Zähler steht der ANDERE Widerstand)

## Dimensionierung
1. Gesamtstrom I und gewünschte Aufteilung festlegen, z.B. I1 = 99 %, I2 = 1 %.
2. Verhältnis: `R1 / R2 = I2 / I1`.
3. Gesamtwiderstand `R_ges = R1 || R2` bestimmt die Spannung `U = I · R_ges` – sie fehlt dem Rest der Schaltung.
4. Leistung je Zweig: `P_k = U² / R_k` (der Zweig mit dem kleinsten Widerstand wird am heissesten).

Beispiel Messbereichserweiterung: Ein Messwerk (100 µA, 1 kΩ) soll 1 A messen. Der Shunt muss 999.9 mA übernehmen: `R_S = Ri · Iv / (I − Iv) = 0.1 Ω` (Rechner Messtechnik → Messbereich).

## Betriebszustände
- **Normalbetrieb**: Aufteilung fest durch das Widerstandsverhältnis, unabhängig von der Grösse des Gesamtstroms.
- **Ein Zweig unterbrochen**: Der ganze Strom fliesst durch den anderen Zweig – bei einer Stromquelle steigt die Spannung.
- **Ein Zweig kurzgeschlossen**: Der ganze Strom fliesst durch den Kurzschluss, die anderen Zweige sind stromlos.

## Messpunkte
- Zweigströme mit dem Amperemeter **in Reihe** zum Zweig messen – oder stromlos über die Spannung: `I_k = U / R_k` (U parallel messen, R bekannt).
- Probe: gemessene Zweigströme addieren → muss I ergeben.
- Bei sehr kleinen Shunts: Spannung direkt an den Shunt-Anschlüssen abgreifen (4-Leiter-Messung), sonst verfälschen Leitungs- und Kontaktwiderstände.

## Grenzfälle
- `R1 = R2`: Strom teilt sich halb/halb.
- `R2 → ∞`: I1 = I (Zweig 2 wirkt wie nicht vorhanden).
- `R2 → 0`: I2 = I, I1 = 0.
- Parallele LEDs/Dioden teilen den Strom **nicht** gleichmässig – kleine Unterschiede in U_F ergeben grosse Stromunterschiede (exponentielle Kennlinie).
""",

    "tipps": [
        "Merkhilfe: Strom nimmt den Weg des geringsten Widerstands – aber nicht NUR diesen; er teilt sich im Verhältnis der Leitwerte G = 1/R auf.",
        "Mit Leitwerten rechnet es sich am einfachsten: I_k = I · G_k / (G1 + G2 + …).",
    ],
    "fehler": [
        "Formel verwechselt: I1 = I · R2 / (R1 + R2) – nicht R1 im Zähler.",
        "LEDs ohne eigene Vorwiderstände parallel geschaltet – eine LED übernimmt fast den ganzen Strom und brennt durch.",
        "Shunt-Leistung vergessen: P = I² · R_S – bei 10 A und 10 mΩ sind das schon 1 W.",
    ],
    "siehe_auch": ["spannungsteiler"],
    "rechner": ["stromteiler", "reihe_parallel", "messbereich"],
}
