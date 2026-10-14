import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

APP_URL = "https://book-concierge-frontend-442712869835.us-east1.run.app"
RECORD_DIR = Path("/tmp/demo_recordings")
OUTPUT_VIDEO = Path("/config/Desktop/BuildWithGemini/demo.mp4")
ARTIFACT_DIR = Path("/config/.gemini/antigravity/brain/afe4424b-bdb7-4b46-83f3-f483e8a7719d")

async def record():
    if RECORD_DIR.exists():
        shutil.rmtree(RECORD_DIR)
    RECORD_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(RECORD_DIR),
            record_video_size={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        print("Navigating to app URL:", APP_URL)
        await page.goto(APP_URL, wait_until="networkidle")
        await asyncio.sleep(3)

        # Question 1: Click first quick-action button
        print("Clicking first quick-action: 서재 현황 확인...")
        buttons = page.locator(".quick-btn")
        await buttons.nth(0).click()

        # Wait for reply to populate in #log
        print("Waiting for first reply...")
        for _ in range(40):
            html = await page.locator("#log").inner_html()
            if "a2card" in html or "서재" in html:
                print("First reply received!")
                break
            await asyncio.sleep(1)
        await asyncio.sleep(4)

        # Question 2: Rich prompt exercising tools, database recommendation, and image generation
        q2 = "내 취향에 어울리는 새로운 SF 도서를 추천해주고, 그 도서의 멋진 북커버 표지 일러스트도 생성해줘!"
        print("Sending second prompt:", q2)
        await page.fill("#input", q2)
        await asyncio.sleep(1.5)
        await page.click("button:has-text('전송')")

        # Wait for second reply (cover image card)
        print("Waiting for second reply with generated cover image...")
        for i in range(90):
            html = await page.locator("#log").inner_html()
            # Check for image or second card
            if html.count("a2card") >= 2 or "<img" in html or "storage.googleapis.com" in html:
                print("Second reply received with image/card!")
                break
            await asyncio.sleep(1)
            if i % 10 == 0:
                print(f"Still waiting for image generation... ({i}s elapsed)")

        await asyncio.sleep(4)

        # Smoothly scroll down so the whole response and image is visible
        print("Scrolling down to show full card...")
        await page.evaluate("""
            const el = document.getElementById('log');
            el.scrollTo({top: el.scrollHeight, behavior: 'smooth'});
        """)
        await asyncio.sleep(5)

        await page.close()
        await context.close()
        await browser.close()

    video_files = list(RECORD_DIR.glob("*.webm"))
    if not video_files:
        raise RuntimeError("No video file was recorded.")
    
    src_video = video_files[0]
    print("Converting and moving video:", src_video)
    os.system(f"ffmpeg -y -i {src_video} -c:v libx264 -pix_fmt yuv420p {OUTPUT_VIDEO}")
    
    artifact_video = ARTIFACT_DIR / "demo.mp4"
    shutil.copy2(OUTPUT_VIDEO, artifact_video)
    print("Done! Video saved to:", OUTPUT_VIDEO, "and", artifact_video)

if __name__ == "__main__":
    asyncio.run(record())
