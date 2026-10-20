# =============================================================================
# uebungen/server.py
# -----------------------------------------------------------------------------
# ÜBUNGEN SERVER / LINUX (Stufen 1–4). Inhalte orientiert an den öffentlichen Prüfungszielen des
# Linux Professional Institute: Linux Essentials (Exam 010, Version 2.0) für Stufe 1–2, LPIC-1 (101/102)
# für Stufe 3–4 (abgerufen 2026-10-20 auf lpi.org). Die Aufgaben sind EIGENE Aufgaben auf diesem Niveau.
#
# Wo immer möglich wird die Lösung BERECHNET statt von Hand eingetragen:
#   Pfade (posixpath), Dateirechte und umask (Bit-Rechnung), Globbing (Shell-Regeln: * passt nicht auf
#   versteckte Dateien), grep/sort/uniq/wc (auf den gezeigten Zeilen), Subnetze (Python-Modul ipaddress),
#   && / || und kleine Bash-Skripte (Regeln von Bash nachgerechnet).
# Befehls-Fragen kommen aus einer Tabelle mit Standard-Befehlen (BEFEHLE_1, BEFEHLE_2).
#
# Personen-Namen gibt es keine - Benutzer heissen z.B. "admin", "dienst", "benutzer".
# WER RUFT DAS AUF?  uebungen/aufgaben.py (lädt alle Übungs-Module)
# =============================================================================

import fnmatch
import ipaddress
import posixpath

from uebungen.kern import art                                        # -> uebungen/kern.py

S = "Server / Linux"
KONSOLE, DATEIEN, RECHTE, SYSTEM, NETZ, SKRIPTE = ("Konsole & Befehle", "Dateien & Pipes", "Benutzer & Rechte",
                                                   "System & Dienste", "Netzwerk", "Skripte")

# (Was soll passieren?, Befehl) - Standardbefehle (Linux Essentials 012/013)
BEFEHLE_1 = [
    ("Das aktuelle Verzeichnis anzeigen", "pwd"),
    ("Alle Dateien im Verzeichnis ausführlich auflisten, auch versteckte", "ls -la"),
    ("Ein neues Verzeichnis anlegen", "mkdir"),
    ("Eine leere Datei anlegen (oder ihren Zeitstempel aktualisieren)", "touch"),
    ("Eine Datei kopieren", "cp"),
    ("Eine Datei verschieben oder umbenennen", "mv"),
    ("Eine Datei löschen", "rm"),
    ("Ein leeres Verzeichnis löschen", "rmdir"),
    ("Den ganzen Inhalt einer Datei ausgeben", "cat"),
    ("Eine lange Datei seitenweise lesen", "less"),
    ("Die ersten 10 Zeilen einer Datei anzeigen", "head"),
    ("Neue Zeilen einer Logdatei laufend mitverfolgen", "tail -f"),
    ("Die Handbuchseite (Hilfe) zu einem Befehl öffnen", "man"),
    ("Zeilen mit einem bestimmten Text in einer Datei suchen", "grep"),
    ("Dateien nach Namen im Verzeichnisbaum suchen", "find"),
    ("Zeilen, Wörter und Zeichen einer Datei zählen", "wc"),
]
# (Linux Essentials 014/015, LPIC-1 103/104)
BEFEHLE_2 = [
    ("Alle laufenden Prozesse anzeigen", "ps aux"),
    ("CPU- und Speicherauslastung live anzeigen", "top"),
    ("Freien und belegten Arbeitsspeicher anzeigen", "free -h"),
    ("Belegung der Dateisysteme (Festplatten) anzeigen", "df -h"),
    ("Gesamtgrösse eines Verzeichnisses anzeigen", "du -sh"),
    ("Einen Dienst jetzt starten", "systemctl start"),
    ("Einen Dienst beim Systemstart automatisch starten", "systemctl enable"),
    ("Den Zustand eines Dienstes anzeigen", "systemctl status"),
    ("Die Logmeldungen eines bestimmten Dienstes anzeigen", "journalctl -u"),
    ("Die Paketlisten neu laden (Debian/Ubuntu)", "apt update"),
    ("Installierte Pakete auf den neusten Stand bringen (Debian/Ubuntu)", "apt upgrade"),
    ("Einen Befehl mit Administratorrechten ausführen", "sudo"),
    ("Den Besitzer einer Datei ändern", "chown"),
    ("Die Zugriffsrechte einer Datei ändern", "chmod"),
    ("Die IP-Adressen der Netzwerkschnittstellen anzeigen", "ip addr show"),
    ("Prüfen, ob ein anderer Rechner erreichbar ist", "ping"),
    ("Offene (lauschende) Ports und ihre Programme anzeigen", "ss -tulpn"),
    ("Sich auf einem entfernten Rechner verschlüsselt anmelden", "ssh"),
    ("Eine Datei verschlüsselt auf einen anderen Rechner kopieren", "scp"),
    ("Ein Verzeichnis als gzip-komprimiertes Archiv packen", "tar -czf"),
    ("Einem Prozess über seine PID ein Signal (Beenden) schicken", "kill"),
]


