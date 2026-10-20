#!/usr/bin/env python3
"""2026. 10. 21.: 로고 벽을 없애고, 위촉·위원회 타일마다 작은 로고 띠(기관 누리집 링크)를 위촉장 그림 위에 붙인다.
강의 목록에도 작은 로고를 붙이고, 한국장애인개발원 청렴시민감사관은 현행 위원회로 옮긴다.
사용: python3 work/logos-src/apply_tiles.py index.html   (아티팩트 미리보기 사본에도 같은 방식으로 적용)"""
import re, sys, pathlib

p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'index.html')
s = p.read_text(encoding='utf-8')
assert '<div class="logo-wall">' in s, '로고 벽이 없음(이미 적용됨?)'

# ---------- 기관별 로고·누리집 ----------
# org 글자(타일의 <b class="org">) → (로고 파일, 가로, 세로, 누리집, 띠 모양)
ORGS = {
    '교육부': ('logos/moe.svg', 1646, 609, 'https://www.moe.go.kr/', ''),
    '기상청': ('logos/kma.svg', 1644, 613, 'https://www.kma.go.kr/', ''),
    '행정안전부': ('logos/mois.svg', 1739, 482, 'https://www.mois.go.kr/', ''),
    '문화체육관광부': ('logos/mcst.svg', 1804, 393, 'https://www.mcst.go.kr/', ''),
    '서울특별시': ('logos/seoul.png', 772, 198, 'https://www.seoul.go.kr/', ''),
    '중소벤처기업부': ('logos/mss.svg', 1804, 393, 'https://www.mss.go.kr/', ''),
    '기후에너지환경부': ('logos/mcee.svg', 1828, 359, 'https://mcee.go.kr/', ''),
    '보건복지부': ('logos/mohw.svg', 1739, 482, 'https://www.mohw.go.kr/', ''),
    '농림축산식품부': ('logos/mafra.svg', 1804, 393, 'https://www.mafra.go.kr/', ''),
    '충남대학교병원': ('logos/cnuh.png', 900, 129, 'https://www.cnuh.co.kr/', ''),
    '한국환경공단': ('logos/keco.png', 436, 112, 'https://www.keco.or.kr/', ''),
    '대한체육회': ('logos/ksoc.svg', 199, 60, 'https://www.sports.or.kr/', ''),
    '서울주택도시개발공사': ('logos/sh.svg', 407, 56, 'https://www.i-sh.co.kr/', ''),
    '서울시설공단': ('logos/sisul.png', 500, 260, 'https://www.sisul.or.kr/', 'tall'),
    '국가과학기술연구회': ('logos/nst.svg', 1641, 375, 'https://www.nst.re.kr/', ''),
    '주식회사 에스알': ('logos/sr.svg', 396, 218, 'https://www.korail.com/', 'mid'),   # SR 누리집은 코레일로 통합되어 코레일 누리집으로
    '축산물품질평가원': ('logos/ekape.png', 340, 58, 'https://www.ekape.or.kr/', ''),
    '한국환경산업기술원': ('logos/keiti.svg', 905, 150, 'https://www.keiti.re.kr/', ''),
    '주택도시보증공사': ('logos/hug.svg', 1324, 200, 'https://www.khug.or.kr/', ''),
    '중소기업기술정보진흥원': ('logos/tipa.png', 624, 192, 'https://www.tipa.or.kr/', 'mid'),
    '과학기술정보통신부': ('logos/msit.svg', 1848, 331, 'https://www.msit.go.kr/', ''),
    '인천광역시교육청': ('logos/ice.svg', 2089, 581, 'https://www.ice.go.kr/', ''),
    '서천군': ('logos/seocheon.svg', 285, 86, 'https://www.seocheon.go.kr/', ''),
    # 위원회 (org 글자는 '기관명 위원회명')
    '과학기술정보통신부 연구자권익보호위원회': ('logos/msit.svg', 1848, 331, 'https://www.msit.go.kr/', ''),
    '중소벤처기업부 국가연구개발혁신법 제재처분 재검토위원회': ('logos/mss.svg', 1804, 393, 'https://www.mss.go.kr/', ''),
    '한국장애인개발원': ('logos/koddi.svg', 686, 194, 'https://www.koddi.or.kr/', ''),
    '한국환경산업기술원 정보공개심의회': ('logos/keiti.svg', 905, 150, 'https://www.keiti.re.kr/', ''),
    '인천광역시교육소청심사위원회': ('logos/ice.svg', 2089, 581, 'https://www.ice.go.kr/', ''),
    '식품의약품안전처 행정처분심의위원회': ('logos/mfds.svg', 1827, 361, 'https://www.mfds.go.kr/', ''),
    '한국전력공사 공정계약심의위원회': ('logos/kepco.svg', 296, 49, 'https://home.kepco.co.kr/', ''),
    '인천광역시 행정심판위원회': ('logos/incheon.png', 928, 207, 'https://www.incheon.go.kr/', ''),
    '중소벤처기업부 국민제안심사위원회': ('logos/mss.svg', 1804, 393, 'https://www.mss.go.kr/', ''),
    '한국산업단지공단': ('logos/kicox.svg', 1521, 330, 'https://www.kicox.or.kr/', ''),
    '과천시 정비구역 등 해제 실무위원회': ('logos/gwacheon.png', 776, 268, 'https://www.gccity.go.kr/', ''),
    '법무부 제57회 사법시험 제1차시험': ('logos/moj.svg', 1647, 629, 'https://www.moj.go.kr/', ''),
}
# 기관 이름(누리집 링크 글자) — 위촉장 없는 기관의 aria 이름에도 씀
SITE_NAME = {
    '과학기술정보통신부 연구자권익보호위원회': '과학기술정보통신부', '중소벤처기업부 국가연구개발혁신법 제재처분 재검토위원회': '중소벤처기업부',
    '한국환경산업기술원 정보공개심의회': '한국환경산업기술원', '인천광역시교육소청심사위원회': '인천광역시교육청',
    '식품의약품안전처 행정처분심의위원회': '식품의약품안전처', '한국전력공사 공정계약심의위원회': '한국전력공사',
    '인천광역시 행정심판위원회': '인천광역시', '중소벤처기업부 국민제안심사위원회': '중소벤처기업부',
    '과천시 정비구역 등 해제 실무위원회': '과천시', '법무부 제57회 사법시험 제1차시험': '법무부', '주식회사 에스알': '코레일(주식회사 에스알 통합)',
}
# 위촉장이 없는 타일의 빈 그림(건물 그림 + 약칭)
NONE_ABBR = {'충남대학교병원': 'CNUH', '주택도시보증공사': 'HUG', '중소기업기술정보진흥원': 'TIPA', '중소벤처기업부 국가연구개발혁신법 제재처분 재검토위원회': 'MSS'}
GLYPH = '<svg viewBox="0 0 32 32"><path d="M5 27V9l11-5 11 5v18"/><path d="M5 27h22"/><path d="M12 27v-8h8v8"/><path d="M16 12v3"/></svg>'

