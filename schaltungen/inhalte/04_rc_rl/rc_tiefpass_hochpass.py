# Seite "RC-Tiefpass und -Hochpass"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "RC-Tiefpass und RC-Hochpass",
    "reihenfolge": 10,
    "kurz": "Frequenzabhängiger Spannungsteiler: lässt tiefe bzw. hohe Frequenzen durch, mit fg = 1 / (2π · R · C).",
    "stichworte": ["Tiefpass", "Hochpass", "RC-Filter", "Grenzfrequenz", "fg", "-3 dB", "Bode", "Frequenzgang",
                   "Phasenverschiebung", "Koppelkondensator", "Integrierglied", "Differenzierglied", "Dekade"],

    "grafiken": ["schaltung_rc_filter"],

    "erklaerung": """
## Funktion
R und C bilden einen Spannungsteiler, dessen einer Teil – der Blindwiderstand `Xc = 1 / (2π · f · C)` – von der Frequenz abhängt.
- **Tiefpass** (Ausgang am C): `|H| = 1 / √(1 + (f / fg)²)`, Phase `φ = −arctan(f / fg)`
- **Hochpass** (Ausgang am R): `|H| = (f / fg) / √(1 + (f / fg)²)`, Phase `φ = 90° − arctan(f / fg)`
- Grenzfrequenz `fg = 1 / (2π · R · C)`: dort ist Xc = R, |H| = 0.707 (−3 dB), φ = ∓45°
- Weit hinter fg fällt der Betrag mit **20 dB pro Dekade** (Faktor 10 in der Frequenz → Faktor 10 in der Spannung).

Im Zeitbereich ist der Tiefpass ein **Integrierglied** (glättet, Rechteck → abgerundete Flanken), der Hochpass ein **Differenzierglied** (lässt nur Änderungen durch, Rechteck → Nadelimpulse).

## Dimensionierung
1. Grenzfrequenz festlegen: Tiefpass deutlich über dem Nutzsignal, aber unter der Störung; Hochpass (Koppelkondensator) deutlich unter der tiefsten Nutzfrequenz.
2. R wählen: gross gegen den Innenwiderstand der Quelle, klein gegen die Last (Faustregel: R_Last ≥ 10 · R).
3. `C = 1 / (2π · R · fg)` und auf die Normreihe (E6/E12) runden – fg neu ausrechnen.
4. Dämpfung bei einer Störfrequenz prüfen: `dB = 20 · log10(|H|)`; braucht man mehr als ≈ 20 … 30 dB, reicht 1. Ordnung meist nicht (2 RC-Glieder oder aktives Filter).
5. Bei Koppelkondensatoren: Spannungsfestigkeit ≥ Gleichspannung, bei Elkos die Polung beachten.

## Betriebszustände
- **f ≪ fg**: Tiefpass lässt alles durch (Ua ≈ Ue, φ ≈ 0°), Hochpass sperrt (Gleichspannung = 0 V am Ausgang).
- **f = fg**: beide 70.7 %, Phasenverschiebung 45° (Tiefpass nacheilend, Hochpass voreilend).
- **f ≫ fg**: Tiefpass sperrt (|H| ≈ fg / f, φ → −90°), Hochpass lässt alles durch.
- **Sprung am Eingang**: Ausgang ändert sich mit τ = R · C (Tiefpass steigt an, Hochpass springt mit und klingt ab).

## Messpunkte
- **M1** (Ausgang) und Eingang gleichzeitig mit dem Oszilloskop: Amplitudenverhältnis = |H|, zeitlicher Versatz Δt → `φ = 360° · Δt · f`.
- fg messen: Frequenz am Generator verändern, bis û_a = 0.707 · û_e (oder Phase 45°).
- Rechteck am Eingang: Anstiegszeit 10 … 90 % ≈ 2.2 · τ → `fg ≈ 0.35 / t_r`.
- Tastkopf (10 MΩ ∥ ≈ 15 pF) belastet hochohmige Filter – bei R > 100 kΩ beachten.

## Grenzfälle
- C → 0 bzw. R → 0: fg → ∞ – der Tiefpass filtert nichts mehr, der Hochpass lässt alles durch.
- Last am Ausgang: liegt parallel zum C bzw. R → fg verschiebt sich, Verstärkung < 1 schon bei Gleichspannung (Tiefpass).
- Quelle mit Innenwiderstand: R_i addiert sich zu R → fg kleiner.
- Zwei RC-Glieder hintereinander ohne Puffer: belasten sich gegenseitig, die Gesamt-fg ist nicht einfach „2 × 1. Ordnung“ (Puffer mit OPV dazwischen).
""",

    "tipps": [
        "Merkhilfe: Tiefpass = C nach unten (GND), Hochpass = C in der Längsleitung.",
        "Zum Abschätzen: Pro Dekade über fg 20 dB, pro Oktave (Faktor 2) 6 dB Dämpfung.",
        "Ein ADC-Eingang mit RC-Tiefpass braucht ein kleines R, sonst lädt der Sample-Kondensator des ADC das C um (Messfehler).",
    ],
    "fehler": [
        "fg mit der Zeitkonstante verwechselt: fg = 1 / (2π · τ), nicht 1 / τ.",
        "Tiefpass am Ausgang mit einer niederohmigen Last betrieben – die Spannung bricht schon bei Gleichspannung ein.",
        "Erwartet, dass bei fg nichts mehr durchkommt – dort sind es noch 70.7 %.",
    ],
    "siehe_auch": ["rc_laden_entladen", "anti_aliasing_filter", "spannungsteiler", "lc_tiefpass",
                   "aktive_filter_sallen_key"],
    "rechner": ["rc_frequenzgang", "rc_filter", "blindwiderstand_c"],
}
