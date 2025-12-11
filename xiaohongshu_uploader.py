import requests
import json
import time
import logging
import os
from typing import Dict, Optional

class XiaohongshuUploader:
    """Class to handle Xiaohongshu video uploads."""
    
    def __init__(self, config_file: str = "xiaohongshu_config.json"):
        self.config_file = config_file
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.load_config()
    
    def load_config(self):
        """Load Xiaohongshu configuration."""
        default_config = {
            "api_base_url": "https://creator.xiaohongshu.com",
            "login_cookie": "",
            "csrf_token": "",
            "upload_timeout": 300,
            "max_retries": 3
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except Exception as e:
                logging.error(f"Error loading Xiaohongshu config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def is_authenticated(self) -> bool:
        """Check if we have valid authentication."""
        return bool(self.config.get("login_cookie")) and bool(self.config.get("csrf_token"))
    
    def authenticate(self, cookie: str, csrf_token: str):
        """Set authentication credentials."""
        self.config["login_cookie"] = cookie
        self.config["csrf_token"] = csrf_token
        self.save_config()
        
        # Update session headers
        self.headers.update({
            "Cookie": cookie,
            "X-CSRF-Token": csrf_token
        })
    
    def upload_video(self, video_path: str, title: str, description: str, 
                    tags: list = None, cover_path: str = None) -> Dict:
        """Upload video to Xiaohongshu."""
        
        if not self.is_authenticated():
            logging.error("Not authenticated. Please set login cookie and CSRF token.")
            return {"success": False, "error": "Not authenticated"}
        
        # Step 1: Initiate upload
        upload_url = f"{self.config['api_base_url']}/api/media/upload"
        
        try:
            # Step 2: Upload video file
            with open(video_path, 'rb') as video_file:
                files = {"file": (os.path.basename(video_path), video_file, 'video/mp4')}
                
                response = self.session.post(
                    upload_url,
                    files=files,
                    headers=self.headers,
                    timeout=self.config["upload_timeout"]
                )
            
            if response.status_code != 200:
                logging.error(f"Upload failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            upload_result = response.json()
            
            if not upload_result.get("success"):
                logging.error(f"Upload API error: {upload_result}")
                return {"success": False, "error": upload_result.get("message", "Unknown error")}
            
            # Step 3: Create post with uploaded media
            media_id = upload_result.get("data", {}).get("id")
            if not media_id:
                logging.error("No media ID in upload response")
                return {"success": False, "error": "No media ID"}
            
            # Step 4: Create the post
            post_data = {
                "title": title,
                "content": description,
                "media_ids": [media_id],
                "tags": tags or [],
                "visibility": "public"
            }
            
            create_url = f"{self.config['api_base_url']}/api/posts"
            response = self.session.post(
                create_url,
                json=post_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logging.info(f"Successfully uploaded video: {title}")
                return {"success": True, "post_id": result.get("data", {}).get("id")}
            else:
                logging.error(f"Post creation failed: {response.status_code} - {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            logging.error(f"Upload error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_upload_status(self) -> Dict:
        """Get current upload status and quota information."""
        if not self.is_authenticated():
            return {"authenticated": False}
        
        try:
            status_url = f"{self.config['api_base_url']}/api/creator/status"
            response = self.session.get(status_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"error": str(e)}

def manual_authentication_helper():
    """Helper function to guide manual authentication setup."""
    print("=== Xiaohongshu Authentication Setup ===")
    print("1. Log in to Xiaohongshu Creator Platform in your browser")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Network tab and make a request")
    print("4. Copy the 'Cookie' header from the request")
    print("5. Copy the 'X-CSRF-Token' header if available")
    print("6. Enter these values when prompted")
    print()
    
    cookie = input("Enter your Xiaohongshu login cookie: ").strip()
    csrf_token = input("Enter CSRF token (if available): ").strip()
    
    uploader = XiaohongshuUploader()
    uploader.authenticate(cookie, csrf_token)
    
    print("Authentication configured successfully!")
    print("You can now use the auto uploader.")

if __name__ == "__main__":
    manual_authentication_helper()