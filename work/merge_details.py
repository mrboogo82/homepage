#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
work/details/*.json (작성자별 배치)를 cases-detail.json 에 합치고, summary_new 가 있으면 index.html 의 사례 요지를 바꾼다.
    python3 work/merge_details.py .            # 합치기
그 뒤  python3 work/ssr_cases.py .  →  python3 work/build_cases.py .
"""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssr_cases as S  # noqa: E402
from check_details import check  # noqa: E402

KEEP = ["overview", "claims", "claims_label", "argument", "argument_label", "issues", "holding", "holding_label", "quotes", "meaning", "laws", "keywords", "instagram", "blog"]


def main():
    site = sys.argv[1] if len(sys.argv) > 1 else "."
    dp = os.path.join(site, "cases-detail.json")
    details = json.load(open(dp, encoding="utf-8")) if os.path.exists(dp) else {}
    ip = os.path.join(site, "index.html")
    idoc = S.read(ip)
    cases, _ = S.load_json_block(idoc, "cases-data")
    by_id = {c["id"]: c for c in cases}
    n_new = n_sum = 0
    for path in sorted(glob.glob(os.path.join(site, "work", "details", "*.json"))):
        data, probs = check(path)
        bad = [p for p in probs if "너무 짧음" not in p[1] and "문단이 긺" not in p[1]]
        if bad:
            print("%s: 검사에 걸려 합치지 않음:" % path)
            for cid, msg in bad:
                print("  -", cid, msg)
            continue
        for cid, d in data.items():
            if cid not in by_id:
                print("  ? 모르는 사례 id:", cid, "(%s)" % path)
                continue
            if d.get("summary_new") and len(d["summary_new"]) > 40:
                by_id[cid]["summary"] = d["summary_new"]
                n_sum += 1
            entry = {k: d[k] for k in KEEP if d.get(k)}
            details[cid] = entry
            n_new += 1
    # 사례 순서대로 정렬해 저장
    order = {c["id"]: i for i, c in enumerate(cases)}
    details = dict(sorted(details.items(), key=lambda kv: order.get(kv[0], 10**6)))
    json.dump(details, open(dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    S.write(ip, S.replace_json_block(idoc, "cases-data", cases))
    print("상세 소개 %d건 합침(요지 교체 %d건) → cases-detail.json %d건" % (n_new, n_sum, len(details)))


if __name__ == "__main__":
    main()
