# SystemLab

> Modulare Lern-, Nachschlage- und Berechnungssoftware für Elektronik, Elektrotechnik, Messtechnik, Digitaltechnik, Schaltungen und Programmierung.

SystemLab entsteht als langfristig erweiterbare Desktop-Anwendung für Schule, Lehrwerkstatt, Labor und eigene Entwicklungsprojekte. Die Anwendung verbindet verständliche Theorie mit Rechnern, interaktiven Grafiken, Schaltungsbeispielen, Datenblattwissen, Praxistipps und typischen Fehlerbildern.

**Created by Jorick Gamba**

Der bisherige Projektname `SystemtechnikToolbox` wird schrittweise durch **SystemLab** ersetzt.

---

# Wichtiger Hinweis zum aktuellen Entwicklungsstand

SystemLab befindet sich in aktiver Entwicklung. Der aktuelle Stand wurde bereits praktisch getestet, die fachliche Richtigkeit aller Inhalte und Berechnungen wurde jedoch noch nicht vollständig und systematisch geprüft.

Die in diesem Dokument aufgeführten Punkte sind deshalb in drei Gruppen zu unterscheiden:

1. **Bereits vorhanden:** Funktion ist grundsätzlich eingebaut.
2. **Verbesserung notwendig:** Funktion ist vorhanden, Darstellung, Bedienung oder Erklärung muss aber überarbeitet werden.
3. **Noch umzusetzen:** Thema oder Funktion ist geplant, aber noch nicht vollständig vorhanden.

## Arbeitsregel für diese Review-Liste

Die folgenden Punkte sind zunächst als ausführliches Pflichtenheft und Entwickler-Prompt zu verstehen.

- Noch keine Punkte automatisch umsetzen.
- Zuerst alle Beobachtungen sammeln.
- Danach fachlich prüfen.
- Anschliessend nach Priorität ordnen.
- Änderungen in kleinen, nachvollziehbaren Schritten umsetzen.
- Nach jeder Etappe testen und separat committen.
- Vor einer Änderung prüfen, ob dieselbe Komponente an mehreren Stellen verwendet wird.
- Bestehende funktionierende Rechner nicht unnötig duplizieren.

---

# Projektziele

SystemLab soll:

- technische Grundlagen verständlich erklären,
- Formeln im passenden technischen Zusammenhang zeigen,
- wiederkehrende Berechnungen vereinfachen,
- Schaltungen interaktiv verständlich machen,
- typische Auslegungs- und Messfehler früh erkennen,
- Theorie, Berechnung, Simulation und Praxis verbinden,
- modular und später einfach erweiterbar bleiben,
- ohne feste lokale Benutzerpfade funktionieren,
- über GitHub verteilt und aktualisiert werden,
- später als Windows-Anwendung oder Installer veröffentlicht werden können.

---

# Aktueller Stand (Oktober 2026)

| Bereich | Stand | Inhalt |
|---|---|---|
| **Startseite** | ✅ vorhanden | Kacheln zu allen Bereichen, Dark/Light Mode |
| **Bauteile** | ✅ vorhanden | Widerstand, Kondensator, Spule, Transformator, Diode, Z-Diode, LED, Bipolartransistor, MOSFET, Relais – mit Rechnern und interaktiven Grafiken |
| **Messtechnik** | ✅ vorhanden | Messunsicherheit, Signalkenngrössen, Multimeter, Oszilloskop, Temperatur, Brücke/DMS, Durchfluss, AD-Wandler |
| **Programmieren** | ✅ vorhanden | 31 Themen, Beispiele in Python, C++ und C# im Vergleich |
| **Server / Linux** | ✅ vorhanden | 35 Seiten Ubuntu Server: Konsole, Dateien, Rechte, Dienste, Netzwerk, Sicherheit, Praxis; Spickzettel mit 60 Befehlen, Kopier-Knopf pro Befehl, Markierung gefährlicher Befehle |
| **Schaltungen** | 🟡 im Aufbau | Widerstandsnetzwerke (5 Seiten) Dioden & Schutz (7 Seiten) und Transistor & MOSFET (6 Seiten: NPN/PNP-Schalter, MOSFET-Schalter, LED/Relais/Motor ansteuern, Emitterschaltung, Emitterfolger, Konstantstromquelle) – mit interaktiven Schaltplänen; RC/RL, OPV, Netzteile folgen |
| **Rechner** | ✅ vorhanden | alle 65 Rechner an einem Ort: Suche, nach Thema oder A–Z, Link zur Wissensseite (`gui/rechner_gui.py`, Metadaten in `bauteile/rechner/rechner_info.py`) |

Alle Bauteil-, Messtechnik-, Programmier- und Server-Seiten sind reine Daten (`THEMA = {...}`) und werden von einer gemeinsamen Engine dargestellt. Neue Dateien erscheinen automatisch in Navigation und Suche.

---

# Geplante Hauptbereiche

- **Startseite:** Einstieg in alle Bereiche
- **Bauteile:** Wissen, Kennwerte, Rechner und interaktive Darstellungen
- **Schaltungen:** Grundschaltungen, Dimensionierung und Simulation
- **Messtechnik:** Messgeräte, Messunsicherheit, Sensoren und AD-Wandlung
- **Digitaltechnik:** Logik, Zahlensysteme und digitale Schaltungen
- **Programmieren:** Python, C++ und C# im Vergleich, technische Programmierbeispiele
- **Server / Linux:** Ubuntu Server über die Konsole, später Proxmox VE
- **Rechner:** zentraler Zugriff auf alle Rechner der Anwendung

---

# Einheitlicher Aufbau der Wissensseiten

Jedes Thema soll möglichst dieselbe Struktur verwenden:

1. Kurzbeschreibung
2. Steckbrief
3. Funktionsweise in eigenen Worten
4. Schaltzeichen oder responsive Darstellung
5. wichtige Formeln
6. typische Werte und Datenblatt-Kennwerte
7. Anwendungen
8. Auswahlhilfe
9. Praxistipps
10. typische Fehler
11. passende Rechner
12. interaktive Grafik, sofern sinnvoll
13. Verweise auf verwandte Themen
14. Literaturhinweise ohne übernommene Originalinhalte

---

# Review und Verbesserungen des bestehenden Bauteilbereichs

Dieser Abschnitt enthält die beim praktischen Test aufgefallenen Punkte. Die Beschreibungen sind bewusst ausführlich formuliert, damit sie später direkt als Arbeitsauftrag für eine Überarbeitung verwendet werden können.

## Übergreifende Anforderungen für alle bestehenden Seiten

### Status

- Mehrere Seiten, Rechner und interaktive Darstellungen funktionieren bereits.
- Die Darstellung ist an verschiedenen Stellen noch nicht ausreichend responsiv.
- Beschriftungen können Schaltzeichen, Kurven oder andere Texte überlagern.
- Einige Regler erlauben nur eine Bedienung über Slider.
- Die fachliche Richtigkeit muss noch systematisch kontrolliert werden.
  → Rechner: erledigt mit `python pruefen_rechner.py` (Schritt 5). Wissenstexte sind noch nicht systematisch geprüft.

