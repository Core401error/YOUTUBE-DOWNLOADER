import argparse
import json
import os
import sys
from pathlib import Path

import yt_dlp
from yt_dlp.utils import DownloadError


def settings_file():
    if os.name == "nt" and os.getenv("APPDATA"):
        config_dir = Path(os.environ["APPDATA"]) / "media-dn"
    else:
        config_dir = Path.home() / ".config" / "media-dn"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / "settings.json"


def get_download_folder():
    settings_path = settings_file()

    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        settings = {}

    saved_folder = settings.get("download_folder")
    if saved_folder and Path(saved_folder).is_dir():
        print(f"Download folder: {saved_folder}")
        return Path(saved_folder)

    while True:
        entered = input("Download folder path: ").strip().strip('"')
        if not entered:
            print("Enter a folder path.")
            continue

        folder = Path(entered).expanduser()
        try:
            folder.mkdir(parents=True, exist_ok=True)
            settings["download_folder"] = str(folder.resolve())
            settings_path.write_text(
                json.dumps(settings, indent=2),
                encoding="utf-8",
            )
            return folder
        except OSError as exc:
            print(f"Could not use that folder: {exc}")


def pick_target(initial_text=None):
    text = initial_text

    while True:
        if text is None:
            text = input(
                "\nPaste a URL or enter YouTube search words "
                "(or Q to quit): "
            ).strip()

        if text.lower() in {"q", "quit", "exit"}:
            return None

        if "://" in text:
            return text

        if not text:
            text = None
            continue

        print("\nSearching YouTube...")
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
                result = ydl.extract_info(
                    f"ytsearch20:{text}",
                    download=False,
                )
        except DownloadError as exc:
            print(f"Search failed: {exc}")
            text = None
            continue

        entries = [
            entry for entry in (result or {}).get("entries", [])
            if entry
        ]

        if not entries:
            print("No results found.")
            text = None
            continue

        for number, entry in enumerate(entries, start=1):
            duration = entry.get("duration")
            length = f" ({duration // 60}:{duration % 60:02d})" if duration else ""
            print(f"{number:2}. {entry.get('title', 'Untitled')}{length}")

        while True:
            choice = input("Choose a result number, or B to search again: ").strip().lower()

            if choice == "b":
                text = None
                break

            if choice.isdigit() and 1 <= int(choice) <= len(entries):
                selected = entries[int(choice) - 1]
                return (
                    selected.get("webpage_url")
                    or selected.get("url")
                    or f"https://www.youtube.com/watch?v={selected['id']}"
                )

            print("Enter a displayed number or B.")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="media-dl",
        description="Interactive media downloader using yt-dlp.",
    )
    parser.add_argument(
        "target",
        nargs="*",
        help="Optional URL or search phrase",
    )
    parser.add_argument(
        "--quality",
        choices=["best", "360", "480", "720", "1080", "1440", "2160"],
        default="best",
        help="Maximum video height; default: best available",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    initial_text = " ".join(args.target).strip() or None
    output_folder = get_download_folder()

    print("\nMedia DL — download only media you are authorized to save.")

    while True:
        target = pick_target(initial_text)
        initial_text = None

        if target is None:
            print("Goodbye.")
            return

        playlist = input("Download as a playlist? [y/N]: ").strip().lower() == "y"
        playlist_items = None

        if playlist:
            playlist_items = input(
                "Playlist range (for example 1-5), or Enter for all: "
            ).strip() or None

        print(
            "\nChoose format:\n"
            "  1. Video\n"
            "  2. Hindi audio — FLAC\n"
            "  3. Hindi audio — MP3\n"
            "  4. English audio — FLAC\n"
            "  5. English audio — MP3"
        )
        choice = input("> ").strip()

        if choice not in {"1", "2", "3", "4", "5"}:
            print("Invalid choice.")
            continue

        if playlist:
            output_template = str(
                output_folder
                / "%(playlist_title)s"
                / "%(playlist_index)02d - %(title)s.%(ext)s"
            )
        else:
            output_template = str(output_folder / "%(title)s.%(ext)s")

        options = {
            "outtmpl": output_template,
            "noplaylist": not playlist,
            "windowsfilenames": True,
        }

        if playlist_items:
            options["playlist_items"] = playlist_items

        if choice == "1":
            if args.quality == "best":
                video_format = "bestvideo*+bestaudio/best"
            else:
                video_format = (
                    f"bestvideo[height<={args.quality}]+bestaudio/"
                    f"best[height<={args.quality}]"
                )

            options.update({
                "format": video_format,
                "merge_output_format": "mp4",
            })
        else:
            language = "hi" if choice in {"2", "3"} else "en"
            audio_format = "flac" if choice in {"2", "4"} else "mp3"

            options.update({
                "format": f"ba[language={language}]/ba",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "0",
                }],
                "addmetadata": True,
            })

        print("\nStarting download...")
        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                ydl.download([target])
            print("\nDownload finished.")
        except DownloadError as exc:
            print(f"\nDownload failed: {exc}")
        except KeyboardInterrupt:
            print("\nDownload cancelled.")

        if input("\nDownload another? [Y/n]: ").strip().lower() == "n":
            print("Goodbye.")
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
        sys.exit(130)
