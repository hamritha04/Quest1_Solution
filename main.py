import argparse

from src.downloader import download_video
from src.pipeline import ExactFramePipeline


def format_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    remaining = seconds % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{remaining:06.3f}"
    )


def main():

    parser = argparse.ArgumentParser(
        description=(
            "Find the exact video frame "
            "corresponding to spoken dialogue."
        )
    )

    source = parser.add_mutually_exclusive_group(
        required=True
    )

    source.add_argument(
        "--url",
        help="Public video URL",
    )

    source.add_argument(
        "--file",
        help="Local video file",
    )

    parser.add_argument(
        "dialogue",
        help="Dialogue sentence to find",
    )

    args = parser.parse_args()

    # ---------------------------------
    # Get the video
    # ---------------------------------

    if args.file:

        video_path = args.file

        print(
            f"\nUsing local video:\n"
            f"{video_path}"
        )

    else:

        print(
            "\nDownloading video..."
        )

        video_path = download_video(
            args.url
        )

    # ---------------------------------
    # Run search pipeline
    # ---------------------------------

    pipeline = ExactFramePipeline()

    result = pipeline.run(
        video_path,
        args.dialogue,
    )

    # ---------------------------------
    # Final output
    # ---------------------------------

    print()
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    print(
        "Timestamp : "
        + format_timestamp(
            result["timestamp"]
        )
    )

    print(
        "Frame     : "
        + str(
            result["frame_number"]
        )
    )

    print(
        'Text      : "'
        + result["text"]
        + '"'
    )

    print(
        "Image     : "
        + result["image"]
    )

    print(
        "FPS       : "
        + f"{result['fps']:.6f}"
    )

    print(
        "Confidence: "
        + f"{result['confidence']:.2f}"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()