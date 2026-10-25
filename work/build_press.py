#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
변호사 부효준 홈페이지 — 홈의 '언론보도' 절 생성기 (2026. 10. 22.)

사용법 (저장소 최상위에서):
    python3 work/build_press.py .          # press.json 대로 index.html의 언론보도 절·llms.txt의 언론보도 목록을 다시 만든다
    python3 work/build_press.py . --check  # 지금 파일이 데이터와 일치하는지 검사만

press.json(items)의 기사 가운데 home 이 true 인 것을 세 묶음으로 보인다:
  수행 사건 보도(kind=case, 관련 사례로 링크) · 토론회·위원회·강의(kind=activity, 본인 발언 quote 포함) ·
  그 밖에 이름이 실린 기사(kind=mention — 2026. 10. 23. 본인 지시로 사법시험 합격자 명단·공익법무관 인사 배치 기사는 모두 뺐으므로 지금은 비어 있음).
2026. 10. 23. 낮 본인 지시("수행사건 보도 최근 3개 정도만 나오게 하고 나머지는 '접기'로") → 2026. 10. 25. 저녁 본인 지시("언론보도도 최근 1개만"): 홈에 보이는 것은 수행 사건 보도
  최근 HOME_RECENT(1)건과 언론보도 페이지(press.html) 링크뿐이고(2026. 10. 23. 저녁: 접힌 목록 대신 페이지로), 전체는 press.html 의 같은 표식 사이에 접지 않고 넣는다(사례 페이지에만 싣던 기사까지 모두).
  (종전 접힌 <details class="press-more">
  ('더 보기 …' / 펼치면 '접기') 안에 들어간다.
index.html 에서는 <!-- press:start --> … <!-- press:end --> 사이를 바꾼다(없으면 상담 문의 절 앞 — 다루는 사건 절 다음 — 에 절 전체를 넣는다;
  2026. 10. 23. 저녁 본인 지시로 홈의 순서가 '다루는 사건 → 언론보도'가 되었다). 절 머리의 설명 문장("수행한 사건의 … 언론보도 페이지에 있습니다")과
  길잡이('무엇을 찾으시나요?') 05 칸의 기사 건수 맞추기는 2026. 10. 25. 본인 지시(설명 문장 삭제, 길잡이 전부 삭제)로 없앴고, 같은 날 '자세히 › 언론보도 전체' 알약도 뺐다 — 절 머리는 제목뿐.
llms.txt 에서는 '## 언론보도' 절을 바꾼다(없으면 '## 연락처' 앞에 넣는다). 그 뒤 ssr_cases.py → build_cases.py 를 돌린다.
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from press_lib import load_press, kdate, check_press, KIND_NAMES  # noqa: E402
from ssr_cases import load_cases  # noqa: E402  (사례 데이터 파일 cases-data.js, 2026. 10. 23.)

SITE = "https://lawyermrboo82.com"
START, END = "<!-- press:start -->", "<!-- press:end -->"
HOME_RECENT = 1   # 홈에 보이는 수행 사건 보도 건수(최근순) — 2026. 10. 25. 저녁 본인 지시로 1건(그 전 2026. 10. 23. 낮 지시 3건). 나머지는 언론보도 페이지(press.html)로


def esc(s):
    return html.escape(s or "", quote=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


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


def section_full(items, cases_by_id):
    """press.html(언론보도 페이지, 2026. 10. 23. 저녁): 접지 않고 전부 — 사건 보도는 사례 페이지에만 싣던 기사까지 모두, 그다음 토론회·위원회·강의."""
    groups = {"case": [], "activity": [], "mention": []}
    for p in items:
        groups.setdefault(p.get("kind") or "case", []).append(p)
    for k in groups:
        groups[k].sort(key=lambda x: x.get("date") or "", reverse=True)
    out = []
    out.append('<header class="section-head">')
    out.append('        <h2 id="press-h">언론보도</h2>')
    out.append('        <p>기사 %d건 — 수행 사건 보도 %d건, %s %d건%s. 사건별 기사는 각 사례 페이지의 \'이 사건의 언론보도\'에도 있습니다.</p>'
               % (len(items), len(groups["case"]), KIND_NAMES["activity"].replace(" · ", "·"), len(groups["activity"]),
                  (", %s %d건" % (KIND_NAMES["mention"], len(groups["mention"]))) if groups["mention"] else ""))
    out.append('      </header>')
    out.append('      <div class="section-body press-body">')
    for k in ("case", "activity", "mention"):
        if not groups[k]:
            continue
        out.append('        <div class="block" id="press-%s">' % ("cases" if k == "case" else k))
        out.append('          <h3 class="block-h">%s</h3>' % esc(KIND_NAMES[k]))
        out.append('          <dl class="rows dates press-list">')
        out += ["            " + row(p, cases_by_id) for p in groups[k]]
        out.append('          </dl>')
        out.append('        </div>')
    out.append('      </div>')
    return "\n".join(out)


def section_inner(items, cases_by_id):
    """홈(index.html)의 언론보도 요약: 수행 사건 보도 최근 HOME_RECENT 건(2026. 10. 25. 저녁부터 1건) + 언론보도 페이지(press.html) 링크 (2026. 10. 23. 저녁 — 접힌 목록 대신 페이지로)."""
    n_all = len(items)
    items = [p for p in items if p.get("home")]
    groups = {"case": [], "activity": [], "mention": []}
    for p in items:
        groups.setdefault(p.get("kind") or "case", []).append(p)
    for k in groups:
        groups[k].sort(key=lambda x: x.get("date") or "", reverse=True)
    out = []
    out.append('<header class="section-head">')
    out.append('        <h2 id="press-h">언론보도</h2>')
    # 절 머리의 설명 문장("수행한 사건의 판결·결정이 보도된 최근 기사입니다. … 전체는 언론보도 페이지에 있습니다.")과
    # '자세히 › 언론보도 전체' 알약(<nav class="jump">)은 2026. 10. 25. 본인 지시로 삭제 — 절 머리는 제목뿐, 전체는 목록 아래 '언론보도 전체 보기 (N건) →' 단추로.
    out.append('      </header>')
    out.append('      <div class="section-body press-body">')
    recent, older = groups["case"][:HOME_RECENT], []
    n_case = 0
    note = ('<p class="press-note">사건별 기사 %d건 가운데 대표 기사 %d건입니다. 나머지는 각 사례 페이지에 있습니다.</p>'
            % (n_case, len(groups["case"]))) if n_case > len(groups["case"]) else ""
    if recent:
        out.append('        <div class="block" id="press-cases">')
        out.append('          <h3 class="block-h">%s</h3>' % esc(KIND_NAMES["case"]))
        out.append('          <dl class="rows dates press-list">')
        out += ["            " + row(p, cases_by_id) for p in recent]
        out.append('          </dl>')
        if not older and note:
            out.append('          ' + note)
        out.append('          <p class="more"><a class="btn ghost" href="press.html">언론보도 전체 보기 (%d건) →</a></p>' % n_all)
        out.append('        </div>')
    # 토론회·위원회·강의 기사와 지난 사건 보도는 홈에 두지 않고 언론보도 페이지(press.html)에만 (2026. 10. 23. 저녁)
    out.append('      </div>')
    return "\n".join(out)


SECTION_TMPL = '''    <section class="section" id="press" aria-labelledby="press-h">
      %s
      %s
      %s
    </section>

'''

CONTACT_ANCHOR = '    <section class="section" id="contact" aria-labelledby="contact-h">'   # 표식이 없을 때 절을 넣는 자리: 다루는 사건 절 다음, 상담 문의 절 앞(2026. 10. 23. 저녁 순서)
# 길잡이('무엇을 찾으시나요?') 05 칸의 기사 건수를 맞추던 FINDER_RE 는 2026. 10. 25. 길잡이 삭제(본인 지시)와 함께 뺐다.


def patch_index(idoc, inner, n_all=None):
    block = SECTION_TMPL % (START, inner, END)
    if START in idoc and END in idoc:
        a, b = idoc.index(START), idoc.index(END) + len(END)
        new = idoc[:a] + START + "\n      " + inner + "\n      " + END + idoc[b:]
    else:
        k = idoc.find(CONTACT_ANCHOR)
        if k < 0:
            raise SystemExit("index.html 에서 '상담 문의' 절을 찾지 못해 언론보도 절을 넣을 자리를 모릅니다")
        new = idoc[:k] + block + idoc[k:]
    # 머리글 차림표·바닥글 차례에 '언론보도' 링크(한 번만)
    # 2026. 10. 23. 저녁부터 머리글·바닥글의 '언론보도' 링크는 press.html 로(공용 부품은 work/build_pages.py 가 맞춤) — 여기서는 손대지 않는다
    return new


def patch_page(pdoc, inner):
    """press.html 의 <!-- press:start --> … <!-- press:end --> 사이를 전체 목록으로."""
    if START not in pdoc or END not in pdoc:
        raise SystemExit("press.html 에 press:start/end 표식이 없습니다")
    a, b = pdoc.index(START), pdoc.index(END) + len(END)
    return pdoc[:a] + START + "\n      " + inner + "\n      " + END + pdoc[b:]


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
    k = doc.find("## 연락처")   # 2026. 10. 23. 저녁: 홈 순서(다루는 사건 → 언론보도)에 맞춰 '## 다루는 사건' 다음
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
    cases = load_cases(site)
    cases_by_id = {c["id"]: c for c in cases}
    press = load_press(site)
    check_press(press, set(cases_by_id))
    inner = section_inner(press, cases_by_id)
    new_idoc = patch_index(idoc, inner, len(press))
    pp = os.path.join(site, "press.html")
    pdoc = read(pp) if os.path.exists(pp) else None
    new_pdoc = patch_page(pdoc, section_full(press, cases_by_id)) if pdoc is not None else None
    new_llms = patch_llms(read(lp), llms_block(press, cases_by_id)) if os.path.exists(lp) else None
    if check:
        ok = new_idoc == idoc and (new_pdoc is None or new_pdoc == pdoc) and (new_llms is None or new_llms == read(lp))
        print("일치" if ok else "불일치")
        sys.exit(0 if ok else 1)
    write(ip, new_idoc)
    if new_pdoc is not None:
        write(pp, new_pdoc)
    if new_llms is not None:
        write(lp, new_llms)
    n_home = sum(1 for p in press if p.get("home"))
    print("언론보도 %d건(홈에 최근 %d건): index.html 언론보도 요약·press.html 전체 목록·llms.txt 갱신" % (len(press), min(HOME_RECENT, n_home)))


if __name__ == "__main__":
    main()
