import os
import re
import subprocess
import tempfile

from rapidfuzz import fuzz


def normalize(text: str) -> str:

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text.strip()


def similarity(
    target: str,
    candidate: str,
) -> float:

    target = normalize(target)
    candidate = normalize(candidate)

    return max(
        fuzz.ratio(
            target,
            candidate,
        ),
        fuzz.partial_ratio(
            target,
            candidate,
        ),
        fuzz.token_set_ratio(
            target,
            candidate,
        ),
    )


def get_duration(
    audio_path: str,
) -> float:

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default="
        "noprint_wrappers=1:"
        "nokey=1",
        audio_path,
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=True,
    )

    return float(
        result.stdout.strip()
    )


def extract_chunk(
    audio_path: str,
    start: float,
    duration: float,
) -> str:

    fd, path = tempfile.mkstemp(
        suffix=".wav"
    )

    os.close(fd)

    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        audio_path,
        "-t",
        str(duration),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        path,
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return path


def coarse_search(
    audio_path,
    target_text,
    asr,
    chunk_size=300,
    top_k=3,
):
    """
    Search the complete audio using
    large 5-minute regions.

    Returns the top candidate regions.
    """

    total_duration = get_duration(
        audio_path
    )

    candidates = []

    position = 0.0

    print(
        "\n========== COARSE SEARCH =========="
    )

    while position < total_duration:

        start = position

        duration = min(
            chunk_size,
            total_duration - start,
        )

        print(
            f"Coarse chunk: "
            f"{start:.0f}s → "
            f"{start + duration:.0f}s"
        )

        chunk_path = extract_chunk(
            audio_path,
            start,
            duration,
        )

        try:

            segments, _ = asr.transcribe(
                chunk_path,
                model_size="base",
                word_timestamps=False,
            )

            best_score = 0.0

            best_text = ""

            for segment in segments:

                score = similarity(
                    target_text,
                    segment.text,
                )   

                if score > best_score:

                    best_score = score
                    best_text = segment.text

            print(
                f"  score = {best_score:.1f}"
            )

            print(
                f"  best text = "
                f"{best_text.strip()}"
            )

            score = best_score

            candidates.append({
                "start": start,
                "duration": duration,
                "score": score,
            })

        finally:

            os.remove(chunk_path)

        position += chunk_size

    candidates.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return candidates[:top_k]


def fine_search(
    audio_path,
    target_text,
    candidates,
    asr,
    chunk_size=60,
    overlap=10,
    threshold=70,
):
    """
    Search candidate regions using
    overlapping 60-second chunks.
    """

    print(
        "\n========== FINE SEARCH =========="
    )

    best_match = None

    step = (
        chunk_size - overlap
    )

    for candidate in candidates:

        region_start = candidate[
            "start"
        ]

        region_end = (
            candidate["start"]
            + candidate["duration"]
        )

        position = region_start

        while position < region_end:

            start = position

            duration = min(
                chunk_size,
                region_end - start,
            )

            if duration <= 0:
                break

            print(
                f"Fine chunk: "
                f"{start:.1f}s → "
                f"{start + duration:.1f}s"
            )

            chunk_path = extract_chunk(
                audio_path,
                start,
                duration,
            )

            try:

                segments, _ = asr.transcribe(
                    chunk_path,
                    model_size="small",
                    word_timestamps=True,
                )

                for segment in segments:

                    score = similarity(
                        target_text,
                        segment.text,
                    )

                    print(
                        f"  "
                        f"{segment.start:.2f}s "
                        f"'{segment.text.strip()}' "
                        f"score={score:.1f}"
                    )

                    if score >= threshold:

                        absolute_start = (
                            start + segment.start
                        )

                        absolute_end = (
                            start + segment.end
                        )

                        match = {
                            "text": segment.text.strip(),
                            "start": absolute_start,
                            "end": absolute_end,
                            "score": score,
                            "chunk_start": start,
                            "segment": segment,
                        }

                        print(
                            "\nTarget found!"
                        )

                        print(
                            f"Text: {match['text']}"
                        )

                        print(
                            f"Score: {score:.1f}"
                        )

                        print(
                            f"Timestamp: "
                            f"{absolute_start:.3f}s"
                        )

                        return match

            finally:

                os.remove(chunk_path)

            position += step

    return None


def precise_match(
    audio_path,
    target_text,
    match,
    asr,
):
    """
    Locate the first target word using
    word-level timestamps.
    """

    start = match["chunk_start"]

    duration = 60.0

    chunk_path = extract_chunk(
        audio_path,
        start,
        duration,
    )

    try:

        segments, _ = asr.transcribe(
            chunk_path,
            model_size="small",
            word_timestamps=True,
        )

        target_words = normalize(
            target_text
        ).split()

        best = None

        for segment in segments:

            if not segment.words:
                continue

            words = segment.words

            normalized_words = [
                normalize(word.word)
                for word in words
            ]

            for i in range(
                len(normalized_words)
            ):

                remaining = (
                    len(normalized_words)
                    - i
                )

                window_size = min(
                    len(target_words),
                    remaining,
                )

                candidate_words = (
                    normalized_words[
                        i:i + window_size
                    ]
                )

                candidate_text = (
                    " ".join(
                        candidate_words
                    )
                )

                target_prefix = (
                    " ".join(
                        target_words[
                            :window_size
                        ]
                    )
                )

                score = fuzz.ratio(
                    target_prefix,
                    candidate_text,
                )

                if (
                    best is None
                    or score > best["score"]
                ):

                    best = {
                        "score": score,
                        "word": words[i],
                    }

        if best is None:
            return match

        first_word = best["word"]

        match["start"] = (
            start + first_word.start
        )

        match["word_score"] = (
            best["score"]
        )

        return match

    finally:

        os.remove(chunk_path)