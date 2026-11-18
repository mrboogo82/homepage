#!/usr/bin/env python3
"""Remove the site's own case numbers (and related lower/related-proceeding numbers) from text data.
Precedent citations (대법원·헌법재판소 판례 인용) and verbatim judgment quotes (quotes[].text) are kept.

Usage: strip_casenos.py SITE [--dry]
"""
import sys, os, re, json, glob, collections

site = sys.argv[1]
DRY = "--dry" in sys.argv
CODES = ("구합|구단|누|두|추|아|무|루|부|가합|가단|가소|나|다|라|마|머|자|카합|카단|카기|카담|카확|카정|차전|차|타채|타경|"
         "회합|회단|회확|하합|하단|개회|고합|고단|고정|고약|노|도|초기|초재|로|모|오|헌마|헌바|헌가|헌라|헌사|"
         "드합|드단|르|므|느합|느단|브|스|재가합|재나|재누|재두|재다|재구합|인|과|비합|비단|그|즈|정|후")
NUM = re.compile(r"(?<![0-9A-Za-z])((?:19|20)\d{2})\s?(%s)\s?(\d{1,7})(?![0-9])" % CODES)
HYP = re.compile(r"(?<![0-9])((?:19|20)\d{2})-(\d{3,6})(?![0-9])")
SUPREME = {"두", "다", "도", "모", "마", "그", "스", "므", "후", "추", "헌마", "헌바", "헌가", "헌라", "헌사"}

data_path = os.path.join(site, "cases-data.js")
src = open(data_path, encoding="utf-8").read()
a, b = src.index("["), src.rindex("]") + 1
data = json.loads(src[a:b])

own = set()
own_hyp = set()
for c in data:
    for f in [c.get("court") or ""] + [im.get("alt") or "" for im in c.get("images", [])]:
        for m in NUM.finditer(f):
            own.add(m.group(1) + m.group(2) + m.group(3))
        for m in HYP.finditer(f):
            own_hyp.add(m.group(0))

stats = collections.Counter()
samples = collections.defaultdict(list)


def is_prec(s, m):
    code = m.group(2)
    if code not in SUPREME:
        return False
    pre = s[max(0, m.start() - 40):m.start()]
    post = s[m.end():m.end() + 14]
    return bool(re.search(r"대법원|헌법재판소|헌재|선고|\d{4}[가-힣]{1,2}\d+,\s*$|\d{4}\.\s*\d", pre) or re.search(r"판결|결정|전원합의체", post))


def clean(s):
    s = re.sub(r"\(\s*[·,]?\s*\)", "", s)                 # ()  (·)
    s = re.sub(r"\(\s*[·,]\s*", "(", s)
    s = re.sub(r"\s*[·,]\s*\)", ")", s)
    s = re.sub(r"\(\s*\)", "", s)
    s = re.sub(r"(\S)\s+\)", r"\1)", s)
    s = re.sub(r"\(\s+", "(", s)
    s = re.sub(r"\s*,\s*,", ",", s)
    s = re.sub(r"([가-힣])\s+(,)", r"\1\2", s)
    s = re.sub(r" {2,}", " ", s)
    return s


def strip_text(s, field):
    if not s or not isinstance(s, str):
        return s
    orig = s

    def rep(m):
        n = m.group(1) + m.group(2) + m.group(3)
        if n in own or not is_prec(s, m):
            stats[field] += 1
            return "\x00"
        return m.group(0)
    s = NUM.sub(rep, s)
    s = HYP.sub(lambda m: "\x00" if m.group(0) in own_hyp else m.group(0), s)
    if "\x00" not in s:
        return orig
    # remove separators that joined removed numbers: "\x00·\x00", "\x00, \x00"
    s = re.sub(r"\x00(\s*[·,]\s*\x00)+", "\x00", s)
    s = re.sub(r"\s*\x00", "", s) if False else s
    s = s.replace(" \x00", "\x00").replace("\x00 ", " ").replace("\x00", "")
    s = clean(s)
    if len(samples[field]) < 60:
        samples[field].append((orig, s))
    return s


def strip_court(s):
    if not s:
        return s
    parts = [p.strip() for p in s.split("·")]
    out = []
    for p in parts:
        q = NUM.sub("", p)
        q = HYP.sub("", q)
        q = re.sub(r"\s{2,}", " ", q).strip()
        if q and q not in out:
            out.append(q)
    r = " · ".join(out)
    if r != s:
        stats["court"] += 1
        if len(samples["court"]) < 40:
            samples["court"].append((s, r))
    return r


def walk(o, field, in_quotes=False):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if in_quotes and k == "text":
                continue
            if k in ("url", "no", "id", "src", "thumb", "link", "href", "file", "files", "path", "slug", "stem"):
                continue
            o[k] = walk(v, k, in_quotes or k == "quotes")
        return o
    if isinstance(o, list):
        return [walk(x, field, in_quotes) for x in o]
    if isinstance(o, str):
        return strip_text(o, field)
    return o


# 1) cases-data.js
for c in data:
    c["court"] = strip_court(c.get("court") or "")
    for im in c.get("images", []):
        if im.get("alt"):
            im["alt"] = strip_text(im["alt"], "alt")
    for k in ("title", "summary", "kw", "party", "date"):
        if k in c:
            c[k] = walk(c[k], k)

# 2) cases-detail.json, press.json, work json files
files = [os.path.join(site, "cases-detail.json"), os.path.join(site, "press.json"),
         os.path.join(site, "work", "detail_inputs", "cases.json")] + sorted(glob.glob(os.path.join(site, "work", "details", "*.json")))
loaded = {}
for f in files:
    if not os.path.exists(f):
        continue
    raw = open(f, encoding="utf-8").read()
    j = json.loads(raw)
    # court fields inside work json
    def fix_courts(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "court" and isinstance(v, str):
                    o[k] = strip_court(v)
                else:
                    fix_courts(v)
        elif isinstance(o, list):
            for x in o:
                fix_courts(x)
    fix_courts(j)
    j = walk(j, os.path.basename(f))
    loaded[f] = (raw, j)

print("own numbers:", len(own), "hyphen:", sorted(own_hyp))
print(dict(stats))
if DRY:
    for field, lst in samples.items():
        print("\n=====", field)
        for o, n in lst[:25]:
            print(" -", o[:200])
            print(" +", n[:200])
    sys.exit(0)

new = src[:a] + json.dumps(data, ensure_ascii=False, indent=1) + src[b:]
open(data_path, "w", encoding="utf-8").write(new)
for f, (raw, j) in loaded.items():
    indent = 1 if raw.startswith("{\n ") or raw.startswith("[\n ") else (2 if raw.startswith("{\n  ") or raw.startswith("[\n  ") else None)
    open(f, "w", encoding="utf-8").write(json.dumps(j, ensure_ascii=False, indent=indent) + ("\n" if raw.endswith("\n") else ""))
print("written")
