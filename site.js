// 변호사 부효준 홈페이지 — 공용 스크립트 (2026. 10. 23. 저녁: index.html 안에 있던 스크립트를 항목별 페이지(career·fields·faq·press·contact)와 함께 쓰려고 뺌)
// 루트의 여섯 페이지가 <script src="site.js?v=해시"> 로 읽는다(해시는 work/build_pages.py 가 넣음). 각 덩어리는 그 페이지에 해당 요소가 없으면 조용히 건너뛴다.
// cases.html 과 사례·주제 페이지는 저마다의 스크립트를 쓴다.
document.documentElement.lang = 'ko';

// 바닥글 서명 날짜(2026. 10. 23.): 빌드 때 적힌 날짜를 서버가 알려 주는 이 파일의 마지막 수정 시각(Last-Modified)으로 맞춘다.
// 서버가 그 시각을 주지 않으면 document.lastModified 가 '지금'이 되므로(2분 안), 그때는 적힌 날짜를 그대로 둔다.
(function () {
  var t = document.getElementById('sign-date'); if (!t) return;
  var lm = Date.parse(document.lastModified); if (!lm || Math.abs(Date.now() - lm) < 120000) return;
  var d = new Date(lm), iso = d.getFullYear() + '-' + ('0' + (d.getMonth() + 1)).slice(-2) + '-' + ('0' + d.getDate()).slice(-2);
  if (iso <= (t.getAttribute('datetime') || '')) return;
  t.setAttribute('datetime', iso); t.textContent = d.getFullYear() + '. ' + (d.getMonth() + 1) + '. ' + d.getDate() + '.';
})();

// ---------- 떠오르기 (2026. 10. 23.) ----------
// 효과 블록 ②의 .reveal/.in을 붙이고 떼는 쪽. add(요소들, 아래만): "지금 화면 아래에 있는 것"에만 .reveal을 붙이므로 처음 보이는 부분은
// 깜박이지 않고, 스크립트가 없는 환경(검색 로봇·AI)에서는 모두 그대로 보인다. 화면에 들어오면(IntersectionObserver) .in을 붙여 떠오르게 하고,
// 한 번에 들어온 여러 개는 70ms 간격(--d)으로 차례로; 전환이 끝나면 두 클래스를 떼어 보통 상태로 돌려놓는다. 페이지 맨 아래에 닿으면 남은 것을 모두 보인다.
// collect(절, 모음): 절 안에서 떠오를 단위를 고른다 — 격자(.case-list·.situations·.advisors·.finder-list·.certs·.faq)는 칸마다, 묶음(.section-body·.block·.pair…)은 안으로 들어가고, 그 밖은 덩어리째.
var FX = (function () {
  var ok = 'IntersectionObserver' in window && !(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var pending = [];
  function finish(el) {
    var i = pending.indexOf(el); if (i >= 0) pending.splice(i, 1);
    el.classList.remove('reveal', 'in'); el.style.removeProperty('--d');
  }
  function show(el, k) {
    io.unobserve(el);
    el.style.setProperty('--d', (Math.min(k, 6) * 70) + 'ms');
    el.classList.add('in');
    var done = false;
    function end(e) { if (e && e.target !== el) return; if (done) return; done = true; el.removeEventListener('transitionend', end); finish(el); }
    el.addEventListener('transitionend', end);
    setTimeout(end, 1500);
  }
  var io = ok ? new IntersectionObserver(function (entries) {
    var k = 0;
    entries.forEach(function (en) { if (en.isIntersecting) show(en.target, k++); });
  }, { rootMargin: '0px 0px -4% 0px', threshold: 0 }) : null;
  if (ok) window.addEventListener('scroll', function () {
    if (pending.length && window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) pending.slice().forEach(function (el, k) { show(el, k); });
  }, { passive: true });
  var GRIDS = '.case-list, .situations, .advisors, .finder-list, .certs, .areas, .faq';
  var CONTAINERS = '.section-body, .block, .pair, .pair > div, .past-wrap, .gallery, .contact, .section-body > div:not([class])';
  function collect(node, out) {
    Array.prototype.forEach.call(node.children, function (c) {
      if (c.hidden || c.matches('script, style, template, .visually-hidden, .lightbox')) return;
      if (c.matches(GRIDS)) Array.prototype.forEach.call(c.children, function (it) { if (!it.hidden) out.push(it); });
      else if (c.matches(CONTAINERS)) collect(c, out);
      else out.push(c);
    });
  }
  function add(els, onlyBelow) {
    if (!ok) return;
    var h = window.innerHeight;
    Array.prototype.forEach.call(els, function (el) {
      if (el.classList.contains('reveal')) return;
      if (onlyBelow && el.getBoundingClientRect().top < h) return;
      el.classList.add('reveal'); pending.push(el); io.observe(el);
    });
  }
  return { ok: ok, collect: collect, add: add };
})();


// Copy buttons appear only next to a real phone number or email (not a ○○ placeholder).
document.querySelectorAll('button[data-copy]').forEach(function (btn) {
  var target = document.getElementById(btn.getAttribute('data-copy'));
  if (!target || /○/.test(target.textContent)) return;
  btn.hidden = false;
  var label = btn.textContent;
  var timer;
  function show(msg) {
    btn.textContent = msg;
    clearTimeout(timer);
    timer = setTimeout(function () { btn.textContent = label; }, 1800);
  }
  function selectText() {
    var range = document.createRange();
    range.selectNodeContents(target);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
    show('선택했습니다');
  }
  btn.addEventListener('click', function () {
    var text = target.textContent.trim();
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { show('복사했습니다'); }, selectText);
    } else {
      selectText();
    }
  });
});

