"""항목별 페이지(경력·다루는 사건·언론보도·상담 문의)의 여백에 넣는 사진 세 장 만들기 (2026. 10. 26. 밤).

본인 지시: "전체 페이지 말고, 세부 페이지 여백마다 위 사진들을 적절히 넣어줘. … 증명사진의 경우 허리가 너무 길게 나와 보이므로
필요하면 가슴 부분 상반신만 나오게끔 하는 게 바람직해 보여."

원본 두 장(저장소에는 없음 — 본인이 2026. 10. 26. 보낸 파일):
  ① 증명사진 720×960 JPG(팔짱을 낀 정장 차림, 회색 바탕)
  ② 제미나이로 만든 사무실 장면 2816×1536 PNG(서가 앞 책상에서 서류를 읽는 모습; 오른쪽 아래 구석에 제미나이 표식이 있어 자르는 범위에서 뺀다)

만드는 파일(모두 WebP):
  photo-portrait.webp      ① y 10~770 · x 56~664 → 608×760 (4:5) — 머리 위 여백 조금과 팔짱 낀 팔까지만(허리 아래는 뺌).
                           경력·언론보도 페이지 제목 머리의 오른쪽, 상담 문의 페이지 '연락처' 칸 아래.
  photo-office-wide.webp   ② x 700~2660 · y 50~1357 → 1440×960 (3:2) — 창가 서류 더미·인물·서가. 다루는 사건·상담 문의 페이지 제목 머리의 오른쪽(넓은 화면).
  photo-office-tall.webp   ② x 1180~2284 · y 0~1380 → 720×900 (4:5) — 인물 위주의 세로 조각. 휴대전화(760px 이하)의 제목 머리와 언론보도 페이지 '언론보도' 칸 아래.
사무실 사진에는 첫 화면 사진(work/photo_desk.py)과 같은 보정(밝기 +5%·대비 −4%·감마 0.93)을 준다. 증명사진은 스튜디오 사진이라 손대지 않는다.

쓰는 법: python3 work/photo_pages.py 증명사진.jpg 사무실.png ./
"""
import os
import sys

from PIL import Image, ImageEnhance

portrait_src, office_src, out_dir = sys.argv[1:4]


def enhance(c):
    c = ImageEnhance.Brightness(c).enhance(1.05)
    c = ImageEnhance.Contrast(c).enhance(0.96)
    lut = [round(255 * (i / 255) ** 0.93) for i in range(256)] * 3
    return c.point(lut)


def save(img, name, quality):
    path = os.path.join(out_dir, name)
    img.save(path, "WEBP", quality=quality, method=6)
    print(name, img.size, os.path.getsize(path) // 1024, "KB")


portrait = Image.open(portrait_src).convert("RGB")
assert portrait.size == (720, 960), portrait.size
save(portrait.crop((56, 10, 664, 770)), "photo-portrait.webp", 86)

office = Image.open(office_src).convert("RGB")
assert office.size == (2816, 1536), office.size
wide = enhance(office.crop((700, 50, 2660, 1357))).resize((1440, 960), Image.LANCZOS)
save(wide, "photo-office-wide.webp", 80)
tall = enhance(office.crop((1180, 0, 2284, 1380))).resize((720, 900), Image.LANCZOS)
save(tall, "photo-office-tall.webp", 80)