### Verbesserungsauftrag

- Alle Seiten bei unterschiedlichen Fensterbreiten und Skalierungen prüfen.
- Mindestens kleine, mittlere und grosse Fensterbreite testen.
- Schrift darf nie in Schaltzeichen, Kurven oder andere Beschriftungen hineinragen.
- Schaltzeichen benötigen ausreichend Abstand zueinander.
- Texte müssen automatisch umbrechen oder passend positioniert werden.
- Achsenbeschriftungen und Einheiten dürfen nicht abgeschnitten werden.
- Interaktive Grafiken müssen sowohl im Hell- als auch im Dunkelmodus lesbar bleiben.
- Bei jedem Slider zusätzlich ein direkt editierbares Zahlenfeld anbieten.
- Slider und Zahlenfeld müssen synchronisiert sein.
- Eingaben müssen Einheiten berücksichtigen und ungültige Werte verständlich melden.
- Wo sinnvoll, sollen Werte direkt in der Darstellung sichtbar sein und nicht nur unterhalb der Grafik.
- Jede interaktive Darstellung benötigt eine kurze Erklärung, welche physikalische Aussage die Grafik vermittelt.
- Fachliche Formeln und Grenzfälle mit bekannten Beispielwerten testen.

---

## Widerstand

### Aktueller Eindruck

Der Widerstandsbereich wirkt im bisherigen Kurztest insgesamt übersichtlich und funktional.

### Noch zu prüfen

- Rechner fachlich systematisch verifizieren.
- Einheiten und Grenzfälle kontrollieren.
- Darstellung bei schmalem Fenster testen.
- prüfen, ob Widerstandsfarbcode, Normreihen, Leistung und Temperaturverhalten vollständig miteinander verknüpft sind.

### Beibehalten

- klare Grundstruktur
- praktische Rechner
- verständliche Aufteilung der Inhalte

---

## Kondensator

### 1. Schaltzeichen des gepolten Kondensators

#### Festgestelltes Problem

Das Schaltzeichen des gepolten Kondensators beziehungsweise Elkos ist optisch nicht sauber. Der horizontale Anschlussstrich wirkt zu lang und die Proportionen zwischen Anschlusslinien, Platten und Pluszeichen sind unausgewogen.

#### Verbesserungsauftrag

- Schaltzeichen geometrisch neu ausrichten.
- Anschlusslinien links und rechts gleichmässig dimensionieren.
- Die beiden Kondensatorplatten klar voneinander trennen.
- Das Pluszeichen oberhalb der positiven Platte positionieren, ohne die Platte oder Anschlusslinie zu berühren.
- Beschriftung `gepolt (Elko): + beachten!` mit ausreichend Abstand unter dem Symbol platzieren.
- Darstellung bei verschiedenen Fenstergrössen testen.
- Wenn mehrere Kondensatortypen nebeneinander dargestellt werden, identische Symbolgrösse und einheitliche Grundlinie verwenden.

### 2. Lade- und Entladekurve

#### Aktueller Stand

- Eine interaktive Kurve ist vorhanden.
- Zeitkonstante und Prozentwerte werden dargestellt.
- Lade- und Entladebetrieb können grundsätzlich ausgewählt werden.

#### Festgestelltes Problem

Die Darstellung zeigt hauptsächlich die Kondensatorspannung. Für das Verständnis der physikalischen Vorgänge fehlt das Stromverhalten. Ausserdem ist der Zusammenhang zwischen Schaltvorgang, Spannung und Strom noch nicht deutlich genug.

#### Verbesserungsauftrag

Die Darstellung soll zu einer kombinierten Lernansicht ausgebaut werden:

- Schaltzustand beziehungsweise Eingangsspannung anzeigen.
- Kondensatorspannung `U_C(t)` darstellen.
- Kondensatorstrom `I_C(t)` gleichzeitig darstellen.
- Lade- und Entladevorgang klar voneinander unterscheiden.
- Beim Laden zeigen:
  - `U_C` beginnt beim Startwert und steigt exponentiell gegen die Versorgungsspannung.
  - `I_C` ist zu Beginn maximal und fällt gegen null.
- Beim Entladen zeigen:
  - `U_C` fällt exponentiell gegen null oder gegen eine gewählte Endspannung.
  - `I_C` hat gegenüber dem Ladevorgang die umgekehrte Richtung beziehungsweise ein negatives Vorzeichen, abhängig von der verwendeten Vorzeichenkonvention.
- Vorzeichenkonvention direkt in der Grafik erklären.
- Startspannung `U_C0`, Versorgungsspannung, Widerstand und Kapazität einstellbar machen.
- Neben `1τ` bis `5τ` immer die tatsächlich berechnete Zeit anzeigen.
- Klar erklären, dass `5τ` nicht automatisch fünf Sekunden bedeutet.
- Prozentwerte für Lade- und Entladevorgang korrekt beschriften.
- Werte am aktuell gewählten Zeitpunkt anzeigen:
  - Zeit
  - Kondensatorspannung
  - Kondensatorstrom
  - Ladezustand in Prozent
- Optional zwei übereinanderliegende Diagramme verwenden, damit Spannung und Strom unterschiedliche Einheiten und Achsen erhalten.
- Keine doppelte y-Achse verwenden, wenn sie die Darstellung unnötig schwer verständlich macht.

#### Gewünschtes Lernziel

Die Darstellung soll nicht nur zeigen, wie eine mathematische Exponentialkurve aussieht. Die Darstellung soll erklären, was unmittelbar nach dem Schalten passiert und warum der Strom mit zunehmender Kondensatorspannung kleiner wird.

---

## Spule

### 1. Schaltzeichen

#### Festgestelltes Problem

Die mehreren Schaltzeichen stehen zu nahe beieinander. Die Beschriftungen `Spule (EN 60617)`, `mit Eisen-/Ferritkern` und `alt (DIN)` wirken teilweise wie eine zusammengehörende Grafik und besitzen zu wenig Abstand.

#### Verbesserungsauftrag

- Jedes Schaltzeichen in einen eigenen klar begrenzten Bereich setzen.
- Einheitliche Symbolgrösse und Grundlinie verwenden.
- Zwischen den Varianten ausreichend horizontalen Abstand einplanen.
- Beschriftung mittig unter dem jeweiligen Symbol platzieren.
- Kernlinien beim Symbol mit Eisen- beziehungsweise Ferritkern korrekt und mit genügend Abstand zur Wicklung darstellen.
- Alte DIN-Darstellung visuell eindeutig als historische beziehungsweise alternative Darstellung kennzeichnen.
- Responsive Umbruchlogik vorsehen. Bei zu wenig Breite sollen die Schaltzeichen untereinander statt überlappend dargestellt werden.

### 2. Ein- und Ausschaltvorgang

#### Aktueller Stand

