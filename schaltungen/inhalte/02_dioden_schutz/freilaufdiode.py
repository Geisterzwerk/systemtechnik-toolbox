# Seite "Freilaufdiode"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Freilaufdiode (Diode / Diode + Z-Diode)",
    "reihenfolge": 40,
    "kurz": "Gibt dem Spulenstrom beim Abschalten einen Weg – sonst schlägt der Schalttransistor durch.",
    "stichworte": ["Freilaufdiode", "Schutzdiode", "Löschdiode", "flyback diode", "Relais", "Spule",
                   "Abschaltspannung", "Z-Diode", "Induktive Last"],

    "grafiken": ["schaltung_freilauf", "rl_kurve"],

    "erklaerung": """
## Stell dir vor …
Beim **Fahrrad** kannst du aufhören zu treten, und das Rad dreht trotzdem weiter – dank Freilauf. Würde die Kette starr blockieren, gäbe es einen harten Ruck. Eine Spule ist wie das schwere Rad: Ihr Strom will weiterlaufen. Die Freilaufdiode ist der Freilauf: Sie lässt den Strom nach dem Abschalten im Kreis weiterfliessen, bis er von selbst ausgelaufen ist.
## Funktion
Eine Spule speichert Energie `W = ½ · L · I²`, und ihr Strom kann nicht springen. Schaltet der Transistor ab, induziert die Spule eine Spannung `u = −L · di/dt`, die so gross wird, dass der Strom weiterfliessen kann. Ohne Freilaufpfad sind das Hunderte Volt am Kollektor.

- **Freilaufdiode** antiparallel zur Spule (Kathode an +U_B): Der Strom fliesst im Kreis Spule → Diode → Spule. Am Transistor liegt nur `U_B + U_F`. Der Strom klingt mit `τ = L / R_Spule` langsam ab.
- **Diode + Z-Diode** in Reihe: Die Gegenspannung ist `U_F + U_Z` statt nur U_F – der Strom ist viel schneller null, am Transistor liegen `U_B + U_Z + U_F`.

Zeit bis der Strom null ist: `t_0 = τ · ln(1 + I · R / U_Gegen)`.

## Dimensionierung
1. **Diode**: Durchlassstrom ≥ Spulenstrom `I = U_B / R_Spule` (nur kurzzeitig), Sperrspannung ≥ U_B. Kleine Relais: 1N4148, grössere: 1N4007 oder Schottky.
2. **Mit Z-Diode**: U_Z so wählen, dass `U_B + U_Z + 0.7 V` sicher unter U_CE0 bzw. U_DS,max bleibt (20 % Reserve). Die Z-Diode muss die Energie ½ · L · I² pro Schaltvorgang aufnehmen.
3. **Transistor**: U_CE0 ≥ 2 · U_B ist eine gute Faustregel.

## Betriebszustände
- **Eingeschaltet**: Diode sperrt (Kathode an +U_B), Spule zieht Strom.
- **Abschalten mit Diode**: Strom fliesst durch die Diode weiter, U_CE ≈ U_B + 0.7 V, Relais fällt verzögert ab (oft 5 … 20 ms).
- **Abschalten mit Diode + Z**: U_CE ≈ U_B + U_Z + 0.7 V, Abfallzeit ein Mehrfaches kürzer – Kontakte öffnen schneller (weniger Abbrand).
- **Ohne Freilauf**: Spannungsspitze → Durchbruch am Transistor oder Funke am Schalter.

## Messpunkte
- **M1** (Kollektor/Drain) mit dem Oszilloskop beim Abschalten: Spitze muss auf U_B + 0.7 V (bzw. + U_Z) begrenzt sein. Tastkopf mit ausreichender Spannungsfestigkeit verwenden!
- Strom mit Stromzange oder kleinem Shunt in Reihe zur Spule: zeigt das langsame Abklingen.
- Abfallzeit des Relais am Kontakt messen (zweiter Kanal).

## Grenzfälle
- Spule ohne Freilauf an einem **mechanischen Schalter**: Funke an den Kontakten, Abbrand, Störungen (EMV).
- Sehr grosse Induktivität (Schütze, Ventile): Mit reiner Freilaufdiode schaltet das Ventil spürbar verzögert ab → Z-Diode oder Varistor.
- AC-Spulen: Hier geht keine Diode – RC-Glied (Snubber) oder Varistor verwenden.
## 🔬 Genauer hingeschaut
- **Wohin geht die Energie?** In der Spule steckt `W = ½ · L · I²`. Nach dem Abschalten wird sie im Spulenwiderstand und in der Diode in Wärme umgewandelt. Der Strom klingt ungefähr mit der Zeitkonstante `τ = L / R` ab – darum fällt ein Relais mit Freilaufdiode verzögert ab.
- **Welche Diode?** Sie muss kurzzeitig den vollen Spulenstrom führen. Bei kleinen Relais reicht eine 1N4148, bei grösseren Spulen eine 1N400x. Bei **PWM** (Motoren, Ventile) schaltet die Diode tausendfach pro Sekunde – dann braucht es eine **schnelle oder Schottky-Diode**, sonst wird sie heiss.
- **Gegenspannung bestimmt die Abfallzeit:** Je höher die Spannung, gegen die der Strom abfliessen muss, desto schneller ist er weg. Diode + Z-Diode ist darum ein Kompromiss zwischen Schutz und Tempo.
## 💡 Wusstest du?
- Bei **Wechselspannungs-Spulen** funktioniert eine Freilaufdiode nicht – sie würde in jeder zweiten Halbwelle die Spule kurzschliessen. Dort nimmt man ein RC-Glied oder einen Varistor.
""",

    "tipps": [
        "Diode immer direkt an die Spule löten (kurze Wege) – sonst strahlt die Leitung bis zur Diode Störungen ab.",
        "Viele Relais-Module haben die Freilaufdiode schon eingebaut – trotzdem nachsehen, ob sie richtig herum sitzt.",
        "ULN2003/ULN2803-Treiber enthalten die Freilaufdioden; der COM-Pin muss dafür an +U_B angeschlossen werden.",
    ],
    "fehler": [
        "Diode falsch herum eingelötet: Beim Einschalten entsteht ein Kurzschluss über die Diode (Diode oder Transistor brennen durch).",
        "COM-Pin des ULN2003 nicht angeschlossen – die internen Freilaufdioden wirken dann nicht.",
        "Z-Diode zu gross gewählt: U_B + U_Z überschreitet U_CE0 – der Transistor schlägt trotzdem durch.",
    ],
    "siehe_auch": ["verpolschutz", "tvs_schutz"],
    "rechner": ["freilauf", "abschaltspitze", "relais_ansteuerung"],
}
