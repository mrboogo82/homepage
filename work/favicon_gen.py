#!/usr/bin/env python3
"""홈페이지 파비콘(인장) 생성기 — 2026. 10. 21.

바닥글의 인장(辯護士 夫孝俊, 두 줄 원형)을 벡터로 다시 그려 파비콘 세트를 만든다.
글자는 Noto Serif CJK KR Black을 외곽선(path)으로 변환해 넣으므로 글꼴 없이도 같은 모양으로 보인다.

생성 파일(저장소 루트):
  favicon.svg             벡터 파비콘(흰 원판 + 크림슨 테두리·글자)
  favicon.ico             16·32·48px
  apple-touch-icon.png    180px, 흰 바탕(iOS 홈 화면)
  icon-192.png, icon-512.png  안드로이드·매니페스트용(흰 바탕, maskable 안전 영역 고려)
  site.webmanifest

실행:  python3 work/favicon_gen.py          (저장소 루트에서)
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

ROWS = ["辯護士", "夫孝俊"]  # 원본 인장과 같은 배열: 윗줄 변호사, 아랫줄 부효준(왼쪽→오른쪽)

# ---- 모양 조절값 (viewBox 0 0 100 100 기준) ----
VIEW = 100.0
RING_R = 47.0        # 테두리 원의 중심선 반지름
RING_W = 5.0         # 테두리 두께
CELL = 29.0          # 글자 한 칸(em) 크기
COL_PITCH = 27.6     # 가로 글자 간격(칸보다 조금 좁게 → 인장처럼 빽빽하게)
ROW_PITCH = 27.6     # 세로 줄 간격
SHIFT_Y = 0.0        # 전체 글자 블록 상하 이동(양수 = 아래)


def load_font():
    col = TTCollection(FONT_TTC)
    return col.fonts[FONT_INDEX]


def glyph_path(font, ch, glyph_set, cmap):
    """글자 하나의 외곽선을 SVG path 문자열(글꼴 단위, y 위쪽 양수)로."""
    gname = cmap[ord(ch)]
    pen = SVGPathPen(glyph_set)
    glyph_set[gname].draw(pen)
    bp = BoundsPen(glyph_set)
    glyph_set[gname].draw(bp)
    return pen.getCommands(), bp.bounds, font["hmtx"][gname][0]


def build_svg(font):
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    upm = font["head"].unitsPerEm
    asc, desc = 880, -120  # 한중일 글꼴의 표의문자 em 상자
    scale = CELL / upm

    paths = []
    n_rows = len(ROWS)
    for ri, row in enumerate(ROWS):
        n = len(row)
        # 줄의 세로 중심: 전체 블록을 원 중심에 맞춤
        row_center_y = VIEW / 2 + (ri - (n_rows - 1) / 2) * ROW_PITCH + SHIFT_Y
        for ci, ch in enumerate(row):
            d, bounds, adv = glyph_path(font, ch, glyph_set, cmap)
            # 칸의 가로 중심
            cell_center_x = VIEW / 2 + (ci - (n - 1) / 2) * COL_PITCH
            # em 상자의 중심(글꼴 단위) → 화면 좌표
            em_cx = adv / 2
            em_cy = (asc + desc) / 2
            tx = cell_center_x - em_cx * scale
            ty = row_center_y + em_cy * scale  # y 뒤집기 전 보정
            paths.append(
                f'<path transform="translate({tx:.3f} {ty:.3f}) scale({scale:.5f} {-scale:.5f})" d="{d}"/>'
            )

    inner_r = RING_R - RING_W / 2
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VIEW:g} {VIEW:g}" width="{VIEW:g}" height="{VIEW:g}">
<title>변호사 부효준 인장</title>
<circle cx="{VIEW/2:g}" cy="{VIEW/2:g}" r="{inner_r:.2f}" fill="{PAPER}"/>
<circle cx="{VIEW/2:g}" cy="{VIEW/2:g}" r="{RING_R:.2f}" fill="none" stroke="{CRIMSON}" stroke-width="{RING_W:.2f}"/>
<g fill="{CRIMSON}">
{chr(10).join(paths)}
</g>
</svg>
"""
    return svg


def render_png(svg: str, size: int) -> Image.Image:
    data = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=size, output_height=size)
    return Image.open(io.BytesIO(data)).convert("RGBA")


