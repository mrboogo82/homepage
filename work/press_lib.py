#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
언론보도 데이터(press.json)를 읽는 공용 함수 (2026. 10. 22.).

press.json 의 items 항목:
  id · date(YYYY-MM-DD) · outlet(언론사) · title(기사 제목 그대로) · url ·
  kind: case(수행 사건 보도) / activity(토론회·위원회·강의 등 활동 보도) / mention(인사·합격자 명단 등 이름만 실린 기사) ·
  cases: 관련 사례 id 목록(cases-data.js) · home: 홈 '언론보도' 절에 보일지 · note: 한 줄 설명 · quote: 기사에 실린 본인 발언

ssr_cases.py(카드 표시·llms-full.txt), build_cases.py(사례 페이지의 '언론보도' 칸), build_press.py(홈 절)가 함께 쓴다.
"""
import json
import os

PRESS_FILE = "press.json"
KIND_NAMES = {"case": "수행 사건 보도", "activity": "토론회 · 위원회 · 강의", "mention": "그 밖에 이름이 실린 기사"}


def load_press(site):
    """press.json 의 items(목록). 없으면 빈 목록."""
    p = os.path.join(site, PRESS_FILE)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    items = data.get("items") if isinstance(data, dict) else data
    out = []
    seen = set()
    for it in items or []:
        if not it or not it.get("url") or not it.get("title"):
            continue
        if it.get("id") in seen:
            raise SystemExit("press.json 에 같은 id 가 둘 있습니다: %s" % it.get("id"))
        seen.add(it.get("id"))
        out.append(it)
    return out


def press_by_case(items):
    """{사례 id: [기사, ...]} — 사례별로 날짜 내림차순."""
    by = {}
    for it in items:
        for cid in it.get("cases") or []:
            by.setdefault(cid, []).append(it)
    for cid in by:
        by[cid].sort(key=lambda x: x.get("date") or "", reverse=True)
    return by


def kdate(iso):
    """'2026-01-03' → '2026. 1. 3.' (홈페이지의 날짜 표기)."""
    try:
        y, m, d = iso.split("-")
        return "%d. %d. %d." % (int(y), int(m), int(d))
    except Exception:
        return iso or ""


def check_press(items, case_ids):
    """사례 id 가 데이터에 없는 기사를 알린다."""
    bad = []
    for it in items:
        for cid in it.get("cases") or []:
            if cid not in case_ids:
                bad.append((it.get("id"), cid))
    if bad:
        raise SystemExit("press.json 의 사례 id 가 데이터에 없습니다: %s" % bad)
