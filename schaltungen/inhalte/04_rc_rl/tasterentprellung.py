# Seite "Tasterentprellung"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Taster entprellen (RC + Schmitt-Trigger)",
    "reihenfolge": 30,
    "kurz": "Ein Taster prellt einige Millisekunden – RC-Glied und Schmitt-Trigger machen daraus genau eine Flanke.",
    "stichworte": ["Entprellung", "Prellen", "Debounce", "Taster", "Schmitt-Trigger", "74HC14", "Hysterese",
                   "Pull-up", "Kontaktprellen", "Interrupt"],

    "grafiken": ["schaltung_entprellung"],

    "erklaerung": """
## Funktion
Mechanische Kontakte federn beim Schliessen und Öffnen zurück: Für ≈ 0.1 … 10 ms (alte oder billige Taster bis 20 ms) wechselt der Kontakt mehrmals zwischen offen und geschlossen. Ein schneller Eingang (µC, Zähler, Interrupt) zählt jeden Wechsel.

**Hardware-Entprellung**: Pull-up R1 zieht den Knoten auf U_B, der Taster nach GND. Über R2 hängt ein Kondensator am Eingang:
- Drücken: C entlädt über R2, `τ_ab = R2 · C`
- Loslassen: C lädt über R1 + R2, `τ_auf = (R1 + R2) · C`
- Die kurzen Prell-Pausen ändern die Kondensatorspannung kaum.
- Ein **Schmitt-Trigger** (z.B. 74HC14, viele µC-Eingänge) hat zwei Schwellen U_T+ und U_T− (Hysterese) – die langsame Flanke schaltet ihn nur einmal.

## Dimensionierung
1. Prellzeit t_prell aus dem Datenblatt (oder messen), typisch 5 ms ansetzen.
2. R1 (Pull-up) 4.7 … 47 kΩ, R2 ≈ R1 / 2 … R1 (begrenzt den Entladestrom über den Kontakt).
3. Zeit bis zur Schwelle mindestens so lang wie das Prellen:
   - `t_ab = R2 · C · ln(U_B / U_T−) ≥ t_prell`
   - `t_auf = (R1 + R2) · C · ln(U_B / (U_B − U_T+)) ≥ t_prell`
4. `C = t_prell / (R2 · ln(U_B / U_T−))` → nächster Normwert nach oben (z.B. 10 kΩ / 4.7 kΩ / 1 µF bei 5 ms).
5. Eingang MIT Hysterese verwenden – ohne Schmitt-Trigger kann die langsame Flanke den Eingang schwingen lassen.

## Betriebszustände
- **Ruhe** (offen): C auf U_B geladen, Schmitt-Trigger-Ausgang (invertierend) LOW.
- **Drücken**: C entlädt sich trotz Prellen stetig, nach t_ab wird U_T− unterschritten → Ausgang HIGH.
- **Halten**: C bleibt bei 0 V.
- **Loslassen**: C lädt über R1 + R2, nach t_auf wird U_T+ überschritten → Ausgang wieder LOW.

## Messpunkte
- Prellen sichtbar machen: Oszilloskop direkt am Taster (Knoten zwischen R1 und Taster), Single-Shot-Trigger auf die erste Flanke, Zeitbasis 1 ms/div.
- **M1** (am C): saubere e-Kurven ohne Sprünge über die Schwellen.
- Ausgang des Schmitt-Triggers: genau eine Flanke pro Betätigung.

## Grenzfälle
- R2 = 0: C wird beim ersten Kontakt schlagartig entladen – hoher Stromstoss über den Kontakt (Verschleiss), und die Entprellung beim Drücken wirkt nur noch über die Hysterese.
- C zu gross: spürbare Verzögerung (> 50 ms fühlt sich träge an), kurze Tastendrücke gehen verloren.
- C zu klein: Prellen kommt durch – mehrere Flanken.
- **Software-Entprellung** (häufigste Lösung bei µC): Pin alle 1 … 5 ms abfragen und erst nach mehreren gleichen Werten (≈ 10 … 20 ms) übernehmen – spart Bauteile, belegt aber Rechenzeit/Timer.
""",

    "tipps": [
        "Bei Interrupt-Eingängen ist Hardware-Entprellung oft besser: Ein prellender Taster löst sonst Dutzende Interrupts aus.",
        "Drehgeber (Encoder) prellen ebenso – dort hilft ein RC mit kleinem τ plus Auswertung im Zustandsautomaten.",
        "Umschalter (Wechsler) lassen sich ohne RC mit einem RS-Flipflop perfekt entprellen.",
    ],
    "fehler": [
        "RC-Glied an einen normalen Eingang ohne Hysterese – die langsame Flanke erzeugt wieder mehrere Umschaltungen.",
        "R2 weggelassen – der Kondensator entlädt sich als Funke über den Kontakt.",
        "Nur das Drücken entprellt – auch beim Loslassen prellt der Kontakt.",
    ],
    "siehe_auch": ["pull_up_down", "rc_laden_entladen"],
    "rechner": ["entprellung", "pull_widerstand", "rc_zeit"],
}
