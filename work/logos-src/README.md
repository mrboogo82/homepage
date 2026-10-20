# 법률고문 위촉 기관 로고 — 출처와 가공 기록 (2026. 10. 20.)

홈페이지 '법률고문 위촉' 절 첫머리의 로고 벽(`.logo-wall`, index.html)과 위촉장이 없는 타일의 그림에 쓰는
`logos/` 폴더 22개 파일의 출처·가공 방법이다. `raw/`에는 받은 원본을 그대로 두었다(다시 만들 때 쓰려고).

기준(2026. 10. 20. 변호사님 지시): 서규영 변호사(lawyersuh.com)·정관영 변호사(policylaw.kr) 홈페이지처럼
의뢰 기관(법률고문으로 위촉한 기관)의 공식 로고를 홈페이지에 보이되, 정부상징 사용 규정 위반 여부는 신경 쓰지 않는다.
종전 결정(공공기관만 로고, 부처는 이름으로)은 이것으로 대체되었다.

## 표시 방식

- 로고 벽은 `#advisory`의 `<h3 class="block-h">법률고문 위촉</h3>` 바로 아래 `<div class="logo-wall">` — 머리글 한 줄 + `<ul class="logos">`(4열, 1000px 이하 3열, 640px 이하 2열) + 안내 한 줄.
- 칸(`.logo-card`)은 어두운 화면에서도 흰 바탕이다(로고 지정색을 그대로 보이려고). 그림 상자는 너비 88%·높이 3.2rem에 `object-fit: contain`;
  모양에 따라 `.wide`(너비 94%: 긴 로고와 긴 이름의 부처), `.tall`(높이 3.7rem: 서울시설공단), `.mid`(너비 70%·높이 3.4rem: SR).
- 위촉장이 있는 기관은 `<button data-certs="…" data-org="…" data-term="…">`이고 누르면 그 기관의 위촉장이 보기 창(LB)에 열린다
  (`data-certs`는 certs/ 파일 이름을 쉼표로, 최근 것이 먼저). 위촉장이 없는 기관(충남대학교병원·HUG·TIPA)은 `<div class="logo-card still" title="…">`로 눌리지 않는다.
- 같은 로고를 위촉 타일(`.adv-fig.logo-fig`)에도 쓴다: 위촉장이 없어 빈 그림이던 충남대학교병원·HUG·TIPA 타일과 중기부 재검토위원회 타일(mss.svg).
- GA 이벤트 `logo_click`(org) — 로고 벽에서 위촉장을 열 때.
- 순서는 위촉 타일과 같다(위촉 시작월 내림차순, 중앙행정기관·지방자치단체 → 공공기관·공기업·단체).

## 파일별 출처

부처 로고는 모두 위키미디어 공용의 "… of the Republic of Korea Logo (horizontal).svg" 계열(정부상징 + 기관명, 같은 조판)에서 받아
서명 체계가 한결같도록 했다. 기관 누리집의 머리글 그림은 대개 150~300px라 작아서, 누리집에서는 CI 소개 자료만 썼다.