def logo_link(org):
    f, w, h, url, shape = ORGS[org]
    name = SITE_NAME.get(org, org)
    cls = 'adv-logo' + (' ' + shape if shape else '')
    return (f'<a class="{cls}" href="{url}" target="_blank" rel="noopener" data-org="{name}" aria-label="{name} 누리집 (새 창)">'
            f'<img src="{f}" alt="" width="{w}" height="{h}" loading="lazy"></a>')

# ---------- 1. 로고 벽 제거 ----------
s, n = re.subn(r'\n\s*<div class="logo-wall">.*?<p class="wall-note">[^\n]*\n\s*</div>', '', s, count=1, flags=re.S)
assert n == 1, '로고 벽 HTML'

# ---------- 2. 타일마다 로고 띠 ----------
def fix_tile(m):
    li = m.group(0)
    org = re.search(r'<b class="org">([^<]+)</b>', li).group(1)
    assert org in ORGS, org
    # 위촉장 없는 타일: 로고 그림 → 빈 그림(건물)으로 되돌림
    li = re.sub(r'<div class="adv-fig logo-fig" aria-hidden="true"><img[^>]*></div>',
                lambda _: f'<div class="adv-fig none" aria-hidden="true">{GLYPH}<span>{NONE_ABBR[org]}</span></div>', li)
    return li.replace('<li class="adv">', '<li class="adv">' + logo_link(org), 1)

body_start = s.index('<div class="block" id="advisory">'); body_end = s.index('<div class="past-wrap">\n            <h4>강의</h4>')
seg = s[body_start:body_end]
seg, n = re.subn(r'<li class="adv">.*?</li>', fix_tile, seg, flags=re.S)
assert n == 35, n