def _text(text, loesung, weg, gesucht, vergleich="genau", **mehr):
    return {"text": text, "antwort": "text", "loesung": loesung, "weg": weg, "gesucht": gesucht,
            "vergleich": vergleich, **mehr}


def _auswahl(z, text, richtig, falsch, weg, **mehr):
    optionen = [richtig] + [f for f in dict.fromkeys(falsch) if f != richtig][:3]   # höchstens 4 Optionen
    z.shuffle(optionen)
    return {"text": text, "antwort": "auswahl", "loesung": richtig, "optionen": optionen, "weg": weg,
            "gesucht": {"zeichen": "Antwort", "text": ""}, **mehr}


def _befehl(z, tabelle, hinweis):
    aufgabe, befehl = z.choice(tabelle)
    falsch = [b for _a, b in z.sample(tabelle, 5) if b != befehl][:3]
    optionen = [befehl] + falsch
    z.shuffle(optionen)
    return {"text": f"Welcher Befehl passt? {aufgabe}.", "antwort": "auswahl", "loesung": befehl, "optionen": optionen,
            "weg": [f"{aufgabe}: {befehl}", hinweis], "gesucht": {"zeichen": "Befehl", "text": ""}}


def _befehl_1(z):
    return _befehl(z, BEFEHLE_1, "Mehr dazu: man <befehl> oder <befehl> --help")


def _befehl_2(z):
    return _befehl(z, BEFEHLE_2, "Viele dieser Befehle brauchen sudo, wenn sie etwas am System ändern.")


# =============================================================================
# PFADE UND DATEIEN
# =============================================================================
HOME = "/home/benutzer"


def _cd(z, schwer):
    start = z.choice([HOME, f"{HOME}/projekte", "/var/log", "/etc/nginx", f"{HOME}/projekte/web/css"])
    if schwer:
        ziel = z.choice(["../..", "../log/./apt", "~/backup", "/tmp/../var", "./../../etc", "..//./.."])
    else:
        ziel = z.choice(["..", "daten", "/etc", "~", "../.."])
    voll = ziel.replace("~", HOME, 1) if ziel.startswith("~") else ziel
    neu = posixpath.normpath(posixpath.join(start, voll)) if not voll.startswith("/") else posixpath.normpath(voll)
    neu = "/" + neu.lstrip("/")
    return _text(f"Du bist im Verzeichnis {start} und gibst cd {ziel} ein. In welchem Verzeichnis bist du danach? "
                 f"(Dein Heimverzeichnis ist {HOME})", neu,
                 [". = aktuelles Verzeichnis, .. = eine Ebene höher, ~ = Heimverzeichnis, / am Anfang = absoluter Pfad",
                  f"Start {start}, dann Schritt für Schritt {ziel} anwenden  ->  {neu}",
                  "Kontrolle in der Konsole: pwd"],
                 {"zeichen": "Pfad", "text": "absoluter Pfad, z.B. /var/log"}, "genau")


def _cd_1(z):
    return _cd(z, False)


def _cd_2(z):
    return _cd(z, True)


DATEIEN_LISTE = ["bericht.txt", "notizen.txt", "Bild1.png", "bild2.png", "bild10.png", ".bashrc", "backup.tar.gz",
                 "log1.txt", "log2.txt", "log10.txt", "skript.sh", "daten.csv"]
