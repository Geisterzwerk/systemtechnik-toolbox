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
## Stell dir vor …
Ein **Voltmeter** ist wie ein Zuschauer am Strassenrand: Er steht daneben (parallel) und soll den Verkehr nicht stören – deshalb ist er sehr hochohmig. Ein **Ampèremeter** ist wie eine Zählstelle mitten auf der Strasse: Alle müssen hindurch (Reihe), also darf sie möglichst nicht bremsen – deshalb ist es sehr niederohmig. Wer das Ampèremeter wie einen Zuschauer an die Spannung hält, baut einen **Kurzschluss**.
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
## Beispiele durchgerechnet
**Belastungsfehler:** Ein Spannungsteiler aus 2 × 1 MΩ an 10 V sollte 5 V liefern. Von aussen gesehen hat er einen Innenwiderstand von 500 kΩ (beide Widerstände parallel). Mit einem 10-MΩ-Multimeter misst man `5 V · 10 MΩ / (10 MΩ + 0.5 MΩ) ≈ 4.76 V` – also **4.8 % zu wenig**, obwohl das Gerät selbst genau ist.
**Messbereich erweitern:** Ein Messwerk mit Ri = 1 kΩ und Iv = 100 µA soll 10 V anzeigen: `Rv = 10 V / 100 µA − 1 kΩ = 99 kΩ`. Für 1 A braucht es einen Shunt: `Rs = 1 kΩ · 100 µA / (1 A − 100 µA) ≈ 0.1 Ω`.
## 🔬 Genauer hingeschaut
- **Phantomspannungen:** Eine offene, nicht angeschlossene Leitung neben einer Netzleitung kann kapazitiv eingekoppelte Spannung zeigen – mit 10 MΩ Eingangswiderstand oft Dutzende Volt. Viele Geräte haben dafür einen **LoZ-Modus** (niedriger Eingangswiderstand), der solche Scheinspannungen zusammenbrechen lässt.
- **Durchgang und Diodentest:** Im Diodentest liefert das Gerät einen kleinen Strom und zeigt die Durchlassspannung an (Si ≈ 0.5 … 0.7 V). Der Durchgangsprüfer piepst unter einer Schwelle von typisch einigen 10 Ω – er zeigt also nicht „0 Ω“, sondern „ziemlich niederohmig“.
- **Strombuchsen sind abgesichert:** Im Strommessbereich ist das Gerät fast ein Kurzschluss. Bleiben die Messleitungen in der A-Buchse stecken und misst man danach Spannung, löst die (hoffentlich hochwertige) Sicherung aus. Darum nach jeder Strommessung die Leitungen sofort zurückstecken.
- **Anzeige und Auflösung:** Ein Gerät mit „6000 Counts“ zeigt maximal 5999. Im 6-V-Bereich ist die kleinste Stelle 1 mV – über die Genauigkeit sagt das noch nichts (siehe Seite Messunsicherheit).
## 💡 Wusstest du?
- Die Messkategorie gilt für die **Spannungsspitzen**, die an einer Messstelle auftreten können: Nahe am Hausanschluss (CAT IV) sind Überspannungen durch Blitz und Schalthandlungen viel energiereicher als an einer Steckdose (CAT II). Darum ist ein CAT-II-Gerät im Verteiler fehl am Platz – auch wenn dort „nur“ 230 V anliegen.
- Bei Zangenmessgeräten muss nur **ein** Leiter durch die Zange: Um ein ganzes Kabel gelegt, heben sich Hin- und Rückstrom auf – die Anzeige ist dann fast null.
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