# ---------- 3. 한국장애인개발원을 현행 위원회로 ----------
m = re.search(r'\s*<li class="adv">(?:(?!</li>).)*한국장애인개발원(?:(?!</li>).)*</li>', seg, flags=re.S)
kodda = m.group(0)
seg = seg.replace(kodda, '', 1)
kodda_now = kodda.replace('<span class="term">2024. 8. 12. ~ 2026. 8. 11.</span>', '<span class="term">2024. 8. ~ 현재 · 위촉장 2024. 8. 12. ~ 2026. 8. 11.</span>')
assert kodda_now != kodda
# 현행 위원회 목록에서 한국환경산업기술원 정보공개심의회 바로 앞에(위촉 시작 순)
anchor = re.search(r'\n\s*<li class="adv">(?:(?!</li>).)*한국환경산업기술원 정보공개심의회', seg, flags=re.S)
seg = seg[:anchor.start()] + kodda_now + seg[anchor.start():]
seg = seg.replace('심의하는 여섯 위원회의 위원입니다.', '심의하는 일곱 위원회의 위원입니다.')
assert '일곱 위원회' in seg
# 안내문: 위촉장은 크게, 로고는 누리집으로
seg = seg.replace('위촉장을 누르면 크게 볼 수 있습니다. 처분청이', '위촉장을 누르면 크게 볼 수 있고, 로고를 누르면 그 기관의 누리집이 열립니다. 처분청이')
seg = seg.replace('출발점입니다. 위촉장을 누르면 크게 볼 수 있습니다.', '출발점입니다. 위촉장을 누르면 크게 볼 수 있고, 로고를 누르면 그 기관의 누리집이 열립니다.')
assert seg.count('로고를 누르면 그 기관의 누리집이 열립니다') == 2
# 임기를 마친 글줄의 기관 이름에 누리집 링크
def link(name, url): return f'<a href="{url}" target="_blank" rel="noopener">{name}</a>'
for name, url in [('그랜드코리아레저 주식회사(GKL)', 'https://www.gkl.co.kr/'), ('새만금개발공사', 'https://www.sdco.or.kr/'),
                  ('한국남동발전', 'https://www.koenergy.kr/'), ('스마트제조혁신추진단', 'https://www.smart-factory.kr/'),
                  ('서울특별시 종로구 계약심의위원회', 'https://www.jongno.go.kr/'), ('서울특별시 종로구 공유재산심의회', 'https://www.jongno.go.kr/'),
                  ('법무부 변호사시험', 'https://www.moj.go.kr/')]:
    assert seg.count('<p class="past">') == 2 and name in seg, name
    seg = re.sub(r'(<p class="past">[^\n]*?)' + re.escape(name), lambda m: m.group(1) + link(name, url), seg, count=1)
s = s[:body_start] + seg + s[body_end:]

# ---------- 4. 강의 목록에 작은 로고 ----------
LEC = [('법무부 법무연수원 국가송무과정', 'logos/ioj.svg', 196, 68, 'https://ioj.moj.go.kr/', '법무부 법무연수원'),
       ('대한법률구조공단 직무교육', 'logos/klac.svg', 1382, 327, 'https://www.klac.or.kr/', '대한법률구조공단'),
       ('인천광역시교육청 교육연수원 직무교육', 'logos/ice.svg', 2089, 581, 'https://www.ieti.or.kr/', '인천광역시교육청교육연수원'),
       ('서울지방변호사회 의무연수', 'logos/seoulbar.png', 215, 31, 'https://www.seoulbar.or.kr/', '서울지방변호사회')]
lec_start = s.index('<h4>강의</h4>'); lec_end = s.index('</dl>', lec_start)
lec = s[lec_start:lec_end]
for text, f, w, h, url, name in LEC:
    old = f'<dd>{text}'
    assert lec.count(old) == 1, text
    lec = lec.replace(old, f'<dd><a class="lec-logo" href="{url}" target="_blank" rel="noopener" data-org="{name}" aria-label="{name} 누리집 (새 창)"><img src="{f}" alt="" width="{w}" height="{h}" loading="lazy"></a>{text}')
s = s[:lec_start] + lec + s[lec_end:]

