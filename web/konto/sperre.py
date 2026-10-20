# =============================================================================
# web/konto/sperre.py  -  LOGIN-SPERRE gegen Passwort-Ausprobieren (Brute Force)
# -----------------------------------------------------------------------------
# Wer zu oft ein falsches Passwort eingibt, wird für settings.SPERRE_MINUTEN gesperrt - und zwar
#   - pro Benutzername  (SPERRE_PRO_NAME):    niemand kann bei EINEM Konto tausende Passwörter probieren
#   - pro Absender      (SPERRE_PRO_ADRESSE): niemand kann mit EINEM Rechner viele Konten durchprobieren
# Während der Sperre wird das Passwort gar nicht mehr geprüft (auch ein richtiges nicht).
#
#   schluessel(art, wert)          "name:<hash>" - gespeichert wird nur ein Hash, nie Name oder IP
#   gesperrt(schluessel, maximum)  True, wenn in der Zeitspanne schon 'maximum' Fehlversuche waren
#   merken(*schluessel)            einen Fehlversuch speichern
#   vergessen(schluessel)          nach erfolgreichem Login: Fehlversuche dieses Namens löschen
#   absender(request)              Absender-Adresse (REMOTE_ADDR)
#
# Gespeichert in der Datenbank (web/konto/models.py Fehlversuch) - so gilt die Sperre auch, wenn der
# Server neu startet oder online mehrere Prozesse laufen.
# WER RUFT DAS AUF?  web/konto/views.py (anmelden, registrieren, loeschen)
# =============================================================================

import hashlib
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from konto.models import Fehlversuch                                   # -> web/konto/models.py


def schluessel(art, wert):
    """Hash mit dem geheimen Schlüssel der Seite - aus der Datenbank kann man Namen/IPs nicht zurückrechnen."""
    roh = f"{settings.SECRET_KEY}|{art}|{str(wert).strip().lower()}"
    return f"{art}:{hashlib.sha256(roh.encode()).hexdigest()[:40]}"


def _grenze(minuten):
    return timezone.now() - timedelta(minutes=minuten)


def gesperrt(s, maximum, minuten=None):
    minuten = minuten or settings.SPERRE_MINUTEN
    Fehlversuch.objects.filter(zeit__lt=_grenze(max(minuten, 60))).delete()       # Altes aufräumen
    return Fehlversuch.objects.filter(schluessel=s, zeit__gte=_grenze(minuten)).count() >= maximum


def merken(*alle):
    Fehlversuch.objects.bulk_create([Fehlversuch(schluessel=s) for s in alle])


def vergessen(s):
    Fehlversuch.objects.filter(schluessel=s).delete()


def absender(request):
    """Absender-Adresse. ACHTUNG online hinter einem Proxy (z.B. nginx): dort steht die echte Adresse in
    einem eigenen Header, den NUR der eigene Proxy setzen darf -> beim Online-Gang anpassen (03_Sicherheit)."""
    return request.META.get("REMOTE_ADDR", "")
