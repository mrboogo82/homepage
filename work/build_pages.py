#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
변호사 부효준 홈페이지 — 항목별 페이지의 공용 부품 맞추기 (2026. 10. 23. 저녁)

홈(index.html) 한 장이던 것을 창천(lawcc.co.kr)처럼 '짧은 홈 + 항목별 페이지'로 나누면서(본인 지시),
루트의 여섯 페이지(index · career · fields · faq · press · contact)가 같은 머리글·바닥글을 쓰도록 index.html 을 기준으로 맞춘다.

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
  3. 홈 '경력' 요약의 기관 띠(법률고문 위촉 약 20곳·위원회 7곳 — 로고와 이름만, 누르면 기관 누리집)를 career.html 의 현행 타일(<li class="adv">)에서 다시 만든다:
       index.html 의 <!-- advisory-chips:start --> … <!-- advisory-chips:end -->, <!-- committees-chips:start --> … <!-- committees-chips:end -->.
     위촉·위원회를 더하거나 뺄 때는 career.html 의 타일만 고치고 이 스크립트를 돌린다.
  4. sitemap.xml 은 build_cases.py 가 만들며 다섯 페이지도 그 목록에 들어 있다.

돌리는 차례(README '고칠 때'): 내용을 고친 뒤 build_press.py(언론보도) → ssr_cases.py(사례) → build_pages.py(공용 부품·기관 띠) → build_cases.py(사례 페이지·사이트맵).
"""
import hashlib
import html
import os
import re
import sys

PAGES = ["career.html", "fields.html", "faq.html", "press.html", "contact.html"]   # index.html 이 기준(master)
ALL_PAGES = ["index.html"] + PAGES
BLOCKS = ["symbols", "header", "quick", "footer", "tail"]
NEEDS_DATA = {"index.html", "fields.html"}   # cases-data.js(사례 데이터, 약 300KB)를 읽는 페이지 — 사례 카드·분야별 건수가 있는 곳만; 다른 페이지의 꼬리에서는 그 태그를 뺀다
DATA_TAG_RE = re.compile(r'<script src="cases-data\.js(?:\?v=[0-9a-f]+)?"></script>\n?')
# 머리글 차림표에서 class="current" 를 받는 링크(href). 홈은 없음(허브).
CURRENT = {"career.html": "career.html", "fields.html": "fields.html", "faq.html": "faq.html", "press.html": "press.html"}


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
UL_RE = re.compile(r'<ul class="advisors">(.*?)</ul>', re.S)


def tiles(section_html):
    """현행 타일(임기를 마친 .past-grid 묶음은 제외) → [(누리집, 기관명, 로고 src, 로고 띠 class 보충(tall/mid))]."""
    out = []
    for ul in UL_RE.findall(section_html):
        for li in LI_RE.findall(ul):
            m = re.search(r'<a class="adv-logo( tall| mid)?" href="([^"]+)"[^>]*data-org="([^"]+)"[^>]*><img src="([^"]+)"', li)
            org = re.search(r'<b class="org">(.*?)</b>', li)
            if m and org:
                out.append((m.group(2), html.unescape(org.group(1)), m.group(4), (m.group(1) or "").strip()))
            elif org:
                out.append(("", html.unescape(org.group(1)), "", ""))
    return out


def chips(items):
    out = []
    for href, org, src, kind in items:
        img = '<img src="%s" alt="" loading="lazy"%s>' % (html.escape(src, quote=True), ' class="%s"' % kind if kind else "") if src else ""
        if href:
            out.append('      <li><a class="org-chip" href="%s" target="_blank" rel="noopener" data-org="%s" aria-label="%s 누리집 (새 창)">%s<span>%s</span></a></li>'
                       % (html.escape(href, quote=True), html.escape(org, quote=True), html.escape(org, quote=True), img, html.escape(org)))
        else:
            out.append('      <li><span class="org-chip" data-org="%s">%s<span>%s</span></span></li>' % (html.escape(org, quote=True), img, html.escape(org)))
    return "\n" + "\n".join(out) + "\n    "


def section(doc, sid):
    m = re.search(r'<div class="block" id="%s">(.*?)\n        </div>\n        <div class="block" id=' % sid, doc, re.S)
    if m:
        return m.group(1)
    m = re.search(r'<div class="block" id="%s">(.*?)\n        </div>\n      </div>\n    </section>' % sid, doc, re.S)
    if not m:
        raise SystemExit("career.html 에서 #%s 묶음을 찾지 못했습니다" % sid)
    return m.group(1)


def current_tiles(block_html):
    """묶음 안에서 '임기를 마친 …'(.past-wrap) 앞까지의 타일."""
    k = block_html.find('<div class="past-wrap')
    return tiles(block_html[:k] if k >= 0 else block_html)


def main():
    args = sys.argv[1:]
    check = "--check" in args
    args = [a for a in args if not a.startswith("--")]
    site = args[0] if args else "."
    idoc = read(os.path.join(site, "index.html"))
    h = site_js_hash(site)
    changed = []

    # 3. 홈 경력 요약의 기관 띠 ← career.html 타일
    cpath = os.path.join(site, "career.html")
    new_idoc = with_js_hash(idoc, h)
    if os.path.exists(cpath):
        cdoc = read(cpath)
        adv = chips(current_tiles(section(cdoc, "advisory")))
        com = chips(current_tiles(section(cdoc, "committees")))
        for name, body in (("advisory-chips", adv), ("committees-chips", com)):
            a, b = "<!-- %s:start -->" % name, "<!-- %s:end -->" % name
            i, j = new_idoc.find(a), new_idoc.find(b)
            if i < 0 or j < 0:
                raise SystemExit("index.html 에 %s 표식이 없습니다" % a)
            new_idoc = new_idoc[:i + len(a)] + body + new_idoc[j:]
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
