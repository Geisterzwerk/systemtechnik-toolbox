# Seite "LC-Tiefpass"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "LC-Tiefpass",
    "reihenfolge": 10,
    "kurz": "Spule in Reihe, Kondensator parallel zur Last: −40 dB pro Dekade fast ohne Verlust – aber mit Resonanz.",
    "stichworte": ["LC-Tiefpass", "LC-Filter", "Filter 2. Ordnung", "Güte", "Q", "Resonanz", "Überhöhung",
                   "Kennwiderstand", "Z0", "Ausgangsfilter", "Schaltregler-Filter", "Netzfilter", "-40 dB",
                   "Dämpfung", "Butterworth"],

    "grafiken": ["schaltung_lc_filter"],

    "erklaerung": """
## Funktion
Die Spule L lässt tiefe Frequenzen durch und sperrt hohe (`X_L = 2π·f·L`), der Kondensator C schliesst hohe Frequenzen nach Masse kurz (`X_C = 1/(2π·f·C)`). Zusammen ergibt das ein Filter **2. Ordnung**:
- Resonanzfrequenz `f0 = 1 / (2π · √(L · C))`
- Kennwiderstand `Z0 = √(L / C)`
- Güte mit der Last R_L parallel zum C: `Q = R_L / Z0 = R_L · √(C / L)`
- Über f0 fällt der Ausgang mit **40 dB pro Dekade** (Faktor 100 pro Faktor 10 in der Frequenz) – doppelt so steil wie ein RC-Glied.

Anders als beim RC-Tiefpass fällt im Durchlass fast keine Spannung ab (nur der Drahtwiderstand der Spule) – darum filtert man so **Leistung**: Ausgang von Schaltreglern, Netzfilter, Audio-Frequenzweichen.

## Dimensionierung
1. f0 festlegen: deutlich unter der Störfrequenz (z.B. Schaltfrequenz), deutlich über dem Nutzsignal.
2. Die Dämpfung bei der Störfrequenz f abschätzen: weit über f0 gilt `|H| ≈ (f0 / f)²` → eine Dekade = 40 dB.
3. Güte festlegen: `Q = 0.707` (Butterworth) ist maximal flach → `Z0 = R_L / 0.707`.
4. Aus f0 und Z0: `L = Z0 / (2π · f0)` und `C = 1 / (2π · f0 · Z0)`.
5. Spule nach Strom auslegen (Sättigungsstrom > Spitzenstrom) und Kondensator nach Rippelstrom (ESR).
6. Schwankt die Last, schwankt Q: bei kleiner Last (grosses R_L) wird Q gross → Dämpfungswiderstand (R in Reihe zu einem zusätzlichen C) vorsehen.

## Betriebszustände
- **f ≪ f0**: Ausgang ≈ Eingang, Phase ≈ 0°.
- **f = f0**: `|H| = Q`, Phase −90°. Bei Q > 1 ist der Ausgang **grösser** als der Eingang!
- **f ≫ f0**: `|H| ≈ (f0 / f)²`, Phase → −180°.
- **Sprung am Eingang** (Einschalten): Bei Q > 0.5 schwingt der Ausgang über – Butterworth 4.3 %, Q = 1 schon 16 %, ohne Last fast 100 % (doppelte Spannung!).
- **Leerlauf** (R_L → ∞): Q → ∞, ungedämpfter Schwingkreis.

## Messpunkte
- **M1** (Ausgang) zusammen mit dem Eingang am Oszilloskop: Amplitudenverhältnis und Phase über der Frequenz → Bode-Diagramm.
- Rechteck mit kleiner Frequenz einspeisen: Das Nachschwingen am Ausgang zeigt f0 (Periodendauer) und Q (Anzahl sichtbarer Schwingungen ≈ Q).
- Bei Schaltreglern: Rippel am Ausgang mit kurzer Massefeder messen, nicht mit der langen Krokodilklemme (sonst misst man Einstreuung).

## Grenzfälle
- R_L sehr klein: Q < 0.5, das Filter wird träge und dämpft schon unter f0.
- R_L sehr gross (Leerlauf): starke Überhöhung bei f0 – eine Störung genau bei f0 wird verstärkt statt gedämpft.
- Spule gesättigt: L bricht ein, f0 steigt, die Filterwirkung verschwindet.
- Weit oberhalb von f0: Eigenkapazität der Spule und ESL des Kondensators – das Filter wird wieder durchlässig (Eigenresonanz).
""",

    "tipps": [
        "Faustregel: Q ≈ R_L / Z0. Für Q = 0.707 muss die Last etwa 0.7 · Z0 sein.",
        "Mit dem Schalter „Sprungantwort“ sieht man sofort, ob das Filter beim Einschalten überschwingt.",
        "Bei LC-Filtern am Eingang von Schaltreglern auf die Stabilität achten: Der negative Eingangswiderstand des Reglers kann ein schwach gedämpftes Filter zum Schwingen bringen.",
    ],
    "fehler": [
        "Filter ohne Last berechnet – in der Praxis ist Q dann sehr hoch und die Spannung bei f0 überhöht.",
        "Spule nur nach Induktivität gewählt, nicht nach Strom – sie geht in Sättigung.",
        "f0 zu nah an der Störfrequenz gelegt – die Dämpfung reicht nicht (oder es gibt sogar Resonanz).",
    ],
    "siehe_auch": ["rc_tiefpass_hochpass", "bandpass_bandsperre", "aktive_filter_sallen_key", "schaltregler_buck_boost"],
    "rechner": ["lc_filter", "lc_resonanz", "blindwiderstand_c"],
}
