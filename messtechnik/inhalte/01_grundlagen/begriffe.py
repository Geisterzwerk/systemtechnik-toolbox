# Thema: Begriffe der Messtechnik  (Messtechnik / Grundlagen)
# Quellen: DIN 1319-1 (Grundbegriffe) und VIM (Internationales Wörterbuch der Metrologie), wie zitiert in den
# Wikipedia-Artikeln „Messabweichung“, „Messeinrichtung“, „Messumformer“, „Kalibrierung“, „Genauigkeitsklasse“.
THEMA = {
    "titel": "Begriffe der Messtechnik",
    "reihenfolge": 1,
    "kurz": "Messgrösse, Messwert, Messergebnis, Auflösung, Kalibrieren, Justieren, Eichen … – was die Fachwörter genau bedeuten.",
    "stichworte": ["begriffe", "grundbegriffe", "din 1319", "vim", "messgrösse", "messwert", "messergebnis",
                   "wahrer wert", "richtiger wert", "messprinzip", "messmethode", "messverfahren", "messbereich",
                   "messspanne", "auflösung", "empfindlichkeit", "genauigkeitsklasse", "kalibrieren", "justieren",
                   "eichen", "rückführbarkeit", "normal", "hysterese", "linearität", "drift", "nullpunkt",
                   "ausschlagmethode", "kompensationsmethode", "einflussgrösse", "rückwirkung"],

    "steckbrief": {
        "zeilen": [
            ("Norm (deutsch)", "DIN 1319 „Grundlagen der Messtechnik“, Teil 1: Grundbegriffe"),
            ("International", "VIM – Internationales Wörterbuch der Metrologie (JCGM 200)"),
            ("Messen heisst", "eine Grösse mit einer **Einheit** vergleichen: `Messwert = Zahlenwert · Einheit`"),
            ("Ergebnis angeben", "`x = Messwert ± Unsicherheit`, z.B. `U = 4.98 V ± 0.05 V`"),
            ("Wichtigste Unterscheidung", "**Kalibrieren** (nur feststellen) ≠ **Justieren** (einstellen) ≠ **Eichen** (gesetzlich)"),
        ],
    },

    "erklaerung": """
## Stell dir vor …
Du misst mit einem Massband die Länge eines Tisches. Schon in diesem einfachen Vorgang stecken fast alle Begriffe der Messtechnik: Die **Länge** ist die Messgrösse, das Massband die Messeinrichtung, „1.20 m“ der Messwert – und weil das Band etwas durchhängt und du schräg abliest, ist der Wert nicht ganz exakt. Damit sich alle über solche Dinge genau verständigen können, sind die Begriffe in der **DIN 1319** und international im **VIM** festgelegt.
## Was beim Messen passiert
Messen heisst, eine Grösse mit einer festgelegten **Einheit** zu vergleichen. Das Ergebnis ist immer ein **Zahlenwert mal Einheit**: 1.20 m, 4.98 V, 23.5 °C.
- **Messgrösse:** die Grösse, die man wissen will (Länge, Spannung, Temperatur …).
- **Messobjekt:** das Ding, an dem gemessen wird (Tisch, Batterie, Rohrleitung).
- **Messwert:** der Wert, den die Messeinrichtung ausgibt.
- **Messergebnis:** der aus einer oder mehreren Messungen gewonnene Schätzwert – vollständig erst **zusammen mit der Messunsicherheit**.
- **Einflussgrösse:** etwas, das nicht gemessen werden soll, das Ergebnis aber verändert (Umgebungstemperatur, Störfelder, Versorgungsspannung).
## Wahrer Wert und richtiger Wert
- Der **wahre Wert** ist der Wert, den die Messgrösse tatsächlich hat. Er ist ein gedachter Idealwert und **nie genau bekannt**.
- Der **richtige Wert** ist ein bekannter Vergleichswert, dessen Abweichung vom wahren Wert vernachlässigbar ist – zum Beispiel der Wert einer Referenzspannungsquelle mit Kalibrierschein.
- Die **Messabweichung** (früher „Messfehler“) ist die Differenz zwischen Messwert und Referenzwert – mehr dazu auf der Seite „Messabweichungen“.
## Prinzip, Methode, Verfahren
- **Messprinzip:** die physikalische Grundlage. Beispiel: Der Widerstand von Platin steigt mit der Temperatur.
- **Messmethode:** die Art des Vorgehens, unabhängig vom Gerät. Bei der **Ausschlagmethode** wird der Messwert direkt angezeigt (Zeiger, Display). Bei der **Kompensationsmethode** (Nullabgleich) wird eine bekannte Grösse so lange verstellt, bis sie die Messgrösse genau aufhebt – wie bei einer abgeglichenen Brückenschaltung oder einer Balkenwaage.
- **Messverfahren:** die konkrete praktische Anwendung, z.B. „Temperatur mit Pt100 in Vierleiterschaltung messen“.
## Kenngrössen einer Messeinrichtung
- **Messbereich:** der Bereich, in dem die zugesicherten Fehlergrenzen gelten. **Messspanne** = Endwert − Anfangswert (z.B. 0 … 250 °C → Spanne 250 K).
- **Auflösung:** die kleinste Änderung, die noch angezeigt wird (z.B. 0.01 V bei „4.98 V“). Sie sagt **nichts** über die Genauigkeit!
- **Empfindlichkeit:** wie stark der Ausgang auf eine Änderung am Eingang reagiert: `E = ΔAusgang / ΔEingang`. Ein Pt100 ändert sich zwischen 0 und 100 °C im Mittel um 0.385 Ω pro Kelvin.
- **Genauigkeitsklasse:** bei Zeigerinstrumenten (DIN EN 60051) die Fehlergrenze in Prozent vom **Messbereichsendwert**. Klasse 1 im Bereich 0 … 100 mA heisst: höchstens ±1 mA Abweichung – überall im Bereich.
- **Fehlergrenze:** die vom Hersteller zugesicherte grösste Abweichung (ohne Vorzeichen).
## 🔬 Genauer hingeschaut
- **Klassenangabe richtig lesen:** Weil sich die Klasse auf den Endwert bezieht, ist die Abweichung im unteren Bereich relativ gross. Klasse 1, Bereich 100 mA: bei 100 mA höchstens 1 %, bei 25 mA aber bis zu 4 % des Messwerts. Darum den Messbereich so wählen, dass der Zeiger möglichst weit ausschlägt.
- **Kennlinienfehler:** Eine echte Kennlinie weicht ab von der idealen Geraden: **Nullpunktabweichung** (Kennlinie verschoben), **Steigungsabweichung** (zu steil oder zu flach), **Linearitätsabweichung** (gekrümmt), **Hysterese** (steigend und fallend gemessen ergeben verschiedene Werte), **Drift** (langsame Änderung mit der Zeit).
- **Rückwirkung:** Jede Messeinrichtung entzieht dem Messobjekt etwas Energie und verändert es dadurch ein wenig – ein Spannungsmesser belastet die Schaltung, ein Thermometer kühlt oder erwärmt das Medium.
- **Rückführbarkeit:** Ein Messergebnis ist rückführbar, wenn es über eine ununterbrochene Kette von Kalibrierungen mit den SI-Einheiten verbunden ist – bis zu den nationalen **Normalen** (in der Schweiz beim METAS). Mit jedem Glied der Kette wird die Unsicherheit etwas grösser.
## Kalibrieren, Justieren, Eichen
Diese drei Wörter werden im Alltag oft verwechselt – in der Messtechnik bedeuten sie etwas ganz Verschiedenes:
- **Kalibrieren:** Die Abweichung des Geräts gegenüber einem Normal wird **festgestellt und dokumentiert** (Kalibrierschein). Am Gerät wird **nichts verändert**.
- **Justieren:** Das Gerät wird **eingestellt**, damit die Abweichung möglichst klein wird. Danach braucht es eine neue Kalibrierung – die alte gilt nicht mehr.
- **Eichen:** eine **gesetzlich vorgeschriebene** Prüfung für Messgeräte im amtlichen oder geschäftlichen Verkehr (z.B. Waagen im Laden, Zapfsäulen). In der Schweiz regelt das Bundesamt für Metrologie (METAS) die Eichpflicht.
## 💡 Wusstest du?
- Früher sprach man von „Messfehlern“. Die DIN 1319 sagt heute **Messabweichung**, weil eine Abweichung kein Fehler im Sinne von „falsch gemacht“ ist – jede Messung hat eine.
- Seit 2019 sind alle SI-Basiseinheiten über feste **Naturkonstanten** definiert. Das Kilogramm hängt damit nicht mehr am Urkilogramm, einem Metallzylinder in Sèvres bei Paris, sondern an der Planck-Konstante.
""",

    "tabellen": [
        {
            "titel": "📊 Begriffe auf einen Blick",
            "kopf": ["Begriff", "Bedeutung", "Beispiel"],
            "zeilen": [
                ["Messgrösse", "Grösse, deren Wert ermittelt werden soll", "Spannung einer Batterie"],
                ["Messwert", "vom Messgerät ausgegebener Wert", "4.98 V"],
                ["Messergebnis", "Schätzwert + Messunsicherheit", "4.98 V ± 0.05 V"],
                ["wahrer Wert", "tatsächlicher Wert – nie genau bekannt", "–"],
                ["richtiger Wert", "bekannter Vergleichswert, Abweichung zum wahren Wert vernachlässigbar", "Referenzquelle 5.000 V"],
                ["Messabweichung", "Messwert − Referenzwert", "4.98 V − 5.000 V = −0.02 V"],
                ["Messunsicherheit", "Bereich, in dem der Wert vernünftigerweise liegt", "± 0.05 V"],
                ["Auflösung", "kleinste angezeigte Änderung", "0.01 V"],
                ["Messbereich", "Bereich mit zugesicherten Fehlergrenzen", "0 … 20 V"],
                ["Empfindlichkeit", "ΔAusgang / ΔEingang", "Pt100: ≈ 0.385 Ω/K"],
                ["Genauigkeitsklasse", "Fehlergrenze in % vom Endwert (Zeigerinstrumente)", "Klasse 1.5"],
                ["Kalibrieren", "Abweichung feststellen und dokumentieren", "Kalibrierschein"],
                ["Justieren", "Gerät einstellen, Abweichung verkleinern", "Nullpunkt nachstellen"],
                ["Eichen", "gesetzlich vorgeschriebene Prüfung", "Waage im Laden"],
            ],
        },
    ],

    "tipps": [
        "**Ein Messwert ohne Unsicherheit ist unvollständig:** „4.98 V“ allein sagt nicht, ob die zweite Nachkommastelle stimmt. „4.98 V ± 0.05 V“ schon.",
        "**Viele Stellen ≠ genau:** Ein Gerät mit 6½ Stellen Anzeige kann trotzdem eine schlechtere Genauigkeit haben als eines mit 4 Stellen – das Datenblatt entscheidet.",
        "**Kalibrierschein lesen:** Er nennt die Abweichung UND die Unsicherheit der Kalibrierung – ist die Abweichung bekannt, kann man sie vom Messwert abziehen.",
    ],
    "fehler": [
        "„Das Gerät ist kalibriert, also misst es richtig“ – Kalibrieren stellt die Abweichung nur fest, es korrigiert nichts.",
        "Auflösung mit Genauigkeit verwechselt.",
        "Genauigkeitsklasse auf den Messwert statt auf den Messbereichsendwert bezogen.",
        "Kalibrieren und Eichen gleichgesetzt – Eichen ist eine gesetzliche Pflicht für bestimmte Geräte.",
    ],
    "siehe_auch": ["messkette", "messabweichungen", "messunsicherheit", "multimeter"],
}
