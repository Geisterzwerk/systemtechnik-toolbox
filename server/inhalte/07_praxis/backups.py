# =============================================================================
# Thema: Backups  (Kategorie: Praxis)
# NUR DATEN - dargestellt von programmieren/engine/seite.py
# =============================================================================

THEMA = {
    "titel": "Backups: 3-2-1 und Wiederherstellung",
    "reihenfolge": 3,
    "kurz": "Ein Backup ist erst dann eines, wenn die Wiederherstellung getestet ist.",
    "stichworte": ["backup", "sicherung", "datensicherung", "3-2-1", "wiederherstellen", "restore", "rsync",
                   "tar", "snapshot", "datenbank backup", "mysqldump", "pg_dump", "restic", "borg",
                   "offsite", "ransomware", "proxmox backup"],

    "erklaerung": """
## Die 3-2-1-Regel
- **3** Kopien der Daten (Original + 2 Backups)
- auf **2** verschiedenen Medien (z.B. Server-Platte + NAS)
- **1** Kopie ausser Haus bzw. offline (Cloud, externe Platte im Schrank)
Warum? Ransomware verschlüsselt alles, was erreichbar ist. Ein Brand oder Einbruch nimmt alles mit, was im selben Raum steht.
## Snapshot ist KEIN Backup
Ein Proxmox-Snapshot liegt auf **derselben** Platte wie die VM. Stirbt die Platte, ist beides weg. Snapshots sind perfekt als schneller Rückweg vor Updates – aber zusätzlich braucht es echte Backups (z.B. Proxmox Backup Server, `vzdump` auf ein anderes Gerät).
## Was muss gesichert werden?
- **Daten:** `/home`, `/srv`, `/var/www`, eigene Ordner
- **Konfiguration:** `/etc` (klein, spart bei Neuinstallation Stunden)
- **Datenbanken:** nie die laufenden Dateien kopieren, sondern **Dump** erstellen (`mysqldump`, `pg_dump`)
- **Nicht nötig:** `/proc`, `/sys`, `/dev`, `/tmp`, `/run` und Programme (die installiert man neu)
## Wiederherstellen testen
Mindestens einmal pro Quartal: eine Datei, einen Ordner **und** eine Datenbank aus dem Backup zurückholen – am besten in einer Test-VM. Viele merken erst im Ernstfall, dass das Backup seit Monaten leer war.
""",

    "befehle": [
        {"titel": "Sichern", "zeilen": [
            ("sudo rsync -aAX --delete /srv/daten/ /mnt/backup/daten/", "Ordner spiegeln (A=ACLs, X=Attribute)"),
            ("sudo tar -czpf /mnt/backup/etc-$(date +%F).tar.gz /etc", "Konfiguration mit Datum"),
            ("sudo mysqldump --all-databases --single-transaction > db.sql", "MySQL/MariaDB-Dump"),
            ("sudo -u postgres pg_dumpall > db.sql", "PostgreSQL-Dump"),
        ]},
        {"titel": "Prüfen & wiederherstellen", "zeilen": [
            ("ls -lh /mnt/backup/", "Sind die Backups da und nicht 0 Byte gross?"),
            ("tar -tzf /mnt/backup/etc-2026-09-29.tar.gz | head", "Inhalt stichprobenartig prüfen"),
            ("tar -xzf etc-2026-09-29.tar.gz -C /tmp/restore etc/ssh/sshd_config", "EINE Datei in einen Testordner zurückholen"),
            ("rsync -avn /mnt/backup/daten/ /srv/daten/", "Trockenlauf: was würde zurückgespielt?"),
        ]},
    ],

    "beispiele": [
        {"titel": "Einfaches Backup-Skript mit Aufbewahrung (7 Tage)",
         "text": "Als `/usr/local/bin/backup.sh` speichern, `sudo chmod 700`, per cron täglich ausführen. Das Ziel sollte ein **anderes Gerät** sein (NAS, zweite Platte).",
         "code": {"Bash": r'''#!/bin/bash
set -euo pipefail
ZIEL="/mnt/backup"
DATUM=$(date +%F)

mountpoint -q "$ZIEL" || { echo "Backup-Ziel nicht eingehängt!" >&2; exit 1; }

tar -czpf "$ZIEL/etc-$DATUM.tar.gz" /etc
rsync -aAX --delete /srv/daten/ "$ZIEL/daten/"
mysqldump --all-databases --single-transaction | gzip > "$ZIEL/db-$DATUM.sql.gz"

find "${ZIEL:?}" -maxdepth 1 -name "*.gz" -mtime +7 -delete   # ältere als 7 Tage löschen
echo "$(date '+%F %T') Backup ok"'''}},
    ],

    "tabellen": [
        {
            "titel": "📊 Backup-Werkzeuge",
            "kopf": ["Werkzeug", "Stärke", "Einsatz"],
            "zeilen": [
                ["rsync", "einfach, überall vorhanden", "Spiegel eines Ordners (kein Versionsverlauf!)"],
                ["tar + Datum", "einfach, versioniert", "Konfiguration, kleinere Datenmengen"],
                ["restic / borg", "verschlüsselt, dedupliziert, Versionen", "richtige Server-Backups, auch in die Cloud"],
                ["Proxmox Backup Server", "ganze VMs, inkrementell, dedupliziert", "Proxmox-Umgebungen"],
                ["mysqldump / pg_dump", "konsistente Datenbank-Sicherung", "vor dem Datei-Backup ausführen"],
            ],
        },
    ],

    "sicherheit": [
        "Nie das einzige Backup auf **derselben** Platte oder demselben Server – das ist nur eine Kopie.",
        "Nie Backups für den Server **beschreib- und löschbar** lassen, auf dem sie entstehen – Ransomware löscht sie mit. Besser: Backup-Server holt die Daten (Pull) oder unveränderliche Backups.",
        "Backups enthalten alles Geheime (Passwort-Hashes, Schlüssel, Kundendaten) → Rechte 600 bzw. verschlüsseln (restic/borg tun das automatisch).",
        "Nie `rsync --delete` als einziges Backup: Löscht jemand eine Datei (oder verschlüsselt sie), ist sie nach dem nächsten Lauf auch im Backup weg/verschlüsselt. Es braucht Versionen.",
    ],
    "tipps": [
        "`mountpoint -q` im Skript verhindert, dass bei nicht eingehängter NAS das Backup die System-Platte vollschreibt.",
        "Backup-Erfolg überwachen: Log prüfen oder eine Nachricht (Mail, Healthchecks.io) schicken lassen.",
        "Dokumentieren, **wie** man wiederherstellt – im Ernstfall ist man gestresst.",
    ],
    "fehler": [
        "Laufende Datenbank-Dateien (`/var/lib/mysql`) kopiert → Backup inkonsistent, oft unbrauchbar.",
        "Backup-Job schlägt seit Wochen still fehl – niemand schaut ins Log.",
        "Nur Daten gesichert, aber keine Konfiguration → Wiederaufbau dauert Tage.",
    ],
    "siehe_auch": ["dateien_uebertragen", "archive", "cron", "bash_skripte", "todsuenden"],
}
