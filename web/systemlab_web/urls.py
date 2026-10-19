# =============================================================================
# web/systemlab_web/urls.py  -  Welche Adresse zeigt welche Seite?
#
#   /                         Startseite                       -> wiki/views.py startseite
#   /suche/?q=…               Suche über alles                 -> wiki/views.py suche
#   /rechner/ …               Rechner                          -> rechner/urls.py
#   /<bereich>/               Übersicht eines Bereichs          -> wiki/views.py bereich
#   /<bereich>/<thema>/       eine Wissensseite                 -> wiki/views.py thema
# =============================================================================
from django.urls import include, path

urlpatterns = [
    path("rechner/", include("rechner.urls")),
    path("", include("wiki.urls")),
]
