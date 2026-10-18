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

NEW_TITLE = "변호사 부효준 — 행정쟁송 · 국가연구개발 제재처분 변호사 | 법무법인(유한) 금성"
NEW_CASES_TITLE = "주요 수행 사례 277건 — 행정소송 · 국가연구개발 제재처분 판결문 · 변호사 부효준"


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


def build_case_page(c, by_cat, cat_counts):
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
                "inLanguage": "ko",
                "datePublished": TODAY,
                "dateModified": TODAY,
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
<meta name="description" content="{esc(desc)}">
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
        {ext_link}
      </section>
      <section class="case-docs" aria-labelledby="docs-h">
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


def patch_index(doc, links):
    doc = patch_html_lang(doc)
    doc = doc.replace("<title>변호사 부효준</title>", "<title>%s</title>" % NEW_TITLE, 1)
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', doc, re.S)
    if m:
        ld = json.loads(m.group(1))
        ld.setdefault("@id", SITE + "/#person")
        same = [clean_url(l["url"]) for l in links if l.get("url") and "keumseong" not in l["url"]]
        ld["sameAs"] = same
        if isinstance(ld.get("worksFor"), dict):
            ld["worksFor"].setdefault("url", "https://www.keumseong.com")
        ld.setdefault("knowsLanguage", "ko")
        # 순서: @context, @type, @id 가 앞에 오도록
        ordered = {k: ld[k] for k in ["@context", "@type", "@id"] if k in ld}
        ordered.update({k: v for k, v in ld.items() if k not in ordered})
        doc = doc[: m.start(1)] + json.dumps(ordered, ensure_ascii=False, indent=1) + doc[m.end(1):]
    doc = link_static_cards(doc)
    doc = patch_js(doc)
    return doc


def patch_cases(doc):
    doc = patch_html_lang(doc)
    doc = doc.replace("<title>주요 수행 사례 전체 · 변호사 부효준</title>", "<title>%s</title>" % NEW_CASES_TITLE, 1)
    doc = doc.replace('<meta property="og:title" content="주요 수행 사례 전체 · 변호사 부효준">',
                      '<meta property="og:title" content="%s">' % NEW_CASES_TITLE, 1)
    doc = doc.replace('<meta name="twitter:title" content="주요 수행 사례 전체 · 변호사 부효준">',
                      '<meta name="twitter:title" content="%s">' % NEW_CASES_TITLE, 1)
    doc = link_static_cards(doc)
    doc = patch_js(doc)
    return doc


def build_sitemap(cases):
    rows = [
        (SITE + "/", TODAY, "weekly", "1.0"),
        (SITE + "/cases.html", TODAY, "weekly", "0.9"),
    ]
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
        if "사례별 개별 페이지" not in doc:
            anchor = "- [수행 사례 전체 텍스트](https://lawyermrboo82.com/llms-full.txt)"
            k = doc.find(anchor)
            if k >= 0:
                e = doc.find("\n", k)
                doc = doc[: e + 1] + line + "\n" + doc[e + 1:]
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
        write(os.path.join(site, page_href(c)), build_case_page(c, by_cat, cat_counts))

    write(index_path, patch_index(index_doc, links))
    write(cases_path, patch_cases(cases_doc))
    write(os.path.join(site, "sitemap.xml"), build_sitemap(cases))
    patch_llms(site, cases)
    print("사례 페이지 %d건, sitemap %d URL, case.css, index.html, cases.html 갱신 → %s" % (len(cases), len(cases) + 2, site))


if __name__ == "__main__":
    main()
