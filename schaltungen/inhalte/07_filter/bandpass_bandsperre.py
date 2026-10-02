# Seite "Bandpass und Bandsperre mit Schwingkreis"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Bandpass und Bandsperre (Reihenschwingkreis)",
    "reihenfolge": 20,
    "kurz": "R, L und C in Reihe: am R nur Frequenzen um f0 (Bandpass), an L + C alle ausser f0 (Bandsperre, Kerbfilter).",
    "stichworte": ["Bandpass", "Bandsperre", "Kerbfilter", "Notch", "Schwingkreis", "Reihenschwingkreis",
                   "RLC", "Resonanz", "Güte", "Bandbreite", "Grenzfrequenz", "Selektivität", "f0", "Q"],

    "grafiken": ["schaltung_schwingkreis"],

    "erklaerung": """
## Funktion
Im Reihenschwingkreis heben sich bei der Resonanzfrequenz die Blindwiderstände von L und C genau auf (`X_L = X_C`). Dann wirkt nur noch R:
- `f0 = 1 / (2π · √(L · C))`
- Güte `Q = Z0 / R = √(L / C) / R` – je kleiner R, desto schärfer die Resonanz
- Bandbreite `B = f0 / Q = R / (2π · L)` (zwischen den beiden −3-dB-Frequenzen)
- **Bandpass** – Ausgang am R: bei f0 ist `Ua = Ue`, darunter und darüber fällt der Ausgang mit 20 dB pro Dekade.
- **Bandsperre** – Ausgang an L + C: bei f0 ist die Reihenschaltung ein Kurzschluss → `Ua = 0`. Alle anderen Frequenzen kommen durch.

## Dimensionierung
1. Mittenfrequenz f0 und Bandbreite B (bzw. Güte `Q = f0 / B`) festlegen.
2. Ein Bauteil wählen (meist C aus der Normreihe), dann `L = 1 / ((2π · f0)² · C)`.
3. `R = Z0 / Q = √(L / C) / Q`. Der Drahtwiderstand der Spule und der Innenwiderstand der Quelle gehören schon zu R!
4. Die −3-dB-Frequenzen prüfen: `f_u,o = f0 · (√(1 + 4Q²) ∓ 1) / (2Q)` – für grosse Q ungefähr `f0 ∓ B/2`.
5. Spannungen beachten: Bei f0 liegt an L und an C je die **Q-fache** Eingangsspannung (Spannungsüberhöhung).

## Betriebszustände
- **f = f0**: Strom maximal (`I = Ue / R`), Bandpass Ua = Ue, Bandsperre Ua = 0, Phase 0° bzw. Sprung um 180°.
- **f < f0**: C überwiegt (kapazitiv), Strom eilt der Spannung vor.
- **f > f0**: L überwiegt (induktiv), Strom eilt nach.
- **Sprung am Eingang**: Bandpass zeigt eine abklingende Schwingung mit f0 – sie klingt umso langsamer ab, je grösser Q ist.

## Messpunkte
- **M1** (Ausgang) und Eingang mit dem Oszilloskop: Frequenz durchstimmen, bei Maximum (Bandpass) bzw. Minimum (Bandsperre) liegt f0.
- Bandbreite messen: die beiden Frequenzen suchen, bei denen der Bandpass-Ausgang 70.7 % des Maximums hat.
- Spannung an L oder C einzeln messen (Tastkopf 10:1): Sie ist bei f0 Q-mal so gross wie Ue – Spannungsfestigkeit prüfen.

## Grenzfälle
- R → 0: Q → ∞, unendlich schmale Resonanz – in der Praxis begrenzt der Drahtwiderstand der Spule.
- R sehr gross: Q < 0.5, es gibt keine ausgeprägte Resonanz mehr, der Bandpass wird sehr breit.
- Last am Ausgang: liegt parallel zum R (Bandpass) und senkt Q bzw. verschiebt die Kerbe.
- Reale Spule: Der Drahtwiderstand verhindert eine vollständige Auslöschung – die Bandsperre erreicht bei f0 nur endliche Dämpfung.
""",

    "tipps": [
        "Q gross = schmal und spitz, Q klein = breit und flach. Die Bandbreite hängt nur von R und L ab: B = R / (2π · L).",
        "Für tiefe Frequenzen (z.B. 50 Hz) werden L und C unhandlich gross – dort nimmt man aktive Filter oder ein Doppel-T-Glied.",
    ],
    "fehler": [
        "Drahtwiderstand der Spule und Innenwiderstand der Quelle vergessen – das tatsächliche Q ist viel kleiner als berechnet.",
        "Spannungsüberhöhung an L und C übersehen – Kondensatoren mit zu kleiner Nennspannung.",
        "Bandbreite mit der Grenzfrequenz verwechselt – B ist die Differenz der beiden −3-dB-Frequenzen.",
    ],
    "siehe_auch": ["lc_tiefpass", "aktive_filter_sallen_key", "rc_tiefpass_hochpass"],
    "rechner": ["schwingkreis_filter", "lc_resonanz"],
}
