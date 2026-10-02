# =============================================================================
# bauteile/rechner/trafo_rechner.py
# -----------------------------------------------------------------------------
# Alle RECHNER für die Seite "Transformator".
#
#   trafo_animation    INTERAKTIV: Animation mit Reglern (bauteile/grafiken/trafo_animation.py)
#   uebersetzung       U1, U2, N1, N2 - drei eingeben, vierter wird berechnet (+ Ströme)
#   leistung_trafo     Scheinleistung, Wirkungsgrad, Primärstrom, Sicherung
#   windungen          Windungen pro Volt aus Kernquerschnitt (Trafo selbst wickeln)
#   netzteil           Trafo + Brückengleichrichter + Elko: Gleichspannung und Welligkeit
# =============================================================================

import math

from bauteile.grafiken.trafo_animation import TrafoAnimation       # -> grafiken/trafo_animation.py
from bauteile.rechner import normreihen                            # -> rechner/normreihen.py
from bauteile.rechner.basis import FormelRechner, RechnerFehler, anzahl_gegeben, fmt   # -> rechner/basis.py


def _uebersetzung(w):
    U1, U2, N1, N2 = w["U1"], w["U2"], w["N1"], w["N2"]
    if anzahl_gegeben(w, "U1", "U2", "N1", "N2") != 3:
        raise RechnerFehler("Genau DREI von U1, U2, N1, N2 eingeben")
    zeilen = []
    if U1 is None:
        U1 = U2 * N1 / N2
        zeilen.append(f"U1 = {fmt(U1, 'spannung')}")
    elif U2 is None:
        U2 = U1 * N2 / N1
        zeilen.append(f"U2 = {fmt(U2, 'spannung')}")
    elif N1 is None:
        N1 = N2 * U1 / U2
        zeilen.append(f"N1 = {N1:.0f} Windungen")
    else:
        N2 = N1 * U2 / U1
        zeilen.append(f"N2 = {N2:.0f} Windungen")
    ue = U1 / U2
    zeilen.append(f"Übersetzung ü = U1/U2 = N1/N2 = {ue:.4g}  ({'Abwärts' if ue > 1 else 'Aufwärts'}-Trafo)")
    if w["I2"] is not None:
        zeilen.append(f"I2 = {fmt(w['I2'], 'strom')} → I1 = I2 / ü = {fmt(w['I2'] / ue, 'strom')}  (ideal)")
    zeilen.append(f"Impedanz-Übersetzung: Last auf Primärseite erscheint ü² = {ue * ue:.4g}× grösser")
    return zeilen


def uebersetzung(master):
    return FormelRechner(
        master, "Übersetzung", "Drei Werte eingeben, der vierte wird berechnet (idealer Trafo)",
        felder=[("U1", "Primär U1", "spannung", {"platzhalter": "z.B. 230"}), ("U2", "Sekundär U2", "spannung"),
                ("N1", "Windungen N1", "zahl"), ("N2", "Windungen N2", "zahl"),
                ("I2", "Sekundärstrom (opt.)", "strom", {"platzhalter": "optional"})],
        berechnen=_uebersetzung, formel="U1 / U2 = N1 / N2 = I2 / I1 = ü")


def _leistung(w):
    U1, U2, I2, eta = w["U1"], w["U2"], w["I2"], w["eta"]
    if None in (U1, U2, I2):
        raise RechnerFehler("U1, U2 und I2 eingeben")
    eta = 0.85 if eta is None else eta
    if not 0 < eta <= 1:
        raise RechnerFehler("Wirkungsgrad zwischen 1 und 100 %")
    S2 = U2 * I2
    S1 = S2 / eta
    I1 = S1 / U1
    zeilen = [f"Leistung sekundär: S2 = U2 · I2 = {fmt(S2, 'leistung').replace('W', 'VA')}",
              f"Aufnahme primär:   S1 = S2 / η = {fmt(S1, 'leistung').replace('W', 'VA')}  (η = {eta * 100:.0f} %)",
              f"Verluste (Wärme):  {fmt(S1 - S2, 'leistung')}",
              f"Primärstrom I1 = {fmt(I1, 'strom')}  (Nennbetrieb)",
              f"Trafo wählen: mind. {fmt(S2 * 1.2, 'leistung').replace('W', 'VA')} (20 % Reserve)",
              "Primärsicherung: träge (T), ca. 1.5–2 × I1 – wegen des Einschaltstroms"]
    return zeilen


def leistung_trafo(master):
    return FormelRechner(
        master, "Leistung & Wirkungsgrad", "Kleine Trafos: η ≈ 70–85 %, grosse: > 95 %",
        felder=[("U1", "Primär U1", "spannung", {"platzhalter": "230"}), ("U2", "Sekundär U2", "spannung"),
                ("I2", "Sekundärstrom I2", "strom"), ("eta", "Wirkungsgrad η", "prozent", {"platzhalter": "85"})],
        berechnen=_leistung, formel="S = U · I     η = P_ab / P_zu")


