# =============================================================================
# programmieren/engine/syntax.py
# -----------------------------------------------------------------------------
# SYNTAX-HIGHLIGHTING: färbt Code ein (Schlüsselwörter lila, Texte grün, ...)
#
# SO FUNKTIONIERT ES:
#   zerlegen(code, "Python") gibt eine Liste von Stücken zurück:
#       [("for", "keyword"), (" i ", None), ("in", "keyword"), ...]
#   engine/codeblock.py fügt die Stücke dann mit der passenden Farbe ein.
#
# Das ist ein einfacher Highlighter (kein vollständiger Parser) -
# für Lernbeispiele reicht das völlig.
# =============================================================================

import re

# -----------------------------------------------------------------------------
# Schlüsselwörter pro Sprache
# -----------------------------------------------------------------------------
KEYWORDS = {
    "Python": {
        "and", "as", "assert", "break", "class", "continue", "def", "del", "elif", "else",
        "except", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda",
        "nonlocal", "not", "or", "pass", "raise", "return", "try", "while", "with", "yield",
        "match", "case", "True", "False", "None", "self", "super",
    },
    "C++": {
        "if", "else", "switch", "case", "default", "for", "while", "do", "break", "continue",
        "return", "class", "struct", "public", "private", "protected", "virtual", "override",
        "const", "static", "new", "delete", "try", "catch", "throw", "namespace", "using",
        "include", "true", "false", "nullptr", "this", "template", "typename", "auto",
        "sizeof", "enum", "friend", "inline", "operator", "pragma", "once", "ifndef", "define", "endif",
    },
    "C#": {
        "if", "else", "switch", "case", "default", "for", "foreach", "in", "while", "do", "break",
        "continue", "return", "class", "struct", "public", "private", "protected", "internal",
        "virtual", "override", "abstract", "static", "readonly", "const", "new", "try", "catch",
        "finally", "throw", "namespace", "using", "true", "false", "null", "this", "base", "get",
        "set", "var", "out", "ref", "is", "as", "interface", "enum", "checked", "unchecked",
    },
    # Bash (Server-Wiki): Kontrollstrukturen der Shell
    "Bash": {
        "if", "then", "else", "elif", "fi", "for", "in", "do", "done", "while", "until", "case", "esac",
        "function", "return", "exit", "local", "export", "source", "true", "false", "break", "continue",
    },
}

# Datentypen (bekommen eine eigene Farbe)
TYPEN = {
    "Python": {"int", "float", "str", "bool", "list", "dict", "tuple", "set", "complex", "bytes",
               "print", "input", "len", "range", "type", "open", "isinstance", "enumerate"},
    "C++": {"int", "float", "double", "char", "bool", "void", "short", "long", "unsigned", "signed",
            "string", "vector", "map", "unordered_map", "size_t", "int8_t", "int16_t", "int32_t",
            "int64_t", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "std", "cout", "cin", "endl",
            "cerr", "ifstream", "ofstream", "array", "exception", "runtime_error", "unique_ptr",
            "make_unique", "getline"},
    "C#": {"int", "uint", "float", "double", "decimal", "char", "bool", "void", "short", "ushort",
           "long", "ulong", "byte", "sbyte", "string", "object", "List", "Dictionary", "Console",
           "Math", "Exception", "File", "Convert", "Array", "StreamReader", "StreamWriter",
           "FormatException", "DivideByZeroException"},
    # Bash: die wichtigsten Befehle bekommen die "Typ"-Farbe (blau), sudo sticht so heraus
    "Bash": {"sudo", "su", "apt", "dpkg", "snap", "systemctl", "journalctl", "service", "ls", "cd", "pwd", "cp",
             "mv", "rm", "mkdir", "rmdir", "touch", "ln", "cat", "less", "head", "tail", "nano", "vim", "grep",
             "find", "locate", "which", "chmod", "chown", "chgrp", "useradd", "adduser", "usermod", "userdel",
             "deluser", "passwd", "groups", "id", "whoami", "ps", "top", "htop", "kill", "pkill", "killall",
             "df", "du", "lsblk", "blkid", "mount", "umount", "free", "uname", "uptime", "hostnamectl",
             "timedatectl", "ip", "ping", "ss", "curl", "wget", "dig", "nslookup", "traceroute", "tracepath",
             "netplan", "ufw", "ssh", "scp", "rsync", "sftp", "tar", "gzip", "gunzip", "zip", "unzip", "echo",
             "printf", "tee", "xargs", "sort", "uniq", "wc", "cut", "awk", "sed", "crontab", "reboot",
             "shutdown", "history", "man", "tldr", "ssh-keygen", "ssh-copy-id", "fail2ban-client", "stat",
             "chmod", "tree", "file", "diff", "date", "env", "alias", "fsck", "mkfs", "dd", "fdisk", "parted",
             "lsof", "nc", "nmap", "tmux", "screen", "watch", "test", "read", "set", "unattended-upgrade"},
}

