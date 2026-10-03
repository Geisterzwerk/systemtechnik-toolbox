# Seite "Darlington"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Darlington-Schaltung",
    "reihenfolge": 10,
    "kurz": "Zwei Transistoren als einer: Stromverstärkung β1 · β2, dafür 1.4 V an der Basis und nie unter 0.9 V U_CE.",
    "stichworte": ["Darlington", "Darlington-Transistor", "Stromverstärkung", "ULN2003", "TIP120", "BD679",
                   "Sziklai", "Komplementär-Darlington", "Leistungstransistor", "Treiber", "Relaistreiber"],

    "grafiken": ["schaltung_darlington"],

    "erklaerung": """
## Funktion
Der Emitterstrom des ersten Transistors (T1) ist der Basisstrom des zweiten (T2), die Kollektoren sind verbunden:
- Stromverstärkung `β ≈ β1 · β2` (genau β1·β2 + β1 + β2) – typisch 1000 … 30 000
- Basis-Emitter-Spannung `U_BE ≈ 2 · 0.7 V = 1.4 V`
- **Keine echte Sättigung**: T2 bekommt seinen Basisstrom über T1, deshalb `U_CE ≥ U_CE,sat(T1) + U_BE(T2) ≈ 0.9 V` (Datenblatt oft 1 … 2 V)

Vorteil: ein µC-Pin (wenige mA) schaltet Ampere. Nachteil: mehr Verlust und langsameres Abschalten als ein Einzeltransistor oder MOSFET.

## Dimensionierung
1. Laststrom I und minimales β aus dem Datenblatt (bei diesem Strom!).
2. Basisstrom mit Übersteuerung 2: `I_B = 2 · I / β`, `R_B = (U_St − 1.4 V) / I_B` (Rechner „Darlington oder Einzeltransistor?“).
3. Verlust: `P ≈ U_CE · I` mit U_CE ≈ 0.9 … 1.5 V – bei 2 A also 2 … 3 W → Kühlkörper.
4. Vergleich: MOSFET mit 50 mΩ hätte bei 2 A nur 0.2 W – für grosse Ströme heute meist die bessere Wahl.
5. Induktive Lasten (Relais, Motor): Freilaufdiode (in ULN2003 schon eingebaut).

## Betriebszustände
- **Aus**: I_B = 0, kein Strom.
- **Ein**: T2 im Quasi-Sättigungsbereich, U_CE ≈ 0.9 V.
- **Zu wenig Basisstrom**: nur β · I_B fliesst, U_CE gross → sehr viel Verlust.
- **Abschalten**: Die Basis von T2 entlädt sich langsam (Widerstand B–E im Gehäuse hilft) – Darlingtons sind langsam.

## Messpunkte
- U_CE im eingeschalteten Zustand (soll ≈ 0.9 … 1.2 V sein, nicht mehr).
- U_BE ≈ 1.2 … 1.5 V am Eingang.
- Gehäusetemperatur unter Volllast.

## Grenzfälle
- Hoher Strom: β sinkt, U_CE steigt – Datenblattkurven beachten.
- 3.3-V-µC: Nach 1.4 V U_BE bleibt wenig Spannung für R_B → R_B klein, Strom aus dem Pin prüfen.
- Hohe Temperatur: Leckströme werden mit β1·β2 verstärkt → Basis-Emitter-Widerstand nötig.
""",

    "tipps": [
        "ULN2003/ULN2803 sind 7 bzw. 8 Darlington-Treiber mit Freilaufdioden in einem Gehäuse – ideal für Relais und Schrittmotoren.",
        "Bei 3.3-V-Logik und Strömen über 1 A ist ein Logic-Level-MOSFET fast immer besser.",
    ],
    "fehler": [
        "U_CE,sat eines normalen Transistors (0.2 V) für den Darlington angenommen – die Verlustleistung wird unterschätzt.",
        "R_B wie beim Einzeltransistor mit 0.7 V gerechnet – der Basisstrom ist kleiner als gedacht.",
    ],
    "siehe_auch": ["transistorschalter", "lasten_ansteuern", "gegentakt_endstufe", "mosfet_schalter"],
    "rechner": ["darlington", "basiswiderstand"],
}
