# web/konto/migrations/0002_abo_gruppe.py  -  legt die Gruppe "Abo" an (web/konto/zugang.py ABO_GRUPPE).
# Wer in dieser Gruppe ist, darf die Abo-Funktionen nutzen. Bis zur Zahlung (Phase 4) trägst du Leute
# in der Verwaltung von Hand ein: Benutzer öffnen -> Gruppen -> "Abo".
from django.db import migrations

ABO_GRUPPE = "Abo"                     # gleich wie konto/zugang.py (Migrationen sollen nichts importieren, was sich ändert)


def anlegen(apps, schema_editor):
    apps.get_model("auth", "Group").objects.get_or_create(name=ABO_GRUPPE)


def entfernen(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name=ABO_GRUPPE).delete()


class Migration(migrations.Migration):
    dependencies = [("konto", "0001_initial"), ("auth", "0012_alter_user_first_name_max_length")]
    operations = [migrations.RunPython(anlegen, entfernen)]
