#!/usr/bin/env python3
"""Survey port coverage: which C++ headers are ported, what is pending.

AST-parses every Python module under ``ut99py/`` for the headers it cites
(``Ported from ...`` / ``Core/Inc/...`` / ``Engine/Inc/...`` in docstrings
and comments) and regex-scans the C++ tree (default ``~/code/Ut99PubSrc``)
for classes/structs/enums per header. Prints:

- ported headers with the Python modules that cite them
- unported headers, Core first, with their public symbols
- a "next job" hint (unported Core headers, then Engine)

This is the mandatory first step before picking the next header to port;
see AGENTS.md "Find the next port job".

Usage:
    python3 tools/port_survey.py [--cpp-dir DIR] [--json]
"""

import argparse
import ast
import json
import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PY_DIR = Path(__file__).resolve().parent.parent / "ut99py"
DEFAULT_CPP_DIR = Path(os.path.expanduser("~/code/Ut99PubSrc"))

# Headers a Python module may cite, e.g. "Port of Core/Inc/UnArc.h".
_HEADER_REF = re.compile(
    r"(?:Port(?:ed)?\s+(?:from|into)\s+)?"
    r"((?:Core|Engine|Audio|UCC|Setup|Window|XDrv|SampleNativePackage)/Inc/[A-Za-z0-9_]+\.h)"
    r"|(?:Port(?:ed)?\s+from\s+)([A-Za-z0-9_]+\.h)"
)
# C++ declarations with an optional API macro.
_CPP_CLASS = re.compile(r"^\s*class\s+(?:\w+_API\s+)?(\w+)", re.MULTILINE)
_CPP_STRUCT = re.compile(r"^\s*struct\s+(?:\w+_API\s+)?(\w+)", re.MULTILINE)
_CPP_ENUM = re.compile(r"^\s*enum\s+(?:\w+\s+)?(\w+)", re.MULTILINE)

# Skip aggregator headers (just #includes) and platform/platform-private noise.
_SKIP_HEADERS = {
    "Core/Inc/Core.h",
    "Engine/Inc/Engine.h",
    "Core/Inc/UnUnix.h",
    "Core/Inc/UnVcWin32.h",
    "Core/Inc/UnVcWn32SSE.h",
    "Core/Inc/UnGnuG.h",
    "Core/Inc/UnBuild.h",
}
# C++ keywords/macros that regex-match the class/struct patterns.
_CPP_NOISE = {
    "CORE_API",
    "ENGINE_API",
    "DLL_IMPORT",
    "DLL_EXPORT",
    "public",
    "private",
    "protected",
    "T",
    "U",
    "FA",
    "FN",
    "US",
}


def py_module_headers(py_path: Path) -> set[str]:
    """Headers cited by one Python module (docstrings, comments, code)."""
    text = py_path.read_text(encoding="utf-8", errors="replace")
    try:
        ast.parse(text)  # syntax gate; regex still sees comments
    except SyntaxError:
        pass
    found: set[str] = set()
    for match in _HEADER_REF.finditer(text):
        ref = match.group(1) or match.group(2)
        if "/" not in ref:
            # Bare filename: resolve against the C++ tree later.
            found.add(ref)
        else:
            found.add(ref)
    return found


def scan_python() -> tuple[dict[str, list[str]], set[str]]:
    """Map header path -> citing modules; plus unresolved bare filenames."""
    header_to_py: dict[str, list[str]] = {}
    bare: set[str] = set()
    for py_path in sorted(PY_DIR.rglob("*.py")):
        # include __init__.py as they may cite headers
        rel = str(py_path.relative_to(REPO_ROOT))
        for ref in py_module_headers(py_path):
            if "/" in ref:
                header_to_py.setdefault(ref, []).append(rel)
            else:
                bare.add(ref)
    return header_to_py, bare


def cpp_symbols(header: Path) -> dict[str, list[str]]:
    """Class/struct/enum names declared in one C++ header."""
    text = header.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)

    def names(rx: re.Pattern[str]) -> list[str]:
        return sorted({n for n in rx.findall(text) if n not in _CPP_NOISE})

    return {
        "classes": names(_CPP_CLASS),
        "structs": names(_CPP_STRUCT),
        "enums": names(_CPP_ENUM),
    }


