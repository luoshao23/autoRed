
import subprocess
import os

# --- Configuration ---
CHANNEL_URL = "https://www.youtube.com/@The_FirstTake"
DOWNLOAD_DIR = "downloads"
ARCHIVE_FILE = os.path.join(DOWNLOAD_DIR, "downloaded.txt")

# --- Create download directory if it doesn't exist ---
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# --- Construct the yt-dlp command ---
# -f: format selection, get the best mp4 video and audio
# -o: output template
# --download-archive: file to track downloaded videos
# --write-thumbnail: download video thumbnail
# --limit-rate: limit download speed to 10M, to be friendly to the network
# --retries: number of retries for a failed download
# --fragment-retries: number of retries for a fragment
# --playlist-items: download the most recent 3 videos for this first run
# --verbose: print more information
command = [
    "yt-dlp",
    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
    "-o", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
    "--download-archive", ARCHIVE_FILE,
    "--write-thumbnail",
    "--limit-rate", "10M",
    "--retries", "3",
    "--fragment-retries", "3",
    "--playlist-items", "1-3", # Download the most recent 3 videos
    "--verbose",
    CHANNEL_URL
]

# --- Run the command ---
print(f"Starting download from channel: {CHANNEL_URL}")
print(f"Downloading to: {os.path.abspath(DOWNLOAD_DIR)}")
print(f"Using archive file: {os.path.abspath(ARCHIVE_FILE)}")
print(f"Executing command: {' '.join(command)}")

try:
    # We need to run this within the conda environment
    conda_command = ["conda", "run", "-n", "web"] + command
    process = subprocess.Popen(conda_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8')

    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip())

    rc = process.poll()
    if rc == 0:
        print("Download process completed successfully.")
    else:
        print(f"Download process failed with return code: {rc}")

except Exception as e:
    print(f"An error occurred: {e}")
