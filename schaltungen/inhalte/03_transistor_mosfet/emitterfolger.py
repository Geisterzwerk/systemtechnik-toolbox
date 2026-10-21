# Seite "Emitterfolger"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Emitterfolger (Kollektorschaltung)",
    "reihenfolge": 50,
    "kurz": "Spannungsverstärkung ≈ 1, aber grosse Stromverstärkung – macht aus einer schwachen Quelle eine starke.",
    "stichworte": ["Emitterfolger", "Kollektorschaltung", "Impedanzwandler", "Puffer", "Stromverstärkung",
                   "Eingangswiderstand", "Ausgangswiderstand", "Längsregler"],

    "grafiken": ["schaltung_emitterfolger"],

    "erklaerung": """
## Stell dir vor …
Ein **starker Helfer**, der genau nachmacht, was du vormachst: Hebst du die Hand um 10 cm, hebt er einen schweren Balken um 10 cm. Er macht die Bewegung nicht grösser, aber er hat viel mehr Kraft. Der Emitterfolger verstärkt nicht die Spannung (Ausgang ≈ Eingang − 0.7 V), sondern den **Strom** – er macht aus einer schwachen Quelle eine starke.
## Funktion
Der Kollektor liegt an +U_B, der Ausgang wird am Emitter abgegriffen. Der Emitter „folgt“ der Basis mit dem Abstand U_BE:
- `Ua = Ue − 0.7 V`,  Spannungsverstärkung `Vu = R / (r_e + R) ≈ 1` (nicht invertierend)
- Stromverstärkung `I_E / I_B = β + 1`
- Eingangswiderstand `r_ein ≈ (β + 1) · (r_e + R)` (hoch),  Ausgangswiderstand `r_aus ≈ r_e + R_Quelle / (β + 1)` (klein)

Deshalb heisst er **Impedanzwandler**: Eine hochohmige Quelle (Spannungsteiler, Sensor) kann über ihn eine niederohmige Last treiben.

## Dimensionierung
1. Grösster Laststrom bestimmt den Transistor (I_C,max, P_tot): `P = (U_B − Ua) · I_E`.
2. Basisstrom `I_B = I_E / (β + 1)` muss die Quelle liefern können.
3. R_E: hält den Ruhestrom, auch wenn die Last klein ist; bei Wechselsignalen so wählen, dass der Transistor in der negativen Spitze nicht sperrt (`Ua,min / R_E ≥ Laststrom`).
4. Als einfacher **Längsregler**: Basis an Z-Diode → `Ua ≈ U_Z − 0.7 V`, der Transistor übernimmt den Laststrom.

## Betriebszustände
- **Normal**: Ausgang = Eingang − 0.7 V.
- **Unten abgeschnitten**: Ue < 0.7 V (oder Last will Strom HINEIN schieben) → Transistor sperrt, er kann nur Strom liefern, nicht aufnehmen.
- **Oben begrenzt**: Ua kann nicht über U_B − U_CE,sat steigen.

## Messpunkte
- **M1** (Emitter) und Basis gleichzeitig: Differenz ≈ 0.6 … 0.7 V, unabhängig von der Last.
- Last verändern: Ua bleibt fast gleich, während der Basisstrom kaum steigt (Vergleich mit einem Spannungsteiler ohne Puffer).
- Mit Oszilloskop bei Wechselsignal: unten abgeflacht → R_E kleiner oder Arbeitspunkt höher.

## Grenzfälle
- Kapazitive Last + schnelle Signale: Der Emitterfolger kann schwingen → kleiner Widerstand (z.B. 47 … 100 Ω) in die Basisleitung.
- Ausgang kurzgeschlossen: Strom nur durch β · I_B begrenzt – Transistor überhitzt.
- Push-Pull: Zwei Emitterfolger (NPN + PNP) liefern und nehmen Strom auf – Grundlage der Gegentakt-Endstufe.
## 🔬 Genauer hingeschaut
- **Impedanzwandler:** Der Eingangswiderstand ist ungefähr `β · R_E` (R_E parallel zur Last), also sehr gross. Der Ausgangswiderstand ist ungefähr der Quellwiderstand geteilt durch β – also sehr klein. Genau das will man, um eine schwache Quelle mit einer schweren Last zu verbinden.
- **Nur eine Richtung:** Ein NPN-Emitterfolger kann Strom nur **liefern**. Muss die Last auch Strom zurückgeben (Lautsprecher, kapazitive Last), braucht es einen zweiten, komplementären Transistor – die **Gegentakt-Endstufe**.
- **Thermisch:** Am Transistor liegt `U_B − Ua` bei vollem Laststrom. Bei grossen Spannungsunterschieden wird er heiss – Kühlkörper einplanen.
## 💡 Wusstest du?
- In klassischen Linearreglern wie dem 7805 sitzt am Ausgang ein Längstransistor, der genau als Emitterfolger arbeitet – angesteuert von einem Regelverstärker.
""",

    "tipps": [
        "Darlington (zwei Emitterfolger hintereinander) ergibt β ≈ β1 · β2, aber U_BE ≈ 1.4 V.",
        "Ein OPV-Spannungsfolger erledigt dasselbe ohne die 0.7-V-Verschiebung – der Emitterfolger ist aber einfacher und robuster bei grossen Strömen.",
    ],
    "fehler": [
        "Die 0.7 V Verschiebung vergessen: Ua ist kleiner als Ue.",
        "Erwartet, dass der Emitterfolger auch Strom aufnehmen kann – er treibt nur in eine Richtung.",
        "Verlustleistung (U_B − Ua) · I übersehen – bei grossen Strömen braucht er einen Kühlkörper.",
    ],
    "siehe_auch": ["emitterschaltung", "z_stabilisierung"],
    "rechner": ["emitterfolger", "kuehlkoerper"],
}
