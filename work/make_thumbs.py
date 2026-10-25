#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사례 카드용 작은 판결문 그림(썸네일) 만들기 (2026. 10. 25.)

왜: 홈·전체 사례 페이지의 카드는 판결문 그림(1240px 폭, 세로 1,750~4,900px)을 16:10 상자에 맞춰 보였는데,
    카드 하나에 2~6백만 화소짜리 JPG를 내려받아 풀어야 해서 전체 사례 페이지(카드 271장)에서 스크롤이 버벅였다(본인 지적).
    카드에는 판결문 첫 면의 윗부분만 보이므로(object-fit: cover, 위 기준), 그 부분만 잘라 640×480(4:3)으로 줄인 그림을 따로 두고
    카드의 <img> 에는 그것(thumb)을, 크게 보기 창에는 원본(src)을 쓴다. 목록 보기의 4:3 상자에는 그대로, 카드 보기의 16:10 상자에는 윗부분이 보인다.

어떻게: 사례마다 첫 그림(images[0].src — 카드에 보이는 그림)에 대해 cases/thumbs/<같은 이름>.jpg 를 만들고 images[0].thumb 에 적는다.
    ssr_cases.py 가 매번 부르므로(ensure_thumbs) 따로 돌릴 일은 없고, 새 사례를 더한 뒤 ssr_cases.py 를 돌리면 저절로 생긴다.
    원본이 썸네일보다 새로우면(다시 가린 경우) 다시 만들고, 더는 쓰지 않는 썸네일은 지운다. Pillow 가 없으면 아무것도 하지 않고 알린다.

사용법 (저장소 최상위에서, 손으로 돌릴 때):
    python3 work/make_thumbs.py .           # 없는 것·오래된 것 만들고 cases-data.js 의 thumb 갱신
    python3 work/make_thumbs.py . --check   # 빠진 것이 있는지만
"""
import os
import sys

THUMB_DIR = "cases/thumbs"
THUMB_W, THUMB_H = 640, 480     # 4:3 — 목록 보기의 상자와 같고, 카드 보기(16:10)에서는 윗부분이 보인다
QUALITY = 72


def thumb_path_for(src):
    """원본 경로(cases/xxx.jpg) → 썸네일 경로(cases/thumbs/xxx.jpg)."""
    return THUMB_DIR + "/" + os.path.splitext(os.path.basename(src))[0] + ".jpg"


def first_image(c):
    for im in (c.get("images") or []):
        if im and im.get("src"):
            return im
    return None


def make_one(site, src, dst):
    from PIL import Image
    with Image.open(os.path.join(site, src)) as im:
        im = im.convert("RGB")
        w, h = im.size
        crop_h = min(h, int(round(w * THUMB_H / THUMB_W)))
        box = im.crop((0, 0, w, crop_h))
        if crop_h < w * THUMB_H / THUMB_W:   # 원본이 4:3 보다 납작하면 아래를 흰색으로 채움
            canvas = Image.new("RGB", (w, int(round(w * THUMB_H / THUMB_W))), "white")
            canvas.paste(box, (0, 0)); box = canvas
        box = box.resize((THUMB_W, THUMB_H), Image.LANCZOS)
        os.makedirs(os.path.dirname(os.path.join(site, dst)), exist_ok=True)
        box.save(os.path.join(site, dst), "JPEG", quality=QUALITY, optimize=True, progressive=True)


def ensure_thumbs(site, cases, write=True):
    """cases(목록, 제자리에서 고침)의 첫 그림마다 썸네일을 두고 thumb 를 적는다.
    돌려주는 값: (만든 수, 빠진 수, 지운 수, 데이터가 바뀌었는지). write=False 면 파일을 만들지도 지우지도 않고 세기만 한다."""
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("Pillow 가 없어 사례 카드용 썸네일을 만들지 못합니다(pip install pillow). 카드는 원본 그림을 그대로 씁니다.")
        return 0, 0, 0, False
    made = missing = removed = 0
    changed = False
    wanted = set()
    for c in cases:
        im = first_image(c)
        if not im:
            continue
        src = im["src"]
        sp = os.path.join(site, src)
        if not os.path.exists(sp):
            continue
        dst = thumb_path_for(src)
        dp = os.path.join(site, dst)
        wanted.add(os.path.basename(dst))
        stale = not os.path.exists(dp) or os.path.getmtime(dp) < os.path.getmtime(sp)
        if stale:
            if write:
                make_one(site, src, dst); made += 1
            else:
                missing += 1
        if im.get("thumb") != dst:
            if write:
                im["thumb"] = dst
            changed = True
    tdir = os.path.join(site, THUMB_DIR)
    if os.path.isdir(tdir):
        for name in sorted(os.listdir(tdir)):
            if name.lower().endswith(".jpg") and name not in wanted:
                if write:
                    os.remove(os.path.join(tdir, name))
                removed += 1
    return made, missing, removed, changed


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    site = args[0] if args else "."
    check = "--check" in sys.argv
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ssr_cases import load_cases, save_cases
    cases = load_cases(site)
    made, missing, removed, changed = ensure_thumbs(site, cases, write=not check)
    if check:
        ok = not missing and not removed and not changed
        print("썸네일 %s: 빠짐 %d, 남은 군더더기 %d, 데이터 갱신 필요 %s" % ("일치" if ok else "불일치", missing, removed, "있음" if changed else "없음"))
        sys.exit(0 if ok else 1)
    if changed:
        save_cases(site, cases)
    print("썸네일: 만듦 %d, 지움 %d, cases-data.js thumb %s" % (made, removed, "갱신" if changed else "그대로"))


if __name__ == "__main__":
    main()
