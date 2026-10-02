# Thema: Durchfluss messen  (Messtechnik / Sensoren)
THEMA = {
    "titel": "Durchfluss messen",
    "reihenfolge": 3,
    "kurz": "Magnetisch-induktiv, Coriolis, Ultraschall & Co. – welches Prinzip für welches Medium?",
    "stichworte": ["durchfluss", "durchflussmessung", "flow", "volumenstrom", "massestrom", "massedurchfluss",
                   "mid", "magnetisch-induktiv", "induktiv", "coriolis", "ultraschall", "laufzeit", "vortex",
                   "wirbel", "thermisch", "leitfähigkeit", "nennweite", "fliessgeschwindigkeit", "einlaufstrecke",
                   "promag", "promass", "prosonic"],

    "steckbrief": {
        "zeilen": [
            ("Volumenstrom Q", "Volumen pro Zeit, z.B. m³/h · `Q = v · A`"),
            ("Massestrom", "Masse pro Zeit, z.B. kg/h · `ṁ = ρ · Q`"),
            ("Magnetisch-induktiv (MID)", "leitfähige Flüssigkeiten, keine bewegten Teile, kein Druckverlust"),
            ("Coriolis", "misst direkt den **Massestrom** (und die Dichte) – sehr genau"),
            ("Ultraschall", "Laufzeitdifferenz mit/gegen die Strömung – auch als Clamp-on von aussen"),
            ("Vortex / thermisch", "Wirbelfrequenz (Gase, Dampf) bzw. Wärmeabtransport (Gase)"),
        ],
    },

    "erklaerung": """
## Magnetisch-induktiv (MID)
Nach dem **Induktionsgesetz**: Bewegt sich ein Leiter durch ein Magnetfeld, entsteht eine Spannung. Beim MID ist die **leitfähige Flüssigkeit** der Leiter. Spulen erzeugen quer zum Rohr ein Magnetfeld, zwei Elektroden greifen die Spannung ab: `U ≈ B · D · v` (proportional zur mittleren Fliessgeschwindigkeit). Daraus folgt mit dem Querschnitt der Volumenstrom.
- ✅ keine bewegten Teile, kein Druckverlust, unabhängig von Druck, Temperatur und Viskosität
- ❌ nur für **elektrisch leitfähige** Medien (Wasser, Abwasser, Säuren, Pulpen) – nicht für Öl, Gase oder reines VE-Wasser
## Coriolis
Das Medium fliesst durch ein oder zwei Messrohre, die zum Schwingen angeregt werden. Durch die **Corioliskraft** verdrehen sich die Rohre etwas: Die Schwingung am Ein- und Auslauf ist **phasenverschoben**. Diese Phasendifferenz ist direkt proportional zum **Massestrom**. Aus der Schwingfrequenz folgt zusätzlich die **Dichte**.
- ✅ misst direkt Masse, sehr genau, für Flüssigkeiten und Gase, dazu Dichte und Temperatur
- ❌ teurer, bei grossen Nennweiten schwer, Druckverlust
## Ultraschall (Laufzeitdifferenz)
Zwei Sensoren senden sich abwechselnd Ultraschallimpulse schräg durch das Rohr. **Mit** der Strömung ist der Schall schneller als **gegen** sie. Aus der Laufzeitdifferenz folgt die Geschwindigkeit. Als **Clamp-on** werden die Sensoren einfach aussen aufs Rohr gespannt – ohne Rohrtrennung.
## Weitere Prinzipien
- **Vortex (Wirbelzähler):** Ein Störkörper erzeugt Wirbel, deren Frequenz proportional zur Geschwindigkeit ist – gut für Dampf und Gase
- **Thermisch:** Ein geheizter Sensor wird vom Gas gekühlt – misst Massestrom von Gasen
- **Differenzdruck (Blende):** klassisch und günstig, aber Druckverlust und begrenzter Messbereich
## Einbau
Die meisten Prinzipien brauchen ein **gleichmässiges Strömungsprofil**: gerade Rohrstrecken vor und nach dem Sensor (Ein- und Auslaufstrecken, oft einige × DN – Herstellerangabe), **Rohr voll gefüllt** und keine Luftblasen an den Elektroden.
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 2.4.4 (Induktions-Durchflussmesser), Kapitel 7.3.4 (Ultraschall-Durchflussmesser), Kapitel 7.4.6 (Coriolis-Massendurchflussmesser), Kapitel 3.7.2 (thermischer Massenstrommesser).
""",

    "tabellen": [
        {
            "titel": "📊 Messprinzipien im Vergleich",
            "kopf": ["Prinzip", "Misst", "Medien", "Stärken", "Grenzen"],
            "zeilen": [
                ["Magnetisch-induktiv", "Volumen", "leitfähige Flüssigkeiten", "kein Druckverlust, robust", "keine Gase/Öle"],
                ["Coriolis", "Masse + Dichte", "Flüssigkeiten, Gase", "sehr genau, direkt Masse", "Kosten, Druckverlust"],
                ["Ultraschall", "Volumen", "Flüssigkeiten, Gase", "Clamp-on möglich", "Blasen/Feststoffe stören"],
                ["Vortex", "Volumen", "Dampf, Gase, Flüssigkeiten", "robust, hohe Temperaturen", "Mindestgeschwindigkeit"],
                ["Thermisch", "Masse", "Gase", "kleine Durchflüsse", "abhängig von Gaszusammensetzung"],
            ],
        },
    ],

    "tipps": [
        "**Einheiten umrechnen:** 1 m³/h = 16.67 l/min = 0.278 l/s. Der Rechner macht das automatisch.",
        "**MID immer voll gefüllt einbauen** – z.B. im steigenden Rohr oder in einem Rohrbogen tief unten, nicht am höchsten Punkt (Luft sammelt sich oben).",
        "**Erdung beim MID** (Erdungsscheiben/Erdungselektrode) ist wichtig, weil die Messspannung nur im µV- bis mV-Bereich liegt.",
        "**Nennweite passend wählen:** Der Messaufnehmer kann kleiner sein als die Rohrleitung, damit die Geschwindigkeit im sinnvollen Bereich liegt (Herstellerangaben).",
        "**Coriolis und Vibrationen:** Starke Rohrschwingungen und Gasblasen in Flüssigkeiten können die Messung stören.",
    ],
    "fehler": [
        "MID für ein nicht leitfähiges Medium (Öl, Kohlenwasserstoffe) ausgewählt.",
        "Keine Einlaufstrecke nach Pumpe, Ventil oder Bogen → verzerrtes Strömungsprofil, Messfehler.",
        "Volumenstrom bei Gasen ohne Druck- und Temperaturangabe verglichen (Normvolumen vs. Betriebsvolumen).",
    ],
    "siehe_auch": ["temperatur", "messunsicherheit"],

    "rechner": ["mid"],
}