MUSTER = ["*.txt", "bild?.png", "log?.txt", "*.*", "[bB]ild*", "*", "log*", "*.t?t", "b*"]


def _glob(z):
    muster = z.choice(MUSTER)
    treffer = [d for d in DATEIEN_LISTE if not d.startswith(".") and fnmatch.fnmatchcase(d, muster)]
    return _text(f"Im Verzeichnis liegen diese Dateien: {', '.join(DATEIEN_LISTE)}. Welche Dateien zeigt "
                 f"ls {muster} an? (Namen mit Leerzeichen getrennt)", " ".join(treffer) or "keine",
                 ["* = beliebig viele Zeichen, ? = genau ein Zeichen, [bB] = eines dieser Zeichen",
                  "Gross/Klein zählt. * und ? passen NICHT auf versteckte Dateien (Name beginnt mit .).",
                  f"{muster} passt auf: {', '.join(treffer) or 'keine'}"],
                 {"zeichen": "Dateien", "text": "Reihenfolge egal"}, "worte")


LOG = ["Jan 10 08:01 sshd: Accepted publickey for admin", "Jan 10 08:15 sshd: Failed password for root",
       "Jan 10 08:15 sshd: Failed password for root", "Jan 10 09:02 cron: Job backup started",
       "Jan 10 09:30 sshd: Failed password for invalid user test", "Jan 10 10:00 nginx: GET /index.html 200",
       "Jan 10 10:01 nginx: GET /admin 404", "Jan 10 10:05 sshd: Accepted password for dienst"]


def _grep_zaehlen(z):
    zeilen = z.sample(LOG, z.randint(5, 8))
    wort = z.choice(["Failed", "sshd", "nginx", "Accepted", "root", "404"])
    n = sum(1 for zeile in zeilen if wort in zeile)
    befehl = z.choice([f"grep -c '{wort}' auth.log", f"grep '{wort}' auth.log | wc -l"])
    return _text(f"Die Datei auth.log enthält die Zeilen im Kasten. Was gibt {befehl} aus?", str(n),
                 [f"grep findet alle Zeilen, die '{wort}' enthalten (Gross/Klein zählt).",
                  "grep -c zählt die Treffer; | wc -l zählt die Zeilen, die grep weitergibt – beides gleich.",
                  f"Treffer: {n}"],
                 {"zeichen": "Ausgabe", "text": "Zahl"}, "basis10", code="\n".join(zeilen), sprache="text")


def _sort_uniq(z):
    werte = [z.choice(["nginx", "sshd", "cron", "mysql", "nginx", "sshd"]) for _ in range(z.randint(6, 9))]
    befehl = z.choice(["uniq dienste.txt | wc -l", "sort dienste.txt | uniq | wc -l", "sort -u dienste.txt | head -n 1"])
    if befehl.startswith("uniq"):
        ohne = [w for i, w in enumerate(werte) if i == 0 or werte[i - 1] != w]
        loesung = str(len(ohne))
        erklaerung = f"uniq entfernt nur AUFEINANDERFOLGENDE Doppelte: {ohne} -> {loesung} Zeilen"
    elif befehl.startswith("sort dienste.txt | uniq"):
        loesung = str(len(set(werte)))
        erklaerung = f"Erst sortieren, dann uniq: jede Zeile nur noch einmal -> {sorted(set(werte))} = {loesung}"
    else:
        loesung = sorted(set(werte))[0]
        erklaerung = f"sort -u sortiert und entfernt Doppelte: {sorted(set(werte))}, head -n 1 nimmt die erste Zeile"
    return _text(f"Die Datei dienste.txt enthält die Zeilen im Kasten. Was gibt {befehl} aus?", loesung,
                 [erklaerung, "Darum steht vor uniq fast immer sort."],
                 {"zeichen": "Ausgabe", "text": ""}, "genau", code="\n".join(werte), sprache="text")


