# Seite "Aktive Filter 2. Ordnung (Sallen-Key)"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Aktive Filter 2. Ordnung (Sallen-Key)",
    "reihenfolge": 30,
    "kurz": "Tief- und Hochpass 2. Ordnung ohne Spule: OPV als Spannungsfolger, zwei R, zwei C – die Charakteristik über Q wählen.",
    "stichworte": ["Sallen-Key", "aktives Filter", "Aktivfilter", "Butterworth", "Bessel", "Tschebyscheff",
                   "Chebyshev", "Güte", "Q", "Filter 2. Ordnung", "Tiefpass 2. Ordnung", "Hochpass 2. Ordnung",
                   "Anti-Aliasing", "Polfrequenz", "Überschwingen", "OPV-Filter"],

    "grafiken": ["schaltung_sallen_key"],

    "erklaerung": """
## Funktion
Zwei RC-Glieder hintereinander, dahinter ein OPV als Spannungsfolger (Verstärkung 1). Der Trick: Das **erste Bauteil** führt nicht nach Masse, sondern zum **Ausgang** (Mitkopplung). Damit lässt sich die Güte Q einstellen.
- `f0 = 1 / (2π · √(R1 · R2 · C1 · C2))`
- Tiefpass: `Q = √(R1R2C1C2) / (C2 · (R1 + R2))` – mit R1 = R2: `Q = ½ · √(C1 / C2)`
- Hochpass: `Q = √(R1R2C1C2) / (R1 · (C1 + C2))` – mit C1 = C2: `Q = ½ · √(R2 / R1)`
- Über f0 (Tiefpass) bzw. unter f0 (Hochpass): **40 dB pro Dekade**

Die Charakteristik hängt nur von Q ab:
- **Q = 0.5** – kritisch gedämpft: kein Überschwingen, aber −3 dB schon bei 0.64 · f0
- **Bessel, Q = 0.577** – fast konstante Laufzeit, Rechtecke bleiben sauber (0.4 % Überschwingen), −3 dB bei 0.79 · f0
- **Butterworth, Q = 0.707** – maximal flach, −3 dB genau bei f0, 4.3 % Überschwingen
- **Tschebyscheff 1 dB, Q = 0.956** – steiler, 1 dB Welligkeit im Durchlass, 14.6 % Überschwingen

## Dimensionierung
Tiefpass (gleiche Widerstände R):
1. f0 und Q wählen, R zwischen 1 kΩ und 100 kΩ festlegen.
2. `C1 = 2Q / (2π · f0 · R)` (zum Ausgang), `C2 = 1 / (2Q · 2π · f0 · R)` (nach Masse).
3. Auf Normwerte runden, f0 und Q nachrechnen (Rechner „Sallen-Key-Filter auslegen“).

Hochpass (gleiche Kondensatoren C):
1. C wählen.
2. `R1 = 1 / (2Q · 2π · f0 · C)` (zum Ausgang), `R2 = 2Q / (2π · f0 · C)` (nach Masse).

OPV auswählen:
- Verstärkungs-Bandbreite-Produkt `GBW ≥ 100 · Q · f0`
- Slew-Rate reicht für die grösste Ausgangsamplitude bei f0

Höhere Ordnungen entstehen durch Hintereinanderschalten (z.B. 4. Ordnung = 2 Stufen mit verschiedenen Q aus einer Tabelle).

## Betriebszustände
- **Durchlass**: Verstärkung 1 (0 dB), Phase ≈ 0°.
- **f = f0**: `|H| = Q`, Phase −90° (Tiefpass) bzw. +90° (Hochpass).
- **Sperrbereich**: −40 dB pro Dekade, Phase → −180° bzw. +180°.
- **Sprung am Eingang**: Überschwingen je nach Q (Schalter „Sprungantwort“ in der Grafik).
- **OPV in der Begrenzung**: Bei grossen Signalen und hohem Q wird die Überhöhung bei f0 abgeschnitten – Verzerrungen.

## Messpunkte
- **M1** (Ausgang) und Eingang am Oszilloskop: Amplitudenverhältnis bei f0 = Q (Kontrolle der Güte).
- Rechteck einspeisen: Überschwingen ablesen und mit der Tabelle oben vergleichen (zeigt falsche C-Werte sofort).
- Weit im Sperrbereich (Tiefpass, z.B. 100 · f0): Durchgriff prüfen – siehe Grenzfälle.

## Grenzfälle
- C1 / C2 bzw. R2 / R1 sehr gross: Q wird gross, das Filter wird zum Resonator und kann bei Toleranzen schwingen.
- Toleranzen: Q reagiert empfindlich auf die Verhältnisse – Kondensatoren mit 1 … 5 % (C0G/NP0) verwenden, keine Elkos oder X7R.
- Tiefpass weit über f0: Der Ausgangswiderstand des OPV steigt, ein Teil des Signals kommt über C1 direkt durch – die Dämpfung bleibt bei einem endlichen Wert stehen.
- Quelle mit Innenwiderstand: addiert sich zu R1 (Tiefpass) – f0 und Q verschieben sich.
""",

    "tipps": [
        "Butterworth für allgemeine Filter, Bessel, wenn die Kurvenform (z.B. Rechteck, Puls) erhalten bleiben soll.",
        "Mit R1 = R2 = 10 kΩ, C1 = 22 nF, C2 = 11 nF (E24) ergibt sich ein Butterworth-Tiefpass bei 1.02 kHz.",
        "Vor einem ADC (Anti-Aliasing) bringt ein Sallen-Key-Tiefpass 40 dB pro Dekade statt 20 dB beim RC-Glied.",
    ],
    "fehler": [
        "C1 und C2 vertauscht – aus Q = 0.707 wird Q = 0.35, das Filter dämpft schon weit unter f0.",
        "Keramikkondensatoren X7R verwendet – ihre Kapazität ändert sich mit Spannung und Temperatur, Q und f0 wandern.",
        "OPV mit zu kleinem GBW gewählt – f0 und Q stimmen nicht mehr, die Überhöhung wächst.",
        "Eingang des OPV ohne Gleichstrompfad (Hochpass ohne R2 nach Masse) – der Ausgang driftet in die Begrenzung.",
    ],
    "siehe_auch": ["rc_tiefpass_hochpass", "lc_tiefpass", "anti_aliasing_filter", "opv_verstaerker"],
    "rechner": ["sallen_key", "rc_frequenzgang"],
}
