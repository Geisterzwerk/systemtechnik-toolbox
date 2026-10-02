# Seite "Analoge und digitale Signale"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py
# Die Abtast-Grafik "abtastung" und der Rechner "adc" stammen aus der Messtechnik (nur wiederverwendet).

THEMA = {
    "titel": "Analoge und digitale Signale",
    "reihenfolge": 10,
    "kurz": "Wert- und zeitkontinuierlich gegen wert- und zeitdiskret – was beim Digitalisieren gewonnen wird und was verloren geht.",
    "stichworte": ["analog", "digital", "Signal", "zeitdiskret", "wertdiskret", "Abtastung", "Quantisierung",
                   "Auflösung", "Binärsignal", "Rauschen", "Regenerierung", "Taktsignal"],

    "grafiken": ["abtastung"],

    "erklaerung": """
## Grundlagen
- **Analoges Signal**: kann jeden Wert annehmen (wertkontinuierlich) und zu jedem Zeitpunkt (zeitkontinuierlich) – z.B. Mikrofon, Thermoelement.
- **Digitales Signal**: nur endlich viele Werte (wertdiskret) zu festen Zeitpunkten (zeitdiskret). Das **Binärsignal** kennt nur zwei Zustände: LOW (0) und HIGH (1).
- **Digitalisieren** = **Abtasten** (zeitdiskret machen, Abtastrate f_s) + **Quantisieren** (wertdiskret machen, Auflösung N Bit → `2^N` Stufen, `LSB = U_ref / 2^N`).
- Abtasttheorem: f_s > 2 · f_max, sonst Aliasing.

Warum digital?
- Ein Binärsignal darf verrauscht ankommen – solange die Störung kleiner als der Störabstand ist, wird es fehlerfrei erkannt und kann **regeneriert** werden (Kopie ohne Verlust).
- Verarbeitung, Speicherung und Übertragung mit Logik, µC und Speicher.
- Dafür: Quantisierungsfehler (±½ LSB) und eine begrenzte Bandbreite durch f_s.

## Vorgehen
1. Signal beschreiben: Bandbreite f_max, Spannungsbereich, nötige Genauigkeit.
2. Abtastrate wählen: f_s ≥ 2 · f_max, praktisch 5 … 10 · f_max, Anti-Aliasing-Filter davor.
3. Auflösung wählen: `LSB = U_ref / 2^N` muss kleiner als die nötige Genauigkeit sein (Rauschen beachten).
4. Pegel anpassen: Signal auf den Eingangsbereich des ADC verstärken bzw. teilen.

## Beispiel
Temperatursensor 0 … 3.3 V, gewünscht 1 mV Auflösung:
- `3.3 V / 2^N ≤ 1 mV` → `2^N ≥ 3300` → N = 12 Bit (4096 Stufen, LSB = 0.81 mV)
- Temperatur ändert sich langsam (< 1 Hz) → f_s = 10 Hz reicht, RC-Tiefpass gegen 50-Hz-Brumm.

## Praxis
- Ein digitaler Pin ist ein 1-Bit-„ADC“ mit Schaltschwellen (U_IL, U_IH) – siehe Logikpegel.
- Digitale Leitungen sind trotzdem analog: Flanken, Reflexionen, Übersprechen – bei schnellen Signalen (MHz) wichtig.
- Abtastung und Aliasing ausführlich: Bereich Messtechnik → „AD-Wandler“ und Schaltungen → „Anti-Aliasing-Tiefpass“.
""",

    "tipps": [
        "Faustregel Dynamik: Jedes Bit bringt 6 dB – 12 Bit ≈ 72 dB, 16 Bit ≈ 96 dB.",
    ],
    "fehler": [
        "Auflösung mit Genauigkeit verwechselt – ein 16-Bit-ADC mit schlechter Referenz misst nicht genauer.",
        "Abtastrate nur doppelt so hoch wie die Signalfrequenz gewählt – ohne steiles Filter gibt es Aliasing.",
    ],
    "siehe_auch": ["logikpegel_stoerabstand", "zahlensysteme_codes"],
    "rechner": ["adc", "zahlensystem"],
}
