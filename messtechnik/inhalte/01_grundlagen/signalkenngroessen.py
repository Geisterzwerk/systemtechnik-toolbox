# Thema: Effektivwert, Mittelwert & Co.  (Messtechnik / Grundlagen)
THEMA = {
    "titel": "Effektivwert, Mittelwert & Co.",
    "reihenfolge": 6,
    "kurz": "Was ein Multimeter bei Wechselgrössen eigentlich anzeigt – und warum „True RMS“ wichtig ist.",
    "stichworte": ["effektivwert", "rms", "true rms", "trms", "mittelwert", "gleichrichtwert", "scheitelwert",
                   "spitzenwert", "spitze-spitze", "crestfaktor", "scheitelfaktor", "formfaktor", "sinus",
                   "rechteck", "dreieck", "pwm", "tastgrad", "mischspannung", "ac+dc", "wechselspannung"],

    "steckbrief": {
        "zeilen": [
            ("Scheitelwert Û", "grösster Momentanwert (Amplitude)"),
            ("Spitze-Spitze Uss", "von Minimum bis Maximum, bei Sinus `Uss = 2 · Û`"),
            ("Effektivwert U_eff (RMS)", "gleiche Wärmewirkung wie Gleichspannung dieser Höhe. Sinus: `Û / √2 ≈ 0.707 · Û`"),
            ("Arithm. Mittelwert Ū", "Gleichanteil (bei reinem Wechselsignal 0) – das zeigt der DC-Bereich"),
            ("Gleichrichtwert |Ū|", "Mittelwert des Betrags. Sinus: `2Û/π ≈ 0.637 · Û`"),
            ("Crestfaktor", "`Û / U_eff` (Sinus 1.414) – wichtig für die Messgeräte-Angabe"),
            ("Formfaktor", "`U_eff / |Ū|` (Sinus 1.111)"),
        ],
    },

    "erklaerung": """
## Stell dir vor …
Du willst eine Herdplatte beschreiben, die mit Wechselspannung heizt. Interessant ist nicht, wie hoch die Spannung kurz ausschlägt, sondern **wie warm die Platte wird**. Der **Effektivwert** ist genau die Gleichspannung, die dieselbe Platte gleich warm machen würde. Der **Scheitelwert** dagegen ist für die Isolation wichtig – denn die muss auch die kurze Spitze aushalten.
## Warum gibt es so viele „Werte“?
Eine Wechselspannung ändert sich ständig. Welche Zahl man angibt, hängt davon ab, was man wissen will:
- **Scheitelwert Û:** Wie hoch wird die Spannung maximal? (Isolation, Spannungsfestigkeit)
- **Effektivwert U_eff:** Wie viel Leistung/Wärme erzeugt sie? Die 230 V im Netz sind ein Effektivwert – der Scheitelwert beträgt ca. 325 V.
- **Arithmetischer Mittelwert:** Wie gross ist der Gleichanteil? (DC-Bereich des Multimeters, Motorspannung bei PWM)
## Wie misst ein Multimeter Wechselspannung?
- **Einfache Geräte (Mittelwert-Messung):** Sie bilden den Gleichrichtwert und multiplizieren mit **1.111** (dem Formfaktor von Sinus). Das stimmt **nur bei reinem Sinus**. Bei Rechteck, PWM, Dreieck oder verzerrten Strömen (Schaltnetzteile, Frequenzumrichter, LED-Treiber) liegen sie teils deutlich daneben.
- **True-RMS-Geräte** berechnen den echten Effektivwert – für jede Signalform, solange der **Crestfaktor** und die **Bandbreite** im erlaubten Bereich liegen (Datenblatt).
- **AC oder AC+DC:** Viele Geräte messen im AC-Bereich nur den Wechselanteil. Für eine Mischspannung (z.B. PWM 0 … 12 V) braucht es **AC+DC**, oder man rechnet `U_eff = √(U_DC² + U_AC²)`.
## PWM
Bei einem Rechteck von 0 … Û mit Tastgrad D gilt: Mittelwert = D · Û, Effektivwert = √D · Û. Ein Motor „spürt“ eher den Mittelwert, ein Heizwiderstand den Effektivwert.
## Beispiele durchgerechnet
**Netzspannung 230 V (Sinus):**
- Scheitelwert `Û = √2 · 230 V ≈ 325 V`, Spitze-Spitze ≈ **650 V**
- Arithmetischer Mittelwert: **0 V** (positive und negative Halbwelle heben sich auf)
- Gleichrichtwert `2/π · Û ≈ 207 V` → Formfaktor `230 / 207 ≈ 1.11`
**PWM an einem Heizwiderstand:** 12 V, Tastgrad 25 %, R = 12 Ω.
- Mittelwert `0.25 · 12 V = 3 V`, Effektivwert `√0.25 · 12 V = 6 V`
- Leistung `P = U_eff² / R = 36 / 12 = 3 W` – genau ein Viertel der 12 W bei Dauer-Ein. Wer mit dem Mittelwert rechnet (3 V → 0.75 W), liegt um den Faktor 4 daneben.
**Falsche Anzeige ohne True-RMS:** Ein Rechteck mit ±5 V hat den Effektivwert 5 V. Ein mittelwertbildendes Multimeter misst den Gleichrichtwert 5 V und multipliziert mit 1.111 → zeigt **5.55 V** (11 % zu viel).
## 🔬 Genauer hingeschaut
- **Formfaktor** `F = U_eff / Gleichrichtwert` und **Crestfaktor** `C = Û / U_eff` beschreiben die Signalform: Sinus F ≈ 1.11, C ≈ 1.41 · Rechteck (symmetrisch) F = 1, C = 1 · Dreieck F ≈ 1.15, C ≈ 1.73.
- **Warum Crestfaktor wichtig ist:** Ein True-RMS-Multimeter kann nur Signale bis zu einem bestimmten Crestfaktor richtig messen (Datenblatt, oft 3). Ströme von Schaltnetzteilen und Gleichrichtern mit Glättungs-Elko fliessen nur in kurzen Spitzen und haben einen deutlich höheren Crestfaktor als Sinus.
- **Effektivwert allgemein:** `U_eff = √( (1/T) · ∫ u(t)² dt )` – man quadriert, mittelt über eine Periode und zieht die Wurzel („root mean square“, RMS). Genau so rechnen digitale True-RMS-Geräte mit ihren Abtastwerten.
## 💡 Wusstest du?
- Früher lag die Netzspannung in Europa bei 220 V bzw. 240 V. Mit der Norm IEC 60038 wurde sie auf **230 V ±10 %** vereinheitlicht.
- Zwischen zwei Aussenleitern misst man **400 V** – das ist `230 V · √3`, weil die drei Phasen um je 120° verschoben sind.
## 📚 Vertiefung
Schrüfer, *Elektrische Messtechnik*: Kapitel 2.1.3 (Messung von Wechselstrom und Wechselspannung), Kapitel 1.8 (informationstragende Parameter von Messsignalen).
""",

    "tabellen": [
        {
            "titel": "📊 Kennwerte der wichtigsten Signalformen",
            "kopf": ["Signal", "U_eff", "Gleichrichtwert", "Crestfaktor", "Formfaktor"],
            "zeilen": [
                ["Sinus", "Û / √2 = 0.707 Û", "0.637 Û", "1.414", "1.111"],
                ["Rechteck ±Û", "Û", "Û", "1", "1"],
                ["Dreieck ±Û", "Û / √3 = 0.577 Û", "0.5 Û", "1.732", "1.155"],
                ["PWM 0…Û, Tastgrad D", "√D · Û", "D · Û", "1 / √D", "1 / √D"],
                ["Sinus einweg-gleichgerichtet", "0.5 Û", "0.318 Û", "2", "1.571"],
                ["Sinus vollweg-gleichgerichtet", "0.707 Û", "0.637 Û", "1.414", "1.111"],
            ],
        },
    ],

    "tipps": [
        "**Nur True RMS misst nicht-sinusförmige Signale richtig** – bei Schaltnetzteilen, Dimmern, Frequenzumrichtern und PWM Pflicht.",
        "**Bandbreite beachten:** Auch True-RMS-Multimeter messen oft nur bis einige kHz korrekt. Schnelle PWM (z.B. 20 kHz) → Oszilloskop verwenden.",
        "**Netzspannung:** 230 V ist der Effektivwert. Û ≈ 325 V, Uss ≈ 650 V – darauf müssen Kondensatoren und Dioden ausgelegt sein.",
        "**Oszilloskop-Messfunktionen** zeigen RMS, Mean, Vpp usw. direkt – auf das richtige Messfenster (ganze Perioden) achten.",
    ],
    "fehler": [
        "PWM oder Rechteck mit einem Mittelwert-Multimeter gemessen und dem Wert vertraut.",
        "Mischspannung im AC-Bereich gemessen – der Gleichanteil fehlt.",
        "Scheitelwert und Effektivwert verwechselt (Faktor 1.41 beim Sinus).",
    ],
    "siehe_auch": ["signalformen", "multimeter", "oszilloskop", "messunsicherheit"],

    "rechner": ["signalform"],
}
