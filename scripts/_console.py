"""Shared console/stdio setup for the deep-research CLI scripts.

Every script in this directory prints status text that mixes UTF-8 emoji
markers (checking/pass/fail/warning glyphs) with report titles/citations in
whatever language the report happens to be in. On Windows, Python's default
stdout/stderr encoding for a script launched as `python script.py` is the
console's active code page (frequently cp1252), not UTF-8 — so the very
first non-cp1252 character written (an emoji, a CJK title, Cyrillic, Arabic,
Slovak diacritics, ...) raises `UnicodeEncodeError` and kills the process.

`ensure_utf8_console()` reconfigures stdout/stderr to UTF-8 in-process, so
these scripts behave the same on Windows as they do on macOS/Linux without
requiring callers to set `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8` first
(previously undocumented workarounds this repo's own docs never mention).

Call it once, first thing inside `if __name__ == "__main__":`, before any
printing happens.
"""

import sys


def ensure_utf8_console() -> None:
    """Force stdout/stderr to UTF-8 if the interpreter didn't already pick
    it (e.g. `PYTHONUTF8=1` is set, or the platform defaults to UTF-8).

    `TextIOWrapper.reconfigure` was added in Python 3.7; every script in
    this repo already relies on 3.9+ syntax (e.g. `list[dict]` generics),
    so no version guard is needed. Wrapped in try/except regardless since
    a stream that isn't a real TextIOWrapper (e.g. redirected/piped in an
    unusual host) should degrade to default behavior, not crash the CLI
    before it even runs.
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
