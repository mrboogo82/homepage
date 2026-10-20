#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사례 데이터(index.html의 #cases-data)로부터 두 페이지의 정적 사례 목록, cases.html의 데이터 블록,
llms.txt·llms-full.txt, 건수 문구를 다시 만든다. build_cases.py 보다 먼저 돌린다.

사용법 (저장소 최상위에서):
    python3 work/ssr_cases.py .          # 갱신
    python3 work/ssr_cases.py . --check  # 지금 파일이 데이터와 일치하는지 검사만

규칙(페이지의 JS card() 와 같은 마크업):
  - 홈(index.html): 주요 분야(rnd·penalty·criminal)의 최근 9건, sort 내림차순(같으면 데이터 순).
    (2026. 10. 21. 12건→9건: 세 장씩 놓이는 화면은 9건, 두 장씩 놓이는 화면은 페이지 CSS가 아홉째 장을 감춰 8건)
  - 전체(cases.html): 전체를 sort 내림차순(같으면 데이터 순)으로.
  - 제목·'자세히 →' 링크는 cases/<첫 이미지 이름>.html (build_cases.py의 page_href 와 같음).
  - 2026. 10. 21. 본인 지시: 카드에는 '판결문 N장' 수를 적지 않고, 요지는 두 줄로 접되 '더 보기' 단추 없이
    '자세히 →' 링크 하나만 둔다(자세히 보려는 사람은 한 번만 누르면 개별 페이지로).
"""
import html
import json
import os
import re
import sys

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
    "civil": "민사·연금·계약",
}
MAIN = ("rnd", "penalty", "criminal")
RECENT = 9
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


def with_keywords(cases, details):
    """cases.html 데이터 블록용: 상세 소개의 검색어(keywords)를 각 항목의 kw 에 넣은 사본."""
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


def render_list(cases, cats=None, limit=None):
    lst = ordered(cases, cats)
    if limit:
        lst = lst[:limit]
    return "\n".join(render_li(c) for c in lst)


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


# ---------- llms ----------

def llms_full(cases, intro_from=None, details=None):
    details = details or {}
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
    lines += ["", "## 수행 사례 (%d건, 최근 순)" % n, ""]
    for c in ordered(cases):
        ims = images_of(c)
        lines.append("### " + c["title"])
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
        lines.append("- 페이지: %s/%s" % (SITE, page_href(c)))
        lines.append("")
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
    cases, _ = load_json_block(idoc, "cases-data")
    n = len(cases)
    details = load_details(site)
    cases_kw = with_keywords(cases, details)   # 두 페이지의 데이터 블록에 검색어(kw)를 더한다(단어로 찾기에 쓰임)

    home = render_list(cases_kw, MAIN, RECENT)
    full = render_list(cases_kw)
    new_idoc = count_text(replace_json_block(replace_list(idoc, home), "cases-data", cases_kw), n)
    new_cdoc = count_text(replace_json_block(replace_list(cdoc, full), "cases-data", cases_kw), n)

    lp, fp = os.path.join(site, "llms.txt"), os.path.join(site, "llms-full.txt")
    new_llms = None
    if os.path.exists(lp):
        d = read(lp)
        d = re.sub(r"주요 수행 사례 \d+건을", "주요 수행 사례 %d건을" % n, d)
        d = re.sub(r"사건 \d+건, 최근 결정일 순", "사건 %d건, 최근 결정일 순" % n, d)
        d = re.sub(r"\d+건의 제목·분야", "%d건의 제목·분야" % n, d)
        new_llms = d
    new_full = llms_full(cases, llms_head(read(fp)), details) if os.path.exists(fp) else None

    if check:
        ok = True
        if current_list(idoc) != home:
            print("index.html 정적 목록이 데이터와 다릅니다"); ok = False
        if current_list(cdoc) != full:
            print("cases.html 정적 목록이 데이터와 다릅니다"); ok = False
        cj, _ = load_json_block(cdoc, "cases-data")
        if cj != cases_kw:
            print("cases.html 데이터 블록이 index.html과 다릅니다"); ok = False
        if cases != cases_kw:
            print("index.html 데이터 블록의 검색어(kw)가 cases-detail.json과 다릅니다"); ok = False
        if new_full is not None and read(fp) != new_full:
            print("llms-full.txt가 데이터와 다릅니다"); ok = False
        print("일치" if ok else "불일치")
        sys.exit(0 if ok else 1)

    write(ip, new_idoc)
    write(cp, new_cdoc)
    if new_llms is not None:
        write(lp, new_llms)
    if new_full is not None:
        write(fp, new_full)
    print("사례 %d건: index.html(홈 %d건)·cases.html·llms.txt·llms-full.txt 갱신" % (n, min(RECENT, len(ordered(cases, MAIN)))))


if __name__ == "__main__":
    main()
