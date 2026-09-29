# Thema: Pointer & Referenzen  (Kategorie: Fortgeschritten)
THEMA = {
    "titel": "Pointer & Referenzen",
    "reihenfolge": 4,
    "kurz": "Adressen im Speicher: Zeiger in C++, Referenztypen in C# und Python. Stack vs. Heap.",
    "stichworte": ["pointer", "zeiger", "referenz", "reference", "adresse", "address", "&", "*",
                   "dereferenzieren", "nullptr", "null", "none", "new", "delete", "heap", "stack",
                   "speicherleck", "memory leak", "smart pointer", "unique_ptr", "shared_ptr",
                   "garbage collector", "werttyp", "referenztyp", "id()"],

    "erklaerung": """
## Speicheradressen
Jede Variable liegt an einer **Adresse** im Arbeitsspeicher, wie eine Hausnummer. Ein **Pointer (Zeiger)** ist eine Variable, die **eine Adresse speichert**, also auf eine andere Variable "zeigt".
## C++: Pointer und Referenzen
- `&x` → Adresse von x
- `int* p = &x;` → p ist ein Zeiger auf einen int und speichert die Adresse von x
- `*p` → **dereferenzieren**: den Wert an dieser Adresse lesen oder ändern
- `int& r = x;` → **Referenz**: ein zweiter Name für x (kann nicht null sein und nicht umgebogen werden)
- `nullptr` → Zeiger zeigt auf nichts
## Stack vs. Heap
- **Stack:** lokale Variablen, schnell, werden am Blockende automatisch freigegeben
- **Heap:** mit `new` angelegter Speicher. Er bleibt bestehen, bis er freigegeben wird. In C++ muss man ihn selbst freigeben (`delete`), sonst gibt es ein **Speicherleck**. Modern und sicher: **Smart Pointer** (`std::unique_ptr`), die das automatisch erledigen.
## C# und Python
Hier gibt es (fast) keine Pointer. Dafür unterscheidet man:
- **Werttypen** (C#: int, double, struct): Bei der Zuweisung wird **kopiert**
- **Referenztypen** (C#: class, Arrays, List; **in Python ALLES**): Die Variable speichert nur einen **Verweis**. Die Zuweisung `b = a` kopiert den Verweis, und beide zeigen auf **dasselbe Objekt**!
- Der **Garbage Collector** gibt nicht mehr benutzte Objekte automatisch frei.
""",

    "bild": "pointer.png",
    "bild_text": "Pointer p speichert die Adresse von x und zeigt damit auf x",

    "beispiele": [
        {
            "titel": "Pointer und Referenzen in C++",
            "code": {
                "C++": r'''#include <iostream>
#include <memory>

int main() {
    int x = 42;

    int* p = &x;                 // p speichert die ADRESSE von x
    std::cout << p << "\n";      // z.B. 0x7ffd5c3a1b2c
    std::cout << *p << "\n";     // 42  (Wert an der Adresse)
    *p = 99;                     // x über den Zeiger ändern
    std::cout << x << "\n";      // 99

    int& r = x;                  // Referenz = zweiter Name für x
    r = 7;
    std::cout << x << "\n";      // 7

    // Heap: alter Stil (Gefahr: delete vergessen = Speicherleck)
    int* heap = new int(5);
    delete heap;

    // Heap: moderner Stil - gibt Speicher AUTOMATISCH frei
    auto sicher = std::make_unique<int>(5);
    std::cout << *sicher << "\n";

    int* leer = nullptr;
    if (leer != nullptr) {       // IMMER prüfen vor dem Dereferenzieren
        std::cout << *leer;
    }
    return 0;
}''',
                "Python": r'''# Python hat keine Pointer - aber JEDE Variable ist eine Referenz!
a = [1, 2, 3]
b = a                  # KEINE Kopie: b zeigt auf dieselbe Liste
b.append(4)
print(a)               # [1, 2, 3, 4]  <- a ist auch verändert!
print(a is b)          # True  (gleiches Objekt)
print(id(a) == id(b))  # True  (id() = "Adresse" des Objekts)

c = a.copy()           # echte Kopie
c.append(5)
print(a)               # [1, 2, 3, 4]  <- unverändert''',
                "C#": r'''// Werttyp: Kopie
int a = 5;
int b = a;
b = 10;
Console.WriteLine(a);        // 5  (unverändert)

// Referenztyp: gleiches Objekt
var liste1 = new List<int> { 1, 2, 3 };
var liste2 = liste1;         // Verweis kopiert, NICHT die Liste
liste2.Add(4);
Console.WriteLine(liste1.Count);   // 4 !

var kopie = new List<int>(liste1); // echte Kopie

// null-Prüfung
List<int>? nichts = null;
Console.WriteLine(nichts?.Count ?? 0);   // ?. und ?? verhindern NullReferenceException''',
            },
        },
    ],

    "tipps": [
        "C++: `new`/`delete` in modernem Code vermeiden, stattdessen `std::vector`, `std::unique_ptr` oder `std::make_unique` verwenden.",
        "Auf Mikrocontrollern (Arduino, STM32) sind Pointer Alltag, z.B. für Register-Adressen und Puffer.",
    ],
    "fehler": [
        "C++: `nullptr` dereferenzieren führt zu einem Absturz (Segmentation Fault / Access Violation).",
        "C++: Pointer auf eine lokale Variable zurückgeben: Die Variable ist nach der Funktion weg (Dangling Pointer).",
        "Python/C#: `b = a` für eine Kopie halten. Das ist nur ein zweiter Name für dasselbe Objekt!",
    ],
    "siehe_auch": ["parameter_rueckgabe", "arrays_listen", "polymorphie", "konstruktor"],
}
