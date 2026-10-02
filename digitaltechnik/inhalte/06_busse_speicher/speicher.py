# Seite "Speicher"  -> Vorlage: digitaltechnik/inhalte/_vorlage.py
# Adressdecoder: Rechner "adressdecoder" aus Schritt 8c wird wiederverwendet.

THEMA = {
    "titel": "Halbleiterspeicher: RAM, ROM, EEPROM, Flash",
    "reihenfolge": 40,
    "kurz": "Speicherarten, Organisation 2^a × d, Steuersignale CS/OE/WE und wie man aus kleinen Chips grosse Speicher baut.",
    "stichworte": ["Speicher", "RAM", "SRAM", "DRAM", "ROM", "PROM", "EPROM", "EEPROM", "Flash", "NOR-Flash",
                   "NAND-Flash", "FRAM", "flüchtig", "nichtflüchtig", "Speicherorganisation", "Adressbus", "Datenbus",
                   "Chip Select", "Output Enable", "Write Enable", "Speichererweiterung", "Zugriffszeit", "62256"],

    "grafiken": ["werkzeug_speicher"],

    "erklaerung": """
## Grundlagen
**Flüchtig** (Inhalt weg ohne Spannung):
- **SRAM**: je Bit ein Flipflop (6 Transistoren), schnell, kein Auffrischen, teuer pro Bit → Register, Cache, µC-Arbeitsspeicher
- **DRAM**: je Bit ein Kondensator + Transistor, sehr dicht und billig, muss alle ~64 ms **aufgefrischt** werden (Refresh) → PC-Arbeitsspeicher

**Nichtflüchtig:**
- **ROM / PROM**: Inhalt bei der Herstellung bzw. einmal programmiert
- **EPROM**: mit UV-Licht löschbar (Fenster im Gehäuse, heute selten)
- **EEPROM**: elektrisch byteweise löschbar, ca. 10⁵ … 10⁶ Schreibzyklen → Einstellungen, Kalibrierwerte
- **Flash**: blockweise (Sektor/Page) löschbar, ca. 10⁴ … 10⁵ Zyklen, sehr dicht → Programmspeicher, USB-Sticks, SSD; NOR-Flash für Programmcode, NAND-Flash für grosse Datenmengen
- **FRAM**: schnell und praktisch unbegrenzt beschreibbar, aber kleiner und teurer

**Organisation** `2^a × d`: **a** Adressleitungen wählen eines von 2^a Wörtern, **d** Datenleitungen tragen die Bits.
- Kapazität = `2^a · d` Bit
- Beispiel: SRAM 62256 = 32 K × 8 → 15 Adressleitungen (A14 … A0), 8 Datenleitungen, 256 Kibit = 32 KiB

**Steuersignale** (aktiv LOW):
- **¬CS/¬CE**: Baustein aktiv
- **¬OE**: beim Lesen Ausgänge an den Bus
- **¬WE**: Schreiben

Ist ¬CS = 1, sind die Datenleitungen **hochohmig** – darum können viele Bausteine am selben Datenbus hängen.

## Vorgehen
Speicher mit Chips **erweitern**:
1. **Wortbreite** (mehr Bits je Adresse): Chips **nebeneinander**. Alle bekommen dieselben Adress- und Steuerleitungen, jeder Chip einen Teil des Datenbusses (z.B. D7 … D0 und D15 … D8).
2. **Tiefe** (mehr Adressen): Chips **untereinander** am gemeinsamen Datenbus. Die unteren Adressbits gehen an alle Chips, die oberen an einen **Adressdecoder**, der genau ein ¬CS aktiviert.
3. Anzahl Chips = `⌈Breite_Ziel / Breite_Chip⌉ · Wörter_Ziel / Wörter_Chip`
4. Adressbereich jedes Chips bestimmen (Rechner „Adressdecodierung“) und Zugriffszeiten prüfen: Decoder-Laufzeit + Zugriffszeit des Speichers < Zeit, die der Prozessor wartet.

## Beispiel
Gesucht: 64 K × 16, vorhanden: 32 K × 8 (62256).
- Wortbreite: 16 / 8 = 2 Chips nebeneinander
- Tiefe: 64 K / 32 K = 2 Reihen → **4 Chips**
- 16 Adressbits: A14 … A0 an alle Chips; A15 wählt die Reihe (Inverter oder 1-aus-2-Decoder)
- Reihe 0: 0x0000 … 0x7FFF, Reihe 1: 0x8000 … 0xFFFF

Kapazität eines 2-Mbit-EEPROMs mit 8 Datenbits: 2 Mibit / 8 = 256 Ki Wörter → `log2(262144) = 18` Adressleitungen.

## Praxis
- Datenblätter geben die Grösse oft in **Bit** an (z.B. „256K“ = 256 Kibit = 32 KiB) – genau lesen.
- K, M, G heissen bei Speichern traditionell 1024, 1024², 1024³ (genau: Ki, Mi, Gi).
- Flash/EEPROM sind nicht unbegrenzt beschreibbar: Werte nicht in jeder Schleife speichern, sondern nur bei Änderung (Wear Leveling bei Flash).
- Viele moderne Speicher (EEPROM 24LCxx, SPI-Flash 25Qxx) hängen seriell an I²C oder SPI statt an einem parallelen Bus – das spart Pins, ist aber langsamer.
""",

    "tipps": [
        "Adressleitungen = log2(Anzahl Wörter): 1 K → 10, 64 K → 16, 1 M → 20.",
        "Wortbreite erweitern: Chips teilen alles ausser dem Datenbus. Tiefe erweitern: Chips teilen alles ausser ¬CS.",
    ],
    "fehler": [
        "Kapazität in Bit mit Kapazität in Byte verwechselt (Faktor 8).",
        "Bei der Tiefenerweiterung zwei Chips gleichzeitig aktiv (Decoder falsch) – Buskonflikt auf dem Datenbus.",
        "Flash-Zelle ohne vorheriges Löschen beschrieben – Flash kann nur Bits von 1 auf 0 setzen, Löschen nur ganze Blöcke.",
        "EEPROM in einer schnellen Schleife beschrieben – nach wenigen Stunden ist die Lebensdauer erreicht.",
    ],
    "siehe_auch": ["decoder_encoder", "ausgangstypen", "flipflops", "spi", "i2c"],
    "rechner": ["speicher_organisation", "speicher_erweitern", "adressdecoder"],
}