- Eine interaktive Stromkurve ist vorhanden.
- Widerstand, Induktivität und Versorgungsspannung sind einstellbar.
- `τ = L/R`, Prozentwerte und Endstrom werden grundsätzlich dargestellt.
- Ein- und Ausschalten können ausgewählt werden.

#### Festgestelltes Problem

Die Grafik zeigt hauptsächlich den Spulenstrom. Für das Verständnis fehlt die Spannung an der Spule. Der wichtige Zusammenhang `u_L = L · di/dt` wird dadurch optisch nicht ausreichend vermittelt.

#### Verbesserungsauftrag

Die Lernansicht soll Spannung und Strom gemeinsam darstellen:

- Schaltzustand beziehungsweise Eingangsspannung als Rechteckverlauf zeigen.
- Spulenstrom `I_L(t)` darstellen.
- Spulenspannung `U_L(t)` gleichzeitig darstellen.
- Einschaltvorgang:
  - Strom beginnt bei seinem Startwert und steigt exponentiell gegen `U/R`.
  - Spulenspannung ist unmittelbar nach dem Einschalten maximal.
  - Spulenspannung fällt mit abnehmender Stromänderung gegen null.
- Ausschaltvorgang:
  - Strom kann nicht sprunghaft auf null fallen.
  - Spulenspannung kehrt ihre Polarität um, damit der Strom weiterfliessen kann.
  - Bei einer Freilaufdiode wird die Spannung begrenzt und der Strom fällt langsamer ab.
- Den Ausschaltvorgang mit und ohne Freilaufdiode vergleichbar machen.
  - **Umgesetzt mit Abschaltwiderstand `R_aus` (Standard 10 kΩ).** Im idealen Modell ist die Abschaltspannung ohne Freilaufpfad unendlich gross. Für die Simulation muss der Ausschaltpfad festgelegt werden (z.B. Abschaltwiderstand `R_aus`, Z-Diode oder Durchbruchspannung). Daraus folgt `τ_aus = L / (R_Spule + R_aus)`.
- Klar anzeigen, welche Widerstände im Einschalt- und Ausschaltpfad wirksam sind.
- Wenn unterschiedliche Zeitkonstanten entstehen, beide ausgeben:
  - `τ_ein`
  - `τ_aus`
- Magnetische Energie `W = 1/2 · L · I²` am gewählten Zeitpunkt anzeigen.
- `1τ` bis `5τ` mit realer Zeit beschriften.
- Prozentwerte beim Ein- und Ausschalten passend erklären.
- Aktuellen Zeitpunkt über Slider oder animierten Cursor auswählen.
- Aktuelle Werte anzeigen:
  - Zeit
  - Strom
  - Spulenspannung
  - gespeicherte Energie
- Zwei übereinanderliegende Diagramme sind zu bevorzugen, wenn Spannung und Strom sonst schwer vergleichbar sind.

#### Gewünschtes Lernziel

Die Grafik soll zeigen, dass die Spule nicht einfach nur einen langsam ansteigenden Strom erzeugt. Entscheidend ist, dass die Spulenspannung von der Geschwindigkeit der Stromänderung abhängt und beim Abschalten die Polarität wechselt.

---

## Transformator

### 1. Schaltzeichen

#### Festgestelltes Problem

Die Beschriftungen für Primärwicklung, Kern und Sekundärwicklung liegen teilweise direkt im Schaltzeichen. Dadurch werden Wicklungen, Kernlinien und Texte optisch vermischt.

#### Verbesserungsauftrag

- Beschriftungen vollständig ausserhalb des Schaltzeichens platzieren.
- `Primärwicklung N1`, `Kern` und `Sekundärwicklung N2` mit kurzen, eindeutigen Bezugslinien versehen.
- Keine Bezugslinie darf durch andere Texte verlaufen.
- Wicklungen symmetrisch und mit einheitlichem Abstand zum Kern zeichnen.
- Primär- und Sekundärseite durch Farben unterstützen, aber die Bedeutung nicht nur über Farbe vermitteln.
- Punktkennzeichnung für Wicklungssinn fachlich prüfen und erklären.
- Darstellung für schmale Fenster responsiv machen.

### 2. Regler und direkte Eingabe

#### Festgestelltes Problem

Primärspannung und Windungszahlen können über Slider verändert werden. Eine direkte numerische Eingabe fehlt oder ist nicht ausreichend sichtbar.

#### Verbesserungsauftrag

- Jeder Slider erhält ein direkt editierbares Zahlenfeld.
- Zahlenfeld und Slider bleiben synchron.
- Einheit neben dem Zahlenfeld darstellen.
- Sinnvolle Mindest- und Höchstwerte definieren.
- Werte ausserhalb des Sliderbereichs entweder zulassen und den Slider dynamisch anpassen oder mit verständlicher Meldung ablehnen.
- Rundungsfehler vermeiden.
- Windungszahlen nur als sinnvolle ganze Werte behandeln, sofern das Modell dies voraussetzt.

### 3. Transformator-Animation

#### Festgestelltes Problem

Die Darstellung zeigt Primärseite, Magnetfeld und Sekundärseite, aber die tatsächlichen Grössen sind nicht direkt in der Grafik erkennbar.

#### Verbesserungsauftrag

- In jedem Teilbereich die aktuellen Werte anzeigen:
  - Primärspannung `U1`
  - Primärwindungszahl `N1`
  - magnetischer Fluss beziehungsweise vereinfachtes Magnetfeld
  - Sekundärwindungszahl `N2`
  - Sekundärspannung `U2`
- Übersetzungsverhältnis sichtbar anzeigen.
- Klar kennzeichnen, ob Momentanwert, Scheitelwert oder Effektivwert dargestellt wird.
- Wenn die Animation einen Wechselspannungsverlauf zeigt, die Phasenlage von U1, Fluss und U2 erklären.
  - Idealer Trafo: Der Fluss `Φ` eilt `U1` um 90° nach; `U2` ist bei gleichem Wicklungssinn (Punktkennzeichnung) in Phase mit `U1`.
- Belastung der Sekundärseite als spätere Erweiterung vorsehen.
- Idealen und realen Transformator klar unterscheiden.
- Bei Überlast oder unrealistischen Eingaben Warnhinweise anzeigen.

---

## Diode

### 1. Schaltzeichen

#### Festgestelltes Problem

Die Texte für Anode und Kathode überlagern sich und ragen in das Schaltzeichen hinein. Auch bei den Varianten Siliziumdiode, Schottky-Diode und Z-Diode ist die Beschriftung zu dicht.

#### Verbesserungsauftrag

- Anode und Kathode räumlich klar trennen.
- Bezugslinien verwenden, die nicht durch das Symbol führen.
- Hinweis `Kathode = Ring` ausserhalb der Symbolfläche platzieren.
- Diodentypen mit identischer Grösse und gleichmässigen Abständen darstellen.
- Jeder Diodentyp erhält eine eindeutige Beschriftung unterhalb des Symbols.
- Beschriftungen müssen bei schmalem Fenster umbrechen oder die Symbole müssen untereinander angeordnet werden.

