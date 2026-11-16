#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수행사례 설명의 구체적인 금액을 어림 금액으로 바꾼다 (2026. 11. 15. 본인 지시:
"금액이 너무 구체적이면 사건의 내용과 당사자가 특정될 여지가 있다. '1억 여 원'과 같이 대략적인 금액으로. 다른 건들도 마찬가지").

사용법 (저장소 최상위에서):
    python3 work/approx_amounts.py .            # 적용 (그 뒤 ssr_cases.py → build_pages.py → build_cases.py)
    python3 work/approx_amounts.py . --dry-run  # 바뀔 곳만 보여 줌
    python3 work/approx_amounts.py . --check    # 아직 구체적인 금액이 남았는지 보고

규칙:
  - 맨 앞 한 단위만 남긴다: 86,988,977원 → 8천만여 원, 7억 1,100만 원 → 7억여 원, 555만 원 → 500만여 원, 207,896원 → 20만여 원.
    이미 딱 떨어지는 금액(5억 원, 3,000만 원, 80만 원)과 1만 원 미만(1원 입찰 등)은 그대로 둔다 — 법령·기준의 금액도 대개 여기에 든다.
  - 대상: cases-data.js 의 title·summary·kw, cases-detail.json 의 overview·claims·argument·issues·holding·meaning·keywords 와
    quotes(판결문 인용 — 이름을 역할어로 바꾼 것과 같은 취지로 금액도 어림으로 바꾼다), work/details/*.json(summary_new 포함),
    work/detail_inputs/cases.json. 새 사례를 더한 뒤 merge_details.py 를 돌렸으면 이 스크립트를 다시 돌린다.
  - 어림하면 두 금액이 같은 말이 되어 뜻이 흐려지는 문장은 PRE 에 적어 문장째 고친다. KEEP 의 문맥은 그대로 둔다.
  - 판결문 이미지의 주문에 보이는 금액은 이 스크립트의 대상이 아니다.
"""
import glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ssr_cases as S  # noqa: E402

D = r'\d[\d,]*(?:\.\d+)?'
SEG = r'(?:%s\s*천\s*)?(?:%s\s*백\s*)?(?:%s\s*십\s*)?(?:%s)?' % (D, D, D, D)      # 만 단위 안의 수: 4천4백, 2,282, 5천, 808
AMT = re.compile(r'(약\s*)?((?:%s\s*조\s*)?(?:%s\s*억\s*)?(?:%s\s*만\s*)?(?:%s)?)\s*(여\s*)?원(?!고|심|칙|처분|판결)' % (D, SEG, SEG, SEG))
KEEP = ['교습비(월']   # 그대로 두는 문맥(금액 앞뒤 글에 이 낱말이 있으면 바꾸지 않음 — 신고 교습비 범위처럼 어림하면 뜻이 흐려지는 곳)
# 어림하면 두 금액이 같은 말이 되어 뜻이 흐려지는 문장은 먼저 문장째 고친다(옛 글 → 새 글).
PRE = [
    ('사업비 정산금 반환채무 157,570,731원 가운데 150,000,000원이 존재하지 않는다는', '사업비 정산금 반환채무 1억여 원 가운데 대부분이 존재하지 않는다는'),
    ('인건비 부정사용 금액은 총 2,162,073원인데도 전문기관이 2,979,480원으로 잘못 산정하였으므로', '인건비 부정사용 금액은 총 200만여 원인데도 전문기관이 그보다 많은 금액으로 잘못 산정하였으므로'),
    ('전문기관이 부정사용 금액을 2,979,480원이 아닌 2,162,073원으로 산정하였고', '전문기관이 부정사용 금액을 원고들이 지적한 금액이 아니라 그보다 적은 200만여 원으로 산정하였고'),
    ('결국 취득세 774,862,570원 중 740,375,520원을 초과하는 부분, 지방교육세 중 38,703,790원을 초과하는 부분, 농어촌특별세 중 48,379,750원을 초과하는 부분만 취소되고', '결국 취득세·지방교육세·농어촌특별세 부과처분 가운데 그 설치비용에 대응하는 일부만 취소되고'),
    ('환수금액이 1차 통보의 159,497,028원에서 159,497,472원으로 늘어났으므로', '환수금액이 1차 통보 때보다 조금 늘어났으므로'),
    ('1,847만 원[(510만 원+1,700만 원)×70%+300만 원]으로', '1,847만 원으로'),
    ('법원 감정 결과(1㎡당 175,000원)가 수용재결 금액(1㎡당 177,500원)에 미치지', '법원 감정 결과가 수용재결 금액에 미치지'),
    ('약 3억 3,400만 원(정산금 제외 시 약 3억 3,200만 원)의', '약 3억 3,400만 원의'),
    ('불인정금액을 2,818만 원으로 줄이고 그 가운데 2,497만 원을 정산금으로', '불인정금액을 2천만여 원으로 줄이고 그 대부분을 정산금으로'),
    ('1㎡당 207,896원으로 원고들의 청구 단가(297,269원)의 약 7할만', '1㎡당 20만여 원으로 원고들의 청구 단가의 약 7할만'),
    ('(피고별 11,966,000원과 12,000,000원)', '(피고별 약 1,200만 원)'),
    ('각 8,376,200원과 8,400,000원 및', '각 800만여 원 및'),
    ('약 1,300만~4,090만 원', '1천만여 원~4천만여 원'),
    ('약 2,290만~3,600만 원', '2천만여 원~3천만여 원'),
    ('약 2,100만~4,400만 원', '2천만여 원~4천만여 원'),
    ('환수금 차이 444원은', '환수금의 근소한 차이는'),
    ('환수금이 444원 늘어난', '환수금이 조금 늘어난'),
    ('환수금액이 444원 늘어난', '환수금액이 조금 늘어난'),
    ('444원', '수백 원'),
]
FIELDS = ['overview', 'claims', 'argument', 'issues', 'holding', 'meaning', 'keywords']


def seg(t):
    """'4천4백' · '2,282' · '5천' → 수"""
    n, rest = 0.0, t
    for u, v in (('천', 1000), ('백', 100), ('십', 10)):
        m = re.match(r'\s*(%s)\s*%s' % (D, u), rest)
        if m:
            n += float(m.group(1).replace(',', '')) * v
            rest = rest[m.end():]
    m = re.match(r'\s*(%s)' % D, rest)
    if m:
        n += float(m.group(1).replace(',', ''))
    return n


def value(body):
    n, rest = 0.0, body
    for u, v in (('조', 10**12), ('억', 10**8), ('만', 10**4)):
        i = rest.find(u)
        if i >= 0:
            n += seg(rest[:i]) * v
            rest = rest[i + 1:]
    n += seg(rest)
    return int(round(n))


def approx(n):
    """맨 앞 한 단위만 남긴다. 이미 딱 떨어지는 금액(5억 원·3,000만 원·80만 원)과 1만 원 미만은 None(그대로 둠)."""
    for base, fmt in ((10**8, '{:,}억'), (10**7, '{}천만'), (10**6, '{}00만'), (10**5, '{}0만'), (10**4, '{}만')):
        if n >= base:
            q = n // base
            return None if n % base == 0 else fmt.format(q) + '여 원'
    return None


def plain(n):
    """딱 떨어지는 금액을 숫자로만 적은 것(1,000,000원)은 단위로 고쳐 적는다(100만 원) — 인용문 밖에서만."""
    out = ''
    for base, u in ((10**8, '억'), (10**4, '만')):
        if n >= base:
            out += ('{:,}'.format(n // base) + u + ' ')
            n %= base
    return (out + ('{:,}'.format(n) if n else '')).strip() + ' 원' if not n else None


def fix(text, log=None, where=''):
    for old, new in PRE:
        if old in text:
            if log is not None:
                log.append((where, old, '(문장)', new))
            text = text.replace(old, new)

    def rep(m):
        body = m.group(2)
        if not re.search(r'\d', body):
            return m.group(0)
        ctx = text[max(0, m.start() - 30):m.end() + 30]
        if any(k in ctx for k in KEEP):
            return m.group(0)
        new = approx(value(body))
        if new is None:
            n = value(body)
            if n >= 10**4 and re.fullmatch(r'[\d,]+', body.strip()) and not where.endswith('quotes') and plain(n):
                new = plain(n)
            else:
                return m.group(0)
        if log is not None:
            log.append((where, ctx.replace('\n', ' '), m.group(0), new))
        return new
    return AMT.sub(rep, text)


def walk(obj, log, where):
    """문자열을 재귀로 바꾼다(지정 필드만)."""
    changed = False
    for k in list(obj.keys()):
        v = obj[k]
        if k in FIELDS or k in ('summary_new', 'summary', 'title', 'kw'):
            if isinstance(v, str):
                nv = fix(v, log, where + '.' + k)
                changed |= nv != v
                obj[k] = nv
            elif isinstance(v, list):
                nl = [fix(t, log, where + '.' + k) if isinstance(t, str) else t for t in v]
                changed |= nl != v
                obj[k] = nl
        elif k == 'quotes':
            for q in v:
                nv = fix(q['text'], log, where + '.quotes')
                changed |= nv != q['text']
                q['text'] = nv
    return changed


def main():
    site = sys.argv[1]
    dry = '--dry-run' in sys.argv or '--check' in sys.argv
    log = []
    cases = S.load_cases(site)
    ch = False
    for c in cases:
        ch |= walk(c, log, c['id'])
    if ch and not dry:
        S.save_cases(site, cases)
    files = [os.path.join(site, 'cases-detail.json')] + sorted(glob.glob(os.path.join(site, 'work/details/*.json')))
    for f in files:
        d = json.load(open(f, encoding='utf-8'))
        ch = False
        for i, v in d.items():
            if isinstance(v, dict):
                ch |= walk(v, log if f.endswith('cases-detail.json') else [], i)
        if ch and not dry:
            json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    f = os.path.join(site, 'work/detail_inputs/cases.json')
    if os.path.exists(f):
        d = json.load(open(f, encoding='utf-8'))
        items = d if isinstance(d, list) else list(d.values())
        ch = False
        for v in items:
            if isinstance(v, dict):
                ch |= walk(v, [], v.get('id', ''))
        if ch and not dry:
            json.dump(d, open(f, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for w, ctx, old, new in log:
        print('%s | %s → %s | …%s…' % (w, old, new, ctx))
    print('%s %d곳' % ('바뀔 곳' if dry else '바꾼 곳', len(log)))
    if '--check' in sys.argv and log:
        sys.exit(1)


if __name__ == '__main__':
    main()
