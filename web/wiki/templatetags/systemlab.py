# =============================================================================
# web/wiki/templatetags/systemlab.py  -  eigene Filter für die Templates
#
#   {{ text|format }}    ganzer Text mit ## / - / **fett** / `code`  -> HTML   (web/wiki/textformat.py)
#   {{ text|inline }}    nur **fett** und `code` (z.B. Tabellenzellen, Tipps)
#   {{ liste|zeilen }}   Ergebniszeilen untereinander (für <pre>)
#
# format und inline escapen zuerst alles (sicher), darum dürfen sie als "safe" markiert werden.
# WER RUFT DAS AUF?  web/templates/**/*.html  ({% load systemlab %})
# =============================================================================
from django import template
from django.utils.safestring import mark_safe

from wiki import textformat                                            # -> web/wiki/textformat.py

register = template.Library()


@register.filter(name="format")
def format_filter(text):
    return mark_safe(textformat.als_html(text or ""))


@register.filter(name="zeilen")
def zeilen_filter(liste):
    """["a", "b"] -> zwei Zeilen (für <pre>; wird von Django normal escaped)"""
    return "\n".join(str(z) for z in liste or [])


@register.filter(name="inline")
def inline_filter(text):
    return mark_safe(textformat.inline(text or ""))
