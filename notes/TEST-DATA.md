# Test Data for Voice Fingerprinting

**Last Updated:** 2026-02-19

---

## Primary Test File

**Video:**
```
/Volumes/2TB/Sync/Flat/Flerfs/C C/Videos/Think about it friday on our Flat-earth 2025-01-17.mp4
```

**Existing Transcript:**
```
/Volumes/2TB/Sync/Flat/Flerfs/C C/Videos/Think about it friday on our Flat-earth 2025-01-17.txt
```

### File Details
| Attribute | Value |
|-----------|-------|
| **Speaker** | Chris (Westchester County, New York) |
| **Duration** | ~16 minutes |
| **Speaker Count** | 1 (monologue) |
| **Audio Quality** | Real-world (driving, background noise, muffler sounds) |
| **Content Type** | Flat earth monologue |
| **Challenges** | Background traffic, car noise, intermittent speech |

### Transcript Format
The existing transcript uses this format:
```
Chris Westchester County  00:01
[Transcribed text...]

Chris Westchester County  08:10
[Transcribed text...]
```

**Note:** Transcript includes timestamps and speaker labels.

---

## Test Scenarios

### 1. Single Speaker Identification
- **Goal:** Verify system correctly identifies one speaker throughout
- **Expected:** Single speaker cluster (SPEAKER_00 or "Chris")
- **Challenge:** Background noise may cause false speaker splits

### 2. Real-World Audio Quality
- **Goal:** Test with non-studio audio (driving, wind, traffic)
- **Expected:** Reasonable accuracy despite noise
- **Benchmark:** Compare to MacWhisper/Whisper.cpp performance

### 3. Long-Form Transcription
- **Goal:** Handle 15+ minute audio files
- **Expected:** Complete transcription with timestamps
- **Performance:** Measure processing time vs real-time

### 4. Speaker Enrollment Test
- **Goal:** Extract voice fingerprint for "Chris"
- **Test:** Can system recognize this speaker in other videos?
- **Validation:** Use other C C videos for cross-identification

---

## Additional Test Resources

### Flerf Video Library
- **Location:** `/Volumes/2TB/Sync/Flat/Flerfs/` (21 folders) + YT Dropbox (687 folders)
- **Use:** Multiple speakers, varying audio quality, diverse content
- **Benefit:** Real-world test data for speaker diarization

### Suggested Test Cases

| Test | Source | Expected Result |
|------|--------|-----------------|
| Multi-speaker diarization | Mark Sargent debates | 2+ speakers identified |
| Noisy audio | Phone call recordings | VAD filters silence/noise |
| Short clips | < 30 seconds | Fast processing, speaker ID |
| Batch processing | 10+ files | Queue management, memory stability |

---

## Baseline Metrics to Capture

From test file processing:
- [ ] Processing time (minutes of audio / minutes of processing)
- [ ] Memory usage peak
- [ ] Speaker accuracy (vs manual transcript)
- [ ] Word Error Rate (WER)
- [ ] Diarization Error Rate (DER)

---

## Notes

- Existing transcript can serve as ground truth for accuracy testing
- Chris has distinctive speaking style (NY accent, flat earth terminology)
- Good candidate for speaker enrollment database
- Background noise makes this a challenging real-world test case

---

*Test data documented for development phase*

## Flerf Whisperer Update - 2026-03-05 **C C (Chris Westchester NY)**

**Status: RESOLVED / ENHANCED**

- Researched C C folder: 2000+ videos/transcripts available
- Confirmed Chris (NY accent, driving recordings)
- **New Test Resources:** All .txt files in Videos/ (ground truth, timestamps)
- Examples:
  | File | Notes |
  |------|-------|
  | (Rated R for language) Ricers rant... .txt | Angry rant, noisy |
  | 1100-200 on our Flat-earth.txt | Short monologue |
  | 1876 on our Flat-earth.txt | Historical claims |
  | 2025-03-29-"Lost technology" on our Flat-earth.txt | Recent, tech claims |

- **Recommendation:** Enroll "Chris Westchester County" as baseline speaker for DER/WER testing
- Flerf summary: /volumes/2tb/sync/flat/flerfs/C C/summary.md

**Collection Status: READY FOR BATCH PROCESSING**

## Flerf Whisperer Update - 2026-03-06 **Mark Sargent (Flat Earth Clues)**

**Status: ENHANCED / NEW TEST DATA**

- Researched `/Volumes/2tb/sync/flat/flerfs/Mark Sargent`: 1893 videos + transcripts
- **Identity Confirmed:** Mark Sargent, Seattle WA, FE pioneer
- **New Test Resources:**
  | File | Notes |
  |------|-------|
  | 2025-02-27-Flat Earth Clues interview 444 Texas high school classes 1 & 2 [5Kw3AldyYmk].txt | Interview, multi-speaker (Mark + students), 86KB, timestamps |
  | 2025-03-05-Strange World 502 Special guest Shane St Pierre - DJ Curious Lisbeth Acosta & Mark Sargent [kTaTA3bsUDw].txt | Podcast, multiple guests, 137KB |
  | 2025-02-14-Flat Earth Clues interview 443 Tin Foil Hat Sombrero [Utx7vrBfe7g].txt | Interview, 138KB |

- **Voice FP Recommendation:** Enroll "Mark Sargent" profile - distinctive voice, many samples
- **Summary:** /Volumes/2tb/sync/flat/flerfs/Mark Sargent/summary.md

**Collection Status: READY FOR BATCH PROCESSING**
