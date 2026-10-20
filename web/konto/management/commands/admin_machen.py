# =============================================================================
# web/konto/management/commands/admin_machen.py
# -----------------------------------------------------------------------------
# Ein BESTEHENDES Konto zum Admin machen (alles frei + Verwaltung), z.B. wenn es über
# "Konto erstellen" statt mit "createsuperuser" angelegt wurde. Das Passwort bleibt, wie es ist.
#
#   py manage.py admin_machen Jorick            -> Admin
#   py manage.py admin_machen Jorick --zurueck  -> wieder normales Konto
#
# Nur im Terminal auf dem Server/PC möglich - nicht über die Webseite (Sicherheit).
# WER RUFT DAS AUF?  du, im Ordner web/
# =============================================================================
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Bestehendes Konto zum Admin machen (alles frei, Verwaltung)"

    def add_arguments(self, parser):
        parser.add_argument("benutzername")
        parser.add_argument("--zurueck", action="store_true", help="Admin-Rechte wieder wegnehmen")

    def handle(self, benutzername, zurueck, **optionen):
        try:
            user = User.objects.get(username=benutzername)
        except User.DoesNotExist:
            raise CommandError(f"Kein Konto mit dem Namen „{benutzername}“ (Gross-/Kleinschreibung beachten).")
        user.is_superuser = user.is_staff = not zurueck
        user.save(update_fields=["is_superuser", "is_staff"])
        if zurueck:
            self.stdout.write(f"„{benutzername}“ ist wieder ein normales Konto.")
        else:
            self.stdout.write(self.style.SUCCESS(f"„{benutzername}“ ist jetzt Admin: alles frei, Verwaltung unter /verwaltung/."))
