# Thema: Messabweichungen (Messfehler)  (Messtechnik / Grundlagen)
# Quellen: DIN 1319-1 wie zitiert im Wikipedia-Artikel „Messabweichung“ (Definitionen, F = x_a − x_r,
# f = F / x_r, systematisch/zufällig, Rückwirkungsabweichung, Fehlergrenze); Hochschul-Unterlagen zur
# Fehlerrechnung (grobe Fehler, 3-s-Faustregel). Beispiel Rückwirkung mit dem Rechner "spannungsteiler"
# nachgerechnet (1 MΩ / 1 MΩ an 10 V, Last 10 MΩ -> 4.762 V).
THEMA = {
    "titel": "Messabweichungen (Messfehler)",
    "reihenfolge": 3,
    "kurz": "Grobe, systematische und zufällige Abweichungen – woher sie kommen, wie man sie erkennt und was man dagegen tut.",
    "stichworte": ["messabweichung", "messfehler", "fehlerarten", "systematischer fehler", "zufälliger fehler",
                   "grober fehler", "ausreisser", "absolute abweichung", "relative abweichung", "rückwirkung",
                   "belastungsfehler", "parallaxe", "ablesefehler", "nullpunktfehler", "linearitätsfehler",
                   "quantisierung", "einflussgrösse", "temperaturfehler", "richtigkeit", "präzision",
                   "fehlergrenze", "korrektur", "normalverteilung"],
    "grafiken": ["messreihe"],

    "steckbrief": {
        "zeilen": [
            ("Absolute Abweichung", "`F = Messwert − richtiger Wert`  (in der Einheit der Messgrösse, mit Vorzeichen)"),
            ("Relative Abweichung", "`f = F / richtiger Wert · 100 %`"),
            ("Systematisch", "gleiche Richtung und Grösse bei jeder Wiederholung → Ergebnis **unrichtig**"),
            ("Zufällig", "streut nach Betrag und Vorzeichen → Ergebnis **unsicher**"),
            ("Grob", "Irrtum (falsch abgelesen, falscher Bereich) → vermeiden, erkennen, streichen"),
        ],
    },

    "erklaerung": """
## Stell dir vor …
Du schiesst mit Pfeilen auf eine Zielscheibe. Landen alle Pfeile eng beieinander, aber oben links neben der Mitte, ist dein Bogen **verzogen** – das ist eine **systematische** Abweichung. Landen die Pfeile rund um die Mitte, aber weit verstreut, zittert deine Hand – das ist eine **zufällige** Abweichung. Und ein Pfeil, der in der Nachbarscheibe steckt, weil du das falsche Ziel genommen hast, ist ein **grober Fehler**. Beim Messen ist es genau gleich.
## Die drei Arten von Abweichungen
- **Systematische Abweichung:** hat bei jeder Wiederholung unter gleichen Bedingungen **dieselbe Richtung und Grösse**. Sie macht das Ergebnis **unrichtig**. Ist sie bekannt, rechnet man sie heraus (Korrektur). Ist sie unbekannt, geht sie als Grenzwert in die Messunsicherheit ein.
- **Zufällige Abweichung:** schwankt in **Betrag und Vorzeichen** von Messung zu Messung. Sie macht das Ergebnis **unsicher**. Misst man oft, verteilen sich die Werte meist wie eine Glockenkurve um den Mittelwert – und der Mittelwert wird umso genauer, je mehr Messungen es sind.
- **Grober Fehler:** ein Irrtum – falsch abgelesen, falscher Messbereich, Messleitung im falschen Anschluss. Grobe Fehler gehören nicht zur Messunsicherheit, sie werden **vermieden** oder **erkannt und begründet gestrichen**.
Die Grafik oben zeigt alle drei: Verschiebe die systematische Abweichung, verändere die Streuung und schalte einen groben Fehler dazu.
## Rechnen: absolute und relative Abweichung
Weil der wahre Wert nie genau bekannt ist, vergleicht man mit einem **richtigen Wert** (z.B. einer kalibrierten Referenz):
- **Absolute Abweichung:** `F = Messwert − richtiger Wert` – mit Vorzeichen und Einheit.
- **Relative Abweichung:** `f = F / richtiger Wert · 100 %`.
**Beispiel:** Eine Referenzspannung von genau 5.000 V wird gemessen, das Multimeter zeigt 5.12 V. Dann ist F = +0.12 V und f = 0.12 V / 5.000 V = **+2.4 %**. Das Vorzeichen sagt: Das Gerät zeigt zu viel an.
## Woher kommen Abweichungen?
- **Messgerät:** Nullpunkt verschoben, Verstärkung zu gross oder zu klein, gekrümmte Kennlinie, Alterung (Drift), Auflösung (ein Display mit 0.01 V kann ±0.005 V nicht unterscheiden).
- **Messverfahren:** z.B. Leitungswiderstand bei einer Zweileiter-Messung, die falsche Messschaltung.
- **Rückwirkung:** Das Messgerät verändert das Messobjekt (siehe Beispiel unten).
- **Umgebung (Einflussgrössen):** Temperatur, Feuchte, elektromagnetische Störungen, Erschütterungen.
- **Beobachter:** Ablesen schräg zur Skala (**Parallaxe**), Rundungen, zu früh abgelesen.
- **Zeitverhalten:** Ein träger Sensor folgt einer schnellen Änderung nicht – es entsteht eine **dynamische** Abweichung.
## Beispiel: Rückwirkung beim Spannungsmessen
Zwei Widerstände mit je 1 MΩ teilen 10 V – an der Mitte liegen 5 V. Misst man dort mit einem Multimeter, das 10 MΩ Innenwiderstand hat, liegt dieser parallel zum unteren Widerstand. Die Spannung sinkt auf **4.76 V** – eine systematische Abweichung von **−4.8 %**, verursacht allein durch das Messgerät. An niederohmigen Schaltungen (z.B. 1 kΩ) wäre sie vernachlässigbar. Darum: Der Innenwiderstand des Spannungsmessers soll viel grösser sein als der Widerstand der Schaltung.
## 🔬 Genauer hingeschaut
- **Systematisch heisst nicht konstant:** Eine systematische Abweichung kann vom Messwert abhängen (Steigungsabweichung) oder von einer Einflussgrösse (Temperaturgang). Sie ist aber bei gleichen Bedingungen immer gleich – darum hilft Mitteln nicht.
- **Mitteln hilft nur gegen Zufall:** Die Unsicherheit des Mittelwerts sinkt mit `s / √n`. Viermal so viele Messungen halbieren sie – eine systematische Abweichung bleibt aber genau gleich gross.
- **Grobe Fehler erkennen:** Eine verbreitete Faustregel: Ein Wert, der mehr als **3 Standardabweichungen** vom Mittelwert abweicht, ist verdächtig. Streichen darf man ihn nur mit Begründung (z.B. „falscher Bereich eingestellt“) – nie nur, weil er nicht passt.
- **Richtigkeit und Präzision:** Kleine systematische Abweichung = gute **Richtigkeit**. Kleine Streuung = gute **Präzision**. Erst beides zusammen ergibt ein **genaues** Ergebnis.
- **Fehlergrenze ≠ Abweichung:** Die Fehlergrenze ist der Höchstbetrag, den der Hersteller zusichert (ohne Vorzeichen). Die tatsächliche Abweichung eines bestimmten Geräts ist meist kleiner – aber man kennt sie erst nach einer Kalibrierung.
- **Quantisierung:** Ein digitales Messgerät kann nur in Stufen anzeigen. Die Abweichung durch die Rundung beträgt bis zu ±½ der letzten Stelle.
## In der Praxis
- **Systematische Abweichungen finden:** mit einer bekannten Referenz vergleichen, ein zweites Messgerät oder ein anderes Messverfahren verwenden, Nullpunkt prüfen (Messleitungen kurzschliessen).
- **Zufällige Abweichungen verkleinern:** mehrmals messen und mitteln, Störungen abschirmen, Mittelwertfunktion des Geräts nutzen.
- **Grobe Fehler vermeiden:** Messbereich und Anschluss vor jeder Messung prüfen, Ergebnis auf Plausibilität kontrollieren („Kann das stimmen?“), wichtige Messungen von einer zweiten Person ablesen lassen.
## 💡 Wusstest du?
- Die DIN 1319 spricht nicht mehr von „Messfehlern“, sondern von **Messabweichungen**: Abweichungen hat jede Messung, ein „Fehler“ klingt nach etwas, das man falsch gemacht hat.
- Die Glockenkurve heisst auch **Gausssche Normalverteilung** – nach Carl Friedrich Gauss, der sie unter anderem für die Auswertung astronomischer Messungen nutzte.
""",

    "tabellen": [
        {
            "titel": "📊 Arten von Messabweichungen",
            "kopf": ["Art", "Merkmal", "Beispiele", "Gegenmassnahme"],
            "zeilen": [
                ["systematisch, bekannt", "gleiche Richtung und Grösse, Wert bekannt", "Abweichung laut Kalibrierschein, Leitungswiderstand gemessen", "Messwert korrigieren"],
                ["systematisch, unbekannt", "gleiche Richtung, Wert nur abgeschätzt", "Fehlergrenze des Geräts, Temperaturgang", "in die Messunsicherheit aufnehmen, kalibrieren"],
                ["zufällig", "streut um den Mittelwert", "Rauschen, Ablesen, kleine Schwankungen", "mehrmals messen, mitteln"],
                ["grob", "Irrtum, meist ein einzelner Ausreisser", "falscher Messbereich, verwechselte Anschlüsse, Tippfehler", "sorgfältig arbeiten, plausibel prüfen, begründet streichen"],
            ],
        },
        {
            "titel": "📊 Typische Ursachen in der Elektrotechnik",
            "kopf": ["Ursache", "Wirkung", "Abhilfe"],
            "zeilen": [
                ["Innenwiderstand des Spannungsmessers", "Spannung wird zu klein gemessen (Belastung)", "hochohmiges Gerät, Rückwirkung abschätzen"],
                ["Innenwiderstand des Strommessers", "Strom wird zu klein gemessen", "kleinen Bürdenwiderstand, passenden Bereich"],
                ["Leitungswiderstand (2-Leiter)", "Widerstand wird zu gross gemessen", "4-Leiter-Messung, Null-Abgleich (REL)"],
                ["Thermospannungen an Kontakten", "µV-Fehler bei kleinen Spannungen", "gleiche Metalle, Temperatur ausgleichen, umpolen"],
                ["Kein True RMS bei verzerrtem Signal", "Wechselgrössen falsch angezeigt", "True-RMS-Gerät verwenden"],
                ["Parallaxe am Zeigerinstrument", "schräg abgelesen", "senkrecht ablesen, Spiegelskala"],
            ],
        },
    ],

    "tipps": [
        "**Zuerst grob, dann fein:** Messbereich zuerst gross wählen, dann verkleinern – schützt das Gerät und vermeidet grobe Fehler.",
        "**Nullpunkt prüfen:** Messleitungen kurzschliessen – zeigt das Multimeter im Ω-Bereich 0.3 Ω, ist das der Leitungswiderstand, nicht der Messwert.",
        "**Plausibilität:** Vor dem Notieren kurz überlegen, welche Grössenordnung zu erwarten ist. 2300 V an einer 230-V-Steckdose ist kein Messwert, sondern ein Ablese- oder Bereichsfehler.",
        "**Rückwirkung abschätzen:** Innenwiderstand des Messgeräts mit dem Widerstand der Schaltung vergleichen – Faktor 100 grösser heisst rund 1 % Abweichung oder weniger.",
    ],
    "fehler": [
        "Mehrmals gemessen und gemittelt, um eine systematische Abweichung loszuwerden – das funktioniert nicht.",
        "Einen unbequemen Messwert ohne Begründung gestrichen.",
        "Relative Abweichung auf den Messwert statt auf den richtigen Wert bezogen.",
        "Den Innenwiderstand des Messgeräts an hochohmigen Schaltungen vergessen.",
    ],
    "siehe_auch": ["begriffe", "messunsicherheit", "messkette", "multimeter"],
    "rechner": ["messreihe", "statistik", "dmm_genauigkeit", "belastung_u"],
}