def _umleitung(z):
    schritte, zeilen = [], 0
    for k in range(z.randint(3, 5)):
        if k == 0 or z.random() < 0.35:
            schritte.append(f"echo 'Zeile {k + 1}' > protokoll.txt")
            zeilen = 1
        else:
            schritte.append(f"echo 'Zeile {k + 1}' >> protokoll.txt")
            zeilen += 1
    schritte.append("wc -l < protokoll.txt")
    return _text("Diese Befehle werden nacheinander ausgeführt. Was gibt der letzte Befehl aus?", str(zeilen),
                 ["> schreibt die Datei NEU (alter Inhalt weg), >> hängt hinten an.",
                  "Nach dem letzten > beginnt das Zählen wieder bei 1.", f"Am Ende hat die Datei {zeilen} Zeilen."],
                 {"zeichen": "Ausgabe", "text": "Zahl"}, "basis10", code="\n".join(schritte), sprache="bash")


# =============================================================================
# BENUTZER UND RECHTE
# =============================================================================
def _rwx(oktal):
    return "".join(("r" if d & 4 else "-") + ("w" if d & 2 else "-") + ("x" if d & 1 else "-")
                   for d in (oktal >> 6 & 7, oktal >> 3 & 7, oktal & 7))


RECHTE_WERTE = [0o644, 0o640, 0o600, 0o755, 0o750, 0o700, 0o664, 0o775, 0o444, 0o711, 0o660, 0o754]


def _oktal_zu_rwx(z):
    o = z.choice(RECHTE_WERTE)
    return _text(f"Welche Rechte (rwx-Schreibweise wie bei ls -l, 9 Zeichen) setzt chmod {o:o} datei?", _rwx(o),
                 ["Jede Ziffer steht für Besitzer, Gruppe, Andere: r = 4, w = 2, x = 1 (addiert)",
                  " · ".join(f"{d} = {_rwx(d)[6:]}" for d in (o >> 6 & 7, o >> 3 & 7, o & 7)),
                  f"Zusammen: {_rwx(o)}"],
                 {"zeichen": "Rechte", "text": "z.B. rw-r--r--"}, "genau")


def _rwx_zu_oktal(z):
    o = z.choice(RECHTE_WERTE)
    return _text(f"ls -l zeigt bei einer Datei -{_rwx(o)}. Mit welcher Zahl setzt man diese Rechte per chmod?",
                 f"{o:o}",
                 ["r = 4, w = 2, x = 1 – pro Dreiergruppe addieren (Besitzer, Gruppe, Andere)",
                  " · ".join(f"{_rwx(o)[i:i + 3]} = {(o >> (6 - i)) & 7}" for i in (0, 3, 6)),
                  f"chmod {o:o} datei"],
                 {"zeichen": "chmod", "text": "3 Ziffern, z.B. 640"}, "genau")


def _chmod_symbolisch(z):
    start = z.choice([0o644, 0o640, 0o600, 0o755, 0o700])
    aenderungen = z.choice(["g+w", "o-r", "u+x", "g-r,o-r", "a+x", "go-w", "u-w", "g+rx"])
    neu = start
    for teil in aenderungen.split(","):                              # z.B. "g-r" -> wer "g", op "-", rechte "r"
        op = "+" if "+" in teil else "-"
        wer, rechte = teil.split(op)
        bits = sum({"r": 4, "w": 2, "x": 1}[r] for r in rechte)
        for w in wer.replace("a", "ugo"):
            stelle = {"u": 6, "g": 3, "o": 0}[w]
            neu = neu | (bits << stelle) if op == "+" else neu & ~(bits << stelle)
    return _text(f"Eine Datei hat die Rechte {start:o} (-{_rwx(start)}). Danach wird chmod {aenderungen} datei "
                 "ausgeführt. Welche Rechte (als Zahl) hat sie jetzt?", f"{neu:o}",
                 ["u = Besitzer, g = Gruppe, o = Andere, a = alle;  + gibt Rechte dazu, − nimmt sie weg",
                  f"Vorher: {_rwx(start)}  ->  nachher: {_rwx(neu)}", f"Als Zahl: {neu:o}"],
                 {"zeichen": "Rechte", "text": "3 Ziffern"}, "genau")