// ---------- lightbox (certificates and judgment images) ----------
var LB = (function () {
  var dlg = document.getElementById('lightbox');
  if (!dlg || typeof dlg.showModal !== 'function') return { open: function () {} };
  var img = document.getElementById('lb-img'), cap = document.getElementById('lb-cap');
  var items = [], index = 0;
  function show(i) {
    index = (i + items.length) % items.length;
    var it = items[index];
    dlg.classList.remove('tall');
    img.onload = function () { dlg.classList.toggle('tall', img.naturalHeight > img.naturalWidth * 1.6); var sc = document.getElementById('lb-scroll'); if (sc) sc.scrollTop = 0; };
    img.src = it.src;
    img.alt = it.alt || '';
    cap.textContent = '';
    var b = document.createElement('b'); b.textContent = it.title || ''; cap.appendChild(b);
    cap.appendChild(document.createTextNode((it.sub || '') + '  (' + (index + 1) + '/' + items.length + ')'));
  }
  function open(list, i) {
    if (!list || !list.length) return;
    items = list; show(i || 0);
    if (!dlg.open) dlg.showModal();
  }
  document.getElementById('lb-prev').addEventListener('click', function () { show(index - 1); });
  document.getElementById('lb-next').addEventListener('click', function () { show(index + 1); });
  document.getElementById('lb-close').addEventListener('click', function () { dlg.close(); });
  dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  dlg.addEventListener('keydown', function (e) {
    if (e.key === 'ArrowLeft') show(index - 1);
    if (e.key === 'ArrowRight') show(index + 1);
  });
  dlg.addEventListener('close', function () { img.src = ''; });
  return { open: open };
})();

// certificates: one gallery across both cert grids
(function () {
  var figs = Array.prototype.slice.call(document.querySelectorAll('.cert'));
  var items = figs.map(function (f) {
    var b = f.querySelector('button'), i = f.querySelector('img'), c = f.querySelector('figcaption');
    var term = c ? Array.prototype.map.call(c.querySelectorAll('span'), function (sp) { return sp.textContent; }).join(' ') : '';
    return { key: b.getAttribute('data-cert'), src: 'certs/' + b.getAttribute('data-cert') + '.jpg', alt: i.getAttribute('alt'), title: c && c.firstElementChild ? c.firstElementChild.textContent : '', sub: term };
  });
  document.querySelectorAll('button[data-cert]').forEach(function (b) {
    b.addEventListener('click', function () {
      var key = b.getAttribute('data-cert');
      var i = items.findIndex(function (it) { return it.key === key; });
      LB.open(items, i < 0 ? 0 : i);
    });
  });
})();