### 2. Kennlinie und Arbeitsgerade

#### Aktueller Stand

- Diodenkennlinie und Arbeitsgerade werden dargestellt.
- Ein Arbeitspunkt wird markiert.
- Die Z-Dioden-Kennlinie wurde bereits so angepasst, dass der Durchbruch im negativen Spannungsbereich gezeigt wird.

#### Noch zu verbessern

- Ausführlich erklären, was die Arbeitsgerade bedeutet.
- Zeigen, dass die Arbeitsgerade alle Kombinationen aus Diodenspannung und Strom beschreibt, die durch Versorgungsspannung und Vorwiderstand möglich sind.
- Erklären, dass der Schnittpunkt von Arbeitsgerade und Kennlinie der tatsächliche Arbeitspunkt ist.
- Achsenbeschriftungen und Einheiten kontrollieren.
- Prüfen, ob Stromwerte links abgeschnitten werden.
- Beschriftung der Arbeitsgeraden so positionieren, dass sie nicht über Kurve oder Achse liegt.
- Änderungen von Versorgungsspannung und Widerstand visuell nachvollziehbar machen.
- Optional Vorher/Nachher-Hinweise anzeigen:
  - höhere Versorgungsspannung verschiebt die Arbeitsgerade
  - grösserer Vorwiderstand macht die Arbeitsgerade flacher
- Für die Z-Diode klar zwischen Bauteilsicht `U_AK = -Uz` und Schaltungssicht `Ausgang = +Uz` unterscheiden.

---

## LED

### Schaltzeichen

#### Festgestelltes Problem

Die Beschriftungen für Anode und Kathode sind nicht sauber positioniert. Text wird teilweise abgeschnitten oder liegt zu nahe am Symbol und an den Anschlusslinien.

#### Verbesserungsauftrag

- Schaltzeichen mittig und mit gleich langen Anschlusslinien darstellen.
- Lichtpfeile mit genügend Abstand zeichnen.
- `Anode (langes Bein)` links ausserhalb des Symbols platzieren.
- `Kathode (kurz, abgeflacht)` rechts ausserhalb des Symbols platzieren.
- Bezugslinien kurz und eindeutig halten.
- Beschriftung darf bei kleinen Fensterbreiten nicht abgeschnitten werden.
- Optional zusätzlich Gehäusedarstellung mit flacher Seite und internem grösserem/kleinerem Elektrodenblech ergänzen.
  - Das grössere Elektrodenblech ist meist die Kathode, aber **nicht bei allen Herstellern** – als unsicheres Merkmal kennzeichnen. Verlässlich: kurzes Bein, abgeflachte Gehäuseseite, Messung mit Diodentest.
- Polung, typischen Spannungsbereich und benötigten Vorwiderstand direkt verknüpfen.

---

## Bipolartransistor und MOSFET

### Festgestelltes Strukturproblem

Die interaktive Darstellung `Transistor als Schalter` kombiniert Bipolartransistor und MOSFET auf derselben Seite beziehungsweise in derselben Ansicht. Dadurch werden zwei unterschiedliche Bauteilprinzipien unnötig vermischt.

### Verbesserungsauftrag

#### Bipolartransistor-Seite

- Nur Bipolartransistoren behandeln.
- Auswahl zwischen NPN und PNP anbieten.
- Schalterdarstellung an den jeweiligen Typ anpassen.
- Basisstrom, Basiswiderstand, Kollektorstrom, Sättigungsspannung und Verlustleistung anzeigen.
- Low-Side- und High-Side-Anwendung verständlich unterscheiden.
- Erklären, dass der Bipolartransistor stromgesteuert ist.
- Übersteuerungsfaktor sichtbar machen.
- Warnen, wenn der Basisstrom nicht für sichere Sättigung reicht.

#### MOSFET-Seite

- Nur MOSFETs behandeln.
- Auswahl zwischen N-Kanal und P-Kanal anbieten.
- Gate-Spannung, `V_GS`, `R_DS(on)`, Laststrom und Verlustleistung anzeigen.
- Low-Side- und High-Side-Anwendung verständlich unterscheiden.
- Erklären, dass der MOSFET spannungsgesteuert ist, beim Umschalten aber Gate-Ladung bewegt werden muss.
- Logic-Level-Eignung nicht nur anhand der Threshold-Spannung bewerten.
- Datenblattwert von `R_DS(on)` bei passender Gate-Spannung berücksichtigen.

#### Gemeinsame Anforderungen

- Keine Registerkarte oder Auswahl verwenden, die BJT und MOSFET fachlich wie austauschbare Varianten desselben Modells erscheinen lässt.
- Eine Vergleichsseite kann später getrennt erstellt werden.
- Diese Vergleichsseite soll Unterschiede bei Ansteuerung, Verlusten, Geschwindigkeit und typischen Anwendungen zeigen.

---

## Relais

### Aktueller Stand

- Vollständige Seite: Aufbau, Kontaktarten und Klemmen (11/12/14, A1/A2), Kennwerte, AC/DC-Schalten, Freilaufdiode, Ansteuerung mit Transistor, Selbsthaltung, Relais/Schütz/SSR.
- Rechner: Ansteuerung mit Transistor, Freilauf-Vergleich (Diode / Diode + Z-Diode), Ansprechen bei heisser Spule, Einschaltströme von Lasten.
- Der Freilauf-Rechner wird auch auf den Seiten Diode und MOSFET verwendet.

### Noch zu prüfen

- Schaltzeichen bei schmalem Fenster.
- Rechner fachlich systematisch verifizieren (wie alle anderen).

---

# Globale Verbesserungen der Interaktivität

## Slider plus Eingabefeld

Für alle interaktiven Regler gilt:

- Slider bleibt für schnelles Experimentieren erhalten.
- Zusätzlich direkt editierbares Zahlenfeld anbieten.
- Einheit separat auswählbar machen.
- Slider, Eingabefeld und Grafik müssen sofort synchron reagieren.
- Eingabe mit Enter übernehmen.
- Optional Fokusverlust als Übernahme verwenden.
- Ungültige Eingabe rot markieren und verständlich erklären.
- Keine stillen Korrekturen ohne Hinweis.

## Darstellung aktueller Werte

Interaktive Grafiken sollen wichtige Grössen direkt sichtbar machen:

- Bezeichnung
- aktueller Zahlenwert
- Einheit
- Formel oder Zusammenhang
- gegebenenfalls Warnstatus

## Diagramme

- Achsen mit Symbol und Einheit beschriften.
- Wertebereiche automatisch sinnvoll skalieren.
- Nullpunkt nicht unnötig abschneiden.
- Kurvenfarben konsistent verwenden.
- Farbe nie als einziges Unterscheidungsmerkmal verwenden.
- Legende ausserhalb kritischer Kurvenbereiche platzieren.
- Hilfslinien dezent halten.
- Prozentwerte nicht über andere Beschriftungen legen.
- Cursorwerte gut lesbar darstellen.
- Skalenwerte immer mit Einheit an die Achse schreiben (`bauteile/grafiken/skala.py`: `schoene_grenze`, `wert_text`, `achse_y`; in Schaltungen `Schaltplan.diagramm(..., einheit="spannung", t_ende=...)`).
- Die Skala richtet sich nach dem Signal, nicht nach einem festen Mindestwert – auch mV- und µA-Signale (Elektronik) sollen das Diagramm füllen.

