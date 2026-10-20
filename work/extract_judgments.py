#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
판결문 PDF → 글(txt). 전자문서는 pdftotext, 스캔본은 tesseract(kor) OCR.
당사자란에서 모은 이름(사람·회사)은 본문에서 역할어로 바꿔 둔다(완전하지 않으므로 글을 쓸 때 다시 가린다).

사용법:
    python3 work/extract_judgments.py <pdf 또는 폴더> [...]  → work/judgments/<법원>-<사건번호>.txt
"""
import os
import re
import subprocess
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "judgments")
CASENO = re.compile(r"(20\d{2}(?:구합|구단|누|두|가합|가단|가소|나|다|고합|고단|고정|노|도|아|루|무|카단|카합|자|카확|카기|재구합|재나|재다|추|초기|즈기|드단|느단|호파|카명|라|마)\d+)")
COURT = re.compile(r"(대법원|[가-힣]+(?:고등|지방|행정|가정)법원(?:\s*[가-힣]+지원)?)")
LABELS = ["원고", "피고", "신청인", "피신청인", "채권자", "채무자", "청구인", "피청구인", "항고인", "상대방", "참가인", "피고보조참가인", "원고보조참가인",
          "선정당사자", "주위적 피고", "예비적 피고", "항소인", "피항소인", "상고인", "피상고인", "피의자", "피고인"]


def pdf_text(path):
    try:
        t = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", path, "-"], capture_output=True, text=True, timeout=120).stdout
    except Exception:
        t = ""
    if len(re.sub(r"\s", "", t)) > 300:
        return t, "text"
    # 스캔본: OCR
    import pypdfium2 as pdfium
    import pytesseract
    pdf = pdfium.PdfDocument(path)
    pages = []
    for i in range(len(pdf)):
        img = pdf[i].render(scale=200 / 72).to_pil()
        pages.append(pytesseract.image_to_string(img, lang="kor+eng", config="--psm 4"))
    return "\n\f".join(pages), "ocr"


LABEL_RX = re.compile(r"^(?:\d+\.\s*)?(" + "|".join(r"\s*".join(lab) for lab in LABELS) + r")\s*[:：]?\s*(.*)$")
COMPANY_RX = re.compile(r"((?:주식회사|유한회사|유한책임회사|농업회사법인|사회복지법인|학교법인|재단법인|사단법인|의료법인|협동조합)\s*[가-힣A-Za-z0-9&·\.\-]+|[가-힣A-Za-z][가-힣A-Za-z0-9&·\.\-]*\s*(?:주식회사|유한회사|\(주\)|㈜|산학협력단|협동조합|새마을금고|학교|대학교|병원))")


def header_names(text):
    """당사자란(사건 ~ 변론종결/판결선고/주문 사이)에서 이름·회사명을 모은다."""
    head = text[:6000]
    m = re.search(r"(변\s*론\s*종\s*결|판\s*결\s*선\s*고|주\s*문|신\s*청\s*취\s*지|결\s*정\s*일)", head)
    block = head[: m.start()] if m else head
    names = set()
    for line in block.splitlines():
        s2 = re.sub(r"\s+", " ", line.strip())
        if not s2 or s2.startswith("개인정보유출주의"):
            continue
        s2 = re.sub(r"^\d+\.\s*", "", s2)
        val = None
        lm = LABEL_RX.match(s2)
        if lm and not CASENO.search(s2) and "법원" not in s2 and "사 건" not in s2:
            val = lm.group(2).strip()
        else:
            val = s2
        val = re.sub(r"^\d+\.\s*", "", val)
        for cm in COMPANY_RX.finditer(val):
            names.add(cm.group(1).strip())
        for key in ["대표자", "대표이사", "소송수행자", "담당변호사", "소송대리인", "법률상 대표자", "이사장", "원장", "총장", "학교장", "지배인", "청산인", "관리인"]:
            if key in val:
                after = val.split(key, 1)[1].strip(" :")
                for tok in re.split(r"[,·\s]", after):
                    tok = tok.strip()
                    if re.fullmatch(r"[가-힣]{2,4}", tok) and tok not in ("부효준", "변호사", "법무법인", "정부법무공단", "담당변호사", "유한", "금성"):
                        names.add(tok)
        if lm:
            v = re.sub(r"\(.*?\)", "", lm.group(2)).strip()
            for tok in re.split(r"[,·\s]+", v):
                if re.fullmatch(r"[가-힣]{2,4}", tok) and tok not in ("부효준", "대한민국", "변호사", "법무법인", "정부법무공단", "외"):
                    names.add(tok)
        # 당사자란에 홀로 적힌 사람 이름
        if re.fullmatch(r"[가-힣]{2,4}", s2) and s2 not in ("부효준", "대한민국", "변호사", "법무법인", "주문", "판결", "결정", "이유", "사건", "원고", "피고"):
            names.add(s2)
    names = {n for n in names if n and len(n) >= 2 and n not in ("부효준", "대한민국")}
    return sorted(names, key=len, reverse=True)


def anonymize(text, names):
    text = "\n".join(l for l in text.splitlines() if not l.strip().startswith("개인정보유출주의"))
    for i, n in enumerate(names):
        if re.fullmatch(r"[가-힣]{2,4}", n):
            text = text.replace(n, "○○○")
        else:
            text = text.replace(n, "[당사자%d]" % (i + 1))
    return text


KNOWN = {}
try:
    import json
    for _cid, _court, _no in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "insta", "case_numbers.json"), encoding="utf-8")):
        KNOWN.setdefault(_no, _court)
except Exception:
    pass


def main():
    os.makedirs(OUT, exist_ok=True)
    files = []
    for a in sys.argv[1:]:
        if os.path.isdir(a):
            for root, _, fs in os.walk(a):
                files += [os.path.join(root, f) for f in fs if f.lower().endswith(".pdf")]
        elif a.lower().endswith(".pdf"):
            files.append(a)
    for f in files:
        text, how = pdf_text(f)
        head = text[:3000]
        no = CASENO.search(head)
        if not no:
            # 파일 이름에서라도 찾는다
            no = CASENO.search(os.path.basename(f).replace(" ", ""))
        if not no:
            print("사건번호를 찾지 못함:", f)
            continue
        number = no.group(1)
        court = KNOWN.get(number)
        if not court:
            m = COURT.search(re.sub(r"[ \t]+", "", head[:600]))
            court = m.group(1) if m else "법원"
        key = court + "-" + number
        names = header_names(text)
        out = os.path.join(OUT, key + ".txt")
        with open(out, "w", encoding="utf-8") as w:
            w.write("# %s (%s) — 원본 파일 이름은 적지 않음\n" % (key, how))
            w.write(anonymize(text, names))
        print(key, how, "names masked:", len(names))


if __name__ == "__main__":
    main()
