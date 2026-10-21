# Seite "Eingangsschutz"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Eingangsschutz (Klemmdioden + Serienwiderstand)",
    "reihenfolge": 20,
    "kurz": "Ein Widerstand und zwei Dioden schützen einen IC-Eingang vor Überspannung.",
    "stichworte": ["Eingangsschutz", "Klemmdiode", "Clamp", "ESD", "Injektionsstrom", "Serienwiderstand",
                   "BAT54S", "Mikrocontroller", "Überspannung", "Schutzdiode"],

    "grafiken": ["schaltung_eingangsschutz"],

    "erklaerung": """
## Stell dir vor …
Ein Damm mit **Überlaufrinnen** auf beiden Seiten: Steigt das Wasser über die Dammkrone, läuft es in die Rinne ab, statt den Damm zu zerstören. Die Schutzdioden am Eingang leiten Überspannung in die Versorgung oder nach GND ab. Der Vorwiderstand sorgt dafür, dass dabei nur so viel Wasser fliesst, wie die Rinnen schlucken können.
## Funktion
Jeder CMOS-Pin hat interne **ESD-Dioden**: eine vom Pin zu U_DD, eine von GND zum Pin. Steigt die Spannung über `U_DD + U_F` (oder sinkt unter `−U_F`), leiten sie und halten den Pin fest. Den Strom begrenzt nur der **Serienwiderstand R**:
- `U_Pin = U_DD + U_F`   bzw.   `−U_F`
- `I_inj = (U_ein − U_Pin) / R`   (Injektionsstrom)

Die internen Dioden sind nur für kurze ESD-Pulse gebaut, als Dauerstrom erlauben die meisten Mikrocontroller nur **±1 … 5 mA** pro Pin (Datenblatt: „injection current“, „clamp current“).

## Dimensionierung
1. Grösste mögliche Spannung am Eingang festlegen (z.B. 24-V-Signal einer SPS, Fehlverdrahtung).
2. `R ≥ (U_max − U_DD − U_F) / I_inj,max` – nächst grösseren Normwert wählen.
3. Negative Spannung genauso: `R ≥ (|U_min| − U_F) / I_inj,max`.
4. Dauerleistung in R prüfen: `P = (U_max − U_Pin)² / R`.
5. Bei grösseren Strömen **externe Schottky-Dioden** (z.B. BAT54S) einsetzen: Sie leiten bei ≈ 0.3 V früher als die internen und übernehmen den Strom.

## Betriebszustände
- **Normal** (0 … U_DD): Dioden sperren, R wirkt nur zusammen mit der Pin-Kapazität als kleiner Tiefpass.
- **Überspannung**: obere Diode leitet, der Strom fliesst **in die Versorgung U_DD**.
- **Unterspannung**: untere Diode leitet, der Strom kommt aus GND, der Pin liegt bei ca. −0.3 … −0.7 V.

## Messpunkte
- **M1** (Pin) gegen GND: im Fehlerfall höchstens U_DD + 0.3 … 0.7 V.
- Injektionsstrom: Spannung an R messen, durch R teilen.
- **U_DD im Standby beobachten**: Ist der Injektionsstrom grösser als der Eigenverbrauch, steigt U_DD an (Rückspeisung) – der Spannungsregler kann das nicht verhindern, weil er nur Strom liefern, nicht aufnehmen kann.

## Grenzfälle
- `R → 0`: Die Quelle treibt grosse Ströme in die ESD-Dioden → Latch-up oder zerstörter Pin.
- `R` sehr gross: Gut geschützt, aber ADC-Messungen werden falsch (der Abtastkondensator lädt nicht schnell genug) → Kondensator direkt am Pin.
- Ausgeschaltetes Gerät (U_DD = 0): Ein Signal am Eingang versorgt den ganzen Chip über die ESD-Diode („phantom powering“) – R begrenzt auch das.
## 🔬 Genauer hingeschaut
- **Interne Dioden sind schwach:** Fast jeder IC-Pin hat eingebaute Schutzdioden gegen elektrostatische Entladungen. Der erlaubte Dauerstrom durch sie (Injektionsstrom) steht im Datenblatt und ist meist klein – deshalb der Vorwiderstand.
- **Externe Schottky-Dioden:** Sie leiten schon bei ca. 0.3 V und damit früher als die internen Si-Dioden. So übernimmt die externe Diode den Strom, und die internen Dioden bleiben geschont.
- **ESD-Prüfung:** Elektronik wird mit nachgebildeten Entladungen getestet, z.B. dem Human Body Model (ein Mensch, der sich aufgeladen hat). Datenblätter geben an, bis zu wie vielen Kilovolt ein Pin das aushält.
## 💡 Wusstest du?
- Wer über einen Teppich läuft, kann sich auf mehrere Tausend Volt aufladen. Den Funken an der Türklinke spürt man erst ab einigen Kilovolt – Halbleiter können schon an kleineren Entladungen sterben, die man gar nicht bemerkt.
""",

    "tipps": [
        "Für Analogeingänge: R (1 … 10 kΩ) + Kondensator am Pin (z.B. 10 nF) – der Kondensator liefert die Ladung für den ADC und filtert Störungen.",
        "Für Industrie-Eingänge (24 V) besser einen Spannungsteiler oder Optokoppler verwenden – der Eingangsschutz ist für Fehlerfälle, nicht für den Dauerbetrieb.",
        "Im Datenblatt nach „absolute maximum ratings: input voltage“ und „injected current“ suchen.",
    ],
    "fehler": [
        "Ohne Serienwiderstand direkt an ein 5-V- oder 12-V-Signal angeschlossen – ein 3.3-V-Pin stirbt sofort.",
        "Rückspeisung in U_DD übersehen: Das Gerät „läuft“ teilweise, obwohl es ausgeschaltet ist.",
        "Z-Diode als Schutz eines Analogeingangs: Ihr Leckstrom verfälscht schon unterhalb von U_Z die Messung.",
    ],
    "siehe_auch": ["diodenbegrenzung", "tvs_schutz", "pull_up_down"],
    "rechner": ["eingangsschutz", "spannungsteiler"],
}
