# =============================================================================
# core/tipps.py
# -----------------------------------------------------------------------------
# "TIPP DES TAGES" auf der Startseite: Bedienung von SystemLab und Fachwissen gemischt.
# Der Tipp hängt vom Datum ab -> er wechselt einmal pro Tag und bleibt den ganzen Tag gleich.
# "Nächster Tipp ›" blättert weiter (tipp_des_tages(versatz)).
#
# NEUER TIPP: einfach eine Zeile in TIPPS ergänzen (fachlich geprüft, kurz, ein Satz).
# WER RUFT DAS AUF?  gui/startseite_gui.py
# =============================================================================

import datetime

TIPPS = [
    # ---- Bedienung ----
    "Ctrl + K springt von überall in die grosse Suche auf der Startseite.",
    "Ctrl + F springt in die Suche von Programmieren bzw. Server / Linux.",
    "Mit ☆ oben rechts merkst du dir eine Seite oder einen Rechner als Favorit – er erscheint dann hier auf der Startseite.",
    "Werte kannst du direkt mit Einheit tippen: 4k7 = 4.7 kΩ, 2.2M = 2.2 MΩ, 470m = 0.47, 100n = 100 nF.",
    "Enter in einem Rechner-Feld rechnet sofort – der Knopf „Berechnen“ ist nicht nötig.",
    "Der ❓-Knopf oben rechts in jedem Rechner erklärt, welche Werte rein müssen.",
    "Wechselst du bei einem Regler die Einheit, reicht der Regler bis zur nächsten Einheit (z.B. 0 … 1000 mV).",
    "↺ Zurücksetzen stellt bei Schaltungen alle Regler, Schalter und Felder wieder auf die Startwerte.",
    "☰ oben links blendet die Seitenliste aus – mehr Platz für Schaltpläne und Diagramme.",
    "Die Seitenliste kannst du am Rand mit der Maus breiter ziehen – Doppelklick stellt die Standardbreite her.",
    "Ctrl + Mausrad oder Ctrl + Plus / Minus vergrössert alles, Ctrl + 0 stellt 100 % wieder her.",
    "Das Kategorie-Icon oben (z.B. 💡 bei Dioden) führt zur Übersicht dieser Kategorie, ◀ eine Seite zurück.",
    "Im KV-Diagramm kannst du die Felder direkt anklicken: 0 → 1 → X → 0.",
    "Bei Lade- und Entladekurven springen die Knöpfe 1τ … 5τ direkt zum gewünschten Zeitpunkt.",
    "Strom- und Spannungspfeile in den Schaltplänen lassen sich oben in der Karte aus- und einblenden.",
    # ---- Fachwissen ----
    "P = U · I – Leistung ist Spannung mal Strom.",
    "τ = R · C – nach 5τ ist ein Kondensator zu über 99 % geladen.",
    "Nach 1τ ist ein RC-Glied zu 63 % geladen, beim Entladen sind noch 37 % übrig.",
    "Zwei gleiche Widerstände parallel ergeben den halben Wert, in Reihe den doppelten.",
    "Kondensatoren in Reihe rechnet man wie Widerstände parallel – und umgekehrt.",
    "Pt1000 statt Pt100: Derselbe Leitungswiderstand verursacht einen 10× kleineren Messfehler.",
    "1 Byte = 8 Bit → Wertebereich 0 … 255 (unsigned) bzw. −128 … 127 (signed).",
    "Eine Hex-Ziffer entspricht genau 4 Bit: 0xF = 1111.",
    "Butterworth-Filter: Q = 0.707 – maximal flach im Durchlassbereich.",
    "Jede induktive Last (Relais, Motor, Ventil) braucht eine Freilaufdiode, sonst zerstört die Abschaltspitze den Transistor.",
    "Abtasttheorem: Die Abtastrate muss mehr als doppelt so hoch sein wie die höchste Signalfrequenz.",
    "Ein Multimeter misst Spannung parallel (hochohmig) und Strom in Reihe (niederohmig).",
    "Ugs(th) ist NICHT die Spannung, bei der ein MOSFET voll durchschaltet – massgebend ist Rds(on) im Datenblatt.",
    "Python: Einrückung ist Teil der Syntax – üblich sind 4 Leerzeichen pro Ebene.",
    "Linux: sudo !! wiederholt den letzten Befehl mit Admin-Rechten.",
]


def tipp_des_tages(versatz=0, datum=None):
    """Tipp für heute (versatz > 0 = die nächsten Tipps). Wechselt einmal pro Tag."""
    tag = (datum or datetime.date.today()).toordinal()
    return TIPPS[(tag + versatz) % len(TIPPS)]
