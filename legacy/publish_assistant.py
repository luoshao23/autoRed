
import os
import shutil
import webbrowser
import re

# --- Configuration ---
DOWNLOAD_DIR = "downloads"
UPLOADED_DIR = os.path.join(DOWNLOAD_DIR, "uploaded")
XHS_UPLOAD_URL = "https://creator.xiaohongshu.com/publish/publish?type=video"

# --- Ensure directories exist ---
os.makedirs(UPLOADED_DIR, exist_ok=True)

def clean_filename_for_title(filename):
    """Cleans the filename to create a more readable title."""
    # Remove extension
    title = os.path.splitext(filename)[0]
    # Remove common patterns like [ID], (Official Video), etc.
    title = re.sub(r'\[.*?\]', '', title)
    title = re.sub(r'\(.*\)', '', title)
    # Replace underscores/dots with spaces
    title = title.replace('_', ' ').replace('.', ' ')
    # Trim whitespace
    return title.strip()

def find_new_videos():
    """Finds video files in the download directory that haven't been uploaded."""
    new_videos = []
    video_extensions = ('.mp4', '.mkv', '.webm', '.mov')
    thumbnail_extensions = ('.jpg', '.jpeg', '.png', '.webp')

    for item in os.listdir(DOWNLOAD_DIR):
        item_path = os.path.join(DOWNLOAD_DIR, item)
        if os.path.isfile(item_path) and item.lower().endswith(video_extensions):
            # Find matching thumbnail
            base_name = os.path.splitext(item)[0]
            thumbnail_path = None
            for ext in thumbnail_extensions:
                potential_thumb = os.path.join(DOWNLOAD_DIR, base_name + ext)
                if os.path.exists(potential_thumb):
                    thumbnail_path = potential_thumb
                    break
            
            new_videos.append({
                "video_path": item_path,
                "thumbnail_path": thumbnail_path,
                "filename": item
            })
    return new_videos

def main():
    """Main function to run the publishing assistant."""
    print("--- 小红书发布助手 ---")
    
    videos_to_process = find_new_videos()
    
    if not videos_to_process:
        print("\n>> 没有在 'downloads' 文件夹中找到新的视频文件。")
        print(">> 请先运行 `download_videos.py` 下载视频。")
        return

    print(f"\n找到了 {len(videos_to_process)} 个新视频，准备处理...\n")

    for video_info in videos_to_process:
        video_path = video_info["video_path"]
        thumbnail_path = video_info["thumbnail_path"]
        filename = video_info["filename"]
        
        # Generate metadata
        title = clean_filename_for_title(filename)
        hashtags = "#THEFIRSTTAKE #音乐现场 #JPOP #live"
        suggested_caption = f"{title}\n\n{hashtags}"

        print("--------------------------------------------------")
        print(f"🎬 准备发布: {title}")
        print(f"   - 视频文件: {video_path}")
        if thumbnail_path:
            print(f"   - 封面文件: {thumbnail_path}")
        else:
            print("   - 封面文件: 未找到")
        print("\n✨ 建议文案:")
        print(suggested_caption)
        print("--------------------------------------------------")

        # User interaction
        action = input("👉 是否现在手动上传这个视频? (y/n/s) [y=是, n=跳过, s=停止]: ").lower()

        if action == 's':
            print("脚本已停止。")
            break
        elif action == 'n':
            print("已跳过。\n")
            continue
        elif action == 'y':
            print(f"\n正在为您打开小红书发布页面: {XHS_UPLOAD_URL}")
            webbrowser.open(XHS_UPLOAD_URL)
            
            input("\n当您在浏览器中完成上传后，请按 Enter 键继续...")
            
            # Move files to uploaded directory
            try:
                shutil.move(video_path, UPLOADED_DIR)
                if thumbnail_path:
                    shutil.move(thumbnail_path, UPLOADED_DIR)
                print(f"✅ 文件已移动到: {UPLOADED_DIR}")
            except Exception as e:
                print(f"移动文件时出错: {e}")
            
            print("\n")

    print("--- 所有视频处理完毕 ---")

if __name__ == "__main__":
    main()
