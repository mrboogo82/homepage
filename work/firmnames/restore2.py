#!/usr/bin/env python3
"""Box-driven un-masking of law-firm names.

Input: det_all.json (gray boxes that directly follow 법무법인/법률사무소/법무조합 in the published image)
       plan.json ({image, pdf:[...]})
For each flagged box: align the published box to the original page (page 1 = unshifted; appended 주문
segments found by template matching of the visible text left of the box), read the original text under the
box (text layer or OCR), keep only the firm-name words (stop at 담당변호사/변호사 ...), and copy the original
pixels back for that span only.

Usage: restore2.py det_all.json plan.json out_dir review_dir
"""
import sys, os, re, json, subprocess, tempfile
import numpy as np, cv2
import pymupdf
from PIL import Image

W_PUB = 1240
PAGE1_H = 1754
GRAY = np.array([61, 64, 69]); TOL = 16
CASES_DIR = '/home/claude/homepage/cases'
STOP_RE = re.compile(r'(담당변호사|변호사|소송복대리인|소송대리인|소송수행자|대리인|담당|^외$|^외[0-9]|^등$)')


def lev(a, b):
    la, lb = len(a), len(b)
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[lb]


def is_stop(tok):
    t = tok.replace(' ', '')
    if STOP_RE.search(t):
        return True
    return len(t) >= 4 and lev(t[:5], '담당변호사') <= 2


def render(page, zoom):
    pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    elif pix.n == 4:
        img = img[..., :3]
    return np.ascontiguousarray(img)


