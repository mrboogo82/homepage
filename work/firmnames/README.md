# 판결문 이미지의 법무법인 이름 가림 해제 도구 (2026. 10. 20.)

기준: 상대방·독립당사자 대리인의 법무법인·법률사무소·법무조합 이름은 유명 여부와 관계없이 모두 보이게 하고,
담당변호사(사람) 이름은 계속 가린다. 종전의 '유명 로펌만 남긴다'는 규칙(rules.FAMOUS_FIRMS)은 폐지.

- `detect.py out.json img...` — 게시 이미지에서 진회색(#3d4045) 상자 가운데 같은 줄 왼쪽 글이
  '법무법인 / 법무법인(유한) / 법률사무소 / 법무조합'으로 끝나는 상자(= 가려진 법인 이름)를 OCR(tesseract kor)로 찾는다.
- `detect_wrap.py out.json img...` — 줄 머리의 상자 가운데 바로 윗줄 끝이 위 접두어로 끝나는 것(이름이 다음 줄로 넘어간 경우)을 찾는다.
- `mapsrc.py 파일목록.txt` — 이미지 이름의 사건번호로 원본 PDF(폴더 파일 이름)를 찾아 map.json을 만든다.
- `restore2.py det.json plan.json out_dir review_dir [이미지,...]` — plan.json([{"image","pdf":[...]}])의 원본 PDF를
  같은 배율(1240px 폭)로 다시 그려 상자 자리에 맞추고(1면은 그대로, 이어 붙인 주문 면은 상자 왼쪽 글로 자리를 찾음),
  상자 아래 글(글자층 또는 OCR)에서 '담당변호사' 앞까지의 법인 이름 부분만 원본 화소로 되살린다.
  out_dir에 새 이미지, review_dir에 전후 비교 그림이 생긴다(복원한 자리는 모두 눈으로 검수할 것).
- HWP 조판본(원본 PDF 없음)은 같은 글꼴(Noto Serif CJK KR Regular 23px, 6배 렌더 후 축소, stroke 1)로 이름을 덧그렸고,
  엘박스 조판본은 work/lbox_specs의 해당 세그먼트 "m": false 로 바꿔 work/render_judgment.py 로 다시 조판한다.

필요한 것: pymupdf, opencv-python-headless, pillow, numpy, tesseract + kor.traineddata. 이미지 폴더 경로는 restore2.py의 CASES_DIR.
