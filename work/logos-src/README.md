# 기관 로고 — 출처와 가공 기록 (2026. 10. 20.~21.)

홈페이지 '법률고문 위촉'·'위원회 · 강의' 절의 타일마다 붙는 **작은 로고 띠**와 강의 목록의 로고에 쓰는 `logos/` 폴더 33개 파일의
출처·가공 방법이다. `raw/`에는 받은 원본을 그대로 두었다(다시 만들 때 쓰려고).

기준(변호사님 지시):
- 2026. 10. 20.: 서규영 변호사(lawyersuh.com)·정관영 변호사(policylaw.kr) 홈페이지처럼 의뢰 기관(법률고문으로 위촉한 기관)의 공식 로고를
  홈페이지에 보이되, 정부상징 사용 규정 위반 여부는 신경 쓰지 않는다. 종전 결정(공공기관만 로고, 부처는 이름으로)은 이것으로 대체.
- 2026. 10. 21.: 처음 만든 '로고 벽'(위촉 절 첫머리의 로고 20칸)은 위촉장 타일과 내용이 겹치고 로고가 커서 번잡하다고 하여 없앰.
  대신 **타일마다 위촉장 그림 위에 로고를 작게** 넣고, 로고는 위촉장이 아니라 **그 기관의 공식 누리집**으로 링크한다.
  임기를 마친 위촉·위원회, 강의 기관도 같게. 주식회사 에스알은 누리집이 코레일로 통합되어 코레일 누리집으로.
  한국장애인개발원 청렴시민감사관은 새 위촉장은 없지만 계속 하고 있으므로 현행 위원회로 옮김(2024. 8. ~ 현재).

## 표시 방식 (2026. 10. 21.)

- 타일(`li.adv`)의 차례: `a.adv-logo`(로고 띠, 누리집 새 창) → `button.adv-fig`(위촉장 그림, 누르면 보기 창) → `div.adv-body`(기관·역할·기간).
  띠는 흰 바탕(어두운 화면에서도 흰색이라 로고 지정색 유지), 높이 2.4rem, 로고 높이 1.4rem(`.tall` 1.9rem: 서울시설공단, `.mid` 1.6rem: SR·TIPA).
  임기를 마친 타일(`.past-grid`)은 띠 1.7rem·로고 1rem. 위촉장이 없는 타일(충남대학교병원·HUG·TIPA·중기부 재검토위원회)은 그림 자리에 건물 그림과 약칭.
- 좁은 화면(≤640px, 한 줄 목록)에서는 띠가 위촉장 그림 옆·기관명 위의 작은 칸으로 간다(`grid-template-areas: "fig logo" "fig body"`).
- 강의 목록(`dl.rows.dates`)의 각 줄 앞에 `a.lec-logo`(띠 1.6rem·로고 1.05rem).
- 임기를 마친 글줄(`p.past`)의 기관 이름은 누리집 링크(GKL·새만금개발공사·한국남동발전·스마트제조혁신추진단·종로구·법무부).
- GA 이벤트 `logo_click`(org) — 로고 띠를 눌러 누리집으로 갈 때.
- 적용 도구: `python3 work/logos-src/apply_tiles.py index.html` (로고 벽이 있는 index.html에 한 번 적용; 아티팩트 미리보기 사본에도 같게 씀).

## 누리집 주소

교육부 moe.go.kr · 기상청 kma.go.kr · 행정안전부 mois.go.kr · 문화체육관광부 mcst.go.kr · 서울특별시 seoul.go.kr · 중소벤처기업부 mss.go.kr ·
기후에너지환경부 mcee.go.kr(me.go.kr이 넘어감) · 보건복지부 mohw.go.kr · 농림축산식품부 mafra.go.kr · 충남대학교병원 cnuh.co.kr · 한국환경공단 keco.or.kr ·
대한체육회 sports.or.kr · 서울주택도시개발공사 i-sh.co.kr · 서울시설공단 sisul.or.kr · 국가과학기술연구회 nst.re.kr · 주식회사 에스알 → korail.com ·
축산물품질평가원 ekape.or.kr · 한국환경산업기술원 keiti.re.kr · 주택도시보증공사 khug.or.kr · 중소기업기술정보진흥원 tipa.or.kr ·
과학기술정보통신부 msit.go.kr · 인천광역시교육청 ice.go.kr · 서천군 seocheon.go.kr · 식품의약품안전처 mfds.go.kr · 한국전력공사 home.kepco.co.kr ·
한국장애인개발원 koddi.or.kr · 인천광역시 incheon.go.kr · 한국산업단지공단 kicox.or.kr · 과천시 gccity.go.kr · 법무부 moj.go.kr · 법무연수원 ioj.moj.go.kr ·
대한법률구조공단 klac.or.kr · 인천광역시교육청교육연수원 ieti.or.kr · 서울지방변호사회 seoulbar.or.kr · GKL gkl.co.kr · 새만금개발공사 sdco.or.kr ·
한국남동발전 koenergy.kr · 스마트제조혁신추진단 smart-factory.kr · 종로구 jongno.go.kr (2026. 10. 21. 브라우저로 접속 확인; gkl·ioj는 접속 확인 못 함)

