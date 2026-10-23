# =============================================================================
# gui/hilfe.py
# -----------------------------------------------------------------------------
# BEDIENUNGSANLEITUNG (Knopf "📖 So funktioniert SystemLab" auf der Startseite).
# Öffnet ein eigenes Fenster mit allen Bedienungs-Themen. Der Text steht unten in ABSCHNITTE
# (Format wie die Wissensseiten: ## Überschrift, - Punkt, **fett**, `code`).
# Jeder Rechner hat zusätzlich seinen eigenen ❓-Knopf (bauteile/rechner/kern.py formel_hilfe).
#
# WER RUFT DAS AUF?  gui/startseite_gui.py
# =============================================================================

import customtkinter as ctk

import config                                                          # -> config.py
from core.layout import Karte, ScrollSeite, Stapel, seiten_kopf        # -> core/layout.py
from core.widgets import FormatText                                    # -> core/widgets.py

ABSCHNITTE = [
    ("🧭 Navigation", """
- **Startseite**: Suche, Favoriten, zuletzt geöffnete Seiten, Schaltung des Tages und alle Bereiche
- **Tabs oben** (Bauteile, Schaltungen, …, Rechner): ein Klick wechselt den Bereich
- **☰** blendet die Seitenliste links aus und ein – mehr Platz für die Seite
- **🏠** führt zurück zur Startseite
- **Kategorie-Icon** (z.B. 💡 bei Dioden): Übersicht dieser Kategorie. Dort zeigt der Knopf das Icon des Bereichs → Übersicht des ganzen Bereichs
- **◀** eine Seite zurück
- **Seitenliste breiter**: den schmalen Streifen rechts neben der Liste mit der Maus ziehen (Doppelklick = Standardbreite). Lange Namen zeigen beim Darüberfahren den ganzen Titel
"""),
    ("🔍 Suchen und merken", """
- **Ctrl + K** – von überall in die grosse Suche auf der Startseite (sucht in allen Bereichen und Rechnern)
- **Ctrl + F** – Suche im Bereich Programmieren bzw. Server / Linux
- In jedem Bereich gibt es oben ein eigenes Suchfeld. **Enter** öffnet den ersten Treffer, **Esc** leert die Suche
- Tippfehler sind kein Problem – die Suche findet auch ähnliche Wörter
- **☆ / ⭐** oben rechts: Seite oder Rechner als **Favorit** merken. Favoriten und **Zuletzt geöffnet** stehen auf der Startseite
"""),
    ("🧮 Rechner", """
- Jede Wissensseite mit Rechnern hat oben den Umschalter **📖 Wissen | 🧮 Rechner**. Alle Rechner gibt es zusätzlich im Tab **Rechner**
- Nur die Felder ausfüllen, die du kennst. **Was genau rein muss**, zeigt der **❓-Knopf** oben rechts in jedem Rechner
- **Einheit** rechts neben dem Feld wählen – oder direkt mit Einheit tippen: `4k7` = 4.7 kΩ, `2.2M`, `470m`, `100n`, `4R7` = 4.7 Ω. Die getippte Einheit gilt
- Komma oder Punkt als Dezimalzeichen – beides geht
- **Enter** oder **Berechnen** rechnet, **↺ Zurücksetzen** leert alle Felder und stellt die Einheiten zurück
- Das Ergebnis steht als Tabelle darunter: das **Hauptergebnis** gross und farbig, der Rechenweg klein daneben, Hinweise und ⚠ Warnungen darunter
"""),
    ("🎛️ Regler und Einheiten", """
- **Regler ziehen** oder rechts eine **Zahl eintippen** (Enter oder Feld verlassen übernimmt)
- **Einheit wechseln**: Der Regler gilt dann in der neuen Einheit. Wählst du eine kleinere Einheit, reicht er bis zur nächsten – z.B. von V auf **mV: 0 … 1000 mV**
- Passt der Wert nicht in den neuen Bereich, bleibt die **Zahl** stehen (230 V → 230 mV)
- Ungültige Eingaben werden **rot** markiert und erklärt – der alte Wert bleibt erhalten
"""),
    ("🔌 Schaltungen und interaktive Grafiken", """
- Oben: **Varianten** (z.B. Laden / Entladen) und **Schalter** der Schaltung
- **Strom-/Spannungspfeile** (rot = Strom, blau = Spannung) lassen sich oben aus- und einblenden
- Unter den Reglern: eigene **Knöpfe** der Grafik, z.B. **1τ … 5τ** bei Lade- und Entladekurven
- **↺ Zurücksetzen** stellt alles wie beim Öffnen ein
- **KV-Diagramm**: Felder direkt anklicken (0 → 1 → X → 0) – oder Nummern bzw. einen Ausdruck eintippen
- Logische Ausdrücke: Die **Tastenleiste** unter dem Feld fügt A B C D ¬ · + ⊕ ( ) an der Cursor-Stelle ein
- Bei einer **ungültigen Eingabe** bleibt die Grafik stehen; das Feld wird rot und die Meldung steht darunter
- Der Text **„Was zeigt …?“** unter jeder Grafik erklärt, was physikalisch passiert
"""),
    ("🖥️ Anzeige", """
- **Dark Mode** ein/aus: Schalter unten auf der Startseite (wird gemerkt)
- **Zoom**: **Ctrl + Mausrad** oder **Ctrl + Plus / Minus**, **Ctrl + 0** = 100 %. Die aktuelle Grösse steht kurz oben rechts
- Das Fenster kann beliebig gross gezogen werden – Seiten und Grafiken passen sich an
"""),
]


def oeffnen(app):
    """Hilfe-Fenster öffnen (oder das schon offene nach vorne holen)."""
    fenster = getattr(app, "hilfe_fenster", None)
    if fenster is not None and fenster.winfo_exists():
        fenster.deiconify()
        fenster.lift()
        fenster.focus_force()
        return fenster
    fenster = ctk.CTkToplevel(app)
    fenster.title(f"📖 {config.APP_NAME} – Bedienung")
    fenster.geometry("820x760")
    fenster.minsize(480, 400)
    fenster.transient(app)                         # bleibt über dem Hauptfenster
    fenster.configure(fg_color=config.FARBEN["hintergrund"])
    fenster.grid_rowconfigure(0, weight=1)
    fenster.grid_columnconfigure(0, weight=1)
    scroll = ScrollSeite(fenster, max_breite=900)
    scroll.grid(row=0, column=0, sticky="nsew")
    body = scroll.body
    s = Stapel(body)
    seiten_kopf(s, f"📖 So funktioniert {config.APP_NAME}", f"Version {config.APP_VERSION}  ·  Bedienung auf einen Blick")
    for titel, text in ABSCHNITTE:
        karte = s.add(Karte(body, titel=titel))
        feld = FormatText(karte.body)
        feld.setze_text(text)
        feld.grid(row=0, column=0, sticky="ew")
    # customtkinter setzt bei neuen Fenstern kurz danach sein eigenes Icon -> unseres danach setzen
    fenster.after(250, lambda: _icon(fenster))
    fenster.after(100, fenster.lift)
    app.hilfe_fenster = fenster
    return fenster


def _icon(fenster):
    try:
        if fenster.winfo_exists():
            fenster.iconbitmap(config.APP_ICON)
    except Exception:
        pass
