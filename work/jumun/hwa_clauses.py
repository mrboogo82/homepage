#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""제소전화해 화해조서 게시 이미지(1면 + 2~4면 이어 붙인 1240px JPEG)에서
제목 줄(법원명·화해조서·사건)과 '화해조항' 부분만 남기고, 화해조항 안의 금액(…원)을 진회색으로 가린다.
    python3 work/jumun/hwa_clauses.py <base> [--end-needle 마지막 화해조항 줄의 글자]
      → $HWA_OUT/out/<base>.jpg, $HWA_OUT/preview/<base>-NN.png (HWA_OUT 기본값: 이 파일의 폴더; TESSDATA_PREFIX에 kor 모델)
    2026. 10. 21. 본인 지시: 화해조서는 화해조항만 보이고 금액은 모두 가림(README-게시방법.txt).
"""
import os, re, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tools
from PIL import Image, ImageDraw
import numpy as np

tools.TESSDATA = os.environ.get("TESSDATA_PREFIX", tools.TESSDATA)
HERE = os.environ.get('HWA_OUT', os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get('HWA_SRC', os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'cases'))

base = sys.argv[1]
end_needle = None
if '--end-needle' in sys.argv:
    end_needle = sys.argv[sys.argv.index('--end-needle') + 1]

img = Image.open(f'{SRC}/{base}.jpg').convert('RGB')
W, H = img.size
a = np.array(img.convert('L')).astype(int)

# 1) 구분선(1px 회색 200, x 40~1200) 찾기 → 면 경계
rows = []
for y in range(H):
    seg = a[y, 40:1200]
    if ((seg > 185) & (seg < 215)).sum() > 1100 and (a[y, :30] > 245).all():
        rows.append(y)
# 인접 행 묶기
seps = []
for y in rows:
    if seps and y - seps[-1][-1] <= 1:
        seps[-1].append(y)
    else:
        seps.append([y])
sep_rows = [s[0] for s in seps]
print('separator rows:', sep_rows)
bounds = []
prev = 0
for s in sep_rows:
    bounds.append((prev, s - 22))   # 구분선 위 22px 흰 여백 앞까지가 그 면
    prev = s + 1
bounds.append((prev, H))
print('page bounds:', bounds)
assert len(bounds) == 4, bounds

pages = [img.crop((0, y0, W, y1)) for (y0, y1) in bounds]

def ink_rows(p):
    g = np.array(p.convert('L'))
    return np.where((g < 200).sum(axis=1) > 2)[0]

# 2) 면마다 OCR
words = [tools.ocr_words(p, scale=2) for p in pages]
lines = [tools.lines_of(w) for w in words]

def line_text(ln):
    return ''.join(w[4] for w in ln)

def find_line(lns, needle):
    n = tools.norm(needle)
    for ln in lns:
        if n in tools.norm(line_text(ln)):
            return ln
    return None

def lbox(ln):
    return (min(w[0] for w in ln), min(w[1] for w in ln), max(w[2] for w in ln), max(w[3] for w in ln))

# 3) 1면: 제목 블록(법원명~사건 줄)과 '화해조항' 부분
p1 = pages[0]
ir = ink_rows(p1)
first_ink = int(ir[0])
ln_case = find_line(lines[0], '사건')   # '사 건 2025자… 건물명도' 줄 (첫 '사건' 포함 줄)
# '사건' 글자가 든 줄 중 가장 위의 것
cands = [ln for ln in lines[0] if re.search(r'\d{4}자\d{3,}', tools.norm(line_text(ln)))]
assert cands, 'case line not found'
ln_case = sorted(cands, key=lambda ln: lbox(ln)[1])[0]
case_bottom = int(lbox(ln_case)[3])
ln_head = find_line(lines[0], '화해조항')
assert ln_head, 'heading not found'
head_top = int(lbox(ln_head)[1])
last_ink_p1 = int(ir[-1])
title_block = p1.crop((0, max(0, first_ink - 60), W, case_bottom + 18))
clause_p1 = p1.crop((0, head_top - 28, W, last_ink_p1 + 24))
print('title block', title_block.size, 'clause part p1', clause_p1.size, 'head_top', head_top)

# 4) 4면: 마지막 화해조항 줄까지만
p4 = pages[3]
if end_needle:
    ln_end = find_line(lines[3], end_needle)
    assert ln_end, 'end needle not found: ' + end_needle
    end_bottom = int(lbox(ln_end)[3])
    p4 = p4.crop((0, 0, W, end_bottom + 40))
    print('page 4 cut after', repr(line_text(ln_end)[:40]), '->', p4.size)
else:
    ir4 = ink_rows(p4)
    p4 = p4.crop((0, 0, W, int(ir4[-1]) + 40))
    print('page 4 trimmed ->', p4.size)

# 5) 금액 가림: 각 면의 줄에서 '숫자…원' 찾기 (정규화 뒤 숫자 5자리 이상 + 원)
#    한 단어 안의 일부만 가릴 때는 글자 너비 가중치(숫자·쉼표·괄호는 한글의 절반 안팎)로 자리를 나눈다.
def cw(ch):
    if ch.isdigit():
        return 0.52
    if ch in ',.':
        return 0.26
    if ch in '()':
        return 0.38
    if ch.isascii():
        return 0.5
    return 1.0

def amount_spans(ln):
    """줄 안의 '숫자{5,}원'을 (x0,y0,x1,y1,text)로. 단어 경계와 무관하게 글자 단위로 자리 계산."""
    chars = []   # (char, x0, x1, y0, y1)
    for w in ln:
        t = w[4]
        if not t:
            continue
        tot = sum(cw(c) for c in t) or 1
        x = w[0]; span = w[2] - w[0]
        for c in t:
            dx = span * cw(c) / tot
            chars.append((c, x, x + dx, w[1], w[3])); x += dx
    s = ''.join(c[0] for c in chars)
    out = []
    for m in re.finditer(r'\d[\d,.\s]{4,}원', s):
        i, j = m.start(), m.end()
        seg = chars[i:j]
        txt = m.group(0)
        if len(re.sub(r'\D', '', txt)) < 5:
            continue
        out.append((seg[0][1], min(c[3] for c in seg), seg[-1][2], max(c[4] for c in seg), txt))
    return out

amount_boxes = {}   # page index -> boxes
report = []
for pi in range(4):
    boxes = []
    for ln in lines[pi]:
        boxes += amount_spans(ln)
    amount_boxes[pi] = boxes
    report.append((pi + 1, [b[4] for b in boxes]))
    print(f'page {pi+1}: amounts', [b[4] for b in boxes])

def mask_on(pimg, boxes, dy=0):
    d = ImageDraw.Draw(pimg)
    for b in boxes:
        x0, y0, x1, y1 = b[:4]
        # 글자 높이보다 조금 넉넉하게
        d.rectangle([x0 - 3, y0 - dy - 3, x1 + 3, y1 - dy + 3], fill=tools.GRAY)

# 1면 화해조항 부분에 든 금액(없겠지만) 좌표 보정
mask_on(clause_p1, [b for b in amount_boxes[0] if b[1] >= head_top - 28], dy=head_top - 28)
def trim_bottom(p, margin=44):
    r = ink_rows(p)
    return p.crop((0, 0, p.width, min(p.height, int(r[-1]) + margin)))

p2 = trim_bottom(pages[1].copy()); mask_on(p2, amount_boxes[1])
p3 = trim_bottom(pages[2].copy()); mask_on(p3, amount_boxes[2])
mask_on(p4, [b for b in amount_boxes[3] if b[3] <= p4.height])

# 6) 이어 붙이기: 제목 블록 → 구분선 → 화해조항(1면) → 구분선 → 2면 → 구분선 → 3면 → 구분선 → 4면
parts = [title_block, tools.separator(W), clause_p1, tools.separator(W), p2, tools.separator(W), p3, tools.separator(W), p4]
Ht = sum(p.height for p in parts)
out = Image.new('RGB', (W, Ht), (255, 255, 255))
y = 0
for p in parts:
    out.paste(p, (0, y)); y += p.height
os.makedirs(f'{HERE}/out', exist_ok=True)
out.save(f'{HERE}/out/{base}.jpg', quality=88, subsampling=0)
print('saved', out.size)

# 미리보기 조각(절반 크기)
os.makedirs(f'{HERE}/preview', exist_ok=True)
n = 0
for yy in range(0, Ht, 1300):
    s = out.crop((0, yy, W, min(Ht, yy + 1300)))
    s.resize((W // 2, s.height // 2)).save(f'{HERE}/preview/{base}-{n:02d}.png'); n += 1
json.dump({'sep_rows': sep_rows, 'bounds': bounds, 'report': report}, open(f'{HERE}/out/{base}.json', 'w'), ensure_ascii=False, indent=1)