# Kommentarzeichen pro Sprache
_KOMMENTAR = {"Python": r"#[^\n]*", "C++": r"//[^\n]*|/\*[\s\S]*?\*/", "C#": r"//[^\n]*|/\*[\s\S]*?\*/",
              "Bash": r"(?<![\w$])#[^\n]*"}          # "$#" (Anzahl Argumente) ist KEIN Kommentar

# -----------------------------------------------------------------------------
# GEFÄHRLICHE BEFEHLE (Server-Wiki) - werden im Code rot hinterlegt und in
# Befehlslisten mit ⚠ markiert. Muster = regulärer Ausdruck pro Zeile.
# -----------------------------------------------------------------------------
GEFAHR_MUSTER = [
    r"\brm\s+(-\w*[rR]\w*f\w*|-\w*f\w*[rR]\w*|--recursive\s+--force|-rf|-fr)\b[^\n#]*",   # rm -rf ...
    r"\bchmod\s+(-R\s+)?[0-7]?777\b[^\n#]*",                                              # chmod 777
    r"\bchmod\s+(-R\s+)?(a|o)\+w\b[^\n#]*",
    r"\bdd\s+[^\n#]*\bof=/dev/[^\n#]*",                                                   # dd auf Laufwerk
    r"\bmkfs(\.\w+)?\b[^\n#]*",                                                           # formatieren
    r"\b(fdisk|parted|wipefs)\s+/dev/[^\n#]*",
    r">\s*/dev/sd\w*",
    r"\bchown\s+-R\s+[^\n#]*\s/(\s|$)",                                                   # chown -R ... /
    r"\bufw\s+disable\b",
    r"\bufw\s+allow\s+(from\s+any\s+to\s+any|\d+:\d+)\b[^\n#]*",
    r"\bPermitRootLogin\s+yes\b",
    r"\bPasswordAuthentication\s+yes\b",
    r"\bcurl\s+[^\n#|]*\|\s*(sudo\s+)?(ba)?sh\b",                                         # curl ... | sh
    r"\bwget\s+[^\n#|]*\|\s*(sudo\s+)?(ba)?sh\b",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",                                           # Fork-Bombe
    r"\bkill\s+-9\s+(-1|1)\b",
    r"\biptables\s+-F\b",
    r"\brsync(?![^\n#]*(--dry-run|\s-\w*n\b))\s[^\n#]*\s--delete\b[^\n#]*",             # rsync --delete (ohne -n)
]
_GEFAHR = re.compile("|".join(f"(?:{m})" for m in GEFAHR_MUSTER))


def gefahr_stellen(zeile):
    """Liste von (start, ende) aller gefährlichen Stellen in EINER Code-Zeile (Kommentare ausgenommen)."""
    ohne_kommentar = re.split(r"(?<![\w$])#", zeile, maxsplit=1)[0]
    return [t.span() for t in _GEFAHR.finditer(ohne_kommentar)]


def ist_gefaehrlich(befehl):
    """True, wenn der Befehl ein gefährliches Muster enthält (für Befehlslisten)."""
    return bool(gefahr_stellen(befehl))


def _regex_fuer(sprache):
    """Baut EINEN grossen regulären Ausdruck mit benannten Gruppen."""
    kommentar = _KOMMENTAR.get(sprache, r"#[^\n]*|//[^\n]*")
    if sprache == "C++":
        kommentar = r"#\s*\w+|" + kommentar          # #include, #pragma -> wie Kommentar-Farbe
    teile = [
        rf"(?P<kommentar>{kommentar})",
        r'(?P<string>"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|\$?"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\')',
        r"(?P<zahl>\b0x[0-9A-Fa-f]+\b|\b0b[01]+\b|\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?[fFmMuUlL]*\b)",
        r"(?P<wort>\b[A-Za-z_]\w*\b)",
    ]
    return re.compile("|".join(teile))


_CACHE = {}


def zerlegen(code, sprache):
    """
    Zerlegt 'code' in (text, tag)-Stücke.
    tag ist eines von: keyword, typ, string, kommentar, zahl, funktion  oder None
    """
    if sprache not in _CACHE:
        _CACHE[sprache] = _regex_fuer(sprache)
    muster = _CACHE[sprache]
    keywords = KEYWORDS.get(sprache, set())
    typen = TYPEN.get(sprache, set())

    stuecke, pos = [], 0
    for treffer in muster.finditer(code):
        start, ende = treffer.span()
        if start > pos:
            stuecke.append((code[pos:start], None))      # normaler Text dazwischen

        art = treffer.lastgroup
        text = treffer.group()
        if art == "wort":
            if text in keywords:
                art = "keyword"
            elif text in typen:
                art = "typ"
            elif code[ende:ende + 1] == "(":            # Name direkt vor "(" = Funktionsaufruf
                art = "funktion"
            else:
                art = None
        stuecke.append((text, art))
        pos = ende

    if pos < len(code):
        stuecke.append((code[pos:], None))
    return stuecke
