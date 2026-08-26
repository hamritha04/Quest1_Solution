from pathlib import Path

from src.audio import extract_audio
from src.asr import ASR
from src.search import (
    coarse_search,
    fine_search,
    precise_match,
)
from src.frame_extractor import (
    extract_frame,
)


class ExactFramePipeline:

    def __init__(self):

        self.asr = ASR(
            device="cpu",
            compute_type="int8",
        )

    def run(
        self,
        video_path: str,
        target_text: str,
    ):

        print(
            "\n"
            "================================"
        )
        print(
            "EXACT FRAME SEARCH"
        )
        print(
            "================================"
        )

        # -----------------------------
        # Audio
        # -----------------------------

        print(
            "\n[1] Extracting audio..."
        )

        audio_path = extract_audio(
            video_path
        )

        # -----------------------------
        # Coarse search
        # -----------------------------

        candidates = coarse_search(
            audio_path,
            target_text,
            self.asr,
            chunk_size=300,
            top_k=3,
        )

        if not candidates:

            raise RuntimeError(
                "No candidate regions found."
            )

        print(
            "\nTop coarse candidates:"
        )

        for candidate in candidates:

            print(
                f"{candidate['start']:.0f}s "
                f"score="
                f"{candidate['score']:.1f}"
            )

        # -----------------------------
        # Fine search
        # -----------------------------

        match = fine_search(
            audio_path,
            target_text,
            candidates,
            self.asr,
            chunk_size=60,
            overlap=10,
            threshold=70,
        )

        if match is None:

            raise RuntimeError(
                "Dialogue could not be found."
            )

        print(
            "\nCandidate dialogue:"
        )

        print(
            match["text"]
        )

        print(
            f"Candidate timestamp: "
            f"{match['start']:.3f}s"
        )

        # -----------------------------
        # Precision
        # -----------------------------

        match = precise_match(
            audio_path,
            target_text,
            match,
            self.asr,
        )

        print(
            f"Precise start: "
            f"{match['start']:.3f}s"
        )

        # -----------------------------
        # Frame
        # -----------------------------

        frame_path = (
            Path("output")
            / "identified_frame.jpg"
        )

        frame = extract_frame(
            video_path,
            match["start"],
            str(frame_path),
        )

        return {
            "timestamp": frame["timestamp"],
            "frame_number": frame[
                "frame_number"
            ],
            "text": match["text"],
            "image": frame["image"],
            "fps": frame["fps"],
            "confidence": match[
                "score"
            ],
        }