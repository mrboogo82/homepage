#!/usr/bin/env python3
"""좁은 화면(640px 이하)의 로고 띠 자리를 바꾼다 (2026. 10. 21. 밤).

종전: 한 줄 목록에서 로고 띠가 위촉장 그림 '옆', 기관명 '위'에 놓여 기관명과 로고의 글자가 겹쳐 보여 어색했다.
변경: 넓은 화면과 같은 짜임 — 왼쪽 칸에 [로고 띠][위촉장 그림]을 세로로 붙이고, 오른쪽 칸은 글(기관명·역할·기간)만.
      그림 칸을 4.25rem → 5rem(임기를 마친 묶음 2.75rem → 4rem)으로 조금 넓혀 띠 안의 로고가 읽히게 했다.

실제 홈페이지(index.html)와 아티팩트 미리보기 사본에 같은 문자열 치환을 한다:
  python3 work/logos-src/mobile_logo.py index.html
"""
import sys

OLD_BLOCK = '''/* 좁은 화면(한 줄 목록): 로고 띠는 위촉장 그림 옆, 기관명 위에 작은 칸으로 */
@media (max-width: 640px) {
  .advisors .adv { grid-template-areas: "fig logo" "fig body"; align-items: start; }
  .advisors .adv-fig { grid-area: fig; align-self: center; border-radius: 3px; }
  .advisors .adv-logo { grid-area: logo; justify-self: start; height: 1.7rem; padding: 0.15rem 0.5rem; border-bottom: 1px solid var(--rule); border-radius: 3px; }
  .advisors .adv-logo img { height: 1.15rem; max-width: 9rem; }
  .advisors .adv-logo.tall img { height: 1.4rem; }
  .advisors .adv-body { grid-area: body; margin-top: 0.3rem; }
  .past-grid .adv-logo { height: 1.5rem; }
  .past-grid .adv-logo img { height: 1rem; }
  .lec-logo { height: 1.45rem; margin-right: 0.45rem; }
  .lec-logo img { height: 0.95rem; }
}
'''

NEW_BLOCK = '''
/* ---------- 좁은 화면의 로고 띠 (2026. 10. 21. 밤) ----------
   한 줄 목록에서 로고 띠가 기관명 '위'에 놓이면 로고 속 글자와 기관명이 겹쳐 보여 어색하다는 지적에,
   넓은 화면과 같은 짜임으로: 왼쪽 칸에 [로고 띠][위촉장 그림]을 세로로 붙이고 오른쪽 칸은 글만.
   그림 칸은 4.25rem → 5rem(임기를 마친 묶음 2.75rem → 4rem)으로 조금 넓혀 띠 안의 로고가 읽히게 한다.
   이 블록은 위의 한 줄 목록 규칙(.advisors .adv, .past-grid .adv)보다 뒤에 있어야 한다. */
@media (max-width: 640px) {
  .advisors .adv { grid-template-columns: 5rem minmax(0, 1fr); grid-template-rows: auto 1fr; grid-template-areas: "logo body" "fig body"; gap: 0 0.85rem; align-items: start; }
  .advisors .adv-logo { grid-area: logo; justify-self: stretch; height: 1.55rem; padding: 0.15rem 0.3rem; border-bottom: 0; border-radius: 3px 3px 0 0; }
  .advisors .adv-logo img { height: 0.95rem; max-width: 90%; }
  .advisors .adv-logo.tall img { height: 1.25rem; }
  .advisors .adv-logo.mid img { height: 1.1rem; }
  .advisors .adv-fig { grid-area: fig; align-self: start; }
  .advisors .adv-logo + .adv-fig { border-top-left-radius: 0; border-top-right-radius: 0; }
  .advisors .adv-body { grid-area: body; align-self: center; margin-top: 0; }
  .past-grid .adv { grid-template-columns: 4rem minmax(0, 1fr); gap: 0 0.6rem; }
  .past-grid .adv-logo { height: 1.3rem; padding: 0.1rem 0.25rem; }
  .past-grid .adv-logo img { height: 0.8rem; }
  .past-grid .adv-logo.tall img { height: 1rem; }
  .past-grid .adv-logo.mid img { height: 0.9rem; }
  .lec-logo { height: 1.45rem; margin-right: 0.45rem; }
  .lec-logo img { height: 0.95rem; }
}
'''


def main(path):
    html = open(path, encoding='utf-8').read()
    assert html.count(OLD_BLOCK) == 1, 'old mobile block not found exactly once in ' + path
    html = html.replace(OLD_BLOCK, '')
    assert html.count('\n</style>') == 1, '</style> not found exactly once'
    html = html.replace('\n</style>', '\n' + NEW_BLOCK + '</style>', 1)
    open(path, 'w', encoding='utf-8').write(html)
    print('ok', path, len(html))


if __name__ == '__main__':
    for p in sys.argv[1:]:
        main(p)
