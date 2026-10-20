# web/konto/urls.py  -  Adressen der Benutzerkonten (Erklärung: web/konto/views.py)
from django.urls import path

from konto import views

urlpatterns = [
    path("", views.uebersicht, name="konto"),
    path("anmelden/", views.anmelden, name="anmelden"),
    path("abmelden/", views.abmelden, name="abmelden"),
    path("registrieren/", views.registrieren, name="registrieren"),
    path("passwort/", views.passwort, name="passwort"),
    path("loeschen/", views.loeschen, name="konto_loeschen"),
]
