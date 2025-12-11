import subprocess
import os
import time
import json
import logging
import shutil
from datetime import datetime
from publish_assistant import find_new_videos, clean_filename_for_title
from xiaohongshu_uploader import XiaohongshuUploader

# --- Configuration ---
CONFIG_FILE = "config.json"
DOWNLOAD_DIR = "downloads"
UPLOADED_DIR = os.path.join(DOWNLOAD_DIR, "uploaded")
LOG_FILE = "auto_uploader.log"

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def load_config():
    """Load configuration from JSON file."""
    default_config = {
        "youtube_channels": [
            "https://www.youtube.com/@The_FirstTake"
        ],
        "download_limit": 3,
        "upload_delay": 300,  # 5 minutes between uploads
        "auto_upload": False,
        "hashtags": "#THEFIRSTTAKE #音乐现场 #JPOP #live",
        "enable_xiaohongshu_api": False
    }
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return default_config
    else:
        # Create default config file
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        return default_config

def download_channel_videos(channel_url, download_limit):
    """Download videos from a YouTube channel using yt-dlp."""
    try:
        command = [
            "yt-dlp",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            "--download-archive", os.path.join(DOWNLOAD_DIR, "downloaded.txt"),
            "--write-thumbnail",
            "--limit-rate", "10M",
            "--retries", "3",
            "--fragment-retries", "3",
            "--playlist-items", f"1-{download_limit}",
            "--verbose",
            channel_url
        ]
        
        logging.info(f"Downloading from channel: {channel_url}")
        
        # Run within conda environment
        conda_command = ["conda", "run", "-n", "web"] + command
        result = subprocess.run(conda_command, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0:
            logging.info(f"Successfully downloaded videos from {channel_url}")
            return True
        else:
            logging.error(f"Download failed: {result.stderr}")
            return False
            
    except Exception as e:
        logging.error(f"Error during download: {e}")
        return False

def upload_to_xiaohongshu(video_info, hashtags, config):
    """Upload video to Xiaohongshu using API or manual process."""
    video_path = video_info["video_path"]
    filename = video_info["filename"]
    thumbnail_path = video_info.get("thumbnail_path")
    
    title = clean_filename_for_title(filename)
    caption = f"{title}\n\n{hashtags}"
    
    logging.info(f"Preparing to upload: {title}")
    logging.info(f"Video file: {video_path}")
    
    if config.get("enable_xiaohongshu_api", False):
        # Use API upload
        try:
            uploader = XiaohongshuUploader()
            
            if not uploader.is_authenticated():
                logging.warning("Xiaohongshu API not authenticated, falling back to manual process")
                return manual_upload_process(video_info, caption, config)
            
            # Convert hashtags to list
            tags = [tag.strip() for tag in hashtags.split("#") if tag.strip()]
            
            result = uploader.upload_video(
                video_path=video_path,
                title=title,
                description=caption,
                tags=tags,
                cover_path=thumbnail_path
            )
            
            if result["success"]:
                move_to_uploaded(video_info)
                logging.info(f"✅ API upload successful: {title}")
                return True
            else:
                logging.error(f"API upload failed: {result.get('error')}")
                return False
                
        except Exception as e:
            logging.error(f"API upload error: {e}")
            return manual_upload_process(video_info, caption, config)
    else:
        # Use manual upload process
        return manual_upload_process(video_info, caption, config)

def manual_upload_process(video_info, caption, config):
    """Manual upload process with user interaction."""
    video_path = video_info["video_path"]
    filename = video_info["filename"]
    title = clean_filename_for_title(filename)
    
    print("\n" + "="*50)
    print(f"🎬 准备手动上传: {title}")
    print(f"📁 视频文件: {video_path}")
    if video_info.get("thumbnail_path"):
        print(f"🖼️  封面文件: {video_info['thumbnail_path']}")
    print("\n📝 文案内容:")
    print(caption)
    print("="*50)
    
    # For manual process, we'll just move the file and log
    # In a real implementation, you might open the upload page
    try:
        move_to_uploaded(video_info)
        logging.info(f"✅ Manual upload process completed for: {title}")
        return True
    except Exception as e:
        logging.error(f"Manual upload process error: {e}")
        return False

def move_to_uploaded(video_info):
    """Move processed files to uploaded directory."""
    os.makedirs(UPLOADED_DIR, exist_ok=True)
    
    # Move video file
    shutil.move(video_info["video_path"], UPLOADED_DIR)
    
    # Move thumbnail if exists
    thumbnail_path = video_info.get("thumbnail_path")
    if thumbnail_path and os.path.exists(thumbnail_path):
        shutil.move(thumbnail_path, UPLOADED_DIR)

def main():
    """Main automation function."""
    logging.info("=== Starting Auto Uploader ===")
    
    config = load_config()
    
    # Download videos from all configured channels
    for channel_url in config["youtube_channels"]:
        success = download_channel_videos(channel_url, config["download_limit"])
        if not success:
            logging.warning(f"Failed to download from {channel_url}, skipping upload")
            continue
    
    # Find and process new videos
    videos_to_process = find_new_videos()
    
    if not videos_to_process:
        logging.info("No new videos found to process")
        return
    
    logging.info(f"Found {len(videos_to_process)} new videos to process")
    
    # Process each video
    for video_info in videos_to_process:
        success = upload_to_xiaohongshu(video_info, config["hashtags"], config)
        
        if success and config["upload_delay"] > 0:
            logging.info(f"Waiting {config['upload_delay']} seconds before next upload...")
            time.sleep(config["upload_delay"])
    
    logging.info("=== Auto Uploader completed ===")

if __name__ == "__main__":
    main()