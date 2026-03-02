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
