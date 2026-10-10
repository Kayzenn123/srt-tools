#!/usr/bin/env python3
"""srt-tools — small subtitle utilities. Pure Python, no dependencies.

Commands:
    shift   move all timestamps by +/- seconds   (fix out-of-sync subs)
    merge   join several .srt files, renumbered  (multi-part movies)
    renum   renumber entries starting at N        (fix broken numbering)
    strip   remove <i>/<b>/<font> tags           (clean formatting)

Usage:
    python srttools.py shift in.srt out.srt --seconds 1.5
    python srttools.py merge out.srt part1.srt part2.srt
    python srttools.py renum in.srt out.srt --start 1
    python srttools.py strip in.srt out.srt
"""

import argparse
import re
import sys

TS = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*"
                r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")
TAG = re.compile(r"</?(i|b|u|font)( [^>]*)?>", re.IGNORECASE)


def to_ms(h, mi, s, ms):
    return ((int(h) * 3600 + int(mi) * 60 + int(s)) * 1000 + int(ms))


def to_ts(ms):
    ms = max(0, int(round(ms)))
    h, ms = divmod(ms, 3600000)
    mi, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{mi:02d}:{s:02d},{ms:03d}"


def parse(path):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read().strip()
    entries = []
    for block in re.split(r"\n\s*\n", text):
        lines = block.strip().splitlines()
        if len(lines) < 2:
            continue
        m = TS.match(lines[1].strip())
        if not m:
            continue
        start = to_ms(*m.groups()[:4])
        end = to_ms(*m.groups()[4:])
        num = lines[0].strip() if lines[0].strip().isdigit() else None
        entries.append({"num": num, "start": start, "end": end,
                        "text": lines[2:]})
    return entries


def write(entries, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, e in enumerate(entries, 1):
            f.write(f"{i}\n{to_ts(e['start'])} --> {to_ts(e['end'])}\n")
            f.write("\n".join(e["text"]) + "\n\n")
    print(f"wrote {len(entries)} entries -> {path}")


def cmd_shift(args):
    entries = parse(args.input)
    delta = int(round(args.seconds * 1000))
    for e in entries:
        e["start"] += delta
        e["end"] += delta
    write(entries, args.output)


def cmd_merge(args):
    entries = []
    for path in args.inputs:
        entries.extend(parse(path))
    entries.sort(key=lambda e: e["start"])
    write(entries, args.output)


def cmd_renum(args):
    entries = parse(args.input)
    write(entries, args.output)  # write() always renumbers sequentially


def cmd_strip(args):
    entries = parse(args.input)
    for e in entries:
        e["text"] = [TAG.sub("", line) for line in e["text"]]
    write(entries, args.output)


def main():
    ap = argparse.ArgumentParser(description="srt-tools — subtitle utilities")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("shift", help="shift timestamps by seconds (+/-)")
    p.add_argument("input"); p.add_argument("output")
    p.add_argument("--seconds", type=float, required=True)

    p = sub.add_parser("merge", help="merge multiple srt files")
    p.add_argument("output"); p.add_argument("inputs", nargs="+")

    p = sub.add_parser("renum", help="renumber entries sequentially")
    p.add_argument("input"); p.add_argument("output")

    p = sub.add_parser("strip", help="strip html-ish formatting tags")
    p.add_argument("input"); p.add_argument("output")

    args = ap.parse_args()
    {"shift": cmd_shift, "merge": cmd_merge,
     "renum": cmd_renum, "strip": cmd_strip}[args.cmd](args)


if __name__ == "__main__":
    main()
