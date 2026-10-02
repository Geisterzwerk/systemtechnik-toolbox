# Seite "Decoder und Encoder"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Decoder, Encoder und 7-Segment-Anzeige",
    "reihenfolge": 30,
    "kurz": "Binärzahl → 1-aus-n (Decoder), 1-aus-n → Binärzahl (Encoder) und Ziffer → Segmente – mit Adressdecodierung.",
    "stichworte": ["Decoder", "Dekoder", "Encoder", "Prioritäts-Encoder", "74HC138", "74HC148", "74HC4511",
                   "7-Segment", "Siebensegment", "Chip-Select", "Adressdecoder", "1-aus-n", "gemeinsame Anode",
                   "gemeinsame Kathode", "BCD"],

    "grafiken": ["werkzeug_decoder"],

    "erklaerung": """
## Grundlagen
- **Decoder** `n : 2^n`: Aus einer n-Bit-Zahl wird genau EIN aktiver Ausgang (1-aus-n). Der 74HC138 (3:8) hat Ausgänge, die aktiv LOW sind (`¬Y0 … ¬Y7`), und drei Freigabe-Eingänge.
- **Encoder** `2^n : n`: umgekehrt – welcher Eingang aktiv ist, wird als Binärzahl ausgegeben. Ein **Prioritäts-Encoder** (74HC148) gibt den HÖCHSTEN aktiven Eingang aus und meldet mit GS, ob überhaupt einer aktiv ist.
- **7-Segment-Decoder** (74HC4511 für BCD): schaltet für jede Ziffer die Segmente a … g. Gemeinsame Kathode: Segment an = HIGH; gemeinsame Anode: Segment an = LOW.

**Adressdecodierung**: Die obersten k Adressbits gehen an einen Decoder, jeder Ausgang wählt einen Baustein (Chip-Select, `¬CS`). Jeder Baustein bekommt einen Block von `2^(N−k)` Adressen.

## Vorgehen
Adressbereiche bestimmen:
1. Adressbreite N und Anzahl Decoder-Eingänge k festlegen.
2. Blockgrösse `2^(N−k)`, Ausgang i deckt `i · Block … (i + 1) · Block − 1` ab.
3. Decoder an die Adressleitungen `A(N−1) … A(N−k)`, die Bausteine an `A(N−k−1) … A0`.

7-Segment:
1. Anzeigetyp prüfen (gemeinsame Anode oder Kathode).
2. Segmente der Ziffer bestimmen, Pegel entsprechend setzen.
3. Je Segment einen Vorwiderstand (nicht einen gemeinsamen!).

## Beispiel
16-Bit-Adressraum (64 Ki), 74HC138 an A15 … A13:
- Block = 2^13 = 8192 Adressen (8 Ki)
- `¬CS0`: 0x0000 … 0x1FFF, `¬CS1`: 0x2000 … 0x3FFF, …, `¬CS7`: 0xE000 … 0xFFFF

Ziffer 7 auf einer Anzeige mit gemeinsamer Kathode: a, b, c = HIGH, d … g = LOW.

## Praxis
- 74HC138 mit Freigaben `E1`, `¬E2`, `¬E3`: Mehrere Decoder lassen sich zu 4:16 und mehr kaskadieren.
- Tastaturen und Interrupt-Controller nutzen Prioritäts-Encoder: Bei mehreren gedrückten Tasten gewinnt die höchste.
- Mehrstellige 7-Segment-Anzeigen werden gemultiplext (eine Stelle nach der anderen, > 100 Hz) – spart Leitungen, braucht aber höhere Spitzenströme.
""",

    "tipps": [
        "Aktiv-LOW-Ausgänge erkennt man am Strich (¬Y, /Y, Y#) und am Kreis im Schaltsymbol.",
        "Die Buchstaben b und d werden auf 7-Segment-Anzeigen klein dargestellt, sonst wären sie mit 8 und 0 verwechselbar.",
    ],
    "fehler": [
        "Gemeinsame Anode wie gemeinsame Kathode angesteuert – die Anzeige zeigt das Negativ der Ziffer.",
        "Einen gemeinsamen Vorwiderstand für alle Segmente verwendet – die Helligkeit hängt von der Ziffer ab.",
        "Freigabe-Eingänge des 74HC138 offen gelassen – kein Ausgang wird aktiv.",
    ],
    "siehe_auch": ["multiplexer", "zahlensysteme_codes", "ausgangstypen"],
    "rechner": ["siebensegment", "adressdecoder"],
}
