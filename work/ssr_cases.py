#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사례 데이터(cases-data.js — 2026. 10. 23. index.html의 #cases-data 블록에서 분리)로부터 두 페이지의 정적 사례 목록,
홈의 접힌 전체 목록, llms.txt·llms-full.txt(와 분야별 파일), 건수 문구를 다시 만든다. build_cases.py 보다 먼저 돌린다.

사용법 (저장소 최상위에서):
    python3 work/ssr_cases.py .          # 갱신
    python3 work/ssr_cases.py . --check  # 지금 파일이 데이터와 일치하는지 검사만

규칙(페이지의 JS card() 와 같은 마크업):
  - 홈(index.html): 6건(2026. 10. 23. 오후 본인 지시: 세 장씩 놓이는 화면은 2줄, 두 장씩 놓이는 화면은 3줄; 그 전 2026. 10. 21. 12건→9건).
    2026. 10. 25. 본인 지시(10:09 "원고 대리하여 승소한 사건(예: 공공재정환수법, 집행정지 각 인용 사건), 국가연구개발사업 관련 형사 승소(불송치 등)를 먼저 게시해주고,
    그 다음 종전처럼 국가연구개발사업 분야, 제재부가금, 환수 분야, 형사 분야 승소 사례를 보이게" → 10:31 "승소 사건 순서를 주요 분야(국가연구개발·제재부가금) 가운데
    처분 상대방을 대리해 이긴 사건(승소·일부승소·인용)을 최근 순으로, 이어서 제목에 '국가연구개발'이 든 형사 승소(불송치·불기소 등), 그 외 처분 상대방을 대리해 이긴 사건 순으로"):
      ① '앞세우는 사례'(lead_cases, 최대 LEAD_MAX = RECENT 건) — 세 단계를 차례로 이어 붙임:
         ㉠ 주요 분야(LEAD_CATS = rnd·penalty)에서 처분 상대방을 대리하여 이긴 사건(party 에 '대리'(보조참가 제외), 결과 승소·일부승소·…인용)을 최근 순으로,
         ㉡ 제목에 '국가연구개발'이 든 형사 사건 가운데 불송치·불기소·혐의없음·무죄·공소기각을 최근 순으로,
         ㉢ 그 외 분야(민사·형사 제외)에서 처분 상대방을 대리하여 이긴 사건(기준은 ㉠과 같음 — 소청 임시처분 인용·교습정지 취소 등)을 최근 순으로.
      ② 앞세우는 사례가 RECENT 에 못 미치면 남는 자리는 MAIN 의 세 분야(국가연구개발 제재처분 → 제재부가금·환수 → 형사)를 번갈아 분야마다 최근 순(sort 내림차순, 같으면 데이터 순), ①에 든 사례는 빼고.
      (10:09 지시 때는 ①을 3건(첫 줄)으로 끊고 둘째 줄에 ② 세 분야 한 건씩을 두었으나, 10:31 지시로 ①을 세 단계로 늘리면서 한도를 RECENT 로 — 지금 데이터로는 6건이 모두 ①.
       그 전 2026. 10. 23. 오후: 형사 → 국가연구개발 → 제재부가금을 번갈아 2건씩)
  - 전체(cases.html): 전체를 sort 내림차순(같으면 데이터 순)으로.
  - 제목·'자세히 →' 링크는 cases/<첫 이미지 이름>.html (build_cases.py의 page_href 와 같음).
  - 2026. 10. 21. 본인 지시: 카드에는 '판결문 N장' 수를 적지 않고, 요지는 두 줄로 접되 '더 보기' 단추 없이
    '자세히 →' 링크 하나만 둔다(자세히 보려는 사람은 한 번만 누르면 개별 페이지로).

데이터 파일(2026. 10. 23.): 사례 데이터 원본은 저장소 최상위의 cases-data.js 한 파일이다
  ("window.CASES_DATA = [...];" — 두 페이지가 <script src="cases-data.js?v=해시"> 로 읽고, 파이썬은 load_cases()/save_cases() 로 읽고 쓴다).
  종전처럼 index.html·cases.html 안에 22만 자 JSON을 두면 검색 로봇·AI 읽기 도구가 받는 HTML이 너무 커지므로 밖으로 뺐다.
  옛 인라인 블록이 남아 있으면 이 스크립트가 한 번 읽어 파일로 옮기고 블록을 지운다.
홈의 접힌 전체 목록(2026. 10. 23. 낮 추가 → 같은 날 오후 본인 지시 "사무소 위치 위의 '주요 수행 사례 전체 목록'은 삭제"로 없앰): HOME_ALL_LIST = False 이면 만들지 않고,
  index.html 에 옛 블록(<!-- all-list:start --> … <!-- all-list:end -->)이 남아 있으면 걷어 낸다. 전체 사례는 cases.html·llms-full.txt·사이트맵으로 읽힌다.
llms(2026. 10. 23.): llms-full.txt 한 파일(2.2MB)은 AI 읽기 도구의 한도를 넘으므로, llms-full.txt 는 '분야별 파일 안내 + 사례 한 줄 목록'으로,
  사례마다의 전체 텍스트는 분야별 llms-full-<분야>-<번호>.txt (각 LLMS_PART_MAX 바이트 이하)로 나눈다.
"""
import glob
import hashlib
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from press_lib import load_press, press_by_case, kdate  # noqa: E402  (press.json: 언론보도, 2026. 10. 22.)

CATS = {   # 2026. 10. 21. 이름·순서를 '다루는 사건' 카드와 맞춤(형사는 출연금·보조금 외 사건도 있어 '형사', 민사는 카드가 없어 맨 뒤)
    "rnd": "국가연구개발 제재처분",
    "penalty": "제재부가금·환수",
    "personnel": "공무원·교원 인사처분",
    "license": "인허가·면허·자격 처분",
    "comp": "손실보상",
    "admin": "그 밖의 행정처분",
    "criminal": "형사",
    "contract": "국가계약법·지방계약법",
    "state": "국가배상",
    "civil": "민사",
}
MAIN = ("rnd", "penalty", "criminal")   # 홈 '주요 분야'에서 앞세우는 사례 뒤에 번갈아 보이는 세 분야와 순서(2026. 10. 25. 본인 지시: 국가연구개발 제재처분 → 제재부가금·환수 → 형사; 그 전 2026. 10. 23. 오후: 형사 → 국가연구개발 → 제재부가금)
RECENT = 6                                # 세 장씩 2줄 = 두 장씩 3줄
LEAD_MAX = RECENT                         # 앞세우는 사례(세 단계) 한도 — 홈 전부를 채울 수 있음(2026. 10. 25. 10:31 본인 지시; 10:09 때는 RECENT - len(MAIN) = 3건으로 끊고 둘째 줄에 MAIN 세 분야 한 건씩)
LEAD_CATS = ("rnd", "penalty")            # ㉠ 주요 분야 가운데 처분 상대방 대리 승소를 먼저 찾는 행정사건 분야
LEAD_SKIP_CATS = ("civil", "criminal")    # ㉢ '그 외 처분 상대방 대리 승소'에서 빼는 분야(처분 사건이 아님; 형사는 ㉡에서 국가연구개발 관련만)
LEAD_WIN_RE = re.compile(r"^(승소|일부승소)|인용")          # 승소·일부승소, 집행정지·임시처분 '…인용'
LEAD_CRIM_WIN_RE = re.compile(r"불송치|불기소|혐의없음|무죄|공소기각")   # 형사 '승소'(불송치 등)
LEAD_CRIM_TITLE = "국가연구개발"            # 형사 사건 가운데 국가연구개발사업 관련(제목 기준 — 사례 제목 규칙상 국가연구개발 분야 사건은 제목에 '국가연구개발사업'이 들어감)
WHO = "담당변호사 부효준"
SITE = "https://lawyermrboo82.com"
LINK_TEXT = "자세히 →"   # 상세 소개(det) 유무와 상관없이 하나(2026. 10. 21.)


def esc(s):
    # 페이지의 기존 마크업과 같게: &, <, >, ", ' 를 이스케이프 (작은따옴표는 &#x27;)
    return html.escape(s or "", quote=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def load_json_block(doc, block_id):
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % re.escape(block_id), doc, re.S)
    if not m:
        raise SystemExit("데이터 블록을 찾지 못했습니다: #" + block_id)
    return json.loads(m.group(1)), m


# ---------- 사례 데이터 파일 (cases-data.js, 2026. 10. 23.) ----------

DATA_FILE = "cases-data.js"
DATA_PREFIX = "window.CASES_DATA = "
DATA_TAG_RE = re.compile(r'<script src="cases-data\.js(?:\?v=[0-9a-f]+)?"></script>')
INLINE_DATA_RE = re.compile(r'[ \t]*<script type="application/json" id="cases-data">.*?</script>[ \t]*\n?', re.S)


def dumps_cases(cases):
    return json.dumps(cases, ensure_ascii=False, indent=1)


def data_version(cases):
    """데이터가 바뀌면 바뀌는 짧은 해시 — 두 페이지의 <script src="cases-data.js?v=…"> 에 붙여 캐시를 새로 받게 한다."""
    return hashlib.sha1(dumps_cases(cases).encode("utf-8")).hexdigest()[:8]


def data_tag(cases):
    return '<script src="%s?v=%s"></script>' % (DATA_FILE, data_version(cases))


def load_cases(site):
    """사례 데이터 원본을 읽는다: cases-data.js. (이행 전 파일이 없으면 index.html 의 옛 #cases-data 블록을 읽는다.)"""
    p = os.path.join(site, DATA_FILE)
    if os.path.exists(p):
        txt = read(p)
        k = txt.find(DATA_PREFIX)
        if k < 0:
            raise SystemExit("%s 에 '%s' 가 없습니다" % (DATA_FILE, DATA_PREFIX.strip()))
        body = txt[k + len(DATA_PREFIX):].strip()
        if body.endswith(";"):
            body = body[:-1].rstrip()
        return json.loads(body)
    doc = read(os.path.join(site, "index.html"))
    cases, _ = load_json_block(doc, "cases-data")
    return cases


def save_cases(site, cases):
    write(os.path.join(site, DATA_FILE), DATA_PREFIX + dumps_cases(cases) + ";\n")


def set_data_tag(doc, cases):
    """페이지에서 옛 인라인 데이터 블록을 없애고(있으면 그 자리에), 외부 데이터 파일 태그의 버전(v=)을 지금 데이터에 맞춘다."""
    tag = data_tag(cases)
    m = INLINE_DATA_RE.search(doc)
    if m:
        indent = re.match(r"[ \t]*", m.group(0)).group(0)
        doc = doc[: m.start()] + indent + tag + "\n" + doc[m.end():]
    if not DATA_TAG_RE.search(doc):
        raise SystemExit("데이터 파일 태그(<script src=\"cases-data.js\">)를 찾지 못했습니다")
    return DATA_TAG_RE.sub(tag, doc, count=1)


def images_of(c):
    return [im for im in (c.get("images") or []) if im and im.get("src")]


DETAILS_FILE = "cases-detail.json"


def load_details(site):
    """사례별 상세 소개(cases-detail.json: {사례 id: {...}}). 없으면 빈 dict.
    항목: overview(문단 목록) · issues(쟁점 목록) · holding(법원의 판단, 문단 목록) · quotes([{text, from}]) ·
          meaning(문단 목록) · laws(관련 법령 목록) · keywords(검색어 목록) · instagram(게시물 주소)"""
    p = os.path.join(site, DETAILS_FILE)
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def with_keywords(cases, details, press=None):
    """cases.html 데이터 블록용: 상세 소개의 검색어(keywords)를 각 항목의 kw 에 넣고,
    언론보도(press.json)가 있는 사례에는 그 건수를 pr 에 넣은 사본(카드에 '언론보도' 표시, 2026. 10. 22.)."""
    by_case = press_by_case(press or [])
    out = []
    for c in cases:
        d = details.get(c["id"]) or {}
        c2 = dict(c)
        kw = [k for k in (d.get("keywords") or []) if k]
        if kw:
            c2["kw"] = kw
        else:
            c2.pop("kw", None)
        if d.get("overview") or d.get("holding"):
            c2["det"] = 1          # 상세 소개가 있는 사례(카드의 링크 글이 달라진다)
        else:
            c2.pop("det", None)
        n_pr = len(by_case.get(c["id"]) or [])
        if n_pr:
            c2["pr"] = n_pr
        else:
            c2.pop("pr", None)
        out.append(c2)
    return out


def stem_of(c):
    ims = images_of(c)
    if ims:
        return re.sub(r"\.[A-Za-z0-9]+$", "", ims[0]["src"].rsplit("/", 1)[-1])
    return c["id"]


def page_href(c):
    return "cases/%s.html" % stem_of(c)


def badge_class(r):
    r = r or ""
    return "part" if r.startswith("일부승소") else "win" if r.startswith("승소") else "other"


def render_li(c):
    ims = images_of(c)
    n = len(ims)
    href = page_href(c)
    out = ['<li class="case" data-cat="%s" id="case-%s">' % (esc(c["cat"]), esc(c["id"]))]
    if ims:
        im = ims[0]
        out.append('<button type="button" class="case-fig" aria-label="%s 판결문 크게 보기">' % esc(c["title"]))
        out.append('<img src="%s" alt="%s" loading="lazy" decoding="async">' % (esc(im.get("thumb") or im["src"]), esc(im.get("alt") or (c["title"] + " 판결문"))))
        out.append('</button>')
    else:
        out.append('<div class="case-fig none" aria-hidden="true"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8 3h11l6 6v20H8z"></path><path d="M19 3v6h6"></path><path d="M12 15h8M12 19h8M12 23h5"></path></svg><span>%s</span></div>' % esc(CATS.get(c["cat"], c["cat"])))
    out.append('<div class="case-body"><div class="case-meta"><span class="tag">%s</span>' % esc(CATS.get(c["cat"], c["cat"])))
    if c.get("date"):
        out.append('<span class="date">%s</span>' % esc(c["date"]))
    if c.get("result"):
        out.append('<span class="badge %s">%s</span>' % (badge_class(c["result"]), esc(c["result"])))
    if c.get("pr"):
        out.append('<span class="pressmark" title="이 사건이 보도된 기사 %d건 — 자세히에서 볼 수 있습니다">언론보도</span>' % int(c["pr"]))   # press.json (2026. 10. 22.)
    out.append("</div>")
    out.append('<h3 class="case-title"><a href="%s">%s</a></h3>' % (href, esc(c["title"])))
    parts = [p for p in [c.get("court"), c.get("party")] if p]
    out.append('<p class="case-sub">%s<span class="who">%s</span></p>' % (esc(" · ".join(parts) + " · ") if parts else "", WHO))
    if c.get("summary"):
        out.append('<p class="case-summary clamp">%s</p>' % esc(c["summary"]))
    out.append('<a class="case-link" href="%s">%s</a>' % (href, LINK_TEXT))
    # 외부 '자세히 보기' 링크(c.link)는 카드에 넣지 않는다(개별 페이지에만).
    out.append("</div></li>")
    return "".join(out)


def ordered(cases, cats=None):
    idx = [(c, i) for i, c in enumerate(cases) if cats is None or c["cat"] in cats]
    idx.sort(key=lambda t: ((t[0].get("sort") or ""), -t[1]), reverse=True)
    return [c for c, _ in idx]


def is_party_win(c):
    """처분 상대방(원고·신청인·소청인 등 민간 의뢰인)을 대리하여 이긴 사건: party 에 '대리'(보조참가 제외), 결과가 승소·일부승소·…인용."""
    party = c.get("party") or ""
    return "대리" in party and "보조참가" not in party and bool(LEAD_WIN_RE.search(c.get("result") or ""))


def is_lead_party_win(c):
    """㉠ 주요 분야(LEAD_CATS)의 처분 상대방 대리 승소."""
    return c["cat"] in LEAD_CATS and is_party_win(c)


def is_lead_crim_win(c):
    """㉡ 국가연구개발사업 관련 형사 사건의 승소(불송치·불기소·혐의없음·무죄·공소기각)."""
    return c["cat"] == "criminal" and LEAD_CRIM_TITLE in (c.get("title") or "") and bool(LEAD_CRIM_WIN_RE.search(c.get("result") or ""))


def is_other_party_win(c):
    """㉢ 그 외 분야(민사·형사 제외)의 처분 상대방 대리 승소."""
    return c["cat"] not in LEAD_CATS and c["cat"] not in LEAD_SKIP_CATS and is_party_win(c)


def lead_cases(cases):
    """홈에 앞세우는 사례(2026. 10. 25. 본인 지시): ㉠ 주요 분야 처분 상대방 대리 승소(최근 순) → ㉡ 국가연구개발 관련 형사 승소(최근 순) → ㉢ 그 외 처분 상대방 대리 승소(최근 순), 합쳐서 LEAD_MAX 건까지 — JS renderList 와 같은 규칙."""
    o = ordered(cases)
    lead = [c for c in o if is_lead_party_win(c)] + [c for c in o if is_lead_crim_win(c)] + [c for c in o if is_other_party_win(c)]
    return lead[:LEAD_MAX]


def home_order(cases):
    """홈 '주요 분야' 보기: 앞세우는 사례(lead_cases)로 채우고, 자리가 남으면 MAIN 의 분야를 차례로 번갈아(국가연구개발·제재부가금·형사·국가연구개발·…) 분야마다 최근 순 — 앞에 든 사례는 빼고(페이지의 JS renderList 와 같은 규칙)."""
    out = lead_cases(cases)
    seen = {c["id"] for c in out}
    per = [[c for c in ordered(cases, (k,)) if c["id"] not in seen] for k in MAIN]
    r = 0
    while len(out) < RECENT and any(len(l) > r for l in per):
        for l in per:
            if r < len(l) and len(out) < RECENT:
                out.append(l[r])
        r += 1
    return out


def render_list(cases, cats=None, limit=None):
    lst = ordered(cases, cats)
    if limit:
        lst = lst[:limit]
    return "\n".join(render_li(c) for c in lst)


def render_home(cases):
    return "\n".join(render_li(c) for c in home_order(cases))


LIST_RE = re.compile(r'(<ol class="case-list" id="case-list">)\n?(.*?)(\n?\s*</ol>)', re.S)


def replace_list(doc, body):
    m = LIST_RE.search(doc)
    if not m:
        raise SystemExit("정적 사례 목록(<ol id=\"case-list\">)을 찾지 못했습니다")
    return doc[: m.start()] + m.group(1) + "\n" + body + "\n      </ol>" + doc[m.end():]


def current_list(doc):
    m = LIST_RE.search(doc)
    return m.group(2).strip() if m else None


def replace_json_block(doc, block_id, data):
    _, m = load_json_block(doc, block_id)
    txt = json.dumps(data, ensure_ascii=False, indent=2)
    return doc[: m.start(1)] + "\n" + txt + "\n" + doc[m.end(1):]


def count_text(doc, n):
    doc = re.sub(r"주요 수행 판결문 \d+건 찾기", "주요 수행 판결문 %d건 찾기" % n, doc)   # 2026. 10. 21. 홈 찾기 상자 제목 "단어로 주요 수행 판결문 N건 찾기"(종전 "판결문 N건에서 단어로 찾기")
    doc = re.sub(r"판결문 \d+건에", "판결문 %d건에" % n, doc)
    doc = re.sub(r"주요 수행 사례 \d+건 — ", "주요 수행 사례 %d건 — " % n, doc)
    doc = re.sub(r'(<span id="find-count">)\d+(</span>)', r"\g<1>%d\g<2>" % n, doc)   # 홈 찾기 상자의 건수(JS가 다시 쓰지만 정적 값도 맞춘다)
    return doc


# ---------- 홈의 접힌 전체 목록 (2026. 10. 23.) ----------

ALL_LIST_RE = re.compile(r"<!-- all-list:start -->.*?<!-- all-list:end -->", re.S)
HOME_ALL_LIST = False   # 2026. 10. 23. 오후 본인 지시로 홈의 전체 목록 삭제 — True 로 바꾸고 ssr_cases.py 를 돌리면 </main> 앞에 다시 생긴다


def line_meta(c):
    """한 줄 목록의 설명: 분야 · 법원·사건번호 · 결정 시기 · 결과."""
    meta = [CATS.get(c["cat"], c["cat"])]
    for key in ("court", "date", "result"):
        if c.get(key):
            meta.append(c[key])
    return " · ".join(meta)


def render_all_list(cases):
    """본문 맨 끝(상담 문의 다음, </main> 앞)의 부록 절: 접힌 전체 목록.
    맨 끝에 두는 까닭 — 검색 로봇·AI 읽기 도구는 글 앞부분부터 일정량만 읽으므로, 긴 목록이 경력·다루는 사건·상담 문의보다 앞에 오면 그 절들이 잘린다."""
    lst = ordered(cases)
    n = len(lst)
    out = [
        "<!-- all-list:start -->",
        '<section class="section appendix" id="all-list-sec" aria-labelledby="all-list-h">',
        '  <header class="section-head">',
        '    <h2 id="all-list-h">주요 수행 사례 전체 목록</h2>',
        '    <p>%d건 · 최근 결정일 순</p>' % n,
        '  </header>',
        '  <div class="section-body">',
        '<details class="all-list" id="all-list">',
        '  <summary><span class="when-closed">전체 목록 %d건 펼쳐 보기 — 제목만 한 줄씩</span><span class="when-open">전체 목록 접기</span></summary>' % n,
        '  <p class="all-list-note">제목을 누르면 판결문과 사건 소개가 있는 개별 페이지가 열립니다. '
        '분야별로 보거나 단어로 찾으려면 <a href="cases.html">주요 수행 사례 전체 보기</a>를 이용해 주십시오. 모두 부효준 변호사가 담당변호사로 직접 수행한 사건입니다.</p>',
        '  <ol class="all-list-body">',
    ]
    for c in lst:
        out.append('    <li><a href="%s">%s</a> <span class="m">%s</span></li>' % (page_href(c), esc(c["title"]), esc(line_meta(c))))
    out += ["  </ol>", "</details>", "  </div>", "</section>", "<!-- all-list:end -->"]
    return "\n".join(out)


def replace_all_list(doc, body):
    """홈의 전체 목록(부록 절)을 데이터대로 바꾼다. 어디에 있든 옛 블록은 걷어 내고 </main> 바로 앞에 둔다(HOME_ALL_LIST 가 False 면 걷어 내기만)."""
    m = ALL_LIST_RE.search(doc)
    if m:
        end = m.end() + (1 if doc[m.end(): m.end() + 1] == "\n" else 0)   # 블록과 그 뒤 줄바꿈까지 걷어 내면 넣기 전 모습으로 돌아간다
        doc = doc[: m.start()] + doc[end:]
    if not body:
        return doc
    k = doc.find("</main>")
    if k < 0:
        raise SystemExit("홈의 </main> 을 찾지 못했습니다(전체 목록을 넣을 자리)")
    line_start = doc.rfind("\n", 0, k) + 1
    return doc[:line_start] + body + "\n" + doc[line_start:]


def current_all_list(doc):
    m = ALL_LIST_RE.search(doc)
    return m.group(0) if m else None


# ---------- llms ----------

LLMS_PART_MAX = 300_000   # 분야별 전체 텍스트 파일 한 개의 최대 크기(바이트) — AI 읽기 도구가 한 번에 읽을 수 있는 정도로


def llms_entry(c, details, by_press):
    """사례 하나의 전체 텍스트 블록('### 제목' 부터 빈 줄까지)."""
    ims = images_of(c)
    lines = ["### " + c["title"]]
    meta = [CATS.get(c["cat"], c["cat"])]
    if c.get("date"):
        meta.append("결정 " + c["date"])
    if c.get("result"):
        meta.append("결과: " + c["result"])
    lines.append("- " + " · ".join(meta))
    parts = [p for p in [c.get("court"), c.get("party")] if p]
    if parts:
        lines.append("- " + " · ".join(parts))
    lines.append("- %s · 판결문 공개" % WHO if ims else "- " + WHO)
    if c.get("summary"):
        lines.append("- 요지: " + c["summary"])
    d = details.get(c["id"]) or {}
    if d.get("overview"):
        lines.append("- 사건 개요: " + " ".join(d["overview"]))
    if d.get("issues"):
        lines.append("- 쟁점: " + " / ".join(d["issues"]))
    if d.get("claims"):
        lines.append("- %s: " % (d.get("claims_label") or "상대방의 주장") + " / ".join(d["claims"]))
    if d.get("argument"):
        lines.append("- %s: " % (d.get("argument_label") or "부효준 변호사의 주장") + " / ".join(d["argument"]))
    if d.get("holding"):
        lines.append("- %s: " % (d.get("holding_label") or "법원의 판단") + " ".join(d["holding"]))
    for q in d.get("quotes") or []:
        if q.get("text"):
            lines.append("- 판결 이유 가운데: \"%s\"%s" % (q["text"], (" (%s)" % q["from"]) if q.get("from") else ""))
    if d.get("meaning"):
        lines.append("- 이 사건의 의미: " + " ".join(d["meaning"]))
    if d.get("laws"):
        lines.append("- 관련 법령: " + " · ".join(d["laws"]))
    if d.get("keywords"):
        lines.append("- 검색어: " + ", ".join(d["keywords"]))
    if d.get("blog"):
        lines.append("- 네이버 블로그 소개 글: " + d["blog"])
    if d.get("instagram"):
        lines.append("- 인스타그램 소개 글: " + d["instagram"])
    for p in by_press.get(c["id"]) or []:   # 언론보도(press.json, 2026. 10. 22.)
        lines.append("- 언론보도: %s %s 「%s」%s %s" % (p.get("outlet") or "", kdate(p.get("date") or ""), p["title"],
                                                 (" — " + p["note"]) if p.get("note") else "", p["url"]))
    lines.append("- 페이지: %s/%s" % (SITE, page_href(c)))
    lines.append("")
    return "\n".join(lines) + "\n"


def llms_part_name(cat, k):
    return "llms-full-%s-%d.txt" % (cat, k)


def llms_parts(cases, details=None, press=None):
    """분야별 전체 텍스트 파일 {파일 이름: 내용}. 한 분야가 LLMS_PART_MAX 를 넘으면 -1, -2… 로 나눈다(최근 순)."""
    details = details or {}
    by_press = press_by_case(press or [])
    files = {}
    for cat, name in CATS.items():
        entries = [llms_entry(c, details, by_press) for c in ordered(cases, (cat,))]
        if not entries:
            continue
        chunks, cur, size = [], [], 0
        for e in entries:
            b = len(e.encode("utf-8"))
            if cur and size + b > LLMS_PART_MAX:
                chunks.append(cur)
                cur, size = [], 0
            cur.append(e)
            size += b
        if cur:
            chunks.append(cur)
        for k, chunk in enumerate(chunks, 1):
            head = [
                "# 변호사 부효준 — 주요 수행 사례 전체 텍스트: %s (%d/%d)" % (name, k, len(chunks)),
                "",
                "> 변호사 부효준(법무법인(유한) 금성, https://lawyermrboo82.com/)이 담당변호사로 직접 수행한 '%s' 분야 사례 %d건의 전체 텍스트%s입니다. "
                "사례마다 요지·사건 개요·쟁점·주장·법원의 판단·관련 법령과 개별 페이지 주소가 있습니다. "
                "전체 사례의 한 줄 목록과 다른 분야의 파일은 https://lawyermrboo82.com/llms-full.txt 에, 홈페이지 안내는 https://lawyermrboo82.com/llms.txt 에 있습니다."
                % (name, len(entries), " 가운데 %d번째 묶음(%d건)" % (k, len(chunk)) if len(chunks) > 1 else ""),
                "",
            ]
            files[llms_part_name(cat, k)] = "\n".join(head) + "".join(chunk).rstrip("\n") + "\n"
    return files


def llms_index(cases, intro_from, parts):
    """llms-full.txt: 머리말 + 분야별 건수 + 분야별 전체 텍스트 파일 안내 + 사례 한 줄 목록(최근 순)."""
    n = len(cases)
    cat_counts = {}
    for c in cases:
        cat_counts[c["cat"]] = cat_counts.get(c["cat"], 0) + 1
    head = intro_from or ""
    head = re.sub(r"주요 수행 사례 \d+건을", "주요 수행 사례 %d건을" % n, head)
    head = re.sub(r"수행 사례 \d+건을 글로", "수행 사례 %d건을 글로" % n, head)
    lines = [head.rstrip("\n"), "", "## 분야별 건수"]
    for k, name in CATS.items():
        lines.append("- %s: %d건" % (name, cat_counts.get(k, 0)))
    lines += ["", "## 분야별 전체 텍스트 파일",
              "사례마다 요지·사건 개요·쟁점·주장·법원의 판단·관련 법령·검색어까지 담은 전체 텍스트는 분야별 파일(각 %dKB 이하)에 있습니다. "
              "한 사례만 보려면 아래 한 줄 목록의 개별 페이지 주소를 여는 것이 가장 빠릅니다." % (LLMS_PART_MAX // 1000)]
    for cat, name in CATS.items():
        names = sorted(f for f in parts if f.startswith("llms-full-%s-" % cat))
        if not names:
            continue
        lines.append("- %s (%d건): %s" % (name, cat_counts.get(cat, 0), " · ".join("%s/%s" % (SITE, f) for f in names)))
    lines += ["", "## 수행 사례 한 줄 목록 (%d건, 최근 순)" % n,
              "형식: [제목](개별 페이지 주소) — 분야 · 법원·사건번호 · 결정 시기 · 결과. 모두 %s가 담당변호사로 직접 수행한 사건입니다." % WHO.replace("담당변호사 ", "변호사 "), ""]
    for c in ordered(cases):
        lines.append("- [%s](%s/%s) — %s" % (c["title"], SITE, page_href(c), line_meta(c)))
    return "\n".join(lines).rstrip("\n") + "\n"


def llms_head(doc):
    k = doc.find("## 분야별 건수")
    return doc[:k] if k >= 0 else doc


def main():
    args = sys.argv[1:]
    check = "--check" in args
    args = [a for a in args if not a.startswith("--")]
    site = args[0] if args else "."
    ip, cp = os.path.join(site, "index.html"), os.path.join(site, "cases.html")
    idoc, cdoc = read(ip), read(cp)
    cases = load_cases(site)                   # cases-data.js (없으면 index.html 의 옛 블록에서 읽어 아래에서 파일로 옮긴다)
    n = len(cases)
    details = load_details(site)
    press = load_press(site)                   # 언론보도(press.json): 카드의 '언론보도' 표시(pr)와 llms 줄에 쓰임
    cases_kw = with_keywords(cases, details, press)   # 데이터 파일에 검색어(kw)·언론보도 건수(pr)를 더한다(단어로 찾기에 쓰임)

    home = render_home(cases_kw)
    full = render_list(cases_kw)
    all_list = render_all_list(cases_kw) if HOME_ALL_LIST else None
    new_idoc = count_text(replace_all_list(set_data_tag(replace_list(idoc, home), cases_kw), all_list), n)
    new_cdoc = count_text(set_data_tag(replace_list(cdoc, full), cases_kw), n)

    lp, fp = os.path.join(site, "llms.txt"), os.path.join(site, "llms-full.txt")
    new_llms = None
    if os.path.exists(lp):
        d = read(lp)
        d = re.sub(r"주요 수행 사례 \d+건을", "주요 수행 사례 %d건을" % n, d)
        d = re.sub(r"사건 \d+건, 최근 결정일 순", "사건 %d건, 최근 결정일 순" % n, d)
        d = re.sub(r"\d+건의 제목·분야", "%d건의 제목·분야" % n, d)
        new_llms = d
    parts = llms_parts(cases, details, press) if os.path.exists(fp) else {}
    new_full = llms_index(cases, llms_head(read(fp)), parts) if os.path.exists(fp) else None
    stale_parts = [p for p in glob.glob(os.path.join(site, "llms-full-*.txt")) if os.path.basename(p) not in parts]

    if check:
        ok = True
        if current_list(idoc) != home:
            print("index.html 정적 목록이 데이터와 다릅니다"); ok = False
        if current_list(cdoc) != full:
            print("cases.html 정적 목록이 데이터와 다릅니다"); ok = False
        if current_all_list(idoc) != all_list:
            print("index.html 접힌 전체 목록이 데이터와 다릅니다(HOME_ALL_LIST=%s)" % HOME_ALL_LIST); ok = False
        if cases != cases_kw:
            print("cases-data.js 의 검색어(kw)·언론보도 건수(pr)가 cases-detail.json·press.json과 다릅니다"); ok = False
        if not os.path.exists(os.path.join(site, DATA_FILE)):
            print("데이터 파일 %s 가 없습니다(옛 인라인 블록 상태)" % DATA_FILE); ok = False
        for p, d in ((ip, idoc), (cp, cdoc)):
            if INLINE_DATA_RE.search(d):
                print("%s 에 옛 인라인 데이터 블록이 남아 있습니다" % os.path.basename(p)); ok = False
            if not DATA_TAG_RE.search(d) or data_tag(cases_kw) not in d:
                print("%s 의 데이터 파일 태그(버전)가 데이터와 다릅니다" % os.path.basename(p)); ok = False
        if new_full is not None and read(fp) != new_full:
            print("llms-full.txt가 데이터와 다릅니다"); ok = False
        for name, text in parts.items():
            p = os.path.join(site, name)
            if not os.path.exists(p) or read(p) != text:
                print("%s 가 데이터와 다릅니다(또는 없음)" % name); ok = False
        if stale_parts:
            print("데이터에 없는 분야별 파일이 남아 있습니다: %s" % ", ".join(os.path.basename(p) for p in stale_parts)); ok = False
        print("일치" if ok else "불일치")
        sys.exit(0 if ok else 1)

    save_cases(site, cases_kw)
    write(ip, new_idoc)
    write(cp, new_cdoc)
    if new_llms is not None:
        write(lp, new_llms)
    if new_full is not None:
        write(fp, new_full)
        for name, text in parts.items():
            write(os.path.join(site, name), text)
        for p in stale_parts:
            os.remove(p)
    print("사례 %d건: cases-data.js·index.html(홈 %d건%s)·cases.html·llms.txt·llms-full.txt(분야별 파일 %d개) 갱신"
          % (n, len(home_order(cases)), " + 접힌 전체 목록" if HOME_ALL_LIST else "", len(parts)))


if __name__ == "__main__":
    main()
