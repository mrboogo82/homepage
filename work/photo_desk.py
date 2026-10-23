"""첫 화면 배경 사진 만들기 (2026. 10. 21.).

원본: 본인이 보낸 사무실 사진(창가에서 판례집을 읽는 모습, 1792×2400 PNG — 저장소에는 없음).
두 장을 만든다(둘 다 가로 전체, 1440px 폭 WebP, 밝기 +5%·대비 −4%·그림자 살짝 들어올림):
  photo-desk.webp       y 255~1438 (1.515:1, 천장과 맨 위 서가 한 줄을 뺀 범위) — 휴대전화(760px 이하) 첫 화면 윗부분의 띠(66vw)
                        (처음 y 0~1500·1.195:1 → 13시 y 255~1505·1.434:1 → 13시 30분 y 255~1438·1.515:1, 띠가 높다는 지적에 따라 두 번 줄임)
  photo-desk-tall.webp  위쪽 y 0~2000 (0.896:1, 책상 위 판례집까지) — 넓은 화면 첫 화면 오른쪽 판
  photo-desk-mobile.webp y 336~1618 (1.398:1, 머리 위 서가 한 줄부터 가슴·판례집을 든 손까지) — 2026. 10. 23. 17시부터 휴대전화 띠(71.5vw).
                        본인 지시 "모바일에서는 사진이 목까지밖에 안 나온다 — 적어도 가슴 아래까지". photo-desk.webp는 이제 쓰지 않지만 남겨 둠.
                        (원본이 없을 때는 work/photo_desk_mobile.py 가 photo-desk-tall.webp에서 같은 범위(y 270~1300)를 잘라 만든다 — 2026. 10. 23. 실제로 그렇게 만듦.)

쓰는 법: python3 work/photo_desk.py 원본.png ./
"""
import sys, os
from PIL import Image, ImageEnhance

src, out_dir = sys.argv[1:3]
im = Image.open(src).convert("RGB")
W, H = im.size


def enhance(c):
    c = ImageEnhance.Brightness(c).enhance(1.05)
    c = ImageEnhance.Contrast(c).enhance(0.96)
    lut = [round(255 * (i / 255) ** 0.93) for i in range(256)] * 3   # 그림자를 살짝 들어올림(감마 0.93)
    return c.point(lut)


for name, top, bottom in (("photo-desk.webp", 255, 1438), ("photo-desk-tall.webp", 0, 2000), ("photo-desk-mobile.webp", 336, 1618)):
    crop = enhance(im.crop((0, top, W, bottom)))
    crop = crop.resize((1440, round((bottom - top) * 1440 / W)), Image.LANCZOS)
    path = os.path.join(out_dir, name)
    crop.save(path, "WEBP", quality=80, method=6)
    print(name, crop.size, os.path.getsize(path) // 1024, "KB")