// advisory tiles: one or more certificates per institution
(function () {
  document.querySelectorAll('button[data-certs]').forEach(function (b) {
    var tile = b.closest('.adv');
    var org = tile && tile.querySelector('.org') ? tile.querySelector('.org').textContent : '';
    var term = tile && tile.querySelector('.term') ? tile.querySelector('.term').textContent : '';
    var first = b.querySelector('img');
    var keys = b.getAttribute('data-certs').split(',').map(function (k) { return k.trim(); }).filter(Boolean);
    var alts = (b.getAttribute('data-alts') || '').split('|').map(function (a) { return a.trim(); });
    var items = keys.map(function (k, i) {
      var alt = alts[i] || (i === 0 && first ? first.getAttribute('alt') : org + ' 위촉장 (' + k.slice(-4) + ')');
      return { key: k, src: 'certs/' + k + '.jpg', alt: alt, title: org, sub: i === 0 ? term : alt };
    });
    b.addEventListener('click', function () { LB.open(items, 0); });
  });
  // 기관 로고 띠(누리집 링크) 클릭 집계 (2026. 10. 21.)
  document.querySelectorAll('a.adv-logo, a.lec-logo').forEach(function (a) {
    a.addEventListener('click', function () { track('logo_click', { org: a.getAttribute('data-org') || '' }); });
  });
})();

