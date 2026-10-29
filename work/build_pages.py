#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
변호사 부효준 홈페이지 — 항목별 페이지의 공용 부품 맞추기 (2026. 10. 23. 저녁)

홈(index.html) 한 장이던 것을 창천(lawcc.co.kr)처럼 '짧은 홈 + 항목별 페이지'로 나누면서(본인 지시),
루트의 다섯 페이지(index · career · fields · press · contact)가 같은 머리글·바닥글을 쓰도록 index.html 을 기준으로 맞춘다.

사용법 (저장소 최상위에서):
    python3 work/build_pages.py .          # 맞춤
    python3 work/build_pages.py . --check  # 일치 여부만

하는 일:
  1. index.html 의 공용 부품 다섯 묶음을 다른 다섯 페이지에 그대로 복사한다. 묶음은 <!-- chrome:이름:start --> … <!-- chrome:이름:end --> 표식 사이:
       symbols  그림 심벌(<svg width="0" …> — 전화·위치 그림, SNS 로고)
       header   머리글(<header class="top">) — 복사할 때 그 페이지의 차림표 항목에 class="current"
       quick    본문 끝의 '사무소 위치 | 전화' 띠(<nav class="quick">)
       footer   바닥글(<footer class="sign">)과 '맨 위로' 단추
       tail     판결문·위촉장 크게 보기 창(<dialog>), 온라인 계정 목록(#links-data), cases-data.js(사례 카드·분야 건수가 있는 index·fields 에만)·site.js 스크립트 태그
     그러므로 머리글·바닥글·계정·스크립트를 고칠 때는 index.html 만 고치고 이 스크립트를 돌리면 된다. cases.html 과 사례·주제 페이지는 머리글이 달라(홈으로·상담 문의만)
     여기서 맞추지 않는다(사례·주제 페이지는 build_cases.py 의 템플릿).
  2. 공용 스크립트 site.js 의 해시를 <script src="site.js?v=해시"> 에 넣는다(여섯 페이지 모두). 브라우저 캐시 때문.
  3. 홈 '경력' 절의 위촉장 타일과 한 줄 요약을 career.html 에서 다시 만든다(2026. 10. 23. 오후 본인 지시: 현행 법률고문 위촉·위원회의 위촉장은 모두 홈 본문에, 나머지는 간단하게):
       <!-- advisory-tiles:start/end -->   career.html #advisory 의 현행 타일(소제목 '중앙행정기관 · 지방자치단체' / '공공기관 · 공기업 · 단체'와 <ul class="advisors">) 그대로
       <!-- advisory-past:start/end -->    임기를 마친 위촉 한 줄(타일의 기관·역할·기간 + 글줄의 것) + career.html 링크
       <!-- committees-tiles:start/end --> #committees 의 현행 위원회 타일 그대로
       <!-- committees-past:start/end -->  임기를 마친 위원회 한 줄 + 강의 한 줄
     위촉·위원회·강의를 더하거나 뺄 때는 career.html 만 고치고 이 스크립트를 돌린다.
  4. sitemap.xml 은 build_cases.py 가 만들며 다섯 페이지도 그 목록에 들어 있다.

돌리는 차례(README '고칠 때'): 내용을 고친 뒤 build_press.py(언론보도) → ssr_cases.py(사례) → build_pages.py(공용 부품·기관 띠) → build_cases.py(사례 페이지·사이트맵).
"""
import hashlib
import html
import os
import re
import sys

PAGES = ["career.html", "fields.html", "press.html", "contact.html", "privacy.html"]   # index.html 이 기준(master); faq.html 은 2026. 10. 23. 오후 삭제; privacy.html(개인정보처리방침) 은 2026. 10. 29. 추가
ALL_PAGES = ["index.html"] + PAGES
BLOCKS = ["symbols", "header", "quick", "footer", "tail"]
NEEDS_DATA = {"index.html", "fields.html"}   # cases-data.js(사례 데이터, 약 300KB)를 읽는 페이지 — 사례 카드·분야별 건수가 있는 곳만; 다른 페이지의 꼬리에서는 그 태그를 뺀다
DATA_TAG_RE = re.compile(r'<script src="cases-data\.js(?:\?v=[0-9a-f]+)?"></script>\n?')
# 머리글 차림표에서 class="current" 를 받는 링크(href). 홈은 없음(허브).
CURRENT = {"career.html": "career.html", "fields.html": "fields.html", "press.html": "press.html", "contact.html": "contact.html"}   # contact 는 2026. 10. 27. '상담 문의'가 단추에서 글자 링크가 되면서 추가


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def marks(name):
    return "<!-- chrome:%s:start -->" % name, "<!-- chrome:%s:end -->" % name


def get_block(doc, name, fname):
    a, b = marks(name)
    i, j = doc.find(a), doc.find(b)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("%s 에 %s 표식이 없습니다" % (fname, a))
    return doc[i + len(a):j]


def set_block(doc, name, content, fname):
    a, b = marks(name)
    i, j = doc.find(a), doc.find(b)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("%s 에 %s 표식이 없습니다" % (fname, a))
    return doc[:i + len(a)] + content + doc[j:]


def mark_current(header, page):
    """머리글 차림표의 링크 가운데 이 페이지로 가는 것에만 class="current"."""
    header = re.sub(r'(<a )class="current" (href="[^"]+")', r"\1\2", header)   # 기존 표시 제거
    target = CURRENT.get(page)
    if not target:
        return header
    return header.replace('<a href="%s">' % target, '<a class="current" href="%s">' % target, 1)


def site_js_hash(site):
    p = os.path.join(site, "site.js")
    return hashlib.md5(open(p, "rb").read()).hexdigest()[:8] if os.path.exists(p) else None


def with_js_hash(doc, h):
    return re.sub(r'<script src="site\.js(?:\?v=[0-9a-f]+)?"></script>', '<script src="site.js?v=%s"></script>' % h, doc) if h else doc


LI_RE = re.compile(r'<li class="adv">(.*?)</li>', re.S)


def block_of(doc, sid):
    """career.html 의 <div class="block" id="sid"> … 안쪽(다음 block 또는 절 끝까지)."""
    m = re.search(r'<div class="block" id="%s">(.*?)\n        </div>\n        <div class="block" id=' % sid, doc, re.S)
    if not m:
        m = re.search(r'<div class="block" id="%s">(.*?)\n        </div>\n      </div>\n    </section>' % sid, doc, re.S)
    if not m:
        raise SystemExit("career.html 에서 #%s 묶음을 찾지 못했습니다" % sid)
    return m.group(1)


def strip_tags(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h)).strip()


def current_tiles_html(block_html):
    """묶음 안에서 첫 소제목(<h4 class="sub-h">)부터 '임기를 마친 …'(.past-wrap) 앞까지 — 현행 타일 목록 그대로."""
    a = block_html.find('<h4 class="sub-h">')
    b = block_html.find('<div class="past-wrap')
    if a < 0:
        raise SystemExit("career.html 묶음에 소제목(<h4 class=\"sub-h\">)이 없습니다")
    part = block_html[a:b] if b >= 0 else block_html[a:]
    return "\n          " + part.strip() + "\n          "


def past_items(block_html):
    """'임기를 마친 …' 타일 → '기관명 역할(기간)' 조각들(기관명은 누리집 링크)."""
    out = []
    m = re.search(r'<ul class="advisors past-grid">(.*?)</ul>', block_html, re.S)
    for li in (LI_RE.findall(m.group(1)) if m else []):
        href = re.search(r'<a class="adv-logo[^"]*" href="([^"]+)"', li)
        org = re.search(r'<b class="org">(.*?)</b>', li, re.S)
        role = re.search(r'<span class="role">(.*?)</span>', li, re.S)
        term = re.search(r'<span class="term">(.*?)</span>', li, re.S)
        if not org:
            continue
        name = strip_tags(org.group(1))
        name_html = ('<a href="%s" target="_blank" rel="noopener">%s</a>' % (html.escape(href.group(1), quote=True), html.escape(name))) if href else html.escape(name)
        role_txt = strip_tags(role.group(1)).split(" · ")[0] if role else ""
        term_txt = strip_tags(term.group(1)) if term else ""
        out.append("%s %s(%s)" % (name_html, html.escape(role_txt), html.escape(term_txt)) if term_txt else "%s %s" % (name_html, html.escape(role_txt)))
    # 타일 없이 글줄로만 적힌 것(<p class="past">…)
    m2 = re.search(r'<ul class="advisors past-grid">.*?</ul>\s*<p class="past">(.*?)</p>', block_html, re.S)
    if m2:
        out += [x.strip() for x in m2.group(1).split(" · ") if x.strip()]
    return out


def lecture_items(block_html):
    """강의 목록(<h4>강의</h4> 아래 dl.rows.dates) → '기관 과정 — 과목(날짜)' 조각들."""
    m = re.search(r'<h4>강의</h4>\s*<dl class="rows dates">(.*?)</dl>', block_html, re.S)
    if not m:
        return []
    out = []
    for dt, dd in re.findall(r'<div><dt>(.*?)</dt><dd>(.*?)</dd></div>', m.group(1), re.S):
        sub = re.search(r'<span class="sub">(.*?)</span>', dd, re.S)
        main = strip_tags(re.sub(r'<span class="sub">.*?</span>', '', dd, flags=re.S))
        out.append("%s — %s(%s)" % (html.escape(main), html.escape(strip_tags(sub.group(1))), html.escape(strip_tags(dt))) if sub else "%s(%s)" % (html.escape(main), html.escape(strip_tags(dt))))
    return out


def past_line(label, items, more_href, more_text):
    if not items:
        return "\n          "
    return '\n          <p class="past"><b>%s</b> %s · <a href="%s">%s</a></p>\n          ' % (label, " · ".join(items), more_href, more_text)


def fill(doc, name, body):
    a, b = "<!-- %s:start -->" % name, "<!-- %s:end -->" % name
    i, j = doc.find(a), doc.find(b)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("index.html 에 %s 표식이 없습니다" % a)
    return doc[:i + len(a)] + body + doc[j:]


def main():
    args = sys.argv[1:]
    check = "--check" in args
    args = [a for a in args if not a.startswith("--")]
    site = args[0] if args else "."
    idoc = read(os.path.join(site, "index.html"))
    h = site_js_hash(site)
    changed = []

    # 3. 홈 경력 절의 위촉장 타일·한 줄 요약 ← career.html
    cpath = os.path.join(site, "career.html")
    new_idoc = with_js_hash(idoc, h)
    if os.path.exists(cpath):
        cdoc = read(cpath)
        adv, com = block_of(cdoc, "advisory"), block_of(cdoc, "committees")
        new_idoc = fill(new_idoc, "advisory-tiles", current_tiles_html(adv))
        new_idoc = fill(new_idoc, "advisory-past", past_line("임기를 마친 위촉", past_items(adv), "career.html#advisory", "위촉장 보기 →"))
        new_idoc = fill(new_idoc, "committees-tiles", current_tiles_html(com))
        new_idoc = fill(new_idoc, "committees-past",
                        past_line("임기를 마친 위원회", past_items(com), "career.html#committees", "위촉장 보기 →").rstrip() +
                        past_line("강의", lecture_items(com), "career.html#committees", "자세히 →"))
    if new_idoc != idoc:
        changed.append("index.html")
        if not check:
            write(os.path.join(site, "index.html"), new_idoc)
    blocks = {name: get_block(new_idoc, name, "index.html") for name in BLOCKS}

    # 1·2. 다른 페이지의 공용 부품
    for page in PAGES:
        p = os.path.join(site, page)
        if not os.path.exists(p):
            print("없음(건너뜀): " + page)
            continue
        doc = read(p)
        new = doc
        for name in BLOCKS:
            body = blocks[name]
            if name == "header":
                body = mark_current(body, page)
            if name == "tail" and page not in NEEDS_DATA:
                body = DATA_TAG_RE.sub("", body)
            new = set_block(new, name, body, page)
        new = with_js_hash(new, h)
        if new != doc:
            changed.append(page)
            if not check:
                write(p, new)
    if check:
        print("일치" if not changed else "불일치: " + ", ".join(changed))
        sys.exit(0 if not changed else 1)
    print("공용 부품 맞춤: %s (site.js?v=%s)" % (", ".join(changed) if changed else "바뀐 것 없음", h))


if __name__ == "__main__":
    main()