def _umask(z):
    m = z.choice([0o022, 0o027, 0o077, 0o002, 0o007])
    art_ = z.choice(["Datei", "Verzeichnis"])
    basis = 0o666 if art_ == "Datei" else 0o777
    ergebnis = basis & ~m
    objekt = "eine neue DATEI" if art_ == "Datei" else "ein neues VERZEICHNIS"
    return _text(f"Die umask ist {m:03o}. Mit welchen Rechten (als Zahl) wird {objekt} angelegt?",
                 f"{ergebnis:o}",
                 [f"Ausgangsrechte: Dateien 666 (nie x), Verzeichnisse 777. Hier: {basis:o}",
                  f"Die umask nimmt Rechte WEG: {basis:o} ohne {m:03o} = {ergebnis:o} ({_rwx(ergebnis)})"],
                 {"zeichen": "Rechte", "text": "3 Ziffern"}, "genau")


def _rechte_pruefen(z):
    o = z.choice(RECHTE_WERTE)
    wer = z.choice(["Besitzer", "Gruppe", "Andere"])
    recht = z.choice([("lesen", 4), ("schreiben", 2), ("ausführen", 1)])
    stelle = {"Besitzer": 6, "Gruppe": 3, "Andere": 0}[wer]
    darf = bool((o >> stelle) & recht[1])
    zeile = f"-{_rwx(o)} 1 admin technik 1824 Jan 10 09:00 bericht.sh"
    wer_text = {"Besitzer": "der Benutzer admin (Besitzer)", "Gruppe": "ein Mitglied der Gruppe technik",
                "Andere": "ein anderer Benutzer (nicht in technik)"}[wer]
    gruppe = _rwx(o)[{6: 0, 3: 3, 0: 6}[stelle]:][:3]
    zeichen = {4: "r", 2: "w", 1: "x"}[recht[1]]
    return _auswahl(z, f"ls -l zeigt: {zeile}. Darf {wer_text} die Datei {recht[0]}? (ohne sudo)",
                    "Ja" if darf else "Nein", ["Ja", "Nein"],
                    ["Aufbau: Typ, dann rwx für Besitzer | Gruppe | Andere, dann Besitzer und Gruppe",
                     f"{wer}: {gruppe}  ->  {recht[0]} ({zeichen}) {'erlaubt' if darf else 'nicht erlaubt'}"])


# =============================================================================
# SYSTEM, NETZWERK, SKRIPTE
# =============================================================================
CRON = [("*/15 * * * *", "alle 15 Minuten"), ("0 2 * * *", "jeden Tag um 02:00 Uhr"),
        ("0 0 * * 0", "jeden Sonntag um Mitternacht"), ("30 6 * * 1-5", "Montag bis Freitag um 06:30 Uhr"),
        ("0 */4 * * *", "alle 4 Stunden zur vollen Stunde"), ("0 0 1 * *", "am 1. jedes Monats um Mitternacht"),
        ("15 14 * * *", "jeden Tag um 14:15 Uhr")]


def _cron(z):
    ausdruck, bedeutung = z.choice(CRON)
    falsch = [b for a, b in CRON if a != ausdruck]
    z.shuffle(falsch)
    return _auswahl(z, f"Wann läuft ein Cronjob mit dem Zeitplan {ausdruck}?", bedeutung, falsch[:3],
                    ["Die 5 Felder: Minute  Stunde  Tag-des-Monats  Monat  Wochentag (0 und 7 = Sonntag)",
                     "* = jeder Wert, */n = alle n, a-b = Bereich",
                     f"{ausdruck} = {bedeutung}"])


PORTS = [("SSH", 22), ("HTTP", 80), ("HTTPS", 443), ("DNS", 53), ("SMTP (Mail versenden)", 25), ("NTP (Zeit)", 123),
         ("FTP (Steuerung)", 21), ("MQTT (unverschlüsselt)", 1883)]


def _port(z):
    dienst, port = z.choice(PORTS)
    return _text(f"Auf welchem Standard-Port lauscht {dienst}?", str(port),
                 [f"{dienst}: Port {port} (von der IANA festgelegt)",
                  "Prüfen, welche Ports offen sind: sudo ss -tulpn"],
                 {"zeichen": "Port", "text": "Zahl"}, "basis10")


