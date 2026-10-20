import sys, pathlib, html, asyncio
from playwright.async_api import async_playwright
# 로고 폴더의 파일을 흰 칸에 늘어놓은 대조표 그림을 만든다: python3 work/logos-src/sheet.py logos sheet.png
raw = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'logos').resolve()
out_png = sys.argv[2] if len(sys.argv) > 2 else 'sheet.png'
files = sorted([p for p in raw.iterdir() if p.suffix in ('.svg','.png','.jpg','.gif','.webp')])
cards = ''.join(f'<figure><div class="box"><img src="file://{p}"></div><figcaption>{html.escape(p.name)}</figcaption></figure>' for p in files)
doc = f'''<!doctype html><meta charset="utf-8"><style>body{{margin:0;padding:16px;background:#e9e9e9;font:12px/1.4 sans-serif}} .g{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}} figure{{margin:0;background:#fff;border:1px solid #ccc;padding:8px}} .box{{height:110px;display:flex;align-items:center;justify-content:center;background:#fff}} img{{max-width:92%;max-height:80px}} figcaption{{text-align:center;color:#555;margin-top:6px}}</style><div class="g">{cards}</div>'''
out = pathlib.Path(out_png).with_suffix('.html'); out.write_text(doc)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1100,'height':800}, device_scale_factor=1)
        await pg.goto(out.resolve().as_uri()); await pg.wait_for_timeout(500)
        await pg.screenshot(path=out_png, full_page=True); await b.close()
asyncio.run(main())
print('ok', len(files))
