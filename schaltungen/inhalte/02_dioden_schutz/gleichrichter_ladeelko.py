# Seite "Gleichrichter mit Ladeelko"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Gleichrichter mit Ladeelko (Einweg, Brücke, Mittelpunkt)",
    "reihenfolge": 50,
    "kurz": "Aus Wechselspannung wird eine pulsierende Gleichspannung, der Elko glättet sie.",
    "stichworte": ["Gleichrichter", "Einweggleichrichter", "Brückengleichrichter", "Graetz", "Mittelpunktschaltung",
                   "Ladeelko", "Siebelko", "Welligkeit", "Brummspannung", "Netzteil"],

    "grafiken": ["schaltung_gleichrichter"],

    "erklaerung": """
## Funktion
Dioden lassen Strom nur in eine Richtung durch. Hinter dem Gleichrichter lädt sich der **Ladeelko** auf den Spitzenwert auf und versorgt die Last, solange die Trafospannung darunter liegt.
- **Einweg** (1 Diode): nur die positive Halbwelle wird genutzt. Brummfrequenz = f (50 Hz).
- **Brücke / Graetz** (4 Dioden): beide Halbwellen, immer 2 Dioden im Strompfad. Brumm = 2 · f (100 Hz).
- **Mittelpunkt** (2 Dioden, Trafo mit Mittelanzapfung): beide Halbwellen, nur 1 Diode im Pfad, braucht aber die doppelte Wicklung.

Kennwerte (U2 = Effektivwert, beim Mittelpunkt einer Wicklungshälfte):
- `Û = U2 · √2`,   Leerlauf `U_DC ≈ Û − n · U_F` (n = Dioden im Strompfad)
- Welligkeit `ΔU ≈ I / (f_Brumm · C)`
- Sperrspannung je Diode: Brücke `Û`, Einweg und Mittelpunkt `2 · Û`

## Dimensionierung
1. U2 wählen: Nach Abzug von Diodenspannung und Welligkeit muss das Minimum noch über dem Bedarf liegen (Regler: Dropout beachten!) – auch bei −10 % Netzspannung.
2. Elko: `C ≥ I / (f_Brumm · ΔU_erlaubt)`. Faustwert Brücke: ca. 1000 … 2000 µF pro Ampere.
3. Elko-Spannungsfestigkeit: ≥ Û · 1.1 (Netz +10 %) plus Reserve, Leerlaufspannung des Trafos ist höher als die Nennspannung.
4. Dioden: mittlerer Strom (Brücke: I/2 je Diode), Sperrspannung mit Reserve (1.5 … 2 ×), **Spitzenstrom beim Einschalten** (leerer Elko) beachten.
5. Elko-Rippelstrom (Datenblatt) prüfen – er ist deutlich grösser als der Laststrom.

## Betriebszustände
- **Leerlauf**: Elko auf Û − n · U_F, fast keine Welligkeit.
- **Last**: Sägezahn – kurzes Nachladen nahe der Spitze, dazwischen lineares Entladen.
- **Einschalten**: Der leere Elko wirkt wie ein Kurzschluss – hoher Einschaltstrom durch Dioden und Trafo (träge Sicherung!).

## Messpunkte
- U_DC am Elko mit Multimeter (DC): zeigt den Mittelwert.
- Welligkeit mit dem Oszilloskop, Kopplung **AC** und kleiner Volt/div: Spitze-Spitze-Wert = ΔU, Frequenz 50 oder 100 Hz.
- 50 Hz Brumm bei einer Brückenschaltung → eine Diode ist defekt (dann arbeitet nur noch ein Halbwellenzweig).

## Grenzfälle
- Ohne Elko: pulsierende Gleichspannung, Mittelwert `0.9 · U2` (Brücke) bzw. `0.45 · U2` (Einweg).
- Sehr grosser Elko: kleine Welligkeit, aber sehr kurze, hohe Ladestromspitzen (Trafo- und Diodenerwärmung, Oberwellen im Netz).
- Last grösser als geplant: Welligkeit wächst, der Spannungsregler fällt aus der Regelung (Brumm am Ausgang).
""",

    "tipps": [
        "Ein kleiner Folienkondensator (100 nF) parallel zum Elko filtert hohe Frequenzen, die der Elko schlecht kann.",
        "Bei Netztrafos ist die Leerlaufspannung oft 10 … 20 % über der Nennspannung – Elko und Regler danach auslegen.",
        "Messungen auf der Netzseite nur mit Trenntrafo und geeigneten Tastköpfen – Lebensgefahr!",
    ],
    "fehler": [
        "Elko verpolt eingebaut – er wird heiss und kann platzen.",
        "Sperrspannung beim Einweg- und Mittelpunktgleichrichter zu knapp: Die Diode sieht 2 · Û, nicht Û.",
        "Oszilloskop-Masse an den Minuspol einer Brücke am Netz angeschlossen – Kurzschluss über die Schutzerde.",
        "Welligkeitsformel mit 50 Hz statt 100 Hz bei der Brücke gerechnet – Elko doppelt so gross wie nötig (oder umgekehrt).",
    ],
    "siehe_auch": ["z_stabilisierung", "verpolschutz"],
    "rechner": ["gleichrichter", "netzteil", "diode_verlust"],
}
