# =============================================================================
# web/konto/views.py
# -----------------------------------------------------------------------------
# BENUTZERKONTEN UND ABO-SEITE
#
#   anmelden(request)       /konto/anmelden/?next=/uebungen/     Benutzername + Passwort
#   abmelden(request)       /konto/abmelden/                     nur POST (Knopf), sonst könnte ein fremdes
#                                                                 Bild <img src=".../abmelden/"> dich abmelden
#   registrieren(request)   /konto/registrieren/                 neues Konto (abschaltbar: REGISTRIERUNG_OFFEN)
#   uebersicht(request)     /konto/                              Name, Abo-Status, Passwort ändern, löschen
#   passwort(request)       /konto/passwort/                     Passwort ändern (altes Passwort nötig)
#   loeschen(request)       /konto/loeschen/                     Konto löschen (Passwort nötig, Datenschutz)
#   abo(request)            /abo/                                was das Abo bietet (Bezahlen kommt in Phase 4)
#
# SICHERHEIT (Obsidian 03_Sicherheit):
#   - Passwörter prüft und hasht Django (settings.AUTH_PASSWORD_VALIDATORS) - im Klartext nirgends gespeichert
#   - Login-Sperre nach Fehlversuchen (web/konto/sperre.py), immer dieselbe Meldung "Benutzername oder
#     Passwort falsch" - so erfährt niemand, welche Benutzernamen es gibt
#   - Nach dem Login neue Sitzungs-ID (Django login()) - eine vorher untergeschobene ID nützt nichts
#   - Alle Formulare POST + CSRF-Schutz; Weiterleitung nach dem Login nur auf DIESE Seite (kein "?next=https://böse.ch")
#   - sensitive_post_parameters: Passwörter erscheinen nie in Fehlerberichten
#   - never_cache: Konto-Seiten landen nicht im Zwischenspeicher des Browsers
#
# WER RUFT DAS AUF?  web/konto/urls.py, web/systemlab_web/urls.py (/abo/)
# =============================================================================

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from konto import sperre                                               # -> web/konto/sperre.py
from konto.formulare import RegistrierFormular                         # -> web/konto/formulare.py
from konto.zugang import hat_abo                                       # -> web/konto/zugang.py
from wiki.rueckmeldung import ist_bot                                  # -> web/wiki/rueckmeldung.py (Bot-Falle)

MAX_EINGABE = 1000                  # längere "Passwörter" sind Unsinn oder ein Angriff
ZU_VIELE = "Zu viele Fehlversuche. Aus Sicherheitsgründen ist die Anmeldung kurz gesperrt – bitte in {} Minuten nochmals versuchen."


def sicheres_ziel(request, ziel):
    """Nur Adressen DIESER Seite als Ziel nach dem Login - sonst die Konto-Seite."""
    if ziel and ziel.startswith("/") and url_has_allowed_host_and_scheme(
            ziel, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return ziel
    return settings.LOGIN_REDIRECT_URL


@never_cache
@sensitive_post_parameters("password")
def anmelden(request):
    weiter = sicheres_ziel(request, request.POST.get("weiter") or request.GET.get("next"))
    fehler, name = None, ""
    if request.method == "POST":
        name = request.POST.get("username", "").strip()[:150]
        passwort = request.POST.get("password", "")[:MAX_EINGABE]
        k_name = sperre.schluessel("name", name)
        k_adresse = sperre.schluessel("adresse", sperre.absender(request))
        if (sperre.gesperrt(k_name, settings.SPERRE_PRO_NAME)
                or sperre.gesperrt(k_adresse, settings.SPERRE_PRO_ADRESSE)):
            fehler = ZU_VIELE.format(settings.SPERRE_MINUTEN)        # Passwort wird gar nicht erst geprüft
        else:
            user = authenticate(request, username=name, password=passwort)
            if user is None:
                sperre.merken(k_name, k_adresse)
                fehler = "Benutzername oder Passwort falsch."
            else:
                login(request, user)
                sperre.vergessen(k_name)
                return redirect(weiter)
    return render(request, "konto/anmelden.html", {"fehler": fehler, "name": name, "weiter": weiter,
                                                   "registrierung": settings.REGISTRIERUNG_OFFEN},
                  status=400 if fehler else 200)


@require_POST
def abmelden(request):
    logout(request)
    return redirect("/")


@never_cache
@sensitive_post_parameters("password1", "password2")
def registrieren(request):
    if not settings.REGISTRIERUNG_OFFEN:
        return render(request, "konto/registrieren.html", {"geschlossen": True}, status=403)
    if request.user.is_authenticated:
        return redirect("konto")
    formular = RegistrierFormular(request.POST or None)
    fehler = None
    if request.method == "POST":
        if ist_bot(request.POST):
            return redirect("/")                                     # Bots erfahren nichts
        k_adresse = sperre.schluessel("registrierung", sperre.absender(request))
        if sperre.gesperrt(k_adresse, settings.REGISTRIERUNG_PRO_STUNDE, minuten=60):
            fehler = "Von hier wurden in letzter Zeit schon viele Konten erstellt. Bitte später nochmals versuchen."
        elif formular.is_valid():
            user = formular.save()
            sperre.merken(k_adresse)
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, "Willkommen! Dein Konto ist erstellt.")
            return redirect("konto")
    return render(request, "konto/registrieren.html", {"formular": formular, "fehler": fehler},
                  status=400 if request.method == "POST" else 200)


@never_cache
@login_required
def uebersicht(request):
    return render(request, "konto/uebersicht.html", {"hat_abo": hat_abo(request.user)})


@never_cache
@login_required
@sensitive_post_parameters("old_password", "new_password1", "new_password2")
def passwort(request):
    formular = PasswordChangeForm(request.user, request.POST or None)
    if request.method == "POST" and formular.is_valid():
        user = formular.save()
        update_session_auth_hash(request, user)          # angemeldet bleiben; andere Sitzungen werden ungültig
        messages.success(request, "Dein Passwort ist geändert.")
        return redirect("konto")
    return render(request, "konto/passwort.html", {"formular": formular},
                  status=400 if request.method == "POST" else 200)


@never_cache
@login_required
@sensitive_post_parameters("password")
def loeschen(request):
    fehler = None
    if request.user.is_superuser:
        fehler = "Das Admin-Konto kann hier nicht gelöscht werden (sonst kommt niemand mehr in die Verwaltung)."
    elif request.method == "POST":
        k_name = sperre.schluessel("name", request.user.get_username())
        if sperre.gesperrt(k_name, settings.SPERRE_PRO_NAME):
            fehler = ZU_VIELE.format(settings.SPERRE_MINUTEN)
        elif not request.user.check_password(request.POST.get("password", "")[:MAX_EINGABE]):
            sperre.merken(k_name)
            fehler = "Das Passwort stimmt nicht."
        else:
            user = request.user
            logout(request)
            user.delete()                                    # Konto weg - Django löscht auch Gruppen-Einträge
            return render(request, "konto/geloescht.html")
    return render(request, "konto/loeschen.html", {"fehler": fehler},
                  status=400 if fehler and request.method == "POST" else 200)


def abo(request):
    return render(request, "konto/abo.html", {"hat_abo": hat_abo(request.user)})
