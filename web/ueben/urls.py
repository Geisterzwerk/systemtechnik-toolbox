# web/ueben/urls.py  -  Adressen der Übungen (Erklärung: web/ueben/views.py)
from django.urls import path

from ueben import views

urlpatterns = [
    path("", views.liste, name="uebungen"),
    path("blatt/", views.blatt, name="uebungsblatt"),
    path("<str:art_id>/", views.aufgabe, name="aufgabe"),
]