def embolden(svg: str, width: float) -> str:
    """아주 작은 크기(≤32px)에서는 가는 가로획이 사라지므로 글자 외곽선에 얇은 선을 둘러 조금 굵게."""
    return svg.replace(
        f'<g fill="{CRIMSON}">',
        f'<g fill="{CRIMSON}" stroke="{CRIMSON}" stroke-width="{width}" stroke-linejoin="round">',
    )


def render_png_supersampled(svg: str, size: int, factor: int = 4) -> Image.Image:
    """작은 크기는 크게 그려 축소(LANCZOS)해야 획이 덜 뭉개진다."""
    if size <= 32:
        svg = embolden(svg, 0.7)
    big = render_png(svg, size * factor)
    return big.resize((size, size), Image.LANCZOS)


def on_square(seal: Image.Image, size: int, diameter: int, bg=PAPER) -> Image.Image:
    """흰 정사각형 바탕 가운데에 인장을 놓는다(iOS·안드로이드 아이콘용)."""
    canvas = Image.new("RGBA", (size, size), bg)
    s = seal.resize((diameter, diameter), Image.LANCZOS) if seal.size[0] != diameter else seal
    off = (size - diameter) // 2
    canvas.alpha_composite(s, (off, off))
    return canvas


def preview_sheet(svg: str, out_path: str):
    """여러 크기·배경에서 어떻게 보이는지 한 장으로."""
    sizes = [16, 24, 32, 48, 64, 96, 128, 180]
    pad = 24
    row_h = 180 + pad * 2
    width = sum(s + pad for s in sizes) + pad + 260
    sheet = Image.new("RGBA", (width, row_h * 2 + 40), "#ffffff")
    # 어두운 띠(탭·다크모드)
    ImageDraw.Draw(sheet).rectangle([0, row_h, width, row_h * 2], fill="#202124")
    for bg_i in range(2):
        x = pad
        y0 = row_h * bg_i
        for s in sizes:
            im = render_png_supersampled(svg, s)
            sheet.alpha_composite(im, (x, y0 + pad + (180 - s) // 2))
            x += s + pad
        # 비교: 기존 스캔 인장
        orig = Image.open(os.path.join(ROOT, "seal.png")).convert("RGBA")
        for i, s in enumerate([32, 48, 180]):
            o = orig.resize((s, s), Image.LANCZOS)
            sheet.alpha_composite(o, (x + (0 if i < 2 else 0), y0 + pad + (180 - s) // 2))
            x += s + 10
    sheet.save(out_path)


def main():
    font = load_font()
    svg = build_svg(font)

    with open(os.path.join(ROOT, "favicon.svg"), "w", encoding="utf-8") as f:
        f.write(svg)

    # ICO: 16·32·48 (각각 따로 그려 넣음)
    ico_imgs = [render_png_supersampled(svg, s) for s in (16, 32, 48)]
    ico_imgs[-1].save(
        os.path.join(ROOT, "favicon.ico"),
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=ico_imgs[:-1],
    )

    # iOS 홈 화면: 180px, 흰 바탕, 인장 지름 156
    seal_512 = render_png(svg, 512)
    on_square(seal_512, 180, 156).convert("RGB").save(os.path.join(ROOT, "apple-touch-icon.png"), optimize=True)

    # 매니페스트 아이콘(maskable 안전 영역: 안쪽 80% 원 → 지름 78%)
    on_square(seal_512, 192, 150).convert("RGB").save(os.path.join(ROOT, "icon-192.png"), optimize=True)
    on_square(seal_512, 512, 400).convert("RGB").save(os.path.join(ROOT, "icon-512.png"), optimize=True)

    manifest = {
        "name": "변호사 부효준",
        "short_name": "부효준",
        "description": "행정쟁송 · 국가연구개발 제재처분 — 변호사 부효준(법무법인(유한) 금성)",
        "start_url": "/",
        "display": "browser",
        "background_color": PAPER,
        "theme_color": CRIMSON,
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    with open(os.path.join(ROOT, "site.webmanifest"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    preview_sheet(svg, os.path.join(ROOT, "work", "favicon_preview.png"))
    print("favicon.svg / favicon.ico / apple-touch-icon.png / icon-192.png / icon-512.png / site.webmanifest 생성")


if __name__ == "__main__":
    main()
