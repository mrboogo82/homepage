#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
스마트공장 관련 사업 이름을 '스마트공장 구축, 확산 사업'으로 통일 (2026. 10. 21. 본인 지시: 제목·내용 모두)

사용법 (저장소 최상위에서):
    python3 work/smart_factory_term.py .            # 적용 (그 뒤 ssr_cases.py → build_cases.py 를 돌린다)
    python3 work/smart_factory_term.py . --dry-run  # 바뀔 문장만 보여 주고 파일은 손대지 않음
    python3 work/smart_factory_term.py . --check    # 남아 있는 다른 표기(판결문 원문 인용 제외)를 보고

규칙:
  1. '스마트공장 보급·확산사업', '보급·확산 사업', '보급·확산 지원사업', '보급사업', '구축사업', '구축 사업',
     '구축 지원사업', '지원사업', '사업' 등 사업 이름의 여러 표기를 모두 '스마트공장 구축, 확산 사업'(TERM)으로 바꾼다.
     옛 이름의 머리·꼬리('ICT 융합 …(추경)', '업종별 특화 …', '…(고도화 과제)')는 괄호 설명으로만 남긴다.
  2. 사례 데이터(cases-data.js(사례 데이터 파일; 2026. 10. 23. index.html #cases-data 블록에서 분리)·work/detail_inputs/cases.json)의 title·summary·court·images[].alt·kw 와
     상세 소개(cases-detail.json·work/details/*.json)의 본문·laws·keywords·quotes[].from 에 적용한다.
     quotes[].text(판결문·결정문 원문 인용)는 원문이므로 손대지 않는다. 바뀐 뒤 같은 검색어가 겹치면 하나만 남긴다.
  3. '스마트공장 구축 협약', '스마트공장 시스템', '스마트공장 고도화'(과제 유형)처럼 사업 이름이 아닌 말은 그대로 둔다.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssr_cases as S  # noqa: E402

TERM = "스마트공장 구축, 확산 사업"
TEXT_FIELDS = ("overview", "claims", "argument", "issues", "holding", "meaning", "instagram", "blog", "summary_new",
               "laws", "claims_label", "argument_label", "holding_label")
CASE_FIELDS = ("title", "summary", "court")

# (가) 옛 이름의 머리·꼬리가 붙은 표기를 먼저 (순서가 중요)
SPECIAL = [
    (r"ICT 융합 스마트공장 보급·확산 지원사업", TERM),                       # 2017년도 … (추경)
    (r"업종별 특화 스마트공장 구축 지원사업", TERM + "(업종별 특화)"),         # 2022년 …
    (r"['‘]스마트공장 고도화 사업['’]에 공급기업으로", "고도화 과제에 공급기업으로"),   # 보급·확산사업 안의 고도화 과제
    (r"스마트공장 추진 사업운영 관리요령", TERM + " 운영 관리요령"),
]
# (나) 일반형: 스마트공장 (보급·확산|보급확산|보급|구축) (지원)사업 / 스마트공장 지원사업 / 스마트공장 사업
GENERAL = re.compile(r"스마트공장\s*(?:보급\s*[·･]?\s*확산|보급|구축)?\s*(?:지원)?사업")


def fix_text(s):
    if not s or "스마트공장" not in s:
        return s
    for pat, rep in SPECIAL:
        s = re.sub(pat, rep, s)
    s = GENERAL.sub(TERM, s)
    return s


def dedupe(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


def fix_case(c, log):
    """사례 항목(index.html 데이터·detail_inputs/cases.json)."""
    changed = False
    for f in CASE_FIELDS:
        v = c.get(f)
        if v and "스마트공장" in v:
            nv = fix_text(v)
            if nv != v:
                log.append((c["id"], f, v, nv)); c[f] = nv; changed = True
    for im in c.get("images") or []:
        a = im.get("alt")
        if a and "스마트공장" in a:
            na = fix_text(a)
            if na != a:
                log.append((c["id"], "images.alt", a, na)); im["alt"] = na; changed = True
    if c.get("kw"):
        nk = dedupe([fix_text(k) for k in c["kw"]])
        if nk != c["kw"]:
            log.append((c["id"], "kw", " | ".join(c["kw"]), " | ".join(nk))); c["kw"] = nk; changed = True
    return changed


def fix_detail(cid, d, log):
    """상세 소개(cases-detail.json·work/details/*.json). quotes[].text 는 그대로."""
    changed = False
    for f in TEXT_FIELDS:
        v = d.get(f)
        if not v:
            continue
        if isinstance(v, list):
            nv = [fix_text(p) if isinstance(p, str) else p for p in v]
        elif isinstance(v, str):
            nv = fix_text(v)
        else:
            continue
        if nv != v:
            for a, b in zip(v if isinstance(v, list) else [v], nv if isinstance(nv, list) else [nv]):
                if a != b:
                    log.append((cid, f, a, b))
            d[f] = nv; changed = True
    if d.get("keywords"):
        nk = dedupe([fix_text(k) for k in d["keywords"]])
        if nk != d["keywords"]:
            log.append((cid, "keywords", " | ".join(d["keywords"]), " | ".join(nk))); d["keywords"] = nk; changed = True
    for q in d.get("quotes") or []:
        if q.get("from") and "스마트공장" in q["from"]:
            nf = fix_text(q["from"])
            if nf != q["from"]:
                log.append((cid, "quotes.from", q["from"], nf)); q["from"] = nf; changed = True
    # 사례 항목 필드가 상세 파일(work/details)에 함께 들어 있을 때
    for f in CASE_FIELDS:
        v = d.get(f)
        if isinstance(v, str) and "스마트공장" in v:
            nv = fix_text(v)
            if nv != v:
                log.append((cid, f, v, nv)); d[f] = nv; changed = True
    return changed


OTHER = re.compile(r"스마트공장(?!\s*구축, 확산 사업)[^\s,.·)('’]*(?:\s*(?:지원)?사업)")


def remaining(cases, details):
    """원문 인용을 뺀 나머지에 남은 다른 사업 표기."""
    out = []
    for c in cases:
        for f in CASE_FIELDS:
            if OTHER.search(c.get(f) or ""):
                out.append((c["id"], f, c[f]))
        for k in c.get("kw") or []:
            if OTHER.search(k):
                out.append((c["id"], "kw", k))
        d = details.get(c["id"]) or {}
        for f in TEXT_FIELDS + ("keywords",):
            v = d.get(f)
            if not v:
                continue
            for p in (v if isinstance(v, list) else [v]):
                if isinstance(p, str) and OTHER.search(p):
                    out.append((c["id"], f, p))
    return out


def main():
    site = sys.argv[1] if len(sys.argv) > 1 else "."
    dry = "--dry-run" in sys.argv
    check = "--check" in sys.argv
    cases = S.load_cases(site)
    dp = os.path.join(site, "cases-detail.json")
    details = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else {}

    if check:
        rem = remaining(cases, details)
        for cid, f, p in rem:
            print("%s [%s] %s" % (cid, f, p))
        print("남은 곳: %d" % len(rem))
        return

    log = []
    n_case = sum(1 for c in cases if fix_case(c, log))
    n_det = sum(1 for cid, d in details.items() if fix_detail(cid, d, log))

    extra = []
    for path in sorted(glob.glob(os.path.join(site, "work", "details", "*.json"))):
        data = json.load(open(path, encoding="utf-8"))
        ch = any([fix_detail(cid, d, extra) for cid, d in data.items()])
        if ch and not dry:
            json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    cp = os.path.join(site, "work", "detail_inputs", "cases.json")
    if os.path.exists(cp):
        data = json.load(open(cp, encoding="utf-8"))
        ch = any([fix_case(c, extra) for c in data])
        if ch and not dry:
            json.dump(data, open(cp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    for cid, f, a, b in log:
        print("== %s [%s]\n   - %s\n   + %s" % (cid, f, a, b))
    print("사례 %d건·상세 %d건 바뀜, 작업용 파일 항목 %d곳" % (n_case, n_det, len(extra)))
    if dry:
        print("(--dry-run: 파일은 바꾸지 않았습니다)")
        return
    S.save_cases(site, cases)
    json.dump(details, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rem = remaining(cases, details)
    print("남은 다른 표기(원문 인용 제외): %d곳" % len(rem))
    for cid, f, p in rem:
        print("  ", cid, f, p)


if __name__ == "__main__":
    main()
