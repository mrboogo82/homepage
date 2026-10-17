변호사 부효준 홈페이지 — 정적 사이트 묶음 (2026. 10. 16. 오후, 아티팩트 Version 121과 같은 내용 — 주요 수행 사례 277건, 판결문 이미지 368장)
※ 묶음이 커져 두 파일로 나누었습니다: 1of2(페이지·certs 등 전부, cases/ 제외)와 2of2-cases(cases/ 폴더). 두 파일을 같은 폴더에 풀면 아래 구성이 됩니다.

구성
- index.html       첫 화면(소개·경력·위촉·위원회·다루는 사건·주요 수행 사례 최근 12건·상담)
- cases.html       주요 수행 사례 전체(목록 보기가 기본, 누르면 펼쳐짐; 카드 보기로 전환 가능; 분류별 보기; cases.html#cat=rnd 처럼 분류를 지정해 열 수 있음 — 분류키: rnd 국가연구개발, personnel 인사·징계·소청,
                   license 인허가·면허·자격, penalty 제재부가금·환수·부정당업자 제재, admin 그 밖의 행정처분, state 국가배상, comp 손실보상, civil 민사·연금·계약, criminal 형사)
- cases/           판결문·결정문 이미지(개인·회사 당사자 정보는 가리고, 본인이 대리한 국가·행정청·공공기관 이름은 보임)
                   1면에 주문이 없는 판결문(110건)은 주문이 있는 면을 같은 기준으로 가려 1면 아래에 이어 붙인 세로로 긴 한 장입니다
                   (파일 하나, alt에 "제1면·제2면(주문)"처럼 면 번호를 적음). 판결문 보기 창에서는 긴 이미지를 창 안에서 스크롤해 읽습니다.
- certs/           위촉장·표창장 이미지
- og-image.jpg, photo-head.jpg, photo-hero.webp, seal.png
- robots.txt, sitemap.xml, 404.html, CNAME(lawyermrboo82.com)

게시(GitHub Pages 기준)
1. GitHub에 저장소를 만들고 이 묶음의 파일을 모두 올립니다(폴더 구조 그대로, index.html이 최상위).
2. 저장소 Settings → Pages → Branch: main(루트) 저장 → Custom domain에 lawyermrboo82.com 입력 → Enforce HTTPS.
3. 도메인 DNS에 A 레코드 4개(185.199.108.153 / 185.199.109.153 / 185.199.110.153 / 185.199.111.153)와
   www CNAME(<깃허브아이디>.github.io)을 추가합니다.
4. Google Search Console·네이버 서치어드바이저·Bing 웹마스터에 사이트를 등록하고
   https://lawyermrboo82.com/sitemap.xml 을 제출합니다.

고칠 때
- 사례를 더하거나 고칠 때는 index.html의 <script id="cases-data"> JSON과 cases.html의 같은 블록,
  두 페이지의 사례 목록(<ol id="case-list">)과 건수 문구를 함께 바꿉니다. 새 판결문은 cases/ 폴더에
  1240px 폭 JPG로 넣습니다. Claude에게 판결문 PDF를 보내면 같은 기준으로 가려서 만들어 줍니다.

온라인 상담 신청(상담 문의 아래 신청서)
- 신청서는 FormSubmit(formsubmit.co, 무료 폼 전송 서비스)을 거쳐 boo@keumseonglaw.com으로 전달됩니다. 서버나 회원가입이 필요 없습니다.
- 처음 한 번만: 게시된 홈페이지에서 신청서를 한 번 보내면 boo@keumseonglaw.com으로 FormSubmit의 확인(Activate) 메일이 옵니다.
  그 메일의 Activate 버튼을 누른 뒤부터 신청 내용이 메일로 들어옵니다(그 전에 보낸 신청은 전달되지 않습니다).
- 확인 메일에는 이메일 주소 대신 쓸 수 있는 무작위 문자열(예: https://formsubmit.co/abcd1234...)도 함께 옵니다. 원하면 index.html에서
  "formsubmit.co/boo@keumseonglaw.com"과 "formsubmit.co/ajax/boo@keumseonglaw.com"의 주소 부분을 그 문자열로 바꾸어도 됩니다(스팸봇에 주소 노출 방지).
- 첨부파일은 10MB까지이며, 전송이 막히면 신청서 아래에 '이메일 앱으로 보내기' 링크가 나타납니다.
- 자바스크립트가 꺼진 환경에서는 FormSubmit의 확인 화면(reCAPTCHA)을 거쳐 https://lawyermrboo82.com/?sent=1#contact 로 돌아옵니다.
