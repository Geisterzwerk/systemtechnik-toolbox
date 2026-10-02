# Seite "Anti-Aliasing-Filter"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Anti-Aliasing-Tiefpass vor dem ADC",
    "reihenfolge": 50,
    "kurz": "Alles über der halben Abtastrate muss vor dem ADC weg – sonst erscheint es als falsche, tiefe Frequenz.",
    "stichworte": ["Anti-Aliasing", "Aliasing", "Nyquist", "Shannon", "Abtasttheorem", "Abtastrate", "ADC",
                   "Tiefpass", "Oversampling", "Spiegelfrequenz", "Sample and Hold"],

    "grafiken": ["schaltung_anti_aliasing"],

    "erklaerung": """
## Funktion
Ein ADC misst nur zu den Abtastzeitpunkten (Abtastrate f_s). **Abtasttheorem** (Nyquist/Shannon): Eindeutig erfasst wird nur, was unter `f_s / 2` liegt.

Eine höhere Frequenz f wird nicht einfach weggelassen, sondern erscheint als **Alias**:
- `f_alias = |f − n · f_s|`  (n = nächste ganze Zahl zu f / f_s)
- Beispiel: f_s = 1 kHz, Störung 900 Hz → erscheint als 100 Hz; 50-Hz-Brumm bei f_s = 49 Hz → 1 Hz Schwankung.

Nach dem Abtasten ist der Alias nicht mehr vom echten Signal zu unterscheiden – das Filter muss **vor** dem ADC sitzen. Der einfachste Anti-Aliasing-Filter ist ein RC-Tiefpass.

## Dimensionierung
1. Höchste Nutzfrequenz f_max bestimmen, f_s ≥ 2 · f_max – praktisch **5 … 10 · f_max** (das Filter braucht Platz zum Abfallen).
2. RC-Tiefpass: fg knapp über f_max, `fg = 1 / (2π · R · C)`.
3. Dämpfung bei f_s / 2 prüfen: Damit eine Störung mit vollem Ausschlag unter ½ LSB fällt, braucht ein N-Bit-ADC `6.02 · N dB` (12 Bit: ≈ 72 dB).
4. 1. Ordnung schafft nur 20 dB/Dekade → in der Praxis: **Oversampling** (viel höher abtasten, digital filtern und dezimieren) oder Filter höherer Ordnung (Sallen-Key mit OPV) – oder ein Sigma-Delta-ADC mit eingebautem Digitalfilter.
5. R klein halten (≤ 1 … 10 kΩ, Datenblatt des ADC): Der Sample-and-Hold-Kondensator des ADC muss beim Abtasten über R nachgeladen werden; C ≥ ≈ 20 · C_Sample puffert dabei.

## Betriebszustände
- **f < f_s / 2**: richtig erfasst, nur durch das Filter etwas gedämpft.
- **f = f_s / 2**: Grenzfall – je nach Phase alles oder nichts sichtbar.
- **f > f_s / 2 ohne Filter**: Alias mit voller Amplitude bei falscher Frequenz.
- **f > f_s / 2 mit Filter**: Alias, aber um |H(f)| gedämpft – im Idealfall unter 1 LSB.

## Messpunkte
- **M1** (ADC-Eingang) mit dem Oszilloskop: Was hier über f_s / 2 noch zu sehen ist, wird falsch gemessen.
- Test: Sinus mit f knapp unter und knapp über f_s / 2 einspeisen und die ADC-Werte ansehen – über Nyquist erscheint eine langsame Schwebung.
- Gleiches Problem beim Digital-Oszilloskop: Zu langsame Zeitbasis zeigt falsche Frequenzen (Peak-Detect oder schnellere Zeitbasis zum Prüfen).

## Grenzfälle
- f genau ein Vielfaches von f_s: Alias bei 0 Hz – das Signal sieht wie eine Gleichspannung aus.
- Kein Filter, aber Signal bandbegrenzt (z.B. Temperatur, sehr langsam): Störungen (Netzbrumm, Schaltregler) falten trotzdem herunter – darum immer ein kleines RC.
- Sehr grosses C bei grossem R: Filter zu langsam, Sprünge im Messsignal werden verschliffen.
""",

    "tipps": [
        "50-Hz-Brumm: Abtasten mit einem ganzzahligen Vielfachen von 50 Hz und Mittelwert über 20 ms unterdrückt ihn fast vollständig.",
        "Viele µC-ADCs (SAR) erwarten eine niederohmige Quelle – RC direkt am Pin mit z.B. 1 kΩ / 100 nF ist ein guter Start.",
    ],
    "fehler": [
        "Gedacht, eine Frequenz über f_s / 2 werde einfach nicht gemessen – sie erscheint als falsche, tiefere Frequenz.",
        "Das Filter erst digital nach dem ADC eingebaut – der Alias ist dann schon im Signal.",
        "f_s genau 2 · f_max gewählt – ein reales Filter hat dann keinen Platz zum Abfallen.",
    ],
    "siehe_auch": ["rc_tiefpass_hochpass", "aktive_filter_sallen_key"],
    "rechner": ["anti_aliasing", "rc_frequenzgang", "rc_filter"],
}
