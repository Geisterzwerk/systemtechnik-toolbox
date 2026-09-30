# Thema: Multimeter  (Messtechnik / Messgeräte)
THEMA = {
    "titel": "Multimeter",
    "reihenfolge": 1,
    "kurz": "Spannung, Strom und Widerstand richtig messen – mit den Fallen, die jeden schon einmal erwischt haben.",
    "stichworte": ["multimeter", "dmm", "digitalmultimeter", "spannung messen", "strom messen", "widerstand messen",
                   "innenwiderstand", "belastungsfehler", "bürdenspannung", "shunt", "vorwiderstand",
                   "messbereichserweiterung", "sicherung", "kat", "cat", "messkategorie", "true rms",
                   "durchgangsprüfer", "diodentest", "4-leiter", "kelvin", "rel", "null"],

    "steckbrief": {
        "zeilen": [
            ("Spannung", "**parallel** zum Messobjekt · Innenwiderstand sehr gross (typ. 10 MΩ)"),
            ("Strom", "**in Reihe** (Stromkreis auftrennen!) · Innenwiderstand klein (Shunt)"),
            ("Widerstand", "nur **spannungsfrei** · Gerät speist einen kleinen Messstrom ein"),
            ("Genauigkeit", "`±(p % vom Messwert + n Digits)` – siehe Datenblatt"),
            ("Sicherheit", "Messkategorie **CAT II/III/IV** und Spannung müssen zur Messstelle passen"),
        ],
    },

    "erklaerung": """
## Spannung messen
Das Multimeter wird **parallel** angeschlossen. Damit es die Schaltung möglichst wenig beeinflusst, hat es einen hohen **Innenwiderstand** (typisch 10 MΩ). Trotzdem bildet es mit dem Innenwiderstand der Quelle einen **Spannungsteiler**: An sehr hochohmigen Punkten (z.B. Spannungsteiler mit MΩ-Widerständen, Sensorausgänge) zeigt es zu wenig an → **Belastungsfehler** (Rechner).
## Strom messen
Das Multimeter muss **in den Stromkreis** (Reihe). Intern fliesst der Strom über einen kleinen **Shunt**, die Spannung daran wird gemessen. Diese **Bürdenspannung** (oft einige 100 mV im Vollausschlag) fehlt der Schaltung – bei kleinen Versorgungsspannungen kann das die Messung verfälschen.
## Widerstand messen
Das Gerät schickt einen bekannten Strom durch das Bauteil und misst die Spannung. Deshalb gilt: **Schaltung spannungsfrei**, Kondensatoren entladen, und idealerweise ein Bein auslöten – parallele Pfade verfälschen sonst das Ergebnis.
## Messbereich erweitern (klassisch)
Ein Zeigermesswerk mit Innenwiderstand Ri und Vollausschlagstrom Iv:
- **Spannungsbereich** vergrössern → **Vorwiderstand** in Reihe: `Rv = U / Iv − Ri`
- **Strombereich** vergrössern → **Shunt** parallel: `Rs = Ri · Iv / (I − Iv)`
Genau so ist auch ein Digitalmultimeter intern aufgebaut (Spannungsteiler und Shunts vor dem AD-Wandler).
## Messkategorien (Sicherheit)
- **CAT II:** Geräte an der Steckdose
- **CAT III:** Gebäudeinstallation, Verteiler, fest installierte Maschinen
- **CAT IV:** Hausanschluss, Freileitung, Zähler
Messgerät **und** Messleitungen müssen mindestens die Kategorie und Spannung der Messstelle haben – sonst kann eine Überspannungsspitze zum Lichtbogen im Gerät führen.
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 2.1 (Messung von Gleichstrom/-spannung, Wechselgrössen, Leistung), Kapitel 3.1–3.2 (Widerstandsmessung), Kapitel 6.5.1 (Digital-Multimeter).
""",

    "tabellen": [
        {
            "titel": "📊 Messaufgabe → Anschluss",
            "kopf": ["Messgrösse", "Schaltung", "Buchsen", "Achtung"],
            "zeilen": [
                ["Spannung", "parallel", "COM + V", "Messkategorie beachten"],
                ["Strom (mA)", "in Reihe", "COM + mA", "kleine Sicherung, Bürdenspannung"],
                ["Strom (A)", "in Reihe", "COM + A (10 A)", "oft nur kurzzeitig erlaubt (Datenblatt)"],
                ["Widerstand / Diode / Durchgang", "spannungsfrei", "COM + Ω", "Kondensatoren entladen"],
                ["Grosse Ströme ohne Auftrennen", "Stromzange", "–", "nur ein Leiter in der Zange"],
            ],
        },
    ],

    "tipps": [
        "**Nach der Strommessung die Messleitung zurückstecken!** Wer danach im A-Eingang eine Spannung misst, erzeugt einen Kurzschluss über den Shunt.",
        "**Sicherung im Strompfad prüfen:** Zeigt der Strombereich immer 0, ist oft die interne Sicherung durchgebrannt.",
        "**REL/Null-Taste** zieht den Widerstand der Messleitungen ab (ca. 0.1–0.3 Ω) – wichtig bei kleinen Widerständen.",
        "**Sehr kleine Widerstände (mΩ)** mit 4-Leiter-Messung (Kelvin) oder mit Konstantstrom + Spannungsmessung bestimmen.",
        "**„Geisterspannungen“:** Offene Leitungen zeigen durch kapazitive Kopplung oft einige Volt an. Ein Gerät mit niedrigerem Innenwiderstand (LoZ-Funktion) entlarvt sie.",
        "**Vor der Messung prüfen:** Multimeter kurz an einer bekannten Spannung testen (z.B. Steckdose, Referenz) – bevor man „spannungsfrei“ feststellt.",
        "**Strommessung ohne Auftrennen:** Stromzange (bei DC nur mit Hall-Sensor-Zange) oder Spannung über einem bekannten Shunt messen.",
    ],
    "fehler": [
        "Strom parallel gemessen → Kurzschluss, Sicherung oder Gerät defekt.",
        "Widerstand in einer Schaltung unter Spannung gemessen.",
        "Messgerät CAT II im Verteiler (CAT III) eingesetzt.",
        "Hochohmige Spannungsquelle gemessen und den Belastungsfehler nicht bemerkt.",
    ],
    "siehe_auch": ["messunsicherheit", "signalkenngroessen", "oszilloskop"],

    "rechner": ["belastung_u", "buerde_i", "dmm_genauigkeit", "messbereich", "signalform"],
}
