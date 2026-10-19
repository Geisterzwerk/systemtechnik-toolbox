# =============================================================================
# web/wiki/management/commands/rueckmeldungen.py
# -----------------------------------------------------------------------------
# Rückmeldungen ("Fehler melden") im Terminal anzeigen, neueste zuerst:
#     python manage.py rueckmeldungen            alle
#     python manage.py rueckmeldungen --anzahl 5 nur die letzten 5
#
# Gespeichert in web/daten/rueckmeldungen.jsonl (nicht im Repo) -> web/wiki/rueckmeldung.py
# WER RUFT DAS AUF?  du im Terminal (Ordner web/)
# =============================================================================
from django.core.management.base import BaseCommand

from wiki import rueckmeldung                                          # -> web/wiki/rueckmeldung.py


class Command(BaseCommand):
    help = "Rückmeldungen der Testpersonen anzeigen (neueste zuerst)"

    def add_arguments(self, parser):
        parser.add_argument("--anzahl", type=int, default=0, help="nur die letzten N anzeigen")

    def handle(self, *args, **optionen):
        meldungen = rueckmeldung.alle()
        if optionen["anzahl"]:
            meldungen = meldungen[:optionen["anzahl"]]
        if not meldungen:
            self.stdout.write("Noch keine Rückmeldungen.")
            return
        for m in meldungen:
            self.stdout.write(self.style.MIGRATE_HEADING(f"{m.get('zeit', '?')}  ·  {m.get('art', '?')}"))
            if m.get("seite"):
                self.stdout.write(f"  Seite:   {m['seite']}")
            if m.get("kontakt"):
                self.stdout.write(f"  Kontakt: {m['kontakt']}")
            for zeile in str(m.get("text", "")).splitlines() or [""]:
                self.stdout.write(f"  {zeile}")
            self.stdout.write("")
        self.stdout.write(f"{len(meldungen)} Rückmeldung(en)")
