# Seite "Busabschluss RS-485 / CAN"  -> Vorlage: schaltungen/inhalte/_vorlage.py
# Protokoll und Pegel von UART/RS-485: Digitaltechnik "uart" (06_busse_speicher).

THEMA = {
    "titel": "Busabschluss RS-485 und CAN",
    "reihenfolge": 60,
    "kurz": "Lange Leitungen reflektieren Signale – 120 Ω an beiden Enden, Fail-safe-Vorspannung und Split-Abschluss.",
    "stichworte": ["RS-485", "CAN", "Busabschluss", "Abschlusswiderstand", "Terminierung", "Termination",
                   "120 Ohm", "Wellenwiderstand", "Reflexion", "Leitung", "Fail-safe", "Bias", "Split-Abschluss",
                   "Modbus", "Feldbus", "verdrillt", "Twisted Pair"],

    "grafiken": ["schaltung_busabschluss"],

    "erklaerung": """
## Funktion
Eine verdrillte Zweidrahtleitung hat einen **Wellenwiderstand** Z0 (RS-485- und CAN-Kabel: ≈ 120 Ω). Ein Signal braucht etwa **5 ns pro Meter**. Kommt eine Flanke am Leitungsende an, wird ein Teil reflektiert:
- Reflexionsfaktor `Γ = (R − Z0) / (R + Z0)`
- offenes Ende Γ = +1 (volle Reflexion), Abschluss mit R = Z0: Γ = 0 (keine Reflexion)

Die reflektierte Welle läuft zurück, wird am niederohmigen Sender wieder reflektiert, und der Empfänger sieht ein **Klingeln** um den Endwert. Bei langen Leitungen und schnellen Flanken entstehen falsche Bits.

**Abschluss**: je ein Widerstand **R_T = Z0 = 120 Ω** an den **beiden Enden** des Busses – nicht an jedem Teilnehmer. Zusammen ergeben sie 60 Ω Last für den Sender.

**RS-485 Fail-safe**: Sendet niemand, ist der Bus hochohmig – die Empfänger sähen Rauschen. Ein Pull-up an A und ein Pull-down an B erzeugen eine Ruhe-Differenzspannung `U_AB ≥ 200 mV` (sicher „1“).

**CAN Split-Abschluss**: 2 × 60 Ω in Reihe mit einem Kondensator (z.B. 4.7 nF) von der Mitte nach Masse. Für das Differenzsignal sind das 120 Ω, Gleichtaktstörungen werden zusätzlich nach Masse abgeleitet.

## Dimensionierung
1. Ist die Leitung „lang“? Laufzeit `t_d = l / (2·10⁸ m/s)`. Faustregel: Abschluss nötig, wenn die Leitung länger als etwa `t_r · v / 6` ist (t_r = Anstiegszeit des Senders, Datenblatt). Rechner „Busabschluss RS-485 / CAN“.
2. R_T = Wellenwiderstand des Kabels (Datenblatt, meist 120 Ω), an beiden physikalischen Enden.
3. Fail-safe (RS-485): `U_AB = U_B · 60 Ω / (2 · R_bias + 60 Ω) ≥ 200 mV` → bei 5 V höchstens 720 Ω, üblich 560 … 680 Ω (nur EINMAL am Bus). Moderne Transceiver haben „true fail-safe“ eingebaut.
4. Topologie: Linie mit kurzen Stichleitungen, kein Stern.
5. Bei sehr langen Leitungen die Baudrate senken (RS-485: bis 1200 m bei ≤ 100 kBit/s).

## Betriebszustände
- **Ohne Abschluss, lange Leitung**: Stufen und Überschwingen am Empfänger, bei hoher Baudrate Bitfehler.
- **Richtig abgeschlossen**: Signal springt sauber auf den Endwert (etwas kleiner wegen der 60-Ω-Last).
- **Zu viele Abschlüsse** (an jedem Teilnehmer): Last zu niederohmig, Sender kann den Pegel nicht halten.
- **Ruhe ohne Fail-safe**: Empfänger liefert Zufallsdaten (UART sieht Startbits).

## Messpunkte
- Bus abschalten, zwischen A und B messen: **60 Ω** bei korrektem Abschluss (120 Ω: einer fehlt, 40 Ω: einer zu viel).
- Mit dem Oszilloskop differenziell (zwei Tastköpfe, Math A − B) am fernsten Teilnehmer: Flanken ohne Treppen?
- Ruhespannung A − B bei abgeschalteten Sendern (Fail-safe ≥ 200 mV).

## Grenzfälle
- Kurze Leitung (wenige Meter) bei niedriger Baudrate: Abschluss bringt wenig, schadet aber auch kaum (mehr Strom).
- Falscher Kabeltyp (z.B. ungeschirmtes Netzkabel mit Z0 ≈ 80 Ω): Abschluss passt nicht, Restreflexionen.
- Abschluss in der Mitte des Busses: Die Enden bleiben offen – reflektiert trotzdem.
- Fehlende Masseverbindung zwischen den Teilnehmern: Gleichtaktspannung verlässt den erlaubten Bereich (−7 … +12 V bei RS-485).
""",

    "tipps": [
        "Schnelltest: Spannung weg, Ohmmeter zwischen A und B – 60 Ω heisst „beide Abschlüsse da“.",
        "Viele Geräte haben einen DIP-Schalter oder Jumper für den Abschluss – nur an den beiden Bus-Enden einschalten.",
    ],
    "fehler": [
        "Abschlusswiderstand an jedem Teilnehmer gesetzt – der Bus ist viel zu niederohmig.",
        "Nur an einem Ende abgeschlossen – das andere Ende reflektiert weiter.",
        "Sternverdrahtung mit langen Abzweigen statt Linie – jeder Abzweig ist eine offene Leitung.",
        "Fail-safe-Widerstände an mehreren Stellen eingebaut – zusammen zu niederohmig für die Sender.",
    ],
    "siehe_auch": ["uart", "pegelwandler_schaltung", "optokoppler_schaltung"],
    "rechner": ["busabschluss", "uart_timing"],
}
