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


def header_names(text):
    """당사자란(사건 ~ 변론종결/판결선고/주문 사이)에서 이름·회사명을 모은다."""
    head = text[:4000]
    m = re.search(r"(변\s*론\s*종\s*결|판\s*결\s*선\s*고|주\s*문)", head)
    block = head[: m.start()] if m else head
    names = set()
    for line in block.splitlines():
        s = line.strip()
        if not s:
            continue
        s2 = re.sub(r"\s+", " ", s)
        # 라벨 뒤의 값
        for lab in LABELS:
            if s2.startswith(lab):
                val = s2[len(lab):].strip(" :.").strip()
                if val and not CASENO.search(val):
                    names.add(val.split("(")[0].strip())
        for key in ["대표자", "대표이사", "소송수행자", "담당변호사", "소송대리인", "법률상 대표자", "이사장", "원장", "총장", "학교장"]:
            if key in s2:
                after = s2.split(key, 1)[1].strip(" :")
                for tok in re.split(r"[,·\s]", after):
                    tok = tok.strip()
                    if re.fullmatch(r"[가-힣]{2,4}", tok) and tok not in ("부효준", "변호사", "법무법인", "정부법무공단", "담당변호사"):
                        names.add(tok)
    names = {n for n in names if n and len(n) >= 2 and n not in ("부효준", "대한민국")}
    # 기관 이름은 남긴다(홈페이지 방침과 별개로, 이름 가림은 사람·회사 우선)
    return sorted(names, key=len, reverse=True)


def anonymize(text, names):
    for i, n in enumerate(names):
        if re.fullmatch(r"[가-힣]{2,4}", n):
            text = text.replace(n, "○○○")
        else:
            text = text.replace(n, "[당사자%d]" % (i + 1))
    return text


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
        court = COURT.search(head)
        if not no:
            print("사건번호를 찾지 못함:", f)
            continue
        key = ((court.group(1).replace(" ", "") if court else "법원") + "-" + no.group(1))
        names = header_names(text)
        out = os.path.join(OUT, key + ".txt")
        with open(out, "w", encoding="utf-8") as w:
            w.write("# %s (%s) — 원본 파일 이름은 적지 않음\n" % (key, how))
            w.write(anonymize(text, names))
        print(key, how, "names masked:", len(names))


if __name__ == "__main__":
    main()