## 파일별 출처

부처 로고는 모두 위키미디어 공용의 "… of the Republic of Korea Logo (horizontal).svg" 계열(정부상징 + 기관명, 같은 조판)에서 받아
서명 체계가 한결같도록 했다. 기관 누리집의 머리글 그림은 대개 150~300px라 작아서, 누리집에서는 CI 소개 자료만 썼다.
SVG는 `tighten_svg.py`로 viewBox를 내용 범위(+1% 여백)로 좁히고 루트 width/height·주석을 지웠다.

| 파일 | 기관 | 출처(raw/ 파일) | 가공 |
|---|---|---|---|
| moe.svg | 교육부 | 위키미디어 공용 SVG(`moe-commons.svg`) | viewBox 좁힘 |
| kma.svg | 기상청 | 위키미디어 공용 SVG(`kma-commons.svg`). kma.go.kr은 weather.go.kr(날씨누리)로 넘어가 로고가 다르고, kma.go.kr/kma 머리글 그림(`kma.png`)은 152px라 쓰지 않음 | 같음 |
| mois.svg | 행정안전부 | 위키미디어 공용 SVG(`mois-commons.svg`); 누리집 PNG(`mois.png`)는 316px | 같음 |
| mcst.svg | 문화체육관광부 | 위키미디어 공용 SVG(`mcst-commons.svg`) | 같음 |
| mss.svg | 중소벤처기업부 | 위키미디어 공용 SVG(`mss-commons.svg`) | 같음. 재검토위원회·국민제안심사위원회 타일에도 사용 |
| mcee.svg | 기후에너지환경부 | 위키미디어 공용 SVG(`mcee-commons.svg`); 옛 환경부 로고는 `me.svg`(미사용) | 같음 |
| mohw.svg | 보건복지부 | 위키미디어 공용 SVG(`mohw-commons.svg`) | 같음 |
| mafra.svg | 농림축산식품부 | 위키미디어 공용 SVG(`mafra-commons.svg`) | 같음 |
| mfds.svg | 식품의약품안전처 | 위키미디어 공용 SVG(`mfds-commons.svg`) | 같음. 행정처분심의위원회 타일 |
| msit.svg | 과학기술정보통신부 | 위키미디어 공용 SVG(`msit-commons.svg`) | 같음. 임기를 마친 위촉·연구자권익보호위원회 타일 |
| moj.svg | 법무부 | 위키미디어 공용 "Ministry of Justice of the Republic of Korea Logo (horizontal).svg"(`moj-commons.svg`) | 같음. 사법시험 검토위원 타일 |
| ioj.svg | 법무부 법무연수원 | 나무위키 수록 SVG(`ioj-namu.svg`, 두 줄 서명) | 같음. 강의 목록 |
| ice.svg | 인천광역시교육청 | 위키미디어 공용 "Incheon Metropolitan City Office of Education Logo (horizontal).svg"(`ice-commons.svg`) | 같음. 임기를 마친 위촉·교육소청심사위원회·교육연수원 강의 |
| kepco.svg | 한국전력공사 | 위키미디어 공용 "Kepco logo ko-en.svg"(`kepco-koen-commons.svg`; 나무위키 SVG `kepco-namu.svg`도 같은 모양) | 같음 |
| kicox.svg | 한국산업단지공단 | 나무위키 수록 SVG(`kicox-namu.svg`) | 같음 |
| klac.svg | 대한법률구조공단 | 나무위키 수록 SVG(`klac-namu.svg`) | 같음. 강의 목록 |
| koddi.svg | 한국장애인개발원 | 나무위키 수록 SVG(`koddi-namu.svg`, 슬로건 포함) | 같음 |
| seocheon.svg | 서천군 | 서천군 누리집 '서천군 상징' 페이지의 로고 SVG(`seocheon-site.svg`); 나무위키 SVG(`seocheon-namu.svg`)는 심벌만 | 같음 |
| incheon.png | 인천광역시 | 인천시 누리집 심볼마크 페이지의 'CI jpg파일.zip' 중 '시그니춰국문 해상도_72.jpg'(`incheon-sig-ko.jpg`; 브라우저 안에서 zip 풀어 받음)의 가로형 서명 부분 | 안내선 밖으로 잘라 내고 흰 바탕을 투명하게 → 928×207. 위키미디어 공용 "Emblem of Incheon.svg"·나무위키 휘장은 심벌만이라 안 씀 |
| gwacheon.png | 과천시 | 나무위키 심벌 SVG(`gwacheon-namu.svg`) + 과천시 누리집 심볼마크 페이지의 한글 로고타입(`gwacheon-logotype.png`) | 누리집 시그니처 안내(`gwacheon-sig7.png`: 글자 높이 A, 심벌 1.86A, 사이 0.2A, 심벌 밑이 글자 밑보다 0.24A 아래)대로 `compose_gwacheon.py`로 합성 → 776×268 |
| seoulbar.png | 서울지방변호사회 | 누리집 머리글 GIF(`seoulbar-head.gif`, 215×31; CI 자료 없음) | 흰 바탕을 투명하게. 강의 목록(작게 보임) |
| seoul.png | 서울특별시 | 서울시 CI 자료(zip)의 국문 가로형 서명(`seoul.png`; 영문형·세로형은 `seoul-en.png`·`seoul-stacked.png`) | 여백 자름 |
| cnuh.png | 충남대학교병원 | 병원 CI 자료 `signature_01_01.png`(`cnuh.png`, 1200px); 누리집 소개 그림(`cnuh-web.png`)은 298px | 여백 자름 → 900×129 |
| keco.png | 한국환경공단 | 공단 CI 자료의 심벌(`keco-symbol.png`)과 로고타입(`keco-logotype.png`) | 머리글 로고(`keco-head.png`)의 비율(심벌 높이 50 : 글자 높이 24, 사이 0.18배)대로 합성 → 436×112 |
| ksoc.svg | 대한체육회 | 대한체육회 누리집 머리글의 SVG(`ksoc.svg`, 199×60) | 그대로 |
| sh.svg | 서울주택도시개발공사 | 나무위키 수록 SVG(`sh-namu.svg`); 누리집 CI 그림(`sh.jpg`·`sh-ci2.jpg`)은 안내선이 함께 있어 쓰지 않음 | 그대로 |
| sisul.png | 서울시설공단 | 공단 누리집 CI 소개 그림(`sisul.png`, 909×545); 머리글 GIF(`sisul.gif`)는 123px | 여백 자름 → 500×260 |
| nst.svg | 국가과학기술연구회 | 나무위키 수록 SVG(`nst-namu.svg`); 누리집 CI 그림(`nst-ci02/06.png`)은 270px | 그대로 |
| sr.svg | 주식회사 에스알 | 위키미디어 공용 "SR Corporation logo.svg"(`sr-commons.svg`); srail.or.kr은 korail.com으로 넘어감 | 그대로 |
| ekape.png | 축산물품질평가원 | 평가원 CI 기본 체계 자료(BS-13 Signature 좌·우조합, `ekape-full.jpg`)의 '국문/Full Name 좌·우조합'(`ekape-logotype.png`) | 흰 바탕을 투명하게 → 340×58 |
| keiti.svg | 한국환경산업기술원 | 나무위키 수록 SVG(`keiti-namu.svg`); 누리집 머리글 PNG(`keiti.png`)는 흰색 로고, 서명 그림(`keiti-sig.png`)은 안내선 포함 | 그대로 |
| hug.svg | 주택도시보증공사 | 나무위키 수록 SVG(`hug-namu.svg`) | 그대로 |
| tipa.png | 중소기업기술정보진흥원 | 진흥원 CI 자료 GIF(`tipa-c2.gif` 등); 누리집 머리글 SVG는 흰색 로고 | 아이보리 바탕을 투명하게(알파 ≤14 → 0) → 624×192 |

