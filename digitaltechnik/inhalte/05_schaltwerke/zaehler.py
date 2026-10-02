# Seite "Zähler"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Zähler und Frequenzteiler",
    "reihenfolge": 20,
    "kurz": "Asynchrone (Ripple-) und synchrone Zähler, Modulo-Zähler, Auf/Ab – und warum Zähler auch Frequenzteiler sind.",
    "stichworte": ["Zähler", "Counter", "asynchron", "synchron", "Ripple-Zähler", "Dualzähler", "BCD-Zähler",
                   "Dekadenzähler", "Modulo", "Frequenzteiler", "Vorwärts", "Rückwärts", "74HC393", "74HC161",
                   "CD4060", "Glitch", "Uhrenquarz"],

    "grafiken": ["werkzeug_zaehler"],

    "erklaerung": """
## Grundlagen
Ein n-Bit-Zähler aus n Flipflops durchläuft `2^n` Zustände (Modulo `2^n`). Bit Q0 hat die halbe Taktfrequenz, jedes weitere wieder die Hälfte.
- **Asynchron (Ripple)**: nur das erste Flipflop am Takt, jedes weitere am Ausgang des vorigen (T-Flipflops).
  - Wenig Logik.
  - Die Bits kippen nacheinander (je t_pd): Beim Übergang `0111 → 1000` sind kurz `0110`, `0100`, `0000` zu sehen.
  - Ausgänge nicht direkt dekodieren (Glitches).
- **Synchron**: alle Flipflops am selben Takt, eine Logik bestimmt, welche Bits kippen (`T_i = Q0·Q1·…·Q(i−1)`).
  - Alle Ausgänge ändern sich gleichzeitig.
  - Höhere Frequenz möglich, sauber dekodierbar.
- **Modulo m**: nach m Zuständen zurück auf 0 (z.B. Dekadenzähler m = 10).
  - Asynchrones Rücksetzen beim Erreichen von m erzeugt einen kurzen Glitch-Zustand m.
  - Synchrones Laden ist sauber.

## Vorgehen
1. Anzahl Zustände m → Flipflops `n = ⌈log2 m⌉`.
2. asynchron (einfach, langsam, Glitches) oder synchron (Standard in digitalen Systemen) wählen.
3. Synchroner Zähler mit besonderer Folge: Zustandsfolgetabelle → Ansteuergleichungen → minimieren (siehe „Synchrone Zähler entwerfen“).
4. Als Frequenzteiler: `f_aus = f / m`; für 50 % Tastgrad bei geradem m durch m/2 teilen und ein T-Flipflop anhängen.

## Beispiel
Uhrenquarz 32 768 Hz = 2^15 Hz:
- 15 T-Flipflops hintereinander → 1 Hz Sekundentakt (CD4060 + ein Flipflop, oder in jeder RTC).

Dekadenzähler (m = 10):
- 4 Flipflops, Zustände 0 … 9
- Asynchron mit Rücksetzen bei `1010`: Zustand 10 ist für einige ns sichtbar → in synchroner Logik vermeiden.

## Praxis
- 74HC393: 2 × 4-Bit-Ripple-Zähler; 74HC161/163: 4-Bit-Synchronzähler mit Laden (163 synchrones Rücksetzen).
- In µC: Timer/Counter-Peripherie zählt Takte (Zeitmessung, PWM, Ereignisse) – ein synchroner Zähler mit Vergleichsregister.
- Messgeräte: Frequenzzähler zählen Impulse während einer genauen Torzeit.
""",

    "tipps": [
        "Auf einen asynchronen Zählerstand erst nach n · t_pd zugreifen – oder den Zählerstand mit einem Register übernehmen.",
    ],
    "fehler": [
        "Ausgänge eines Ripple-Zählers direkt dekodiert – die Zwischenzustände erzeugen Störimpulse.",
        "Anzahl Flipflops falsch: m = 10 braucht 4 Flipflops, nicht 3.",
        "Frequenzteiler durch 10 mit 50 % Tastgrad erwartet – das höchste Bit ist nur 2 von 10 Takten HIGH.",
    ],
    "siehe_auch": ["flipflops", "zaehler_entwurf", "schieberegister"],
    "rechner": ["frequenzteiler", "zaehler_entwurf", "fmax_schaltwerk"],
}
