# Thema: Messunsicherheit & Auswertung  (Messtechnik / Grundlagen)
# Die Arten von Messabweichungen ausführlich: messabweichungen.py
THEMA = {
    "titel": "Messunsicherheit & Auswertung",
    "reihenfolge": 4,
    "kurz": "Kein Messwert ist exakt. Wie gross der Fehler ist, und wie man ihn angibt, rechnet und klein hält.",
    "stichworte": ["messfehler", "messunsicherheit", "fehler", "systematisch", "zufällig", "mittelwert",
                   "standardabweichung", "streuung", "student", "t-verteilung", "vertrauensbereich",
                   "fehlerfortpflanzung", "genauigkeit", "digits", "auflösung", "kalibrierung",
                   "worst case", "absoluter fehler", "relativer fehler", "toleranz", "präzision", "richtigkeit"],

    "steckbrief": {
        "zeilen": [
            ("Absoluter Fehler", "`F = Anzeige − wahrer Wert`  (in der Einheit der Messgrösse)"),
            ("Relativer Fehler", "`f = F / wahrer Wert`  (in %)"),
            ("Systematisch", "gleiche Richtung, wiederholbar → kann korrigiert werden"),
            ("Zufällig", "streut um den Mittelwert → wird durch Mitteln kleiner (∝ 1/√n)"),
            ("Ergebnis angeben", "`x = x̄ ± u`  (mit Vertrauensniveau, z.B. 95 %)"),
            ("Multimeter", "Genauigkeit meist als `±(p % vom Messwert + n Digits)`"),
        ],
    },

    "erklaerung": """
## Stell dir vor …
Vier Leute werfen Darts. Die erste trifft immer dicht beieinander, aber alles links unten – **präzise, aber nicht richtig** (systematischer Fehler). Der zweite verteilt die Pfeile wild um die Mitte – im Mittel **richtig, aber unpräzise** (zufällige Fehler). Die dritte trifft eng um die Mitte – **richtig und präzise**. Messen ist genauso: Man will beides, und muss ehrlich sagen, wie gross die Streuung ist.
## Warum ist kein Messwert exakt?
Jede Messung beeinflusst das Messobjekt und hat ein unvollkommenes Messgerät. Der „wahre Wert“ ist deshalb nie genau bekannt – man gibt an, **in welchem Bereich** er mit welcher Wahrscheinlichkeit liegt: das ist die **Messunsicherheit**.
## Die zwei Arten von Fehlern
Ausführlich mit allen Arten, Ursachen und einer interaktiven Messreihe: Seite **Messabweichungen (Messfehler)**.
- **Systematische Fehler** haben immer dieselbe Richtung und Grösse: falsch kalibriertes Gerät, Belastung durch den Innenwiderstand, Leitungswiderstand, Temperatureinfluss. Sind sie **bekannt**, rechnet man sie heraus (Korrektur). Sind sie **unbekannt**, gehen sie als Grenzwert in die Unsicherheit ein (z.B. Genauigkeitsangabe des Multimeters).
- **Zufällige Fehler** streuen: Rauschen, Ablesen, kleine Schwankungen. Misst man mehrmals, verteilen sich die Werte meist wie eine **Glockenkurve** (Normalverteilung) um den Mittelwert.
## Mehrere Messungen auswerten
- **Mittelwert** x̄: bester Schätzwert
- **Standardabweichung** s: wie stark ein einzelner Messwert streut
- **Unsicherheit des Mittelwerts** s/√n: wird mit mehr Messungen kleiner. Vierfache Anzahl Messungen = halbe Unsicherheit.
- Bei **wenigen** Messungen ist s selbst unsicher. Deshalb multipliziert man mit dem **Student-Faktor t** (bei 95 % und n = 5 z.B. t ≈ 2.8, bei vielen Messungen ≈ 1.96).
## Genauigkeit eines Multimeters lesen
Eine Angabe wie **±(0.5 % + 2 Digits)** bedeutet: 0.5 % vom angezeigten Wert **plus** 2 × die kleinste Stelle der Anzeige. Bei kleinen Werten im grossen Messbereich dominieren die Digits – darum immer den **kleinstmöglichen Messbereich** wählen.
## Fehlerfortpflanzung
Wird aus mehreren Messwerten etwas berechnet (z.B. P = U · I), pflanzen sich die Unsicherheiten fort:
- **Produkt / Quotient:** die **relativen** Fehler addieren sich
- **Summe / Differenz:** die **absoluten** Fehler addieren sich
- **Worst Case:** Beträge einfach addieren (sicher, aber pessimistisch)
- **Statistisch:** quadratisch addieren `√(a² + b²)` – realistisch, wenn die Fehler unabhängig sind
## Begriffe
- **Richtigkeit:** wie nahe der Mittelwert am wahren Wert liegt (systematisch)
- **Präzision:** wie eng die Werte beieinander liegen (zufällig)
- **Auflösung:** kleinste Änderung, die angezeigt wird – sagt NICHTS über die Genauigkeit!
## Beispiele durchgerechnet
**Multimeter-Genauigkeit:** Angabe ±(0.5 % + 2 Digits). Angezeigt werden 4.000 V im 6-V-Bereich (letzte Stelle = 1 mV):
- `0.5 % · 4.000 V = 20 mV`, dazu `2 · 1 mV = 2 mV` → **±22 mV**, der Wert liegt also zwischen 3.978 V und 4.022 V.
- Dieselbe Spannung im 60-V-Bereich zeigt 4.00 V (letzte Stelle = 10 mV): `20 mV + 2 · 10 mV = ±40 mV` – fast doppelt so unsicher.
**Messreihe:** Fünf Messungen ergeben 10.1, 10.3, 9.9, 10.2, 10.0 (in V).
- Mittelwert `x̄ = 10.10 V`, Standardabweichung `s ≈ 0.158 V`
- Unsicherheit des Mittelwerts `s / √5 ≈ 0.071 V`, mal Student-Faktor t ≈ 2.78 (95 %, n = 5) → **±0.20 V**
- Ergebnis: **U = (10.10 ± 0.20) V** mit 95 % Vertrauen
**Fehlerfortpflanzung:** P = U · I mit U ±1 % und I ±2 %. Worst Case: **±3 %**. Statistisch: `√(1² + 2²) ≈ ±2.2 %`.
## 🔬 Genauer hingeschaut
- **Der GUM:** International wird die Messunsicherheit nach dem „Guide to the Expression of Uncertainty in Measurement“ (GUM) angegeben. Er unterscheidet **Typ A** (statistisch aus Messreihen ermittelt) und **Typ B** (aus anderen Informationen: Datenblatt, Kalibrierschein, Erfahrung).
- **Grenzwerte umrechnen:** Steht im Datenblatt nur „±a“, nimmt man oft an, dass jeder Wert dazwischen gleich wahrscheinlich ist (Rechteckverteilung). Die Standardunsicherheit ist dann `u = a / √3`.
- **Erweiterte Unsicherheit:** Die kombinierte Standardunsicherheit u wird mit einem Erweiterungsfaktor multipliziert: `U = k · u`. Mit **k = 2** liegt der wahre Wert bei normalverteilten Grössen mit rund **95 %** Wahrscheinlichkeit im angegebenen Bereich. Auf Kalibrierscheinen steht darum oft „k = 2“.
- **Sinnvoll runden:** Die Unsicherheit wird auf ein bis zwei gültige Stellen gerundet, der Messwert auf dieselbe Stelle. „10.0973 ± 0.2 V“ täuscht eine Genauigkeit vor, die es nicht gibt.
## 💡 Wusstest du?
- **Kalibrieren** heisst: Abweichung gegenüber einer genaueren Referenz feststellen und dokumentieren. **Eichen** ist eine amtliche Prüfung im gesetzlichen Messwesen (z.B. Zapfsäulen, Ladenwaagen, Stromzähler). In der Schweiz ist dafür das Eidgenössische Institut für Metrologie **METAS** zuständig.
- Seit **2019** sind alle SI-Einheiten über Naturkonstanten festgelegt. Das Kilogramm hängt seither an der Planck-Konstante statt an einem Metallzylinder in einem Tresor bei Paris.
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 1.4 (Messfehler und Messunsicherheiten, Normalverteilung, Student'sche t-Verteilung, korrelierte Messgrössen).
""",

    "tabellen": [
        {
            "titel": "📊 Student-Faktor t (zweiseitig)",
            "kopf": ["Anzahl Messungen n", "t bei 68 %", "t bei 95 %", "t bei 99 %"],
            "zeilen": [
                ["2", "1.84", "12.71", "63.66"], ["3", "1.32", "4.30", "9.92"], ["5", "1.14", "2.78", "4.60"],
                ["10", "1.06", "2.26", "3.25"], ["20", "1.03", "2.09", "2.86"], ["sehr viele", "1.00", "1.96", "2.58"],
            ],
            "hinweis": "Bei wenigen Messungen ist t deutlich grösser – das „bestraft“ die geringe Datenbasis.",
        },
    ],

    "tipps": [
        "**Auflösung ≠ Genauigkeit:** Ein 6-stelliges Display kann trotzdem um 1 % daneben liegen. Die Genauigkeit steht im Datenblatt.",
        "**Kleinsten Messbereich wählen:** Die Digit-Anteile der Fehlerangabe sind im grossen Bereich viel grösser.",
        "**Differenzen sind heikel:** Die Differenz zweier fast gleicher Werte (z.B. 10.02 V − 10.00 V) kann einen riesigen relativen Fehler haben.",
        "**Mitteln hilft nur gegen Zufall:** Ein falsch kalibriertes Gerät liefert auch nach 1000 Messungen einen falschen Mittelwert.",
        "**Messmittel regelmässig kalibrieren** – und Kalibrierstatus prüfen, bevor man sich auf einen Wert verlässt.",
        "**Sinnvoll runden:** Die Unsicherheit mit 1–2 gültigen Stellen angeben, den Messwert auf dieselbe Stelle runden (z.B. 4.998 ± 0.012 V, nicht 4.99812 ± 0.0123 V).",
    ],
    "fehler": [
        "Messwert ohne Unsicherheit angegeben – eine Zahl allein sagt nichts über ihre Qualität.",
        "Standardabweichung eines einzelnen Werts mit der Unsicherheit des Mittelwerts verwechselt (Faktor √n).",
        "Bei wenigen Messungen mit 1.96 statt mit dem Student-Faktor gerechnet.",
        "Relative Fehler bei einer Summe addiert (dort addieren sich die absoluten).",
    ],
    "siehe_auch": ["messabweichungen", "begriffe", "multimeter", "signalkenngroessen"],

    "rechner": ["statistik", "dmm_genauigkeit", "fehlerfortpflanzung"],
}
