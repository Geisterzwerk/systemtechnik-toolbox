# =============================================================================
# web/konto/models.py  -  Tabellen in der Datenbank (nur was für die Sicherheit nötig ist)
#
#   Fehlversuch   ein fehlgeschlagener Login (oder eine Registrierung) -> Login-Sperre (web/konto/sperre.py)
#                 gespeichert wird NUR ein Hash (Prüfsumme) von Benutzername bzw. Absender und die Zeit,
#                 nie der Name, die IP-Adresse oder gar das Passwort. Alte Einträge löscht sperre.py.
#
# Benutzer und Gruppen ("Abo") bringt Django selbst mit (django.contrib.auth).
# WER RUFT DAS AUF?  web/konto/sperre.py
# =============================================================================
from django.db import models


class Fehlversuch(models.Model):
    schluessel = models.CharField(max_length=80, db_index=True)    # z.B. "name:3f9a…" oder "adresse:7b1c…"
    zeit = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.schluessel[:20]}… {self.zeit:%Y-%m-%d %H:%M}"
