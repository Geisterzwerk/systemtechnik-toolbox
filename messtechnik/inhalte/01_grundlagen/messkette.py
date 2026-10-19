# Thema: Messkette – Aufnehmer, Messumformer, Ausgeber  (Messtechnik / Grundlagen)
# Quellen: DIN 1319 (Messeinrichtung, Messkette, Messumformer) wie zitiert in den Wikipedia-Artikeln
# „Messeinrichtung“ (Beispiel Temperaturmesskette 0…250 °C) und „Messumformer“ (Einheitssignale).
# Zahlen der Grafik: messtechnik/grundlagen_mathe.py, Pt100 nach IEC 60751 (messtechnik/rechner.py).
THEMA = {
    "titel": "Messkette: Aufnehmer, Messumformer, Ausgeber",
    "reihenfolge": 2,
    "kurz": "Vom Messobjekt bis zur Anzeige: Welche Glieder eine Messeinrichtung hat und was jedes davon tut.",
    "stichworte": ["messkette", "messeinrichtung", "messaufbau", "aufnehmer", "sensor", "messwertaufnehmer",
                   "messumformer", "transmitter", "messverstärker", "messwandler", "messumsetzer", "ausgeber",
                   "anzeige", "hilfsenergie", "einheitssignal", "normsignal", "4-20 ma", "4…20 ma", "0-10 v",
                   "live zero", "zweileiter", "anpasser", "signalaufbereitung"],
    "grafiken": ["messkette_pt100"],

    "steckbrief": {
        "zeilen": [
            ("Messeinrichtung", "Gesamtheit aller Messgeräte und Zusatzeinrichtungen, um ein Messergebnis zu erhalten (DIN 1319)"),
            ("Messkette", "mehrere Glieder hintereinander: Ausgang des einen = Eingang des nächsten"),
            ("Glieder", "**Aufnehmer** (Sensor) → **Messumformer** / Messverstärker → **Ausgeber** (Anzeige, Speicher, Steuerung)"),
            ("Einheitssignale", "4 … 20 mA (bevorzugt), 0 … 20 mA, 0 … 10 V"),
            ("Hilfsenergie", "Energie von aussen, z.B. 24 V DC für Messumformer"),
        ],
    },

    "erklaerung": """
## Stell dir vor …
Im Heizraum soll die Temperatur eines Heizungsrohrs auf einem Bildschirm in der Leitwarte erscheinen – 50 Meter entfernt. Der Fühler am Rohr liefert aber nur einen winzigen Widerstandsunterschied. Damit daraus eine Zahl auf dem Bildschirm wird, braucht es mehrere Stationen hintereinander, jede mit einer eigenen Aufgabe. Diese Kette heisst **Messkette**.
## So ist eine Messkette aufgebaut
Die DIN 1319 nennt die Gesamtheit aller Geräte, die zusammen ein Messergebnis liefern, eine **Messeinrichtung**. Sind mehrere Geräte hintereinander geschaltet, gibt jedes sein Ausgangssignal an das nächste weiter – das ist die **Messkette**:
1. **Aufnehmer (Sensor):** der Teil, der die Messgrösse unmittelbar erfasst und in ein meist elektrisches Signal umsetzt. Beispiele: Pt100 (Temperatur → Widerstand), Thermoelement (Temperatur → Spannung), Dehnungsmessstreifen (Dehnung → Widerstand).
2. **Messumformer:** formt sein Eingangssignal nach einer festen Beziehung in ein anderes Ausgangssignal um – oft in ein **Einheitssignal** wie 4 … 20 mA, das sich gut übertragen lässt. Er übernimmt die Signalanpassung: verstärken, linearisieren, filtern, galvanisch trennen.
3. **Ausgeber:** stellt den Messwert bereit – als Anzeige (Zeiger, Display), als gespeicherte Daten oder als Signal für eine Steuerung (SPS).
Zwischen den Gliedern liegt die **Übertragung** (Leitungen, Bus). Geräte, die nicht im Signalweg liegen, aber nötig sind (z.B. das Netzgerät für die **Hilfsenergie**), heissen **Hilfsgeräte**.
## Messumformer, Messverstärker, Messwandler
Die DIN 1319 unterscheidet nach dem, was der Messumformer macht:
- **Messverstärker:** Eingang und Ausgang sind **dieselbe Grösse** (z.B. Spannung → grössere Spannung), er braucht **Hilfsenergie**.
- **Messwandler:** ebenfalls dieselbe Grösse, aber **ohne Hilfsenergie** – z.B. ein Stromwandler, der 400 A auf 5 A herunter transformiert.
- **Messumsetzer:** ändert die Signalstruktur, z.B. analog → digital (AD-Wandler).
In der Industrie heisst ein Messumformer oft **Transmitter**.
## Beispiel: Temperatur von 0 … 250 °C (siehe Grafik)
Diese Kette nach dem Beispiel zur DIN 1319 kannst du oben in der Grafik durchspielen:
- **Pt100** (Aufnehmer): 0 … 250 °C → 100.0 … 194.1 Ω
- **Messbrücke** (Messumformer): Widerstand → 0 … 60 mV
- **Messumformer**: 0 … 60 mV → **4 … 20 mA**
- **Anzeiger** (Ausgeber): 4 … 20 mA → Skala 0 … 250 °C
Bei 125 °C hat der Pt100 147.95 Ω, die Brücke liefert 30.6 mV und der Messumformer 12.15 mA. Weil die Pt100-Kennlinie leicht gekrümmt ist, die Skala des Anzeigers aber gleichmässig, zeigt er ohne Linearisierung **127.4 °C** – 2.4 K zu viel. Moderne Messumformer rechnen die Kennlinie deshalb zurück (Schalter „linearisiert“ in der Grafik).
## Warum 4 … 20 mA?
- **Strom statt Spannung:** In einem geschlossenen Stromkreis fliesst überall derselbe Strom. Der Leitungswiderstand verfälscht den Wert deshalb nicht, solange die Spannung der Quelle reicht – ideal für lange Leitungen in der Industrie.
- **„Live Zero“:** Der Messbereich beginnt bei 4 mA, nicht bei 0 mA. Ein Drahtbruch (0 mA) lässt sich so vom Messwert „Anfang des Bereichs“ unterscheiden.
- **Zweileitertechnik:** Ein Messumformer kann sich aus den 4 mA selbst versorgen. Versorgung und Messsignal laufen dann über dieselben zwei Drähte.
- **Umrechnung:** `Wert = Anfang + (I − 4 mA) / 16 mA · Spanne`. Beispiel 0 … 250 °C: 12 mA → (12 − 4) / 16 · 250 °C = **125 °C**.
## 🔬 Genauer hingeschaut
- **Jedes Glied trägt zur Unsicherheit bei:** Sensor, Brücke, Messumformer und Anzeige haben je eigene Fehlergrenzen. Für die gesamte Kette werden die einzelnen Beiträge zusammengefasst (Fehlerfortpflanzung).
- **Rückwirkung:** Das erste Glied belastet das Messobjekt. Ein Pt100 wird vom Messstrom selbst ein wenig erwärmt (Eigenerwärmung) – deshalb ist der Messstrom klein (typisch um 1 mA).
- **Störfestigkeit:** Kleine Signale (mV vom Sensor) sind empfindlich auf Störungen. Darum sitzt der Messumformer möglichst nahe am Sensor („Kopftransmitter“ direkt im Anschlusskopf), und erst das kräftige 4…20-mA-Signal geht über die lange Leitung.
- **Fehlersignal nach NAMUR NE 43:** Viele Messumformer melden einen erkannten Fehler mit einem Strom ausserhalb des Messbereichs (≤ 3.6 mA oder ≥ 21 mA). Die Steuerung erkennt so einen defekten Sensor.
- **Digitale Messketten:** Heute wird das Signal oft schon im Messumformer digitalisiert und über einen Bus übertragen (z.B. HART auf der 4…20-mA-Leitung, IO-Link, Modbus). Die Glieder bleiben dieselben.
## In der Praxis
- **Messkette prüfen:** Glied für Glied messen – am Sensor (Ω), am Ausgang des Messumformers (mA, Multimeter in Reihe) und an der Anzeige. So findet man, wo der Fehler entsteht.
- **Strom messen ohne Auftrennen:** Manche Messumformer haben Testklemmen, an denen man den Schleifenstrom misst, ohne den Kreis zu öffnen.
- **Bürde beachten:** Jedes Gerät in der Stromschleife hat einen Innenwiderstand. Die Summe darf die maximale Bürde des Messumformers nicht übersteigen, sonst erreicht er die 20 mA nicht mehr.
## 💡 Wusstest du?
- Vor den elektrischen Einheitssignalen wurden Messwerte in der Prozessindustrie **pneumatisch** übertragen, mit Druckluft von 0.2 … 1 bar. Auch dort begann der Bereich nicht bei null – dieselbe Idee wie das „Live Zero“ bei 4 mA.
""",

    "tabellen": [
        {
            "titel": "📊 Glieder einer Messkette",
            "kopf": ["Glied", "Aufgabe", "Beispiele"],
            "zeilen": [
                ["Aufnehmer (Sensor)", "erfasst die Messgrösse, setzt sie in ein Signal um", "Pt100, Thermoelement, DMS, Fotodiode, Shunt"],
                ["Messumformer / Transmitter", "formt in ein Einheitssignal um, linearisiert, trennt galvanisch", "Kopftransmitter 4…20 mA, Trennverstärker"],
                ["Messverstärker", "verstärkt (gleiche Grösse), braucht Hilfsenergie", "DMS-Messverstärker, Instrumentenverstärker"],
                ["Messwandler", "wandelt (gleiche Grösse), ohne Hilfsenergie", "Stromwandler 400/5 A, Spannungswandler"],
                ["Messumsetzer", "ändert die Signalstruktur", "AD-Wandler"],
                ["Ausgeber", "zeigt an, speichert oder gibt weiter", "Anzeige, Datenlogger, SPS-Eingang"],
                ["Hilfsgerät", "nicht im Signalweg, aber nötig", "Netzgerät 24 V DC, Thermostat"],
            ],
        },
        {
            "titel": "📊 Einheitssignale",
            "kopf": ["Signal", "Besonderheit", "Typischer Einsatz"],
            "zeilen": [
                ["4 … 20 mA", "Live Zero (Drahtbruch erkennbar), Zweileiter möglich, unempfindlich auf Leitungswiderstand", "Prozessindustrie, lange Leitungen"],
                ["0 … 20 mA", "wie oben, aber ohne Live Zero", "ältere Anlagen"],
                ["0 … 10 V", "einfach, aber empfindlich auf Spannungsfall und Störungen", "kurze Leitungen, Gebäudetechnik"],
            ],
        },
    ],

    "tipps": [
        "**Messumformer nahe am Sensor:** Kleine mV-Signale nicht über lange Leitungen schicken – lieber zuerst umformen.",
        "**4 mA = Anfang, nicht 0:** Zeigt die Anzeige bei 0 mA einen negativen Wert oder „Unterlauf“, ist das oft ein Drahtbruch, kein Messwert.",
        "**Polarität der Stromschleife beachten:** Bei Zweileiter-Messumformern speist meist die SPS-Eingangskarte oder ein Speisetrenner die Schleife.",
    ],
    "fehler": [
        "Strom mit dem Multimeter parallel statt in Reihe gemessen – das schliesst die Schleife kurz.",
        "Zu viele Geräte in einer Stromschleife (Summe der Bürden zu gross) – der Messumformer kommt nicht mehr auf 20 mA.",
        "Messbereich in Messumformer und Anzeige verschieden eingestellt (z.B. 0…200 °C gegen 0…250 °C) – systematische Abweichung.",
        "Pt100-Kennlinie nicht linearisiert, aber mit linearer Skala angezeigt.",
    ],
    "siehe_auch": ["begriffe", "messabweichungen", "temperatur", "bruecke_dms", "ad_wandler"],
    "rechner": ["messkette_pt100", "pt100"],
}
