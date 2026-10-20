#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
상세 소개(JSON) 검사기: 구조·길이·금지어(기관명·비실명 기호·광고 표현)를 훑는다.
    python3 work/check_details.py work/details/rnd-01.json [...]
"""
import json
import re
import sys

AGENCIES = [
    "중소기업기술정보진흥원", "기정원", "중소벤처기업부", "중기부", "과학기술정보통신부", "과기정통부", "문화체육관광부", "문체부",
    "보건복지부", "교육부", "행정안전부", "농림축산식품부", "기상청", "서울특별시", "서울시", "경기도", "안성시", "과천시", "강릉시", "종로구",
    "금강유역환경청", "한국도로공사", "도로공사", "한국수자원공사", "수자원공사", "주택도시보증공사", "서울주택도시공사", "에스에이치", "SH공사",
    "한국환경산업기술원", "환경산업기술원", "서울시설공단", "사립학교교직원연금공단", "사학연금", "한국고용정보원", "에스알", "코레일", "강원랜드",
    "국립중앙과학관", "조달청", "인사혁신처", "법무부", "산업통상자원부", "국가정보원", "대검찰청", "인천광역시", "인천시", "울산광역시", "연천군",
    "스마트제조혁신추진단", "한국산업기술진흥원", "한국콘텐츠진흥원", "정보통신기획평가원", "군포산업진흥원", "한국기계전기전자시험연구원",
    "국립대학교", "서울시립대", "충남대", "전북대", "경북대", "부산대", "강원대", "한국해양대",
]
BAD_WORDS = ["전문 변호사", "전문변호사", "최고", "유일", "압도적", "국내 최다", "최다", "1위"]
PLACEHOLDER = re.compile(r"(?<![A-Za-z가-힣])(원고|피고|신청인|피신청인|참가인|주식회사|회사|대표자|대표이사|증인|선정자)\s?[A-Z]\b|\b[A-Z](?:장|회사|대학교|병원|공사|공단|시장|군수|구청장|기관장)\b|\b[A-Z]\s?(?:에게|은|는|이|가|을|를|의|과|와)\s")
NAME_HINT = re.compile(r"(변호사|판사|대표이사|대표자|연구책임자|과제책임자|증인|소송수행자)\s+[가-힣]{2,3}(?=[\s,.)]|$)")
SECTIONS = ["overview", "claims", "argument", "issues", "holding", "quotes", "meaning", "laws", "keywords"]


def texts_of(d):
    for k in ["overview", "claims", "argument", "issues", "holding", "meaning", "laws", "keywords"]:
        for x in d.get(k) or []:
            yield k, x
    for q in d.get("quotes") or []:
        yield "quotes", q.get("text", "")
        yield "quotes.from", q.get("from", "")
    if d.get("summary_new"):
        yield "summary_new", d["summary_new"]


def check(path):
    data = json.load(open(path, encoding="utf-8"))
    problems = []
    for cid, d in data.items():
        if not isinstance(d, dict):
            problems.append((cid, "항목이 객체가 아님")); continue
        n_over = sum(len(x) for x in d.get("overview") or [])
        n_hold = sum(len(x) for x in d.get("holding") or [])
        if n_over < 150:
            problems.append((cid, "overview 너무 짧음(%d자)" % n_over))
        if n_hold < 120:
            problems.append((cid, "holding 너무 짧음(%d자)" % n_hold))
        if not d.get("keywords") or len(d["keywords"]) < 4:
            problems.append((cid, "keywords 부족"))
        for q in d.get("quotes") or []:
            if len(q.get("text", "")) > 700:
                problems.append((cid, "인용문이 긺(%d자)" % len(q["text"])))
        for k, t in texts_of(d):
            if not isinstance(t, str):
                problems.append((cid, "%s: 문자열 아님" % k)); continue
            for a in AGENCIES:
                if a in t:
                    problems.append((cid, "%s: 기관명 '%s'" % (k, a)))
            for w in BAD_WORDS:
                if w in t:
                    problems.append((cid, "%s: 광고 표현 '%s'" % (k, w)))
            m = PLACEHOLDER.search(t)
            if m:
                problems.append((cid, "%s: 비실명 기호 '%s'" % (k, m.group(0))))
            m = NAME_HINT.search(t)
            if m:
                problems.append((cid, "%s: 이름 의심 '%s'" % (k, m.group(0))))
            if k != "quotes" and len(t) > 420 and k in ("overview", "holding", "meaning"):
                problems.append((cid, "%s: 문단이 긺(%d자) — 나눌 것" % (k, len(t))))
        for k in d:
            if k not in SECTIONS + ["claims_label", "argument_label", "instagram", "blog", "summary_new"]:
                problems.append((cid, "알 수 없는 항목 %s" % k))
    return data, problems


if __name__ == "__main__":
    total = 0
    for p in sys.argv[1:]:
        data, probs = check(p)
        print("%s: %d건" % (p, len(data)))
        for cid, msg in probs:
            print("  -", cid, msg)
        total += len(probs)
    sys.exit(1 if total else 0)
