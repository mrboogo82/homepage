#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
변호사 부효준 홈페이지 — 홈의 '언론보도' 절 생성기 (2026. 10. 22.)

사용법 (저장소 최상위에서):
    python3 work/build_press.py .          # press.json 대로 index.html의 언론보도 절·llms.txt의 언론보도 목록을 다시 만든다
    python3 work/build_press.py . --check  # 지금 파일이 데이터와 일치하는지 검사만

press.json(items)의 기사 가운데 home 이 true 인 것을 세 묶음으로 보인다:
  수행 사건 보도(kind=case, 관련 사례로 링크) · 토론회·위원회·강의(kind=activity, 본인 발언 quote 포함) ·
  그 밖에 이름이 실린 기사(kind=mention, 접힌 <details>).
index.html 에서는 <!-- press:start --> … <!-- press:end --> 사이를 바꾸고(없으면 경력 절 다음에 절 전체를 넣는다),
llms.txt 에서는 '## 언론보도' 절을 바꾼다(없으면 '## 경력' 앞에 넣는다). 그 뒤 ssr_cases.py → build_cases.py 를 돌린다.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from press_lib import load_press, kdate, check_press, KIND_NAMES  # noqa: E402

SITE = "https://lawyermrboo82.com"
START, END = "<!-- press:start -->", "<!-- press:end -->"


