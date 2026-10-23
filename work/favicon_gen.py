#!/usr/bin/env python3
"""홈페이지 파비콘 생성기 — 2026. 10. 23. '부' 한 글자 마크

2026. 10. 21.에는 바닥글 인장(辯護士 夫孝準, 두 줄)을 벡터로 옮겨 썼으나 작은 크기에서 글자가 읽히지 않아,
2026. 10. 23. 본인 요청으로 **크림슨 원판 + 흰 '부' 한 글자**(노토 명조 가장 굵은 굵기)로 바꿈.
안쪽 흰 테(인장 느낌)도 검토했으나 16~24px(탭·검색 결과)에서는 테가 뭉개지고 글자만 작아져서 빼고,
글자를 원판의 70%까지 키웠다. 16px은 획이 1px 안팎이라 외곽선에 얇은 선을 둘러 조금 굵게 그린다.
글자는 글꼴 외곽선(path)으로 넣으므로 글꼴 없이도 같은 모양. (옛 두 줄 인장 생성기는 git 이력 a3d1996 참고)

생성 파일(저장소 루트):
  favicon.svg             벡터 파비콘(크림슨 원판 + 흰 부, 바탕 투명)
  favicon.ico             16(조금 굵게)·32·48px
  apple-touch-icon.png    180px, 크림슨 바탕 꽉 채움(iOS가 모서리를 둥글림)
  icon-192.png, icon-512.png  안드로이드·매니페스트용(maskable 안전 영역 안에 글자)
  site.webmanifest

실행:  python3 work/favicon_gen.py          (저장소 루트에서; cairosvg·fontTools·Pillow 필요)
미리보기 시트: work/favicon_preview.png
"""
import io
import json
import os
import sys

from fontTools.ttLib import TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen

try:
    import cairosvg
except ImportError:  # pragma: no cover
    sys.exit("cairosvg가 필요합니다: pip install cairosvg")
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_TTC = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"
FONT_INDEX = 1  # Noto Serif CJK KR Black

CRIMSON = "#a21a2d"   # 홈페이지 --seal 값(고려대 크림슨을 화면용으로 올린 값)
PAPER = "#ffffff"
CHAR = "부"

# ---- 모양 조절값 (viewBox 0 0 100 100 기준) ----
DISC_R = 48.0        # 크림슨 원판 반지름
GLYPH_H = 70.0       # 글자 잉크 높이(원판 지름 96의 약 73%)
SMALL_STROKE = 1.5   # 16px용: 글자 외곽선에 두르는 선 두께(획을 조금 굵게)
SQUARE_GLYPH_H = 58.0  # 꽉 채운 정사각형(iOS)에서 글자 높이(%)
MASKABLE_GLYPH_H = 50.0  # maskable(원형 마스크 안전 영역 80%)에서 글자 높이(%)


def load_font():
    return TTCollection(FONT_TTC).fonts[FONT_INDEX]


def glyph(font, ch):
    """글자 외곽선(SVG path, 글꼴 단위, y 위쪽 양수)과 잉크 상자."""
    gs = font.getGlyphSet()
    g = gs[font.getBestCmap()[ord(ch)]]
    pen = SVGPathPen(gs)
    g.draw(pen)
    bp = BoundsPen(gs)
    g.draw(bp)
    return pen.getCommands(), bp.bounds


def placed_glyph(font, ch, height, cx, cy, fill):
    """잉크 상자의 중심을 (cx, cy)에 맞추고 잉크 높이를 height로."""
    d, (x0, y0, x1, y1) = glyph(font, ch)
    s = height / (y1 - y0)
    tx = cx - (x0 + x1) / 2 * s
    ty = cy + (y0 + y1) / 2 * s
    return f'<path fill="{fill}" transform="translate({tx:.3f} {ty:.3f}) scale({s:.5f} {-s:.5f})" d="{d}"/>'


def wrap(body, title="변호사 부효준"):
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">\n'
        f"<title>{title}</title>\n{body}\n</svg>\n"
    )


