#!/usr/bin/env python

"""
Add youtube data (currently only title) to a list of youtube videos.
This version can resume an interrupted job by skipping IDs already present
in the output file and flushes data to disk after each video.
"""

import sys
import os
import argparse
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

    # yt-dlp options:
    # 'quiet': Suppresses console output from the library.
    # 'no_warnings': Suppresses warnings.
    # 'extract_flat': Only extracts basic info, making it faster.
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
    }

    try:
        print(f"Fetching data for ID: {video_id}...")
        # The 'with' statement ensures resources are properly handled.
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Fetch the video's metadata without downloading.
            info_dict = ydl.extract_info(video_url, download=False)

            # Extract the title from the returned dictionary.
            title = info_dict.get('title', None)

            if title:
                # Replace commas to avoid breaking CSV format
                return title.replace(',', ';').strip()
            return None

    except DownloadError as e:
        # This error is triggered for unavailable videos, private videos, etc.
        print(f"Error fetching ID {video_id} with yt-dlp: {e}")
        return None
    # pylint: disable=broad-except
    except Exception as e:
        # Catch any other unexpected errors.
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

    # Check if the input file exists
    if not os.path.exists(input_path):
        print(f"Error: The file '{input_path}' was not found.")
        sys.exit(1)

    # --- MODIFICATION: Read existing output file to find processed IDs ---
    processed_ids = set()
    output_file_exists = os.path.exists(output_path)

    if output_file_exists:
        print(f"Output file '{output_path}' found. Reading existing IDs to avoid re-processing.")
        try:
            with open(output_path, 'r', encoding='utf-8') as f_out_read:
                next(f_out_read, None)  # Skip header row
                for line in f_out_read:
                    if ',' in line:
                        video_id = line.split(',')[0].strip()
                        if video_id:
                            processed_ids.add(video_id)
            print(f"Found {len(processed_ids)} previously processed IDs.")
        except IOError as e:
            print(f"Warning: Could not read from '{output_path}'. Proceeding without skipping. Error: {e}")
            processed_ids.clear()

    print(f"Reading IDs from: {input_path}")
    print(f"Appending new data to: {output_path}")

    try:
        # --- MODIFICATION: Open the output file in append mode ('a') ---
        with open(input_path, 'r') as infile, open(output_path, 'a', encoding='utf-8') as outfile:
            # --- MODIFICATION: Write header only if the file is new ---
            if not output_file_exists:
                outfile.write("video_id,video_title\n")
                outfile.flush()  # Also flush the header

            for line in infile:
                video_id = line.strip()
                if not video_id:
                    continue

                # --- MODIFICATION: Skip IDs that are already processed ---
                if video_id in processed_ids:
                    print(f"Skipping already processed ID: {video_id}")
                    continue

                title = get_video_title(video_id)
                if title:
                    outfile.write(f"{video_id},{title}\n")
                else:
                    outfile.write(f"{video_id},TITLE_NOT_FOUND\n")

                # --- MODIFICATION: Flush the buffer to disk after each write ---
                outfile.flush()

    except IOError as e:
        print(f"Error reading or writing file: {e}")
        sys.exit(1)

    print("\nProcessing complete! ✨")


if __name__ == "__main__":
    main()