---

# Geplanter Ausbau der Bauteile

## Passive Bauteile

- Potentiometer
- Varistor
- Sicherung
- NTC und PTC vertiefen
- lichtabhängiger Widerstand

## Dioden und Optoelektronik

- Si-, Schottky- und SiC-Vergleich
- TVS-Diode
- Fotodiode
- Fototransistor
- Solarzelle
- Optokoppler
- Lichtschranke
- Laserdiode als spätere Vertiefung

## Transistoren und Schaltbauteile

- JFET
- Darlington
- Thyristor
- TRIAC
- Optotriac
- IGBT als spätere Vertiefung

## Spannungsregler

- Festspannungsregler
- einstellbarer Linearregler
- LDO
- Datenblattbegriffe wie Dropout, Line Regulation und Load Regulation

---

# Schaltungen

Der Schaltungen-Bereich soll keine reine Bildergalerie werden. Jede Schaltung benötigt Funktion, Dimensionierung, Betriebszustände, Messpunkte, Grenzfälle, typische Fehler und passende Rechner.

## Priorität 1: Pflichtschaltungen

### Widerstandsnetzwerke

- Spannungsteiler
- belasteter Spannungsteiler
- Stromteiler
- Pull-up und Pull-down
- Potentiometer als Teiler
- Wheatstone-Brücke

### Dioden- und Schutzschaltungen

- Diodenbegrenzung
- Eingangsschutz
- Verpolschutz mit Diode
- Verpolschutz mit P-MOSFET
- Freilaufdiode
- Einweg- und Brückengleichrichter
- Mittelpunktschaltung
- Gleichrichter mit Ladeelko
- Z-Dioden-Stabilisierung
- TVS-Schutz

### Transistor- und MOSFET-Schaltungen

- NPN Low-Side-Schalter
- PNP High-Side-Schalter
- N-MOSFET Low-Side-Schalter
- P-MOSFET High-Side-Schalter
- Relaisansteuerung
- LED- und Motoransteuerung
- Emitterschaltung
- Emitterfolger
- Transistor- und JFET-Konstantstromquelle

### RC- und RL-Schaltungen

- RC-Tiefpass
- RC-Hochpass
- RC-Laden und Entladen
- Tasterentprellung
- RL-Ein- und Ausschalten
- Freilaufpfad
- Anti-Aliasing-Tiefpass

### Operationsverstärker

- Spannungsfolger
- invertierender Verstärker
- nichtinvertierender Verstärker
- Addierverstärker
- Differenzverstärker
- Instrumentenverstärker
- Komparator
- Schmitt-Trigger invertierend und nichtinvertierend
- Schmitt-Trigger mit Offset
- Integrator
- Differenzierer

### Netzteile und Quellen

- reales Spannungs- und Stromquellenmodell
- Transformator, Gleichrichter und Elko
- Linearregler und LDO
- Strombegrenzung
- bipolare Versorgung
- geregelte Stromquelle
- Buck und Boost als Grundprinzip

## Priorität 2: Sehr wichtige Ergänzungen

- Filter zweiter Ordnung ✅ (9a)
- LC-Tiefpass ✅ (9a)
- aktive Filter ✅ (9a, Sallen-Key)
- Pt100 in 2-, 3- und 4-Leiter-Schaltung
- NTC-Spannungsteiler
- DMS-Brücken
- Instrumentenverstärker an Messbrücke
- Open Collector und Open Drain
- Tri-State
- Logikpegelwandler
- Optokoppler
- H-Brücke
- MOSFET-Gate-Treiber
- ADC-Eingangsschutz

## Priorität 3: Nice to have

- UART-Grundbeschaltung
- RS-485 und CAN-Abschluss
- I²C-Pull-ups
- SPI-Grundbeschaltung
- Watchdog
- Rechteck-/Dreieckgenerator
- Multivibrator
- 555-Timer monostabil und astabil
- VCO-Grundprinzip
- Darlington- und AB-Endstufe

## Vorerst nicht priorisiert

- Smith-Diagramm und HF-Anpassung
- Antennentechnik
- vollständige Flyback-, PFC-, LLC- und Resonanzwandler-Auslegung
- Lock-in- und Chopper-Verstärker
- hochspezialisierte Spektrumanalysator-Schaltungen

---

# Messtechnik

## Vorhandene und geplante Kernthemen

- Messfehler und Messunsicherheit
- Effektivwert und True RMS
- Digitalmultimeter
- Oszilloskop
- Pt100/Pt1000
- NTC
- Thermoelement
- Wheatstone-Brücke und DMS
- Durchflussverfahren
- AD-Wandler und Aliasing

## Noch systematisch zu prüfen

- fachliche Richtigkeit aller Formeln
- Einheiten und Umrechnungen
- Grenzfälle
- Darstellungen im schmalen Fenster
- direkte Eingabe zusätzlich zu Slidern
- klare Verlinkung zwischen Sensor, Messschaltung und Rechner

---

# Digitaltechnik

Digitaltechnik soll langfristig ein eigener Hauptbereich werden.

## Inhalte

- analoge und digitale Signale
- Logikpegel und Störabstand
- AND, OR, NOT, NAND, NOR, XOR und XNOR
- Wahrheitstabellen
- Funktionsgleichungen
- Normalformen
- boolesche Algebra und De Morgan
- KV-Diagramme
- Halb- und Volladdierer
- Zweierkomplement
- Zahlensysteme und Codes
- Bitmasken
- Multiplexer, Demultiplexer, Decoder und Encoder
- TTL, CMOS, Open Collector, Open Drain, Tri-State

## Interaktive Werkzeuge

- Logikgatter-Simulator
- Wahrheitstabellengenerator
- boolescher Ausdruck zu Wahrheitstabelle
- Wahrheitstabelle zu Normalform
- KV-Diagramm-Vereinfacher
- Zahlensystem-Rechner
- Zweierkomplement-Rechner
- Bitmasken-Werkzeug
- Addierer-Simulator
- Logikpegel-Kompatibilitätsprüfer

---

# Zentraler Rechner-Tab

Der bisherige Formel-Tab soll in **Rechner** umgewandelt werden.

## Ziel

- Formeln bleiben auf den passenden Wissensseiten.
- Wissensseiten erklären den fachlichen Zusammenhang.
- Wissensseiten und Rechner-Tab verwenden dieselbe Berechnungslogik.
- Rechner werden nicht kopiert.

## Funktionen

- globale Suche
- Kategorien und Unterkategorien
- alphabetische und thematische Ansicht
- direkte Verlinkung zur Wissensseite
- später Favoriten, Verlauf und gespeicherte Berechnungen

## Kategorien

