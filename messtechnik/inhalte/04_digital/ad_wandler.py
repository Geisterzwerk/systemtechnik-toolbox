# Thema: AD-Wandler & Abtastung  (Messtechnik / Digital)
THEMA = {
    "titel": "AD-Wandler & Abtastung",
    "reihenfolge": 1,
    "kurz": "Wie ein analoges Signal zur Zahl wird: Auflösung, Abtastrate, Aliasing und die wichtigsten Wandlertypen.",
    "stichworte": ["adc", "ad-wandler", "a/d", "analog-digital", "analog digital wandler", "umsetzer", "dac",
                   "auflösung", "bit", "lsb", "quantisierung", "abtasttheorem", "nyquist", "shannon", "aliasing",
                   "anti-aliasing", "abtastrate", "samplerate", "sar", "delta-sigma", "sigma-delta", "dual-slope",
                   "flash", "enob", "snr", "referenzspannung", "sample and hold"],

    "steckbrief": {
        "zeilen": [
            ("Auflösung", "n Bit → 2ⁿ Stufen (12 Bit = 4096)"),
            ("1 LSB", "`Uref / 2ⁿ`  (kleinster Schritt, z.B. 3.3 V / 4096 ≈ 0.8 mV)"),
            ("Quantisierungsfehler", "± ½ LSB – unvermeidlich"),
            ("Abtasttheorem", "`fs > 2 · fmax` – sonst Aliasing"),
            ("Idealer Rauschabstand", "`SNR ≈ 6.02 · n + 1.76 dB`"),
        ],
    },

    "grafiken": ["abtastung"],

    "erklaerung": """
## Vom Signal zur Zahl
Ein AD-Wandler macht zwei Dinge:
- **Abtasten (zeitlich):** Er schaut nur zu bestimmten Zeitpunkten hin – `fs` Mal pro Sekunde. Ein **Abtast-Halte-Glied** friert den Wert kurz ein, während gewandelt wird.
- **Quantisieren (Wert):** Er teilt den Bereich 0 … Uref in 2ⁿ Stufen und gibt die Nummer der Stufe aus. Alles zwischen zwei Stufen geht verloren → **Quantisierungsfehler** von ± ½ LSB.
## Das Abtasttheorem (siehe Grafik oben)
Ein Signal kann nur dann korrekt rekonstruiert werden, wenn **mehr als zwei Abtastwerte pro Periode** der höchsten Frequenz vorliegen: `fs > 2 · fmax`. Die Grenze **fs/2** heisst Nyquist-Frequenz. Frequenzen darüber erscheinen **gespiegelt als falsche, tiefere Frequenz** (Aliasing) – und lassen sich hinterher nicht mehr vom echten Signal unterscheiden. Deshalb gehört vor jeden ADC ein **Anti-Aliasing-Tiefpass**. In der Praxis tastet man mit 2.5 … 10 × fmax ab.
## Auflösung ist nicht Genauigkeit
Ein 16-Bit-Wandler zeigt Schritte von 1/65536 – aber Rauschen, Offset, Verstärkungsfehler und eine ungenaue **Referenzspannung** bestimmen die tatsächliche Genauigkeit. Die **effektive Bitzahl (ENOB)** gibt an, wie viele Bits nach Abzug des Rauschens übrig bleiben.
## Die wichtigsten Wandlertypen
- **SAR (sukzessive Approximation):** vergleicht Bit für Bit wie eine Waage – schnell und genau, Standard in Mikrocontrollern (10–16 Bit, kHz … MHz)
- **Delta-Sigma:** tastet sehr schnell mit 1 Bit ab und filtert digital – sehr hohe Auflösung (16–24 Bit), eher langsam. Typisch für Wägezellen, Temperatur, Audio und Prozessmessgeräte.
- **Dual-Slope (Zweirampen):** integriert über eine feste Zeit – sehr störsicher gegen Netzbrumm, langsam. Klassisch in Digitalmultimetern.
- **Flash (parallel):** ein Komparator pro Stufe – extrem schnell, aber wenige Bits. Oszilloskope, Video.
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 6 (Abtast-Halte-Glied, Komparator, Parallel-, SAR-, Zweirampen- und Delta-Sigma-Umsetzer, Kenngrössen, Abtasttheorem, Quantisierungsrauschen, effektive Bitzahl), Kapitel 8 (Spektralanalyse, DFT, Fensterfunktionen).
""",

    "tabellen": [
        {
            "titel": "📊 Auflösung auf einen Blick",
            "kopf": ["Bit", "Stufen", "1 LSB bei 3.3 V", "1 LSB bei 5 V", "SNR ideal"],
            "zeilen": [
                ["8", "256", "12.9 mV", "19.5 mV", "49.9 dB"],
                ["10", "1'024", "3.22 mV", "4.88 mV", "62.0 dB"],
                ["12", "4'096", "806 µV", "1.22 mV", "74.0 dB"],
                ["16", "65'536", "50.4 µV", "76.3 µV", "98.1 dB"],
                ["24", "16'777'216", "0.197 µV", "0.298 µV", "146.2 dB"],
            ],
            "hinweis": "Manche Datenblätter rechnen mit Uref / (2ⁿ − 1) – der Unterschied ist bei vielen Bits vernachlässigbar.",
        },
    ],

    "tipps": [
        "**Referenzspannung ist alles:** Ein ADC ist nur so genau wie seine Referenz. Die Versorgungsspannung als Referenz schwankt oft um mehrere %.",
        "**Ratiometrisch messen:** Sensoren (Poti, Brücke, NTC-Teiler) mit derselben Spannung speisen, die auch Referenz ist – dann kürzen sich Schwankungen heraus.",
        "**Mitteln verbessert die Auflösung:** 4 Messungen mitteln ≈ 1 Bit mehr (Oversampling), sofern etwas Rauschen vorhanden ist.",
        "**Quellimpedanz beachten:** SAR-Wandler laden beim Abtasten einen kleinen Kondensator. Hochohmige Quellen (z.B. 100-kΩ-Teiler) brauchen einen Kondensator am Eingang oder einen Puffer-OPV.",
        "**Mittelwert über ganze Netzperioden** (20 ms bei 50 Hz) unterdrückt Netzbrumm – so machen es Multimeter und Prozessgeräte.",
    ],
    "fehler": [
        "Kein Anti-Aliasing-Filter → Störungen oberhalb fs/2 erscheinen als falsche, tiefe Frequenzen.",
        "Eingangsspannung über Uref oder unter GND → Überlauf oder Schaden am Eingang.",
        "Auflösung mit Genauigkeit verwechselt.",
        "Abtastrate nur doppelt so hoch wie die Signalfrequenz gewählt – das reicht in der Praxis nicht.",
    ],
    "siehe_auch": ["oszilloskop", "bruecke_dms", "temperatur", "messunsicherheit"],

    "rechner": ["adc", "abtastung"],
}
