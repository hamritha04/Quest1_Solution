from pathlib import Path
import subprocess
import sys


def download_video(
    url: str,
    output_dir: str = "output",
) -> str:
    """
    Download a publicly accessible video using yt-dlp.

    yt-dlp is invoked through the Python interpreter so that
    the same environment and dependencies are used.

    Chrome impersonation is enabled because some video hosts,
    including the tested OK.ru URL, require browser-like
    TLS/network behavior.
    """

    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_template = (
        output_path / "video.%(ext)s"
    )

    command = [
        sys.executable,
        "-m",
        "yt_dlp",

        # Browser impersonation.
        "--impersonate",
        "chrome",

        # Don't download playlists.
        "--no-playlist",

        # Prefer a reasonably sized video.
        "-f",
        "best[height<=480]/best",

        # Network resilience.
        "--retries",
        "10",

        "--fragment-retries",
        "10",

        # Continue partial downloads.
        "--continue",

        # Output path.
        "-o",
        str(output_template),

        url,
    ]

    print(
        "\nDownloading video with yt-dlp..."
    )

    print(
        "Chrome impersonation: enabled"
    )

    try:

        subprocess.run(
            command,
            check=True,
        )

    except subprocess.CalledProcessError as exc:

        raise RuntimeError(
            "yt-dlp failed to download "
            "the supplied video URL.\n"
            f"URL: {url}\n"
            f"Exit code: {exc.returncode}"
        ) from exc

    # Find the resulting video.
    candidates = sorted(
        output_path.glob(
            "video.*"
        )
    )

    video_candidates = [
        path
        for path in candidates
        if path.suffix.lower()
        in {
            ".mp4",
            ".mkv",
            ".webm",
            ".mov",
            ".avi",
            ".ts",
        }
    ]

    if not video_candidates:

        raise RuntimeError(
            "yt-dlp completed, but no "
            "downloaded video file was found."
        )

    # Prefer MP4.
    mp4_files = [
        path
        for path in video_candidates
        if path.suffix.lower() == ".mp4"
    ]

    if mp4_files:
        return str(mp4_files[0])

    return str(
        video_candidates[0]
    )