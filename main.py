# main entry point for autoRed

"""Orchestrates the end‑to‑end workflow:
1. Generate an image prompt using Gemini Flash.
2. Generate 3‑6 images with Imagen.
3. Create a title and copy for a Xiaohongshu post.
4. Publish the post via Playwright.
5. Schedule the job to run daily at the configured time.
"""

import os
from pathlib import Path
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

from src.llm_client import generate_image_prompt, generate_post_content, generate_content_element, generate_content_element_cloudflare
from src.image_client import generate_images
from src.publisher import run_publish
from config.settings import SCHEDULE_TIME


def job_v2(mode="prod"):
    print(f"[autoRed] Job started at {datetime.now()}")
    # 1. Prompt generation
    # content_element = generate_content_element()
    content_element = generate_content_element_cloudflare()
    # content_element = {}
    image_prompt = content_element.get("image_prompt", "")
    title = content_element.get("title", "title")
    copy = content_element.get("copy", "nothing")

    print(f"Generated prompt: {image_prompt}")
    print(f"Title: {title}\nCopy: {copy}")
    # 2. Image generation (default 3 images)
    images = generate_images(image_prompt, count=1, mode=mode)
    print(f"Generated {len(images)} images. \nlist: {images}")

    # 3. Publish
    run_publish(images, title, copy, headless=False)
    # print("[autoRed] Job completed.")

def job(mode="prod"):
    print(f"[autoRed] Job started at {datetime.now()}")
    # 1. Prompt generation
    prompt = generate_image_prompt()
    # prompt = "a picture of a hot girl"
    print(f"Generated prompt: {prompt}")
    # 2. Image generation (default 3 images)
    images = generate_images(prompt, count=1, mode=mode)
    print(f"Generated {len(images)} images. \nlist: {images}")
    # # 3. Post content generation
    content = generate_post_content(prompt)
    title = content.get("title", "")
    copy = content.get("copy", "")
    print(f"Title: {title}\nCopy: {copy}")
    # # 4. Publish
    run_publish(images, title, copy, headless=False)
    print("[autoRed] Job completed.")

if __name__ == "__main__":
    mode = os.getenv("MODE", "test")
    print(f"[autoRed] Mode: {mode}")
    if mode in ("test", "dev"):
        job_v2(mode)
    elif mode == "daily":
        # Scheduler configuration – run daily at SCHEDULE_TIME (HH:MM)
        hour, minute = map(int, SCHEDULE_TIME.split(":"))
        scheduler = BlockingScheduler()
        scheduler.add_job(job_v2, "cron", hour=hour, minute=minute, id="autoRed_daily")
        print(f"[autoRed] Scheduler started – job will run daily at {SCHEDULE_TIME}.")
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            print("Scheduler stopped.")
