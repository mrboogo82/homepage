#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HWP 5.0 파일에서 본문 글만 뽑는 최소 추출기(표 안의 글 포함, 서식 없음).
    python3 work/hwp_text.py 파일.hwp  → 표준출력
"""
import struct
import sys
import zlib

import olefile

PARA_TEXT = 67  # HWPTAG_BEGIN(16) + 51


def records(data):
    i = 0
    n = len(data)
    while i + 4 <= n:
        (h,) = struct.unpack_from("<I", data, i)
        tag = h & 0x3FF
        size = (h >> 20) & 0xFFF
        i += 4
        if size == 0xFFF:
            (size,) = struct.unpack_from("<I", data, i)
            i += 4
        yield tag, data[i:i + size]
        i += size


def para_text(payload):
    out = []
    u = payload
    j = 0
    while j + 1 < len(u):
        ch = struct.unpack_from("<H", u, j)[0]
        j += 2
        if ch < 32:
            # 인라인/확장 컨트롤(8글자 = 16바이트)은 건너뛴다
            if ch in (1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 21, 22, 23):
                j += 14
            elif ch == 13:
                out.append("\n")
            elif ch in (9, 10):
                out.append(" ")
            # 그 밖의 제어문자는 무시
        else:
            out.append(chr(ch))
    return "".join(out)


def hwp_text(path):
    ole = olefile.OleFileIO(path)
    header = ole.openstream("FileHeader").read()
    compressed = bool(header[36] & 1)
    texts = []
    sections = sorted([e for e in ole.listdir() if e and e[0] == "BodyText"], key=lambda e: int(e[1].replace("Section", "") or 0))
    for e in sections:
        raw = ole.openstream(e).read()
        data = zlib.decompress(raw, -15) if compressed else raw
        for tag, payload in records(data):
            if tag == PARA_TEXT:
                t = para_text(payload)
                if t.strip():
                    texts.append(t)
    return "\n".join(texts)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(hwp_text(p))
