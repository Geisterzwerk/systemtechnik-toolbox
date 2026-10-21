# Seite "Flipflops"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Flipflops und Latches",
    "reihenfolge": 10,
    "kurz": "Ein Bit speichern: RS-Latch, D-Latch, D-, JK- und T-Flipflop – pegel- oder flankengesteuert, mit Setup und Hold.",
    "stichworte": ["Flipflop", "Latch", "RS-Flipflop", "D-Flipflop", "JK-Flipflop", "T-Flipflop", "Flankensteuerung",
                   "Pegelsteuerung", "Takt", "Clock", "Setup-Zeit", "Hold-Zeit", "Metastabilität", "74HC74",
                   "74HC573", "Speicher", "Schaltwerk"],

    "grafiken": ["werkzeug_flipflop"],

    "erklaerung": """
## Stell dir vor …
Ein **Fotograf** mit Blitz: Egal, wie sich die Leute vorher bewegen – im Moment des Blitzes (Taktflanke) wird festgehalten, wie sie gerade stehen, und das Bild bleibt, bis der nächste Blitz kommt. Ein D-Flipflop macht genau das mit einem Bit. Ein Latch dagegen ist wie ein Spiegel: Solange er „offen“ ist, zeigt er jede Bewegung live.
## Grundlagen
Schaltnetze vergessen sofort – **Schaltwerke** haben einen Zustand (Speicher). Das kleinste Speicherelement ist das Flipflop (1 Bit).
- **RS-Latch** (z.B. aus zwei NOR): S setzt, R setzt zurück, `S = R = 0` speichert, `S = R = 1` ist verboten. `Q⁺ = S + ¬R·Q`
- **D-Latch** (pegelgesteuert, 74HC573): Solange `C = 1`, ist es transparent (Q = D); bei `C = 0` hält es den Wert.
- **D-Flipflop** (flankengesteuert, 74HC74): übernimmt D nur bei der steigenden Taktflanke: `Q⁺ = D`. Symbol: Dreieck am Takteingang.
- **JK-Flipflop**: wie RS, aber `J = K = 1` toggelt: `Q⁺ = J·¬Q + ¬K·Q`
- **T-Flipflop** (Toggle): `T = 1` → kippt bei jeder Flanke: `Q⁺ = T ⊕ Q` – teilt die Frequenz durch 2.

**Timing** (Datenblatt):
- **t_setup**: so lange VOR der Flanke muss D stabil sein
- **t_hold**: so lange NACH der Flanke darf sich D nicht ändern
- **t_pd**: Verzögerung Takt → Q

Wird Setup/Hold verletzt, kann das Flipflop **metastabil** werden (Ausgang kurz zwischen 0 und 1).

## Vorgehen
1. Pegel- oder Flankensteuerung? Für synchrone Schaltungen fast immer flankengesteuerte D-Flipflops.
2. Charakteristische Gleichung bzw. Tabelle des Typs nehmen.
3. Zeitdiagramm zeichnen: nur an den aktiven Flanken (bzw. bei C = 1) ändert sich Q.
4. Timing prüfen: `T_Takt ≥ t_pd + t_Logik + t_setup` (siehe Rechner „Höchste Taktfrequenz“).
5. Asynchrone Eingänge (Taster, andere Taktdomäne) über zwei Flipflops hintereinander einsynchronisieren.

## Beispiel
D-Flipflop, D wechselt zwischen zwei Flanken von 0 auf 1 und wieder auf 0:
- Q bleibt 0 – zwischen den Flanken wird D nicht beachtet.
- Ein D-Latch mit C = 1 in dieser Zeit hätte den kurzen Puls durchgelassen.

T-Flipflop mit T = 1 an einem 1-kHz-Takt: Q = 500 Hz, Tastgrad exakt 50 %.

## Praxis
- 74HC74: 2 D-Flipflops mit Set/Reset (asynchron, aktiv LOW). 74HC573/574: 8-Bit-Latch / 8-Bit-Register für Busse.
- In µC und FPGAs sind praktisch alle Register D-Flipflops; JK und T baut man daraus bei Bedarf mit Logik.
- Ein RS-Latch aus zwei NAND entprellt einen Wechsler-Taster perfekt.
- Taster oder Signale aus einer anderen Taktdomäne nie direkt in ein synchrones Schaltwerk führen – Synchronisierer verwenden.
## 🔬 Genauer hingeschaut
- **Metastabilität:** Ändert sich D genau in der verbotenen Zeit um die Taktflanke (Setup/Hold verletzt), kann das Flipflop kurz zwischen 0 und 1 „hängen“. Bei Signalen von aussen, die nicht zum Takt passen (Taster, andere Taktbereiche), schaltet man deshalb **zwei Flipflops hintereinander** (Synchronisierer) – das zweite sieht fast sicher einen stabilen Wert.
- **Taktversatz:** Kommt der Takt nicht überall gleichzeitig an, können Flipflops falsche Werte übernehmen. In Chips wird das Taktnetz darum sorgfältig gleich lang verteilt.
- **Register:** Mehrere D-Flipflops mit gemeinsamem Takt bilden ein Register, z.B. 8 Bit. Jedes Register in einem Prozessor ist im Kern so aufgebaut.
## 💡 Wusstest du?
- Die Flipflop-Schaltung wurde **1918** von William Eccles und Frank Jordan erfunden – damals mit zwei Elektronenröhren.
""",

    "tipps": [
        "Flankengesteuert erkennt man im Symbol am kleinen Dreieck am Takteingang (C1).",
        "Das JK-Flipflop kann alles: J = D und K = ¬D ergibt ein D-Flipflop, J = K = T ein T-Flipflop.",
    ],
    "fehler": [
        "D-Latch statt D-Flipflop verwendet – während C = 1 laufen Störungen ungehindert durch.",
        "RS-Latch mit S = R = 1 betrieben – nach dem Loslassen ist der Zustand zufällig.",
        "Setup-Zeit verletzt (zu langsame Logik vor dem Flipflop) – sporadische Fehler, die nur bei Wärme auftreten.",
    ],
    "siehe_auch": ["zaehler", "schieberegister", "zaehler_entwurf"],
    "rechner": ["fmax_schaltwerk", "frequenzteiler"],
}
