#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""판결문 PDF에서 면을 1240px 폭으로 그려 내고, 글자 상자(글자층 또는 OCR)를 얻어 가림 상자를 그리고,
기존 게시 이미지 아래에 이어 붙이는 도구 모음 (2026. 10. 20. 주문 보완 작업)."""
import json, os, re, subprocess, sys, tempfile
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import numpy as np

W = 1240
GRAY = (0x3d, 0x40, 0x45)
TESSDATA = '/tmp/claude-0/-home-claude/448991fe-19fd-53f3-b941-ffdd0cce2d30/scratchpad/tessdata'


def page_count(pdf):
    with fitz.open(pdf) as d:
        return d.page_count


def render(pdf, pno, width=W):
    """pno: 0-based. returns PIL RGB image width px wide."""
    with fitz.open(pdf) as d:
        p = d[pno]
        s = width / p.rect.width
        pix = p.get_pixmap(matrix=fitz.Matrix(s, s), alpha=False)
        return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def text_words(pdf, pno, width=W):
    """글자층 단어 상자 [(x0,y0,x1,y1,text)] in 1240px 좌표. 없으면 []"""
    with fitz.open(pdf) as d:
        p = d[pno]
        s = width / p.rect.width
        ws = p.get_text('words')
        out = []
        for x0, y0, x1, y1, t, *_ in ws:
            t = t.strip()
            if not t:
                continue
            out.append((x0 * s, y0 * s, x1 * s, y1 * s, t))
        return out


def ocr_words(img, scale=2):
    """tesseract TSV로 단어 상자. img: PIL (1240 폭). 2배로 키워 읽고 좌표를 되돌린다."""
    big = img.resize((img.width * scale, img.height * scale), Image.LANCZOS)
    with tempfile.TemporaryDirectory() as td:
        pth = os.path.join(td, 'p.png')
        big.save(pth)
        env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)
        r = subprocess.run(['tesseract', pth, 'stdout', '-l', 'kor', '--psm', '4', 'tsv'],
                           capture_output=True, text=True, env=env)
    out = []
    for line in r.stdout.split('\n')[1:]:
        f = line.split('\t')
        if len(f) < 12:
            continue
        try:
            conf = float(f[10])
        except ValueError:
            continue
        t = f[11].strip()
        if not t or conf < 0:
            continue
        x, y, w, h = map(int, f[6:10])
        out.append((x / scale, y / scale, (x + w) / scale, (y + h) / scale, t))
    return out


def get_words(pdf, pno, img=None):
    ws = text_words(pdf, pno)
    if len(ws) >= 20:
        return ws, 'text'
    if img is None:
        img = render(pdf, pno)
    return ocr_words(img), 'ocr'


def lines_of(words, ytol=None):
    """단어를 줄로 묶는다. returns list of lines; each line = list of words sorted by x."""
    ws = sorted(words, key=lambda w: ((w[1] + w[3]) / 2, w[0]))
    lines = []
    for w in ws:
        cy = (w[1] + w[3]) / 2
        hh = w[3] - w[1]
        tol = ytol or max(6, hh * 0.5)
        placed = False
        for ln in lines:
            lcy = sum((v[1] + v[3]) / 2 for v in ln) / len(ln)
            if abs(lcy - cy) <= tol:
                ln.append(w); placed = True; break
        if not placed:
            lines.append([w])
    for ln in lines:
        ln.sort(key=lambda w: w[0])
    lines.sort(key=lambda ln: sum((v[1] + v[3]) / 2 for v in ln) / len(ln))
    return lines


def norm(s):
    return re.sub(r'[\s·\.,;:()\[\]「」『』\'"“”‘’·‧ㆍ_\-~]', '', s)


def find_spans(lines, needles):
    """각 줄의 글자를 이어 붙인 문자열에서 needles(정규화 문자열)를 찾아 해당 단어 상자들을 모아 돌려준다.
    returns (boxes, missing) ; boxes = [(x0,y0,x1,y1,needle)]"""
    boxes = []
    found = set()
    for ln in lines:
        # char index -> word index map
        txt = ''
        cmap = []
        for wi, w in enumerate(ln):
            t = norm(w[4])
            txt += t
            cmap += [wi] * len(t)
        for nd in needles:
            n = norm(nd)
            if not n:
                continue
            start = 0
            while True:
                i = txt.find(n, start)
                if i < 0:
                    break
                wis = sorted(set(cmap[i:i + len(n)]))
                x0 = min(ln[k][0] for k in wis); y0 = min(ln[k][1] for k in wis)
                x1 = max(ln[k][2] for k in wis); y1 = max(ln[k][3] for k in wis)
                # 단어 안의 부분만 가리려면 글자 비율로 나눈다 (한 단어 안에 조사 등이 붙은 경우)
                if len(wis) == 1:
                    w = ln[wis[0]]
                    t = norm(w[4])
                    j = t.find(n)
                    if j >= 0 and len(t) > len(n):
                        cw = (w[2] - w[0]) / len(t)
                        x0 = w[0] + cw * j
                        x1 = w[0] + cw * (j + len(n))
                boxes.append((x0, y0, x1, y1, nd))
                found.add(nd)
                start = i + len(n)
    missing = [nd for nd in needles if nd not in found]
    return boxes, missing


def draw_boxes(img, boxes, color=GRAY, pad=2):
    d = ImageDraw.Draw(img)
    for b in boxes:
        x0, y0, x1, y1 = b[:4]
        d.rectangle([x0 - pad, y0 - pad, x1 + pad, y1 + pad], fill=color)
    return img


def white_rects(img, rects):
    d = ImageDraw.Draw(img)
    for r in rects:
        d.rectangle(list(r[:4]), fill=(255, 255, 255))
    return img


def separator(img_w=W):
    """Version 50 식 구분: 22px 흰 여백 + 1px 회색(200) 선(x 40~1200) + 여백 없음(다음 면의 여백이 이어짐)"""
    sep = Image.new('RGB', (img_w, 23), (255, 255, 255))
    d = ImageDraw.Draw(sep)
    d.line([(40, 22), (1200, 22)], fill=(200, 200, 200), width=1)
    return sep


def compose(base_img, pages):
    """base_img: 기존 게시 이미지(PIL). pages: 더할 면 이미지 목록. 각 면 앞에 구분선."""
    parts = [base_img]
    for p in pages:
        parts.append(separator(base_img.width))
        if p.width != base_img.width:
            p = p.resize((base_img.width, int(p.height * base_img.width / p.width)), Image.LANCZOS)
        # 위쪽 흰 여백은 첫 글줄 60px 위까지만 남긴다(Version 50의 '내용 부분만' 방식과 비슷하게)
        a = np.array(p.convert('L'))
        ink = np.where((a < 200).sum(axis=1) > 2)[0]
        if len(ink):
            top = max(0, int(ink[0]) - 60)
            p = p.crop((0, top, p.width, p.height))
        parts.append(p)
    H = sum(p.height for p in parts)
    out = Image.new('RGB', (base_img.width, H), (255, 255, 255))
    y = 0
    for p in parts:
        out.paste(p, (0, y)); y += p.height
    return out


def page_text(pdf, pno, img=None):
    """읽기용 글: 글자층이 있으면 그것, 없으면 OCR."""
    with fitz.open(pdf) as d:
        t = d[pno].get_text('text')
    if len(t.strip()) >= 40:
        return t, 'text'
    if img is None:
        img = render(pdf, pno)
    with tempfile.TemporaryDirectory() as td:
        pth = os.path.join(td, 'p.png')
        img.resize((img.width * 2, img.height * 2), Image.LANCZOS).save(pth)
        env = dict(os.environ, TESSDATA_PREFIX=TESSDATA)
        r = subprocess.run(['tesseract', pth, 'stdout', '-l', 'kor', '--psm', '4'],
                           capture_output=True, text=True, env=env)
    return r.stdout, 'ocr'
