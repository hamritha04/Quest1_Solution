from pathlib import Path
import subprocess


def extract_audio(
    video_path: str,
    output_dir: str = "output",
) -> str:

    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    audio_path = (
        output_path / "audio.wav"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(audio_path),
    ]

    try:

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
        )

    except subprocess.CalledProcessError as exc:

        raise RuntimeError(
            "FFmpeg audio extraction failed:\n"
            + exc.stderr
        ) from exc

    return str(audio_path)