// ---------- online accounts ----------
(function () {
  var links = [];
  try { links = JSON.parse(document.getElementById('links-data').textContent) || []; } catch (e) { links = []; }
  links = links.filter(function (l) { return l && /^https?:\/\//i.test(l.url || ''); });
  var SVG = 'http://www.w3.org/2000/svg';
  function icon(name) {
    name = name || 'blog';
    // A symbol carrying data-brand is a service's own mark: it fills the tile as drawn ("edge" adds a hairline around it).
    var sym = document.getElementById('i-' + name);
    var brand = sym ? sym.getAttribute('data-brand') : null;
    var svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('aria-hidden', 'true');
    var use = document.createElementNS(SVG, 'use');
    use.setAttribute('href', '#i-' + name);
    svg.appendChild(use);
    var wrap = document.createElement('span');
    wrap.className = 'ico' + (brand === null ? '' : ' brand' + (brand === 'edge' ? ' edge' : ''));
    wrap.appendChild(svg);
    return wrap;
  }
  [['sns-hero', false], ['sns-contact', true], ['sns-footer', false]].forEach(function (cfg) {
    var box = document.getElementById(cfg[0]);
    if (!box) return;
    links.forEach(function (l) {
      var a = document.createElement('a');
      a.href = l.url; a.rel = 'noopener'; a.target = '_blank';
      a.setAttribute('aria-label', l.name + (l.handle ? ' ' + l.handle : '') + ' (새 창)');
      a.appendChild(icon(l.icon));
      var label = document.createElement('span'); label.textContent = l.name; a.appendChild(label);
      if (cfg[1] && l.handle) { var sm = document.createElement('small'); sm.textContent = l.handle; a.appendChild(sm); }
      box.appendChild(a);
    });
  });
})();

// ---------- online consultation form (FormSubmit → boo@keumseonglaw.com) ----------
(function () {
  var form = document.getElementById('consult-form');
  if (!form) return;
  var status = document.getElementById('q-status'), btn = document.getElementById('q-send');
  var F = function (id) { return document.getElementById(id); };
  var MAIL = 'boo@keumseonglaw.com';
  var DONE = '상담 신청이 접수되었습니다. 확인한 뒤 연락드리겠습니다.';
  if (/[?&]sent=1/.test(location.search)) {
    status.textContent = DONE;
    try { history.replaceState(null, '', location.pathname + '#contact'); } catch (e) {}
  }
  function subject() { return '[홈페이지 상담 신청] ' + F('q-cat').value + ' · ' + F('q-name').value.trim(); }
  function body() {
    return ['상담 분야: ' + F('q-cat').value, '성함: ' + F('q-name').value.trim(), '연락처: ' + F('q-phone').value.trim(), '이메일: ' + F('q-email').value.trim(), '', F('q-msg').value.trim(), '', '개인정보 수집·이용 동의: 동의함'].join('\n');
  }
  function fallback(msg) {
    status.textContent = '';
    status.appendChild(document.createTextNode(msg || '바로 전송되지 않았습니다. '));
    var a = document.createElement('a');
    a.href = 'mailto:' + MAIL + '?subject=' + encodeURIComponent(subject()) + '&body=' + encodeURIComponent(body());
    a.textContent = '이메일 앱으로 보내기';
    status.appendChild(a);
    status.appendChild(document.createTextNode(' 또는 02-588-8685로 연락해 주십시오.'));
  }
  form.addEventListener('submit', function (ev) {
    var missing = [];
    if (!F('q-name').value.trim()) missing.push(['q-name', '성함']);
    if (!F('q-phone').value.trim()) missing.push(['q-phone', '연락처']);
    if (!F('q-msg').value.trim()) missing.push(['q-msg', '문의 내용']);
    if (!F('q-agree').checked) missing.push(['q-agree', '개인정보 수집·이용 동의']);
    if (missing.length) {
      ev.preventDefault();
      status.textContent = missing.map(function (m) { return m[1]; }).join(', ') + '을(를) 확인해 주십시오.';
      F(missing[0][0]).focus();
      return;
    }
    var file = F('q-file').files && F('q-file').files[0];
    if (file && file.size > 10 * 1024 * 1024) { ev.preventDefault(); status.textContent = '첨부파일은 10MB 이내여야 합니다.'; return; }
    track('contact_click', { method: '상담 신청' });
    if (!window.fetch || !window.FormData) return;   // 구형 브라우저는 일반 전송(FormSubmit 확인 페이지를 거쳐 돌아옵니다)
    ev.preventDefault();
    btn.disabled = true; status.textContent = '보내는 중…';
    var fd = new FormData(form);
    fd.set('_subject', subject()); fd.delete('_next');
    if (!file) fd.delete('attachment');
    fetch('https://formsubmit.co/ajax/' + MAIL, { method: 'POST', body: fd, headers: { 'Accept': 'application/json' } })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j || {} }; }); })
      .then(function (res) {
        if (res.ok && String(res.j.success) === 'true') { form.reset(); status.textContent = DONE; return; }
        var m = String(res.j.message || '');
        if (/activ/i.test(m)) fallback('이 신청서는 아직 수신 확인(활성화) 전입니다. ');
        else fallback();
      })
      .catch(function () { fallback(); })
      .then(function () { btn.disabled = false; });
  });
})();

