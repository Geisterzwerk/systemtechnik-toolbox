# Seite "Quellenmodell"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Quellenmodell: Innenwiderstand und Anpassung",
    "reihenfolge": 10,
    "kurz": "Jede reale Quelle = ideale Quelle + Innenwiderstand. Daraus folgen Spannungseinbruch, Kurzschlussstrom und Leistungsanpassung.",
    "stichworte": ["Innenwiderstand", "Ersatzspannungsquelle", "Ersatzstromquelle", "Thevenin", "Norton",
                   "Klemmenspannung", "Leerlaufspannung", "Kurzschlussstrom", "Leistungsanpassung",
                   "Spannungsanpassung", "Stromanpassung", "Wirkungsgrad"],

    "grafiken": ["schaltung_quelle"],

    "erklaerung": """
## Funktion
Eine reale Quelle liefert nicht unbegrenzt Strom – ihre Spannung sinkt unter Last. Modell:
- **Ersatzspannungsquelle** (Thevenin): ideale Quelle U0 in Reihe mit R_i. Klemmenspannung `U_K = U0 − I · R_i = U0 · R_L / (R_i + R_L)`.
- **Ersatzstromquelle** (Norton): ideale Stromquelle I0 parallel zu R_i, mit `I0 = U0 / R_i`. Beide Modelle verhalten sich an den Klemmen identisch.
- Leerlauf (R_L → ∞): `U_K = U0`;  Kurzschluss (R_L = 0): `I_K = U0 / R_i`.

Drei Betriebsarten:
- **Spannungsanpassung** `R_L ≫ R_i`: U_K ≈ U0, hoher Wirkungsgrad – Netzteile, Batterien, Messgeräteeingänge.
- **Leistungsanpassung** `R_L = R_i`: grösste Leistung an der Last `P_max = U0² / (4 · R_i)`, aber nur 50 % Wirkungsgrad – HF-Technik, Antennen, Lautsprecher an Röhrenverstärkern.
- **Stromanpassung** `R_L ≪ R_i`: Strom ≈ I_K, fast unabhängig von der Last – Stromquellen.

## Dimensionierung
1. R_i bestimmen: Leerlaufspannung U0 messen, dann mit bekannter Last U_last messen: `R_i = (U0 − U_last) / I_last`.
2. Spannungseinbruch prüfen: Bei maximalem Laststrom muss `U0 − I · R_i` noch reichen (Batterie bei Kälte: R_i steigt!).
3. Leitungen und Steckverbinder gehören zum R_i dazu (2 × Leitungswiderstand).
4. Kurzschlussstrom `U0 / R_i` für Sicherung und Leitungsquerschnitt berücksichtigen (Akku: Hunderte Ampere!).

## Betriebszustände
- **Leerlauf**: kein Strom, U_K = U0, kein Verlust.
- **Nennlast**: U_K etwas kleiner, Verlust I² · R_i in der Quelle (Erwärmung).
- **Kurzschluss**: U_K = 0, I = U0 / R_i, die ganze Leistung wird in R_i umgesetzt.

## Messpunkte
- U0 hochohmig messen (Multimeter 10 MΩ), U_last unter bekannter Last – beide direkt an den Klemmen.
- Bei Akkus: kurzer Lastpuls (z.B. 1 s), sonst ändert sich U0 durch Entladung und Erwärmung.
- Bei Netzteilen mit Regelung ist R_i im Regelbereich fast 0 – erst an der Strombegrenzung bricht die Spannung ein.

## Grenzfälle
- R_i = 0 (ideale Spannungsquelle): U_K = U0 bei jeder Last, Kurzschlussstrom unendlich (gibt es nicht).
- R_i → ∞ (ideale Stromquelle): Strom fest, Spannung beliebig (Leerlauf → unendlich).
- Nichtlineare Quellen (Solarzelle, Akku bei tiefer Ladung): R_i ändert sich mit dem Arbeitspunkt – Kennlinie statt fester Wert.
""",

    "tipps": [
        "Jede lineare Schaltung aus Quellen und Widerständen lässt sich an zwei Klemmen durch U0 und R_i ersetzen (Satz von Thevenin) – praktisch für Spannungsteiler mit Last.",
        "Ein guter Akku hat wenige mΩ R_i – deshalb ist ein Akku-Kurzschluss so gefährlich.",
    ],
    "fehler": [
        "Leistungsanpassung bei einem Netzteil angestrebt – dabei verheizt die Quelle genauso viel wie die Last.",
        "U0 unter Last gemessen und für die Leerlaufspannung gehalten.",
        "Leitungswiderstand vergessen – bei 2 A über 2 m dünne Litze fehlen schnell 0.5 V an der Last.",
    ],
    "siehe_auch": ["netzteil_ungeregelt", "spannungsteiler", "geregelte_stromquelle"],
    "rechner": ["innenwiderstand", "ohm_leistung"],
}
