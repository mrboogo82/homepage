#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
아직 상세 소개가 없는 사례를 자료 유무에 따라 묶어 작성 배치를 만든다.
    python3 work/plan_batches.py .   → work/detail_inputs/plan.json, 요약 출력
자료 종류: local(판결 전문 txt 있음) / insta(인스타그램 글 확정) / lbox(엘박스만) / none(건너뜀)
"""
import json
import os
import sys
from collections import Counter, defaultdict

site = sys.argv[1] if len(sys.argv) > 1 else "."
sys.path.insert(0, os.path.join(site, "work"))
import ssr_cases as S  # noqa: E402

cases_in = json.load(open(os.path.join(site, "work", "detail_inputs", "cases.json"), encoding="utf-8"))
live = S.load_cases(site)
live_ids = {c["id"] for c in live}
dp = os.path.join(site, "cases-detail.json")
done = set(json.load(open(dp, encoding="utf-8")).keys()) if os.path.exists(dp) else set()
texts = os.listdir(os.path.join(site, "work", "judgments"))
by_no = defaultdict(list)
for t in texts:
    stem = t[:-4]
    if "-" in stem:
        by_no[stem.rsplit("-", 1)[1]].append(t)

plan = []
kinds = Counter()
for c in cases_in:
    if c["id"] not in live_ids or c["id"] in done:
        continue
    local = []
    for n in c.get("numbers", []):
        local += by_no.get(n["no"], [])
    insta = [x for x in c.get("insta", []) if not x.endswith("?")]
    insta_q = [x[:-1] for x in c.get("insta", []) if x.endswith("?")]
    lbox = [n for n in c.get("numbers", []) if n.get("lbox")]
    if local:
        kind = "local"
    elif insta:
        kind = "insta"
    elif lbox:
        kind = "lbox"
    else:
        kind = "none"
    kinds[kind] += 1
    plan.append({"id": c["id"], "cat": c["cat"], "kind": kind, "local": sorted(set(local)), "insta": insta, "insta_q": insta_q,
                 "lbox": [n["url"] for n in lbox], "title": c["title"]})

json.dump(plan, open(os.path.join(site, "work", "detail_inputs", "plan.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("남은 사례", len(plan), dict(kinds))
bycat = defaultdict(Counter)
for p in plan:
    bycat[p["cat"]][p["kind"]] += 1
for cat, cnt in sorted(bycat.items()):
    print(" ", cat, dict(cnt))
