# =============================================================================
# web/systemlab_web/urls.py  -  Welche Adresse zeigt welche Seite?
#
#   /                         Startseite                       -> wiki/views.py startseite
#   /suche/?q=…               Suche über alles                 -> wiki/views.py suche
#   /rechner/ …               Rechner                          -> rechner/urls.py
#   /konto/ …                 Anmelden, Registrieren, Konto     -> konto/urls.py
#   /abo/                     was das Abo bietet               -> konto/views.py abo
#   /uebungen/ …              Übungen (nur mit Abo)             -> ueben/urls.py
#   /<ADMIN_PFAD>             Verwaltung (Django-Admin)        -> settings.ADMIN_PFAD, nicht /admin/
#   /<bereich>/               Übersicht eines Bereichs          -> wiki/views.py bereich
#   /<bereich>/<thema>/       eine Wissensseite                 -> wiki/views.py thema
# =============================================================================
from urllib.parse import quote

from django.conf import settings
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from konto import views as konto_views                                 # -> web/konto/views.py


def _admin_login(request, extra_context=None):
    """Die Verwaltung hat KEINE eigene Anmeldung: es gilt dieselbe wie überall, mit Login-Sperre
    (web/konto/views.py anmelden). Nach dem Login geht es zurück in die Verwaltung."""
    return redirect(f"{settings.LOGIN_URL}?next={quote(request.GET.get('next') or '/' + settings.ADMIN_PFAD)}")


admin.site.login = _admin_login
admin.site.site_header = admin.site.site_title = "SystemLab Verwaltung"
admin.site.index_title = "Konten und Abo-Gruppe"

urlpatterns = [
    path(settings.ADMIN_PFAD, admin.site.urls),
    path("konto/", include("konto.urls")),
    path("abo/", konto_views.abo, name="abo"),
    path("uebungen/", include("ueben.urls")),
    path("rechner/", include("rechner.urls")),
    path("", include("wiki.urls")),
]
