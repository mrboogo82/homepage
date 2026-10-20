#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""spec/<base>.json 대로 더할 면을 가리고 기존 게시 이미지 아래에 이어 붙여 out/cases/<base>.jpg 를 만든다.
spec 형식:
{ "pdf": "...", "pages": [ {"pno": 2, "mask": ["가릴 글자", ...], "boxes": [[x0,y0,x1,y1],...], "white": [[x0,y0,x1,y1],...],
                            "white_after": "이 글자가 든 줄부터 아래를 흰색(쪽번호 제외)" } ],
  "alt": "제1면·제2면(주문)" }
    python3 apply.py <base> [--show]"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
import tools
from PIL import Image

ROOT = '/home/claude/jumun2'
REPO = '/home/claude/homepage'
base = sys.argv[1]
spec = json.load(open(f'{ROOT}/spec/{base}.json', encoding='utf-8'))
pdf = spec['pdf']
HEADER_PAT = re.compile(r'(개인정보|출력자|제출자|등록자|\d{4}-\d{6,}|열람용|음성출력|위변조|발급번호|발행번호)')
pages = []
report = []
for pg in spec['pages']:
    pno = pg['pno']
    img = Image.open(f'{ROOT}/raw/{base}-p{pno}.png').convert('RGB')
    wj = json.load(open(f'{ROOT}/words/{base}-p{pno}.json', encoding='utf-8'))
    words = [tuple(w) for w in wj['words']]
    if wj.get('how') == 'text':
        # 열람용 워터마크(옅은 회색) 지우기: 모든 채널이 165보다 밝은 화소는 흰색
        import numpy as np
        a = np.array(img)
        light = (a > 165).all(axis=2)
        a[light] = 255
        img = Image.fromarray(a)
    lines = tools.lines_of(words)
    boxes, missing = tools.find_spans(lines, pg.get('mask', []))
    # 머리글·꼬리말 자동 흰색: 상단 6% / 하단 6% 안의 줄 중 HEADER_PAT 에 걸리는 줄 전체
    H = img.height
    whites = [tuple(r) for r in pg.get('white', [])]
    for ln in lines:
        cy = sum((w[1] + w[3]) / 2 for w in ln) / len(ln)
        txt = ''.join(w[4] for w in ln)
        if (cy < H * 0.07 or cy > H * 0.93) and HEADER_PAT.search(txt) and not re.fullmatch(r'\s*\d+\s*/\s*\d+\s*', txt):
            x0 = min(w[0] for w in ln); x1 = max(w[2] for w in ln)
            y0 = min(w[1] for w in ln); y1 = max(w[3] for w in ln)
            whites.append((x0 - 4, y0 - 4, x1 + 4, y1 + 4))
    def line_y(needle):
        ys = [(min(w[1] for w in ln), max(w[3] for w in ln)) for ln in lines if tools.norm(needle) in tools.norm(''.join(w[4] for w in ln))]
        return ys
    # white_above: 이 글자가 든 줄 위쪽을 모두 흰색(스캔 머리글 잡음)
    wa = pg.get('white_above')
    if wa:
        ys = line_y(wa)
        if ys:
            whites.append((0, 0, img.width, min(y for y, _ in ys) - 8))
        else:
            report.append(f'white_above not found: {wa}')
    # white_below: 이 글자가 든 줄 아래쪽을 모두 흰색(스캔 꼬리말·바코드 잡음)
    wb = pg.get('white_below')
    if wb:
        ys = line_y(wb)
        if ys:
            whites.append((0, max(y for _, y in ys) + 8, img.width, img.height))
        else:
            report.append(f'white_below not found: {wb}')
    tools.white_rects(img, whites)
    tools.draw_boxes(img, boxes + [tuple(b) + ('box',) for b in pg.get('boxes', [])])
    pages.append(img)
    report.append(f'p{pno}: {len(boxes)} boxes, {len(whites)} whites' + (f', MISSING {missing}' if missing else ''))
    os.makedirs(f'{ROOT}/masked', exist_ok=True)
    img.save(f'{ROOT}/masked/{base}-p{pno}.png')

src = spec.get('src', f'cases/{base}.jpg')
basei = Image.open(os.path.join(REPO, src)).convert('RGB')
if spec.get('base_crop'):
    basei = basei.crop(tuple(spec['base_crop']))
out = tools.compose(basei, pages)
os.makedirs(f'{ROOT}/out/cases', exist_ok=True)
out.save(f'{ROOT}/out/cases/{base}.jpg', quality=88, subsampling=0)
print(base, out.size, '|', ' | '.join(report))