def ocr_words(img_rgb, scale=2.0, psm=7):
    big = cv2.resize(img_rgb, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        path = f.name
    Image.fromarray(big).save(path)
    try:
        r = subprocess.run(['tesseract', path, 'stdout', '-l', 'kor', '--psm', str(psm), 'tsv'],
                           capture_output=True, text=True, timeout=300)
    finally:
        os.unlink(path)
    raw = []
    for line in r.stdout.splitlines()[1:]:
        p = line.split('\t')
        if len(p) < 12 or p[0] != '5':
            continue
        txt = p[11].strip()
        if not txt:
            continue
        x, y, w, h = int(p[6]), int(p[7]), int(p[8]), int(p[9])
        raw.append({'bbox': [x / scale, y / scale, (x + w) / scale, (y + h) / scale], 'text': txt})
    raw.sort(key=lambda w: w['bbox'][0])
    merged = []
    for w in raw:
        if merged:
            p = merged[-1]
            h = max(p['bbox'][3] - p['bbox'][1], w['bbox'][3] - w['bbox'][1], 1)
            gap = w['bbox'][0] - p['bbox'][2]
            if gap <= 0.62 * h:
                p['text'] += w['text']
                p['bbox'] = [min(p['bbox'][0], w['bbox'][0]), min(p['bbox'][1], w['bbox'][1]),
                             max(p['bbox'][2], w['bbox'][2]), max(p['bbox'][3], w['bbox'][3])]
                continue
        merged.append(dict(w))
    return merged


def text_words_in(page, zoom, x0, y0, x1, y1):
    out = []
    for wx0, wy0, wx1, wy1, w, b, l, n in page.get_text('words'):
        bx0, by0, bx1, by1 = wx0 * zoom, wy0 * zoom, wx1 * zoom, wy1 * zoom
        ix = min(bx1, x1) - max(bx0, x0); iy = min(by1, y1) - max(by0, y0)
        if ix > 0.5 * (bx1 - bx0) and iy > 0.5 * (by1 - by0):
            out.append({'bbox': [bx0, by0, bx1, by1], 'text': w})
    out.sort(key=lambda w: w['bbox'][0])
    return out


def gray_mask(img):
    d = np.abs(img.astype(int) - GRAY)
    return (d[..., 0] <= TOL) & (d[..., 1] <= TOL) & (d[..., 2] <= TOL)


def ncc_at(pub_gray, orig_gray, x0, y0, x1, y1, win=6):
    """match pub template (x0,y0,x1,y1) in orig near same spot; return (dx,dy,score): orig = pub + (dx,dy)"""
    tpl = pub_gray[y0:y1, x0:x1]
    sx0 = max(0, x0 - win); sy0 = max(0, y0 - win)
    sx1 = min(orig_gray.shape[1], x1 + win); sy1 = min(orig_gray.shape[0], y1 + win)
    sub = orig_gray[sy0:sy1, sx0:sx1]
    if tpl.shape[0] < 8 or tpl.shape[1] < 20 or sub.shape[0] < tpl.shape[0] or sub.shape[1] < tpl.shape[1]:
        return None
    res = cv2.matchTemplate(sub, tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(res)
    return (sx0 + loc[0] - x0, sy0 + loc[1] - y0, float(mx))


def ncc_global(pub_gray, orig_gray, x0, y0, x1, y1):
    tpl = pub_gray[y0:y1, x0:x1]
    if tpl.shape[0] < 8 or tpl.shape[1] < 20 or tpl.std() < 5:
        return None
    res = cv2.matchTemplate(orig_gray, tpl, cv2.TM_CCOEFF_NORMED)
    _, mx, _, loc = cv2.minMaxLoc(res)
    return (loc[0] - x0, loc[1] - y0, float(mx))


class Doc:
    def __init__(self, pdf):
        self.doc = pymupdf.open(pdf)
        self.cache = {}

    def page(self, pno):
        if pno not in self.cache:
            page = self.doc[pno]
            zoom = W_PUB / page.rect.width
            orig = render(page, zoom)
            words = page.get_text('words')
            self.cache[pno] = (page, zoom, orig, cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY), len(words) > 20)
        return self.cache[pno]


def process(image, boxes, pdfs, out_dir, review_dir, log):
    pub = np.asarray(Image.open(os.path.join(CASES_DIR, image)).convert('RGB')).copy()
    pub_gray = cv2.cvtColor(pub, cv2.COLOR_RGB2GRAY)
    gm = gray_mask(pub)
    H, W = pub.shape[:2]
    before = pub.copy()
    docs = [Doc(p) for p in pdfs]
    restored, skipped = [], []
    seg_offsets = []
    for bi, b in enumerate(boxes):
        bx, by, bw, bh = b['box']
        rec = {'image': image, 'box': b['box'], 'left': b.get('left', '')[-20:]}
        # template: visible text left of the box
        tx0 = max(0, bx - 240); tx1 = bx - 2; ty0 = max(0, by - 5); ty1 = min(H, by + bh + 5)
        best = None  # (doc_i, pno, dx, dy, score)
        if by + bh < PAGE1_H + 10:
            for di, d in enumerate(docs):
                page, zoom, orig, og, tl = d.page(0)
                m = ncc_at(pub_gray, og, tx0, ty0, tx1, ty1)
                if m and (best is None or m[2] > best[4]):
                    best = (di, 0, m[0], m[1], m[2])
        else:
            # appended segment: the narrow strip template is precise but ambiguous (identical lines);
            # verify each strip peak with a tall (3-line) template and keep the best verified one.
            ty0b = max(0, by - 60); ty1b = min(H, by + bh + 60)
            tall = pub_gray[ty0b:ty1b, tx0:tx1]
            strip = pub_gray[ty0:ty1, tx0:tx1]
            cands = []
            for di, d in enumerate(docs):
                for pno in range(1, min(len(d.doc), 5)):
                    page, zoom, orig, og, tl = d.page(pno)
                    if strip.shape[0] < 8 or strip.shape[1] < 20 or strip.std() < 5:
                        continue
                    res = cv2.matchTemplate(og, strip, cv2.TM_CCOEFF_NORMED)
                    dil = cv2.dilate(res, np.ones((9, 9), np.float32))
                    ys, xs = np.where((res >= 0.85) & (res >= dil - 1e-6))
                    for yy, xx in zip(ys, xs):
                        dx_, dy_ = int(xx) - tx0, int(yy) - ty0
                        if abs(dx_) > 4:
                            continue
                        oy0, oy1 = ty0b + dy_, ty1b + dy_
                        ox0, ox1 = tx0 + dx_, tx1 + dx_
                        if oy0 < 0 or ox0 < 0 or oy1 > og.shape[0] or ox1 > og.shape[1]:
                            continue
                        sub = og[oy0:oy1, ox0:ox1]
                        tscore = float(cv2.matchTemplate(sub, tall, cv2.TM_CCOEFF_NORMED)[0, 0])
                        cands.append((di, pno, dx_, dy_, float(res[yy, xx]), tscore))
            if cands:
                cands.sort(key=lambda c: c[5], reverse=True)
                c = cands[0]
                rec['tall_score'] = round(c[5], 3)
                rec['n_cands'] = len(cands)
                if c[5] >= 0.35:
                    best = (c[0], c[1], c[2], c[3], c[4])
        if best is None or best[4] < 0.7:
            rec['why'] = 'no alignment'; rec['best'] = best; skipped.append(rec); continue
        di, pno, dx, dy, score = best
        page, zoom, orig, og, text_layer = docs[di].page(pno)
        rec.update({'pdf': os.path.basename(pdfs[di]), 'page': pno + 1, 'match': [dx, dy, round(score, 3)],
                    'text_layer': text_layer})
        # original region under the box
        ox0, oy0, ox1, oy1 = bx + dx, by + dy, bx + bw + dx, by + bh + dy
        if ox0 < 0 or oy0 < 0 or ox1 > orig.shape[1] or oy1 > orig.shape[0]:
            rec['why'] = 'orig out of bounds'; skipped.append(rec); continue
        if text_layer:
            words = text_words_in(page, zoom, ox0 - 2, oy0 - 2, ox1 + 2, oy1 + 2)
        else:
            crop = orig[max(0, oy0 - 3):oy1 + 3, max(0, ox0 - 3):ox1 + 3]
            words = ocr_words(crop)
            for w in words:
                w['bbox'] = [w['bbox'][0] + max(0, ox0 - 3), w['bbox'][1] + max(0, oy0 - 3),
                             w['bbox'][2] + max(0, ox0 - 3), w['bbox'][3] + max(0, oy0 - 3)]
        rec['words'] = [w['text'] for w in words]
        firm = []
        for w in words:
            t = w['text'].strip()
            if re.match(r'^\(?유한\)?[,.]?$', t):
                firm.append(w); continue
            if is_stop(t):
                break
            firm.append(w)
            if len([f for f in firm if not re.match(r'^\(?유한\)?[,.]?$', f['text'])]) >= 2:
                break
        # decide span (in original coords)
        if firm:
            span_x1 = max(w['bbox'][2] for w in firm) + 3
            if len(firm) == len(words):
                span_x1 = ox1  # whole box
            span_x1 = min(span_x1, ox1)
            name = ' '.join(w['text'] for w in firm)
        elif not words and bw <= 130:
            span_x1 = ox1; name = '(OCR 없음, 좁은 상자 전체)'
        else:
            rec['why'] = 'no firm words'; skipped.append(rec); continue
        if re.search(r'\d{6}', name):
            rec['why'] = 'digits in name'; skipped.append(rec); continue
        rec['name'] = name
        # sanity: name should be short
        if len(name.replace(' ', '')) > 14:
            rec['why'] = 'name too long'; skipped.append(rec); continue
        # paste into published image: span [bx, span_x1-dx) x [by, by+bh)
        px1 = int(round(span_x1 - dx))
        px0, py0, py1 = bx, by, by + bh
        if px1 <= px0 + 4:
            rec['why'] = 'empty span'; skipped.append(rec); continue
        py0e = max(0, py0 - 3); py1e = min(H, py1 + 3); px0e = max(0, px0 - 3)
        if px1 >= bx + bw - 2:
            px1 = min(W, px1 + 3)
        if py0e + dy < 0 or px0e + dx < 0 or py1e + dy > orig.shape[0] or px1 + dx > orig.shape[1]:
            rec['why'] = 'orig out of bounds'; skipped.append(rec); continue
        src = orig[py0e + dy:py1e + dy, px0e + dx:px1 + dx].copy()
        if not text_layer:
            lum = cv2.cvtColor(src, cv2.COLOR_RGB2GRAY)
            src[lum > 175] = 255
        sub_g = gm[py0e:py1e, px0e:px1].astype(np.uint8)
        sub_g = cv2.dilate(sub_g, np.ones((7, 7), np.uint8))
        region = pub[py0e:py1e, px0e:px1]
        region[sub_g > 0] = src[sub_g > 0]
        pub[py0e:py1e, px0e:px1] = region
        gm[py0e:py1e, px0e:px1] &= ~(sub_g > 0)
        rec['pub_span'] = [px0, py0, px1, py1]
        rec['partial'] = px1 < bx + bw - 2
        restored.append(rec)
    if restored:
        os.makedirs(out_dir, exist_ok=True)
        Image.fromarray(pub).save(os.path.join(out_dir, image), quality=92, subsampling=0)
        os.makedirs(review_dir, exist_ok=True)
        for k, rec in enumerate(restored):
            px0, py0, px1, py1 = rec['pub_span']
            cx0 = max(0, px0 - 330); cx1 = min(W, px1 + 330); cy0 = max(0, py0 - 8); cy1 = min(H, py1 + 8)
            a = before[cy0:cy1, cx0:cx1]; bimg = pub[cy0:cy1, cx0:cx1]
            sheet = np.vstack([a, np.full((4, a.shape[1], 3), 200, np.uint8), bimg])
            Image.fromarray(sheet).save(os.path.join(review_dir, f'{image[:-4]}_{k}.png'))
    for d in docs:
        d.doc.close()
    log.append({'image': image, 'restored': restored, 'skipped': skipped})
    return restored, skipped


if __name__ == '__main__':
    det = {r['image']: r for r in json.load(open(sys.argv[1]))}
    plan = json.load(open(sys.argv[2]))
    out_dir, review_dir = sys.argv[3], sys.argv[4]
    only = set(sys.argv[5].split(',')) if len(sys.argv) > 5 else None
    log = []
    for e in plan:
        if only and e['image'] not in only:
            continue
        boxes = [b for b in det.get(e['image'], {}).get('firm_boxes', []) if b.get('left_prefix')]
        if not boxes:
            continue
        try:
            r, s = process(e['image'], boxes, e['pdf'], out_dir, review_dir, log)
            print(e['image'], 'restored', len(r), 'skipped', len(s), [x['name'] for x in r], [(x.get('words'), x['why']) for x in s], flush=True)
        except Exception as ex:
            import traceback; traceback.print_exc()
            log.append({'image': e['image'], 'error': str(ex)})
    os.makedirs(out_dir, exist_ok=True)
    json.dump(log, open(os.path.join(out_dir, '_log.json'), 'w'), ensure_ascii=False, indent=1)
