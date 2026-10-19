#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
새 사례를 index.html의 #cases-data JSON에 더한다(이미 있는 id는 교체). 그 뒤 반드시
    python3 work/ssr_cases.py .  →  python3 work/build_cases.py .
을 차례로 돌린다.

사용법: python3 work/add_cases.py . new_cases.json
new_cases.json 은 사례 항목(id, cat, sort, date, title, court, party, result, summary, link, images)의 목록.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssr_cases as S  # noqa: E402

REQUIRED = ["id", "cat", "sort", "date", "title", "court", "result", "summary", "images"]


def main():
    site, path = sys.argv[1], sys.argv[2]
    new = json.load(open(path, encoding="utf-8"))
    ip = os.path.join(site, "index.html")
    doc = S.read(ip)
    cases, _ = S.load_json_block(doc, "cases-data")
    by_id = {c["id"]: i for i, c in enumerate(cases)}
    added = replaced = 0
    for c in new:
        for k in REQUIRED:
            if k not in c:
                raise SystemExit("항목 %s에 %s가 없습니다" % (c.get("id"), k))
        if c["cat"] not in S.CATS:
            raise SystemExit("분류키가 잘못되었습니다: %s (%s)" % (c["cat"], c["id"]))
        c.setdefault("party", "")
        c.setdefault("link", "")
        for im in c["images"]:
            im.setdefault("thumb", "")
            if not os.path.exists(os.path.join(site, im["src"])):
                raise SystemExit("판결문 이미지가 없습니다: %s" % im["src"])
        entry = {k: c[k] for k in ["id", "cat", "sort", "date", "title", "court", "party", "result", "summary", "link", "images"]}
        if c.get("kw"):
            entry["kw"] = c["kw"]   # 검색어(선택; 보통은 cases-detail.json의 keywords에서 ssr_cases.py가 채운다)
        if c["id"] in by_id:
            cases[by_id[c["id"]]] = entry
            replaced += 1
        else:
            cases.append(entry)
            added += 1
    S.write(ip, S.replace_json_block(doc, "cases-data", cases))
    print("추가 %d건, 교체 %d건 → 사례 %d건 (index.html 데이터 블록만 갱신; ssr_cases.py와 build_cases.py를 이어서 돌릴 것)" % (added, replaced, len(cases)))


if __name__ == "__main__":
    main()
