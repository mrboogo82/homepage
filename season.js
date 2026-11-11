// ---------- 계절 효과 (2026. 11. 11. 본인 지시) ----------
// 가을(9~11월) 낙엽 · 겨울(12~2월) 눈 · 봄(3~5월) 벚꽃 · 여름(6~8월) 햇볕. "너무 많이는 말고 살짝 알아차릴 수 있을 정도로만."
// 모든 페이지가 이 파일 하나만 부른다(<script src="season.js" defer>) — 모양·움직임 CSS도 여기서 넣으므로 home.css·cases.css·case.css 는 건드리지 않는다.
// 화면 위에 고정된 얇은 층(.season, 누를 수 없음·머리글 아래)에 조각 몇 개만 띄우고, transform·opacity 만 움직여 스크롤에 부담을 주지 않는다.
// 움직임 줄이기 설정·인쇄에서는 끔. 미리 보기: 주소 끝에 ?season=spring | summer | autumn | winter (끄기 ?season=off).
// 조절 자리: COUNT(조각 수), SIZE(크기 px), TIME(떨어지는 시간 초), OPACITY(진하기).
(function () {
  var m = new Date().getMonth() + 1;
  var season = m >= 3 && m <= 5 ? 'spring' : m >= 6 && m <= 8 ? 'summer' : m >= 9 && m <= 11 ? 'autumn' : 'winter';
  var q = /[?&]season=(spring|summer|autumn|winter|off)\b/.exec(location.search);
  if (q) season = q[1];
  if (season === 'off' || document.querySelector('.season')) return;

  // ---------- 머리글 이름 옆 나무 한 그루 (2026. 11. 11. 19:20 본인 지시) ----------
  // 봄 벚꽃 나무 · 여름 잎이 우거진 나무 · 가을 단풍 나무 · 겨울 눈 덮인 나무. "한 스푼 감성이 들어가되, 너무 튀지는 않는 느낌으로."
  // 머리글 이름 묶음(.top .brand) 오른쪽에 겹쳐 놓으므로(자리 차지 없음) 머리글 배치는 그대로다. 우듬지만 아주 천천히 흔들리고, 움직임 줄이기 설정에서는 멈춘 그림.
  // 조절 자리: 크기는 아래 CSS 의 .season-tree height, 색은 TREE 의 색 셋.
  (function () {
    var brand = document.querySelector('.top .brand'); if (!brand) return;
    var TREE = {
      spring: { c: ['#f6c6d3', '#f9dbe3', '#efaec0'], o: 0.95 },
      summer: { c: ['#6f9a60', '#86ad72', '#587f51'], o: 1 },
      autumn: { c: ['#c2553a', '#d98a35', '#dcab45'], o: 1 }
    };
    var BLOBS = [[15, 23, 8, 1], [33, 23, 8, 2], [24, 25, 7.5, 0], [18, 14, 8, 0], [30, 14, 8, 1], [24, 9.5, 7, 2], [24, 17.5, 8.5, 1]];
    var wood = '#7a5a44';
    var h = '<ellipse cx="24" cy="50.4" rx="10" ry="1.3" fill="rgba(60,45,35,0.10)"/>';
    if (season === 'winter') {
      var BR = ['M24 36L14 26', 'M24 33L34 23', 'M24 28L18 15', 'M24 28L30 14', 'M14 26L8.5 22.5', 'M34 23L39.5 20', 'M18 15L14.5 9.5', 'M30 14L33 8.5', 'M24 28L24 12'];
      var SNOW = ['M9 21.2L14 24.4L19 29.4', 'M39 18.7L34 21.4L29.5 25.9'];
      var PUFF = [[13.5, 20.5, 5.2], [34.5, 18.5, 5.2], [18, 13, 6.2], [30, 12.5, 6.2], [24, 8.5, 5.8], [24, 16.5, 5.6]], k, puffs = '', lines = '';
      h += '<path d="M24 50C23.4 43 24.6 36 24 28" fill="none" stroke="' + wood + '" stroke-width="2.8" stroke-linecap="round"/>';
      h += '<path d="' + BR.join('') + '" fill="none" stroke="' + wood + '" stroke-width="1.5" stroke-linecap="round"/>';
      h += '<path d="' + SNOW.join('') + '" fill="none" stroke="#b9c7d6" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/>';
      h += '<path d="' + SNOW.join('') + '" fill="none" stroke="#f4f8fb" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>';
      // 가지 위에 소복이 얹힌 눈: 바깥 금(옅은 청회색)을 먼저 한꺼번에 그리고 그 위에 흰 덩이를 얹어 덩이끼리 겹친 자리에 금이 남지 않게
      for (k = 0; k < PUFF.length; k++) { lines += '<circle cx="' + PUFF[k][0] + '" cy="' + PUFF[k][1] + '" r="' + (PUFF[k][2] + 0.55) + '"/>'; puffs += '<circle cx="' + PUFF[k][0] + '" cy="' + PUFF[k][1] + '" r="' + PUFF[k][2] + '"/>'; }
      h += '<g fill="#b9c7d6">' + lines + '</g><g fill="#f4f8fb">' + puffs + '</g>';
      h += '<g fill="#dfe7ef"><circle cx="20" cy="15.5" r="2.2"/><circle cx="29" cy="10.5" r="1.8"/><circle cx="14" cy="22" r="1.5"/></g>';
      h += '<path d="M24 27L24 20.5M21 22.5L24 25.5L27.4 21.8" fill="none" stroke="' + wood + '" stroke-width="1.1" stroke-linecap="round" opacity="0.55"/>';
      h += '<path d="M11 50.6Q24 44.6 37 50.6Z" fill="#f4f8fb" stroke="#b9c7d6" stroke-width="0.7" stroke-linejoin="round"/>';
      h += '<g fill="#b9c7d6"><circle cx="7" cy="33" r="1"/><circle cx="41" cy="31" r="1.1"/><circle cx="38" cy="41" r="0.8"/><circle cx="10" cy="43" r="0.8"/><circle cx="24" cy="4" r="0.9"/></g>';
    } else {
      var t = TREE[season], k, b, top = '';
      h += '<path d="M24 50C23.4 44 24.6 38 24 27M24 37L16.5 28M24 34L31.5 26" fill="none" stroke="' + wood + '" stroke-width="2.6" stroke-linecap="round"/>';
      for (k = 0; k < BLOBS.length; k++) { b = BLOBS[k]; top += '<circle cx="' + b[0] + '" cy="' + b[1] + '" r="' + b[2] + '" fill="' + t.c[b[3]] + '"/>'; }
      if (season === 'spring') top += '<g fill="#fff" opacity="0.75"><circle cx="19" cy="12" r="1.3"/><circle cx="29" cy="18" r="1.2"/><circle cx="14" cy="22" r="1.1"/><circle cx="33" cy="25" r="1"/><circle cx="24" cy="8" r="1"/></g><g fill="#e58fa8"><circle cx="23" cy="15" r="0.9"/><circle cx="31" cy="11" r="0.8"/><circle cx="17" cy="19" r="0.8"/><circle cx="27" cy="24" r="0.8"/></g>';
      if (season === 'summer') top += '<g fill="#a5c88f" opacity="0.8"><circle cx="19.5" cy="11.5" r="3"/><circle cx="29.5" cy="19" r="2.4"/><circle cx="13.5" cy="21" r="2"/></g>';
      if (season === 'autumn') top += '<g fill="#e9c35a" opacity="0.85"><circle cx="20" cy="11" r="2.4"/><circle cx="31" cy="20" r="2"/></g><g fill="#a93f2e"><circle cx="27" cy="13" r="1.6"/><circle cx="16" cy="23" r="1.4"/></g>';
      h += '<g class="season-tree-top" opacity="' + t.o + '">' + top + '</g>';
      if (season === 'spring') h += '<g fill="#efaec0"><ellipse cx="41" cy="33" rx="1.5" ry="1" transform="rotate(-30 41 33)"/><ellipse cx="8" cy="38" rx="1.4" ry="0.9" transform="rotate(25 8 38)"/><ellipse cx="35" cy="49.6" rx="1.5" ry="0.8"/><ellipse cx="14" cy="50" rx="1.3" ry="0.7"/></g>';
      if (season === 'autumn') h += '<g><ellipse cx="41" cy="35" rx="1.8" ry="1.1" fill="#d98a35" transform="rotate(-35 41 35)"/><ellipse cx="8" cy="40" rx="1.6" ry="1" fill="#c2553a" transform="rotate(30 8 40)"/><ellipse cx="34" cy="49.8" rx="1.8" ry="0.9" fill="#dcab45"/><ellipse cx="15" cy="50" rx="1.6" ry="0.8" fill="#c2553a"/><ellipse cx="29" cy="50.4" rx="1.4" ry="0.7" fill="#d98a35"/></g>';
    }
    var st = document.createElement('style');
    st.textContent =
      '.top .brand{position:relative}' +
      '.season-tree{position:absolute;left:100%;bottom:-0.15rem;height:2.9rem;width:auto;margin-left:0.55rem;overflow:visible;pointer-events:none}' +
      '.season-tree-top{transform-box:view-box;transform-origin:24px 50px;animation:season-tree-sway 7s ease-in-out infinite alternate}' +
      '@keyframes season-tree-sway{from{transform:rotate(-1.3deg)}to{transform:rotate(1.3deg)}}' +
      '@media (max-width:760px){.season-tree{height:2.45rem;margin-left:0.4rem}}' +
      '@media (prefers-reduced-motion:reduce){.season-tree-top{animation:none}}' +
      '@media print{.season-tree{display:none}}';
    document.head.appendChild(st);
    var box = document.createElement('span');
    box.innerHTML = '<svg class="season-tree" viewBox="0 0 48 52" aria-hidden="true" focusable="false">' + h + '</svg>';
    brand.appendChild(box.firstChild);
  })();

  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;   // 떨어지는 조각·햇볕은 움직임 줄이기 설정에서 끔(나무는 멈춘 그림으로 남김)

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
