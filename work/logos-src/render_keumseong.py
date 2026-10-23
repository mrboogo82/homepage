#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
법무법인(유한) 금성 가로형 로고(logos/keumseong.png, 828×168) 다시 만들기 (2026. 10. 23.)

keumseong_lockup_c.html(엠블럼 + 세리프 워드마크 "법무법인(유한) 금성" + KEUMSEONG LAW FIRM)을 Chromium으로 4배 확대 촬영한다.
엠블럼은 logos/keumseong-emblem.png(원래 로고 keumseong-logo@2x.png 에서 금색 화소만 추려 낸 134×166)이고,
글꼴은 npm 의 @fontsource/noto-serif-kr(500·700)·@fontsource/montserrat(600) — 이 작업 환경은 구글 글꼴 서버에 닿지 않아 패키지로 받았다.

    cd work/logos-src && npm i @fontsource/noto-serif-kr@5 @fontsource/montserrat@5 && python3 render_keumseong.py   # playwright 필요
→ 같은 폴더에 keumseong.png 가 생기니 logos/ 로 옮긴다. 법인 홈페이지 머리글·첫 화면·바닥글에 올린 로고와 같은 파일이다.
"""
import asyncio, os, shutil
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))

async def main():
    emblem = os.path.join(HERE, "emblem.png")
    if not os.path.exists(emblem):
        shutil.copy(os.path.join(HERE, "..", "..", "logos", "keumseong-emblem.png"), emblem)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(device_scale_factor=4, viewport={"width": 800, "height": 300})
        page = await ctx.new_page()
        await page.goto("file://" + os.path.join(HERE, "keumseong_lockup_c.html"))
        await page.evaluate("document.fonts.ready")
        await page.wait_for_timeout(300)
        fonts = await page.evaluate("[...document.fonts].map(f=>f.family+' '+f.weight+' '+f.status)")
        print(fonts)
        await page.locator("#lock").screenshot(path=os.path.join(HERE, "keumseong.png"), omit_background=True)
        await b.close()

asyncio.run(main())