// ---------- case board ----------
(function () {
  var DATA_ID = 'cases-data';
  var CATS = { rnd: '국가연구개발 제재처분', penalty: '제재부가금·환수', personnel: '공무원·교원 인사처분', license: '인허가·면허·자격 처분', comp: '손실보상', admin: '그 밖의 행정처분', criminal: '형사', contract: '국가계약법·지방계약법', state: '국가배상', civil: '민사' };   // 2026. 10. 21. 이름·순서를 '다루는 사건' 카드와 맞춤(형사는 출연금·보조금 외 사건도 있어 '형사'로, 민사는 카드가 없어 맨 뒤)
  var RECENT = 9;   // 홈 화면의 사례 수(2026. 10. 21.): 세 장씩 놓이는 넓은 화면은 9건, 두 장씩 놓이는 화면(1000px 이하)은 CSS가 아홉째 장을 감춰 8건
  var MAIN = ['rnd', 'penalty', 'criminal']; // 홈 화면이 먼저 보이는 세 분야 (Version 90)
  var WHO = '담당변호사 부효준'; // 모든 사례에 적는 담당변호사 (Version 111)
  function bySortDesc(a, b) { return (b.sort || '') < (a.sort || '') ? -1 : (b.sort || '') > (a.sort || '') ? 1 : 0; }
  var cases = [];
  // 사례 데이터는 외부 파일 cases-data.js(window.CASES_DATA; 2026. 10. 23. 인라인 JSON 블록에서 분리)에서; 옛 인라인 블록이 있으면 그것을 읽는다
  try { cases = Array.isArray(window.CASES_DATA) ? window.CASES_DATA : (JSON.parse(document.getElementById(DATA_ID).textContent) || []); } catch (e) { cases = []; }

  // 분야 카드 맨 아래 '주요 수행 사례 N건 →' 단추의 건수 (Version 87)
  Array.prototype.forEach.call(document.querySelectorAll('.cases-link[data-cat]'), function (a) {
    var cat = a.getAttribute('data-cat'), n = 0;
    cases.forEach(function (c) { if (c.cat === cat) n++; });
    var el = a.querySelector('.n');
    if (el && n) el.textContent = n + '건';
  });
  var fc = document.getElementById('find-count'); if (fc && cases.length) fc.textContent = String(cases.length);

  var state = { filter: 'main' };
  var listEl = document.getElementById('case-list');
  if (!listEl) return;   // 카드 목록이 없는 페이지(경력·다루는 사건 등 — 2026. 10. 23. 저녁 항목별 페이지)에서는 여기까지(분야 건수·찾기 건수만 채움)
  var chipsEl = document.getElementById('chips');
  var allLink = document.getElementById('all-cases');
  var emptyEl = document.getElementById('case-empty');

  function pageHref(c) { var im = (Array.isArray(c.images) ? c.images : []).filter(function (im) { return im && im.src; })[0]; var stem = im ? String(im.src).replace(/^.*\//, '').replace(/\.[A-Za-z0-9]+$/, '') : c.id; return 'cases/' + stem + '.html'; }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function renderChips() {
    if (!chipsEl) return;
    chipsEl.textContent = '';
    var counts = {};
    cases.forEach(function (c) { counts[c.cat] = (counts[c.cat] || 0) + 1; });
    var keys = ['main', 'all'].concat(Object.keys(CATS).filter(function (k) { return counts[k]; }));
    if (state.filter !== 'all' && state.filter !== 'main' && !counts[state.filter]) state.filter = 'main';
    keys.forEach(function (k) {
      var b = el('button', 'chip', k === 'main' ? '주요 분야' : k === 'all' ? '전체' : CATS[k]);
      if (k === 'main') b.title = '국가연구개발 제재처분 · 제재부가금·환수 · 형사';
      b.type = 'button';
      b.id = 'chip-' + k;
      b.setAttribute('role', 'tab');
      b.setAttribute('aria-selected', String(state.filter === k));
      b.addEventListener('click', function () { state.filter = k; track('case_filter', { filter: k === 'main' ? '주요 분야' : k === 'all' ? '전체' : (CATS[k] || k) }); render(true); });
      chipsEl.appendChild(b);
    });
  }

  var SVGNS = 'http://www.w3.org/2000/svg';
  function docGlyph() {
    var svg = document.createElementNS(SVGNS, 'svg');
    svg.setAttribute('viewBox', '0 0 32 32'); svg.setAttribute('aria-hidden', 'true');
    ['M8 3h11l6 6v20H8z', 'M19 3v6h6', 'M12 15h8M12 19h8M12 23h5'].forEach(function (d) {
      var path = document.createElementNS(SVGNS, 'path'); path.setAttribute('d', d); svg.appendChild(path);
    });
    return svg;
  }


  function badgeClass(r) { r = r || ''; return r.indexOf('일부승소') === 0 ? 'part' : r.indexOf('승소') === 0 ? 'win' : 'other'; }
  function badge(c) { return c.result ? el('span', 'badge ' + badgeClass(c.result), c.result) : null; }
  function figure(c) {
    var imgs = Array.isArray(c.images) ? c.images.filter(function (im) { return im && im.src; }) : [];
    if (imgs.length) {
      var lbItems = imgs.map(function (im, k) { return { src: im.src, alt: im.alt || (c.title + ' 판결문 ' + (k + 1)), title: c.title, sub: im.alt || '판결문' }; });
      var fig = el('button', 'case-fig'); fig.type = 'button';
      fig.setAttribute('aria-label', c.title + ' 판결문 크게 보기');
      var pic = el('img'); pic.src = imgs[0].thumb || imgs[0].src; pic.alt = imgs[0].alt || (c.title + ' 판결문'); pic.loading = 'lazy'; pic.decoding = 'async';
      fig.appendChild(pic);   // 장수('판결문 N장') 표시는 두지 않는다 (2026. 10. 21.)
      fig.addEventListener('click', function () { track('case_open', { case_title: c.title, case_id: c.id }); LB.open(lbItems, 0); });
      return fig;
    }
    var ph = el('div', 'case-fig none'); ph.setAttribute('aria-hidden', 'true');
    ph.appendChild(docGlyph()); ph.appendChild(el('span', null, CATS[c.cat] || c.cat));
    return ph;
  }
  // 요지는 두 줄까지만 보이고(.clamp), '더 보기' 단추 없이 '자세히 →' 링크 하나로 개별 페이지에 간다 (2026. 10. 21.)
  function card(c) {
    var li = el('li', 'case'); li.dataset.cat = c.cat; li.id = 'case-' + c.id;
    li.appendChild(figure(c));
    var body = el('div', 'case-body');
    var meta = el('div', 'case-meta');
    meta.appendChild(el('span', 'tag', CATS[c.cat] || c.cat));
    if (c.date) meta.appendChild(el('span', 'date', c.date));
    var bd = badge(c); if (bd) meta.appendChild(bd);
    if (c.pr) { var pm = el('span', 'pressmark', '언론보도'); pm.title = '이 사건이 보도된 기사 ' + c.pr + '건 — 자세히에서 볼 수 있습니다'; meta.appendChild(pm); }   // press.json (2026. 10. 22.)
    body.appendChild(meta);
    var h3 = el('h3', 'case-title'); var ta = el('a', null, c.title); ta.href = pageHref(c); h3.appendChild(ta); body.appendChild(h3);
    var parts = [c.court, c.party].filter(Boolean);
    var sub = el('p', 'case-sub', parts.length ? parts.join(' · ') + ' · ' : ''); sub.appendChild(el('span', 'who', WHO)); body.appendChild(sub);
    if (c.summary) body.appendChild(el('p', 'case-summary clamp', c.summary));
    var pa = el('a', 'case-link', '자세히 →'); pa.href = pageHref(c); body.appendChild(pa);
    li.appendChild(body);
    return li;
  }

  function renderList() {
    listEl.textContent = '';
    var shown = cases.filter(function (c) { return state.filter === 'all' || (state.filter === 'main' ? MAIN.indexOf(c.cat) >= 0 : c.cat === state.filter); });
    // 최근 결정일 순으로 정렬하고, 홈 화면에는 최근 9건(두 장씩 놓이는 화면에서는 8건)만 보입니다(전체는 cases.html, 최근 순).
    shown = shown.map(function (c, i) { return [c, i]; })
      .sort(function (a, b) { return bySortDesc(a[0], b[0]) || a[1] - b[1]; })
      .map(function (t) { return t[0]; });
    shown = shown.slice(0, RECENT);
    if (allLink) {
      var whole = state.filter === 'all' || state.filter === 'main';
      allLink.textContent = whole ? '주요 수행 사례 전체 보기 (최근 순)' : (CATS[state.filter] || '') + ' 사례 전체 보기';
      allLink.href = whole ? 'cases.html' : 'cases.html#cat=' + state.filter;
    }
    emptyEl.hidden = shown.length > 0;
    shown.forEach(function (c) { listEl.appendChild(card(c)); });
  }

  function render(animate) { renderChips(); renderList(); FX.add(listEl.children, !animate); }   // 칩을 눌러 바뀐 카드는 화면 안의 것도 떠오르고(animate), 처음 그릴 때는 화면 아래의 것만 (2026. 10. 23.)
  render();
})();
// 2026. 10. 16. (Version 69): 머리글 차림표 — 지금 보고 있는 절의 링크에 .current, 스크롤하면 머리글 아래에 선(.stuck),
// 머리글이 위에 붙는 화면에서는 앵커 이동이 머리글에 가려지지 않도록 scroll-padding-top을 머리글 높이에 맞춘다.
(function () {
  var top = document.querySelector('header.top');
  if (!top) return;
  var links = Array.prototype.slice.call(top.querySelectorAll('nav a[href^="#"]:not(.btn)'));
  var targets = links.map(function (a) { return a.getAttribute('href').slice(1); });
  var secs = Array.prototype.slice.call(document.querySelectorAll('section[id]')).filter(function (s) { return targets.indexOf(s.id) >= 0; });
  var ticking = false;
  function update() {
    ticking = false;
    var sticky = getComputedStyle(top).position === 'sticky';
    top.classList.toggle('stuck', sticky && window.scrollY > 4);
    document.documentElement.style.scrollPaddingTop = sticky ? (top.offsetHeight + 8) + 'px' : '';
    var totop = document.getElementById('totop');
    if (totop) totop.classList.toggle('show', window.scrollY > window.innerHeight * 1.2);
    var line = (sticky ? top.offsetHeight : 0) + window.innerHeight * 0.3;
    var cur = null;
    secs.forEach(function (s) { if (s.getBoundingClientRect().top <= line) cur = s.id; });
    if (window.scrollY < 80) cur = null;
    links.forEach(function (a) { a.classList.toggle('current', a.getAttribute('href') === '#' + cur); });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll);
  window.addEventListener('load', update);
  update();
})();
// 2026. 10. 16. (Version 71·75): 주요 수행 사례의 찾기 칸 — 단어을 들고 전체 사례 페이지로 가서 모든 분야에서 찾는다.
(function () {
  var form = document.getElementById('find-form'), q = document.getElementById('find-q');
  if (!form || !q) return;
  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var term = q.value.trim();
    // 단어 찾기는 고른 분야와 상관없이 언제나 전체 사례에서 찾는다(Version 75).
    location.href = 'cases.html' + (term ? '#q=' + encodeURIComponent(term) : '');
  });
  Array.prototype.forEach.call(form.querySelectorAll('.preset'), function (b) {
    b.addEventListener('click', function () { location.href = 'cases.html#q=' + encodeURIComponent(b.getAttribute('data-q')); });
  });
})();

