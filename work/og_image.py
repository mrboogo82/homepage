"""og-image.jpg(링크 공유용 1200×630)를 work/og_image.html에서 찍어 만든다.

    python3 work/og_image.py            # 저장소 루트에서 실행 → og-image.jpg 덮어씀

크로미움(playwright)이 필요하다. 글꼴은 Google Fonts에서 내려받으므로 네트워크가 있어야 Noto Serif KR·Noto Sans KR로 찍힌다.
"""
import asyncio
import os
import sys

from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "work", "og_image.html")
OUT = os.path.join(ROOT, "og-image.jpg")


async def main():
    exe = os.environ.get("CHROMIUM", "/opt/pw-browsers/chromium")
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=exe if os.path.exists(exe) else None)
        ctx = await browser.new_context(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        page = await ctx.new_page()
        await page.goto("file://" + SRC, wait_until="load")
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(600)
        await page.screenshot(path=OUT, type="jpeg", quality=90, clip={"x": 0, "y": 0, "width": 1200, "height": 630})
        await browser.close()
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
