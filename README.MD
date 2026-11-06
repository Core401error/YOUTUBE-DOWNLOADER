                                                         MEDIA DOWNLOADER

An interactive command-line downloader built with Python and yt-dlp.It is used to download audio and video files from YouTube.

Requirements

- Windows
- Python 3.10 or newer
- FFmpeg on PATH for audio conversion and video merging

Install

Open Command Prompt in this folder and run:

    py -3 -m pip install -r requirements.txt


Interactive:

    media-dn

Search directly:

    media-dn "search words"

Search or URL with a maximum video height:

    media-dl "search words" --quality 1080
    media-dl "https://example.com/video" --quality 2160

The default quality is `best`. A selected resolution is a maximum; if it is
unavailable, a lower resolution may be used.

Add the command to Windows PATH

Add the full path to this project folder—the folder containing `media-dn.cmd`—
to your user PATH:

1. Search Windows for **Edit environment variables for your account**.
2. Select **Path** under User variables, then **Edit** → **New**.
3. Enter this project's folder path and confirm the dialogs.
4. Open a new terminal and run `media-dn`.

The first run asks for a download folder and remembers it.

FFmpeg

FFmpeg is a separate program, not a Python requirement. Install it separately
and ensure `ffmpeg` is available on PATH.