def esc(s):
    return html.escape(s or "", quote=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def load_cases(idoc):
    m = re.search(r'<script type="application/json" id="cases-data">(.*?)</script>', idoc, re.S)
    if not m:
        raise SystemExit("index.html 의 #cases-data 를 찾지 못했습니다")
    return json.loads(m.group(1))


def stem_of(c):
    ims = [im for im in (c.get("images") or []) if im and im.get("src")]
    if ims:
        return re.sub(r"\.[A-Za-z0-9]+$", "", ims[0]["src"].rsplit("/", 1)[-1])
    return c["id"]


def row(p, cases_by_id):
    """<dl class="rows dates press-list"> 의 한 줄."""
    links = []
    for cid in p.get("cases") or []:
        c = cases_by_id.get(cid)
        if c:
            links.append('<a href="cases/%s.html">%s</a>' % (esc(stem_of(c)), esc(c["title"])))
    sub = []
    if p.get("note"):
        sub.append(esc(p["note"]))
    if links:
        sub.append("관련 사례: " + " · ".join(links))
    body = ['<span class="head"><span class="outlet">%s</span><a class="press-title" href="%s" target="_blank" rel="noopener">%s</a></span>' % (
        esc(p.get("outlet") or ""), esc(p["url"]), esc(p["title"]))]
    if sub:
        body.append('<span class="sub">%s</span>' % " — ".join(sub))
    if p.get("quote"):
        body.append('<q>%s</q>' % esc(p["quote"]))
    return '<div><dt>%s</dt><dd>%s</dd></div>' % (esc(kdate(p.get("date") or "")), "".join(body))


def section_inner(items, cases_by_id):
    n_case = sum(1 for p in items if (p.get("kind") or "case") == "case")   # 사례 페이지까지 합친 전체 건수(홈에 안 보이는 것 포함)
    items = [p for p in items if p.get("home")]
    groups = {"case": [], "activity": [], "mention": []}
    for p in items:
        groups.setdefault(p.get("kind") or "case", []).append(p)
    for k in groups:
        groups[k].sort(key=lambda x: x.get("date") or "", reverse=True)
    out = []
    out.append('<header class="section-head">')
    out.append('        <h2 id="press-h">언론보도</h2>')
    out.append('        <p>수행한 사건의 판결·결정이 보도된 기사와 토론회·위원회·강의 활동이 실린 기사입니다. 기사 제목을 누르면 해당 언론사의 기사가 새 창으로 열리고, 사례 제목을 누르면 그 사건의 판결문과 소개로 갑니다. 사건별 기사 전체는 각 사례 페이지의 \'이 사건의 언론보도\'에 있습니다.</p>')
    out.append('      </header>')
    out.append('      <div class="section-body press-body">')
    if groups["case"]:
        out.append('        <div class="block" id="press-cases">')
        out.append('          <h3 class="block-h">%s</h3>' % esc(KIND_NAMES["case"]))
        out.append('          <dl class="rows dates press-list">')
        out += ["            " + row(p, cases_by_id) for p in groups["case"]]
        out.append('          </dl>')
        if n_case > len(groups["case"]):
            out.append('          <p class="press-note">사건별 기사 %d건 가운데 대표 기사 %d건입니다. 나머지는 각 사례 페이지에 있습니다.</p>' % (n_case, len(groups["case"])))
        out.append('        </div>')
    if groups["activity"]:
        out.append('        <div class="block" id="press-activity">')
        out.append('          <h3 class="block-h">%s</h3>' % esc(KIND_NAMES["activity"]))
        out.append('          <dl class="rows dates press-list">')
        out += ["            " + row(p, cases_by_id) for p in groups["activity"]]
        out.append('          </dl>')
        out.append('        </div>')
    if groups["mention"]:
        out.append('        <details class="press-more" id="press-mention">')
        out.append('          <summary>%s (인사 · 합격자 명단) %d건</summary>' % (esc(KIND_NAMES["mention"]), len(groups["mention"])))
        out.append('          <dl class="rows dates press-list">')
        out += ["            " + row(p, cases_by_id) for p in groups["mention"]]
        out.append('          </dl>')
        out.append('        </details>')
    out.append('      </div>')
    return "\n".join(out)


SECTION_TMPL = '''    <section class="section" id="press" aria-labelledby="press-h">
      %s
      %s
      %s
    </section>

'''

FIELDS_ANCHOR = '    <section class="section" id="fields" aria-labelledby="fields-h">'


def patch_index(idoc, inner):
    block = SECTION_TMPL % (START, inner, END)
    if START in idoc and END in idoc:
        a, b = idoc.index(START), idoc.index(END) + len(END)
        new = idoc[:a] + START + "\n      " + inner + "\n      " + END + idoc[b:]
    else:
        k = idoc.find(FIELDS_ANCHOR)
        if k < 0:
            raise SystemExit("index.html 에서 '다루는 사건' 절을 찾지 못해 언론보도 절을 넣을 자리를 모릅니다")
        new = idoc[:k] + block + idoc[k:]
    # 머리글 차림표·바닥글 차례에 '언론보도' 링크(한 번만)
    if '<a href="#press">' not in new.split("<main>")[0]:
        new = new.replace('      <a href="#career">경력</a>\n      <a href="#fields">다루는 사건</a>',
                          '      <a href="#career">경력</a>\n      <a href="#press">언론보도</a>\n      <a href="#fields">다루는 사건</a>', 1)
    foot = '<a href="#committees">위원회·강의</a> <a href="#fields">다루는 사건</a>'
    if foot in new and '<a href="#press">언론보도</a> <a href="#fields">' not in new:
        new = new.replace(foot, '<a href="#committees">위원회·강의</a> <a href="#press">언론보도</a> <a href="#fields">다루는 사건</a>', 1)
    return new


def llms_block(items, cases_by_id):
    lines = ["## 언론보도 (수행 사건·활동이 실린 기사)"]
    for p in sorted(items, key=lambda x: x.get("date") or "", reverse=True):
        rel = " · ".join("%s/cases/%s.html" % (SITE, stem_of(cases_by_id[cid])) for cid in (p.get("cases") or []) if cid in cases_by_id)
        lines.append("- %s %s 「%s」 %s%s%s" % (p.get("outlet") or "", kdate(p.get("date") or ""), p["title"], p["url"],
                                          (" — " + p["note"]) if p.get("note") else "", (" (관련 사례: %s)" % rel) if rel else ""))
    return "\n".join(lines) + "\n\n"


def patch_llms(doc, block):
    m = re.search(r"(?ms)^## 언론보도.*?(?=^## |\Z)", doc)
    if m:
        return doc[: m.start()] + block + doc[m.end():]
    k = doc.find("## 경력")
    if k < 0:
        return doc.rstrip("\n") + "\n\n" + block
    return doc[:k] + block + doc[k:]


def main():
    args = sys.argv[1:]
    check = "--check" in args
    args = [a for a in args if not a.startswith("--")]
    site = args[0] if args else "."
    ip, lp = os.path.join(site, "index.html"), os.path.join(site, "llms.txt")
    idoc = read(ip)
    cases = load_cases(idoc)
    cases_by_id = {c["id"]: c for c in cases}
    press = load_press(site)
    check_press(press, set(cases_by_id))
    inner = section_inner(press, cases_by_id)
    new_idoc = patch_index(idoc, inner)
    new_llms = patch_llms(read(lp), llms_block(press, cases_by_id)) if os.path.exists(lp) else None
    if check:
        ok = new_idoc == idoc and (new_llms is None or new_llms == read(lp))
        print("일치" if ok else "불일치")
        sys.exit(0 if ok else 1)
    write(ip, new_idoc)
    if new_llms is not None:
        write(lp, new_llms)
    n_home = sum(1 for p in press if p.get("home"))
    print("언론보도 %d건(홈에 %d건): index.html 언론보도 절·llms.txt 갱신" % (len(press), n_home))


if __name__ == "__main__":
    main()
