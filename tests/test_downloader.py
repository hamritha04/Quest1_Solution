from pathlib import Path
from unittest.mock import patch

import pytest

from src.downloader import download_video


def test_download_video_success(tmp_path):

    fake_video = tmp_path / "video.mp4"
    fake_video.write_bytes(b"fake video")

    with patch(
        "src.downloader.subprocess.run"
    ) as mock_run:

        result = download_video(
            "https://ok.ru/video/248244667877",
            str(tmp_path),
        )

    mock_run.assert_called_once()

    assert result.endswith("video.mp4")


def test_download_video_command_uses_impersonation(tmp_path):

    fake_video = tmp_path / "video.mp4"
    fake_video.write_bytes(b"fake video")

    with patch(
        "src.downloader.subprocess.run"
    ) as mock_run:

        download_video(
            "https://ok.ru/video/248244667877",
            str(tmp_path),
        )

    command = mock_run.call_args.args[0]

    assert "--impersonate" in command
    assert "chrome" in command
    assert "--no-playlist" in command


def test_download_failure(tmp_path):

    import subprocess

    with patch(
        "src.downloader.subprocess.run",
        side_effect=subprocess.CalledProcessError(
            1,
            ["yt-dlp"],
        ),
    ):

        with pytest.raises(RuntimeError):
            download_video(
                "https://ok.ru/video/248244667877",
                str(tmp_path),
            )