def svg_disc(font, small=False):
    """투명 바탕 위의 크림슨 원판(파비콘). small=True면 16px용으로 획을 조금 굵게."""
    g = placed_glyph(font, CHAR, GLYPH_H, 50, 50, PAPER)
    if small:
        g = g.replace("<path ", f'<path stroke="{PAPER}" stroke-width="{SMALL_STROKE:g}" stroke-linejoin="round" ', 1)
    return wrap(f'<circle cx="50" cy="50" r="{DISC_R:g}" fill="{CRIMSON}"/>\n' + g)


def svg_square(font, glyph_h):
    """크림슨으로 꽉 채운 정사각형(홈 화면 아이콘)."""
    body = f'<rect width="100" height="100" fill="{CRIMSON}"/>\n' + placed_glyph(font, CHAR, glyph_h, 50, 50, PAPER)
    return wrap(body)


def render(svg: str, size: int, supersample: int = 4) -> Image.Image:
    """크게 그려 축소(LANCZOS)해야 작은 크기에서 획이 덜 뭉개진다."""
    big = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=size * supersample, output_height=size * supersample)
    im = Image.open(io.BytesIO(big)).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS) if supersample != 1 else im


def preview_sheet(font, out_path):
    """탭·즐겨찾기·검색 결과·홈 화면 크기에서 어떻게 보이는지 한 장으로(밝은 띠·어두운 띠)."""
    normal, small, square = svg_disc(font), svg_disc(font, small=True), svg_square(font, SQUARE_GLYPH_H)
    sizes = [16, 20, 24, 32, 48, 64, 96, 128, 180]
    pad = 20
    row_h = 180 + pad * 2
    width = sum(s + pad for s in sizes) + pad * 2 + 200
    sheet = Image.new("RGBA", (width, row_h * 2), "#ffffff")
    ImageDraw.Draw(sheet).rectangle([0, row_h, width, row_h * 2], fill="#202124")
    for row in range(2):
        x = pad
        y0 = row * row_h
        for s in sizes:
            im = render(small if s <= 16 else normal, s)
            sheet.alpha_composite(im, (x, y0 + pad + (180 - s) // 2))
            x += s + pad
        # 홈 화면 아이콘 모양(모서리 둥근 정사각형)
        sq = render(square, 180)
        mask = Image.new("L", (180, 180), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 179, 179], radius=40, fill=255)
        sq.putalpha(mask)
        sheet.alpha_composite(sq, (x + 10, y0 + pad))
    sheet.convert("RGB").save(out_path)


def main():
    font = load_font()
    normal = svg_disc(font)
    small = svg_disc(font, small=True)

    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(normal)

    # ICO: 16은 획을 조금 굵게, 32·48은 그대로
    ico = [render(small, 16), render(normal, 32), render(normal, 48)]
    ico[-1].save(os.path.join(ROOT, "favicon.ico"), format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=ico[:-1])

    # iOS 홈 화면: 크림슨 꽉 채움(iOS가 모서리를 둥글림)
    render(svg_square(font, SQUARE_GLYPH_H), 180, 2).convert("RGB").save(os.path.join(ROOT, "apple-touch-icon.png"), optimize=True)

    # 매니페스트 아이콘(any + maskable): 원형 마스크 안전 영역(안쪽 80%) 안에 글자
    for size in (192, 512):
        render(svg_square(font, MASKABLE_GLYPH_H), size, 2).convert("RGB").save(os.path.join(ROOT, f"icon-{size}.png"), optimize=True)

    manifest = {
        "name": "변호사 부효준",
        "short_name": "부효준",
        "description": "행정쟁송 · 국가연구개발 제재처분 — 변호사 부효준(법무법인(유한) 금성)",
        "start_url": "/",
        "display": "browser",
        "background_color": PAPER,
        "theme_color": CRIMSON,
        "icons": [
            {"src": "/icon-192.png?v=2", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/icon-512.png?v=2", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    preview_sheet(font, os.path.join(ROOT, "work", "favicon_preview.png"))
    print("favicon.svg / favicon.ico / apple-touch-icon.png / icon-192.png / icon-512.png / site.webmanifest 생성")


if __name__ == "__main__":
    main()
