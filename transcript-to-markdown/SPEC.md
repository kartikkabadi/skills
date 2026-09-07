# Transcript to Markdown Specification

## Intent

Turn spoken-word content from any common source into a clean, readable, sectioned markdown transcript. The skill is source-agnostic: YouTube, local audio/video, caption files, and raw text all flow through the same cleaning, segmenting, and rewriting pipeline.

## Scope

In scope:
- Extracting and cleaning transcripts from YouTube URLs, audio files, video files, VTT/SRT captions, and raw text.
- Deduplicating rolling captions.
- Segmenting by chapters, timestamps, or natural word-count boundaries.
- Rewriting chunks in parallel with subagents for accuracy and consistency.
- Verifying and cleaning up intermediate artifacts.

Out of scope:
- Summaries, threads, blog posts, or other derivative content.
- Translation.
- Real-time/live transcription.

## Users and trigger context

- Primary users: anyone who wants a readable markdown version of spoken content.
- Should trigger for: "transcript", "clean transcript", "full transcript", "captions to markdown", "subtitles to markdown", "podcast transcript", "meeting transcript".
- Should not trigger for: "summary", "thread", "blog post", "translate".

## Runtime contract

- Required first actions: identify input source, choose extraction path, run `scripts/clean_captions.py` if the input is VTT/SRT.
- Required outputs: a single final `.md` file with section headers and cleaned prose.
- Non-negotiable constraints: delete all intermediate artifacts; do not pass background knowledge into rewrite briefs; keep subagent chunks at 1,500–3,000 raw words.
- Expected bundled files loaded at runtime: `scripts/clean_captions.py`.

## Source and evidence model

Authoritative sources:
- User-provided source file or URL.
- Captions or ASR output from yt-dlp/whisper.

Useful improvement sources:
- positive examples: well-formatted markdown transcripts with correct entity names.
- negative examples: 3x duplicated VTT text, oversized single-subagent rewrites that timeout.
- validation results: word count and header checks after stitching.

Data that must not be stored:
- secrets, API keys, or private credentials.
- unrelated user files copied into the scratch dir.

## Reference architecture

- `SKILL.md` contains: trigger language, source-routing table, ordered workflow, pitfalls.
- `SPEC.md` contains: this contract.
- `SOURCES.md` contains: provenance and change notes.
- `scripts/` contains: `clean_captions.py` for VTT/SRT deduplication and formatting.

## Validation

- Lightweight validation: run `scripts/clean_captions.py` on a sample VTT and SRT; verify no duplication and paragraph breaks are inserted.
- Deeper validation: end-to-end run on a short YouTube video or audio file; verify final `.md` matches expected word count and headers.
- Holdout examples: long multi-chapter video, plain SRT with formatting tags, whisper output with no chapters.
- Acceptance gates: final `.md` exists; all section headers present; intermediate files removed.

## Known limitations

- Requires `yt-dlp` and optionally whisper.cpp for non-caption sources.
- ASR quality depends on the local whisper model; no new models are downloaded automatically.
- Parallel chunk rewrites can diverge on entity spelling; the orchestrator must unify them.

## Maintenance notes

- Update `SKILL.md` when a new source type or extraction tool becomes common.
- Update `SOURCES.md` when provenance or change rationale is added.
- Update `scripts/clean_captions.py` when new caption formats need handling.
