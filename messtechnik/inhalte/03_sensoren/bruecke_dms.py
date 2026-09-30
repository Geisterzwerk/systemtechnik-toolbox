# Thema: Brückenschaltung & DMS  (Messtechnik / Sensoren)
THEMA = {
    "titel": "Brückenschaltung & DMS",
    "reihenfolge": 2,
    "kurz": "Kleine Widerstandsänderungen empfindlich messen – Grundlage für Kraft-, Druck- und Wägezellen.",
    "stichworte": ["brücke", "brückenschaltung", "wheatstone", "messbrücke", "abgleich", "ausschlagbrücke",
                   "dms", "dehnungsmessstreifen", "dehnung", "k-faktor", "viertelbrücke", "halbbrücke",
                   "vollbrücke", "wägezelle", "kraftsensor", "drucksensor", "mv/v", "instrumentenverstärker",
                   "temperaturkompensation"],

    "steckbrief": {
        "zeilen": [
            ("Aufbau", "zwei Spannungsteiler parallel an Ue, gemessen wird die Spannung **zwischen** den Mitten"),
            ("Abgleich", "`Ua = 0` wenn `R1/R2 = R3/R4`"),
            ("Ausgang", "`Ua = Ue · (R2/(R1+R2) − R4/(R3+R4))`"),
            ("DMS", "`ΔR/R = k · ε`  (k ≈ 2 bei Metall-DMS, ε = Dehnung)"),
            ("Typische Signale", "wenige mV pro Volt Speisespannung (mV/V) → Verstärker nötig"),
        ],
    },

    "erklaerung": """
## Warum eine Brücke?
Ändert sich ein Widerstand nur um 0.1 %, ist das mit einem einfachen Spannungsteiler kaum messbar: Die kleine Änderung „schwimmt“ auf einer grossen Grundspannung. Die **Wheatstone-Brücke** vergleicht zwei Spannungsteiler. Sind sie **abgeglichen** (R1/R2 = R3/R4), ist die Ausgangsspannung **genau null** – jede kleine Änderung eines Widerstands erscheint direkt als kleine Ausgangsspannung um null herum, die man stark verstärken kann.
## Abgleichbrücke und Ausschlagbrücke
- **Abgleichbrücke:** Ein Widerstand wird so lange verstellt, bis Ua = 0 ist. Der gesuchte Widerstand folgt aus dem Verhältnis – sehr genau, weil nur ein Nullabgleich nötig ist.
- **Ausschlagbrücke:** Die Brücke bleibt fest, die Ausgangsspannung ist das Messsignal. So arbeiten praktisch alle Sensoren (Wägezellen, Drucksensoren).
## Dehnungsmessstreifen (DMS)
Ein DMS ist ein dünnes Widerstandsgitter, das auf ein Bauteil geklebt wird. Wird das Bauteil gedehnt, wird der Draht länger und dünner → der Widerstand steigt: `ΔR/R = k · ε`. Bei Metall-DMS ist **k ≈ 2**. Typische Dehnungen sind klein (z.B. 1000 µm/m = 0.1 %), also ΔR/R ≈ 0.2 %.
## Viertel-, Halb- und Vollbrücke
- **Viertelbrücke:** 1 aktiver DMS – einfach, aber empfindlich auf Temperatur
- **Halbbrücke:** 2 aktive DMS (z.B. einer gedehnt, einer gestaucht) – doppeltes Signal, Temperatureffekte heben sich auf
- **Vollbrücke:** 4 aktive DMS – vierfaches Signal, beste Kompensation. So sind Wägezellen aufgebaut.
Näherung: `Ua ≈ Ue · k · ε · n / 4` (n = Anzahl aktiver DMS mit passender Anordnung).
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 3.3 (Abgleich- und Ausschlag-Widerstandsmessbrücke), Kapitel 3.4 (Verstärker für Brückenschaltungen), Kapitel 3.11 (Dehnungsmessstreifen), Kapitel 3.12 (Linearisieren).
""",

    "tipps": [
        "**Angabe in mV/V:** Wägezellen werden mit z.B. 2 mV/V angegeben – bei 5 V Speisung sind das bei Nennlast nur 10 mV.",
        "**Instrumentenverstärker verwenden:** Er verstärkt nur die Differenz der beiden Brückenmitten und unterdrückt die gemeinsame Spannung (ca. Ue/2).",
        "**Speisespannung = Referenz des ADC** (ratiometrische Messung): Schwankungen der Speisung kürzen sich dann heraus.",
        "**6-Leiter-Anschluss** bei Wägezellen: zwei Sense-Leitungen messen die Speisespannung direkt an der Zelle.",
        "**Temperatur:** Metall-DMS und Bauteil dehnen sich bei Erwärmung auch ohne Kraft. Halb- oder Vollbrücke kompensiert das.",
    ],
    "fehler": [
        "Brückenausgang gegen Masse gemessen statt zwischen den beiden Mitten.",
        "Viertelbrücke ohne Temperaturkompensation → Nullpunkt wandert mit der Temperatur.",
        "Kleines mV-Signal ohne Abschirmung über lange Leitungen geführt → Störungen grösser als das Signal.",
    ],
    "siehe_auch": ["temperatur", "ad_wandler", "messunsicherheit"],

    "rechner": ["bruecke", "dms"],
}
