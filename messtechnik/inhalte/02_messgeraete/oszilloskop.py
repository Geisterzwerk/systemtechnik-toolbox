# Thema: Oszilloskop  (Messtechnik / Messgeräte)
THEMA = {
    "titel": "Oszilloskop",
    "reihenfolge": 2,
    "kurz": "Signale über die Zeit sichtbar machen – Bandbreite, Abtastrate, Tastkopf und Trigger richtig wählen.",
    "stichworte": ["oszilloskop", "oszi", "scope", "dso", "tastkopf", "probe", "10:1", "1:1", "kompensation",
                   "bandbreite", "abtastrate", "samplerate", "anstiegszeit", "trigger", "zeitbasis", "masse",
                   "erdschleife", "differenztastkopf", "kopplung", "ac", "dc", "fft", "aliasing", "speichertiefe"],

    "steckbrief": {
        "zeilen": [
            ("Zeigt", "Spannung über der Zeit (Y = Spannung, X = Zeit)"),
            ("Bandbreite B", "Frequenz, bei der die Amplitude um 3 dB (≈ 30 %) zu klein angezeigt wird"),
            ("Anstiegszeit", "`tr ≈ 0.35 / B`  (z.B. 100 MHz → 3.5 ns)"),
            ("Abtastrate", "mind. 2.5 … 5 × Bandbreite (Samples pro Sekunde)"),
            ("Tastkopf 10:1", "Standard: hoher Eingangswiderstand, grosse Bandbreite – muss **kompensiert** werden"),
            ("Masse", "Die Masseklemme liegt meist auf **Schutzleiter-Potenzial**!"),
        ],
    },

    "grafiken": ["abtastung"],

    "erklaerung": """
## Bandbreite – die wichtigste Kenngrösse
Das Oszilloskop verhält sich wie ein **Tiefpass**. Bei der Bandbreitenfrequenz B zeigt es einen Sinus schon **ca. 30 % zu klein** an. Faustregel: **B ≥ 3 … 5 × die höchste Signalfrequenz**. Für Rechtecksignale zählen die Oberwellen – massgebend ist die **Anstiegszeit**: `tr ≈ 0.35 / B`. Das Oszilloskop selbst „verschmiert“ Flanken; angezeigt wird ungefähr `√(tr,Signal² + tr,Oszi²)`.
## Abtastrate und Aliasing (siehe Grafik oben)
Ein digitales Oszilloskop tastet das Signal ab. Ist die Abtastrate zu klein, entsteht eine **falsche, tiefere Frequenz** auf dem Bildschirm (Aliasing). Achtung: Bei langer Zeitbasis sinkt die tatsächliche Abtastrate, weil die **Speichertiefe** begrenzt ist.
## Tastkopf
- **10:1** ist Standard: 10 MΩ Eingangswiderstand, kleine Kapazität, volle Bandbreite. Muss am **Kalibrier-Rechteck** kompensiert werden (Trimmer drehen, bis das Rechteck flache Dächer hat).
- **1:1** nur für kleine, langsame Signale – Bandbreite oft nur wenige MHz, belastet die Schaltung stärker.
- Das Teilerverhältnis muss auch im **Oszilloskop-Menü** eingestellt sein, sonst stimmen die angezeigten Volt nicht.
## Masse – die gefährlichste Falle
Bei den meisten Tischoszilloskopen ist die Masseklemme **mit dem Schutzleiter verbunden**. Klemmt man sie an einen Punkt, der nicht auf Erdpotenzial liegt (z.B. netzseitige Elektronik, Brückenschaltungen), entsteht ein **Kurzschluss über den Schutzleiter**. Lösung: **Differenztastkopf**, isoliertes Oszilloskop oder Trenntrafo für den Prüfling – niemals den Schutzleiter des Oszilloskops abklemmen!
## Trigger
Der Trigger sorgt für ein **stehendes Bild**: Die Aufzeichnung startet immer an derselben Stelle (z.B. steigende Flanke bei 1 V). Für einmalige Ereignisse: **Single**-Modus.
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 2.2 (Oszilloskop, Baugruppen, Betriebsarten), Kapitel 6.5.2 (Digitales Speicheroszilloskop), Kapitel 6.4.2 und 8.3.3 (Abtasttheorem), Kapitel 1.5 (dynamisches Verhalten).
""",

    "tipps": [
        "**Tastkopf kompensieren** bei jedem Wechsel an einen anderen Kanal oder ein anderes Gerät.",
        "**Kurze Masseverbindung:** Die lange Masseklemme wirkt wie eine Antenne und erzeugt Überschwinger. Für schnelle Signale die kurze Massefeder verwenden.",
        "**Kanalkopplung:** DC zeigt alles, AC blendet den Gleichanteil aus (gut für kleine Welligkeit auf einer Versorgung).",
        "**Welligkeit messen:** AC-Kopplung, 20-MHz-Bandbreitenbegrenzung einschalten, kurze Masse – sonst misst man vor allem Störungen.",
        "**Strom mit dem Oszi:** Spannung über einem kleinen Shunt messen oder eine Stromzange mit Oszilloskop-Ausgang verwenden.",
        "**Signal sieht komisch aus?** Zeitbasis ändern: Wenn sich die angezeigte Frequenz „komisch“ ändert, ist es Aliasing.",
        "**Messfunktionen nutzen** (Frequenz, Vpp, RMS, Anstiegszeit) – sie rechnen mit den Abtastwerten und sind genauer als Ablesen am Raster.",
    ],
    "fehler": [
        "Masseklemme an einen netzverbundenen Punkt angeschlossen → Kurzschluss über den Schutzleiter.",
        "Tastkopf auf 10:1, Oszilloskop auf 1:1 eingestellt → Werte um Faktor 10 falsch.",
        "Bandbreite zu klein gewählt → Flanken zu flach, Amplituden zu klein.",
        "Unkompensierter Tastkopf → Rechtecke mit „Dachschräge“ oder Überschwingern, die es in Wirklichkeit nicht gibt.",
    ],
    "siehe_auch": ["ad_wandler", "multimeter", "signalkenngroessen"],

    "rechner": ["oszi", "abtastung"],
}
