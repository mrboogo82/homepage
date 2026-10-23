"""휴대전화 첫 화면 띠 사진 photo-desk-mobile.webp 만들기 — 원본 PNG가 없을 때 (2026. 10. 23. 17시).

photo-desk-tall.webp(원본 y 0~2000을 1440px 폭으로 줄인 것, 이미 밝기·대비 보정됨)에서 y 270~1300(원본 y 약 336~1618)을 잘라
1440×1030(1.398:1)으로 저장한다 — 머리 위 서가 한 줄부터 가슴·판례집을 든 손까지. 원본이 있으면 work/photo_desk.py 가 같은 범위를 원본에서 바로 만든다.

쓰는 법 (저장소 최상위에서): python3 work/photo_desk_mobile.py
"""
import os
from PIL import Image

TOP, BOTTOM = 270, 1300
im = Image.open("photo-desk-tall.webp").convert("RGB")
crop = im.crop((0, TOP, im.width, BOTTOM))
crop.save("photo-desk-mobile.webp", "WEBP", quality=82, method=6)
print("photo-desk-mobile.webp", crop.size, round(crop.width / crop.height, 3), os.path.getsize("photo-desk-mobile.webp") // 1024, "KB")
