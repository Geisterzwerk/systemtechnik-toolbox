# Seite "Watchdog"  -> Vorlage: schaltungen/inhalte/_vorlage.py

THEMA = {
    "titel": "Watchdog (Überwachung eines Mikrocontrollers)",
    "reihenfolge": 40,
    "kurz": "Ein Baustein, der den µC neu startet, wenn das Programm hängt – mit Timeout-Toleranz, Bootzeit und Fenster.",
    "stichworte": ["Watchdog", "Watchdog-Timer", "WDT", "Fenster-Watchdog", "Window Watchdog", "Reset",
                   "Supervisor", "Spannungsüberwachung", "WDI", "Timeout", "Hänger", "Absturz", "TPS3828",
                   "MAX6369", "Funktionale Sicherheit"],

    "grafiken": ["schaltung_watchdog"],

    "erklaerung": """
## Stell dir vor …
Ein **Totmannschalter** im Zug: Der Lokführer muss regelmässig eine Taste drücken. Bleibt das Drücken aus, weil er eingeschlafen ist oder ein Problem hat, bremst der Zug automatisch. Der Watchdog ist der Totmannschalter für Software: Bleibt das regelmässige „Lebenszeichen“ aus, wird der Mikrocontroller neu gestartet.
## Funktion
Ein Watchdog ist ein Zeitglied, das ständig „zurückgesetzt“ werden muss:
- Das Programm sendet im normalen Ablauf regelmässig einen **Trigger** (Puls an WDI, oder bei internen Watchdogs ein Register-Schreibzugriff).
- Jeder Trigger startet die Zeitmessung neu.
- Bleibt der Trigger länger als der **Timeout** aus (Endlosschleife, Absturz, Störung), zieht der Watchdog **RESET** – der µC startet neu.

**Fenster-Watchdog**: Ein Trigger ist nur in einem Zeitfenster erlaubt – zu früh ist ebenfalls ein Fehler. So fällt auch ein Programm auf, das in einer kurzen Schleife hängt, die ständig triggert.

Externe Watchdog-ICs enthalten oft zusätzlich eine **Spannungsüberwachung** (Reset bei Unterspannung).

## Dimensionierung
1. Timeout und **Toleranz** aus dem Datenblatt (oft ±20 … 50 %!). Gerechnet wird mit dem **kürzesten** Timeout.
2. Trigger-Abstand im Programm deutlich darunter (Faustregel: ≤ halber kürzester Timeout), auch für die längsten Programmteile (Flash schreiben, Netzwerk).
3. **Bootzeit**: Zeit vom Reset bis zum ersten Trigger muss unter dem Timeout liegen – sonst Reset-Schleife (manche ICs haben dafür einen längeren ersten Timeout).
4. Trigger nur an EINER Stelle in der Hauptschleife – nicht in Interrupts (die laufen auch weiter, wenn die Hauptschleife hängt).
5. Fenster-Watchdog: frühester Trigger < Trigger-Abstand < kürzester Timeout.
6. Nach einem Watchdog-Reset die Ursache speichern/melden (Reset-Grund-Register).

## Betriebszustände
- **Normal**: Zähler steigt zwischen den Triggern und fällt bei jedem Trigger auf null.
- **Hänger**: kein Trigger → Zähler erreicht den Timeout → Reset-Impuls.
- **Neustart**: Bootzeit, dann wieder regelmässige Trigger.
- **Falsch dimensioniert**: Resets auch im Normalbetrieb (Trigger zu selten) oder endlose Reset-Schleife (Bootzeit zu lang).

## Messpunkte
- WDI und RESET gleichzeitig mit dem Oszilloskop (Single-Shot auf RESET triggern).
- Test: Im Programm absichtlich eine Endlosschleife auslösen → Reset muss nach dem Timeout kommen.
- Trigger-Abstand unter Volllast messen (längster Programmdurchlauf).

## Grenzfälle
- Watchdog im Debugger: beim Anhalten am Breakpoint gibt es Resets → im Debug-Modus deaktivieren (bei internen WDTs meist einstellbar).
- Trigger im Timer-Interrupt: Hauptprogramm kann hängen, der Watchdog merkt es nicht.
- Toleranz ignoriert: Ein Teil der Geräte resettet sporadisch, ein anderer nie.
## 🔬 Genauer hingeschaut
- **Wo man triggert, ist entscheidend:** Wird der Watchdog in einem Timer-Interrupt zurückgesetzt, läuft er weiter, auch wenn das Hauptprogramm hängt – dann ist er nutzlos. Triggern sollte man an einer Stelle, die nur erreicht wird, wenn alle wichtigen Aufgaben wirklich laufen.
- **Ursache merken:** Viele Mikrocontroller speichern, warum der letzte Neustart passiert ist (Einschalten, Reset-Taste, Watchdog …). Wer das beim Start ausliest und protokolliert, findet sporadische Fehler viel schneller.
- **Unabhängiger Takt:** Ein guter Watchdog läuft mit einem eigenen Oszillator. Fällt der Haupttakt aus, merkt er es trotzdem.
## 💡 Wusstest du?
- 1997 setzte der Watchdog der Mars-Sonde **Pathfinder** den Bordrechner immer wieder zurück. Die Ursache war ein Software-Fehler (Prioritätsinversion), den die Ingenieure von der Erde aus per Update beheben konnten – der Watchdog hatte die Mission bis dahin am Leben gehalten.
""",

    "tipps": [
        "Im Feld lieber einen Neustart als ein eingefrorenes Gerät – der Watchdog ist die letzte Sicherheitsleine.",
        "Mit dem Simulator ausprobieren: Trigger-Abstand knapp unter den Timeout schieben und die Toleranz erhöhen.",
    ],
    "fehler": [
        "Watchdog im Interrupt getriggert – das Hauptprogramm darf hängen, ohne dass es auffällt.",
        "Mit dem typischen statt dem kürzesten Timeout gerechnet – sporadische Resets bei manchen Geräten.",
        "Bootzeit länger als der Timeout – das Gerät hängt in einer Reset-Schleife.",
    ],
    "siehe_auch": ["ne555_timer", "rechteck_dreieck_generator"],
    "rechner": ["watchdog"],
}
