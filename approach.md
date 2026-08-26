Quest1 — Implementation Approach

1. Project Objective

The system accepts a publicly accessible video URL and a target spoken dialogue
sentence. It locates the occurrence of that sentence in the video's audio and
produces:

the timestamp of the identified frame

the frame number, where applicable

the extracted dialogue text

the corresponding video frame as an image

The target dialogue is audio speech, not text visually displayed on the
video.

Test video:

https://ok.ru/video/248244667877

Development target:

My mind rebels at stagnation

2. Initial Approach

The project began with a straightforward pipeline:

Public video URL
      ↓
Download video
      ↓
Extract audio
      ↓
Transcribe audio
      ↓
Search for target dialogue
      ↓
Extract corresponding frame

The first major concern was the cost of transcribing a long video. The test video
is approximately 54 minutes long, so performing a complete high-quality
transcription before searching for one known sentence would be inefficient.

This led to progressively more targeted processing.

3. Video Acquisition

The supplied video is hosted on OK.ru.

During development, ordinary requests could intermittently fail with connection
reset errors. yt-dlp with Chrome impersonation was tested successfully:

yt-dlp --impersonate chrome "https://ok.ru/video/248244667877"

The OK.ru extractor exposes the video as HLS with multiple quality levels.

The available representations included approximately:

192×144
320×240
480×360
640×480
960×720

The highest 960×720 representation is close to 1 GB, while the 640×480
representation is approximately 475 MB.

The 640×480 stream was successfully downloaded using:

python -m yt_dlp --impersonate chrome \
-f "best[height<=480]/best" \
--no-playlist \
-o "output\test_video.%(ext)s" \
"https://ok.ru/video/248244667877"

The download completed successfully and produced a usable MP4.

Current acquisition strategy

For the submitted version, the reliable path is:

Public URL
   ↓
yt-dlp + Chrome impersonation
   ↓
HLS video download
   ↓
Local video file

The downloader includes retry handling because the source/CDN can occasionally
reset connections.

4. Why Full Transcription Was Not Used

A complete transcription of a 54-minute video is unnecessary when the target
sentence is already known.

The initial full-transcription concept was therefore changed to a search-based
architecture.

Instead of:

54-minute audio
      ↓
full transcription
      ↓
search transcript

the system uses:

54-minute audio
      ↓
coarse localization
      ↓
candidate regions
      ↓
fine localization
      ↓
precise timestamp

This significantly reduces the amount of high-quality transcription required.

5. Coarse-to-Fine Search

The final working search system uses three levels of processing.

Stage 1 — Coarse Search

The audio is divided into approximately 5-minute regions.

A faster Whisper model (base) is used to identify which regions are likely to
contain the target sentence.

The target sentence is compared with recognized speech using fuzzy matching.

The coarse stage is intended only for localization. It does not need to produce
the final exact timestamp.

For the test sentence, the relevant region was correctly ranked first:

300s → 600s
score = 88.1
best text = My mind rebelled. It's stagnation.

Stage 2 — Fine Search

The strongest coarse candidate regions are searched using smaller overlapping
windows.

Configuration:

60-second chunks

10-second overlap

Whisper small

fuzzy text matching

Example:

300–360
350–410
400–460
...

The overlap is important because a sentence can cross a chunk boundary.

Early termination

Once a sufficiently strong match is found, the fine-search function immediately
returns the result.

Previously, the implementation continued searching later chunks even after the
target had already been identified. This was changed so that:

Target found
    ↓
return match
    ↓
stop searching

This avoids unnecessary transcription.

For the test video, the target was found at:

25.09s within the 300–360s fine-search chunk

with:

"My mind rebels at stagnation."
score = 100.0

Stage 3 — Precision Search

After the correct region is identified, word-level transcription is used to
obtain the precise dialogue timestamp.

The local timestamp within the selected chunk is converted into the video's
global timestamp.

For the development example:

Precise dialogue timestamp ≈ 325.090 seconds

6. Exact Frame Selection

Once the dialogue timestamp is known, the video FPS is read from the actual
video file.

The frame is selected using:

math.ceil(timestamp * fps)

rather than:

round(timestamp * fps)

The reason is that round() can select a frame that occurs slightly before
the detected dialogue timestamp.

The requirement is instead:

Select the first video frame whose timestamp is at or after the detected
dialogue timestamp.

For the development example:

Dialogue timestamp : ≈ 325.090 s
FPS                 : ≈ 23.976166
Frame               : 7795

The resulting image is:

output/identified_frame.jpg

7. Verified Output

The working local-video pipeline produced:

============================================================
FINAL RESULT
============================================================
Timestamp : 00:05:25.115
Frame     : 7795
Text      : "My mind rebels at stagnation."
Image     : output\identified_frame.jpg
FPS       : 23.976166
Confidence: 100.00
============================================================

This verifies the complete core processing path:

Video
 ↓
Audio
 ↓
Target dialogue localization
 ↓
Precise timestamp
 ↓
Frame number
 ↓
Image

8. Current Submitted Architecture

The version being submitted prioritizes reliability and demonstrated
functionality over an untested optimization.

