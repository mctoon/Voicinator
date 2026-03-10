# Quickstart: 007 Web UI to Identify Unknown Speakers

**Feature**: 007-webui-to-identify-unknown-speakers

## What this feature does

- Adds a **list of all videos** that need speaker identification (any media in "Videos 5 needs speaker identification" across all channel folders).
- For each video you can open an **identification view**: transcript with **click-to-play** (click a word or segment to play from that time), and a **side list of unidentified speakers** (from diarization).
- For each unidentified speaker you can: **assign to an existing speaker**, **create a new speaker** (type a name), or **choose not to identify** (system creates a full speaker record with a unique placeholder name, e.g. Unidentified-1; that speaker’s corpus and media linking work the same as for a named speaker).
- If the system can **suggest** an existing speaker (e.g. from a previous identification), you see the suggestion and can **confirm or change** it; on confirm, the current video’s passages are added to that speaker’s corpus.
- When **all speakers are resolved**, a **"Complete identification"** button is enabled. Clicking it:
  - Backs up the current transcript files (transcript.txt, transcript_words.json) under new names in the paired folder.
  - Rewrites transcript.txt and transcript_words.json with the resolved speaker names (or placeholders).
  - Moves the video and its paired folder to **"Videos 6 speakers matched"**.
  - Takes you back to the list (the completed video no longer appears).
- **Videos with no speakers** (e.g. no speech) are moved to step 6 immediately and do not appear in the list.

## How to use it (end user)

1. Open the web UI and go to the **Unknown Speakers** section (or equivalent).
2. You see a **list of videos** that need identification (channel + filename).
3. **Click a video** to open the identification view.
4. Use the **transcript** to click a section and **play from that point**; use the **side list** to resolve each unidentified speaker (existing / new / placeholder, or confirm a suggestion).
5. When every speaker is resolved, click **"Complete identification"**.
6. You are returned to the list; the completed video is moved to "Videos 6 speakers matched" and its transcript files are updated with speaker names.

## Technical notes (developer)

- **Backend**: Extend `pipelineSpeakersRoutes` with GET transcript, POST complete; extend `speakerResolver` for placeholder name generation (global counter) and suggested ID; add transcript backup+rewrite before move.
- **Frontend**: Extend `unknownSpeakersPage` with transcript panel, click-to-play (media currentTime), and Complete button that calls POST complete then navigates back.
- **Contracts**: See `specs/007-webui-to-identify-unknown-speakers/contracts/007-unknown-speakers-api.md` for API details.
- **Data**: Transcript files live in the paired folder; backup names (e.g. transcript_pre_speaker_id.txt) created before overwrite. Placeholder names: Unidentified-1, Unidentified-2, … (no spaces, globally unique).
- **Navigate away without completing**: If you leave the identification view without clicking "Complete identification", the video stays in "Videos 5 needs speaker identification". Resolutions (assignments, new speakers, placeholders) are persisted in the resolver; you can return to the same video later and finish. No move or transcript rewrite occurs until you click Complete.
