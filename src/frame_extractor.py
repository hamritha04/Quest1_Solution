import math
import cv2


def get_video_info(video_path: str):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video: {video_path}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    frame_count = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    duration = (
        frame_count / fps
        if fps > 0
        else 0
    )

    cap.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
    }


def extract_frame(
    video_path: str,
    timestamp: float,
    output_path: str,
):
    """
    Extract the FIRST video frame whose timestamp
    is at or after the supplied dialogue timestamp.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open video: {video_path}"
        )

    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        cap.release()
        raise RuntimeError(
            "Could not determine video FPS."
        )

    # Important:
    # Use ceil rather than round so we don't select
    # a frame that occurs BEFORE the dialogue timestamp.
    frame_number = math.ceil(
        timestamp * fps
    )

    cap.set(
        cv2.CAP_PROP_POS_FRAMES,
        frame_number,
    )

    success, frame = cap.read()

    if not success:
        cap.release()

        raise RuntimeError(
            f"Could not read frame "
            f"{frame_number}."
        )

    actual_frame_number = int(
        cap.get(
            cv2.CAP_PROP_POS_FRAMES
        )
    ) - 1

    actual_timestamp = (
        actual_frame_number / fps
    )

    success = cv2.imwrite(
        output_path,
        frame,
    )

    cap.release()

    if not success:
        raise RuntimeError(
            f"Could not save frame to: "
            f"{output_path}"
        )

    return {
        "frame_number": actual_frame_number,
        "timestamp": actual_timestamp,
        "fps": fps,
        "image": output_path,
    }