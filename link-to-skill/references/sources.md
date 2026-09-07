# Source extraction recipes

Per-source extraction for the link-to-skill pipeline. Goal of every path:
clean text in the scratch dir (`/tmp/<task>-work/`), plus metadata worth
keeping (author, duration, chapters, engagement numbers if the user is
studying performance, not just content).

## X / Twitter

### Direct media URL (`video.twimg.com/...mp4`)

The URL 401s without headers. Download with curl, not yt-dlp:

```bash
curl -sL -H "Referer: https://x.com/" -H "User-Agent: <browser UA>" -o vid.mp4 "<twimg url>"
ffmpeg -y -v error -i vid.mp4 -ar 16000 -ac 1 audio.wav
whisper-cli -m ~/.local/share/whisper/ggml-large-v3.bin -f audio.wav -otxt -of trans -t 8 -l auto
```

- Only models already under `~/.local/share/whisper/` — never download new ones.
- Whisper writes output files only when the process exits. Wait for exit; do
  not tail partial files.
- For screen-content videos, grab frames and vision-check them:
  `ffmpeg -y -v error -ss 30 -i vid.mp4 -frames:v 1 frame1.jpg` (repeat at
  several offsets).
- Sanity check: transcript words ≈ duration_min × 130–190.

### Status URL (`x.com/<user>/status/<id>`)

```bash
curl -s "https://api.fxtwitter.com/<screen_name>/status/<tweet_id>"
```

Returns author, text, stats (replies/retweets/likes/bookmarks/views), and
`media.all[]` / `formats` — pick ~720p and download per the direct-URL recipe.
The numeric id in a `video.twimg.com` path is a media snowflake, NOT the tweet
id — the API needs the real status id from the tweet URL.

### Profile / timeline research

- `curl -s "https://api.fxtwitter.com/<screen_name>"` — bio, counts, join
  date, verification. No auth.
- `https://syndication.twitter.com/srv/timeline-profile/screen-name/<handle>`
  returns public timeline HTML with embedded JSON (`__NEXT_DATA__`): post
  text, like/retweet counts. Rate-limits quickly — one call, parse, move on.
- Replies and anything behind the login wall need a browser session that is
  actually logged in. If the host browser shows "Log in / Sign up", do not
  fight it — fall back to the public APIs and say the replies were not
  checked.

## YouTube

```bash
yt-dlp --no-update --list-subs "URL"                       # see what exists
yt-dlp --no-update --write-subs --sub-langs "en.*" --sub-format vtt --skip-download "URL"
yt-dlp --no-update --write-auto-subs --sub-langs "en.*" --sub-format vtt --skip-download "URL"
```

- Prefer human subs (`--write-subs`) over auto (`--write-auto-subs`).
- Flag is `--sub-format` (singular) — `--sub-formats` does not exist.
- Clean the VTT with `scripts/clean_captions.py`. NEVER flatten naively:
  auto-caption VTTs are rolling captions and triple the text (the `<c>`-tag
  filter in the script is the correct dedupe).
- No captions at all → `yt-dlp -x --audio-format wav "URL"` → whisper as above.
- Chapters for section structure: `yt-dlp --print "%(chapters)s" "URL"`.
- If yt-dlp extraction errors, update it first (`brew upgrade yt-dlp`) —
  old versions break on player changes.

## Articles / blogs / docs

Use the host's web fetch tool on the URL; for docs prefer raw source
(`raw.githubusercontent.com`, `?plain=1`). If fetch is blocked, try the
host browser; if still blocked, say so rather than summarizing a guess.

## Podcasts / audio / local files

- Direct audio URL or local file → whisper path above (extract audio with
  ffmpeg first for video files).
- `.vtt` / `.srt` files → `scripts/clean_captions.py <in> <out>`.
- Raw text → save to `<scratch>/raw.txt`, then clean and segment.

## Post-extraction checklist

- Word count within the 130–190 words/minute band; flag big deviations.
- Entity names are the #1 ASR casualty — list every proper noun, and
  web-search the correct spellings before distilling.
- If the transcript will be distilled by subagents: split at 1,500–3,000
  raw words per chunk, one chapter/section per worker. Oversized chunks die
  on generation timeouts even when the read fits.
