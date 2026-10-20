import asyncio, base64, pathlib
from playwright.async_api import async_playwright
S=pathlib.Path('/tmp/claude-0/-home-claude/63189853-a4d3-5547-a890-9915b6cad885/scratchpad')
svg=(S/'logos-raw/gwacheon-namu.svg').read_text(encoding='utf-8')
text_b64=base64.b64encode((S/'gwacheon-text.png').read_bytes()).decode()
A=48*3           # text height at 3x
sym_h=round(1.86*A); gap=round(0.2*A); drop=round(0.24*A)   # symbol bottom sits 0.24A below the text bottom
html=f'''<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;background:transparent}}
.w{{display:inline-flex;align-items:flex-end;gap:{gap}px;padding:4px}}
.sym{{height:{sym_h}px;width:auto}} .txt{{height:{48*3}px;width:auto;margin-bottom:{drop}px;image-rendering:auto}}</style>
<div class="w" id="w"><img class="sym" src="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}"><img class="txt" src="data:image/png;base64,{text_b64}"></div>'''
out=S/'gwacheon-compose.html'; out.write_text(html)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1200,'height':600}, device_scale_factor=1)
        await pg.goto(out.as_uri()); await pg.wait_for_timeout(300)
        el=await pg.query_selector('#w'); await el.screenshot(path=str(S/'final/gwacheon.png'), omit_background=True)
        await b.close()
asyncio.run(main())
