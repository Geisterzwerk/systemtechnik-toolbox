# Thema: Module, Bibliotheken & Imports  (Kategorie: Fortgeschritten)
THEMA = {
    "titel": "Module, Bibliotheken & Imports",
    "reihenfolge": 3,
    "kurz": "Fremden und eigenen Code einbinden: import, #include, using, pip, NuGet.",
    "stichworte": ["import", "module", "modul", "bibliothek", "library", "include", "using", "pip",
                   "nuget", "package", "paket", "venv", "virtuelle umgebung", "requirements",
                   "standardbibliothek", "__name__", "__init__.py", "from"],

    "erklaerung": """
## Drei Arten von Code
- **Standardbibliothek:** ist mitgeliefert, z.B. Python `math`, `os`, `json`; C++ `<vector>`, `<cmath>`; C# `System.IO`
- **Externe Pakete:** muss man installieren. Python: **pip**, C#: **NuGet**, C++: vcpkg/conan oder manuell
- **Eigener Code:** deine eigenen Dateien (siehe *Klassen in mehreren Dateien*)
## Python-Import-Varianten
- `import math`: Zugriff mit `math.sqrt(2)`
- `from math import sqrt`: Zugriff direkt mit `sqrt(2)`
- `import customtkinter as ctk`: Kurzname (Alias)
- `from math import *`: **vermeiden**, weil man nicht mehr sieht, woher ein Name kommt
## if __name__ == "__main__"
Beim Import wird eine Python-Datei **komplett ausgeführt**. Code unter `if __name__ == "__main__":` läuft aber nur, wenn die Datei **direkt gestartet** wird, und nicht beim Import. So kann eine Datei gleichzeitig Modul und eigenständiges Programm sein.
## Virtuelle Umgebung (Python)
Jedes Projekt bekommt seine eigenen Pakete, dadurch gibt es keine Versionskonflikte zwischen Projekten.
""",

    "beispiele": [
        {
            "titel": "Bibliotheken einbinden und benutzen",
            "code": {
                "Python": r'''import math                         # ganzes Modul
from datetime import datetime       # nur eine Sache
import customtkinter as ctk         # mit Alias (externes Paket)

print(math.sqrt(16))                # 4.0
print(math.pi)
print(datetime.now().strftime("%H:%M:%S"))''',
                "C++": r'''#include <cmath>       // < > = Standardbibliothek / installierte Bibliothek
#include <iostream>
#include "Sensor.h"    // " " = eigene Datei im Projekt

int main() {
    std::cout << std::sqrt(16.0) << "\n";   // std:: = Namespace der Standardbibliothek
    return 0;
}
// "using namespace std;" spart Tipparbeit, ist aber in grösseren Projekten
// (vor allem in Header-Dateien) schlechter Stil -> Namenskonflikte''',
                "C#": r'''using System;              // Namespaces einbinden
using System.IO;
using System.Text.Json;

Console.WriteLine(Math.Sqrt(16));        // 4
Console.WriteLine(DateTime.Now.ToString("HH:mm:ss"));
// Seit .NET 6 sind viele usings bereits automatisch aktiv (ImplicitUsings)''',
            },
        },
        {
            "titel": "Pakete installieren (Terminal)",
            "code": {
                "Python": r'''# Virtuelle Umgebung anlegen und aktivieren (Windows)
python -m venv .venv
.venv\Scripts\activate

# Pakete installieren
pip install customtkinter pillow

# Installierte Pakete festhalten / auf anderem PC wiederherstellen
pip freeze > requirements.txt
pip install -r requirements.txt''',
                "C++": r'''# Windows: vcpkg (Paketmanager von Microsoft)
vcpkg install nlohmann-json

# Linux (Ubuntu): viele Bibliotheken über apt
sudo apt install libboost-all-dev''',
                "C#": r'''# NuGet-Paket zum Projekt hinzufügen
dotnet add package Newtonsoft.Json

# Pakete wiederherstellen (passiert bei dotnet build automatisch)
dotnet restore''',
            },
        },
        {
            "titel": "Eigenes Modul: Datei ist Modul UND Programm",
            "code": {
                "Python": r'''# ---------- elektro.py ----------
def leistung(u, i):
    return u * i

if __name__ == "__main__":
    # läuft NUR bei "python elektro.py", NICHT bei "import elektro"
    print("Test:", leistung(12, 2))


# ---------- main.py ----------
import elektro
print(elektro.leistung(230, 0.5))   # 115.0 (der Test oben läuft hier NICHT)''',
            },
            "hinweis": {
                "C++": "Nicht nötig: Nur die Datei mit `main()` ist der Startpunkt. Siehe *Klassen in mehreren Dateien*.",
                "C#": "Nicht nötig: Es gibt genau einen Startpunkt pro Projekt (Program.cs bzw. Main).",
            },
        },
    ],

    "tipps": [
        "Python: In VS Code unten rechts den Interpreter der `.venv` auswählen, sonst findet VS Code die installierten Pakete nicht.",
        "`requirements.txt` gehört zu jedem Python-Projekt. Auch für diese Toolbox: `customtkinter` und `pillow`.",
    ],
    "fehler": [
        "`ModuleNotFoundError`: Das Paket ist nicht installiert oder in der falschen Python-Umgebung installiert. Mit `python -m pip install ...` installiert man es sicher in das richtige Python.",
        "Eigene Datei heisst wie ein Modul (`math.py`, `json.py`, `customtkinter.py`) und überdeckt so das echte Modul.",
    ],
    "siehe_auch": ["mehrere_dateien", "programmablauf"],
}