- Grundlagen
- Bauteile
- Schaltungen
- Messtechnik
- Digitaltechnik

## Zentrale Registry

```python
RECHNER = {
    "gleichrichter": gleichrichter,
    "pt100": pt100,
    "bjt_schalter": bjt_schalter,
}
```

Wissensseiten speichern nur Rechner-IDs:

```python
"rechner": ["gleichrichter"]
```

## Metadaten

```python
RECHNER_INFO = {
    "gleichrichter": {
        "titel": "Gleichrichter mit Ladeelko",
        "kategorie": "Schaltungen",
        "unterkategorie": "Netzteile",
        "beschreibung": "Berechnet Gleichspannung, Welligkeit und Sperrspannung.",
        "stichworte": ["Brücke", "Einweg", "Elko", "Brummspannung"],
        "wissensseite": "diode",
    }
}
```

## Validierung

Prüfskript für:

- doppelte Rechner-IDs
- unbekannte Rechner-IDs
- fehlende Metadaten
- ungültige Kategorien
- fehlende Stichworte
- Rechner ohne Wissensseite
- ungültige Querverweise

---

# Projektstruktur

```text
main.py                     Startpunkt, Liste der Bereiche (BEREICHE)
config.py                   Farben, Schriften, Pfade
core/                       Layout-Bausteine (Karte, ResponsiveGrid, Tabelle, FormatText …)
gui/                        ein Modul pro Tab (bauteile_gui, messtechnik_gui, server_gui …)
bauteile/inhalte/           Bauteil-Seiten (nur Daten), ein Ordner pro Kategorie
bauteile/rechner/           Rechner + zentrale Registry (__init__.py), Mathe in *_mathe.py,
                            Metadaten für den Rechner-Tab in rechner_info.py
bauteile/grafiken/          Schaltzeichen und interaktive Grafiken
bauteile/engine/            zeichnet eine Seite (seite.py) und den ganzen Wiki-Bereich (wiki_bereich.py,
                            gemeinsam für Bauteile, Messtechnik, Schaltungen)
messtechnik/                Messtechnik-Seiten, Rechner und Grafiken
programmieren/engine/       Wiki-Engine (Lader, Suche, Seite, Codeblock, Befehlsliste)
programmieren/inhalte/      Programmier-Seiten (nur Daten)
server/inhalte/             Server-/Linux-Seiten (nur Daten, gleiche Engine)
images/                     Bilder und Icons
schaltungen/inhalte/        Schaltungs-Seiten (nur Daten, Vorlage _vorlage.py mit Pflichtabschnitten)
schaltungen/grafiken.py     interaktive Schaltpläne (Basis SchaltungsKarte aus bauteile/grafiken/schaltplan.py)
schaltungen/netzwerk_mathe.py  Rechnung Teiler, Pull-up, Poti, Brücke (ohne GUI, testbar)
pruefen.py                  prüft, ob alle wichtigen Dateien vorhanden sind
pruefen_rechner.py          prüft alle Rechner: bekannte Werte, Grenzfälle, Verweise (-v, --gui)
pruefung/rechner_faelle.py  Beispielwerte (von Hand gerechnet) für pruefen_rechner.py
```

---

# Pfade, EXE und Benutzerdaten

