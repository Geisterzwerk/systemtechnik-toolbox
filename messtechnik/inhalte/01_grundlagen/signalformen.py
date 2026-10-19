# Thema: Signalformen & Fourier-Synthese  (Messtechnik / Grundlagen)
# Quellen: Fourierreihe (Wikipedia „Fourierreihe“, Beispiele Rechteck/Dreieck/Sägezahn, Gibbssches Phänomen).
# Alle Zahlen nachgerechnet mit messtechnik/signal_mathe.py (siehe pruefung/rechner_faelle.py):
# Rechteck Û = 1 V: 1.27 V / 424 mV / 255 mV; Gibbs-Spitze ≈ 1.179 · Û (≈ 9 % der Sprunghöhe).
THEMA = {
    "titel": "Signalformen & Fourier-Synthese",
    "reihenfolge": 5,
    "kurz": "Sinus, Rechteck, Dreieck, Sägezahn – und warum sich jedes periodische Signal aus Sinusschwingungen zusammensetzen lässt.",
    "stichworte": ["signalform", "signalformen", "sinus", "rechteck", "dreieck", "sägezahn", "puls", "pwm",
                   "periode", "frequenz", "kreisfrequenz", "amplitude", "scheitelwert", "spitze-spitze", "phase",
                   "fourier", "fourier-synthese", "fourier-analyse", "fourierreihe", "oberschwingung",
                   "harmonische", "grundschwingung", "spektrum", "gibbs", "klirrfaktor", "thd", "bandbreite"],
    "grafiken": ["fourier_synthese"],

    "steckbrief": {
        "zeilen": [
            ("Periodendauer", "`T` in s – Zeit für eine ganze Schwingung"),
            ("Frequenz", "`f = 1 / T` in Hz – Schwingungen pro Sekunde"),
            ("Kreisfrequenz", "`ω = 2π · f` in 1/s"),
            ("Sinus", "`u(t) = Û · sin(ω · t + φ)` – Scheitelwert Û, Phase φ"),
            ("Fourier", "jedes periodische Signal = Grundschwingung (f) + Oberschwingungen (2f, 3f, 4f …)"),
        ],
    },

    "erklaerung": """
## Stell dir vor …
Ein Klavier und eine Gitarre spielen genau denselben Ton, zum Beispiel das A mit 440 Hz – und trotzdem hörst du sofort, welches Instrument es ist. Der Grund: Keines der beiden erzeugt einen reinen Sinuston. Zum Grundton mit 440 Hz kommen **Obertöne** mit ungefähr 880 Hz, 1320 Hz und so weiter, bei jedem Instrument in einer anderen Mischung. Genau so ist es bei elektrischen Signalen: Fast jedes Signal ist eine Mischung aus Sinusschwingungen.
## Die wichtigsten Signalformen
- **Sinus:** die „reinste“ Schwingung – nur eine einzige Frequenz. Unser Stromnetz liefert (fast) einen Sinus mit 50 Hz.
- **Rechteck:** springt zwischen zwei Werten hin und her. Taktsignale, digitale Signale, PWM.
- **Dreieck:** steigt und fällt gleichmässig. Entsteht z.B. beim Laden und Entladen eines Kondensators mit konstantem Strom.
- **Sägezahn:** steigt gleichmässig und fällt dann schlagartig zurück (oder umgekehrt). Früher die Zeitablenkung in Röhrenbildschirmen und Oszilloskopen.
- **Puls / PWM:** ein Rechteck, bei dem „ein“ und „aus“ verschieden lang sind. Das Verhältnis heisst **Tastgrad**.
## Kenngrössen eines Signals
- **Periodendauer T** und **Frequenz f = 1 / T**: 50 Hz ergibt T = 20 ms.
- **Scheitelwert Û** (Amplitude): der grösste Wert. **Spitze-Spitze-Wert** U_ss: vom tiefsten zum höchsten Punkt, beim Sinus 2 · Û.
- **Phase φ:** um wie viel ein Signal gegenüber einem anderen verschoben ist (in Grad oder Bogenmass).
- **Effektivwert, Mittelwert, Formfaktor:** siehe Seite „Effektivwert, Mittelwert & Co.“
## Fourier: Signale aus Sinus bauen
Der Mathematiker **Joseph Fourier** zeigte, dass sich jedes periodische Signal (praktisch alle, die in der Technik vorkommen) als Summe von Sinusschwingungen schreiben lässt:
- einer **Grundschwingung** mit der Frequenz f des Signals und
- **Oberschwingungen** (Harmonischen) mit 2f, 3f, 4f …, jede mit ihrer eigenen Amplitude.
Das Zusammensetzen heisst **Fourier-Synthese**, das Zerlegen **Fourier-Analyse**. Die Liste aller Amplituden über der Frequenz ist das **Spektrum** – in der Grafik oben unten als Balken.
**Beispiel Rechteck mit Û = 1 V und f = 50 Hz:**
- Grundschwingung: 50 Hz mit 4/π · 1 V = **1.27 V**
- 3. Harmonische: 150 Hz mit 1.27 V / 3 = **424 mV**
- 5. Harmonische: 250 Hz mit 1.27 V / 5 = **255 mV**
- … nur **ungerade** Vielfache, die Amplitude nimmt mit 1/k ab.
Die Grundschwingung allein ist grösser als das Rechteck selbst (1.27 V statt 1 V) – erst die Oberschwingungen „drücken“ die Kurve flach. Probiere es in der Grafik: Mit jedem weiteren Glied werden die Flanken steiler und das Dach flacher.
## Die drei Formen im Vergleich
- **Rechteck:** nur ungerade Harmonische (3f, 5f, 7f …), Amplitude ~ 1/k – nimmt langsam ab, darum braucht ein Rechteck viele hohe Frequenzen.
- **Dreieck:** ebenfalls nur ungerade, Amplitude ~ 1/k² – nimmt schnell ab. Schon mit 3 Gliedern sieht es fast perfekt aus.
- **Sägezahn:** **alle** Harmonischen (2f, 3f, 4f …), Amplitude ~ 1/k.
Faustregel: **Je steiler die Flanken, desto mehr hohe Frequenzen** enthält ein Signal.
## 🔬 Genauer hingeschaut
- **Die Formeln** (Scheitelwert Û, ω = 2πf, Beginn bei t = 0 steigend):
- Rechteck: `u(t) = 4Û/π · [sin(ωt) + sin(3ωt)/3 + sin(5ωt)/5 + …]`
- Dreieck: `u(t) = 8Û/π² · [sin(ωt) − sin(3ωt)/9 + sin(5ωt)/25 − …]`
- Sägezahn: `u(t) = 2Û/π · [sin(ωt) − sin(2ωt)/2 + sin(3ωt)/3 − …]`
- **Gibbs-Phänomen:** An einem Sprung schwingt die Summe immer über – um rund **9 % der Sprunghöhe**, beim Rechteck ±1 V also bis etwa 1.18 V. Das bleibt so, egal wie viele Glieder man nimmt; der Überschwinger wird nur schmaler.
- **Warum nur ungerade Harmonische?** Rechteck und Dreieck sehen in der zweiten Halbperiode genau gleich aus wie in der ersten, nur umgekehrt (Halbwellensymmetrie). Gerade Harmonische würden diese Symmetrie stören – sie fehlen deshalb.
- **Bandbreite beim Oszilloskop:** Ein Messgerät zeigt nur die Frequenzen, die es durchlässt. Ein 10-MHz-Rechteck auf einem 20-MHz-Oszilloskop sieht fast wie ein Sinus aus, weil schon die 3. Harmonische (30 MHz) oberhalb der Bandbreite liegt und stark gedämpft wird. Faustregel: Bandbreite mindestens 5× die Signalfrequenz.
- **Verzerrter Sinus:** Ein verzerrter Sinus enthält Oberschwingungen. Ihr Anteil heisst **Klirrfaktor** oder THD (Total Harmonic Distortion). Im Stromnetz entstehen solche Oberschwingungen z.B. durch Schaltnetzteile und Frequenzumrichter.
## In der Praxis
- **Spektrum messen:** Viele Oszilloskope haben eine **FFT-Funktion** (Fast Fourier Transform), die das Spektrum direkt anzeigt.
- **Signalform beim Multimeter beachten:** Nur True-RMS-Geräte messen Rechteck, Dreieck und verzerrte Signale richtig.
- **Filter verstehen:** Ein Tiefpass entfernt hohe Harmonische – aus einem Rechteck wird dann ein abgerundetes Signal. Genau das passiert auch auf langen Leitungen.
## 💡 Wusstest du?
- Fourier entwickelte seine Idee Anfang des 19. Jahrhunderts eigentlich für ein ganz anderes Problem: die **Ausbreitung von Wärme** in festen Körpern.
- MP3 und JPEG nutzen eine verwandte Zerlegung in Schwingungen: Frequenzanteile, die man kaum hört oder sieht, werden weggelassen – so wird die Datei klein.
""",

    "tabellen": [
        {
            "titel": "📊 Signalformen und ihre Oberschwingungen",
            "kopf": ["Signal", "Oberschwingungen", "Amplitude der k-ten", "Grundschwingung (Û = 1 V)"],
            "zeilen": [
                ["Sinus", "keine", "–", "1 V"],
                ["Rechteck", "nur ungerade (3, 5, 7 …)", "4Û/(π·k)  ~ 1/k", "1.27 V"],
                ["Dreieck", "nur ungerade (3, 5, 7 …)", "8Û/(π²·k²)  ~ 1/k², wechselndes Vorzeichen", "0.81 V"],
                ["Sägezahn", "alle (2, 3, 4 …)", "2Û/(π·k)  ~ 1/k, wechselndes Vorzeichen", "0.64 V"],
            ],
            "hinweis": "Werte für die Phasenlage „Beginn bei t = 0, steigend“. Rechnung: messtechnik/signal_mathe.py – zum Ausprobieren die Grafik oben.",
        },
    ],

    "tipps": [
        "**Rechteck auf dem Oszilloskop rund?** Bandbreite von Oszilloskop und Tastkopf prüfen – und den Tastkopf abgleichen (Kompensation).",
        "**Spektrum zuerst:** Bei Störungen hilft die FFT-Funktion des Oszilloskops: Eine Spitze bei 150 Hz deutet z.B. auf Oberschwingungen aus dem Netz hin (3 × 50 Hz).",
        "**PWM mit dem Multimeter:** Im DC-Bereich misst man den Mittelwert, für den Effektivwert braucht es True RMS mit AC+DC.",
    ],
    "fehler": [
        "Angenommen, ein Rechteck enthalte nur seine Grundfrequenz – für Filter, Leitungen und EMV zählen gerade die Oberschwingungen.",
        "Scheitelwert und Spitze-Spitze-Wert verwechselt (Faktor 2 beim Sinus).",
        "Ein zu langsames Oszilloskop für steile Flanken verwendet – die Messung zeigt dann das Messgerät, nicht das Signal.",
    ],
    "siehe_auch": ["signalkenngroessen", "oszilloskop", "ad_wandler", "begriffe"],
    "rechner": ["fourier_synthese", "signalform", "oszi"],
}
