# Seite "Gegentakt-Endstufe"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Emitterfolger (Grundbaustein): Seite "emitterfolger" (03_transistor_mosfet).

THEMA = {
    "titel": "Gegentakt-Endstufe Klasse B und AB",
    "reihenfolge": 20,
    "kurz": "Zwei Emitterfolger teilen sich die Halbwellen: hoher Wirkungsgrad, aber ohne Vorspannung eine Lücke im Nulldurchgang.",
    "stichworte": ["Gegentakt", "Push-Pull", "Endstufe", "Klasse B", "Klasse AB", "Klasse A", "Übernahmeverzerrung",
                   "Crossover", "Klirrfaktor", "THD", "Ruhestrom", "Komplementär", "Audioverstärker", "Wirkungsgrad",
                   "Leistungsverstärker"],

    "grafiken": ["schaltung_gegentakt"],

    "erklaerung": """
## Funktion
Ein NPN-Emitterfolger liefert die **positive** Halbwelle aus +U_B, ein PNP-Emitterfolger die **negative** aus −U_B. Beide Basen werden vom gleichen Signal angesteuert, die Emitter treiben gemeinsam die Last.
- **Klasse B** (Basen direkt verbunden): Ein Transistor leitet erst ab |u_e| > 0.65 V. Um den Nulldurchgang entsteht eine Lücke – **Übernahmeverzerrung** (Crossover). Bei kleinen Signalen ist der Klirrfaktor sehr hoch.
- **Klasse AB**: Zwei Dioden (oder ein U_BE-Vervielfacher) zwischen den Basen erzeugen eine Vorspannung ≈ 1.3 V. Beide Transistoren leiten schon mit einem kleinen **Ruhestrom**, die Lücke verschwindet.
- **Klasse A** (zum Vergleich): dauernd voller Ruhestrom, Wirkungsgrad höchstens 25 %.

Leistung (Klasse B, ±U_B, Amplitude û an R_L):
- `P_aus = û² / (2 · R_L)`
- `P_auf = 2 · U_B · û / (π · R_L)`
- `η = π/4 · û / U_B` – höchstens **78.5 %** bei Vollaussteuerung
- Verlust beider Transistoren am grössten bei `û = 2 · U_B / π`: `P_V,max = 2 · U_B² / (π² · R_L)`

## Dimensionierung
1. Ausgangsleistung und Last festlegen → `û = √(2 · P · R_L)`, dann `U_B ≥ û + 1 … 3 V` (Sättigung, Emitterwiderstände).
2. Spitzenstrom `û / R_L` → Transistoren nach Strom, Spannung (2 · U_B!) und Verlustleistung auswählen.
3. Kühlkörper nach `P_V,max / 2` je Transistor (Rechner „Gegentakt-Endstufe“).
4. Klasse AB: Vorspannung über Dioden, die thermisch mit den Endtransistoren gekoppelt sind (sonst steigt der Ruhestrom mit der Temperatur – thermisches Weglaufen).
5. Emitterwiderstände (0.1 … 0.47 Ω) stabilisieren den Ruhestrom.
6. Gegenkopplung über einen OPV (Treiberstufe) senkt den Klirrfaktor weiter.

## Betriebszustände
- **Leerlauf (Klasse AB)**: kleiner Ruhestrom durch beide Transistoren.
- **Positive Halbwelle**: NPN leitet, PNP sperrt.
- **Negative Halbwelle**: PNP leitet, NPN sperrt.
- **Übersteuerung**: Ausgang begrenzt bei ≈ ±(U_B − 1 V) – Rechteck-artige Verzerrung, hoher Klirrfaktor.

## Messpunkte
- **M1** (Ausgang) zusammen mit dem Eingang: Lücke im Nulldurchgang bei Klasse B sofort sichtbar (kleines Signal einspeisen).
- Ruhestrom über den Spannungsabfall an den Emitterwiderständen.
- Klirrfaktor mit FFT des Oszilloskops oder einem Audio-Analyzer.
- Temperatur der Transistoren bei Vollaussteuerung und bei û ≈ 0.64 · U_B (Maximum der Verluste).

## Grenzfälle
- Last kurzgeschlossen: Strom nur durch die Transistoren begrenzt → Strombegrenzung vorsehen.
- Zu grosse Vorspannung: Ruhestrom hoch, Transistoren werden warm, im Extremfall thermisches Weglaufen.
- Einzelversorgung: Ausgang auf U_B/2 legen und Last über einen grossen Koppelkondensator anschliessen.
""",

    "tipps": [
        "Übernahmeverzerrung hört man besonders bei leiser Musik – das Diagramm „Kennlinie“ zeigt die Lücke direkt.",
        "Fertige Audio-Endstufen-ICs (z.B. TDA- oder LM386-Familie) enthalten Vorspannung, Schutz und Gegenkopplung.",
    ],
    "fehler": [
        "Klasse B ohne Vorspannung für Audio verwendet – starke Verzerrung bei kleinen Lautstärken.",
        "Kühlkörper nur für Vollaussteuerung berechnet – die grössten Verluste entstehen bei etwa ⅔ Aussteuerung.",
        "Vorspannungsdioden nicht thermisch an die Endtransistoren gekoppelt – der Ruhestrom läuft weg.",
    ],
    "siehe_auch": ["emitterfolger", "darlington_schaltung", "opv_verstaerker"],
    "rechner": ["endstufe", "emitterfolger"],
}