def _hosts(z):
    p = z.randint(20, 30)
    netz = ipaddress.ip_network(f"192.168.0.0/{p}", strict=False)
    n = netz.num_addresses - 2
    return _text(f"Wie viele Geräte (Host-Adressen) passen in ein IPv4-Netz mit der Präfixlänge /{p}?", str(n),
                 [f"/{p}: {p} Bit Netzanteil, {32 - p} Bit für Hosts -> 2^{32 - p} = {netz.num_addresses} Adressen",
                  "Davon sind 2 reserviert: Netzadresse (alle Host-Bits 0) und Broadcast (alle Host-Bits 1)",
                  f"Nutzbar: {netz.num_addresses} − 2 = {n}"],
                 {"zeichen": "Hosts", "text": "Anzahl"}, "basis10")


def _netzadresse(z):
    p = z.choice([22, 24, 25, 26, 27, 28, 29])
    erster = z.choice(["10.{}.{}", "172.{}.{}", "192.168.{}"])        # private Bereiche (RFC 1918)
    if erster.startswith("10."):
        ip_text = f"10.{z.randint(0, 255)}.{z.randint(0, 255)}.{z.randint(1, 254)}"
    elif erster.startswith("172."):
        ip_text = f"172.{z.randint(16, 31)}.{z.randint(0, 255)}.{z.randint(1, 254)}"
    else:
        ip_text = f"192.168.{z.randint(0, 255)}.{z.randint(1, 254)}"
    ip = ipaddress.ip_address(ip_text)
    netz = ipaddress.ip_network(f"{ip}/{p}", strict=False)
    frage = z.choice(["Netzadresse", "Broadcast-Adresse"])
    loesung = str(netz.network_address if frage == "Netzadresse" else netz.broadcast_address)
    return _text(f"Ein Gerät hat die Adresse {ip}/{p}. Wie lautet die {frage} seines Netzes?", loesung,
                 [f"/{p} = Subnetzmaske {netz.netmask}",
                  f"Netzadresse = Adresse UND Maske = {netz.network_address}",
                  f"Broadcast = alle Host-Bits auf 1 = {netz.broadcast_address}",
                  f"Nutzbare Adressen: {netz.network_address + 1} … {netz.broadcast_address - 1}"],
                 {"zeichen": frage, "text": "z.B. 192.168.1.0"}, "genau")


def _und_oder(z):
    a, b = z.choice([True, False]), z.choice([True, False])
    befehl_a = "ping -c 1 server" if a else "ping -c 1 gibtesnicht.invalid"
    befehl_b = "mkdir /tmp/test" if b else "mkdir /root/test"                # /tmp/test gibt es noch nicht
    code = f"{befehl_a} > /dev/null && {befehl_b} && echo 'beides ok' || echo 'Fehler'"
    if a and b:
        loesung, grund = "beides ok", "Beide Befehle sind erfolgreich (Exit-Status 0) -> echo 'beides ok' läuft, || wird übersprungen."
    else:
        teil = "der erste Befehl" if not a else "mkdir (ohne Rechte für /root)"
        loesung, grund = "Fehler", f"{teil} schlägt fehl -> die &&-Kette bricht ab und der Teil nach || läuft."
    return _text("Annahme: server ist erreichbar, gibtesnicht.invalid nicht; du bist ein normaler Benutzer (kein root). "
                 "Was gibt diese Zeile aus?", loesung,
                 ["&& : rechter Befehl nur, wenn der linke ERFOLGREICH war (Exit-Status 0)",
                  "|| : rechter Befehl nur, wenn der linke FEHLGESCHLAGEN ist", grund],
                 {"zeichen": "Ausgabe", "text": ""}, "genau", code=code, sprache="bash")


def _bash_skript(z):
    k, grenze = z.randint(2, 5), z.choice([15, 20, 30, 40])
    werte = z.sample(range(1, 7), 3)
    summe = sum(i * k for i in werte)
    code = (f"#!/bin/bash\nsumme=0\nfor i in {' '.join(map(str, werte))}; do\n    summe=$((summe + i * {k}))\ndone\n"
            f"if [ \"$summe\" -gt {grenze} ]; then\n    echo \"gross $summe\"\nelse\n    echo \"klein $summe\"\nfi")
    loesung = f"{'gross' if summe > grenze else 'klein'} {summe}"
    return _text("Was gibt dieses Bash-Skript aus?", loesung,
                 [f"Die Schleife geht durch {werte}: summe = " + " + ".join(f"{i}·{k}" for i in werte) + f" = {summe}",
                  f"[ \"$summe\" -gt {grenze} ]: -gt heisst 'grösser als' -> {summe} > {grenze} ist {summe > grenze}",
                  f"Ausgabe: {loesung}"],
                 {"zeichen": "Ausgabe", "text": ""}, "genau", code=code, sprache="bash")


