// Thu spec UI THẬT của trang web — cùng định dạng với figma_extract.js để dc.py so được.
// Chạy bằng Playwright MCP: đọc file này, truyền NGUYÊN VĂN vào `browser_evaluate` (tham số `function`),
// hoặc `page.evaluate(<nội dung>)` trong browser_run_code_unsafe. Ghi kết quả ra reports/design-compare/<run>/actual_<màn>.json.
//
// Đơn vị: CSS px. `rect` = [x, y, w, h] tính từ góc trái-trên của TÀI LIỆU (đã cộng scroll) — khớp với khung Figma vẽ toàn trang.
// Muốn so một vùng (dialog, card) thay vì cả trang: đặt ROOT_SELECTOR, toạ độ sẽ tính từ góc của phần tử đó.
() => {
  const ROOT_SELECTOR = null;           // VD '[role=dialog]' — null = cả trang
  const root = ROOT_SELECTOR ? document.querySelector(ROOT_SELECTOR) : document.documentElement;
  const rb = root.getBoundingClientRect();
  const ox = ROOT_SELECTOR ? rb.left : -window.scrollX, oy = ROOT_SELECTOR ? rb.top : -window.scrollY;
  const toHex = (c) => {
    const m = c && c.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
    if (!m) return null;
    const a = m[4] === undefined ? 1 : +m[4];
    if (a === 0) return null;
    const h = v => Math.round(+v).toString(16).padStart(2, '0');
    return '#' + h(m[1]) + h(m[2]) + h(m[3]) + (a < 1 ? '@' + a.toFixed(2) : '');
  };
  const visible = (el, r) => {
    if (r.width < 1 || r.height < 1) return false;
    const s = getComputedStyle(el);
    return s.visibility !== 'hidden' && s.display !== 'none' && +s.opacity > 0.01;
  };
  const rect = (r) => [Math.round(r.left - ox), Math.round(r.top - oy), Math.round(r.width), Math.round(r.height)];
  const sel = (el) => el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.getAttribute('name') ? `[name="${el.getAttribute('name')}"]` : '');
  // Font THỰC SỰ được vẽ = họ đầu tiên trong font-stack có trên máy (computed fontFamily trả cả stack,
  // phần tử đầu như "-apple-system" không có trên Windows). Dò bằng đo chữ trên canvas so với font dự phòng.
  const ctx = document.createElement('canvas').getContext('2d'), probe = 'mmmmmmmmmmlli1WQ@#', usedCache = {};
  const usedFont = (stack) => {
    if (stack in usedCache) return usedCache[stack];
    const fams = stack.split(',').map(f => f.trim().replace(/["']/g, ''));
    const w = (f) => { ctx.font = `72px ${f}`; return ctx.measureText(probe).width; };
    const hit = fams.find(f => /^(serif|sans-serif|monospace|cursive|fantasy|system-ui|ui-\w+)$/.test(f)
      || ['monospace', 'serif'].some(g => w(`"${f}", ${g}`) !== w(g)));
    return (usedCache[stack] = hit || fams[fams.length - 1]);
  };
  const nodes = [];
  const all = root.querySelectorAll('*');
  for (const el of all) {
    if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'SVG', 'PATH'].includes(el.tagName.toUpperCase())) continue;
    const r = el.getBoundingClientRect();
    if (!visible(el, r)) continue;
    const s = getComputedStyle(el);
    const own = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ').replace(/\s+/g, ' ').trim();
    const base = { size: parseFloat(s.fontSize), font: usedFont(s.fontFamily),
      weight: +s.fontWeight, lh: s.lineHeight === 'normal' ? null : parseFloat(s.lineHeight), color: toHex(s.color),
      align: s.textAlign.toUpperCase().replace('START', 'LEFT').replace('END', 'RIGHT'), tag: el.tagName.toLowerCase(), sel: sel(el) };
    if (own) {
      // Đo đúng phần chữ (ink box) bằng Range — rect của phần tử khối thường rộng hơn chữ nhiều
      const range = document.createRange(); range.selectNodeContents(el);
      const tr = range.getBoundingClientRect();
      // chữ bị cắt "…" (text-overflow) hoặc bị khung cha che bớt — dấu hiệu tràn mà ảnh nhỏ khó thấy
      const cut = s.textOverflow === 'ellipsis' && el.scrollWidth > el.clientWidth + 1;
      nodes.push({ k: 'text', text: own, rect: rect(tr.width ? tr : r), ...base, ...(cut ? { cut: true } : {}) });
    } else if (['INPUT', 'TEXTAREA'].includes(el.tagName) && (el.placeholder || el.value)) {
      nodes.push({ k: 'input', text: el.value || el.placeholder, placeholder: !el.value, rect: rect(r), ...base });
    } else if (el.tagName === 'IMG' && el.alt) {
      nodes.push({ k: 'image', text: el.alt, rect: rect(r), tag: 'img', sel: sel(el) });
    }
    const fill = toHex(s.backgroundColor);
    const bw = parseFloat(s.borderTopWidth);
    const stroke = bw > 0 ? toHex(s.borderTopColor) : null;
    if ((fill || stroke) && r.width >= 8 && r.height >= 8 && el !== document.body && el !== document.documentElement) {
      nodes.push({ k: 'box', name: base.sel, rect: rect(r), fill, stroke, strokeW: stroke ? bw : null,
        radius: parseFloat(s.borderTopLeftRadius) || 0, tag: base.tag, sel: base.sel });
    }
  }
  // Bề ngang khung = vùng NHÌN THẤY (clientWidth, đã trừ thanh cuộn dọc) — khung Figma không vẽ thanh cuộn.
  // Trang tràn ngang thì scrollWidth > clientWidth: ghi riêng ở overflow_x, không lấy làm bề ngang (sai phép neo phải/giữa).
  const de = document.documentElement;
  return { source: 'web', url: location.href, overflow_x: ROOT_SELECTOR ? null : Math.max(0, de.scrollWidth - de.clientWidth),
    frame: { name: document.title, w: Math.round(ROOT_SELECTOR ? rb.width : de.clientWidth),
    h: Math.round(ROOT_SELECTOR ? rb.height : document.documentElement.scrollHeight), viewport: [innerWidth, innerHeight], dpr: devicePixelRatio,
    fill: toHex(getComputedStyle(document.body).backgroundColor) }, nodes };
}
