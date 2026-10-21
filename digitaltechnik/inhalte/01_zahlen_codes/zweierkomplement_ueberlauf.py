# Seite "Zweierkomplement und Überlauf"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py

THEMA = {
    "titel": "Zweierkomplement, Carry und Overflow",
    "reihenfolge": 20,
    "kurz": "So speichert die Hardware negative Zahlen – und so erkennt sie, wenn ein Ergebnis nicht mehr hineinpasst.",
    "stichworte": ["Zweierkomplement", "Einerkomplement", "signed", "unsigned", "negative Zahlen", "Vorzeichen",
                   "Overflow", "Überlauf", "Carry", "Übertrag", "Flags", "int8", "Wertebereich", "Sign Extension"],

    "grafiken": ["werkzeug_zweierkomplement"],

    "erklaerung": """
## Stell dir vor …
Dreh einen vierstelligen **Kilometerzähler** von 0000 einen Schritt zurück: Er zeigt 9999. Man könnte sagen, 9999 „bedeutet“ hier −1. Genau so funktioniert das Zweierkomplement mit Bits: Ein Schritt unter 0000 0000 ergibt 1111 1111 – und das wird als −1 gelesen. Der Vorteil: Plus und Minus rechnet dasselbe Addierwerk.
## Grundlagen
Im **Zweierkomplement** hat das MSB die negative Wertigkeit `−2^(n−1)`, alle anderen Bits zählen normal positiv.
- Wertebereich mit n Bit: `−2^(n−1) … 2^(n−1) − 1` (8 Bit: −128 … +127), unsigned `0 … 2^n − 1` (0 … 255).
- MSB = 1 → negativ. Es gibt nur EINE Null (anders als beim Einerkomplement).
- Vorteil: Das Addierwerk rechnet für signed und unsigned genau gleich – Subtraktion ist Addition des Zweierkomplements.

Ob ein Muster signed oder unsigned ist, steht nicht im Muster. `1111 1011` ist unsigned 251, signed −5.

**Flags** nach einer Addition (Statusregister im µC):
- **C (Carry)**: Übertrag aus dem MSB → bei **unsigned** stimmt das Ergebnis nicht.
- **V (Overflow)**: zwei Zahlen mit gleichem Vorzeichen ergeben ein anderes Vorzeichen → bei **signed** stimmt das Ergebnis nicht.

## Vorgehen
- **−x bilden**: x binär → alle Bits invertieren (Einerkomplement) → +1. Gleichbedeutend: `2^n − x`.
- **Muster → signed lesen**: MSB = 0 → normal lesen; MSB = 1 → `Wert = Muster − 2^n` (oder: invertieren, +1, Minus davor).
- **Erweitern auf mehr Bit** (Sign Extension): das MSB nach links wiederholen: `1011` (−5, 4 Bit) → `1111 1011` (−5, 8 Bit).
- **Overflow prüfen**: nur möglich, wenn beide Summanden dasselbe Vorzeichen haben.

## Beispiel
8 Bit, −5:
- 5 = `0000 0101` → invertiert `1111 1010` → +1 = `1111 1011` = 0xFB
- Kontrolle: 256 − 5 = 251 = 0xFB

100 + 50 mit 8 Bit:
- `0110 0100 + 0011 0010 = 1001 0110`
- unsigned: 150 → richtig (C = 0)
- signed: −106 statt +150 → **Overflow** (V = 1), denn +150 passt nicht in −128 … 127

## Praxis
- C-Datentypen: `int8_t` (−128 … 127), `uint8_t` (0 … 255), `int16_t`, `uint32_t` … Ein Überlauf bei unsigned rechnet modulo 2^n weiter (z.B. Zähler 255 + 1 = 0).
- ADC-Werte von Sensoren (z.B. Temperatur 0xFFF0 bei 16 Bit) erst als signed deuten, dann skalieren.
- In Assembler/Statusregistern: Bedingte Sprünge prüfen C für unsigned- und V für signed-Vergleiche.
## 🔬 Genauer hingeschaut
- **Ein Addierwerk für alles:** Die Hardware weiss nicht, ob eine Zahl signed oder unsigned ist – sie addiert einfach Bits. Erst das Programm entscheidet, wie das Ergebnis zu lesen ist und ob es das Carry- oder das Overflow-Flag prüft.
- **Unsymmetrischer Bereich:** Mit 8 Bit gehen −128 … +127. −128 hat kein positives Gegenstück: Bildet man davon −x, kommt wieder −128 heraus.
- **Je nach Sprache verschieden:** In Python werden ganze Zahlen einfach grösser – es gibt keinen Überlauf. In C ist der Überlauf bei vorzeichenbehafteten Zahlen nicht definiert, bei vorzeichenlosen läuft er im Kreis.
## 💡 Wusstest du?
- 1996 zerstörte sich die erste **Ariane 5** kurz nach dem Start: Ein Wert wurde von einer 64-Bit-Gleitkommazahl in eine 16-Bit-Ganzzahl umgewandelt, war dafür zu gross, und der Fehler legte die Steuerung lahm.
""",

    "tipps": [
        "Schnelltrick für −x: von rechts bis zur ersten 1 alles abschreiben, danach alle Bits invertieren.",
        "−1 ist immer „alles Einsen“ (0xFF, 0xFFFF …), die kleinste Zahl ist 1000…0 (−128 bei 8 Bit).",
    ],
    "fehler": [
        "Nur invertiert, +1 vergessen – das ist das Einerkomplement (um 1 daneben).",
        "Carry als Fehler bei signed gedeutet – bei signed zählt nur das Overflow-Flag.",
        "Beim Erweitern auf 16 Bit mit Nullen aufgefüllt – aus −5 wird 251.",
    ],
    "siehe_auch": ["zahlensysteme_codes", "bitmasken"],
    "rechner": ["zweierkomplement", "binaer_addieren"],
}