def _systemctl_wahl(z):
    faelle = [("Ein Dienst soll SOFORT laufen, aber nach einem Neustart nicht automatisch starten.", "systemctl start dienst"),
              ("Ein Dienst soll ab jetzt bei jedem Systemstart starten UND sofort laufen.", "systemctl enable --now dienst"),
              ("Die Konfiguration wurde geändert – der Dienst soll sie ohne Unterbruch neu einlesen (falls er das kann).",
               "systemctl reload dienst"),
              ("Ein Dienst soll beim Systemstart NICHT mehr automatisch starten.", "systemctl disable dienst")]
    frage, richtig = z.choice(faelle)
    return _auswahl(z, f"Welcher Befehl passt? {frage}", richtig, [b for _f, b in faelle] + ["systemctl status dienst"],
                    ["start/stop: jetzt;  enable/disable: beim Systemstart;  --now: beides auf einmal",
                     "reload: Konfiguration neu lesen ohne Neustart (nicht jeder Dienst kann das; sonst restart)",
                     f"-> {richtig} (mit sudo)"])


# =============================================================================
# ANMELDEN
# =============================================================================
_LISTE = [
    ("linux_befehl_1", "Grundbefehle: welcher Befehl?", KONSOLE, 1, "spickzettel", _befehl_1),
    ("linux_cd_1", "Pfade: wo bin ich nach cd?", KONSOLE, 1, "navigieren", _cd_1),
    ("linux_befehl_2", "System-Befehle: welcher Befehl?", KONSOLE, 2, "spickzettel", _befehl_2),
    ("linux_cd_2", "Pfade mit .., . und ~", KONSOLE, 2, "navigieren", _cd_2),
    ("linux_glob", "Platzhalter * ? [ ]", DATEIEN, 2, "dateien_verwalten", _glob),
    ("linux_grep", "grep und wc zählen", DATEIEN, 2, "pipes_umleitung", _grep_zaehlen),
    ("linux_umleitung", "Umleitung > und >>", DATEIEN, 2, "pipes_umleitung", _umleitung),
    ("linux_sort_uniq", "sort und uniq", DATEIEN, 3, "pipes_umleitung", _sort_uniq),
    ("linux_oktal_rwx", "chmod: Zahl → rwx", RECHTE, 2, "dateirechte", _oktal_zu_rwx),
    ("linux_rwx_oktal", "chmod: rwx → Zahl", RECHTE, 2, "dateirechte", _rwx_zu_oktal),
    ("linux_rechte_pruefen", "ls -l lesen: wer darf was?", RECHTE, 2, "dateirechte", _rechte_pruefen),
    ("linux_chmod_symbolisch", "chmod mit u/g/o +/-", RECHTE, 3, "dateirechte", _chmod_symbolisch),
    ("linux_umask", "umask", RECHTE, 3, "dateirechte", _umask),
    ("linux_port", "Standard-Ports", NETZ, 2, "offene_ports", _port),
    ("linux_hosts", "Subnetz: Anzahl Hosts", NETZ, 3, "netzwerk_konfig", _hosts),
    ("linux_netzadresse", "Subnetz: Netz- und Broadcast-Adresse", NETZ, 4, "netzwerk_konfig", _netzadresse),
    ("linux_systemctl", "systemctl: start, enable, reload", SYSTEM, 3, "dienste_systemctl", _systemctl_wahl),
    ("linux_cron", "Cron-Zeitplan lesen", SYSTEM, 3, "cron", _cron),
    ("linux_und_oder", "&& und || in der Shell", SKRIPTE, 3, "bash_skripte", _und_oder),
    ("linux_bash_skript", "Bash-Skript: Ausgabe", SKRIPTE, 4, "bash_skripte", _bash_skript),
]
for _id, _titel, _thema, _stufe, _seite, _erz in _LISTE:
    art(_id, _titel, S, _thema, _stufe, [(S, _seite)], _erz)
