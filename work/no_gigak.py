#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수행 사례 결과 표시 단순화 + 국가·행정청·공공기관을 대리한 사건의 설명에서 '기각' 표현 없애기 (2026. 10. 20. 결정)

사용법 (저장소 최상위에서):
    python3 work/no_gigak.py .            # 적용 (그 뒤 ssr_cases.py → build_cases.py 를 돌린다)
    python3 work/no_gigak.py . --dry-run  # 바뀔 문장만 보여 주고 파일은 손대지 않음
    python3 work/no_gigak.py . --check    # 남아 있는 '기각'(판결문 원문 인용 제외)을 보고

규칙:
  1. result: '승소 (…)' → '승소', '일부승소 (…)' → '일부승소'. 괄호 설명은 화해권고결정·화해·조정·형사 결과처럼
     승소/일부승소가 아닌 결과에만 남긴다.
  2. party 가 비어 있거나 '보조참가'인 사례(= 국가·행정청·지방자치단체·공공기관을 대리한 사건, 형사 사건 제외)의
     title·summary 와 cases-detail.json 의 overview·claims·argument·issues·holding·meaning·keywords·instagram 에서
     '기각'을 다른 표현으로 바꾼다. quotes(판결문·결정문 원문 인용)는 원문이므로 손대지 않는다.
  3. work/details/*.json (summary_new 포함)과 work/detail_inputs/cases.json 에도 같은 규칙을 적용해
     나중에 merge_details.py 를 다시 돌려도 되돌아가지 않게 한다.
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssr_cases as S  # noqa: E402

TEXT_FIELDS = ("overview", "claims", "argument", "issues", "holding", "meaning", "instagram", "blog", "summary_new")
ADMIN_CATS = ("rnd", "penalty", "personnel", "license", "admin")

# ---------- 1. 결과 표시 ----------


def fix_result(r):
    r = (r or "").strip()
    if r.startswith("일부승소"):
        return "일부승소"
    if r.startswith("승소"):
        return "승소"
    return r


# ---------- 2. 문장 ----------

# (가) 특정 표현을 먼저 바꾼다 (순서가 중요)
SPECIAL = [
    # 괄호 요약
    (r"\s*\(청구 기각, 항소 기각\)", ""),
    (r"\(심리불속행 기각\)", "(심리불속행)"),
    (r"\(각하·항고기각\)", "(각하 결정과 항고심)"),
    (r"기각\)", "받아들여지지 않음)"),
    # 같은 말이 거듭되지 않도록 먼저 손보는 문장들
    (r"1심은 원고 회사의 청구를 기각하였고, 서울고등법원은 (\d{4}년 \d{1,2}월) 항소를 기각하였으며, 대법원은 (\d{4}년 \d{1,2}월) 상고를 기각하여",
     r"1심은 원고 회사의 청구를 받아들이지 않았고, 서울고등법원은 \1 1심의 결론을 유지하였으며, 대법원은 \2 상고심을 마무리하여"),
    (r"항소심도 ((?:\d{4}년 (?:\d{1,2}월 )?)?)항소를 (?:모두 )?기각하였습니다", r"항소심도 \1같은 결론을 유지하였습니다"),
    (r"항소심도 ((?:\d{4}년 (?:\d{1,2}월 )?)?)항소를 (?:모두 )?기각하였고", r"항소심도 \1같은 결론을 유지하였고"),
    (r"항소심도 ((?:\d{4}년 (?:\d{1,2}월 )?)?)항소를 (?:모두 )?기각했습니다", r"항소심도 \1같은 결론을 유지하였습니다"),
    (r"원고들의 청구를 모두 기각하고 원고 회사의 항소를 기각하였으며", "원고들의 청구를 모두 받아들이지 않았고, 원고 회사의 항소는 이유 없다고 보았으며"),
    (r"재량권 일탈·남용 주장도 받아들이지 않아 원고의 청구를 모두 기각하였고", "재량권 일탈·남용 주장도 배척하여 원고의 청구를 모두 받아들이지 않았고"),
    (r"집행정지 신청은 기각되었고 본안에서도 청구가 모두 기각되었습니다", "집행정지 신청은 받아들여지지 않았고, 본안에서도 처분이 모두 적법하다고 판단되었습니다"),
    (r"원고들의 청구를 모두 기각하였으며, 원고들의 항소도 모두 기각하였습니다", "원고들의 청구를 모두 받아들이지 않았으며, 원고들의 항소도 이유 없다고 보았습니다"),
    (r"원고의 항소를 기각하였고, 청구를 기각한 제1심 판결이 그대로 유지되었습니다", "원고의 항소를 받아들이지 않아, 제1심 판결의 결론이 그대로 유지되었습니다"),
    (r"원고의 항소를 기각하여, 청구를 기각한 제1심 판결을 유지하였습니다", "원고의 항소를 받아들이지 않고 제1심 판결의 결론을 유지하였습니다"),
    # 심리불속행
    (r"심리불속행으로 상고를 (?:모두 )?기각하여", "심리불속행으로 상고심을 마무리하여"),
    (r"심리불속행으로 상고를 (?:모두 )?기각하였습니다", "심리불속행 판결로 상고심을 마무리하였습니다"),
    (r"심리불속행으로 상고를 (?:모두 )?기각하였고", "심리불속행 판결로 상고심을 마무리하였고"),
    (r"심리불속행으로 (?:모두 )?기각되어", "심리불속행으로 마무리되어"),
    (r"심리불속행으로 (?:모두 )?기각되었습니다", "심리불속행으로 마무리되었습니다"),
    (r"심리불속행 기각", "심리불속행 확정"),
    (r"본안 심리 없이 상고를 기각하는 심리불속행 판결", "본안 심리 없이 상고심을 마무리하는 심리불속행 판결"),
    (r"판결로 상고를 기각할 수 있도록", "판결로 상고심을 마무리할 수 있도록"),
    # 행정심판 재결
    (r"청구 기각 재결에 이어, 취소소송에서도 1심 청구 기각과 항소 기각을 거쳐 대법원에서 상고가 기각되어",
     "재결에 이어, 취소소송에서도 1심과 항소심을 거쳐 대법원까지"),
    (r"행정심판을 청구하였으나 기각 재결을 받았고", "행정심판을 청구하였으나 받아들여지지 않았고"),
    (r"행정심판 기각 재결과", "행정심판 재결과"),
    # 이의신청·청원 등 '기각 + 명사'
    (r"이의신청 기각 통지", "이의신청 결과 통지"),
    (r"이의신청 기각 통보", "이의신청 결과 통보"),
    (r"이의신청 기각결정", "이의결정"),
    (r"그 기각 통지를", "그 결과 통지를"),
    (r"그 기각결정은", "그 이의결정은"),
    (r"수형자 이송청원 기각처분 취소소송", "수형자 이송청원 불허 결정 취소소송"),
    (r"청원 기각 회신", "청원 불허 회신"),
    (r"이송청원에 대한 기각결정", "이송청원에 대한 불허 결정"),
    (r"이 사건 기각결정", "이 사건 불허 결정"),
    (r"이 기각결정의 취소", "이 불허 결정의 취소"),
    (r"기각 회신", "불허 회신"),
    # 상대방 주장·요청
    (r"기각되어야 한다고", "받아들여져서는 안 된다고"),
    (r"신청의 기각을 구하였습니다", "신청이 받아들여져서는 안 된다고 주장하였습니다"),
    # 그 밖의 명사형
    (r"각 기각하였습니다", "각각 받아들이지 않았습니다"),
    (r"청구 기각과 항소 기각", "1심과 항소심"),
]

# (나) 일반 동사형
VERB = [
    (r"기각하였습니다", "받아들이지 않았습니다"),
    (r"기각했습니다", "받아들이지 않았습니다"),
    (r"기각하였고", "받아들이지 않았고"),
    (r"기각했고", "받아들이지 않았고"),
    (r"기각하였으며", "받아들이지 않았으며"),
    (r"기각하였으나", "받아들이지 않았으나"),
    (r"기각하였는데", "받아들이지 않았는데"),
    (r"기각하였다", "받아들이지 않았다"),
    (r"기각하였음", "받아들이지 않았음"),
    (r"기각하고", "받아들이지 않고"),
    (r"기각하며", "받아들이지 않으며"),
    (r"기각하면서", "받아들이지 않으면서"),
    (r"기각하여", "받아들이지 않아"),
    (r"기각한다", "받아들이지 않는다"),
    (r"기각한", "받아들이지 않은"),
    (r"기각하는", "받아들이지 않는"),
    (r"기각할", "받아들이지 않을"),
    (r"기각하기", "받아들이지 않기"),
    (r"기각되었습니다", "받아들여지지 않았습니다"),
    (r"기각됐습니다", "받아들여지지 않았습니다"),
    (r"기각되었고", "받아들여지지 않았고"),
    (r"기각되었으며", "받아들여지지 않았으며"),
    (r"기각되었으나", "받아들여지지 않았으나"),
    (r"기각되었는데", "받아들여지지 않았는데"),
    (r"기각되었다", "받아들여지지 않았다"),
    (r"기각되었음", "받아들여지지 않았음"),
    (r"기각되어", "받아들여지지 않아"),
    (r"기각되고", "받아들여지지 않고"),
    (r"기각되면서", "받아들여지지 않으면서"),
    (r"기각되면", "받아들여지지 않으면"),
    (r"기각되자", "받아들여지지 않자"),
    (r"기각하자", "받아들이지 않자"),
    (r"기각된다", "받아들여지지 않는다"),
    (r"기각된", "받아들여지지 않은"),
    (r"기각되는", "받아들여지지 않는"),
    (r"기각됩니다", "받아들여지지 않습니다"),
    (r"기각될", "받아들여지지 않을"),
    (r"기각됨", "받아들여지지 않음"),
]


def fix_text(s):
    if not s or "기각" not in s:
        return s
    for pat, rep in SPECIAL:
        s = re.sub(pat, rep, s)
    for pat, rep in VERB:
        s = re.sub(pat, rep, s)
    return s


# (다) 키워드
KEYWORD_MAP = {
    "항소 기각": "항소심 유지", "항소기각": "항소심 유지",
    "상고 기각": "대법원 확정", "상고기각": "대법원 확정",
    "심리불속행 기각": "심리불속행 확정",
    "집행정지 기각": "집행정지 불허", "기각 결정": "집행정지 불허",
    "행정심판 기각": "행정심판 처분 유지",
    "청원 기각": "청원 불허",
    "이의신청 기각 통지 처분성": "이의신청 결과 통지 처분성",
    "이의신청 기각 통지": "이의신청 결과 통지",
    "이의신청 기각": "이의신청 불수용",
}


def fix_keyword(k, cat, title=""):
    if "기각" not in k:
        return k
    if k in KEYWORD_MAP:
        return KEYWORD_MAP[k]
    if k in ("기각", "청구 기각", "청구기각"):
        # 처분을 다툰 행정사건이면 '처분 적법', 돈을 구한 사건이면 '청구 배척', 국가배상은 '배상책임 불인정'
        if cat == "state" or re.search(r"손해배상|국가배상", title):
            return "배상책임 불인정"
        if cat in ADMIN_CATS and not re.search(r"부존재확인|청구소송|부당이득|반환", title):
            return "처분 적법"
        return "청구 배척"
    return fix_text(k)


def dedupe(seq):
    out = []
    for x in seq:
        if x not in out:
            out.append(x)
    return out


# ---------- 적용 ----------


def is_agency(c):
    return (c.get("party") or "") in ("", "보조참가") and c.get("cat") != "criminal"


def fix_case(c, log):
    """사례 항목(index.html 데이터·detail_inputs/cases.json)의 result·title·summary."""
    changed = False
    new = fix_result(c.get("result"))
    if new != (c.get("result") or ""):
        log.append((c["id"], "result", c.get("result"), new)); c["result"] = new; changed = True
    if is_agency(c):
        for f in ("title", "summary"):
            if c.get(f) and "기각" in c[f]:
                new = fix_text(c[f])
                if new != c[f]:
                    log.append((c["id"], f, c[f], new)); c[f] = new; changed = True
    return changed


def fix_detail(cid, d, cat, log, title=""):
    """상세 소개(cases-detail.json·work/details/*.json)의 본문·키워드. quotes 는 그대로."""
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
        nk = dedupe([fix_keyword(k, cat, title) for k in d["keywords"]])
        if nk != d["keywords"]:
            log.append((cid, "keywords", " | ".join(d["keywords"]), " | ".join(nk))); d["keywords"] = nk; changed = True
    for q in d.get("quotes") or []:
        if q.get("from") and "기각" in q["from"]:
            nf = fix_text(q["from"])
            if nf != q["from"]:
                log.append((cid, "quotes.from", q["from"], nf)); q["from"] = nf; changed = True
    if d.get("result"):  # work/details 에 결과가 들어 있을 때
        nr = fix_result(d["result"])
        if nr != d["result"]:
            log.append((cid, "result", d["result"], nr)); d["result"] = nr; changed = True
    return changed


def remaining(cases, details):
    """판결문 원문 인용을 뺀 나머지에 남은 '기각'."""
    out = []
    for c in cases:
        if not is_agency(c):
            continue
        for f in ("title", "summary"):
            if "기각" in (c.get(f) or ""):
                out.append((c["id"], f, c[f]))
        d = details.get(c["id"]) or {}
        for f in TEXT_FIELDS + ("keywords", "laws"):
            v = d.get(f)
            if not v:
                continue
            for p in (v if isinstance(v, list) else [v]):
                if isinstance(p, str) and "기각" in p:
                    out.append((c["id"], f, p))
    return out


def main():
    site = sys.argv[1] if len(sys.argv) > 1 else "."
    dry = "--dry-run" in sys.argv
    check = "--check" in sys.argv
    ip = os.path.join(site, "index.html")
    idoc = S.read(ip)
    cases, _ = S.load_json_block(idoc, "cases-data")
    cat_of = {c["id"]: c["cat"] for c in cases}
    title_of = {c["id"]: c["title"] for c in cases}
    agency = {c["id"] for c in cases if is_agency(c)}
    dp = os.path.join(site, "cases-detail.json")
    details = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else {}

    if check:
        rem = remaining(cases, details)
        for cid, f, p in rem:
            print("%s [%s] %s" % (cid, f, p))
        print("남은 곳: %d" % len(rem))
        quoted = sum(1 for c in cases if c["id"] in agency and any("기각" in q.get("text", "") for q in (details.get(c["id"]) or {}).get("quotes", [])))
        print("판결문 원문 인용에 '기각'이 든 사례(그대로 둠): %d건" % quoted)
        return

    log = []
    n_case = sum(1 for c in cases if fix_case(c, log))
    n_det = sum(1 for cid, d in details.items() if cid in agency and fix_detail(cid, d, cat_of.get(cid), log, title_of.get(cid, "")))

    # work/details/*.json 과 detail_inputs/cases.json 도 같게
    extra = []
    for path in sorted(glob.glob(os.path.join(site, "work", "details", "*.json"))):
        data = json.load(open(path, encoding="utf-8"))
        ch = False
        for cid, d in data.items():
            if cid in agency and fix_detail(cid, d, cat_of.get(cid), extra, title_of.get(cid, "")):
                ch = True
            elif cid in cat_of and d.get("result") and fix_result(d["result"]) != d["result"]:
                d["result"] = fix_result(d["result"]); ch = True
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
    print("사례 %d건·상세 %d건 바뀜 (대리 기관 사례 %d건 기준), 작업용 파일 항목 %d곳" % (n_case, n_det, len(agency), len(extra)))
    if dry:
        print("(--dry-run: 파일은 바꾸지 않았습니다)")
        return
    S.write(ip, S.replace_json_block(idoc, "cases-data", cases))
    json.dump(details, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    rem = remaining(cases, details)
    print("남은 '기각'(원문 인용 제외): %d곳" % len(rem))
    for cid, f, p in rem:
        print("  ", cid, f, p)


if __name__ == "__main__":
    main()
