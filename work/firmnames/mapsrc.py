#!/usr/bin/env python3
"""Map published image names (cases/<cat>-<year><type><no>.jpg) to original files on the user's computer
by case number found in the original file names. Writes map.json."""
import re, json, sys, os
from collections import defaultdict

ROMAN = {'guhap': '구합', 'nu': '누', 'gaso': '가소', 'gadan': '가단', 'na': '나', 'a': '아', 'du': '두',
         'gahap': '가합', 'gojeong': '고정', 'da': '다', 'gudan': '구단', 'kadan': '카단', 'ja': '자',
         'ru': '루', 'kahap': '카합', 'godan': '고단'}

lst = [l.rstrip('\n') for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
imgs = sorted(os.path.basename(p) for p in os.listdir('/home/claude/homepage/cases') if p.endswith('.jpg'))

CASE_RE = re.compile(r'(?<![0-9])((?:20|19)?[0-9]{2})\s*(구합|구단|누|두|아|가소|가단|가합|나|다|고정|고단|고합|카단|카합|자|루|무|노|드단|느단|즈기|차|재|비합|비단|카기|카확|카명|타채|카불|머|카담|과|로|초기|소|고약)\s*([0-9]{1,8})')

def norm_year(y):
    y = int(y)
    if y < 100:
        y += 2000 if y < 50 else 1900
    return str(y)

by_case = defaultdict(list)
for p in lst:
    name = os.path.basename(p)
    for m in CASE_RE.finditer(name):
        key = norm_year(m.group(1)) + m.group(2) + m.group(3)
        if p not in by_case[key]:
            by_case[key].append(p)

out = {}
unmapped = []
for im in imgs:
    m = re.match(r'^[a-z]+-(\d{4})([a-z]+)(\d+)\.jpg$', im)
    if not m:
        unmapped.append(im); continue
    key = m.group(1) + ROMAN[m.group(2)] + m.group(3)
    cands = by_case.get(key, [])
    out[im] = {'case': key, 'candidates': cands}
    if not cands:
        unmapped.append(im)

json.dump({'map': out, 'unmapped': unmapped}, open('map.json', 'w'), ensure_ascii=False, indent=1)
print('images', len(imgs), 'mapped', sum(1 for v in out.values() if v['candidates']), 'unmapped', len(unmapped))
for u in unmapped: print('  ', u)