// ---------- 연락 단추 집계 (Version 116) ----------
document.addEventListener('click', function (e) {
  var a = e.target && e.target.closest ? e.target.closest('a[href]') : null; if (!a) return;
  var h = a.getAttribute('href') || '', method = '';
  if (/^tel:/i.test(h)) method = h.indexOf('588') >= 0 ? '사무실 전화' : '휴대전화';
  else if (/^mailto:/i.test(h)) method = '이메일';
  else if (/map\.naver\.com/i.test(h)) method = '네이버 지도';
  else if (/google\.com\/maps/i.test(h)) method = '구글 지도';
  else if (a.closest('.sns')) { var lbl = a.querySelector('span:not(.ico)'); method = (lbl && lbl.firstChild ? lbl.firstChild.textContent : a.textContent).trim(); }
  if (method) track('contact_click', { method: method });
}, true);

// ---------- 홈에서 본 부분 집계 (Version 116) ----------
(function () {
  if (!('IntersectionObserver' in window)) return;
  var names = { record: '주요 수행 사례', career: '경력', fields: '다루는 사건', faq: '자주 묻는 질문', contact: '상담 문의' };   // 2026. 10. 21. '국가연구개발 제재처분' 절(rnd)은 없앰
  var seen = {};
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (en) { if (en.isIntersecting && !seen[en.target.id]) { seen[en.target.id] = 1; track('section_view', { section: names[en.target.id] }); } });
  }, { threshold: 0, rootMargin: '-40% 0px -40% 0px' });
  Object.keys(names).forEach(function (id) { var s = document.getElementById(id); if (s) io.observe(s); });
})();


