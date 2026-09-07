---
name: transcript-to-markdown
description: "Convert any transcript source — YouTube, audio or video files, VTT/SRT captions, or raw text — into a clean, readable markdown file. Use when the user asks for a transcript, clean transcript, full transcript in markdown, or wants captions, subtitles, or recordings converted to readable prose. Not for summaries."
platforms: [linux, macos, windows]
disable-model-invocation: true
---

# Transcript to Markdown

Convert a transcript from any common source into a polished, sectioned markdown file.

## When to use

Use this skill when the user wants:
- A transcript from a YouTube video, podcast, lecture, interview, or meeting recording.
- A clean markdown version of an existing `.vtt`, `.srt`, or raw text transcript.
- Captions or subtitles converted to flowing, paragraph-style prose.

Do not use for summaries, threads, or blog posts — use `youtube-content` or other content skills for those.

## Source routing

Pick the input source and use the matching extraction path.

| Input | First try | Fallback if first try fails |
|---|---|---|
| YouTube URL | `yt-dlp --list-subs URL`, then `--write-subs` (human-made) or `--write-auto-subs` | Download audio (`yt-dlp -x --audio-format wav`) and transcribe with local whisper.cpp |
| Audio file (mp3, wav, m4a, etc.) | Local whisper.cpp | — |
| Video file | Extract audio (`yt-dlp -x` or `ffmpeg -i file -vn -acodec pcm_s16le -ar 16000 -ac 1 out.wav`) then whisper.cpp | — |
| VTT/SRT file | `python3 scripts/clean_captions.py input.vtt output.txt` | — |
| Raw text file or pasted text | Read or save to a scratch file, then clean and segment | — |

For projectless chats use the scratch dir `./work/transcript-work`; otherwise use `/tmp/transcript-work`. Create the output dir `./outputs/` if it does not exist and the chat is projectless; otherwise write the final `.md` to `~/Downloads` or the project outputs directory the user names.

## Steps

1. **Collect the source material.**
   - For YouTube: note the URL and, if possible, the chapter list from the description (`yt-dlp --print "%(chapters)s" URL`).
   - For audio/video: locate the file path.
   - For VTT/SRT/text: read the file or save pasted text to `<scratch>/raw.txt`.

2. **Extract raw transcript text.**
   - YouTube: fetch captions with `yt-dlp --no-update --sub-langs "en.*" --sub-format vtt --skip-download URL`. Prefer `--write-subs` if human captions exist. If no captions, fall back to audio extraction + whisper.
   - Audio/video: run whisper.cpp with a model at `~/.local/share/whisper/` — never download new models unless the user already has them. Output raw text.
   - VTT/SRT: use `scripts/clean_captions.py` to dedupe and clean.
   - Raw text: write it to `<scratch>/raw.txt` as-is.

3. **Initial clean.**
   - Run `python3 scripts/clean_captions.py <input> <scratch>/cleaned.txt` for VTT/SRT.
   - For raw text/whisper output: remove obvious duplicate lines, fix broken punctuation, and insert paragraph breaks after sentence-ending punctuation.
   - Word-count sanity check: expect ~130–190 words per minute of content. Flag big deviations.

4. **Build section headers.**
   - Use YouTube chapters, user-provided timestamps, or detect natural topic shifts.
   - Format each section as `## Section Name (m:ss)` or `## Section Name` when no timestamp is known.
   - If no chapter list exists, split into ~1,500–3,000 word contiguous chunks and use generic headers like `## Part 1`, `## Part 2`, etc.

5. **Rewrite in parallel chunks.**
   - Never hand the whole transcript to a single subagent for long sources. Split into ~1,500–3,000 word raw ranges, one section or chapter per subagent.
   - For each chunk, spawn a subagent with:
     - input path and exact line range
     - chunk output path (e.g., `chunk1.md`)
     - exact list of `## Section Name (m:ss)` headers verbatim
     - shared style rules: read the whole range, fix ASR typos and entity names (use `web_search` for spellings), keep first-person voice, reproduce complete content (no summarizing), one paragraph per idea, light filler removal, start directly with the first `##` header (no title)
     - tell it not to delete the input file
     - pass shared context (entity spellings, book titles, speaker/channel) via the batch `context` field
     - never pass background knowledge about the subject; shared context = spelling conventions only
   - Redispatch failures at a smaller size (one chapter at a time) instead of retrying the same oversized chunk.

6. **Stitch the final file.**
   - Concatenate chunks in order.
   - Add a top `# Title` only if the source has a clear title (video title, filename, or user-provided).
   - Add a small footer note: `Transcript generated from <source type> on <date>` unless the user asks not to.
   - Verify cross-chunk spelling consistency (e.g., one agent may write "Sinara" while another writes "Synara").

7. **Verify the deliverable.**
   - The output `.md` exists and has all section headers.
   - Word count matches the expected ~130–190 words/minute.
   - Spot-check the first and last paragraphs of each chunk.

8. **Clean up.**
   - Delete the scratch dir (`rm -rf <scratch>`).
   - Remove any temporary whisper model or package installed specifically for this run.
   - The only surviving artifact is the final `.md`.

## Pitfalls

- Do not flatten VTT naively — rolling captions contain duplicated text. Always use `scripts/clean_captions.py` for caption files.
- `--sub-formats` (plural) is not a valid `yt-dlp` flag; use `--sub-format`.
- YouTube auto-captions and whisper ASR mangle entity names. The subagent rewrite pass is not optional.
- Old `yt-dlp` versions fail on new YouTube player changes. If extraction errors, update `yt-dlp` first (`brew upgrade yt-dlp` or `uv pip install -U yt-dlp`).
- Long transcripts die on a single subagent because of proxy timeouts. Fan out at chapter granularity; 3–4 chapter ranges still fail.
- Never pass incident background or prior-session knowledge into the rewrite brief. Use only the actual source.
