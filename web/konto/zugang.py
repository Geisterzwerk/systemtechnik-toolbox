# =============================================================================
# web/konto/zugang.py  -  WER DARF DIE ABO-FUNKTIONEN BENUTZEN?
# -----------------------------------------------------------------------------
#   hat_abo(user)   True für:  - Admin (Superuser): alles frei, ohne Kosten
#                              - Mitglieder der Gruppe "Abo" (in der Verwaltung von Hand eintragen;
#                                ab Phase 4 trägt die Zahlung das automatisch ein)
#   ABO_GRUPPE      Name der Gruppe (angelegt von migrations/0002_abo_gruppe.py)
#
# WICHTIG: Der Zugang wird IMMER hier auf dem Server geprüft - nie im Browser. Gesperrte Inhalte werden gar
# nicht erst an den Browser geschickt; die verschwommene Vorschau ist nur ein Beispiel (web/konto/templates/
# konto/schloss.html), kein echter Inhalt. So hilft es nichts, die Unschärfe im Browser wegzumachen.
#
# WER RUFT DAS AUF?  web/ueben/views.py, web/wiki/views.py (Übungen zur Seite), web/konto/views.py
# =============================================================================

ABO_GRUPPE = "Abo"


def hat_abo(user):
    if not (user and user.is_authenticated and user.is_active):
        return False
    return user.is_superuser or user.groups.filter(name=ABO_GRUPPE).exists()
