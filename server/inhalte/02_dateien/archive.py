# =============================================================================
# Thema: Archive (tar, gzip, zip)  (Kategorie: Dateien & Navigation)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Archive: tar, gzip, zip",
    "reihenfolge": 7,
    "kurz": "Ordner zu einer Datei packen und komprimieren – für Backups und Übertragungen.",
    "stichworte": ["archiv", "tar", "tar.gz", "tgz", "gzip", "gunzip", "zip", "unzip", "packen", "entpacken",
                   "komprimieren", "zstd", "xz", "backup datei"],

    "erklaerung": """
## tar – der Linux-Standard
`tar` packt viele Dateien in **eine** Datei (Archiv) und behält dabei Rechte und Besitzer. Mit `z` wird zusätzlich mit gzip komprimiert → Endung **.tar.gz** (oder .tgz).
## Die Optionen merken
- **c** = create (packen), **x** = extract (entpacken), **t** = list (Inhalt anzeigen)
- **z** = gzip, **J** = xz (kleiner, langsamer), **v** = verbose (Dateien anzeigen), **f** = Dateiname folgt (**immer als letzte Option!**)
- Merksatz: **c**zvf = „**c**reate **z**e **v**ile **f**iles“, **x**zvf = „e**x**tract …“
## zip
Für den Austausch mit Windows ist `zip` praktischer. Muss auf Ubuntu Server meist erst installiert werden: `sudo apt install zip unzip`.
""",

    "befehle": [
        {"titel": "tar", "zeilen": [
            ("tar -czvf backup.tar.gz ordner/", "Ordner packen und komprimieren"),
            ("tar -tzvf backup.tar.gz", "Inhalt anzeigen, ohne zu entpacken"),
            ("tar -xzvf backup.tar.gz", "Im aktuellen Ordner entpacken"),
            ("tar -xzvf backup.tar.gz -C /ziel/", "In einen bestimmten Ordner entpacken"),
            ("sudo tar -czpf etc-$(date +%F).tar.gz /etc", "/etc mit Datum sichern (p = Rechte erhalten)"),
            ("tar -czvf web.tar.gz --exclude='*.log' /var/www", "Packen, aber .log-Dateien auslassen"),
        ]},
        {"titel": "gzip & zip", "zeilen": [
            ("gzip grosse.log", "Einzelne Datei komprimieren (wird zu grosse.log.gz)"),
            ("gunzip grosse.log.gz", "Wieder entpacken"),
            ("zcat alt.log.gz | less", "Komprimiertes Log lesen, ohne zu entpacken"),
            ("zip -r archiv.zip ordner/", "ZIP für Windows-Benutzer"),
            ("unzip archiv.zip -d ziel/", "ZIP in Ordner entpacken"),
        ]},
    ],

    "beispiele": [
        {"titel": "Konfiguration sichern, prüfen und zum PC holen",
         "code": {"Bash": r'''sudo tar -czpf ~/etc-backup-$(date +%F).tar.gz /etc
tar -tzf ~/etc-backup-*.tar.gz | head       # Stichprobe: ist etwas drin?

# auf DEINEM PC (PowerShell):
scp jorick@srv01:~/etc-backup-*.tar.gz .'''},
         "ausgabe": "tar: Removing leading `/' from member names\netc/\netc/hostname\netc/ssh/\n..."},
    ],

    "sicherheit": [
        "Nie fremde Archive **als root direkt in `/`** entpacken – ein manipuliertes Archiv kann Systemdateien überschreiben. Erst `tar -tzvf` anschauen, dann in einen leeren Ordner entpacken.",
        "Backups von `/etc` enthalten Passwort-Hashes und private Schlüssel (`/etc/ssh/ssh_host_*`) – Archiv mit `chmod 600` schützen und nicht offen herumliegen lassen.",
    ],
    "tipps": [
        "„Removing leading `/'“ ist kein Fehler – tar speichert Pfade absichtlich relativ, damit man sie überall entpacken kann.",
        "Für grosse Backups `zstd` ist deutlich schneller: `tar --zstd -cvf backup.tar.zst ordner/`.",
        "Alte Logs heissen oft `syslog.2.gz` – mit `zcat`, `zgrep` und `zless` kann man sie direkt lesen.",
    ],
    "fehler": [
        "`tar -czvf ordner/ backup.tar.gz` (Reihenfolge vertauscht) → Fehler oder falsches Archiv. Nach `f` kommt **immer** der Archivname.",
        "Das Archiv in den Ordner schreiben, den man gerade packt → tar packt sich selbst mit ein.",
    ],
    "siehe_auch": ["backups", "dateien_uebertragen", "dateien_verwalten"],
}
