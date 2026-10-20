# =============================================================================
# web/konto/formulare.py  -  Formular "Konto erstellen"
#
#   RegistrierFormular   Benutzername + Passwort (2×). Django prüft das Passwort mit den Regeln aus
#                        settings.AUTH_PASSWORD_VALIDATORS und speichert nur den Hash.
#                        Zusätzlich hier: nur einfache Zeichen im Namen, Gross/Klein zählt nicht doppelt
#                        ("Admin" und "admin" wären sonst zwei Konten - Verwechslungsgefahr).
#
# WER RUFT DAS AUF?  web/konto/views.py registrieren
# =============================================================================
import re

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

NAME_REGEL = re.compile(r"[A-Za-z0-9._-]{3,30}")
RESERVIERT = {"admin", "administrator", "root", "systemlab", "support", "verwaltung", "abo"}


class RegistrierFormular(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username",)

    def clean_username(self):
        name = (self.cleaned_data.get("username") or "").strip()
        if not NAME_REGEL.fullmatch(name):
            raise forms.ValidationError("3 bis 30 Zeichen: Buchstaben a–z, Ziffern und . _ - (keine Umlaute, keine Leerzeichen).")
        if name.lower() in RESERVIERT or User.objects.filter(username__iexact=name).exists():
            raise forms.ValidationError("Dieser Benutzername ist leider nicht verfügbar.")
        return name
