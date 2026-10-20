#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
변호사 부효준 홈페이지 — 사례별 개별 페이지 생성기

사용법 (저장소 최상위에서):
    python3 work/build_cases.py .

하는 일:
  1. index.html 안의 <script id="cases-data"> JSON(사례 데이터, 원본)을 읽는다.
  2. cases.html의 <style>을 공용 case.css 로 뽑고, 개별 페이지용 규칙을 덧붙인다.
  3. 사례마다 cases/<판결문 이미지 이름>.html 페이지를 만든다
     (제목·메타·OG·JSON-LD·판결문 이미지·같은 분야 사례·상담 안내).
  4. index.html / cases.html 의 카드(정적 목록 + JS 렌더링)에 개별 페이지 링크를 넣고,
     메인 <title>·JSON-LD(@id, sameAs)를 보강하고, <html lang="ko">를 넣는다.
  5. 전체 URL이 든 sitemap.xml 을 만든다.

  6. llms.txt / llms-full.txt 가 있으면 사례별 페이지 주소를 덧붙인다.
  7. 주제별 모아 보기 페이지 topics/*.html (참여제한·환수·제재부가금·집행정지·당사자소송)을 만들고
     메인의 국가연구개발 절과 cases.html 목록 위에 그 링크를 넣는다. 메인 <title>·설명·키워드도 TOPICS/NEW_* 상수대로 맞춘다.

같은 폴더에 다시 돌려도 안전하다(이미 고친 곳은 건너뜀). 사례 데이터(index.html의 cases-data)를
고친 뒤 이 스크립트를 다시 돌리면 모든 페이지·사이트맵·링크가 다시 만들어진다.
"""
import glob
import html
import json
import os
import re
import sys
from datetime import date
from urllib.parse import urlsplit, urlunsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ssr_cases import load_details  # noqa: E402  (cases-detail.json: 사례별 상세 소개)

SITE = "https://lawyermrboo82.com"
TODAY = date.today().isoformat()
WHO = "담당변호사 부효준"
GA_ID = "G-STLB5BC2G2"

CATS = {
    "rnd": "국가연구개발",
    "personnel": "인사·징계·소청",
    "license": "인허가·면허·자격",
    "penalty": "제재부가금·환수·부정당업자 제재",
    "comp": "손실보상",
    "admin": "그 밖의 행정처분",
    "state": "국가배상",
    "civil": "민사·연금·계약",
    "criminal": "형사",
}
# 사이트맵 우선순위: 주력 분야를 앞세운다
PRIORITY = {"rnd": "0.8", "penalty": "0.8", "criminal": "0.7", "personnel": "0.6", "license": "0.6",
            "admin": "0.6", "comp": "0.5", "state": "0.5", "civil": "0.4"}

# 메인 페이지 제목·설명: 사람들이 실제로 찾는 말(참여제한·연구비 환수·제재부가금)을 앞세운다 (2026. 10. 19.)
NEW_TITLE = "국가연구개발사업 참여제한·연구비 환수·제재부가금 취소소송 — 변호사 부효준 | 행정쟁송 · 법무법인(유한) 금성"
NEW_OG_TITLE = "변호사 부효준 — 국가연구개발사업 참여제한·연구비 환수·제재부가금 · 행정쟁송"
NEW_DESCRIPTION = ("국가연구개발사업 참여제한·연구비(연구개발비) 환수·제재부가금 처분의 취소소송·집행정지와 행정쟁송 전반을 맡는 부효준 변호사(법무법인(유한) 금성). "
                   "국가연구개발 제재처분을 심의하는 위원회의 위원이자 정부·지방자치단체·공공기관 약 20곳의 고문변호사로서, 처분을 받은 연구자·기업·공무원을 대리하고, "
                   "정부출연금·보조금의 부정집행을 이유로 한 사기·보조금법 위반 등 형사사건도 제재처분과 함께 변호합니다. 주요 수행 사례를 판결문과 함께 공개합니다.")
NEW_EYEBROW = "행정쟁송 · 국가연구개발사업 참여제한 · 연구비 환수 · 제재부가금 · 변호사 부효준"
EXTRA_KEYWORDS = ["국가연구개발사업 참여제한 변호사", "참여제한 변호사", "연구비 환수 변호사", "국가연구개발혁신법 변호사", "참여제한 처분 취소소송",
                  "국가 R&D 제재처분", "연구비 제재부가금 취소", "참여제한 집행정지", "연구개발비 회수금 당사자소송", "부효준 변호사"]
NEW_CASES_TITLE = "주요 수행 사례 %d건 — 행정소송 · 국가연구개발 제재처분 판결문 · 변호사 부효준"   # %d에 사례 수가 들어간다

# 주제별 모아 보기 페이지 (검색 의도별: 참여제한 / 환수 / 제재부가금 / 집행정지 / 당사자소송)
TOPICS = [
    {
        "slug": "rnd-participation-restriction",
        "name": "참여제한처분 취소소송",
        "title": "국가연구개발사업 참여제한처분 취소소송 사례 — 변호사 부효준",
        "h1": "국가연구개발사업 참여제한처분 취소소송 사례",
        "lead": "국가연구개발사업 참여제한처분을 다툰 취소소송·무효확인소송과 집행정지 사례입니다.",
        "intro": [
            "참여제한은 「국가연구개발혁신법」 제32조 제1항에 따라 연구개발기관·연구책임자·연구자 등에게 10년 이내의 범위에서 국가연구개발활동 참여를 제한하는 처분입니다. "
            "처분사유가 실제로 있는지, 기관과 개인 가운데 누구에게 얼마의 기간을 정한 것이 법령의 기준에 맞는지(재량권 일탈·남용), 사전통지와 재검토 등 절차를 지켰는지가 주로 다투어집니다.",
            "처분이 있음을 안 날부터 90일 이내에 취소소송을 제기해야 하고(「행정소송법」 제20조 제1항), 진행 중인 과제가 중단될 상황이면 집행정지를 함께 신청합니다(같은 법 제23조). "
            "사전통지 단계라면 통지를 받은 날부터 20일 이내에 재검토 요청 의견을 낼 수 있습니다(「국가연구개발혁신법」 제33조 제3항).",
        ],
        "cats": ("rnd", "penalty"),
        "pattern": r"참여제한",
    },
    {
        "slug": "rnd-recovery",
        "name": "연구개발비·출연금 환수처분",
        "title": "연구비(연구개발비)·정부출연금 환수처분 취소소송 사례 — 변호사 부효준",
        "h1": "연구비(연구개발비)·정부출연금 환수처분 취소소송 사례",
        "lead": "연구개발비·정부출연금 환수처분과 환수금·회수금 채무를 다툰 사례입니다.",
        "intro": [
            "「국가연구개발혁신법」 제32조 제3항의 연구개발비 환수는 제재사유와 관련된 정부 연구개발비를 돌려받는 처분이고, 같은 법 제13조 제7항의 정산 회수금은 성격이 다릅니다. "
            "환수처분은 취소소송으로 다투지만, 정산에 따른 반환채무는 공법상 당사자소송(채무부존재확인)으로 다투어야 하는 경우가 있어 문서의 성격부터 가려야 합니다.",
            "환수 범위가 제재사유와 관련된 금액으로 한정되는지, 위반금액 가운데 정부지원연구개발비의 비율만큼만 환수되는지(같은 법 시행령 제59조 제3항), 처분사유의 존부와 재량권 일탈·남용이 주로 다투어집니다.",
        ],
        "cats": ("rnd", "penalty"),
        "pattern": r"환수|회수",
    },
    {
        "slug": "rnd-penalty-surcharge",
        "name": "제재부가금 부과처분",
        "title": "제재부가금 부과처분 취소소송·집행정지 사례 — 변호사 부효준",
        "h1": "제재부가금 부과처분 취소소송·집행정지 사례",
        "lead": "국가연구개발혁신법·보조금법·공공재정환수법에 따른 제재부가금 부과처분을 다툰 사례입니다.",
        "intro": [
            "「국가연구개발혁신법」 제32조 제1항은 이미 지급한 정부 연구개발비의 5배 범위에서 제재부가금을 부과할 수 있게 하고, 참여제한과 병과할 수 있습니다(같은 조 제2항). "
            "「보조금 관리에 관한 법률」 제33조의2와 「공공재정 부정청구 금지 및 부정이익 환수 등에 관한 법률」 제9조도 각각 제재부가금을 두고 있어 어느 법이 적용되는지부터 살핍니다.",
            "산정의 기준이 되는 금액, 배수와 감경 사유, 처분을 한 기관이 법이 정한 행정청인지, 상대방이 법인인지 대표자 개인인지가 자주 쟁점이 되고, 금액이 크면 집행정지의 필요성도 함께 다툽니다.",
        ],
        "cats": ("rnd", "penalty"),
        "pattern": r"제재부가금",
    },
    {
        "slug": "rnd-stay-of-execution",
        "name": "집행정지",
        "title": "참여제한·제재부가금·환수처분 집행정지 사례 — 변호사 부효준",
        "h1": "참여제한·제재부가금·환수처분 집행정지 사례",
        "lead": "본안 판결까지 처분의 효력을 멈추는 집행정지·효력정지 사례입니다.",
        "intro": [
            "취소소송을 제기해도 처분의 효력은 그대로 유지되므로, 법원이 집행정지를 받아들여야 판결 때까지 효력이 멈춥니다(「행정소송법」 제23조). "
            "참여제한처럼 기간이 지나면 돌이킬 수 없는 처분, 진행 중인 과제가 중단되는 상황에서는 소송 제기와 함께 집행정지를 서둘러 신청해야 합니다.",
            "회복하기 어려운 손해와 긴급한 필요가 소명되는지, 본안 청구가 이유 없음이 명백하지 않은지, 통보가 집행정지의 대상이 되는 처분인지가 다투어집니다.",
        ],
        "cats": ("rnd", "penalty"),
        "pattern": r"집행정지|효력정지|가처분",
    },
    {
        "slug": "rnd-party-litigation",
        "name": "회수금·정산금 당사자소송",
        "title": "연구개발비 회수금·정산금 반환채무 당사자소송 사례 — 변호사 부효준",
        "h1": "연구개발비 회수금·정산금 반환채무 당사자소송 사례",
        "lead": "정산 회수금·사업비 반환채무의 존부를 다툰 공법상 당사자소송과 관련 사례입니다.",
        "intro": [
            "국가연구개발사업 협약은 공법상 계약이어서, 전문기관의 정산 회수 통보에 따른 반환의무의 존부와 범위는 민사소송이 아니라 공법상 당사자소송으로 다툽니다. "
            "통보서에 '환수'라고 적혀 있어도 그 실질이 제재처분인지 정산 회수인지에 따라 취소소송과 당사자소송으로 길이 갈립니다.",
            "누구를 상대로 소를 내야 하는지(전문기관인지 국가인지), 협약상 반환 요건이 충족되었는지, 과제 중단·특별평가 판정이 적법한지가 주로 쟁점이 됩니다.",
        ],
        "cats": ("rnd", "penalty"),
        "pattern": r"당사자소송|채무부존재|부존재확인|정산금|회수금|부당이득금 징수",
    },
]


def esc(s):
    return html.escape(s or "", quote=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def load_json_block(doc, block_id):
    m = re.search(r'<script type="application/json" id="%s">(.*?)</script>' % re.escape(block_id), doc, re.S)
    if not m:
        raise SystemExit("데이터 블록을 찾지 못했습니다: #" + block_id)
    return json.loads(m.group(1))


def images_of(c):
    return [im for im in (c.get("images") or []) if im and im.get("src")]


def stem_of(c):
    ims = images_of(c)
    if ims:
        return re.sub(r"\.[A-Za-z0-9]+$", "", ims[0]["src"].rsplit("/", 1)[-1])
    return c["id"]


def page_href(c):            # 홈·목록 페이지에서 쓰는 상대 경로
    return "cases/%s.html" % stem_of(c)


def page_url(c):
    return "%s/%s" % (SITE, page_href(c))


def topics_of(c):
    return [t for t in TOPICS if c["cat"] in t["cats"] and re.search(t["pattern"], c["title"])]


def topic_href(t):             # 홈·목록 페이지에서 쓰는 상대 경로
    return "topics/%s.html" % t["slug"]


def topic_url(t):
    return "%s/%s" % (SITE, topic_href(t))


def first_sentence(text):
    text = (text or "").strip()
    k = text.find("다.")
    return text[: k + 2] if 0 < k < 200 else (text[:160] + "…" if len(text) > 160 else text)


def badge_class(r):
    r = r or ""
    return "part" if r.startswith("일부승소") else "win" if r.startswith("승소") else "other"


def description_of(c):
    """검색 결과에 보일 설명문: 법원·사건번호 + 요지 앞부분(약 150자)."""
    head = c.get("court") or ""
    body = (c.get("summary") or "").strip()
    text = (head + ". " if head else "") + body
    if len(text) <= 160:
        return text
    cut = text[:160]
    k = cut.rfind("다.")                       # 문장 끝에서 자른다
    if k > 80:
        return cut[: k + 2]
    k = cut.rfind(" ")                         # 아니면 낱말 경계에서 자르고 줄임표
    if k > 80:
        cut = cut[:k]
    return cut.rstrip(" ,·") + "…"


def ga_snippet():
    return (
        '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n'
        "<script>\n"
        "  window.dataLayer = window.dataLayer || [];\n"
        "  function gtag(){dataLayer.push(arguments);}\n"
        "  try { if (localStorage.getItem('ga-ignore') === '1') window['ga-disable-%s'] = true; } catch (e) {}\n"
        "  gtag('js', new Date());\n"
        "  gtag('config', '%s');\n"
        "  function track(name, params) { try { if (typeof gtag === 'function') gtag('event', name, params || {}); } catch (e) {} }\n"
        "</script>\n" % (GA_ID, GA_ID, GA_ID)
    )


EXTRA_CSS = """
/* ---------- 사례별 개별 페이지 (build_cases.py) ---------- */
.crumbs { margin-top: 1.25rem; font-size: var(--step--1); color: var(--ink-soft); }
.crumbs ol { list-style: none; display: flex; flex-wrap: wrap; gap: 0.2rem 0.5rem; margin: 0; padding: 0; }
.crumbs li + li::before { content: "›"; margin-right: 0.5rem; color: var(--rule); }
.crumbs a { color: inherit; }
.case-page { display: grid; gap: 2.25rem; max-width: 56rem; padding-block: 1rem 2rem; }
.case-head { display: grid; gap: 0.7rem; }
.case-head .case-meta { font-size: var(--step--1); }
.case-head .badge { margin-left: 0; }
.case-h1 { font-size: clamp(1.45rem, 2.8vw, 2.1rem); line-height: 1.35; letter-spacing: -0.015em; }
.case-head .case-sub { font-size: var(--step--1); }
.case-head .case-sub .who { display: inline; margin-top: 0; }
.case-text p { margin: 0; font-size: var(--step-0); line-height: 1.85; }
.case-text .case-link { display: inline-block; margin-top: 0.75rem; }
.case-docs { display: grid; gap: 1.25rem; }
.case-docs h2, .related h2, .case-cta h2 { font-size: var(--step-1); }
.case-docs figure { margin: 0; display: grid; gap: 0.45rem; }
.case-docs figure a { display: block; border: 1px solid var(--rule); background: var(--wash); }
.case-docs figure img { display: block; width: 100%; height: auto; }
.case-docs figcaption { font-size: var(--step--2); color: var(--ink-soft); }
.related { display: grid; gap: 0.9rem; padding-top: 1.5rem; border-top: 1px solid var(--rule); }
.related ul { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.6rem; }
.related li { display: grid; gap: 0.15rem; padding: 0.7rem 0; border-bottom: 1px solid var(--rule); }
.related li a { font-family: var(--serif); font-weight: 600; text-decoration: none; }
.related li a:hover { text-decoration: underline; }
.related .meta { font-size: var(--step--2); color: var(--ink-soft); }
.related .meta .badge { margin-left: 0.4rem; }
.related .more { margin-top: 0.25rem; }
.case-cta { display: grid; gap: 0.75rem; padding: 1.4rem 1.5rem; border: 1px solid var(--rule); border-radius: 3px; background: var(--wash); }
.case-cta p { margin: 0; font-size: var(--step--1); line-height: 1.75; }
.case-cta .btns { display: flex; flex-wrap: wrap; gap: 0.6rem; }
.case-cta .btns .btn { color: var(--paper); background: var(--ink); border-color: var(--ink); }
.case-cta .btns .btn.ghost { color: var(--ink); background: none; }
.case-detail { display: grid; gap: 1.6rem; padding-top: 1.75rem; border-top: 1px solid var(--rule); }
.case-detail h2 { font-size: var(--step-1); margin: 0; }
.case-detail .part { display: grid; gap: 0.7rem; }
.case-detail p { margin: 0; font-size: var(--step-0); line-height: 1.85; }
.case-detail ol, .case-detail ul { margin: 0; padding-left: 1.4rem; display: grid; gap: 0.45rem; font-size: var(--step-0); line-height: 1.8; }
.case-detail .quotes { display: grid; gap: 0.9rem; }
.case-detail blockquote { margin: 0; padding: 0.9rem 1.2rem; border-left: 3px solid var(--seal); background: var(--wash); font-family: var(--serif); font-size: var(--step--1); line-height: 1.85; }
.case-detail blockquote p { font-size: inherit; line-height: inherit; }
.case-detail blockquote p + p { margin-top: 0.5rem; }
.case-detail blockquote cite { display: block; margin-top: 0.5rem; font-style: normal; font-family: var(--sans); font-size: var(--step--2); color: var(--ink-soft); }
.case-detail .laws-line, .case-detail .kw-line { margin: 0; font-size: var(--step--1); line-height: 1.9; }
.case-detail .laws-line .label, .case-detail .kw-line .label { margin-right: 0.5rem; }
.case-detail .kw-line a, .case-detail .kw-line span.kw { display: inline-block; margin: 0.15rem 0.35rem 0.15rem 0; padding: 0.1rem 0.6rem; border: 1px solid var(--rule); border-radius: 999px; font-size: var(--step--2); text-decoration: none; color: var(--ink); }
.case-detail .kw-line a:hover { border-color: var(--seal); color: var(--seal); }
.case-detail .source-line { margin: 0; font-size: var(--step--2); color: var(--ink-soft); line-height: 1.7; }
.topic-line { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin: 1rem 0 0; font-size: var(--step--1); }
.topic-line .label { margin-right: 0.3rem; }
.topic-line .btn.ghost.small, .topic-links .btn.ghost.small { padding: 0.25rem 0.85rem; font-size: var(--step--2); }
.topic-links { display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; }
.topic-links .label { margin-right: 0.3rem; }
.topic-page { display: grid; gap: 2rem; max-width: 56rem; padding-block: 1rem 2rem; }
.topic-page .intro { display: grid; gap: 0.8rem; }
.topic-page .intro p { margin: 0; line-height: 1.85; }
.topic-page .lead-sub { font-size: var(--step-0); color: var(--ink-soft); }
.topic-cases { list-style: none; margin: 0; padding: 0; display: grid; gap: 0; }
.topic-cases li { display: grid; gap: 0.3rem; padding: 1rem 0; border-top: 1px solid var(--rule); }
.topic-cases li:last-child { border-bottom: 1px solid var(--rule); }
.topic-cases h3 { font-size: var(--step-0); }
.topic-cases h3 a { text-decoration: none; }
.topic-cases h3 a:hover { text-decoration: underline; }
.topic-cases .meta { font-size: var(--step--2); color: var(--ink-soft); }
.topic-cases .meta .badge { margin-left: 0.4rem; }
.topic-cases .gist { margin: 0; font-size: var(--step--1); line-height: 1.7; }
.topic-nav { display: grid; gap: 0.75rem; padding-top: 1.5rem; border-top: 1px solid var(--rule); }
.visually-hidden { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }
@media (prefers-color-scheme: dark) {
  .case-cta .btns .btn { color: var(--paper); background: var(--ink); border-color: var(--ink); }
  .case-cta .btns .btn.ghost { color: var(--ink); background: none; }
}
"""


def related_cases(c, by_cat):
    lst = by_cat[c["cat"]]
    i = next(k for k, x in enumerate(lst) if x["id"] == c["id"])
    newer = lst[max(0, i - 3): i]
    older = lst[i + 1: i + 4]
    out = newer + older
    # 모자라면 반대쪽에서 채운다 (최대 6건)
    k = 1
    while len(out) < 6 and (i - 3 - k >= 0 or i + 3 + k < len(lst)):
        if i + 3 + k < len(lst):
            out.append(lst[i + 3 + k])
        if len(out) < 6 and i - 3 - k >= 0:
            out.insert(0, lst[i - 3 - k])
        k += 1
    return out[:6]


def paras(lst):
    return "".join("<p>%s</p>" % esc(x) for x in (lst or []) if x)


def items_or_paras(lst):
    """항목이 둘 이상이면 번호 목록(블로그 글의 '1. 2. 3.' 꼴), 하나면 문단."""
    lst = [x for x in (lst or []) if x]
    if len(lst) >= 2:
        return "<ol>%s</ol>" % "".join("<li>%s</li>" % esc(x) for x in lst)
    return paras(lst)


def holding_label_of(c):
    """판단 주체에 맞는 소제목: 법원 / 경찰 / 검찰 / 위원회."""
    court = c.get("court") or ""
    if "경찰" in court:
        return "경찰의 결정"
    if "검찰" in court:
        return "검찰의 결정"
    if "법원" not in court and ("위원회" in court or "심판" in court):
        return "위원회의 결정"
    return "법원의 판단"


def detail_html(c, d):
    """cases-detail.json 의 상세 소개를 개별 페이지의 본문으로. 없으면 빈 문자열."""
    if not d:
        return ""
    parts = []
    if d.get("overview"):
        parts.append('<div class="part"><h2>사건의 주요 내용</h2>%s</div>' % paras(d["overview"]))
    if d.get("issues"):
        parts.append('<div class="part"><h2>쟁점</h2><ol>%s</ol></div>' % "".join("<li>%s</li>" % esc(x) for x in d["issues"] if x))
    if d.get("claims"):
        parts.append('<div class="part"><h2>%s</h2>%s</div>' % (esc(d.get("claims_label") or "상대방의 주장"), items_or_paras(d["claims"])))
    if d.get("argument"):
        parts.append('<div class="part"><h2>%s</h2>%s</div>' % (esc(d.get("argument_label") or "부효준 변호사의 주장"), items_or_paras(d["argument"])))
    if d.get("holding") or d.get("quotes"):
        q = ""
        quotes = [x for x in (d.get("quotes") or []) if x and x.get("text")]
        if quotes:
            items = []
            for x in quotes:
                body = "".join("<p>%s</p>" % esc(t) for t in str(x["text"]).split("\n") if t.strip())
                items.append("<blockquote>%s%s</blockquote>" % (body, ('<cite>%s</cite>' % esc(x["from"])) if x.get("from") else ""))
            q = '<div class="quotes">%s</div>' % "".join(items)
            q += '<p class="source-line">※ 판결 이유 가운데 이 사건의 판단 기준이 된 부분을 그대로 옮긴 것으로, 당사자 이름 등은 가렸습니다.</p>'
        parts.append('<div class="part"><h2>%s</h2>%s%s</div>' % (esc(d.get("holding_label") or holding_label_of(c)), paras(d.get("holding")), q))
    if d.get("meaning"):
        parts.append('<div class="part"><h2>이 사건이 보여 주는 것</h2>%s</div>' % paras(d["meaning"]))
    tail = []
    if d.get("laws"):
        tail.append('<p class="laws-line"><span class="label">관련 법령</span>%s</p>' % esc(" · ".join(d["laws"])))
    if d.get("keywords"):
        tail.append('<p class="kw-line"><span class="label">관련 단어</span>%s</p>' % "".join(
            '<a href="../cases.html#q=%s">%s</a>' % (esc(k), esc(k)) for k in d["keywords"] if k))
    links = []
    if d.get("blog"):
        links.append('<a href="%s" rel="noopener" target="_blank">네이버 블로그</a>' % esc(d["blog"]))
    if d.get("instagram"):
        links.append('<a href="%s" rel="noopener" target="_blank">인스타그램(@lawyer.boo)</a>' % esc(d["instagram"]))
    if links:
        tail.append('<p class="source-line">이 사건의 소개 글은 %s에도 있습니다.</p>' % "·".join(links))
    if tail:
        parts.append('<div class="part">%s</div>' % "".join(tail))
    return '<section class="case-detail" aria-label="사례 상세 소개">%s</section>\n      ' % "".join(parts)


def dates_of(path):
    """이미 만들어진 페이지가 있으면 그 datePublished·dateModified를 읽는다(게시일이 빌드 때마다 바뀌지 않게)."""
    try:
        with open(path, encoding="utf-8") as f:
            head = f.read(20000)
        p = re.search(r'"datePublished":\s*"(\d{4}-\d{2}-\d{2})"', head)
        m = re.search(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})"', head)
        return (p.group(1) if p else TODAY), (m.group(1) if m else TODAY)
    except OSError:
        return TODAY, TODAY


def build_case_page(c, by_cat, cat_counts, details=None, site="."):
    """내용이 바뀐 페이지만 dateModified를 오늘로 한다."""
    path = os.path.join(site, page_href(c))
    published, modified = dates_of(path)
    html_old = render_case_page(c, by_cat, cat_counts, details, published, modified)
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() == html_old:
                return html_old
    except OSError:
        pass
    return render_case_page(c, by_cat, cat_counts, details, published, TODAY)


def render_case_page(c, by_cat, cat_counts, details, published, modified):
    d = (details or {}).get(c["id"]) or {}
    cat = CATS.get(c["cat"], c["cat"])
    url = page_url(c)
    ims = images_of(c)
    title = c["title"]
    desc = description_of(c)
    og_image = "%s/cases/%s" % (SITE, ims[0]["src"].rsplit("/", 1)[-1]) if ims else SITE + "/og-image.jpg"
    parts = [p for p in [c.get("court"), c.get("party")] if p]

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Article",
                "@id": url + "#article",
                "mainEntityOfPage": url,
                "headline": title,
                "description": desc,
                "image": ["%s/cases/%s" % (SITE, im["src"].rsplit("/", 1)[-1]) for im in ims] or [SITE + "/og-image.jpg"],
                "articleSection": cat,
                "keywords": ", ".join(d.get("keywords") or []) if d.get("keywords") else None,
                "articleBody": " ".join([c.get("summary") or ""] + list(d.get("overview") or []) + list(d.get("claims") or []) + list(d.get("argument") or []) + list(d.get("holding") or []) + list(d.get("meaning") or [])).strip() or None,
                "inLanguage": "ko",
                "datePublished": published,
                "dateModified": modified,
                "author": {"@type": "Person", "@id": SITE + "/#person", "name": "부효준", "jobTitle": "변호사", "url": SITE + "/"},
                "publisher": {"@type": "Person", "@id": SITE + "/#person", "name": "부효준"},
                "isPartOf": {"@type": "WebSite", "name": "변호사 부효준", "url": SITE + "/"},
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "주요 수행 사례", "item": SITE + "/cases.html"},
                    {"@type": "ListItem", "position": 3, "name": cat, "item": "%s/cases.html#cat=%s" % (SITE, c["cat"])},
                    {"@type": "ListItem", "position": 4, "name": title},
                ],
            },
        ],
    }

    for k in ("keywords", "articleBody"):
        if ld["@graph"][0].get(k) is None:
            del ld["@graph"][0][k]
    figs = []
    for k, im in enumerate(ims):
        fname = im["src"].rsplit("/", 1)[-1]
        alt = im.get("alt") or ("%s 판결문 %d" % (title, k + 1))
        figs.append(
            '<figure><a href="%s" target="_blank" rel="noopener" aria-label="%s 크게 보기">'
            '<img src="%s" alt="%s" loading="%s" decoding="async"></a>'
            "<figcaption>%s</figcaption></figure>"
            % (esc(fname), esc(alt), esc(fname), esc(alt), "eager" if k == 0 else "lazy", esc(alt))
        )

    rel_items = []
    for r in related_cases(c, by_cat):
        rel_items.append(
            '<li><a href="%s.html">%s</a><span class="meta">%s%s%s</span></li>'
            % (
                esc(stem_of(r)),
                esc(r["title"]),
                esc(r.get("court") or ""),
                (" · " + esc(r["date"])) if r.get("date") else "",
                ('<span class="badge %s">%s</span>' % (badge_class(r.get("result")), esc(r["result"]))) if r.get("result") else "",
            )
        )

    ext_link = ""
    if c.get("link") and re.match(r"^https?://", c["link"], re.I):
        ext_link = '<a class="case-link ext" href="%s" rel="noopener">자세히 보기 (법무법인 금성 성공사례)</a>' % esc(c["link"])
    tps = topics_of(c)
    topic_line = ""
    if tps:
        topic_line = '<p class="topic-line"><span class="label">주제별 사례</span>%s</p>' % "".join(
            '<a class="btn ghost small" href="../topics/%s.html">%s</a>' % (esc(t["slug"]), esc(t["name"])) for t in tps)

    if c["cat"] == "rnd":
        cta_text = ("국가연구개발 제재처분은 사전통지를 받은 날부터 20일 이내에 재검토 요청 의견을 내고, "
                    "처분이 있음을 안 날부터 90일 이내에 취소소송을 제기해야 합니다. 처분서나 사전통지서를 받은 날짜부터 확인해 드립니다.")
    elif c["cat"] == "criminal":
        cta_text = ("정부출연금·보조금과 관련한 고발·수사는 참여제한·환수 같은 행정제재와 사실관계가 하나이므로, "
                    "두 절차를 한 흐름으로 대응해야 합니다. 출석 요구서나 처분서를 받으셨다면 연락 주십시오.")
    else:
        cta_text = ("행정처분은 처분이 있음을 안 날부터 90일 이내에 행정심판이나 취소소송으로 다투어야 하고, "
                    "기간이 지나면 돌이킬 수 없는 처분은 집행정지를 서둘러야 합니다. 처분서를 받은 날짜부터 확인해 드립니다.")

    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)} · {esc(cat)} 수행 사례 · 변호사 부효준</title>
<meta name="description" content="{esc(desc)}">{('\n<meta name="keywords" content="%s">' % esc(", ".join(d["keywords"]))) if d.get("keywords") else ""}
<meta name="author" content="부효준">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="article">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="변호사 부효준">
<meta property="og:url" content="{esc(url)}">
<meta property="og:title" content="{esc(title)} — 변호사 부효준 수행 사례">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{esc(og_image)}">
<meta property="og:image:alt" content="{esc(ims[0].get('alt') if ims else title)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)} — 변호사 부효준 수행 사례">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{esc(og_image)}">
{ga_snippet()}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<link rel="stylesheet" href="../case.css">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<div class="page" id="top">
  <header class="top">
    <a class="brand" href="../index.html">변호사 부효준</a>
    <nav aria-label="페이지 이동">
      <a href="../cases.html">주요 수행 사례</a>
      <a href="../index.html#rnd">국가연구개발 제재처분</a>
      <a class="btn small" href="../index.html#contact">상담 문의</a>
    </nav>
  </header>
  <main>
    <nav class="crumbs" aria-label="현재 위치">
      <ol>
        <li><a href="../index.html">홈</a></li>
        <li><a href="../cases.html">주요 수행 사례</a></li>
        <li><a href="../cases.html#cat={esc(c['cat'])}">{esc(cat)}</a></li>
      </ol>
    </nav>
    <article class="case-page" id="case-{esc(c['id'])}">
      <header class="case-head">
        <div class="case-meta"><span class="tag">{esc(cat)}</span>{('<span class="date">%s</span>' % esc(c['date'])) if c.get('date') else ''}{('<span class="badge %s">%s</span>' % (badge_class(c.get('result')), esc(c['result']))) if c.get('result') else ''}</div>
        <h1 class="case-h1">{esc(title)}</h1>
        <p class="case-sub">{esc(' · '.join(parts) + (' · ' if parts else ''))}<span class="who">{WHO}</span></p>
      </header>
      <section class="case-text" aria-labelledby="gist-h">
        <h2 id="gist-h" class="visually-hidden">사건의 요지</h2>
        <p>{esc(c.get('summary') or '')}</p>
        {ext_link}{topic_line}
      </section>
      {detail_html(c, d)}<section class="case-docs" aria-labelledby="docs-h">
        <h2 id="docs-h">판결문 {len(ims)}장</h2>
        {''.join(figs)}
      </section>
      <section class="related" aria-labelledby="rel-h">
        <h2 id="rel-h">같은 분야의 다른 사례</h2>
        <ul>
          {''.join(rel_items)}
        </ul>
        <p class="more"><a class="btn ghost" href="../cases.html#cat={esc(c['cat'])}">{esc(cat)} 수행 사례 {cat_counts[c['cat']]}건 전체 보기</a></p>
      </section>
      <section class="case-cta" aria-labelledby="cta-h">
        <h2 id="cta-h">비슷한 처분을 받으셨다면</h2>
        <p>{esc(cta_text)}</p>
        <div class="btns"><a class="btn" href="../index.html#contact">상담 문의</a><a class="btn ghost" href="tel:+82-2-588-8685">전화 02-588-8685</a><a class="btn ghost" href="mailto:boo@keumseonglaw.com">boo@keumseonglaw.com</a></div>
      </section>
    </article>
  </main>
  <footer class="sign">
    <div class="fine">
      <nav class="foot-nav" aria-label="페이지 차례">
        <a href="../index.html">홈으로</a> <a href="../cases.html">주요 수행 사례 전체</a> <a href="../index.html#career">경력</a> <a href="../index.html#fields">다루는 사건</a> <a href="../index.html#rnd">국가연구개발 제재처분</a> <a href="../index.html#faq">자주 묻는 질문</a> <a href="../index.html#advisory">법률고문 위촉</a> <a href="../index.html#contact">상담 문의</a>
      </nav>
      <p>광고책임변호사 부효준</p>
      <p>법무법인(유한) 금성 · 서울 서초구 반포대로30길 12-6, 4층</p>
    </div>
  </footer>
</div>
</body>
</html>
"""


