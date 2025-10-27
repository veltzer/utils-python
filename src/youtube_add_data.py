#!/usr/bin/env python

"""
Add youtube data (extensive metadata) to a list of youtube videos.
This version can resume an interrupted job, handles commas and special characters correctly
by using the standard csv library, and flushes data to disk after each video.
"""

import sys
import os
import argparse
import csv
import json
import subprocess

def get_video_metadata(video_id: str) -> dict | None:
    """
    Fetches extensive metadata of a YouTube video given its ID using yt-dlp via subprocess.
    This avoids format selection issues by using the command line interface directly.

    Args:
        video_id: The 11-character ID of the YouTube video.

    Returns:
        A dictionary containing video metadata, or None if it cannot be found.
    """
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        print(f"Fetching data for ID: {video_id}...")

        # Use yt-dlp command line to get JSON metadata without downloading
        # The -j flag outputs JSON without downloading
        # --no-warnings suppresses warnings
        cmd = [
            "yt-dlp",
            "-j",  # Dump JSON metadata only
            "--no-warnings",
            "--skip-download",
            video_url
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            # Check if it's a format error and try with --ignore-no-formats-error
            if "format" in result.stderr.lower():
                cmd_fallback = [
                    "yt-dlp",
                    "-j",
                    "--no-warnings",
                    "--skip-download",
                    "--ignore-no-formats-error",  # Ignore format errors
                    video_url
                ]
                result = subprocess.run(cmd_fallback, capture_output=True, text=True, timeout=30)

                if result.returncode != 0:
                    print(f"Error fetching ID {video_id}: {result.stderr}")
                    return None

        if result.stdout:
            info_dict = json.loads(result.stdout)
        else:
            return None

        if not info_dict:
            return None

        # Extract comprehensive metadata
        metadata = {
            "video_id": video_id,
            "title": info_dict.get("title", ""),
            "description": info_dict.get("description", ""),
            "duration": info_dict.get("duration", ""),
            "upload_date": info_dict.get("upload_date", ""),
            "uploader": info_dict.get("uploader", ""),
            "uploader_id": info_dict.get("uploader_id", ""),
            "channel": info_dict.get("channel", ""),
            "channel_id": info_dict.get("channel_id", ""),
            "view_count": info_dict.get("view_count", ""),
            "like_count": info_dict.get("like_count", ""),
            "comment_count": info_dict.get("comment_count", ""),
            "average_rating": info_dict.get("average_rating", ""),
            "age_limit": info_dict.get("age_limit", ""),
            "categories": ", ".join(info_dict.get("categories", [])) if info_dict.get("categories") else "",
            "tags": ", ".join(info_dict.get("tags", [])) if info_dict.get("tags") else "",
            "is_live": info_dict.get("is_live", ""),
            "was_live": info_dict.get("was_live", ""),
            "live_status": info_dict.get("live_status", ""),
            "resolution": info_dict.get("resolution", ""),
            "fps": info_dict.get("fps", ""),
            "vcodec": info_dict.get("vcodec", ""),
            "acodec": info_dict.get("acodec", ""),
            "width": info_dict.get("width", ""),
            "height": info_dict.get("height", ""),
            "thumbnail": info_dict.get("thumbnail", ""),
            "webpage_url": info_dict.get("webpage_url", ""),
            "availability": info_dict.get("availability", ""),
            "playable_in_embed": info_dict.get("playable_in_embed", ""),
            "channel_follower_count": info_dict.get("channel_follower_count", ""),
            "language": info_dict.get("language", ""),
            "subtitles_available": ", ".join(info_dict.get("subtitles", {}).keys()) if info_dict.get("subtitles") else "",
            "automatic_captions_available":
                ", ".join(info_dict.get("automatic_captions", {}).keys()) if info_dict.get("automatic_captions") else "",
        }

        return metadata

    except subprocess.TimeoutExpired:
        print(f"Timeout fetching ID {video_id}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for ID {video_id}: {e}")
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

    # Define all fields we want to extract
    fieldnames = [
        "video_id", "title", "description", "duration", "upload_date",
        "uploader", "uploader_id", "channel", "channel_id",
        "view_count", "like_count", "comment_count", "average_rating",
        "age_limit", "categories", "tags", "is_live", "was_live", "live_status",
        "resolution", "fps", "vcodec", "acodec", "width", "height",
        "thumbnail", "webpage_url", "availability", "playable_in_embed",
        "channel_follower_count", "language", "subtitles_available",
        "automatic_captions_available"
    ]

    processed_ids = set()
    output_file_exists = os.path.exists(output_path)

    if output_file_exists:
        print(f"Output file [{output_path}] found. Reading existing IDs to avoid re-processing.")
        try:
            with open(output_path, "r", encoding="utf-8", newline="") as f_out_read:
                reader = csv.DictReader(f_out_read)
                for row in reader:
                    if row and "video_id" in row:
                        processed_ids.add(row["video_id"])
            print(f"Found {len(processed_ids)} previously processed IDs.")
        except IOError as e:
            print(f"Warning: Could not read from [{output_path}]. Proceeding without skipping. Error: {e}")
            processed_ids.clear()

    print(f"Reading IDs from [{input_path}]")
    print(f"Appending new data to [{output_path}]")

    with open(input_path, "r") as infile, open(output_path, "a", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        if not output_file_exists:
            writer.writeheader()
            outfile.flush()

        for line in infile:
            video_id = line.strip()
            if not video_id:
                continue

            if video_id in processed_ids:
                print(f"Skipping already processed ID: [{video_id}]")
                continue

            metadata = get_video_metadata(video_id)
            if metadata:
                writer.writerow(metadata)
            else:
                # Write a row with just the video_id and error indicator
                error_row = {field: "" for field in fieldnames}
                error_row["video_id"] = video_id
                error_row["title"] = "METADATA_NOT_FOUND"
                writer.writerow(error_row)
            outfile.flush()

    print("Processing complete")


if __name__ == "__main__":
    main()
