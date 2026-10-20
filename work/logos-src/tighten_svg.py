import asyncio, re, sys, pathlib, json
from playwright.async_api import async_playwright
# usage: tighten_svg.py out_dir in1.svg[:outname] in2.svg ...
out_dir=pathlib.Path(sys.argv[1]); out_dir.mkdir(exist_ok=True)
jobs=[]
for arg in sys.argv[2:]:
    src,_,name=arg.partition(':'); p=pathlib.Path(src); jobs.append((p, name or p.stem))
async def main():
    async with async_playwright() as pw:
        b=await pw.chromium.launch(); pg=await b.new_page()
        for p,name in jobs:
            s=p.read_text(encoding='utf-8')
            s=re.sub(r'<\?xml[^>]*\?>','',s); s=re.sub(r'<!DOCTYPE[^>]*>','',s,flags=re.S); s=re.sub(r'<!--.*?-->','',s,flags=re.S)
            s=re.sub(r'<metadata>.*?</metadata>','',s,flags=re.S).strip()
            await pg.set_content('<!doctype html><body style="margin:0">'+s)
            info=await pg.evaluate('''() => { const sv=document.querySelector('svg'); const bb=sv.getBBox(); const vb=sv.getAttribute('viewBox'); return {x:bb.x,y:bb.y,w:bb.width,h:bb.height,vb}; }''')
            m=0.01*max(info['w'],info['h'])
            vb=f"{info['x']-m:.2f} {info['y']-m:.2f} {info['w']+2*m:.2f} {info['h']+2*m:.2f}"
            # root tag edits: replace/add viewBox, drop width/height
            def fix_root(mo):
                tag=mo.group(0)
                tag=re.sub(r'\s(width|height)="[^"]*"','',tag)
                tag=re.sub(r'\sviewBox="[^"]*"','',tag)
                return tag[:-1]+f' viewBox="{vb}">'
            s2=re.sub(r'<svg\b[^>]*>',fix_root,s,count=1)
            (out_dir/f'{name}.svg').write_text(s2,encoding='utf-8')
            print(f"{name}: bbox {info['x']:.1f},{info['y']:.1f} {info['w']:.1f}x{info['h']:.1f} (old viewBox {info['vb']}) -> {len(s2)} B")
        await b.close()
asyncio.run(main())
