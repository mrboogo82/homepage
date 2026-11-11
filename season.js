// ---------- 계절 효과 (2026. 11. 11. 본인 지시) ----------
// 가을(9~11월) 낙엽 · 겨울(12~2월) 눈 · 봄(3~5월) 벚꽃 · 여름(6~8월) 햇볕. "너무 많이는 말고 살짝 알아차릴 수 있을 정도로만."
// 모든 페이지가 이 파일 하나만 부른다(<script src="season.js" defer>) — 모양·움직임 CSS도 여기서 넣으므로 home.css·cases.css·case.css 는 건드리지 않는다.
// 화면 위에 고정된 얇은 층(.season, 누를 수 없음·머리글 아래)에 조각 몇 개만 띄우고, transform·opacity 만 움직여 스크롤에 부담을 주지 않는다.
// 움직임 줄이기 설정·인쇄에서는 끔. 미리 보기: 주소 끝에 ?season=spring | summer | autumn | winter (끄기 ?season=off).
// 조절 자리: COUNT(조각 수), SIZE(크기 px), TIME(떨어지는 시간 초), OPACITY(진하기).
(function () {
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var m = new Date().getMonth() + 1;
  var season = m >= 3 && m <= 5 ? 'spring' : m >= 6 && m <= 8 ? 'summer' : m >= 9 && m <= 11 ? 'autumn' : 'winter';
  var q = /[?&]season=(spring|summer|autumn|winter|off)\b/.exec(location.search);
  if (q) season = q[1];
  if (season === 'off' || document.querySelector('.season')) return;

  var small = window.innerWidth <= 640;
  var COUNT = { spring: small ? 6 : 10, autumn: small ? 5 : 8, winter: small ? 9 : 14, summer: 3 };
  var SIZE = { spring: [9, 14], autumn: [13, 20], winter: [4, 8] };
  var TIME = { spring: [15, 26], autumn: [16, 28], winter: [13, 24] };
  var OPACITY = { spring: [0.55, 0.85], autumn: [0.45, 0.7], winter: [0.55, 0.9] };

  function svg(body) { return 'url("data:image/svg+xml,' + encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">' + body + '</svg>') + '")'; }
  function leaf(c, v) { return svg('<path fill="' + c + '" d="M12 2.5c-5 3.4-7.2 8.6-5.6 13.6.8 2.4 2.7 3.9 5.6 4.6 2.9-.7 4.8-2.2 5.6-4.6C19.2 11.1 17 5.9 12 2.5z"/><path fill="none" stroke="' + v + '" stroke-width="1" stroke-linecap="round" d="M12 6.5V23"/>'); }
  function petal(c) { return svg('<path fill="' + c + '" d="M12 3.2l1.3 1.5 1.6-1c3.6 3.4 4.5 8.6 2.2 13-1.2 2.2-2.9 3.6-5.1 4.3-2.2-.7-3.9-2.1-5.1-4.3-2.3-4.4-1.4-9.6 2.2-13l1.6 1z"/>'); }
  var IMG = {
    autumn: [leaf('#b9691f', '#8a4a12'), leaf('#cf9a2e', '#a37318'), leaf('#96362b', '#6e231b')],
    spring: [petal('#f4bccb'), petal('#f8d3dc'), petal('#eeaabd')],
    winter: ['radial-gradient(circle, #c9d3de 0 38%, rgba(201,211,222,0.55) 55%, rgba(201,211,222,0) 72%)']
  };

  var css =
    '.season{position:fixed;inset:0;z-index:20;overflow:hidden;pointer-events:none;contain:strict}' +
    '.season i{position:absolute;top:-8vh;left:var(--x);width:var(--s);height:var(--s);animation:season-fall var(--t) linear var(--d) infinite;will-change:transform}' +
    '.season i b{display:block;width:100%;height:100%;background:var(--img) center/contain no-repeat;opacity:var(--o);animation:season-sway var(--w) ease-in-out var(--d) infinite alternate}' +
    '@keyframes season-fall{to{transform:translate3d(var(--dx),118vh,0)}}' +
    '@keyframes season-sway{from{transform:translateX(calc(var(--a) * -1)) rotate(var(--r0))}to{transform:translateX(var(--a)) rotate(var(--r1))}}' +
    /* 여름: 오른쪽 위에서 비치는 옅은 햇빛 + 천천히 밝아졌다 옅어지는 빛줄기 세 가닥 */
    '.season.summer{z-index:31}' +
    '.season.summer::before{content:"";position:absolute;top:-30vmax;right:-30vmax;width:90vmax;height:90vmax;background:radial-gradient(circle,rgba(255,206,92,0.26) 0,rgba(255,214,120,0.12) 32%,rgba(255,220,140,0) 62%);animation:season-sun 9s ease-in-out infinite alternate}' +
    '.season.summer i{top:-20vh;right:var(--x);left:auto;width:var(--s);height:150vh;transform-origin:top right;transform:rotate(var(--r0));background:linear-gradient(180deg,rgba(255,214,110,0.26),rgba(255,224,150,0.09) 45%,rgba(255,224,150,0));filter:blur(22px);opacity:0;animation:season-ray var(--t) ease-in-out var(--d) infinite alternate;will-change:opacity}' +
    '@keyframes season-sun{from{opacity:.7}to{opacity:1}}' +
    '@keyframes season-ray{from{opacity:.15}to{opacity:.9}}' +
    '@media print{.season{display:none}}';
  var st = document.createElement('style'); st.textContent = css; document.head.appendChild(st);

  function rnd(a, b) { return a + Math.random() * (b - a); }
  var layer = document.createElement('div');
  layer.className = 'season ' + season; layer.setAttribute('aria-hidden', 'true');
  var n = COUNT[season], k, el, t;
  if (season === 'summer') {
    for (k = 0; k < n; k++) {
      el = document.createElement('i'); t = rnd(7, 12);
      el.style.cssText = '--x:' + (4 + k * 9) + 'vw;--s:' + rnd(5, 9).toFixed(1) + 'vw;--r0:' + (24 + k * 9) + 'deg;--t:' + t.toFixed(1) + 's;--d:-' + rnd(0, t).toFixed(1) + 's';
      layer.appendChild(el);
    }
  } else {
    var imgs = IMG[season], sz = SIZE[season], tm = TIME[season], op = OPACITY[season], snow = season === 'winter';
    for (k = 0; k < n; k++) {
      el = document.createElement('i'); t = rnd(tm[0], tm[1]);
      // 가로 자리는 칸을 나눠 고르게(한쪽에 몰리지 않게), 시작 시점은 음수 지연으로 흩어 처음부터 화면 곳곳에 떠 있게
      el.style.cssText = '--x:' + ((k + rnd(0.1, 0.9)) / n * 100).toFixed(1) + '%;--s:' + rnd(sz[0], sz[1]).toFixed(1) + 'px;--t:' + t.toFixed(1) + 's;--d:-' + rnd(0, t).toFixed(1) + 's;--dx:' + rnd(-6, 10).toFixed(1) + 'vw;--w:' + rnd(3, 6).toFixed(1) + 's;--a:' + rnd(8, snow ? 14 : 22).toFixed(0) + 'px;--o:' + rnd(op[0], op[1]).toFixed(2) + ';--r0:' + (snow ? 0 : rnd(-70, -10).toFixed(0)) + 'deg;--r1:' + (snow ? 0 : rnd(20, 110).toFixed(0)) + 'deg;--img:' + imgs[k % imgs.length];
      el.appendChild(document.createElement('b'));
      layer.appendChild(el);
    }
  }
  (document.body || document.documentElement).appendChild(layer);
})();