| 파일 | 기관 | 출처(raw/ 파일) | 가공 |
|---|---|---|---|
| moe.svg | 교육부 | 위키미디어 공용 SVG(`moe-commons.svg`) | viewBox를 내용 범위(+1% 여백)로 좁히고 루트 width/height·주석 제거 |
| kma.svg | 기상청 | 위키미디어 공용 SVG(`kma-commons.svg`). kma.go.kr은 weather.go.kr(날씨누리)로 넘어가 로고가 다르고, kma.go.kr/kma 머리글 그림(`kma.png`)은 152px라 쓰지 않음 | 같음 |
| mois.svg | 행정안전부 | 위키미디어 공용 SVG(`mois-commons.svg`); 누리집 PNG(`mois.png`)는 316px | 같음 |
| mcst.svg | 문화체육관광부 | 위키미디어 공용 SVG(`mcst-commons.svg`) | 같음 |
| mss.svg | 중소벤처기업부 | 위키미디어 공용 SVG(`mss-commons.svg`) | 같음. 재검토위원회 타일에도 사용 |
| mcee.svg | 기후에너지환경부 | 위키미디어 공용 SVG(`mcee-commons.svg`); 옛 환경부 로고는 `me.svg`(미사용) | 같음 |
| mohw.svg | 보건복지부 | 위키미디어 공용 SVG(`mohw-commons.svg`) | 같음 |
| mafra.svg | 농림축산식품부 | 위키미디어 공용 SVG(`mafra-commons.svg`) | 같음 |
| mfds.svg · msit.svg | 식품의약품안전처 · 과학기술정보통신부 | 위키미디어 공용 SVG | 같음. 로고 벽에는 아직 쓰지 않음(현행 법률고문 위촉이 아님) — 필요할 때 같은 방식으로 추가 |
| seoul.png | 서울특별시 | 서울시 CI 자료(zip)의 국문 가로형 서명(`seoul.png`; 영문형·세로형은 `seoul-en.png`·`seoul-stacked.png`) | 여백 자름 |
| cnuh.png | 충남대학교병원 | 병원 CI 자료 `signature_01_01.png`(`cnuh.png`, 1200px); 누리집 소개 그림(`cnuh-web.png`)은 298px | 여백 자름 → 900×129 |
| keco.png | 한국환경공단 | 공단 CI 자료의 심벌(`keco-symbol.png`)과 로고타입(`keco-logotype.png`) | 머리글 로고(`keco-head.png`)의 비율(심벌 높이 50 : 글자 높이 24, 사이 0.18배)대로 두 그림을 합성 → 436×112 |
| ksoc.svg | 대한체육회 | 대한체육회 누리집 머리글의 SVG(`ksoc.svg`, 199×60) | 그대로 |
| sh.svg | 서울주택도시개발공사 | 나무위키 수록 SVG(`sh-namu.svg`); 누리집 CI 그림(`sh.jpg`·`sh-ci2.jpg`)은 안내선이 함께 있어 쓰지 않음 | 그대로 |
| sisul.png | 서울시설공단 | 공단 누리집 CI 소개 그림(`sisul.png`, 909×545); 머리글 GIF(`sisul.gif`)는 123px | 여백 자름 → 500×260 |
| nst.svg | 국가과학기술연구회 | 나무위키 수록 SVG(`nst-namu.svg`); 누리집 CI 그림(`nst-ci02/06.png`)은 270px | 그대로 |
| sr.svg | 주식회사 에스알 | 위키미디어 공용 "SR Corporation logo.svg"(`sr-commons.svg`); srail.or.kr은 korail.com으로 넘어감(코레일–SR 통합 승인 2026. 8.) | 그대로 |
| ekape.png | 축산물품질평가원 | 평가원 CI 기본 체계 자료(BS-13 Signature 좌·우조합, `ekape-full.jpg`)의 '국문/Full Name 좌·우조합'(`ekape-logotype.png`) | 흰 바탕을 투명하게 → 340×58 |
| keiti.svg | 한국환경산업기술원 | 나무위키 수록 SVG(`keiti-namu.svg`); 누리집 머리글 PNG(`keiti.png`)는 흰색 로고, 서명 그림(`keiti-sig.png`)은 안내선 포함 | 그대로 |
| hug.svg | 주택도시보증공사 | 나무위키 수록 SVG(`hug-namu.svg`) | 그대로 |
| tipa.png | 중소기업기술정보진흥원 | 진흥원 CI 자료 GIF(`tipa-c2.gif` 등); 누리집 머리글 SVG는 흰색 로고 | 아이보리 바탕을 투명하게(알파 ≤14 → 0) → 624×192 |

## 다시 만들 때

- 원본은 `raw/`에 있고, 받은 날은 모두 2026. 10. 20.이다. 이 작업 환경의 셸은 바깥 사이트에 닿지 않아, 데스크톱 앱의 브라우저 창에서 `fetch()`로 받아
  base64·SHA-256과 함께 넘겨 받고 해시를 대조해 저장했다(SVG는 창에서 직접 열어 문서를 직렬화).
- 대조표: `python3 work/logos-src/sheet.py logos 대조표.png` (playwright 필요) — 22개를 흰 칸에 늘어놓은 그림을 만든다.
- 새 기관을 더할 때: 로고를 `logos/`에 넣고(SVG가 가장 좋고, PNG는 투명 배경·짧은 변 100px 이상), `.logos`에 `<li>` 한 줄을 위촉 순서에 맞게 끼우고,
  위촉장이 있으면 `data-certs`에 certs/ 파일 이름을 적는다. 로고가 유난히 길거나 높으면 `.wide`·`.tall`·`.mid`로 맞춘다.
- 주식회사 에스알: 공정위가 2026. 8. 3. 코레일의 SR 고속철도 영업양수를 승인했고 정부는 2026. 9. 통합 완료를 예정했다(srail.or.kr은 이미 korail.com으로 넘어감).
  법률고문 위촉이 그대로 이어지는지에 따라 위촉 타일과 로고 벽을 '임기를 마친 위촉'으로 옮길지 변호사님 확인이 필요하다.
