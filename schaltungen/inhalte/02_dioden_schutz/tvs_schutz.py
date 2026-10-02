# Seite "TVS-Schutz"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "TVS-Schutz gegen Spannungsspitzen",
    "reihenfolge": 70,
    "kurz": "Eine Suppressordiode klemmt kurze Überspannungen (Surge, Burst, ESD) auf eine verträgliche Spannung.",
    "stichworte": ["TVS", "Suppressordiode", "Transil", "Surge", "Burst", "ESD", "Überspannungsschutz",
                   "Stossspannung", "IEC 61000-4-5", "Klemmspannung"],

    "grafiken": ["schaltung_tvs"],

    "erklaerung": """
## Funktion
Eine TVS-Diode (Transient Voltage Suppressor) ist eine Z-Diode für sehr grosse, kurze Ströme. Sie liegt parallel zur geschützten Leitung:
- Im Betrieb sperrt sie (`U_B ≤ U_WM`, Stand-off-Spannung), es fliesst nur ein kleiner Leckstrom.
- Kommt eine Spitze, bricht sie ab **U_BR** (≈ 1.11 · U_WM) durch und leitet den Störstrom nach GND.
- Am Gerät bleibt die **Klemmspannung** `U_C = U_BR + I · r_d` stehen statt der vollen Spitze.

Den Strom begrenzt der **Innenwiderstand der Störquelle** (und eventuelle Leitungs-/Vorwiderstände): `I ≈ (U_peak − U_C) / R_q`. Die Prüfnorm IEC 61000-4-5 (Surge) nutzt 2 Ω zwischen den Leitungen und 12/42 Ω gegen Erde.

## Dimensionierung
1. `U_WM ≥ U_B,max` (Versorgungstoleranz einrechnen, z.B. 24 V + 10 % → U_WM ≥ 26.4 V).
2. `U_C` bei dem erwarteten Pulsstrom muss **unter der Spannungsfestigkeit** des Geräts (Regler, Kondensatoren, ICs) liegen.
3. **Pulsstrom** `I ≈ (U_peak − U_C) / R_q` muss unter I_PP aus dem Datenblatt liegen – für dieselbe Pulsform (meist 10/1000 µs; 8/20 µs-Werte sind höher).
4. **Unidirektional** für DC-Versorgungen (in Gegenrichtung leitet sie wie eine Diode, ≈ −1 V), **bidirektional** für Signale, die beide Polaritäten haben (AC, RS-485, Audio).
5. Für Datenleitungen: TVS-Arrays mit sehr kleiner Kapazität (wenige pF) – eine Leistungs-TVS hat einige 100 pF bis nF.

## Betriebszustände
- **Normalbetrieb**: TVS sperrt, Leckstrom µA (bei U_WM spezifiziert).
- **Störung**: TVS leitet für µs bis ms, Pulsleistung oft Hunderte Watt bis kW – nur kurzzeitig erlaubt.
- **Dauerüberspannung** (z.B. falsches Netzteil): TVS leitet dauernd und überhitzt – sie ist kein Überspannungsregler. Vorne eine Sicherung vorsehen.

## Messpunkte
- **M1** (geschützte Leitung) mit dem Oszilloskop bei einer Surge-/Burst-Prüfung: Spitze ≤ U_C.
- Leckstrom bei U_B: Spannung über einem Messwiderstand in Reihe – steigt er stark an, ist U_WM zu knapp gewählt.
- Nach einer starken Störung: TVS auf Kurzschluss prüfen (Ohmmeter) – defekte TVS schliessen meist kurz.

## Grenzfälle
- `U_B > U_WM`: TVS leitet schon im Betrieb, wird heiss und stirbt.
- Sehr energiereiche Störungen (Blitz, Netz): TVS allein reicht nicht → Stufenschutz mit Gasableiter/Varistor vorne, Entkopplung (Induktivität/Widerstand), TVS als Feinschutz.
- Lange Leitungen zur TVS: Ihre Induktivität (≈ 1 µH/m) lässt schnelle Spitzen durch – TVS direkt am Steckverbinder platzieren.
""",

    "tipps": [
        "Datenblatt-Kennzeichnung: SMBJ = 600 W, SMCJ = 1.5 kW (10/1000 µs); „A“-Typen haben engere U_BR-Toleranz, „CA“ = bidirektional.",
        "TVS kurz und breit an Masse anbinden – jeder Millimeter Leiterbahn erhöht die Klemmspannung bei schnellen Pulsen.",
        "Varistoren sind günstiger und vertragen mehr Energie, klemmen aber höher und altern – TVS für empfindliche Elektronik.",
    ],
    "fehler": [
        "U_WM gleich der Nennspannung gewählt – mit +10 % Toleranz leitet die TVS bereits im Betrieb.",
        "I_PP für 8/20 µs mit einem 10/1000-µs-Puls verglichen – die TVS ist dann viel zu klein.",
        "Unidirektionale TVS auf einer Signalleitung mit negativen Pegeln – das Signal wird bei −1 V abgeschnitten.",
        "Keine Sicherung vor der TVS – bei Dauerüberspannung brennt sie durch und schliesst kurz.",
    ],
    "siehe_auch": ["eingangsschutz", "verpolschutz", "diodenbegrenzung"],
    "rechner": ["tvs_auswahl", "kuehlkoerper"],
}
