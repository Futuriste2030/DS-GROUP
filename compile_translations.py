"""Compile locale/*/LC_MESSAGES/django.po -> django.mo (stdlib only).

Usage:  python compile_translations.py
(no gettext needed — same role as `django-admin compilemessages`).
"""
import struct
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOCALE = BASE / "locale"


def parse_po(path):
    entries = {}
    msgid = msgstr = None
    section = None  # 'id' | 'str'
    fuzzy = False

    def flush():
        nonlocal msgid, msgstr, fuzzy
        if msgid is not None and msgstr is not None and not fuzzy:
            entries[msgid] = msgstr
        msgid = msgstr = None
        fuzzy = False

    def unescape(s):
        return (
            s.replace("\\\\", "\\")
            .replace('\\"', '"')
            .replace("\\n", "\n")
            .replace("\\t", "\t")
            .replace("\\r", "\r")
        )

    with open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                flush()
                section = None
                continue
            if line.startswith("#"):
                if "fuzzy" in line:
                    fuzzy = True
                continue
            if line.startswith("msgid"):
                flush()
                section = "id"
                msgid = unescape(line[5:].strip().strip('"'))
                continue
            if line.startswith("msgstr"):
                section = "str"
                msgstr = unescape(line[6:].strip().strip('"'))
                continue
            if line.startswith('"') and line.endswith('"'):
                chunk = unescape(line[1:-1])
                if section == "id" and msgid is not None:
                    msgid += chunk
                elif section == "str" and msgstr is not None:
                    msgstr += chunk
    flush()
    return entries


def write_mo(entries, path):
    keys = sorted(entries.keys())
    offsets = []
    ids = strs = b""
    for k in keys:
        kb = k.encode("utf-8")
        vb = entries[k].encode("utf-8")
        offsets.append((len(ids), len(kb), len(strs), len(vb)))
        ids += kb + b"\x00"
        strs += vb + b"\x00"
    n = len(keys)
    keystart = 7 * 4 + 16 * n
    valuestart = keystart + len(ids)
    koffsets = []
    voffsets = []
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
    out = struct.pack(
        "Iiiiiii", 0x950412DE, 0, n, 7 * 4, 7 * 4 + n * 8, 0, 0
    )
    out += struct.pack("i" * n * 2, *koffsets)
    out += struct.pack("i" * n * 2, *voffsets)
    out += ids + strs
    with open(path, "wb") as f:
        f.write(out)


def main():
    ok = True
    for po in sorted(LOCALE.glob("*/LC_MESSAGES/django.po")):
        try:
            entries = parse_po(po)
            translatable = {k: v for k, v in entries.items() if k}
            mo = po.with_suffix(".mo")
            write_mo(entries, mo)
            print(f"OK  {po.relative_to(BASE)}: {len(translatable)} entries -> {mo.name}")
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"FAIL {po}: {e}", file=sys.stderr)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