SystemLab darf keine festen Benutzerpfade enthalten. Aktuell erfüllt: `config.py` bildet alle Pfade relativ zum Programmordner.

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"
```

Für PyInstaller soll langfristig eine zentrale Ressourcenfunktion verwendet werden.

Benutzerdaten gehören nicht in den Installationsordner. Einstellungen, Favoriten, Lernfortschritt und gespeicherte Berechnungen sollen beispielsweise hier liegen:

```text
%LOCALAPPDATA%/SystemLab/
```

---

# GitHub, Releases und Updates

## Entwicklung

```powershell
git pull
git add .
git commit -m "Beschreibung der Änderung"
git push
```

## Nutzung aus dem Repository

```powershell
git clone <Repository-URL>
pip install -r requirements.txt
python main.py
```

Updates werden zunächst mit `git pull` geholt.

## Spätere Releases

- Versionsnummer
- Änderungsübersicht
- bekannte Fehler
- Quellcode
- Windows-Build oder Installer
- optional Prüfsumme

Ein automatischer Updater ist eine spätere Erweiterung. Zunächst reicht eine Update-Prüfung, die auf ein neues GitHub Release verweist.

---

# Qualitätsregeln

## Fachlich

- Formeln mit Einheiten testen.
- Näherungen und Annahmen sichtbar machen.
- Grenzfälle und Überlast erkennen.
- typische Werte nicht als garantierte Datenblattwerte darstellen.
- Netzspannung und Leistungselektronik mit Sicherheitshinweisen versehen.

## Rechner

Jeder Rechner benötigt Tests für:

- normalen Betriebsfall
- Nullwerte
- ungültige Eingaben
- fehlende Eingaben
- sehr kleine und sehr grosse Werte
- Einheitenumrechnung
- Grenz- und Überlastfälle

## GUI

- responsive Darstellung
- keine Textüberlagerungen
- klare Achsenbeschriftungen
- Slider plus direkte Eingabe
- kontrollierte Animationen
- klare Fehlermeldungen
- einheitliche Farben und Schriften

## Inhalte

- eigene verständliche Formulierungen
- konsistente Formelzeichen
- selbst erstellte Abbildungen
- keine kopierten Textpassagen, Tabellen oder Aufgabenserien
- Verweise zwischen zusammengehörenden Themen

---

# Quellen und Urheberrecht

Fachbücher, Schulunterlagen und Datenblätter dienen nur als Grundlage zum Lernen, Prüfen und Strukturieren. Für ein öffentliches oder kommerzielles SystemLab werden Inhalte eigenständig formuliert und visualisiert.

Nicht in das öffentliche Repository gehören:

- vollständige Bücher oder Schulunterlagen
- eingescannte Seiten
- kopierte Abbildungen und Tabellen
- längere Originaltexte
- fremde Aufgabenserien samt Lösungen ohne Erlaubnis
- private oder betriebliche Dokumente

Vor einer kommerziellen Veröffentlichung müssen auch die Lizenzen der Python-Pakete, Schriften, Icons und Assets geprüft werden.

---

# Vereinbarte Reihenfolge der Umsetzung

Gemeinsame Bausteine zuerst, weil jede Seite davon profitiert. Jeder Schritt wird einzeln getestet und separat committet.

| # | Schritt | Status |
|---|---|---|
| 0 | Alte Übergangsdateien entfernen, README aktualisieren | ✅ erledigt |
| 1 | Gemeinsame Komponente **Slider + Zahlenfeld + Einheit** (`WertRegler` in `bauteile/rechner/basis.py`, eingebaut in RC/RL-Kurve, Trafo-Animation, Diodenkennlinie, Transistor-Schalter, Abtast-Grafik) | ✅ erledigt |
| 2 | Gemeinsame Komponente **Schaltzeichen-Reihe** (`SymbolReihe` in `bauteile/grafiken/symbol_reihe.py`; alle Schaltzeichen in `symbole.py` neu gezeichnet: eigene Zelle pro Symbol, gleiche Grösse, Beschriftung darunter, Anschlussbezeichnungen ausserhalb, Umbruch bei schmalem Fenster) | ✅ erledigt |
| 3 | Simulator Bipolartransistor (NPN/PNP) und MOSFET (N-/P-Kanal) trennen (`schalter_simulator.py`, Rechnung in `transistor_mathe.py` / `mosfet_mathe.py`; Low-/High-Side, Übersteuerungsfaktor, R_DS(on) bei tatsächlicher U_GS, U_GS,max, Gate-Ladung) | ✅ erledigt |
| 4 | RC- und RL-Lernansicht: Spannung und Strom, zwei Diagramme, `τ_ein` / `τ_aus` (`kurven.py` neu, Rechnung in `schaltvorgaenge_mathe.py`; Eingang als Rechteck, Startspannung U_C0, Vorzeichen erklärt, Ausschalten ohne Freilaufdiode (Modell R_aus), mit Freilaufdiode und mit Diode + Z-Diode) | ✅ erledigt |
| 5 | Prüfskript für alle Rechner mit bekannten Beispielwerten und Grenzfällen (`python pruefen_rechner.py`, Fälle in `pruefung/rechner_faelle.py`; zentrale Eingabeprüfung in `basis.formel_auswerten()`; dabei gefundene Fehler behoben, siehe unten) | ✅ erledigt |
| 6 | Rechner-Tab mit `RECHNER_INFO` (Formel-Tab ersetzt; Kategorien Grundlagen/Bauteile/Schaltungen/Messtechnik/Digitaltechnik mit Unterkategorien, Suche, A–Z, Knopf zur Wissensseite + „auch auf“; Validierung in `pruefen_rechner.py`) | ✅ erledigt |
| 7a | Schaltungen-Tab: gemeinsamer Wiki-Baustein (`bauteile/engine/wiki_bereich.py`, ersetzt 3 Kopien), Schaltplan-Zeichner (`bauteile/grafiken/schaltplan.py`, Raster, Spannung blau / Strom rot / Messpunkte orange), `SchaltungsKarte` für interaktive Pläne, Kategorie Widerstandsnetzwerke mit 5 Seiten, Pflichtabschnitte werden geprüft | ✅ erledigt |
| 7b | Dioden & Schutz: 7 Seiten mit interaktiven Schaltplänen (Zeitdiagramm bei Begrenzer, Gleichrichter, TVS), Rechnung in `schaltungen/dioden_mathe.py` (auch vom Gleichrichter-Rechner genutzt), neue Rechner Eingangsschutz, Verpolschutz-Vergleich, TVS prüfen; Messwerte-Tab entfernt | ✅ erledigt |
| 7c | Transistor & MOSFET: 6 Seiten (Schalter-Seiten nutzen die bestehenden Simulatoren), neue interaktive Pläne Lasttreiber, Emitterschaltung, Emitterfolger, Konstantstromquelle; Rechnung in `schaltungen/verstaerker_mathe.py` (auch vom Arbeitspunkt-Rechner genutzt, der jetzt Vu mit C_E und r_ein zeigt); neue Rechner Emitterfolger und Konstantstromquelle | ✅ erledigt |
| 7d | RC & RL: 5 Seiten (Laden/Entladen und RL ein/aus nutzen die bestehende Lernansicht und den Freilauf-Plan), neue interaktive Pläne Tief-/Hochpass (Bode + Zeitbereich), Tasterentprellung (Prell-Simulation), Anti-Aliasing (Abtastpunkte mit/ohne RC); Rechnung in `schaltungen/rc_mathe.py` (`alias_frequenz` auch von der Abtast-Grafik in Messtechnik genutzt); neue Rechner Frequenzgang, Entprellung, Anti-Aliasing | ✅ erledigt |
| 7e | OPV-Grundschaltungen: 5 Seiten (Verstärker, Addierer, Differenz-/Instrumentenverstärker, Komparator/Schmitt-Trigger, Integrator/Differenzierer), neues OPV-Symbol `Schaltplan.opv()`, 5 interaktive Pläne mit Simulation (Übersteuerung, Flattern, Drift), Rechnung in `schaltungen/opv_mathe.py`, 5 neue Rechner | ✅ erledigt |
| 7f | Netzteile & Quellen: 7 Seiten (Quellenmodell, Netzteil auslegen, Linearregler/LM317, Strombegrenzung, geregelte Stromquelle, bipolare Versorgung/virtuelle Masse, Buck/Boost), Spulen-Symbol `Schaltplan.spule()`, 6 interaktive Pläne, Rechnung in `schaltungen/netzteil_mathe.py`, 7 neue Rechner; Normwert-Auswahl (nächster / nächst grösserer) in den Schaltungs-Rechnern korrigiert | ✅ erledigt |
| 8a | Digitaltechnik als eigener Tab (`digitaltechnik/`, `gui/digitaltechnik_gui.py`, Pflichtabschnitte Grundlagen/Vorgehen/Beispiel/Praxis): Zahlensysteme & Codes, Zweierkomplement & Overflow, Bitmasken, analog/digital, Logikpegel & Störabstand; 4 interaktive Werkzeuge (Bit-Umrechner, Zahlenkreis, Bitmasken, Pegelbänder), 5 Rechner | ✅ erledigt |
| 8b | Logik: 4 Seiten (Gatter, boolesche Algebra/De Morgan, Normalformen, KV-Diagramme); Parser für boolesche Ausdrücke (viele Schreibweisen), Quine-McCluskey mit don't cares in `digitaltechnik/logik_mathe.py`; Werkzeuge Gatter-Simulator (IEC + ANSI), Ausdruck → Tabelle/Normalformen, KV-Diagramm mit Blöcken; 3 Rechner | ✅ erledigt |
| 8c | Schaltnetze & Ausgänge: 4 Seiten (Addierer, Multiplexer, Decoder/Encoder/7-Segment, Ausgangstypen); Werkzeuge Ripple-Carry-Addierer, MUX/DEMUX, Decoder/Prioritäts-Encoder/7-Segment, Push-Pull/Open Drain/Tri-State an einer Leitung; Rechnung in `digitaltechnik/schaltnetze_mathe.py`; 5 Rechner (Addierer-Laufzeit, MUX-Funktion, 7-Segment, Adressdecoder, I²C-Pull-up) | ✅ erledigt |
| 8d | Schaltwerke: 4 Seiten (Flipflops, Zähler, Schieberegister, synchroner Zählerentwurf); Werkzeuge Flipflop mit Takt und Zeitdiagramm, Zähler asynchron/synchron mit Zwischenzuständen, Schieberegister/Ring/Johnson; Zählerentwurf mit D/JK und Selbststart-Prüfung in `digitaltechnik/schaltwerke_mathe.py`; 3 Rechner | ✅ erledigt |
| 8e | Busse und Speicher: 4 Seiten (UART/RS-232/RS-485, SPI, I²C, Halbleiterspeicher); Werkzeuge UART-Rahmen (TTL + RS-232), SPI-Modi 0 … 3, I²C mit START/ACK/NACK/Sr/STOP, Speicherbaustein mit CS/OE/WE; Rechnung in `digitaltechnik/busse_mathe.py`; 6 Rechner (UART-Timing, Baudraten-Teiler, SPI, I²C-Dauer, Speicher-Organisation, Speicher erweitern) | ✅ erledigt |
| 8f | Überarbeitung: Server-Beispiele mit allgemeinen Platzhaltern + Einstiegsseite „Erste Schritte“; alle Diagramme mit Skalenwerten und Einheiten, Skala nach Signal (kleine Spannungen/Ströme gut sichtbar): Trafo-Animation, Schaltungsdiagramme, Diodenkennlinien, Abtastung | ✅ erledigt |
| 9a | Filter 2. Ordnung: 3 Seiten (LC-Tiefpass, Bandpass/Bandsperre mit Schwingkreis, aktive Sallen-Key-Filter); 3 interaktive Pläne mit Bode-Diagramm und umschaltbarer Sprungantwort (exakt gelöst, stabil für jedes Q); Rechnung in `schaltungen/filter_mathe.py`; 3 Rechner (LC-Tiefpass, Schwingkreis, Sallen-Key auslegen mit Normwerten); `STARTWERTE` je Variante jetzt in `SchaltungsKarte` | ✅ erledigt |
| 9b+ | Priorität 2 weiter: Sensor-Messschaltungen (Pt100 2/3/4-Leiter, NTC-Teiler, DMS-Brücke + Instrumentenverstärker), dann Schnittstellen/Leistung (Pegelwandler, Optokoppler, H-Brücke, Gate-Treiber, ADC-Eingangsschutz) | offen |

### Schritt 5: Was das Prüfskript gefunden hat (behoben)

```bash
python pruefen_rechner.py          # schnell, ohne Fenster
python pruefen_rechner.py --gui    # zusätzlich jede Rechner-Karte aufbauen
```

| Fehler | Wo | Behebung |
|---|---|---|
| Normwert bei pF-Werten falsch (4.7 pF → 5 pF, unter 1 pF → Absturz) | `normreihen.py` | auf gültige Stellen statt Nachkommastellen runden |
| „1A“ im mA-Feld ergab 1 mA | `einheiten.py` | getippte Einheit gilt vor dem Dropdown |
| „inf“ / „nan“ als Eingabe angenommen | `einheiten.py` | wird abgelehnt |
| Negative Widerstände, Kapazitäten, Zeiten … führten zu Unsinn oder Python-Fehlern | alle Formel-Rechner | zentrale Prüfung `NIE_NEGATIV` in `basis.py` |
| „Division durch 0“ ohne Hinweis, welches Feld | alle Formel-Rechner | Meldung nennt jetzt die Felder mit 0 |
| Pt100: Python-Fehler bei zu grossem R | `messtechnik/rechner.py` | Bereich −200 … 850 °C nach IEC 60751 |
| NTC: Python-Fehler bei R = 0 oder T unter 0 K | `messtechnik/rechner.py` | verständliche Meldung |
| Arbeitspunkt bei U_B < U_CE,sat zeigte „inf“ | `transistor_rechner.py`, `halbleiter_rechner.py` | Meldung |
| LED-Anzahl −1 oder 1.5 wurde gerechnet | `widerstand_rechner.py` | nur ganze Zahl ab 1 |
| ADC mit 10.5 Bit wurde still abgerundet | `messtechnik/rechner.py` | nur ganze Bitzahl |
| Netzteil/Gleichrichter mit zu kleiner Trafospannung ergab negative Gleichspannung | `trafo_rechner.py`, `halbleiter_rechner.py` | Meldung „U2 zu klein“ |

### Schritt 7a: Aufbau einer Schaltungsseite

Jede Schaltung hat die Pflichtabschnitte **Funktion, Dimensionierung, Betriebszustände, Messpunkte, Grenzfälle**, dazu typische Fehler, passende Rechner und einen interaktiven Schaltplan. `python pruefen_rechner.py` meldet fehlende Abschnitte. Weitere Neuerungen: `WertRegler(..., log=True)` für Widerstände/Kapazitäten über mehrere Dekaden, Stromeinheit nA.

### Schritt 6: Offene Punkte aus dem Rechner-Tab

- **Doppelter Rechner:** `bjt_schalter` (Halbleiter, E24) und `basiswiderstand` (Transistor, NPN/PNP, E12) rechnen beide den Basiswiderstand. Vorschlag: `bjt_schalter` entfernen und überall `basiswiderstand` verwenden – noch nicht umgesetzt (Entscheid offen).
- Favoriten, Verlauf über Programmstarts und gespeicherte Berechnungen: später.

Die folgenden Phasen beschreiben die Inhalte im Detail.

# Empfohlene nächste Arbeitsschritte

## Phase 1: Review vervollständigen

- weitere Beobachtungen aus dem praktischen Test sammeln
- keine vorschnellen GUI-Änderungen durchführen
- jede Beobachtung einer Seite oder gemeinsamen Komponente zuordnen
- fachliche und rein optische Fehler trennen

## Phase 2: Gemeinsame GUI-Probleme lösen

- responsive Schaltzeichen
- Beschriftungspositionen
- gemeinsame Slider-/Eingabefeld-Komponente
- Diagramm-Layout
- Einheiten- und Werteanzeige

## Phase 3: Bestehende Inhalte fachlich prüfen

- Widerstand
- Kondensator
- Spule
- Transformator
- Dioden und LED
- Bipolartransistor
- MOSFET
- Messtechnik

## Phase 4: Rechner-Tab

- Formel-Tab analysieren
- in Rechner umbenennen
- Registry um Metadaten erweitern
- Rechner automatisch sammeln
- Suche und Kategorien erstellen
- Wissensseiten verknüpfen

## Phase 5: Pflichtschaltungen

- Widerstandsnetzwerke
- Dioden- und Schutzschaltungen
- Transistor- und MOSFET-Schalter
- RC- und RL-Grundschaltungen
- Messbrücken und Sensorschnittstellen

## Phase 6: Operationsverstärker und Versorgung

- OPV-Grundschaltungen
- Quellenmodelle
- Gleichrichter und Siebung
- Linearregler
- Buck und Boost

## Phase 7: Digitaltechnik

- Logikgatter
- Wahrheitstabellen
- Zahlensysteme
- Zweierkomplement und Bitmasken
- KV-Diagramme
- Addierer und Multiplexer
- Logikpegel und Ausgangstypen

---

# Vision

SystemLab soll weder eine reine Formelsammlung noch nur ein digitales Fachbuch sein. Es soll eine technische Lernumgebung werden, in der Wissen, Berechnung und Experiment zusammengehören:

```text
Verstehen → Berechnen → Simulieren → Aufbauen → Messen → Verbessern
```
