#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
사례를 사례 데이터 파일 cases-data.js(2026. 10. 23. index.html의 #cases-data 블록에서 분리)에서 지운다. 그 사례만 쓰던 판결문 이미지(cases/*.jpg)와
작업용 목록(work/detail_inputs/cases.json·batches.json, work/insta/case_numbers.json)의 항목도 함께 치운다.
그 뒤 반드시
    python3 work/ssr_cases.py .  →  python3 work/build_cases.py .
을 차례로 돌린다(개별 페이지·사이트맵·llms는 build_cases.py가 지운 사례에 맞춰 다시 만든다).

사용법:
    python3 work/remove_cases.py . d-2012gaso10317 d-2012gaso13781 ...   # id로
    python3 work/remove_cases.py . --title 임금 --title 퇴직금            # 제목에 그 말이 든 사례 모두
    python3 work/remove_cases.py . --title 임금 --dry-run                # 무엇이 지워질지 보기만
옵션: --keep-images  이미지 파일은 남겨 둔다(기본은 삭제; 지워진 파일도 git 이력에는 남는다).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssr_cases as S  # noqa: E402


def load(p):
    return json.load(open(p, encoding="utf-8"))


def save(p, data, indent=1):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
        f.write("\n")


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    keep_images = "--keep-images" in args
    titles, ids, site = [], [], None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--title":
            titles.append(args[i + 1]); i += 2; continue
        if a.startswith("--"):
            i += 1; continue
        if site is None:
            site = a
        else:
            ids.append(a)
        i += 1
    if site is None or (not ids and not titles):
        raise SystemExit(__doc__)

    cases = S.load_cases(site)
    want = set(ids)
    gone = [c for c in cases if c["id"] in want or any(t in c["title"] for t in titles)]
    missing = want - {c["id"] for c in gone}
    if missing:
        raise SystemExit("모르는 사례 id: %s" % sorted(missing))
    if not gone:
        raise SystemExit("지울 사례가 없습니다")
    gone_ids = {c["id"] for c in gone}
    keep = [c for c in cases if c["id"] not in gone_ids]

    # 남는 사례가 쓰지 않는 이미지만 지운다
    used = {im["src"] for c in keep for im in S.images_of(c)}
    orphan = sorted({im["src"] for c in gone for im in S.images_of(c)} - used)

    for c in gone:
        print("- %s | %s | %s | %s" % (c["id"], c.get("date", ""), c["title"], c.get("court", "")))
    print("지울 사례 %d건 → 남는 사례 %d건, 더는 쓰지 않는 이미지 %d장%s" % (len(gone), len(keep), len(orphan), " (보기만)" if dry else ""))
    if dry:
        return

    S.save_cases(site, keep)
    if not keep_images:
        for src in orphan:
            p = os.path.join(site, src)
            if os.path.exists(p):
                os.remove(p)

    # 상세 소개 작성용 목록과 인스타그램 대조표에서도 뺀다
    p = os.path.join(site, "work", "detail_inputs", "cases.json")
    if os.path.exists(p):
        save(p, [c for c in load(p) if c["id"] not in gone_ids])
    p = os.path.join(site, "work", "detail_inputs", "batches.json")
    if os.path.exists(p):
        batches = []
        for b in load(p):
            b["ids"] = [x for x in b["ids"] if x not in gone_ids]
            if b["ids"]:
                batches.append(b)
        save(p, batches)
    p = os.path.join(site, "work", "insta", "case_numbers.json")
    if os.path.exists(p):
        with open(p, "w", encoding="utf-8") as f:   # 원래 형식(한 줄)대로
            json.dump([row for row in load(p) if row[0] not in gone_ids], f, ensure_ascii=False)
    p = os.path.join(site, "cases-detail.json")
    if os.path.exists(p):
        d = load(p)
        if any(k in d for k in gone_ids):
            save(p, {k: v for k, v in d.items() if k not in gone_ids})
    print("cases-data.js·작업용 목록 갱신%s (ssr_cases.py와 build_cases.py를 이어서 돌릴 것)" % ("" if keep_images else ", 이미지 %d장 삭제" % len(orphan)))


if __name__ == "__main__":
    main()