The current architecture is:

                 PUBLIC VIDEO URL
                         │
                         ▼
              yt-dlp + Chrome impersonation
                         │
                         ▼
                  HLS download
                         │
                         ▼
                   Local MP4
                         │
                         ▼
                  Audio extraction
                         │
                         ▼
               5-minute coarse search
                   Whisper base
                         │
                         ▼
                 Candidate regions
                         │
                         ▼
              60-second fine search
                 10-second overlap
                   Whisper small
                         │
                         ▼
                  Target found
                         │
                         ▼
                Word-level precision
                         │
                         ▼
                 Dialogue timestamp
                         │
                         ▼
             First frame at/after timestamp
                         │
                         ▼
               identified_frame.jpg

This is the version that has been tested successfully.

9. Improvements to Coarse Matching

The current coarse stage can produce misleading scores for very short
utterances.

For example, generic speech such as:

"Yes."
"Indeed."
"Me?"
"No."

can receive relatively high fuzzy similarity scores despite not being meaningful
matches for a longer target sentence.

The current test run showed:

300s → 600s
score = 88.1
"My mind rebelled. It's stagnation."

600s → 900s
score = 66.7
"Indeed."

900s → 1200s
score = 66.7
"None."

1200s → 1500s
score = 66.7
"Yes."

The real target still ranked first, so this did not prevent successful detection,
but the matching strategy can be improved.

Planned improvements

A. Minimum candidate length

Ignore very short candidate transcripts during coarse matching.

For example, require a candidate to contain at least three words before
calculating its coarse score.

B. Neighboring-segment combination

Whisper can split a sentence into multiple segments:

"My mind rebels"
"at stagnation"

The search can also compare the combined neighboring text:

"My mind rebels at stagnation"

This reduces sensitivity to Whisper's segmentation boundaries.

C. Better candidate scoring

Future scoring can combine:

fuzzy similarity

word overlap

target-word coverage

candidate length

semantic similarity

This should reduce false positives caused by short generic utterances.

D. Retain multiple meaningful candidates

Instead of relying only on a raw similarity score, several meaningful candidate
regions can be retained for the fine-search stage.

This is safer when the target appears more than once or when ASR quality varies.

10. HLS Streaming / Partial-Data Processing — Future Scope

The OK.ru source exposes an HLS manifest consisting of many media fragments.

Therefore, the complete 475 MB video does not necessarily need to be downloaded
before searching.

A more efficient future architecture is:

                    PUBLIC URL
                         │
                         ▼
                  HLS manifest
                         │
                         ▼
                 Segment timeline
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       Small audio batches      Video segments
             │                       │
             ▼                       │
          Whisper                    │
             │                       │
             ▼                       │
       Target found ─────────────────┘
             │
             ▼
       Exact timestamp
             │
             ▼
     Corresponding video segment
             │
             ▼
        Exact frame

Advantages

lower temporary storage requirements

less unnecessary network transfer

earlier termination when the target is near the beginning

better scalability for very long videos

ability to process only the relevant media segments

Controlled parallelism

Small numbers of HLS segments can be processed concurrently.

A reasonable future design would use a small worker pool, for example:

Worker 1 → segment/batch A
Worker 2 → segment/batch B
Worker 3 → segment/batch C

Concurrency should remain controlled because the OK.ru source has demonstrated
intermittent connection resets. Excessive simultaneous requests could make the
network behavior less reliable rather than faster.

11. Full-Download Fallback

The HLS streaming approach should become the preferred mode in a future version,
but the existing full-download path should remain as a fallback.

Final desired architecture:

                     PUBLIC URL
                         │
                         ▼
                  Resolve source
                         │
                  HLS available?
                    /         \
                  YES          NO
                   │            │
                   ▼            ▼
          HLS streaming      Full download
          / partial mode       via yt-dlp
                   │            │
                   └─────┬──────┘
                         ▼
                   Audio search
                         │
                         ▼
                  Exact timestamp
                         │
                         ▼
                    Exact frame

This provides compatibility with sources that expose HLS as well as sources that
only provide downloadable media.

12. Future Robustness Improvements

Additional improvements include:

Multilingual speech

The current development target is English. Future versions could support
language detection and multilingual Whisper models.

Better error handling

The application should distinguish between:

invalid URL

inaccessible/private video

unsupported host

network failure

missing audio

target dialogue not found

video decoding failure

frame extraction failure

Repeated-dialogue handling

If the same sentence appears multiple times, the system could return all
matches or allow the user to request the first, last, or best-confidence
occurrence.

Evaluation across different positions

Testing should include targets:

near the beginning

near the middle

near the end

across chunk boundaries

with punctuation differences

with minor ASR transcription errors

in noisy audio

This would measure how well the coarse-to-fine architecture generalizes.

13. Final Status

At submission time, the implemented and tested functionality is:

✓ Public video acquisition through yt-dlp
✓ Chrome impersonation for the tested OK.ru source
✓ HLS video download
✓ Audio extraction
✓ Coarse 5-minute localization
✓ Fine 60-second overlapping search
✓ Early termination after target detection
✓ Fuzzy dialogue matching
✓ Word-level timestamp refinement
✓ First frame at/after dialogue timestamp
✓ Frame number calculation
✓ Extracted dialogue text
✓ Corresponding frame image
✓ Local-file processing fallback

The key verified result is:

Timestamp : 00:05:25.115
Frame     : 7795
Text      : "My mind rebels at stagnation."
Image     : output\identified_frame.jpg
Confidence: 100.00

The main future optimization is direct HLS segment processing, which can reduce
download size, storage usage, and time-to-first-result for long videos. It is
kept as future scope in the submitted version because the current full-download
pipeline has been tested end-to-end and is therefore the safer submission
baseline.