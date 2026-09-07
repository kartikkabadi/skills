# Sources

## Source adaptation

This skill adapts the user-provided `youtube-transcript-to-markdown` workflow into a source-agnostic transcript-to-markdown skill.

| Decision | Record |
|---|---|
| Source intent | Convert YouTube captions into a polished, sectioned markdown transcript using yt-dlp, VTT cleaning, parallel subagent rewrites, and cleanup. |
| Local target | Generalize the same pipeline to any transcript source: YouTube URL, audio/video files, VTT/SRT files, or raw text. |
| Fidelity boundary | The parallel-chunk rewrite, word-count sanity check, and cleanup rules remain the same. The VTT `<c>`-tag dedupe method is preserved. |
| Local replacement | Source detection/routing table replaces the YouTube-only extraction step. `scripts/clean_captions.py` replaces `scripts/clean_vtt.py` and adds SRT support. Output location is generalized from YouTube/Downloads to project or user output dirs. |
| Omitted material | Nothing omitted; the YouTube path is kept as one row in the routing table. |
| Provenance | `~/.claude/skills/youtube-transcript-to-markdown/SKILL.md` and `~/.agents/skills/youtube-transcript-to-markdown/SKILL.md`, user-provided. |
| Rights and attribution | User's own work; no external license. |

## Changelog

- 2026-08-29: Initial skill created.