// ---------- 분야 카드 아무 곳을 눌러도 그 분야 사례로 (Version 120) ----------
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('.situation'), function (card) {
    var link = card.querySelector('a.cases-link'); if (!link) return;
    card.classList.add('linked');
    card.addEventListener('click', function (e) {
      if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (e.target.closest && e.target.closest('a, button')) return;   // 카드 안의 다른 링크·단추는 제 몫대로
      if (String(window.getSelection && window.getSelection()).length) return;   // 글자를 긁는 중이면 그대로
      track('case_filter', { filter: (link.querySelector('.lbl') || link).textContent.replace(/\s+/g, ' ').trim() + ' (카드)' });
      location.href = link.href;
    });
  });
})();


// ---------- 휴대전화의 '다루는 사건' 카드 접기 (2026. 10. 23. 낮, 길이 줄이기) ----------
// 640px 이하에서는 카드마다 설명을 네 줄까지만 보이고 '다룬 사건'·근거 법령은 접어 두며(.fold, home.css), '더 보기' 단추로 펼친다(.open).
// 국가연구개발 카드의 세 기한은 접지 않는다. 스크립트가 없는 환경(검색 로봇·AI)과 넓은 화면에서는 모두 펼쳐 보인다.
// 카드 아무 곳을 눌러도 사례로 가는 동작(위 블록)은 단추 위에서는 일어나지 않는다(a, button 제외).
(function () {
  Array.prototype.forEach.call(document.querySelectorAll('.situation'), function (card) {
    var btn = document.createElement('button'); btn.type = 'button'; btn.className = 'situation-more';
    btn.setAttribute('aria-expanded', 'false'); btn.textContent = '더 보기';
    card.insertBefore(btn, card.querySelector('a.cases-link'));
    card.classList.add('fold');
    btn.addEventListener('click', function () {
      var open = card.classList.toggle('open');
      btn.setAttribute('aria-expanded', String(open));
      btn.textContent = open ? '접기' : '더 보기';
    });
  });
})();

// ---------- '단어로 찾기'로 가는 링크는 입력칸에 커서를 둔다 (Version 122) ----------
(function () {
  var q = document.getElementById('find-q'); if (!q) return;
  Array.prototype.forEach.call(document.querySelectorAll('a[href="#find-form"]'), function (a) {
    a.addEventListener('click', function () { setTimeout(function () { try { q.focus({ preventScroll: true }); } catch (e) { q.focus(); } }, 450); });
  });
})();

// ---------- 떠오르기 대상 고르기 (2026. 10. 23.) ----------
// 첫 화면은 CSS 애니메이션으로 따로 떠오르므로 뺀다. 길잡이·각 절은 FX.collect로 단위를 나누고, '위치 | 연락처' 띠와 바닥글은 덩어리째.
(function () {
  if (!FX.ok) return;
  var out = [];
  Array.prototype.forEach.call(document.querySelectorAll('main > *'), function (c) {
    if (c.matches('.hero')) return;
    if (c.matches('.finder, .section')) FX.collect(c, out); else out.push(c);
  });
  Array.prototype.forEach.call(document.querySelectorAll('.quick, footer.sign'), function (c) { out.push(c); });
  FX.add(out, true);
})();
