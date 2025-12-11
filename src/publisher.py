# publisher for autoRed

"""Module to automate publishing posts to Xiaohongshu using Playwright.
It handles login (via QR code) and posting images with title and copy.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import List

from playwright.async_api import async_playwright

# Path to store cookies for persistent login
COOKIES_PATH = Path(__file__).parent.parent / "cookies" / "xhs_cookies.json"

class XHSPublisher:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None

    async def _ensure_browser(self):
        if self.browser is None:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()

    async def _load_cookies(self):
        if COOKIES_PATH.exists():
            cookies = json.loads(COOKIES_PATH.read_text())
            await self.context.add_cookies(cookies)

    async def _save_cookies(self):
        cookies = await self.context.cookies()
        COOKIES_PATH.parent.mkdir(parents=True, exist_ok=True)
        COOKIES_PATH.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))

    async def login(self):
        """Login to Xiaohongshu. If cookies are present they are used, otherwise a QR code is shown.
        The user must scan the QR code within the browser window.
        """
        await self._ensure_browser()
        await self._load_cookies()
        await self.page.goto("https://creator.xiaohongshu.com")
        # Check if we are already logged in by looking for the avatar element.
        if await self.page.query_selector("img[alt='User Avatar']"):
            print("Already logged in via cookies.")
            return
        # Otherwise trigger QR login flow.
        await self.page.wait_for_selector("text=QR code login", timeout=10000)
        await self.page.click("text=QR code login")
        # Wait for the QR code canvas to appear.
        await self.page.wait_for_selector("canvas", timeout=30000)
        print("Please scan the QR code displayed in the browser window.")
        # Wait until the avatar appears, indicating successful login.
        await self.page.wait_for_selector("img[alt='User Avatar']", timeout=120000)
        await self._save_cookies()
        print("Login successful and cookies saved.")

    async def publish(self, image_paths: List[Path], title: str, copy: str):
        """Publish a post with given images, title and copy.
        Args:
            image_paths: List of image file paths to upload.
            title: Post title.
            copy: Post body text.
        """
        await self._ensure_browser()
        await self._load_cookies()
        await self.page.goto("https://creator.xiaohongshu.com")
        # Ensure we are logged in.
        if not await self.page.query_selector("img[alt='User Avatar']"):
            await self.login()

        # Click the button to create a new post.
        await self.page.wait_for_selector("text=Create Post", timeout=10000)
        await self.page.click("text=Create Post")

        # Upload images.
        for img_path in image_paths:
            # The file input is hidden; we use set_input_files.
            await self.page.set_input_files("input[type='file']", str(img_path))
            # Wait a short moment for the thumbnail to appear.
            await self.page.wait_for_timeout(1000)

        # Fill title and copy.
        await self.page.fill("textarea[placeholder='Add a title']", title)
        await self.page.fill("div[role='textbox']", copy)

        # Submit the post.
        await self.page.click("text=Publish")
        # Wait for confirmation.
        await self.page.wait_for_selector("text=Published successfully", timeout=30000)
        print("Post published.")

    async def close(self):
        if self.browser:
            await self.browser.close()

# Helper function for synchronous usage
def run_publish(image_paths: List[Path], title: str, copy: str, headless: bool = True):
    async def _run():
        publisher = XHSPublisher(headless=headless)
        await publisher.login()
        await publisher.publish(image_paths, title, copy)
        await publisher.close()
    asyncio.run(_run())
