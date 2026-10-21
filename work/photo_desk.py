"""첫 화면(휴대전화) 윗부분 배경 사진 만들기.

원본: 본인이 보낸 사무실 사진(창가에서 판례집을 읽는 모습, 1792×2400).
위쪽 62.5%(y 0~1500)를 가로 전체로 잘라(가로세로 1.195:1) 1440px 폭 WebP로 저장.
밝은 느낌이 나도록 아주 조금만 밝기를 올리고 대비를 낮춘다(과한 보정은 하지 않음).
"""
import sys
from PIL import Image, ImageEnhance

src, out_webp, out_jpg = sys.argv[1:4]
im = Image.open(src).convert("RGB")
W, H = im.size
crop = im.crop((0, 0, W, 1500))          # 1792×1500
crop = ImageEnhance.Brightness(crop).enhance(1.05)
crop = ImageEnhance.Contrast(crop).enhance(0.96)
# 그림자를 살짝 들어올림(감마 0.93)
lut = [round(255 * (i / 255) ** 0.93) for i in range(256)] * 3
crop = crop.point(lut)
crop = crop.resize((1440, round(1500 * 1440 / W)), Image.LANCZOS)
crop.save(out_webp, "WEBP", quality=80, method=6)
crop.save(out_jpg, "JPEG", quality=82, optimize=True, progressive=True)
print(crop.size)
