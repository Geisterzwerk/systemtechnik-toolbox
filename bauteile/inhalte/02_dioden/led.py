# =============================================================================
# Thema: LED  (Kategorie: Dioden)
# NUR DATEN - dargestellt von bauteile/engine/seite.py
# Rechner: led_vorwiderstand (widerstand_rechner.py) + halbleiter_rechner.py
# =============================================================================

THEMA = {
    "titel": "LED",
    "reihenfolge": 3,
    "kurz": "Leuchtdiode: eine Diode, die beim Stromfluss Licht aussendet – immer mit Strombegrenzung betreiben!",
    "stichworte": ["led", "leuchtdiode", "light emitting diode", "vorwiderstand", "konstantstrom", "pwm",
                   "dimmen", "helligkeit", "durchlassspannung", "rgb", "power-led", "ir", "infrarot",
                   "optokoppler", "anode", "kathode", "farbe", "wellenlänge"],

    "steckbrief": {
        "symbol": "led",
        "zeilen": [
            ("Anschlüsse", "Anode = langes Bein (+) · Kathode = kurzes Bein, abgeflachte Seite (−)"),
            ("Durchlassspannung", "rot/gelb ≈ 1.8–2.2 V · grün ≈ 2–3.2 V · blau/weiss ≈ 2.8–3.4 V · IR ≈ 1.2–1.5 V"),
            ("Typischer Strom", "Standard-LED 2–20 mA · Power-LED 350 mA … mehrere A"),
            ("Sperrspannung", "klein, oft nur **5 V** – LEDs vertragen kaum Sperrspannung"),
            ("Strombegrenzung", "**immer nötig**: Vorwiderstand oder Konstantstromquelle"),
            ("Helligkeit", "hängt vom **Strom** ab, nicht von der Spannung"),
        ],
    },

    "erklaerung": """
## Wie funktioniert eine LED?
Im pn-Übergang treffen Elektronen und Löcher aufeinander. Bei der LED wird die frei werdende Energie als **Licht** abgegeben. Das Halbleitermaterial bestimmt die **Farbe** – und damit auch die **Durchlassspannung**: Blaues Licht hat mehr Energie als rotes, deshalb braucht eine blaue LED rund 3 V, eine rote nur rund 2 V. Weisse LEDs sind meist blaue LEDs mit einer gelben Leuchtstoffschicht.
## Warum braucht eine LED einen Vorwiderstand?
Die Kennlinie einer LED ist, wie bei jeder Diode, **sehr steil**: Schon ein wenig mehr Spannung führt zu viel mehr Strom. Dazu kommt, dass Uf mit der Temperatur **sinkt** – wird die LED warm, steigt der Strom weiter. Ohne Begrenzung zerstört sie sich selbst. Deshalb steuert man eine LED über den **Strom**:
- **Vorwiderstand:** `R = (Ub − Uf) / I_LED` – einfach und günstig
- **Konstantstromquelle:** für Power-LEDs und wenn die Helligkeit trotz schwankender Versorgung gleich bleiben soll
## Helligkeit einstellen (Dimmen)
- **Strom verändern:** funktioniert, verschiebt aber bei manchen LEDs leicht die Farbe
- **PWM (Pulsweitenmodulation):** Die LED wird sehr schnell ein- und ausgeschaltet. Das Auge sieht den Mittelwert. Ab ca. **200 Hz** ist kein Flackern mehr sichtbar (bei Kameras eher > 1 kHz).
## LEDs in Reihe oder parallel?
- **Reihe:** Die Spannungen addieren sich, durch alle fliesst derselbe Strom → gleiche Helligkeit, ein Widerstand reicht.
- **Parallel:** Jede LED braucht ihren **eigenen** Vorwiderstand – sonst übernimmt die LED mit dem kleinsten Uf fast den ganzen Strom.
## Ansteuerung vom Mikrocontroller
Ein Pin liefert typisch ca. 10–20 mA (Datenblatt!). Für mehr Strom oder viele LEDs schaltet man über einen **Transistor oder MOSFET** (siehe dort).
## 📚 Vertiefung
Zastrow, *Elektronik*: Kapitel 2 (Halbleiterdiode, Kennlinien). Rechner „LED-Vorwiderstand“ auch auf der Seite Widerstand.
""",

    "tabellen": [
        {
            "titel": "📊 Typische Werte nach Farbe",
            "kopf": ["Farbe", "Wellenlänge ca.", "Uf typisch", "Bemerkung"],
            "zeilen": [
                ["Infrarot", "850–940 nm", "1.2–1.5 V", "unsichtbar – mit Handykamera prüfbar"],
                ["Rot", "620–630 nm", "1.8–2.2 V", ""],
                ["Gelb / Orange", "590–610 nm", "2.0–2.2 V", ""],
                ["Grün", "520–570 nm", "2.0–3.2 V", "alte Typen ≈ 2 V, moderne (InGaN) ≈ 3 V"],
                ["Blau", "460–470 nm", "2.8–3.4 V", ""],
                ["Weiss", "–", "2.8–3.4 V", "blaue LED + Leuchtstoff"],
                ["UV", "365–405 nm", "3.2–4.0 V", "⚠ nicht direkt hineinschauen"],
            ],
            "hinweis": "Richtwerte – das Datenblatt der konkreten LED ist massgebend.",
        },
    ],

    "tipps": [
        "**Polung erkennen:** langes Bein = Anode (+). Im Gehäuse ist die Kathode meist die grössere „Fahne“. Die flache Seite am Rand markiert die Kathode.",
        "**Nicht an den Strom-Maximalwert gehen:** Moderne LEDs sind schon bei 2–5 mA hell genug für Anzeigen. Weniger Strom = längere Lebensdauer, weniger Wärme.",
        "**LED testen:** Diodentest am Multimeter lässt viele LEDs schwach leuchten. Blaue und weisse brauchen oft mehr Spannung als das Multimeter liefert.",
        "**Keine Sperrspannung:** LEDs vertragen oft nur 5 V in Sperrrichtung. An Wechselspannung eine normale Diode antiparallel schalten.",
        "**Power-LEDs brauchen Kühlung:** Nur ein Teil der Leistung wird zu Licht, der Rest wird Wärme. Zu heiss → Helligkeit sinkt, Lebensdauer bricht ein.",
        "**Infrarot-LED prüfen:** Viele Handykameras (vor allem die Frontkamera) zeigen IR-Licht als violettes Leuchten.",
        "**PWM-Flackern:** Unter ca. 200 Hz nimmt man Flackern wahr, auf Videos sieht man es noch bei höheren Frequenzen.",
    ],
    "fehler": [
        "LED direkt an 5 V oder an eine Batterie ohne Vorwiderstand → sofort defekt oder stark vorgealtert.",
        "Mehrere LEDs parallel an einem gemeinsamen Vorwiderstand → ungleiche Helligkeit, eine LED überlastet.",
        "Mit der falschen Durchlassspannung gerechnet (z.B. 2 V für eine weisse LED) → zu viel oder zu wenig Strom.",
        "LED verkehrt herum eingelötet → leuchtet nicht (meist bleibt sie heil, solange die Sperrspannung klein ist).",
    ],
    "siehe_auch": ["diode", "widerstand", "bipolartransistor", "mosfet"],

    "rechner": ["led_vorwiderstand", "diode_kennlinie", "bjt_schalter"],
}