def build_topic_page(t, matched, cat_counts):
    url = topic_url(t)
    desc = t["lead"] + " " + first_sentence(t["intro"][0])
    if len(desc) > 165:
        desc = desc[:160].rstrip(" ,·") + "…"
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "CollectionPage",
                "@id": url,
                "url": url,
                "name": t["h1"],
                "description": desc,
                "inLanguage": "ko",
                "dateModified": TODAY,
                "isPartOf": {"@type": "WebSite", "name": "변호사 부효준", "url": SITE + "/"},
                "author": {"@type": "Person", "@id": SITE + "/#person", "name": "부효준", "jobTitle": "변호사", "url": SITE + "/"},
                "hasPart": [{"@type": "Article", "@id": page_url(c) + "#article", "headline": c["title"], "url": page_url(c)} for c in matched],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "주요 수행 사례", "item": SITE + "/cases.html"},
                    {"@type": "ListItem", "position": 3, "name": t["name"]},
                ],
            },
        ],
    }
    items = []
    for c in matched:
        items.append(
            '<li><h3><a href="../%s">%s</a></h3><p class="meta">%s%s%s%s</p><p class="gist">%s</p></li>'
            % (
                esc(page_href(c)), esc(c["title"]),
                esc(CATS.get(c["cat"], c["cat"])),
                (" · " + esc(c["court"])) if c.get("court") else "",
                (" · " + esc(c["date"])) if c.get("date") else "",
                ('<span class="badge %s">%s</span>' % (badge_class(c.get("result")), esc(c["result"]))) if c.get("result") else "",
                esc(first_sentence(c.get("summary"))),
            )
        )
    others = "".join('<a class="btn ghost small" href="%s.html">%s</a>' % (esc(o["slug"]), esc(o["name"])) for o in TOPICS if o["slug"] != t["slug"])
    intro_html = "".join("<p>%s</p>" % esc(p) for p in t["intro"])
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(t["title"])}</title>
<meta name="description" content="{esc(desc)}">
<meta name="author" content="부효준">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{esc(url)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ko_KR">
<meta property="og:site_name" content="변호사 부효준">
<meta property="og:url" content="{esc(url)}">
<meta property="og:title" content="{esc(t["title"])}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/og-image.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(t["title"])}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/og-image.jpg">
{ga_snippet()}<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@500;600;700&family=Noto+Sans+KR:wght@400;500;700&display=swap">
<link rel="stylesheet" href="../case.css">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<div class="page" id="top">
  <header class="top">
    <a class="brand" href="../index.html">변호사 부효준</a>
    <nav aria-label="페이지 이동">
      <a href="../cases.html">주요 수행 사례</a>
      <a href="../index.html#rnd">국가연구개발 제재처분</a>
      <a class="btn small" href="../index.html#contact">상담 문의</a>
    </nav>
  </header>
  <main>
    <nav class="crumbs" aria-label="현재 위치">
      <ol>
        <li><a href="../index.html">홈</a></li>
        <li><a href="../cases.html">주요 수행 사례</a></li>
        <li>{esc(t["name"])}</li>
      </ol>
    </nav>
    <article class="topic-page">
      <header class="case-head">
        <p class="eyebrow">주제별 사례 · 국가연구개발 제재처분</p>
        <h1 class="case-h1">{esc(t["h1"])}</h1>
        <p class="lead-sub">{esc(t["lead"])} 모두 변호사 부효준이 담당변호사로 직접 수행한 사건이며, 사례를 누르면 판결문 이미지가 있는 페이지로 이어집니다.</p>
      </header>
      <section class="intro" aria-labelledby="intro-h">
        <h2 id="intro-h" class="visually-hidden">무엇이 다투어지는가</h2>
        {intro_html}
      </section>
      <section aria-labelledby="list-h">
        <h2 id="list-h">수행 사례 {len(matched)}건 <small class="meta">(최근 순)</small></h2>
        <ol class="topic-cases">
          {"".join(items)}
        </ol>
      </section>
      <section class="topic-nav" aria-labelledby="nav-h">
        <h2 id="nav-h">다른 주제</h2>
        <p class="topic-links">{others}<a class="btn ghost small" href="../cases.html#cat=rnd">국가연구개발 사례 {cat_counts.get("rnd", 0)}건 전체</a></p>
      </section>
      <section class="case-cta" aria-labelledby="cta-h">
        <h2 id="cta-h">처분서나 사전통지서를 받으셨다면</h2>
        <p>처분이 있음을 안 날부터 90일 이내에 취소소송을, 국가연구개발 제재처분의 사전통지라면 통지를 받은 날부터 20일 이내에 재검토 요청 의견을 내야 합니다. 받은 날짜와 처분청부터 확인해 드립니다.</p>
        <div class="btns"><a class="btn" href="../index.html#contact">상담 문의</a><a class="btn ghost" href="tel:+82-2-588-8685">전화 02-588-8685</a><a class="btn ghost" href="mailto:boo@keumseonglaw.com">boo@keumseonglaw.com</a></div>
      </section>
    </article>
  </main>
  <footer class="sign">
    <div class="fine">
      <nav class="foot-nav" aria-label="페이지 차례">
        <a href="../index.html">홈으로</a> <a href="../cases.html">주요 수행 사례 전체</a> <a href="../index.html#career">경력</a> <a href="../index.html#fields">다루는 사건</a> <a href="../index.html#rnd">국가연구개발 제재처분</a> <a href="../index.html#faq">자주 묻는 질문</a> <a href="../index.html#advisory">법률고문 위촉</a> <a href="../index.html#contact">상담 문의</a>
      </nav>
      <p>광고책임변호사 부효준</p>
      <p>법무법인(유한) 금성 · 서울 서초구 반포대로30길 12-6, 4층</p>
    </div>
  </footer>
</div>
</body>
</html>
"""


def topic_links_html(prefix=""):
    return '<p class="laws-line topic-links"><span class="label">주제별 사례</span>%s</p>' % "".join(
        '<a class="btn ghost small" href="%s%s">%s</a>' % (prefix, topic_href(t), esc(t["name"])) for t in TOPICS)


# ---------- index.html / cases.html 손보기 ----------

LI_RE = re.compile(r'<li class="case"[^>]*>.*?</li>', re.S)


def link_static_cards(doc):
    """정적으로 박혀 있는 사례 카드의 제목을 개별 페이지 링크로 바꾸고, '자세히' 링크를 단다."""
    def fix(m):
        li = m.group(0)
        if 'class="case-title"><a ' in li:
            return li
        im = re.search(r'<img src="cases/([^"]+?)\.[A-Za-z0-9]+"', li)
        if not im:
            return li
        href = "cases/%s.html" % im.group(1)
        li = re.sub(r'<h3 class="case-title">(.*?)</h3>',
                    lambda t: '<h3 class="case-title"><a href="%s">%s</a></h3>' % (href, t.group(1)), li, count=1, flags=re.S)
        li = li.replace('</div></li>', '<a class="case-link" href="%s">판결문과 사례 자세히 →</a></div></li>' % href, 1)
        return li
    return LI_RE.sub(fix, doc)


JS_PAGEHREF = (
    "  function pageHref(c) { var im = (Array.isArray(c.images) ? c.images : []).filter(function (im) { return im && im.src; })[0];"
    " var stem = im ? String(im.src).replace(/^.*\\//, '').replace(/\\.[A-Za-z0-9]+$/, '') : c.id; return 'cases/' + stem + '.html'; }\n"
)


LINK_JS_OLD = "el('a', 'case-link', '판결문과 사례 자세히 →')"
LINK_JS_NEW = "el('a', 'case-link', c.det ? '사건 내용·판결 이유 자세히 →' : '판결문과 사례 자세히 →')"


def patch_link_text(doc):
    """카드·목록의 '자세히' 링크 글: 상세 소개가 있는 사례(det)는 '사건 내용·판결 이유 자세히'."""
    return doc.replace(LINK_JS_OLD, LINK_JS_NEW)


HAY_OLD = "var hay = [c.title, c.summary, c.court, c.party, c.result, c.date, CATS[c.cat]].join(' ').toLowerCase();"
HAY_NEW = "var hay = [c.title, c.summary, c.court, c.party, c.result, c.date, CATS[c.cat], (c.kw || []).join(' ')].join(' ').toLowerCase();"


def patch_search(doc):
    """단어로 찾기: 상세 소개의 검색어(kw)도 찾는 범위에 넣는다."""
    return doc.replace(HAY_OLD, HAY_NEW, 1) if HAY_OLD in doc else doc


def patch_js(doc):
    n = doc.count("body.appendChild(el('h3', 'case-title', c.title));")
    if n == 0 and "pageHref(c)" in doc:
        return doc
    if n != 1:
        raise SystemExit("card() 제목 줄을 %d군데 찾았습니다(1이어야 함)" % n)
    doc = doc.replace(
        "body.appendChild(el('h3', 'case-title', c.title));",
        "var h3 = el('h3', 'case-title'); var ta = el('a', null, c.title); ta.href = pageHref(c); h3.appendChild(ta); body.appendChild(h3);",
    )
    # 카드: 요지 아래에 개별 페이지 링크
    doc = doc.replace(
        "if (c.summary) { var p = el('p', 'case-summary', c.summary); body.appendChild(p); clampSummary(p, body); }",
        "if (c.summary) { var p = el('p', 'case-summary', c.summary); body.appendChild(p); clampSummary(p, body); }\n"
        "      var pa = el('a', 'case-link', '판결문과 사례 자세히 →'); pa.href = pageHref(c); body.appendChild(pa);",
        1,
    )
    # 목록(row) 보기: 펼친 본문에도 링크
    doc = doc.replace(
        "if (c.summary) txt.appendChild(el('p', 'case-summary', c.summary));",
        "if (c.summary) txt.appendChild(el('p', 'case-summary', c.summary));\n"
        "        var pa2 = el('a', 'case-link', '판결문과 사례 자세히 →'); pa2.href = pageHref(c); txt.appendChild(pa2);",
        1,
    )
    # pageHref 정의를 card()와 같은 범위(scope)에: card() 바로 앞에 있는 el() 선언 줄 앞에 넣는다
    k = doc.find("function card(c)")
    m = None
    for m2 in re.finditer(r"\n( *)function el\(tag, cls, text\)", doc):
        if m2.start() < k:
            m = m2
    if not m:
        raise SystemExit("card() 앞의 el() 함수를 찾지 못했습니다")
    doc = doc[: m.start() + 1] + m.group(1) + JS_PAGEHREF.strip() + "\n" + doc[m.start() + 1:]
    return doc


def patch_html_lang(doc):
    return doc.replace("<html>", '<html lang="ko">', 1) if "<html>" in doc else doc


def clean_url(u):
    s = urlsplit(u)
    return urlunsplit((s.scheme, s.netloc, s.path, "", ""))


def replace_meta(doc, name_attr, name, content):
    """<meta name|property="..." content="..."> 의 content를 바꾼다(없으면 그대로)."""
    pat = re.compile(r'(<meta %s="%s" content=")([^"]*)(")' % (name_attr, re.escape(name)))
    return pat.sub(lambda m: m.group(1) + esc(content) + m.group(3), doc, count=1)


def patch_index(doc, links):
    doc = patch_html_lang(doc)
    doc = re.sub(r"<title>.*?</title>", "<title>%s</title>" % NEW_TITLE, doc, count=1, flags=re.S)
    doc = replace_meta(doc, "name", "description", NEW_DESCRIPTION)
    doc = replace_meta(doc, "property", "og:title", NEW_OG_TITLE)
    doc = replace_meta(doc, "name", "twitter:title", NEW_OG_TITLE)
    mk = re.search(r'<meta name="keywords" content="([^"]*)"', doc)
    if mk:
        kws = [k.strip() for k in html.unescape(mk.group(1)).split(",") if k.strip()]
        kws = [k for k in kws if k not in EXTRA_KEYWORDS]
        kws[1:1] = EXTRA_KEYWORDS   # 이름 바로 뒤에, 정해진 순서로
        doc = replace_meta(doc, "name", "keywords", ", ".join(kws))
    doc = doc.replace('<p class="eyebrow">행정쟁송 · 국가연구개발 제재처분 · 변호사 부효준</p>', '<p class="eyebrow">%s</p>' % NEW_EYEBROW, 1)
    # 국가연구개발 제재처분 절의 '관련 법령' 줄 아래에 주제별 사례 링크
    if 'class="laws-line topic-links"' not in doc:
        k = doc.find('<p class="laws-line"><span class="label">관련 법령</span>')
        if k >= 0:
            e = doc.find("</p>", k) + 4
            doc = doc[:e] + "\n          " + topic_links_html() + doc[e:]
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', doc, re.S)
    if m:
        ld = json.loads(m.group(1))
        ld.setdefault("@id", SITE + "/#person")
        same = [clean_url(l["url"]) for l in links if l.get("url") and "keumseong" not in l["url"]]
        ld["sameAs"] = same
        if isinstance(ld.get("worksFor"), dict):
            ld["worksFor"].setdefault("url", "https://www.keumseong.com")
        ld.setdefault("knowsLanguage", "ko")
        alt = ld.get("alternateName")
        alt = [alt] if isinstance(alt, str) else list(alt or [])
        for a in ["부효준 변호사", "Boo Hyo-jun"]:
            if a not in alt:
                alt.append(a)
        ld["alternateName"] = alt
        ka = list(ld.get("knowsAbout") or [])
        for k in ["국가연구개발사업 참여제한처분 취소소송·집행정지", "연구비(연구개발비)·정부출연금 환수처분 취소소송", "제재부가금 부과처분 취소소송", "연구개발비 회수금·정산금 반환채무 당사자소송"]:
            if k not in ka:
                ka.append(k)
        ld["knowsAbout"] = ka
        # 순서: @context, @type, @id 가 앞에 오도록
        ordered = {k: ld[k] for k in ["@context", "@type", "@id"] if k in ld}
        ordered.update({k: v for k, v in ld.items() if k not in ordered})
        doc = doc[: m.start(1)] + json.dumps(ordered, ensure_ascii=False, indent=1) + doc[m.end(1):]
    doc = link_static_cards(doc)
    doc = patch_js(doc)
    doc = patch_link_text(doc)
    return doc


def patch_cases(doc, n_cases=None):
    doc = patch_html_lang(doc)
    title = NEW_CASES_TITLE % n_cases if n_cases else NEW_CASES_TITLE
    doc = doc.replace("<title>주요 수행 사례 전체 · 변호사 부효준</title>", "<title>%s</title>" % title, 1)
    doc = doc.replace('<meta property="og:title" content="주요 수행 사례 전체 · 변호사 부효준">',
                      '<meta property="og:title" content="%s">' % title, 1)
    doc = doc.replace('<meta name="twitter:title" content="주요 수행 사례 전체 · 변호사 부효준">',
                      '<meta name="twitter:title" content="%s">' % title, 1)
    # 사례 수가 바뀌면 제목의 건수도 맞춘다 (ssr_cases.py 도 같은 일을 하지만 여기서도 보장)
    if n_cases:
        doc = re.sub(r"주요 수행 사례 \d+건 — ", "주요 수행 사례 %d건 — " % n_cases, doc)
    doc = link_static_cards(doc)
    doc = patch_js(doc)
    doc = patch_link_text(doc)
    doc = patch_search(doc)
    # 사례 목록 위에 주제별 사례 링크
    if 'class="laws-line topic-links"' not in doc:
        k = doc.find('<ol class="case-list" id="case-list">')
        if k >= 0:
            doc = doc[:k] + topic_links_html() + "\n      " + doc[k:]
    return doc


def build_sitemap(cases):
    rows = [
        (SITE + "/", TODAY, "weekly", "1.0"),
        (SITE + "/cases.html", TODAY, "weekly", "0.9"),
    ]
    for t in TOPICS:
        rows.append((topic_url(t), TODAY, "weekly", "0.9"))
    for c in cases:
        rows.append((page_url(c), TODAY, "monthly", PRIORITY.get(c["cat"], "0.5")))
    body = "".join(
        "  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>\n" % (esc(u), lm, cf, pr)
        for u, lm, cf, pr in rows
    )
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n"


def patch_llms(site, cases):
    """llms.txt에는 개별 페이지 안내 한 줄, llms-full.txt에는 사례마다 '- 페이지:' 줄을 넣는다 (이미 있으면 건너뜀)."""
    p = os.path.join(site, "llms.txt")
    if os.path.exists(p):
        doc = read(p)
        line = "- 사례별 개별 페이지: 사례마다 https://lawyermrboo82.com/cases/<판결문 이미지 이름>.html 주소의 페이지가 있습니다(제목·요지·판결문 이미지·같은 분야 사례). 전체 목록은 https://lawyermrboo82.com/sitemap.xml 에 있습니다."
        changed = False
        if "사례별 개별 페이지" not in doc:
            anchor = "- [수행 사례 전체 텍스트](https://lawyermrboo82.com/llms-full.txt)"
            k = doc.find(anchor)
            if k >= 0:
                e = doc.find("\n", k)
                doc = doc[: e + 1] + line + "\n" + doc[e + 1:]
                changed = True
        if "## 주제별 사례" not in doc:
            block = "## 주제별 사례 (국가연구개발 제재처분)\n" + "".join("- [%s](%s): %s\n" % (t["h1"], topic_url(t), t["lead"]) for t in TOPICS) + "\n"
            k = doc.find("## 경력")
            if k >= 0:
                doc = doc[:k] + block + doc[k:]
                changed = True
        if changed:
            write(p, doc)
    p = os.path.join(site, "llms-full.txt")
    if os.path.exists(p):
        doc = read(p)
        if "- 페이지: https://lawyermrboo82.com/cases/" in doc:
            return
        ordered = sorted(enumerate(cases), key=lambda t: ((t[1].get("sort") or ""), -t[0]), reverse=True)
        ordered = [c for _, c in ordered]
        blocks = re.split(r"(?m)^(?=### )", doc)
        head, entries = blocks[0], blocks[1:]
        if len(entries) != len(ordered):
            print("llms-full.txt 사례 수(%d)가 데이터(%d)와 달라 페이지 주소를 넣지 않았습니다" % (len(entries), len(ordered)))
            return
        out = [head]
        for blk, c in zip(entries, ordered):
            title = blk.split("\n", 1)[0][4:].strip()
            if title != c["title"]:
                print("llms-full.txt 순서가 데이터와 달라 페이지 주소를 넣지 않았습니다: %r / %r" % (title, c["title"]))
                return
            lines = blk.rstrip("\n").split("\n")
            lines.append("- 페이지: " + page_url(c))
            out.append("\n".join(lines) + "\n\n")
        write(p, "".join(out).rstrip("\n") + "\n")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    site = sys.argv[1]
    index_path, cases_path = os.path.join(site, "index.html"), os.path.join(site, "cases.html")
    index_doc, cases_doc = read(index_path), read(cases_path)
    cases = load_json_block(index_doc, "cases-data")
    links = load_json_block(index_doc, "links-data")
    details = load_details(site)

    stems = [stem_of(c) for c in cases]
    dup = {s for s in stems if stems.count(s) > 1}
    if dup:
        raise SystemExit("판결문 이미지 이름이 겹치는 사례가 있습니다: %s" % sorted(dup))
    for c in cases:
        for im in images_of(c):
            if not os.path.exists(os.path.join(site, im["src"])):
                raise SystemExit("판결문 이미지가 없습니다: %s (%s)" % (im["src"], c["title"]))

    by_cat = {}
    for c in sorted(cases, key=lambda x: x.get("sort") or "", reverse=True):
        by_cat.setdefault(c["cat"], []).append(c)
    cat_counts = {k: len(v) for k, v in by_cat.items()}

    css = re.search(r"<style[^>]*>(.*?)</style>", cases_doc, re.S).group(1)
    write(os.path.join(site, "case.css"), css.strip() + "\n" + EXTRA_CSS)

    # 지워진 사례의 옛 페이지는 치운다
    keep = {os.path.join(site, page_href(c)) for c in cases}
    for old in glob.glob(os.path.join(site, "cases", "*.html")):
        if old not in keep:
            os.remove(old)
    for c in cases:
        write(os.path.join(site, page_href(c)), build_case_page(c, by_cat, cat_counts, details, site))

    # 주제별 모아 보기 페이지
    recent = sorted(cases, key=lambda x: x.get("sort") or "", reverse=True)
    for t in TOPICS:
        matched = [c for c in recent if t in topics_of(c)]
        write(os.path.join(site, topic_href(t)), build_topic_page(t, matched, cat_counts))

    write(index_path, patch_index(index_doc, links))
    write(cases_path, patch_cases(cases_doc, len(cases)))
    write(os.path.join(site, "sitemap.xml"), build_sitemap(cases))
    patch_llms(site, cases)
    n_detail = sum(1 for c in cases if details.get(c["id"]))
    print("사례 페이지 %d건(상세 소개 %d건), 주제 페이지 %d건, sitemap %d URL, case.css, index.html, cases.html 갱신 → %s" % (len(cases), n_detail, len(TOPICS), len(cases) + len(TOPICS) + 2, site))


if __name__ == "__main__":
    main()
