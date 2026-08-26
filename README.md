# Quest1 - Exact Dialogue Frame Finder

## Overview

This project finds a specified **spoken dialogue sentence** in a video and returns:

- Timestamp of the dialogue
- Frame number
- Extracted dialogue text
- Corresponding video frame as an image

The project uses Whisper for speech recognition and OpenCV/FFmpeg for video processing.

---


## Requirements

Install the following:

- Python 3.10+
- FFmpeg
- yt-dlp

Make sure FFmpeg and FFprobe are available from the command line.

Check the installations:

```cmd
python --version
ffmpeg -version
ffprobe -version
```

## 1. Create Virtual Environment(Windows)

Open a terminal in the project directory:

```cmd
python -m venv venv
venv\Scripts\activate
```

## 2. Install Dependencies

Install the required Python packages:

```cmd
pip install -r requirements.txt
```

## 3. Run Using a Local Video

If the video is already downloaded, run:

```cmd
python main.py --file "video.mp4" "target dialogue"
```

Example:

```cmd
python main.py --file "The Adventures of Sherlock Holmes： A Scandal in Bohemia [Jeremy Brett] [248244667877].mp4" "My mind rebels at stagnation"
```
The program will:

Extract the audio from the video.
Perform a coarse search for the target dialogue.
Perform a finer overlapping search.
Identify the precise dialogue timestamp.
Calculate the corresponding frame number.
Save the identified frame as an image.

## 4. Run Using a Public Video URL

A publicly accessible video URL can be supplied directly:
```cmd
python main.py --url "VIDEO_URL" "target dialogue"
```
Example:
```cmd
python main.py --url "https://ok.ru/video/248244667877" "My mind rebels at stagnation"
```
The program uses yt-dlp to obtain the video before processing it.

## 5. Output

A successful run produces output similar to:
```cmd
================================
FINAL RESULT
================================

Timestamp : 00:05:25.115
Frame     : 7795
Text      : "My mind rebels at stagnation."
Image     : output\identified_frame.jpg
FPS       : 23.976166
Confidence: 100.00
```
The extracted frame is saved as:
```cmd
output/identified_frame.jpg
```
## 6. Run Unit Tests

Run all unit tests using:
```cmd
pytest -v
```
The tests cover the main components of the application, including:

Dialogue matching
Frame extraction
Timestamp handling
Downloader behavior
