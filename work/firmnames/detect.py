#!/usr/bin/env python3
"""Detect gray mask boxes in published judgment images that sit right after a law-firm prefix
(법무법인 / 법무법인(유한) / 법률사무소 / 법무조합) on the same line → those boxes hide a firm name.
Usage: detect.py out.json img1.jpg img2.jpg ...
"""
import sys, os, json, re, subprocess, tempfile
import numpy as np, cv2
from PIL import Image

GRAY = (61, 64, 69)
TOL = 16

def lev(a, b):
    if a == b: return 0
    la, lb = len(a), len(b)
    if la == 0: return lb
    if lb == 0: return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[lb]

PREFIXES = ['법무법인', '법률사무소', '법무조합', '(유한)', '유한)', '법무법인(유한)']

def ends_with_prefix(text):
    t = re.sub(r'\s+', '', text)
    t = t.replace('（', '(').replace('）', ')')
    best = None
    for p in PREFIXES:
        n = len(p)
        for extra in (0, 1):
            tail = t[-(n + extra):] if len(t) >= n + extra else t
            if not tail: continue
            d = lev(tail, p)
            if d <= (1 if n >= 4 else 0):
                if best is None or d < best[1]:
                    best = (p, d, t[-14:])
    return best

def starts_with_prefix(text):
    t = re.sub(r'\s+', '', text)
    for p in ['법무법인', '법률사무소', '법무조합']:
        head = t[:len(p)]
        if head and lev(head, p) <= 1:
            return (p, t[:14])
    return None

def ocr(im, psm=7):
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        path = f.name
    im.save(path)
    try:
        r = subprocess.run(['tesseract', path, 'stdout', '-l', 'kor', '--psm', str(psm)],
                           capture_output=True, text=True, timeout=120)
        return r.stdout.strip()
    finally:
        os.unlink(path)

def boxes_of(a):
    m = ((np.abs(a[..., 0].astype(int) - GRAY[0]) <= TOL) &
         (np.abs(a[..., 1].astype(int) - GRAY[1]) <= TOL) &
         (np.abs(a[..., 2].astype(int) - GRAY[2]) <= TOL)).astype(np.uint8)
    # close small gaps
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    out = []
    for i in range(1, n):
        x, y, w, h, area = stats[i]
        if w < 8 or h < 10 or h > 80 or area < 0.6 * w * h:
            continue
        out.append((int(x), int(y), int(w), int(h)))
    out.sort(key=lambda b: (b[1], b[0]))
    return out

def process(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im)
    W, H = im.size
    res = []
    for (x, y, w, h) in boxes_of(a):
        y0, y1 = max(0, y - 6), min(H, y + h + 6)
        left = None; right = None
        lx0 = max(0, x - 460)
        if x - lx0 > 20:
            crop = im.crop((lx0, y0, x - 1, y1))
            crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
            left = ocr(crop)
        rx1 = min(W, x + w + 320)
        if rx1 - (x + w) > 20:
            crop = im.crop((x + w + 1, y0, rx1, y1))
            crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
            right = ocr(crop)
        ep = ends_with_prefix(left or '')
        sp = starts_with_prefix(right or '')
        if ep or sp:
            res.append({'box': [x, y, w, h], 'left': (left or '')[-40:], 'right': (right or '')[:30],
                        'left_prefix': ep[0] if ep else None, 'right_prefix': sp[0] if sp else None})
    return {'image': os.path.basename(path), 'size': [W, H], 'firm_boxes': res}

if __name__ == '__main__':
    out = sys.argv[1]
    results = []
    for p in sys.argv[2:]:
        try:
            results.append(process(p))
        except Exception as e:
            results.append({'image': os.path.basename(p), 'error': str(e)})
        print(os.path.basename(p), len(results[-1].get('firm_boxes', [])), flush=True)
    json.dump(results, open(out, 'w'), ensure_ascii=False, indent=1)
