---
name: youtube-transcript-to-markdown
description: "Full YouTube transcript to polished markdown file."
platforms: [linux, macos, windows]
---

# YouTube Transcript to Polished Markdown

Full end-to-end workflow: pull a YouTube video's captions with yt-dlp, clean the
rolling-caption duplication, hand the raw text to a subagent for a full
read + fact-check + rewrite into a formatted markdown transcript, then delete
every intermediate artifact so only the final `.md` remains.

## When to use

User shares a YouTube URL and asks for the "full transcript", a "clean transcript",
or a markdown version of everything said in the video. Not for summaries (use
`youtube-content` for summaries/threads/blogs).

## Steps

1. **Fetch captions with yt-dlp** (work in a scratch dir like `/tmp/ytdlp-work`):

   ```bash
   mkdir -p /tmp/ytdlp-work && cd /tmp/ytdlp-work
   yt-dlp --no-update --write-auto-subs --sub-langs "en.*" --sub-format vtt \
     --skip-download "URL"
   ```

   Prefer `--write-subs` (human-made) over `--write-auto-subs` when available;
   check with `yt-dlp --list-subs URL`. If NO transcript exists at all, fall
   back to downloading audio (`yt-dlp -x --audio-format wav`) and transcribing
   with the local whisper.cpp install (see `local-audio-transcription` skill;
   models at `~/.local/share/whisper/` — never download new models).

2. **Clean the VTT.** Auto-caption VTTs are "rolling" captions: each cue repeats
   the previous line, so naive text extraction triples the text. Correct method:
   split on blank lines into cue blocks, keep ONLY blocks whose body contains
   inline timestamp tags (`<00:00:02.879><c> ...`), take the LAST line of each
   block, strip `<...>` tags, join with spaces. Header-duplicate blocks have no
   `<c>` tags — skipping them removes all duplication. Insert paragraph breaks
   after sentence-ending punctuation. Result should be ~word_count = duration_min
   x 130-190 (a 103-min video ≈ 19-20K words). See `scripts/clean_vtt.py`.

3. **Get the chapter list** from the video description (the URL context or
   `yt-dlp --print "%(chapters)s" URL`). Use chapters as the `##` section headers.

4. **Delegate the rewrite to PARALLEL chunk subagents, never one.** A single
   subagent asked to read 100K+ chars and rewrite ~20K words in one context
   dies: the assemble-then-write step exceeds the API proxy read timeout
   (observed HTTP 524 after ~18 min, zero output written). Instead compute
   per-chapter line boundaries (map chapter timestamps to cumulative word
   count, words-per-second ≈ total_words / duration_sec), split into 3-5
   contiguous ranges, and fan out one subagent per range with delegate_task
   `tasks=[...]`. KEEP RANGES SMALL: one chapter per subagent (1,500-3,000
   words raw). A 3-4 chapter range (~5-6K words) still dies on the same 524 —
   the long generation after reading blows the 120s proxy window even when the
   read phase fits. Expect roughly 1 success in 4 for oversized chunks and
   redispatch failures at chapter granularity instead of retrying the same
   size. Each writes ONLY its own chunk file (e.g. chunk1.md) in the
   scratch dir. You then stitch chunks + title header + footer note yourself.
   Each chunk brief must include:
   - input path + its exact line range + its chunk output path
   - its exact list of `## Chapter Name (m:ss)` headers, verbatim, in order
   - shared style rules: read the WHOLE range by paging, fix ASR typos and
     entity names (web_search for spellings), keep first-person voice,
     reproduce COMPLETE content (no summarizing), paragraph per idea, light
     filler removal, start directly with the first ## header (no title)
   - tell it NOT to delete the input file (orchestrator does cleanup)
   - pass shared context (entity spellings, book titles, speaker/channel) via
     the batch `context` field so all 4 writers stay consistent

5. **Verify the deliverable yourself.** Check the output file exists, has all
   chapter headers, and the word count matches expectation. Subagent reports
   are self-reports — spot-check the actual file.

6. **Clean up everything else.** `rm -rf /tmp/ytdlp-work` (the VTT, cleaned
   txt, any audio). If a fallback whisper model or package was installed
   specifically for this run and the user didn't have it before, remove it.
   The ONLY surviving artifact is the markdown file in Downloads.

## Pitfalls

- **Never flatten VTT naively** — you get 3x duplicated text (59K words for a
  20K-word video). The `<c>`-tag filter in step 2 is the reliable dedupe.
- `--sub-formats` (plural) is not a valid yt-dlp flag — it's `--sub-format`.
- YouTube auto-captions mangle entity names ("moes" for "moats", wrong brand
  names) — the subagent rewrite pass is not optional.
- Old yt-dlp versions fail on new YouTube player changes; if extraction errors,
  update yt-dlp first (`brew upgrade yt-dlp` or `uv pip install -U yt-dlp`).
- Set explicit expectations on subagent output size: a full 2-hour transcript
  rewrite is ~110K chars; the child may need to assemble it in chunks.
