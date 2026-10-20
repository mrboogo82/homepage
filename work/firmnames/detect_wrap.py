#!/usr/bin/env python3
"""Supplementary detection: gray boxes at a line start whose PREVIOUS line ends with a firm prefix
(법무법인 / 법률사무소 / 법무조합 / (유한)) — i.e. the firm name wrapped to the next line.
Also: boxes whose left text was not readable in the first pass. Usage: detect_wrap.py out.json img...
"""
import sys, os, json
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from detect import boxes_of, ocr, ends_with_prefix

def process(path):
    im = Image.open(path).convert('RGB')
    a = np.asarray(im)
    W, H = im.size
    res = []
    for (x, y, w, h) in boxes_of(a):
        if x > 460:
            continue  # the first pass already read the left context
        # previous line: strip above the box, from x-20 to the right edge
        py0 = max(0, y - int(1.9 * h)); py1 = max(0, y - 2)
        if py1 - py0 < 12:
            continue
        crop = im.crop((max(0, x - 20), py0, W, py1))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        txt = ocr(crop)
        ep = ends_with_prefix(txt or '')
        if ep:
            res.append({'box': [x, y, w, h], 'prev_line': (txt or '')[-40:], 'left_prefix': ep[0], 'wrapped': True})
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
