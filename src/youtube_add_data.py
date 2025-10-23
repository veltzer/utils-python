#!/usr/bin/env python

"""
Add youtube data (currently only title) to a list of youtube videos.
This version can resume an interrupted job, handles commas in titles correctly
by using the standard csv library, and flushes data to disk after each video.
"""

import sys
import os
import argparse
import csv
import yt_dlp
from yt_dlp.utils import DownloadError

def get_video_title(video_id: str) -> str | None:
    """
    Fetches the title of a YouTube video given its ID using the yt-dlp library.

    Args:
        video_id: The 11-character ID of the YouTube video.

    Returns:
        The video title as a string, or None if it cannot be found.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
    }

    try:
        print(f"Fetching data for ID: {video_id}...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=False)
            title = info_dict.get("title", None)

            if title:
                return title.strip()
            return None

    except DownloadError as e:
        print(f"Error fetching ID {video_id} with yt-dlp: {e}")
        return None
    # pylint: disable=broad-except
    except Exception as e:
        print(f"An unexpected error occurred for ID {video_id}: {e}")
        return None

def main():
    """
    Main function to process the list of video IDs from a file.
    """
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video titles from a list of IDs and save to a new CSV file."
    )
    parser.add_argument(
        "input_file",
        help="Path to the text file containing YouTube video IDs (one per line)."
    )
    parser.add_argument(
        "output_file",
        help="Path to the new CSV file where the results will be saved."
    )
    args = parser.parse_args()

    input_path = args.input_file
    output_path = args.output_file

    if not os.path.exists(input_path):
        print(f"Error: The file [{input_path}] was not found.")
        sys.exit(1)

    processed_ids = set()
    output_file_exists = os.path.exists(output_path)

    if output_file_exists:
        print(f"Output file [{output_path}] found. Reading existing IDs to avoid re-processing.")
        try:
            with open(output_path, "r", encoding="utf-8", newline="") as f_out_read:
                reader = csv.reader(f_out_read)
                next(reader, None)  # Skip header row
                for row in reader:
                    if row:
                        processed_ids.add(row[0])
            print(f"Found {len(processed_ids)} previously processed IDs.")
        except IOError as e:
            print(f"Warning: Could not read from [{output_path}]. Proceeding without skipping. Error: {e}")
            processed_ids.clear()

    print(f"Reading IDs from [{input_path}]")
    print(f"Appending new data to [{output_path}]")

    with open(input_path, "r") as infile, open(output_path, "a", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)

        if not output_file_exists:
            writer.writerow(["video_id", "video_title"])
            outfile.flush()

        for line in infile:
            video_id = line.strip()
            if not video_id:
                continue

            if video_id in processed_ids:
                print(f"Skipping already processed ID: [{video_id}]")
                continue

            title = get_video_title(video_id)
            if title:
                writer.writerow([video_id, title])
            else:
                writer.writerow([video_id, "TITLE_NOT_FOUND"])
            outfile.flush()

    print("Processing complete")


if __name__ == "__main__":
    main()
