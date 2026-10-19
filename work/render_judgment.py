#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
판결문 본문(엘박스에 공개된 판결 글)을 법원 판결문 서식으로 다시 조판해 1면 이미지(1240px 폭 JPG)를 만든다.
HWP 판결문을 조판하던 종전 방식(hwp2pdf.py)과 같은 모양: 법원명 · 재판부 · 판결 · 사건/원고/피고/변론종결/판결선고 · 주문.
가림: 세그먼트에 {"m": true}가 있으면 진회색(#3d4045) 상자로 가린다(상대방 변호사 이름, 같은 줄의 다른 변호사 이름, 목록에 없는 로펌 이름 등).

spec(JSON):
{
  "out": "rnd-2019guhap102207.jpg",
  "court": "대전지방법원", "panel": "제1행정부", "kind": "판결",
  "rows": [
     ["사건", [["2019구합102207 정부출연지원금 환수처분에 대한 취소"]]],
     ["원고", [["A"], ["소송대리인 변호사 ", {"t":"이두철","m":true}]]],
     ...
  ],
  "jumun": ["원고의 청구를 기각한다.", "소송비용은 원고가 부담한다."]
}
rows의 각 값은 '줄'의 목록이고, 줄은 세그먼트(문자열 또는 {"t":..., "m":true})의 목록이다.
"""
import json
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1240, 1754
FONT = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
KR = 1
INK = (20, 20, 20)
MASK = (61, 64, 69)
LABEL_X, VALUE_X, RIGHT = 148, 355, 1095
LINE = 50


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size, index=KR)


def segs(line):
    out = []
    for s in line:
        if isinstance(s, str):
            out.append((s, False))
        else:
            out.append((s["t"], bool(s.get("m"))))
    return out


def text_w(d, t, f):
    return d.textlength(t, font=f)


def draw_segs(d, x, y, line, f):
    """세그먼트 목록을 한 줄에 그린다(가림 세그먼트는 상자)."""
    for t, m in segs(line):
        w = text_w(d, t, f)
        if m:
            asc, desc = f.getmetrics()
            d.rectangle([x, y + 2, x + w, y + asc + desc - 4], fill=MASK)
        else:
            d.text((x, y), t, font=f, fill=INK)
        x += w
    return x


def wrap_segs(d, line, f, width):
    """세그먼트 줄을 폭에 맞게 여러 줄로 나눈다(가림 세그먼트는 통째로 둔다)."""
    lines, cur, cur_w = [], [], 0
    for t, m in segs(line):
        if m:
            w = text_w(d, t, f)
            if cur and cur_w + w > width:
                lines.append(cur); cur, cur_w = [], 0
            cur.append({"t": t, "m": True}); cur_w += w
            continue
        # 공백 단위로 나누되, 한 낱말이 너무 길면 글자 단위
        words = t.split(" ")
        for i, wd in enumerate(words):
            piece = wd + (" " if i < len(words) - 1 else "")
            w = text_w(d, piece, f)
            if cur_w + w > width and cur:
                # 줄 끝 공백 제거
                lines.append(cur); cur, cur_w = [], 0
            if w > width:
                for ch in piece:
                    cw = text_w(d, ch, f)
                    if cur_w + cw > width and cur:
                        lines.append(cur); cur, cur_w = [], 0
                    cur.append(ch); cur_w += cw
            else:
                cur.append(piece); cur_w += w
    if cur:
        lines.append(cur)
    # 인접 문자열 합치기
    merged = []
    for ln in lines:
        m2 = []
        for s in ln:
            if isinstance(s, str) and m2 and isinstance(m2[-1], str):
                m2[-1] += s
            else:
                m2.append(s)
        if m2 and isinstance(m2[-1], str):
            m2[-1] = m2[-1].rstrip(" ")
        merged.append(m2)
    return merged


def spaced(label, slots=5):
    """'사건' → '사    건' 처럼 라벨 글자를 벌린다(5칸 기준)."""
    chars = list(label)
    if len(chars) == 1:
        return label
    if len(chars) == 2:
        return chars[0] + "        " + chars[1]
    if len(chars) == 3:
        return "   ".join(chars)
    return " ".join(chars)


def render(spec):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    f_title = font(36, True)
    f_panel = font(28, True)
    f_h = font(34, True)
    f_lab = font(27)
    f_val = font(27)

    y = 150
    t = " ".join(spec["court"])  # 글자 사이 띄움
    d.text(((W - text_w(d, t, f_title)) / 2, y), t, font=f_title, fill=INK)
    y += 62
    if spec.get("panel"):
        t = " ".join(spec["panel"])
        d.text(((W - text_w(d, t, f_panel)) / 2, y), t, font=f_panel, fill=INK)
        y += 56
    kind = spec.get("kind", "판결")
    t = "          ".join(kind) if len(kind) == 2 else " ".join(kind)
    d.text(((W - text_w(d, t, f_h)) / 2, y), t, font=f_h, fill=INK)
    y += 80

    for label, lines in spec["rows"]:
        d.text((LABEL_X, y), spaced(label), font=f_lab, fill=INK)
        first = True
        for line in lines:
            for wl in wrap_segs(d, line, f_val, RIGHT - VALUE_X):
                draw_segs(d, VALUE_X, y, wl, f_val)
                y += LINE
                first = False
        if first:
            y += LINE
    y += 60
    t = "주          문"
    d.text(((W - text_w(d, t, f_h)) / 2, y), t, font=f_h, fill=INK)
    y += 75
    for i, item in enumerate(spec["jumun"], 1):
        head = "%d. " % i
        hw = text_w(d, head, f_val)
        d.text((LABEL_X, y), head, font=f_val, fill=INK)
        wls = wrap_segs(d, [item] if isinstance(item, str) else item, f_val, RIGHT - LABEL_X - hw)
        for k, wl in enumerate(wls):
            draw_segs(d, LABEL_X + hw, y, wl, f_val)
            y += LINE
    if y > H - 80:
        raise SystemExit("한 면을 넘습니다: %s" % spec["out"])
    im.save(spec["out"], quality=90, subsampling=0)
    return spec["out"], y


if __name__ == "__main__":
    for p in sys.argv[1:]:
        spec = json.load(open(p, encoding="utf-8"))
        print(render(spec))