def scan_cpp(cpp_dir: Path) -> dict[str, dict[str, list[str]]]:
    """Every header under */Inc of the C++ tree with its symbols."""
    out: dict[str, dict[str, list[str]]] = {}
    for inc in sorted(cpp_dir.glob("*/Inc")):
        for header in sorted(inc.glob("*.h")):
            rel = str(header.relative_to(cpp_dir))
            if rel in _SKIP_HEADERS:
                continue
            out[rel] = cpp_symbols(header)
    return out


def resolve_bare(bare: set[str], cpp: dict[str, dict[str, list[str]]]) -> None:
    """Attribute bare "UnMath.h"-style refs to any matching C++ header."""
    for name in bare:
        for rel in cpp:
            if rel.endswith("/" + name):
                # Can't tell which module cited it; record the survey itself.
                cpp[rel].setdefault("ported", True)


def survey(cpp_dir: Path) -> dict:
    header_to_py, bare = scan_python()
    cpp = scan_cpp(cpp_dir)
    resolve_bare(bare, cpp)

    ported: dict[str, list[str]] = {}
    unported: dict[str, dict[str, list[str]]] = {}
    for rel, symbols in cpp.items():
        citing = header_to_py.get(rel, [])
        if citing or symbols.get("ported"):
            ported[rel] = citing
        else:
            unported[rel] = symbols

    def subsystem(rel: str) -> str:
        return rel.split("/", 1)[0]

    core_pending = {r: s for r, s in unported.items() if subsystem(r) == "Core"}
    engine_pending = {r: s for r, s in unported.items() if subsystem(r) == "Engine"}
    other_pending = {
        r: s for r, s in unported.items() if subsystem(r) not in ("Core", "Engine")
    }
    return {
        "ported": ported,
        "core_pending": core_pending,
        "engine_pending": engine_pending,
        "other_pending": other_pending,
    }


def _symbol_count(symbols: dict[str, list[str]]) -> int:
    return sum(len(v) for v in symbols.values())


def print_report(result: dict) -> None:
    print(f"=== PORTED ({len(result['ported'])} headers) ===")
    for rel, modules in sorted(result["ported"].items()):
        print(f"  {rel} -> {', '.join(modules) or '(cited by filename only)'}")

    print(f"\n=== CORE PENDING ({len(result['core_pending'])} headers) ===")
    for rel, symbols in sorted(
        result["core_pending"].items(), key=lambda kv: -_symbol_count(kv[1])
    ):
        print(
            f"  {rel}  (classes={len(symbols['classes'])} "
            f"structs={len(symbols['structs'])} enums={len(symbols['enums'])})"
        )
        for kind in ("classes", "structs", "enums"):
            if symbols[kind]:
                print(f"      {kind}: {', '.join(symbols[kind])}")

    print(f"\n=== ENGINE PENDING ({len(result['engine_pending'])} headers) ===")
    for rel, symbols in sorted(
        result["engine_pending"].items(), key=lambda kv: -_symbol_count(kv[1])
    ):
        print(f"  {rel}  (symbols={_symbol_count(symbols)})")

    if result["other_pending"]:
        print(f"\n=== OTHER PENDING ({len(result['other_pending'])} headers) ===")
        for rel in sorted(result["other_pending"]):
            print(f"  {rel}")

    print("\n=== NEXT JOB ===")
    if result["core_pending"]:
        best = max(result["core_pending"].items(), key=lambda kv: _symbol_count(kv[1]))
        print(
            f"  Port Core header {best[0]} ({_symbol_count(best[1])} declared symbols)."
        )
    elif result["engine_pending"]:
        best = max(
            result["engine_pending"].items(), key=lambda kv: _symbol_count(kv[1])
        )
        print(
            f"  Core is done. Port Engine header {best[0]} "
            f"({_symbol_count(best[1])} declared symbols)."
        )
    else:
        print("  Nothing pending.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--cpp-dir",
        type=Path,
        default=DEFAULT_CPP_DIR,
        help="C++ source tree (default: ~/code/Ut99PubSrc)",
    )
    parser.add_argument("--json", action="store_true", help="emit the survey as JSON")
    args = parser.parse_args()

    if not args.cpp_dir.is_dir():
        parser.error(f"C++ tree not found: {args.cpp_dir}")

    result = survey(args.cpp_dir)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print_report(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
