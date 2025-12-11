#!/usr/bin/env python3
"""
Test script to verify the YouTube to Xiaohongshu automation workflow.
This script tests the basic functionality without actual downloads/uploads.
"""

import os
import sys
import json
from unittest.mock import patch, MagicMock

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """Test configuration loading functionality."""
    print("Testing configuration loading...")
    
    # Import and test config loading
    from auto_uploader import load_config
    
    config = load_config()
    
    # Verify required keys exist
    required_keys = ['youtube_channels', 'download_limit', 'upload_delay', 'hashtags']
    for key in required_keys:
        assert key in config, f"Missing config key: {key}"
    
    assert isinstance(config['youtube_channels'], list), "youtube_channels should be a list"
    assert isinstance(config['download_limit'], int), "download_limit should be an integer"
    
    print("✅ Configuration loading test passed")

def test_filename_cleaning():
    """Test filename cleaning functionality."""
    print("Testing filename cleaning...")
    
    from publish_assistant import clean_filename_for_title
    
    test_cases = [
        ("My_Video_Title.mp4", "My Video Title"),
        ("Song_Name_[Official_Video].mkv", "Song Name"),
        ("Artist_-_Song_(Live_Performance).webm", "Artist - Song"),
        ("video.with.dots.and_underscores.mp4", "video with dots and underscores")
    ]
    
    for filename, expected in test_cases:
        result = clean_filename_for_title(filename)
        assert result == expected, f"Expected '{expected}', got '{result}' for '{filename}'"
    
    print("✅ Filename cleaning test passed")

def test_video_discovery():
    """Test video file discovery functionality."""
    print("Testing video discovery...")
    
    from publish_assistant import find_new_videos
    
    # Mock the directory listing
    with patch('os.listdir') as mock_listdir, \
         patch('os.path.isfile') as mock_isfile, \
         patch('os.path.exists') as mock_exists:
        
        # Mock directory contents
        mock_listdir.return_value = [
            'video1.mp4',
            'video2.mkv', 
            'video1.jpg',  # thumbnail
            'not_a_video.txt',
            'video3.webm'
        ]
        
        mock_isfile.side_effect = lambda x: x.endswith(('.mp4', '.mkv', '.webm', '.txt'))
        mock_exists.side_effect = lambda x: x.endswith('.jpg')
        
        videos = find_new_videos()
        
        assert len(videos) == 3, f"Expected 3 videos, found {len(videos)}"
        
        # Verify video1 has thumbnail
        video1 = next(v for v in videos if v['filename'] == 'video1.mp4')
        assert video1['thumbnail_path'] is not None, "video1 should have thumbnail"
        
        # Verify video2 has no thumbnail  
        video2 = next(v for v in videos if v['filename'] == 'video2.mkv')
        assert video2['thumbnail_path'] is None, "video2 should not have thumbnail"
    
    print("✅ Video discovery test passed")

def main():
    """Run all tests."""
    print("Running automation workflow tests...\n")
    
    try:
        test_config_loading()
        test_filename_cleaning() 
        test_video_discovery()
        
        print("\n🎉 All tests passed! The automation workflow is ready.")
        print("\nNext steps:")
        print("1. Run 'python xiaohongshu_uploader.py' to set up authentication")
        print("2. Modify config.json to add your YouTube channels")
        print("3. Run 'python auto_uploader.py' to start the automation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()