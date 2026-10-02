# =============================================================================
# Thema: Festplatten & Speicherplatz  (Kategorie: System & Dienste)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Festplatten, Speicherplatz & mount",
    "reihenfolge": 5,
    "kurz": "Speicher voll? Neue Festplatte einbinden? df, du, lsblk, mount und fstab.",
    "stichworte": ["festplatte", "disk", "speicher", "speicherplatz", "voll", "df", "du", "lsblk", "blkid",
                   "mount", "umount", "einhängen", "fstab", "uuid", "partition", "formatieren", "mkfs", "ext4",
                   "lvm", "ncdu", "inode", "no space left", "usb"],

    "erklaerung": """
## Wie viel Platz ist frei?
- **`df -h`** (disk free) – freier Platz **pro Laufwerk/Partition**
- **`du -sh ordner`** (disk usage) – wie viel ein **Ordner** belegt
- **`ncdu`** – interaktiv durch die Ordner klicken und sehen, was gross ist (`sudo apt install ncdu`)
Voll ist meist `/` bzw. `/var` – Logs, Docker-Images, alte Kernel, Datenbanken.
## Geräte und Partitionen
Festplatten heissen `/dev/sda`, `/dev/sdb` … (NVMe: `/dev/nvme0n1`), Partitionen `/dev/sda1`, `/dev/sda2`. **`lsblk -f`** zeigt alle mit Dateisystem und Einhängepunkt.
Ubuntu Server installiert oft **LVM** (logische Volumes, z.B. `/dev/mapper/ubuntu--vg-ubuntu--lv`). Tipp: Der Installer nutzt standardmässig nicht die ganze Platte – freien Platz kann man später mit `lvextend` hinzufügen.
## Einhängen (mount)
Eine Partition wird in einen **leeren Ordner** eingehängt: `sudo mount /dev/sdb1 /mnt/daten`. Das gilt nur bis zum Neustart. **Dauerhaft** → Eintrag in **`/etc/fstab`**.
## fstab – immer mit UUID
Gerätenamen wie `/dev/sdb` können sich beim Neustart ändern. Deshalb in der fstab die **UUID** verwenden (`sudo blkid`).
""",

    "befehle": [
        {"titel": "Platz prüfen", "zeilen": [
            ("df -h", "Freier Platz pro Laufwerk"),
            ("df -i", "Freie Inodes (Platz da, aber „No space left“? → viele kleine Dateien)"),
            ("sudo du -sh /var/*", "Grösse jedes Ordners in /var"),
            ("sudo du -h --max-depth=1 / 2>/dev/null | sort -rh | head", "Die grössten Ordner auf oberster Ebene"),
            ("sudo ncdu /", "Interaktiv suchen, was Platz frisst"),
        ]},
        {"titel": "Geräte", "zeilen": [
            ("lsblk -f", "Alle Laufwerke, Partitionen, Dateisysteme, Einhängepunkte"),
            ("sudo blkid", "UUIDs aller Partitionen (für fstab)"),
            ("findmnt", "Was ist wo eingehängt (als Baum)"),
            ("sudo fdisk -l", "Partitionstabellen anzeigen (nur lesen)"),
        ]},
        {"titel": "Einhängen", "zeilen": [
            ("sudo mkdir -p /mnt/daten", "Einhängepunkt anlegen"),
            ("sudo mount /dev/sdb1 /mnt/daten", "Einhängen (bis zum Neustart)"),
            ("sudo umount /mnt/daten", "Aushängen (vor dem Abziehen!)"),
            ("sudo findmnt --verify", "fstab auf Fehler prüfen"),
            ("sudo mount -a", "Alles aus fstab einhängen – TEST vor dem Neustart"),
        ]},
        {"titel": "Platz schaffen", "zeilen": [
            ("sudo apt autoremove && sudo apt clean", "Alte Pakete und Kernel, Paket-Cache"),
            ("sudo journalctl --vacuum-size=500M", "Journal auf 500 MB begrenzen"),
            ("docker system df", "Wie viel belegt Docker? (falls installiert)"),
        ]},
    ],

    "beispiele": [
        {"titel": "Neue (leere!) Festplatte formatieren und dauerhaft einbinden",
         "text": "**Achtung:** `mkfs` löscht ALLES auf der Partition. Mit `lsblk -f` dreimal prüfen, dass `/dev/sdb1` wirklich die neue, leere Platte ist!",
         "code": {"Bash": r'''lsblk -f                                # welche Platte ist neu? (keine FSTYPE, kein MOUNTPOINT)
sudo mkfs.ext4 /dev/sdb1                # FORMATIEREN – löscht alles auf sdb1!
sudo mkdir -p /mnt/daten
sudo blkid /dev/sdb1                    # UUID kopieren
echo "UUID=1234-abcd /mnt/daten ext4 defaults,nofail 0 2" | sudo tee -a /etc/fstab
sudo findmnt --verify && sudo mount -a  # testen, BEVOR neu gestartet wird
df -h /mnt/daten'''}},
        {"titel": "Speicher voll: Schritt für Schritt eingrenzen",
         "code": {"Bash": r'''df -h /
sudo du -h --max-depth=1 / 2>/dev/null | sort -rh | head -5
sudo du -h --max-depth=1 /var 2>/dev/null | sort -rh | head -5
sudo du -h --max-depth=1 /var/log 2>/dev/null | sort -rh | head -5'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 Eine fstab-Zeile",
            "kopf": ["Feld", "Beispiel", "Bedeutung"],
            "zeilen": [
                ["Gerät", "UUID=1234-abcd", "welche Partition (immer UUID, nicht /dev/sdb1)"],
                ["Einhängepunkt", "/mnt/daten", "wohin"],
                ["Dateisystem", "ext4", "ext4, xfs, vfat, nfs, cifs …"],
                ["Optionen", "defaults,nofail", "nofail: Server bootet trotzdem, wenn die Platte fehlt"],
                ["dump", "0", "veraltet, immer 0"],
                ["pass", "2", "Prüfreihenfolge: 1 = /, 2 = andere, 0 = nie"],
            ],
        },
    ],

    "sicherheit": [
        "**Nie `mkfs`, `fdisk`, `parted`, `wipefs` oder `dd` auf ein Gerät**, ohne mit `lsblk -f` dreifach geprüft zu haben, welches es ist. Ein vertauschter Buchstabe (`sda` statt `sdb`) löscht das System.",
        "Nie nach einer fstab-Änderung neu starten, ohne vorher `sudo findmnt --verify` und `sudo mount -a` fehlerfrei durchlaufen zu lassen – sonst bootet der Server nicht mehr (Notfall-Konsole nötig, per SSH unerreichbar).",
        "Für Zusatzplatten in der fstab immer `nofail` setzen.",
        "Nie Logs oder Datenbank-Dateien löschen, die gerade offen sind, um Platz zu schaffen – der Platz wird erst frei, wenn der Prozess sie schliesst, und die Anwendung kann kaputtgehen.",
    ],
    "tipps": [
        "Ab ca. **85–90 %** Belegung handeln: Datenbanken und Updates brauchen Reserve, bei 100 % stürzen Dienste ab.",
        "Gelöschte, aber noch offene Dateien belegen weiter Platz: `sudo lsof +L1` findet sie.",
        "Netzlaufwerke (NAS): `cifs` (Windows/SMB) oder `nfs` in der fstab, immer mit `nofail` und `_netdev`.",
    ],
    "fehler": [
        "`df` zeigt voll, `du` findet nichts → gelöschte, noch offene Datei (`lsof +L1`) oder etwas liegt **unter** einem Einhängepunkt versteckt.",
        "`umount: target is busy` → jemand ist noch in dem Ordner (auch deine eigene Shell!). `cd` raus, `sudo lsof +D /mnt/daten`.",
        "Tippfehler in fstab → Server hängt beim Booten im Emergency Mode.",
    ],
    "siehe_auch": ["systeminfo", "logs", "backups", "fehlersuche"],
}
