#!/usr/bin/env python3
"""Clean a YouTube rolling-caption VTT into deduplicated flowing prose.

Usage: python3 clean_vtt.py input.vtt output.txt

Method: YouTube auto-caption VTTs duplicate every line twice (once as a plain
header line, once with inline <timestamp><c> word tags). Keeping only blocks
whose body contains '<' tags, and taking the last line of each, yields the
complete stream with zero duplication.
"""
import re
import sys


def main():
    raw = open(sys.argv[1], encoding="utf-8").read()
    blocks = re.split(r"\n\s*\n", raw)
    segments = []
    for b in blocks:
        lines = b.split("\n")
        if not any("-->" in l for l in lines):
            continue
        body = [l for l in lines if "-->" not in l]
        if not any("<" in l for l in body):
            continue  # header-duplicate block
        text = re.sub(r"<[^>]+>", " ", body[-1])
        text = re.sub(r"\s+", " ", text).strip()
        if text:
            segments.append(text)

    full = " ".join(segments)
    # paragraph breaks after sentence-ending punctuation
    full = re.sub(r"(?<=[.!?]) (?=[A-Z0-9\"'$])", "\n\n", full)

    with open(sys.argv[2], "w", encoding="utf-8") as f:
        f.write(full)
    print(f"segments={len(segments)} words={len(full.split())} chars={len(full)}")


if __name__ == "__main__":
    main()
