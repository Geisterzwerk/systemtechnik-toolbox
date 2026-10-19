# web/rechner/urls.py  -  /rechner/ (Liste) und /rechner/<id>/ (ein Rechner)
from django.urls import path

from rechner import views

urlpatterns = [
    path("", views.liste, name="rechner_liste"),
    path("<str:rechner_id>/", views.rechner, name="rechner"),
]
