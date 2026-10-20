#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""대상 판결문의 더할 면을 그려 내고(raw), 글자를 뽑아(text) 검토용으로 저장한다.
    python3 prep.py <base> <pdf> <pno...>   (pno: 1-based 면 번호)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import tools

ROOT = '/home/claude/jumun2'
base, pdf = sys.argv[1], sys.argv[2]
pnos = [int(x) for x in sys.argv[3:]]
os.makedirs(f'{ROOT}/raw', exist_ok=True)
os.makedirs(f'{ROOT}/text', exist_ok=True)
os.makedirs(f'{ROOT}/words', exist_ok=True)
for pno in pnos:
    img = tools.render(pdf, pno - 1)
    img.save(f'{ROOT}/raw/{base}-p{pno}.png')
    ws, how = tools.get_words(pdf, pno - 1, img)
    json.dump({'how': how, 'words': ws}, open(f'{ROOT}/words/{base}-p{pno}.json', 'w', encoding='utf-8'), ensure_ascii=False)
    txt, how2 = tools.page_text(pdf, pno - 1, img)
    open(f'{ROOT}/text/{base}-p{pno}.txt', 'w', encoding='utf-8').write(txt)
    print(base, pno, how, how2, len(ws), 'words', img.size)
