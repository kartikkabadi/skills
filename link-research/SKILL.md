---
name: link-research
description: "Use when user drops a link to research it (X, YT, article)."
version: 1.0.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [media, research, x, youtube, transcription, replies]
    related_skills: [youtube-transcript-to-markdown, captionless-video-transcript, xurl, ego-browser, hygiene]
platforms: [linux, macos, windows]
---

# Link -> Full Research + TLDR

One proactive pipeline for any link the user drops. No clarifying questions. Deliver the full research, then a TLDR, then clean up.

## When to Use

- User drops a bare URL (X/Twitter, YouTube, TikTok, article, podcast) and wants it watched, summarized, or researched.
- User asks to "check the replies", "research everything", or "watch and summarise" a link.
- User wants the full picture plus a short TLDR, with cleanup handled automatically.

## Pipeline

1. Classify the link.
2. Extract the source content.
3. Transcribe video/audio.
4. Pull the surrounding conversation (replies, quotes).
5. Research the topic (web + ego-browser).
6. Deliver full research + TLDR in wait-what style.
7. Clean up everything except the deliverable.

## 1. Classify

- `x.com`, `twitter.com`, `t.co` -> X path.
- `youtube.com`, `youtu.be` -> YT path.
- anything else -> web_extract, or download + whisper if it is media.

## 2. X path (no auth needed for metadata)

Get tweet JSON:

```bash
curl -s "https://api.fxtwitter.com/<screen_name>/status/<tweet_id>"
```

Read: author, tweet text, stats (replies/retweets/likes/bookmarks/quotes/views), `media.all[0]` (duration, width/height), `formats` (pick 720p).

Download the video with curl, NOT yt-dlp (yt-dlp -f fails on direct twimg URLs with "Requested format is not available"):

```bash
curl -sL -H "Referer: https://x.com/" -H "User-Agent: <browser UA>" -o vid.mp4 "<720p twimg URL>"
```

Background the download with notify_on_complete. Extract audio:

```bash
ffmpeg -y -v error -i vid.mp4 -ar 16000 -ac 1 audio.wav
```

Transcribe (output files appear only when the process EXITS, poll/wait, do not tail):

```bash
whisper-cli -m ~/.local/share/whisper/ggml-large-v3.bin -f audio.wav -otxt -of trans -t 8 -l auto
```

Never download new whisper models. Only `ggml-large-v3.bin` at `~/.local/share/whisper/`.

Grab frames for screen content, then vision_analyze them:

```bash
ffmpeg -y -v error -ss 30 -i vid.mp4 -frames:v 1 frame1.jpg   # repeat at 30/90/150s
```

Sanity-check transcript: word_count ~= duration_min x 130-190.

## 3. X replies (ego-browser, logged-in session)

The `twitter` CLI and `xurl` may not be installed or authenticated. ego-browser reuses the user's browser login. Open the tweet, click "Show probable spam" (reveals hidden replies), then scroll-and-accumulate into a window Set — X virtualizes the DOM so article counts drop as you scroll; that is virtualization, not data loss:

```js
// ego-browser nodejs: accumulate, then dump once at the end
await js(`window.__seen = new Set(); window.__allReplies = []`)
// loop: js( scroll to bottom ), wait, collect new article innerText, dedupe
```

## 4. YT path

```bash
yt-dlp --no-update --write-subs --sub-langs "en.*" --sub-format vtt --skip-download "<url>"   # prefer human subs
```

If none exist: `--write-auto-subs`. Clean the VTT with the dedupe script (rolling captions triple naive extraction):

```bash
python3 /Users/user/.hermes/skills/media/youtube-transcript-to-markdown/scripts/clean_vtt.py
```

No subs at all -> `yt-dlp -x --audio-format wav` + whisper (step 2 flags). Get chapters for section headers: `yt-dlp --print "%(chapters)s" <url>`.

## 5. Research the topic

- 2-3 web_search queries on the subject + named entities (verify spellings).
- ego-browser on official docs / repo pages; pull raw design docs via `raw.githubusercontent.com`.
- SOURCE FIDELITY RULE (user correction, non-negotiable): the transcript/summary of the source contains ONLY what the source says. Never inject background from memory, prior sessions, or the user's projects. Context passed to helpers = spelling conventions only, nothing else.
- Never post, reply, or quote on X without explicit approval (standing rule).

## 6. Deliverable

Full research first: what the link says (source-faithful), the replies/conversation digest, topic research with sources. Then the TLDR — wait-what style:

- ASD-STE100 Simplified Technical English.
- Plain words, short sentences, one idea per sentence.
- Active voice, present tense.
- No idioms, no metaphors, no buzzwords.
- Keep it to a few lines: what it is, the key claim, why it matters, what you did.

End with: what changed, what was verified, what remains.

## 7. Cleanup (hygiene)

- `rm -rf` the scratch dir (`/tmp/<task>-work`).
- Close ego-browser tabs you opened.
- Kill/verify background processes exited.
- No files in home dir or repos unless asked. The chat reply IS the deliverable.

## Pitfalls

- twimg 401 without Referer + UA is expected, not a dead link.
- X video duration from fxtwitter is in seconds (178.133 = ~3 min).
- Media snowflake ID in twimg path is NOT the tweet ID; use the full tweet URL for fxtwitter.
- X GraphQL internal API calls from page context fail without op IDs — do not rabbit-hole there; scroll the page instead.
- Subagent self-reports are not verification: spot-check files, word counts, headers yourself.
- Strong-accent ASR mangles entity names; the rewrite/fact-check pass is mandatory.