## 다시 만들 때

- 원본은 `raw/`에 있고, 받은 날은 2026. 10. 20.~21.이다. 이 작업 환경의 셸은 바깥 사이트에 닿지 않아, 데스크톱 앱의 브라우저 창에서 `fetch()`로 받아
  base64·SHA-256과 함께 넘겨 받고 해시를 대조해 저장했다(SVG는 창에서 직접 열어 받음; 인천시 zip은 브라우저의 DecompressionStream으로 풀었음).
- 대조표: `python3 work/logos-src/sheet.py logos 대조표.png` (playwright 필요) — 로고를 흰 칸에 늘어놓은 그림을 만든다.
- SVG 정리: `python3 work/logos-src/tighten_svg.py 출력폴더 원본.svg:이름 …` (viewBox 좁히기·width/height 제거).
- 새 기관을 더할 때: 로고를 `logos/`에 넣고(SVG가 가장 좋고, PNG는 투명 배경·짧은 변 100px 이상), 그 타일 맨 앞에
  `<a class="adv-logo" href="누리집" target="_blank" rel="noopener" data-org="기관" aria-label="기관 누리집 (새 창)"><img src="logos/파일" alt="" width=… height=… loading="lazy"></a>`를 붙인다.
  로고가 유난히 높으면 `.tall`, 짧고 높으면 `.mid`.
- 주식회사 에스알: 공정위가 2026. 8. 3. 코레일의 SR 고속철도 영업양수를 승인했고 정부는 2026. 9. 통합 완료를 예정했다(srail.or.kr은 이미 korail.com으로 넘어감).
  법률고문 위촉이 그대로 이어지는지에 따라 위촉 타일을 '임기를 마친 위촉'으로 옮길지 변호사님 확인이 필요하다(로고 링크는 코레일로 해 둠).
