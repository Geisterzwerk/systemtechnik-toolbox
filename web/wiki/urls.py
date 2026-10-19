# web/wiki/urls.py  -  Adressen der Wissensseiten (Erklärung: web/systemlab_web/urls.py)
from django.urls import path

from wiki import views

urlpatterns = [
    path("", views.startseite, name="startseite"),
    path("suche/", views.suche, name="suche"),
    path("schaltung/<str:rechner_id>/", views.schaltung, name="schaltung"),
    path("<slug:slug>/", views.bereich, name="bereich"),
    path("<slug:slug>/<str:thema_id>/", views.thema, name="thema"),
]