# ---------- 5. CSS: 로고 벽 규칙 → 로고 띠 규칙 ----------
css_start = s.index('/* 법률고문 위촉 기관 로고 벽 (2026. 10. 20.)')
css_end = s.index('.past-wrap { display: grid;')
NEW_CSS = '''/* 기관 로고 띠 (2026. 10. 21.): 위촉·위원회 타일마다 위촉장 그림 위에 작은 흰 띠를 붙이고 그 기관의 공식 로고를 작게 놓는다.
   띠를 누르면 기관 누리집이 새 창으로 열리고, 위촉장 그림을 누르면 전처럼 위촉장이 크게 열린다.
   띠는 어두운 화면에서도 흰색이라 로고의 지정색이 그대로 보인다. (2026. 10. 20.의 로고 벽은 위촉장 타일과 겹치고 로고가 커서 없앰) */
.adv { gap: 0; }
.adv-body { margin-top: 0.6rem; }
.adv-logo {
  display: flex; align-items: center; justify-content: center;
  box-sizing: border-box; height: 2.4rem; padding: 0.25rem 0.6rem;
  background: #fff; border: 1px solid var(--rule); border-bottom: 0; border-radius: 3px 3px 0 0;
  text-decoration: none; transition: border-color 0.15s;
}
.adv-logo img { display: block; width: auto; max-width: 84%; height: 1.4rem; object-fit: contain; }
.adv-logo.tall img { height: 1.9rem; }    /* 세로로 짜인 로고(서울시설공단) */
.adv-logo.mid img { height: 1.6rem; }     /* 짧고 높은 로고(SR·TIPA) */
.adv-logo:hover, .adv-logo:focus-visible { border-color: var(--ink-soft); }
.adv-logo:hover img { opacity: 0.85; }
.adv-logo:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
.adv-logo + .adv-fig { border-top-left-radius: 0; border-top-right-radius: 0; }
.adv-fig.none span { font-size: var(--step--2); }
.past-grid .adv-body { margin-top: 0.4rem; }
.past-grid .adv-logo { height: 1.7rem; padding: 0.2rem 0.4rem; }
.past-grid .adv-logo img { height: 1rem; max-width: 88%; }
.past-grid .adv-logo.tall img { height: 1.3rem; }
.past-grid .adv-logo.mid img { height: 1.15rem; }
/* 강의 목록: 글줄 앞의 작은 로고 */
.lec-logo { display: inline-flex; align-items: center; vertical-align: -0.35em; box-sizing: border-box; height: 1.6rem; margin-right: 0.55rem; padding: 0.15rem 0.45rem; background: #fff; border: 1px solid var(--rule); border-radius: 3px; text-decoration: none; }
.lec-logo img { display: block; width: auto; max-width: 8rem; height: 1.05rem; object-fit: contain; }
.lec-logo:hover { border-color: var(--ink-soft); }
/* 좁은 화면(한 줄 목록): 로고 띠는 위촉장 그림 옆, 기관명 위에 작은 칸으로 */
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
s = s[:css_start] + NEW_CSS + s[css_end:]
# 로고 벽 전용이던 .adv-fig.logo-fig 규칙은 위에서 함께 지워졌다(NEW_CSS 안에 없음)
assert '.logo-wall' not in s and 'logo-fig' not in s, 'logo-wall/logo-fig 잔재'

# ---------- 6. JS: 로고 벽 단추용 분기 → 누리집 링크 집계 ----------
old_js = '''      // 로고 벽의 단추(.logo-card)는 기관명·기간을 data-org·data-term으로 가진다(2026. 10. 20.)
      var org = b.getAttribute('data-org') || (tile && tile.querySelector('.org') ? tile.querySelector('.org').textContent : '');
      var term = b.getAttribute('data-term') || (tile && tile.querySelector('.term') ? tile.querySelector('.term').textContent : '');
      var first = tile ? b.querySelector('img') : null;'''
new_js = '''      var org = tile && tile.querySelector('.org') ? tile.querySelector('.org').textContent : '';
      var term = tile && tile.querySelector('.term') ? tile.querySelector('.term').textContent : '';
      var first = b.querySelector('img');'''
assert s.count(old_js) == 1; s = s.replace(old_js, new_js)
old_click = "      b.addEventListener('click', function () { if (!tile) track('logo_click', { org: org }); LB.open(items, 0); });\n    });\n  })();"
new_click = '''      b.addEventListener('click', function () { LB.open(items, 0); });
    });
    // 기관 로고 띠(누리집 링크) 클릭 집계 (2026. 10. 21.)
    document.querySelectorAll('a.adv-logo, a.lec-logo').forEach(function (a) {
      a.addEventListener('click', function () { track('logo_click', { org: a.getAttribute('data-org') || '' }); });
    });
  })();'''
assert s.count(old_click) == 1; s = s.replace(old_click, new_click)

p.write_text(s, encoding='utf-8')
print('ok', p, len(s))
