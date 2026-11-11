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
    // 2026. 11. 11. 19:25 본인 지시("실제 나무 같은 느낌이 더 나도록"): 둥근 덩이 일곱 개 대신, 줄기에서 가지가 갈라져 나가는 뼈대를 먼저 기르고(grow)
    // 가지 끝마다 작은 잎 뭉치를 그늘 → 중간 → 햇빛 받는 쪽 차례로 겹쳐 얹는다. 난수는 씨앗을 고정해 어느 페이지에서나 같은 나무가 나온다.
    var seed = +(/[?&]seed=(\d+)/.exec(location.search) || [0, 3])[1];   // 씨앗 11번 나무(미리 보기: ?seed=숫자)
    function rnd() { seed = seed + 0x6D2B79F5 | 0; var t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }
    function r2(a, b) { return a + rnd() * (b - a); }
    function f(n) { return n.toFixed(1); }
    var limbs = [], tips = [], nodes = [];
    function grow(x, y, ang, len, w, depth) {
      if (ang > 1.3) ang = 1.3; if (ang < -1.3) ang = -1.3;
      var bend = depth === 4 ? 0.34 : r2(-0.34, 0.34), x2 = x + Math.sin(ang) * len, y2 = y - Math.cos(ang) * len;
      var mx = (x + x2) / 2 + Math.cos(ang) * bend * len * 0.5, my = (y + y2) / 2 + Math.sin(ang) * bend * len * 0.5;
      limbs.push({ d: 'M' + f(x) + ' ' + f(y) + 'Q' + f(mx) + ' ' + f(my) + ' ' + f(x2) + ' ' + f(y2), w: w });
      if (depth <= 1) tips.push([x2, y2]);
      if (depth >= 1 && depth <= 3) nodes.push([x2, y2, ang]);
      if (depth === 0) return;
      var n = depth === 4 ? 3 : 2, i, a;
      for (i = 0; i < n; i++) {
        a = ang + (i - (n - 1) / 2) * r2(0.55, 0.95) + r2(-0.24, 0.24);
        grow(x2, y2, a, len * r2(0.6, 0.84), Math.max(0.45, w * 0.58), depth - 1);
      }
    }
    grow(25.5, 50, -0.2, 14, 4, 4);   // 19:30 지시(고목처럼 고독하게): 굵고 한쪽으로 기운 줄기, 들쭉날쭉 뻗은 가지, 성긴 잎

    var PAL = {
      spring: { dark: ['#e38fa8', '#e9a3b7'], mid: ['#f3bccb', '#f6c9d5'], light: ['#fbe1e8', '#fff3f6'], n: 5, r: [1.1, 1.9], R: 3.9, o: 0.96 },
      summer: { dark: ['#3f6a3d', '#4a7745'], mid: ['#5d8c4f', '#6b9a59'], light: ['#86b06c', '#a2c684'], n: 6, r: [1.4, 2.3], R: 3.9, o: 1 },
      autumn: { dark: ['#8f3423', '#a8432b'], mid: ['#c4553a', '#d67a33', '#cf6a35'], light: ['#e0a03f', '#e8bd57'], n: 5, r: [1.3, 2.1], R: 3.8, o: 1 }
    };
    var FLIP = '<g transform="translate(48 0) scale(-1 1)">';   // 줄기가 이름 반대쪽(오른쪽)으로 기울도록 좌우를 뒤집어 그린다
    var bark = '#5c4434', barkLight = '#836651', k, j, L;
    var h = '<path d="M1 50.9H47" fill="none" stroke="rgba(60,45,35,0.22)" stroke-width="0.5" stroke-linecap="round"/>';   // 빈 들판의 지평선 한 줄
    var body = '<path d="M20.2 50.9Q23.4 49.4 23 44.5L27 44.5Q27.2 49.4 30.6 50.9Z" fill="' + bark + '"/>';
    for (k = 0; k < limbs.length; k++) { L = limbs[k]; body += '<path d="' + L.d + '" fill="none" stroke="' + bark + '" stroke-width="' + f(L.w) + '" stroke-linecap="round"/>'; }
    body += '<path d="M24.6 49.6C24.3 46.5 24 44 23.2 41" fill="none" stroke="' + barkLight + '" stroke-width="0.8" stroke-linecap="round" opacity="0.75"/><ellipse cx="25.4" cy="43.6" rx="0.75" ry="1.05" fill="#3f2e23"/>';

    if (season === 'winter') {
      var sh = '', sn = '', x, y, rx, ry;
      for (k = 0; k < nodes.length; k++) {
        if (rnd() < 0.18) continue;
        x = nodes[k][0] + r2(-0.6, 0.6); y = nodes[k][1] - 0.9; rx = r2(2.1, 3.4); ry = rx * r2(0.42, 0.58);
        sh += '<ellipse cx="' + f(x) + '" cy="' + f(y + 0.55) + '" rx="' + f(rx + 0.35) + '" ry="' + f(ry + 0.3) + '"/>';
        sn += '<ellipse cx="' + f(x) + '" cy="' + f(y) + '" rx="' + f(rx) + '" ry="' + f(ry) + '"/>';
      }
      for (k = 0; k < tips.length; k++) {
        if (rnd() < 0.45) continue;
        x = tips[k][0]; y = tips[k][1] - 0.4; rx = r2(1.1, 1.8);
        sh += '<ellipse cx="' + f(x) + '" cy="' + f(y + 0.45) + '" rx="' + f(rx + 0.3) + '" ry="' + f(rx * 0.6 + 0.25) + '"/>';
        sn += '<ellipse cx="' + f(x) + '" cy="' + f(y) + '" rx="' + f(rx) + '" ry="' + f(rx * 0.6) + '"/>';
      }
      h += FLIP + body + '<g fill="#b4c3d3">' + sh + '</g><g fill="#f6f9fc">' + sn + '</g></g>';
      h += '<path d="M10.5 50.7Q17 46.6 24 47.6Q31.5 46.4 37.5 50.7Z" fill="#f6f9fc" stroke="#b4c3d3" stroke-width="0.7" stroke-linejoin="round"/>';
      h += '<g fill="#b4c3d3"><circle cx="5.5" cy="33" r="0.9"/><circle cx="43" cy="30" r="1"/><circle cx="40" cy="42" r="0.75"/><circle cx="8.5" cy="43" r="0.75"/></g>';
    } else {
      var P = PAL[season], lay = { dark: '', mid: '', light: '' }, ang2, dist, px, py, sc, tone, col, rr;
      for (k = 0; k < tips.length; k++) {
        if (rnd() < 0.22) continue;   // 잎이 없는 잔가지도 남김
        for (j = 0; j < P.n; j++) {
          ang2 = r2(0, 6.283); dist = Math.sqrt(rnd()) * P.R;
          px = tips[k][0] + Math.cos(ang2) * dist; py = tips[k][1] + Math.sin(ang2) * dist * 0.85 - 0.8;
          sc = (py - 19) / 14 * 0.85 + (px - 24) / 20 * 0.18 + r2(-0.6, 0.6);   // 아래·오른쪽일수록 그늘, 위·왼쪽일수록 햇빛
          tone = sc > 0.4 ? 'dark' : sc < -0.3 ? 'light' : 'mid';
          col = P[tone][Math.floor(rnd() * P[tone].length)]; rr = r2(P.r[0], P.r[1]);
          lay[tone] += '<ellipse cx="' + f(px) + '" cy="' + f(py) + '" rx="' + f(rr) + '" ry="' + f(rr * r2(0.62, 0.9)) + '" fill="' + col + '" transform="rotate(' + Math.round(r2(-60, 60)) + ' ' + f(px) + ' ' + f(py) + ')"/>';
        }
      }
      h += '<g class="season-tree-top">' + FLIP + body + '<g opacity="' + P.o + '">' + lay.dark + lay.mid + lay.light + '</g></g></g>';
      if (season === 'spring') h += '<g fill="#efaec0"><ellipse cx="43.5" cy="34" rx="1.4" ry="0.9" transform="rotate(-30 43.5 34)"/><ellipse cx="5" cy="39" rx="1.3" ry="0.85" transform="rotate(25 5 39)"/><ellipse cx="35" cy="49.8" rx="1.4" ry="0.75"/><ellipse cx="14" cy="50.1" rx="1.2" ry="0.65"/><ellipse cx="30" cy="50.5" rx="1.1" ry="0.6" fill="#f6c9d5"/></g>';
      if (season === 'autumn') h += '<g><ellipse cx="43.5" cy="36" rx="1.6" ry="1" fill="#d67a33" transform="rotate(-35 43.5 36)"/><ellipse cx="5" cy="41" rx="1.5" ry="0.95" fill="#c4553a" transform="rotate(30 5 41)"/><ellipse cx="34" cy="49.9" rx="1.7" ry="0.85" fill="#e0a03f"/><ellipse cx="15" cy="50.1" rx="1.5" ry="0.8" fill="#c4553a"/><ellipse cx="29.5" cy="50.5" rx="1.3" ry="0.7" fill="#d67a33"/><ellipse cx="19" cy="50.6" rx="1.1" ry="0.6" fill="#e8bd57"/></g>';
    }
    var st = document.createElement('style');
    st.textContent =
      '.top .brand{position:relative}' +
      '.season-tree{position:absolute;left:100%;top:0.16rem;height:calc(100% - 0.21rem);width:auto;margin-left:0.45rem;overflow:visible;pointer-events:none}' +
      '.season-tree-top{transform-box:view-box;transform-origin:50% 100%;animation:season-tree-sway 7s ease-in-out infinite alternate}' +
      '@keyframes season-tree-sway{from{transform:rotate(-0.9deg)}to{transform:rotate(0.9deg)}}' +
      '@media (max-width:760px){.season-tree{top:0.1rem;height:calc(100% - 0.15rem);margin-left:0.35rem}}' +
      '@media (prefers-reduced-motion:reduce){.season-tree-top{animation:none}}' +
      '@media print{.season-tree{display:none}}';
    document.head.appendChild(st);
    var box = document.createElement('span');
    box.innerHTML = '<svg class="season-tree" viewBox="0 0 48 52" aria-hidden="true" focusable="false">' + h + '</svg>';
    var tree = brand.appendChild(box.firstChild), y0 = 1.2;
    // 19:30 지시(이름 글씨와 나무의 높이 맞춤): 그림 틀(viewBox)을 나무 꼭대기 ~ 땅 줄에 딱 맞게 잘라, 나무 꼭대기는 '부효준' 글자 윗선에, 땅 줄은 BOO HYOEJUNE 글자 아랫선에 오게 한다(CSS 의 top·height).
    try { var bb = tree.querySelector('g[transform]').getBBox(); if (bb && bb.height) y0 = bb.y - 0.2; } catch (e) {}
    tree.setAttribute('viewBox', '2 ' + y0.toFixed(1) + ' 52 ' + (51.2 - y0).toFixed(1));
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
