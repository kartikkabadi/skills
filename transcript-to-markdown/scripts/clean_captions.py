#!/usr/bin/env python3
"""Clean a rolling-caption VTT or SRT file into flowing prose.

Usage: python3 clean_captions.py <input.vtt|input.srt> [output.txt]

YouTube auto-caption VTTs duplicate each line once as a plain "header" cue and
once with inline <timestamp><c> word tags. Keeping only blocks whose body
contains inline tags and taking the last line of each block removes the
duplication. SRT files have no duplication; this script joins their text lines
and strips any formatting tags.
"""
import re
import sys
from pathlib import Path


def clean_vtt(text: str) -> tuple[str, int]:
    blocks = re.split(r"\n\s*\n", text.strip())
    segments = []
    for b in blocks:
        lines = b.splitlines()
        if not any("-->" in l for l in lines):
            continue
        body = [l for l in lines if "-->" not in l]
        # A cue with actual word tags contains inline <...><c> markup.
        if not any("<c" in l or re.search(r"<\d{2}:\d{2}:\d{2}\.\d+", l) for l in body):
            continue
        text_line = re.sub(r"<[^>]+>", " ", body[-1])
        text_line = re.sub(r"\s+", " ", text_line).strip()
        if text_line:
            segments.append(text_line)
    return " ".join(segments), len(segments)


def clean_srt(text: str) -> tuple[str, int]:
    blocks = re.split(r"\n\s*\n", text.strip())
    segments = []
    for b in blocks:
        lines = b.splitlines()
        if len(lines) < 3:
            continue
        # Drop the numeric cue id and the timecode line; keep everything else.
        text_lines = []
        for line in lines:
            if line.strip().isdigit():
                continue
            if "-->" in line:
                continue
            text_lines.append(line)
        text_line = " ".join(text_lines)
        text_line = re.sub(r"<[^>]+>", " ", text_line)
        text_line = re.sub(r"\s+", " ", text_line).strip()
        if text_line:
            segments.append(text_line)
    return " ".join(segments), len(segments)


def insert_paragraphs(text: str) -> str:
    # Paragraph breaks after sentence-ending punctuation before a capital, number, or quote.
    return re.sub(r"(?<=[.!?]) (?=[A-Z0-9\"'$])", "\n\n", text)


def detect_format(path: Path, text: str) -> str:
    ext = path.suffix.lower()
    if ext == ".vtt" or text.strip().startswith("WEBVTT"):
        return "vtt"
    if ext == ".srt":
        return "srt"
    # Fallback: if we see "WEBVTT" cue tags, treat as VTT; otherwise SRT.
    if "<c" in text or re.search(r"<\d{2}:\d{2}:\d{2}\.\d+", text):
        return "vtt"
    return "srt"


def main():
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <input.vtt|input.srt> [output]", file=sys.stderr)
        sys.exit(1)

    inp = Path(sys.argv[1])
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    text = inp.read_text(encoding="utf-8", errors="replace")

    fmt = detect_format(inp, text)
    if fmt == "vtt":
        raw, seg_count = clean_vtt(text)
    else:
        raw, seg_count = clean_srt(text)

    result = insert_paragraphs(raw)

    if out:
        out.write_text(result, encoding="utf-8")
    else:
        print(result)

    word_count = len(result.split())
    print(
        f"format={fmt} segments={seg_count} words={word_count} chars={len(result)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
