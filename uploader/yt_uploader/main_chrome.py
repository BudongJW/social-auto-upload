# -*- coding: utf-8 -*-
"""YouTube Shorts uploader via Playwright (YouTube Studio)."""
import asyncio
import os

from playwright.async_api import Playwright, async_playwright

from conf import LOCAL_CHROME_PATH, LOCAL_CHROME_HEADLESS
from utils.base_social_media import set_init_script
from utils.files_times import get_absolute_path
from utils.log import youtube_logger


async def cookie_auth(account_file):
    """Check if YouTube cookie is still valid."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context(storage_state=account_file)
        page = await context.new_page()
        await page.goto("https://studio.youtube.com")
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(5000)

        current_url = page.url
        await context.close()
        await browser.close()

        if "accounts.google.com" in current_url or "signin" in current_url:
            youtube_logger.error("[+] cookie expired")
            return False

        youtube_logger.success("[+] cookie valid")
        return True


async def youtube_setup(account_file, handle=False):
    """Setup YouTube cookies. If handle=True, opens browser for manual login."""
    account_file = get_absolute_path(account_file, "yt_uploader")
    if not os.path.exists(account_file) or not await cookie_auth(account_file):
        if not handle:
            return False
        youtube_logger.info(
            "[+] Cookie not found or expired. Opening browser for YouTube login..."
        )
        await get_youtube_cookie(account_file)
    return True


async def get_youtube_cookie(account_file):
    """Open browser for manual YouTube/Google login and save cookies."""
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=False)
        context = await browser.new_context()
        context = await set_init_script(context)
        page = await context.new_page()
        await page.goto("https://accounts.google.com/signin")
        await page.pause()  # User logs in manually, then clicks Resume
        await context.storage_state(path=account_file)


class YoutubeVideo:
    """Upload a video to YouTube Studio as a Short."""

    def __init__(self, title, file_path, tags, publish_date, account_file):
        self.title = title
        self.file_path = str(file_path)
        self.tags = tags
        self.publish_date = publish_date
        self.account_file = str(account_file)
        self.local_executable_path = LOCAL_CHROME_PATH
        self.headless = LOCAL_CHROME_HEADLESS

    async def upload(self, playwright: Playwright) -> None:
        browser = await playwright.chromium.launch(
            headless=self.headless,
            executable_path=self.local_executable_path or None,
        )
        context = await browser.new_context(storage_state=self.account_file)
        page = await context.new_page()

        youtube_logger.info(f"[+] Uploading: {self.title}")

        # Go to YouTube Studio upload page
        await page.goto("https://studio.youtube.com")
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(3000)

        # Click the Create button (upload icon)
        create_btn = page.locator("#create-icon, button#create-icon")
        if await create_btn.count() > 0:
            await create_btn.first.click()
            await page.wait_for_timeout(1000)

        # Click "Upload videos" from dropdown
        upload_item = page.locator(
            'tp-yt-paper-item:has-text("Upload videos"), '
            '#text-item-0:has-text("Upload videos"), '
            'a:has-text("Upload videos")'
        )
        if await upload_item.count() > 0:
            await upload_item.first.click()
            await page.wait_for_timeout(2000)

        # Upload file via file chooser
        file_input = page.locator('input[type="file"]')
        await file_input.set_input_files(self.file_path)
        youtube_logger.info("[+] File selected, uploading...")
        await page.wait_for_timeout(5000)

        # Set title
        title_input = page.locator(
            '#textbox[aria-label="Add a title that describes your video (type @ to mention a channel)"], '
            'div#textbox[contenteditable="true"]'
        ).first
        await title_input.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.insert_text(self.title)
        await page.wait_for_timeout(1000)

        # Set description with hashtags
        desc_input = page.locator(
            '#textbox[aria-label="Tell viewers about your video (type @ to mention a channel)"], '
            'div#textbox[contenteditable="true"]'
        ).nth(1)
        if await desc_input.count() > 0:
            await desc_input.click()
            tags_text = " ".join([f"#{tag}" for tag in self.tags]) if self.tags else ""
            desc = f"{self.title}\n{tags_text} #shorts"
            await page.keyboard.insert_text(desc)
            await page.wait_for_timeout(1000)

        # Select "No, it's not made for kids"
        not_for_kids = page.locator(
            'tp-yt-paper-radio-button[name="NOT_MADE_FOR_KIDS"], '
            '#radioLabel:has-text("No, it\'s not made for kids")'
        ).first
        if await not_for_kids.count() > 0:
            await not_for_kids.click()
            await page.wait_for_timeout(500)

        # Click through Next buttons (Details → Video elements → Checks → Visibility)
        for step in range(3):
            next_btn = page.locator('#next-button, button:has-text("Next")')
            if await next_btn.count() > 0:
                await next_btn.first.click()
                await page.wait_for_timeout(2000)
                youtube_logger.info(f"[+] Step {step + 1}/3 completed")

        # Wait for upload processing
        await page.wait_for_timeout(3000)

        # Select visibility: Public
        public_radio = page.locator(
            'tp-yt-paper-radio-button[name="PUBLIC"], '
            '#radioLabel:has-text("Public")'
        ).first
        if await public_radio.count() > 0:
            await public_radio.click()
            await page.wait_for_timeout(1000)

        # Wait for upload to complete before publishing
        for _ in range(60):  # max 2 minutes wait
            progress = page.locator('.progress-label.style-scope.ytcp-video-upload-progress')
            if await progress.count() > 0:
                text = await progress.inner_text()
                if "Processing" in text or "Checks complete" in text or "100%" in text:
                    youtube_logger.info(f"[+] Upload status: {text}")
                    break
                elif "Uploading" in text:
                    youtube_logger.info(f"[+] {text}")
            await asyncio.sleep(2)

        # Click Publish / Done
        publish_btn = page.locator(
            '#done-button, button:has-text("Publish"), button:has-text("Done")'
        )
        if await publish_btn.count() > 0:
            await publish_btn.first.click()
            await page.wait_for_timeout(3000)
            youtube_logger.success("[+] Video published!")

        # Dismiss "Video published" dialog if present
        close_btn = page.locator(
            'button:has-text("Close"), '
            'ytcp-button#close-button'
        )
        if await close_btn.count() > 0:
            await close_btn.first.click()

        # Save updated cookies
        await context.storage_state(path=self.account_file)
        youtube_logger.info("[+] Cookie updated")

        await context.close()
        await browser.close()

    async def main(self):
        async with async_playwright() as playwright:
            await self.upload(playwright)