def _windungen(w):
    f, B, A = w["f"] or 50.0, w["B"], w["A"]
    if B is None or A is None:
        raise RechnerFehler("Flussdichte B und Kernquerschnitt A eingeben")
    n_pro_volt = 1 / (4.44 * f * B * A)
    zeilen = [f"{n_pro_volt:.3g} Windungen pro Volt"]
    if w["U1"] is not None:
        zeilen.append(f"N1 = {w['U1'] * n_pro_volt:.0f} Windungen für {fmt(w['U1'], 'spannung')}")
    if w["U2"] is not None:
        zeilen.append(f"N2 = {w['U2'] * n_pro_volt * 1.05:.0f} Windungen für {fmt(w['U2'], 'spannung')} "
                      f"(+5 % für Lastverluste)")
    zeilen.append("Faustwert Netztrafo-Blech: B ≈ 1.0–1.3 T. Zu wenig Windungen → Kern sättigt → Trafo wird heiss")
    return zeilen


def windungen(master):
    return FormelRechner(
        master, "Windungen pro Volt", "Für Eigenbau/Umwickeln: A = Querschnitt des Mittelschenkels",
        felder=[("A", "Kernquerschnitt A", "flaeche", {"einheit": "cm²"}),
                ("B", "Flussdichte B", "flussdichte", {"platzhalter": "z.B. 1.2"}),
                ("f", "Frequenz f", "frequenz", {"platzhalter": "50"}),
                ("U1", "Primär U1 (opt.)", "spannung", {"platzhalter": "optional"}),
                ("U2", "Sekundär U2 (opt.)", "spannung", {"platzhalter": "optional"})],
        berechnen=_windungen, formel="N / U = 1 / (4.44 · f · B · A)")


def _netzteil(w):
    U2, I, C, f = w["U2"], w["I"], w["C"], w["f"] or 50.0
    if U2 is None or I is None:
        raise RechnerFehler("Trafospannung U2 (eff) und Laststrom eingeben")
    uf = w["uf"] if w["uf"] is not None else 0.7
    u_spitze = U2 * math.sqrt(2)
    u_dc = u_spitze - 2 * uf
    if u_dc <= 0:
        raise RechnerFehler(f"U2 zu klein: Der Spitzenwert {fmt(u_spitze, 'spannung')} reicht nicht "
                            f"für 2 Dioden à {fmt(uf, 'spannung')}")
    zeilen = [f"Spitzenwert Û = U2 · √2 = {fmt(u_spitze, 'spannung')}",
              f"Nach Brücke (2 Dioden leiten): ≈ {fmt(u_dc, 'spannung')}  (Leerlauf, ohne Welligkeit)"]
    if C is not None:
        ripple = I / (2 * f * C)
        zeilen.append(f"Welligkeit ΔU ≈ I / (2·f·C) = {fmt(ripple, 'spannung')}")
        zeilen.append(f"Minimum ≈ {fmt(u_dc - ripple, 'spannung')}   Mittelwert ≈ {fmt(u_dc - ripple / 2, 'spannung')}")
    else:
        c_min = I / (2 * f * 0.1 * u_dc)
        zeilen.append(f"Für 10 % Welligkeit: C ≥ {fmt(c_min, 'kapazitaet')} "
                      f"(E6: {fmt(normreihen.naechste_werte(c_min, 'E6')[1], 'kapazitaet')})")
    zeilen.append(f"Elko-Spannungsfestigkeit: > {fmt(u_spitze * 1.1 * 1.2, 'spannung')} (Netz +10 %, Trafo im Leerlauf höher)")
    return zeilen


def netzteil(master):
    return FormelRechner(
        master, "Trafo + Gleichrichter + Elko", "Was kommt nach dem Brückengleichrichter heraus?",
        felder=[("U2", "Trafo U2 (eff)", "spannung", {"platzhalter": "z.B. 12"}),
                ("I", "Laststrom", "strom", {"einheit": "mA"}),
                ("C", "Ladeelko (opt.)", "kapazitaet", {"platzhalter": "optional"}),
                ("f", "Netzfrequenz", "frequenz", {"platzhalter": "50"}),
                ("uf", "Diodenspannung", "spannung", {"platzhalter": "0.7"})],
        berechnen=_netzteil, formel="Û = U · √2     ΔU ≈ I / (2 · f · C)   (Brücke = doppelte Netzfrequenz)")


RECHNER = {
    "trafo_animation": TrafoAnimation,
    "uebersetzung": uebersetzung,
    "leistung_trafo": leistung_trafo,
    "windungen": windungen,
    "netzteil": netzteil,
}
