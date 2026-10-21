# Seite "DMS-Brücke mit Instrumentenverstärker"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Brücke und DMS allein: Rechner "bruecke", "dms" (messtechnik/rechner.py); Instrumentenverstärker: Seite
# "differenz_instrumentenverstaerker" (05_opv).

THEMA = {
    "titel": "DMS-Brücke mit Instrumentenverstärker",
    "reihenfolge": 30,
    "kurz": "Wägezelle, Kraft, Dehnung: wenige Millivolt aus der Brücke sauber auf den ADC-Bereich verstärken.",
    "stichworte": ["DMS", "Dehnungsmessstreifen", "Wägezelle", "Load Cell", "Kraftaufnehmer", "Brücke",
                   "Wheatstone", "Instrumentenverstärker", "INA128", "AD620", "INA333", "HX711", "mV/V",
                   "Nennkennwert", "Viertelbrücke", "Halbbrücke", "Vollbrücke", "Gleichtakt"],

    "grafiken": ["schaltung_dms_kette"],

    "erklaerung": """
## Stell dir vor …
Du willst messen, wie stark sich eine dicke Stahlplatte unter einem Gewicht verbiegt – die Änderung ist kleiner als ein Haar breit. Der DMS macht daraus eine Widerstandsänderung von Promille, die Brücke daraus wenige Millivolt, und der Messverstärker ist die **Lupe**, die diese Millivolt so gross macht, dass ein ADC sie lesen kann.
## Funktion
Ein Dehnungsmessstreifen ändert seinen Widerstand nur sehr wenig: `ΔR / R = k · ε` (k ≈ 2, ε = Dehnung). Bei 1000 µm/m sind das 0.2 %.
Die Wheatstone-Brücke macht daraus eine kleine Differenzspannung:
- **Viertelbrücke** (1 aktiver DMS): `U_d = U_e · x / (4 + 2x)` mit x = ΔR/R – leicht nichtlinear
- **Halbbrücke** (2 aktive DMS mit +ε und −ε): `U_d = U_e · x / 2`
- **Vollbrücke** (4 aktive DMS, Wägezellen): `U_d = U_e · x`

Wägezellen geben einen **Nennkennwert** an, z.B. 2 mV/V: Bei 5 V Speisung und Nennlast entstehen 10 mV.
Diese Differenz „schwimmt“ auf der halben Speisespannung (Gleichtakt U_e/2). Ein **Instrumentenverstärker** verstärkt nur die Differenz: `U_aus = REF + G · U_d`, mit `G = 1 + R_intern / R_G` (INA128: 50 kΩ, AD620: 49.4 kΩ).

## Dimensionierung
1. Signal bei Nennlast: `U_d = Kennwert · U_e` (z.B. 2 mV/V · 5 V = 10 mV).
2. Gewünschte Ausgangsspanne festlegen (ADC-Bereich minus Reserve), dann `G = U_a / U_d`.
3. `R_G = R_intern / (G − 1)` und den nächst **grösseren** Normwert wählen (G etwas kleiner → keine Übersteuerung).
4. REF: 0 V, wenn nur eine Richtung gemessen wird; sonst Mitte des ADC-Bereichs über einen Puffer (REF braucht eine niederohmige Quelle).
5. Gleichtaktbereich prüfen: U_e/2 muss im zulässigen Eingangsbereich des Verstärkers liegen (bei 5-V-Single-Supply kritisch).
6. Ratiometrisch: Brückenspeisung = ADC-Referenz (oder Sense-Leitungen bei 6-Leiter-Wägezellen).
7. Fertige Lösung: 24-Bit-ADC mit eingebautem Verstärker (z.B. HX711) – der Grundgedanke bleibt gleich.

## Betriebszustände
- **Unbelastet**: U_d ≈ 0 (Offset der Zelle wenige % des Nennsignals → Tara in der Software).
- **Zug/Druck**: U_aus wandert von REF nach oben bzw. unten.
- **Überlast**: Ausgang läuft in die Begrenzung (Grafik: waagrechter Teil) – Messwert friert ein.
- **Temperaturänderung**: Viertelbrücke driftet, Halb- und Vollbrücke kompensieren (alle DMS erwärmen sich gleich).

## Messpunkte
- Brückenspeisung U_e direkt an der Zelle messen (Spannungsabfall auf langen Leitungen!).
- U_d unbelastet und mit bekanntem Gewicht (Kalibrierung: zwei Punkte, Nullpunkt und Steigung).
- **M1** (Ausgang) gegen REF: sollte G · U_d sein.
- Brückenwiderstände ohne Speisung: Eingang–Eingang und Ausgang–Ausgang je ≈ Nennwiderstand (z.B. 350 Ω / 1000 Ω).

## Grenzfälle
- G zu gross: schon kleine Lasten treiben den Ausgang in die Begrenzung.
- Gleichtakt ausserhalb des erlaubten Bereichs: Ausgang falsch, obwohl die Rechnung stimmt.
- Lange Leitungen ohne Sense: Spannungsabfall an den Speiseleitungen verkleinert U_e an der Zelle.
- Störungen (50 Hz): verdrillte, geschirmte Leitungen, Tiefpass vor dem ADC, Mittelwertbildung.
## 🔬 Genauer hingeschaut
- **Wie fein muss der ADC sein?** Eine Wägezelle mit 2 mV/V an 5 V liefert bei Nennlast 10 mV. Soll die Waage 3000 Schritte anzeigen, muss sie etwa 3.3 µV auflösen. Darum verwendet man meist Delta-Sigma-Wandler mit 24 Bit und eingebautem Verstärker (z.B. HX711 in vielen Bastel-Waagen).
- **Ratiometrisch messen:** Hängen Brückenspeisung und ADC-Referenz an derselben Spannung, kürzen sich deren Schwankungen heraus – die Speisung muss dann nicht besonders genau sein.
- **Kriechen:** Unter dauernder Last ändert sich das Signal einer Wägezelle über Minuten leicht. Gute Zellen geben dieses Kriechen im Datenblatt an.
## 💡 Wusstest du?
- Eine Fahrzeugwaage für Lastwagen besteht aus mehreren Wägezellen unter einer Plattform. Ihre Signale werden zusammengezählt – so spielt es keine Rolle, wo das Fahrzeug genau steht.
""",

    "tipps": [
        "Halb- oder Vollbrücke verwenden, wo es geht: doppeltes bzw. vierfaches Signal und automatische Temperaturkompensation.",
        "Erst den Nullpunkt (Tara), dann mit einem bekannten Gewicht die Steigung kalibrieren.",
        "Ein OPV-Differenzverstärker aus 4 Widerständen reicht hier nicht: Die Brücke ist zu hochohmig und die Widerstandstoleranz ruiniert die Gleichtaktunterdrückung.",
    ],
    "fehler": [
        "REF an einen hochohmigen Spannungsteiler gelegt – die Verstärkung stimmt nicht mehr (REF braucht einen Puffer).",
        "Gleichtaktbereich des Instrumentenverstärkers nicht geprüft – bei 5 V Single Supply läuft der Eingang in die Begrenzung.",
        "R_G auf den nächst kleineren Normwert gerundet – bei Nennlast übersteuert der Ausgang.",
    ],
    "siehe_auch": ["differenz_instrumentenverstaerker", "wheatstone_bruecke", "pt100_leiterschaltung"],
    "rechner": ["dms_verstaerker", "dms", "bruecke"],
}
