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
from playwright.async_api import TimeoutError # 导入TimeoutError

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

    async def check_login_status(self):
        # 尝试等待头像元素出现
        try:
            # 使用 wait_for_selector 或 page.locator.wait_for()
            # 注意: page.wait_for_selector 在 Playwright 1.x 版本的 Python 绑定中, 超时会抛出异常
            await self.page.wait_for_selector("img.user_avatar", timeout=10000)
            # 如果代码执行到这里，说明找到头像，即已登录
            print("[autoRed] 已成功登录.")
            return True

        except TimeoutError:
            # 如果超时，说明未找到头像，即未登录
            print("[autoRed] 未检测到用户头像，判断为未登录.")
            return False
        except Exception as e:
            # 捕获其他任何意外错误
            print(f"[autoRed] 发生其他错误: {e}")
            return False

    async def login(self):
        """Login to Xiaohongshu. If cookies are present they are used, otherwise a QR code is shown.
        The user must scan the QR code within the browser window.
        """
        await self._ensure_browser()
        await self._load_cookies()
        await self.page.goto("https://creator.xiaohongshu.com")
        # Check if we are already logged in by looking for the avatar element.
        current_url = self.page.url
        is_logged_in = await self.check_login_status()
        # is_logged_in = "/home" in current_url
        # is_logged_in = await self.page.locator("img.user_avatar").is_visible(timeout=10000)
        if is_logged_in:
            print("Already logged in via cookies.")
            return
        # Otherwise trigger QR login flow.
        await self.page.wait_for_selector("img", timeout=10000)
        await self.page.click("img")
        # Wait for the QR code canvas to appear.
        await self.page.wait_for_selector("text=APP扫一扫登录", timeout=100000)
        print("Please scan the QR code displayed in the browser window.")
        # Wait until the avatar appears, indicating successful login.
        await self.page.wait_for_selector("img.user_avatar", timeout=120000)
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
        current_url = self.page.url
        is_logged_in = await self.check_login_status()
        # is_logged_in = "/home" in current_url
        # is_logged_in = await self.page.locator("img.user_avatar").is_visible(timeout=10000)
        if not is_logged_in:
            print("not logged in")
            await self.login()
        print("login succeeded")

        # Click the button to create a new post.
        await self.page.wait_for_selector("text=发布笔记", timeout=10000)
        await self.page.click("text=发布笔记")
        await self.page.click("text=上传图文")

        # Upload images.
        for img_path in image_paths:
            # The file input is hidden; we use set_input_files.
            await self.page.set_input_files("input[type='file']", str(img_path))
            # Wait a short moment for the thumbnail to appear.
            await self.page.wait_for_timeout(10000)
        print("images uploaded")
        # Fill title and copy.
        await self.page.fill("input.d-text", title)
        await self.page.fill("div[role='textbox']", copy)
        print("title and copy filled")

        # Submit the post.
        locator = self.page.locator("div.d-button-content")
        await self.page.wait_for_timeout(3600*1000)
        # filtered_locator = locator.filter(has_text="发布")
        # await filtered_locator.click()
        # # Wait for confirmation.
        # await self.page.wait_for_selector("text=发布成功", timeout=30000)
        print("Post published.")

    async def close(self):
        if self.browser:
            await self.browser.close()

# Helper function for synchronous usage
def run_publish(image_paths: List[Path], title: str, copy: str, headless: bool = True):
    async def _run():
        publisher = XHSPublisher(headless=headless)
        # await publisher.login()
        await publisher.publish(image_paths, title, copy)
        await publisher.close()
    asyncio.run(_run())
