"""dc.py — so thiết kế Figma với UI thật (web · Android · iOS). Bộ công cụ của skill skills-figma-design-comparator.

Mọi bước đều xuất cùng một định dạng "spec JSON":
    {"source": "figma|android|ios|web", "frame": {"w", "h", ...}, "scale": px-ảnh/đơn-vị, "top": status bar, "bottom": thanh điều hướng,
     "nodes": [{"k": "text|input|image|label|box", "text", "rect": [x, y, w, h], "size", "weight", "lh", "color", "fill", ...}]}
Đơn vị: dp (Android) · pt (iOS) · CSS px (web) — cùng đơn vị với Figma nên so thẳng được.

    python scripts/design-compare/dc.py android-tree <page_source.xml> --density 480 --top-px 159 --bottom-px 72 --png <ảnh.png> -o actual.json
    python scripts/design-compare/dc.py ios-tree <page_source.xml> --scale 3 --top 59 --bottom 34 --png <ảnh.png> -o actual.json
    python scripts/design-compare/dc.py match figma.json actual.json -o <thư-mục>/<tên>          # → <tên>.json + <tên>.md
    python scripts/design-compare/dc.py visual figma.png actual.png --design figma.json --actual actual.json -o <thư-mục>/<tên>
    python scripts/design-compare/dc.py render figma.json -o figma_render.png                     # hết lượt ảnh Figma: dựng sơ đồ từ JSON
    python scripts/design-compare/dc.py annotate <tên>.json --png actual.png -o <ảnh_khoanh.png>  # khung đỏ + số DIFF
    python scripts/design-compare/dc.py annotate --png app.png --actual actual.json --text "Create a new book=DIFF-…-08" --rect "16,284,416,58=DIFF-…-02" -o marked.png
    python scripts/design-compare/dc.py sections frames.json -o sections.md                       # mục 4 của báo cáo từ các <mã>_match.md
    python scripts/design-compare/dc.py color <ảnh.png> --rect x,y,w,h [--unit-px 3]           # màu nền + màu chữ trong vùng
    python scripts/design-compare/dc.py mask app.png --actual actual.json --pattern "^0[0-9]{8,10}$" -o app_masked.png  # che dữ liệu cá nhân
    python scripts/design-compare/dc.py deltae "#42bc40" "#43bd41"

Ngưỡng mặc định lấy theo .claude/rules/design_compare_rules.md — đổi bằng --tol / --tol-size / --de-text / --de-fill.
Cần: Python 3.9+ · pip install pillow
"""
import argparse, difflib, html, json, math, re, statistics, sys, unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding='utf-8', errors='replace')

ICON = {'ok': '✅', 'minor': '⚠️', 'diff': '❌', 'missing': '🔍', 'extra': '➕', 'offscreen': '⤵️', 'na': '❔'}
LABEL = {'ok': 'Khớp', 'minor': 'Lệch nhỏ', 'diff': 'Lệch', 'missing': 'Thiếu trên app', 'extra': 'Thừa trên app',
         'offscreen': 'Ngoài màn hình đã chụp', 'na': 'Không so được'}


# ───────────────────────── màu ─────────────────────────
def hex2rgb(h):
    h = h.split('@')[0].lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return '#%02x%02x%02x' % tuple(int(v) for v in c[:3])


def _lab(rgb):
    def lin(v):
        v /= 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(v) for v in rgb)
    x = (r * 0.4124 + g * 0.3576 + b * 0.1805) / 0.95047
    y = r * 0.2126 + g * 0.7152 + b * 0.0722
    z = (r * 0.0193 + g * 0.1192 + b * 0.9505) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(c1, c2):
    """CIEDE2000. ≤1 mắt thường không thấy · 2–3 nhìn kỹ mới thấy · >5 thấy rõ · >10 là màu khác."""
    if isinstance(c1, str): c1 = hex2rgb(c1)
    if isinstance(c2, str): c2 = hex2rgb(c2)
    L1, a1, b1 = _lab(c1); L2, a2, b2 = _lab(c2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cb = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cb ** 7 / (Cb ** 7 + 25 ** 7)))
    a1p, a2p = a1 * (1 + G), a2 * (1 + G)
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h = lambda b, a: math.degrees(math.atan2(b, a)) % 360
    h1p, h2p = h(b1, a1p), h(b2, a2p)
    dLp, dCp = L2 - L1, C2p - C1p
    dhp = 0 if C1p * C2p == 0 else (h2p - h1p if abs(h2p - h1p) <= 180 else h2p - h1p - 360 if h2p > h1p else h2p - h1p + 360)
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    hbp = h1p + h2p if C1p * C2p == 0 else ((h1p + h2p) / 2 if abs(h1p - h2p) <= 180 else (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2)
    T = 1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp)) + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.2 * math.cos(math.radians(4 * hbp - 63))
    SL = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2); SC = 1 + 0.045 * Cbp; SH = 1 + 0.015 * Cbp * T
    RT = -2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hbp - 275) / 25) ** 2)))
    return math.sqrt((dLp / SL) ** 2 + (dCp / SC) ** 2 + (dHp / SH) ** 2 + RT * (dCp / SC) * (dHp / SH))


def sample(img, box_px):
    """Trả (màu nền, màu chữ) trong vùng: nền = màu nhiều nhất; chữ = màu nhiều nhất trong số pixel khác hẳn nền (ΔE > 20).
    Khử răng cưa làm viền chữ ra màu trung gian, nên lấy màu XUẤT HIỆN NHIỀU NHẤT chứ không lấy trung bình."""
    x, y, w, h = (int(round(v)) for v in box_px)
    x, y = max(0, x), max(0, y)
    crop = img.crop((x, y, min(img.width, x + max(1, w)), min(img.height, y + max(1, h)))).convert('RGB')
    q = lambda c: tuple(v // 4 * 4 for v in c)          # gộp sai lệch 1–3 đơn vị do nén ảnh
    px = [q(c) for c in (crop.get_flattened_data() if hasattr(crop, 'get_flattened_data') else crop.getdata())]
    if not px:
        return None, None
    cnt = Counter(px); bg = cnt.most_common(1)[0][0]
    far = Counter({c: n for c, n in cnt.items() if delta_e(c, bg) > 20}) if len(cnt) < 4000 else \
        Counter({c: n for c, n in cnt.most_common(400) if delta_e(c, bg) > 20})
    fg = far.most_common(1)[0][0] if far else None
    return rgb2hex(bg), (rgb2hex(fg) if fg else None)


# ───────────────────────── cây phần tử app ─────────────────────────
def _bounds(s):
    m = re.findall(r'\d+', s or '')
    if len(m) != 4: return None
    x1, y1, x2, y2 = map(int, m)
    return [x1, y1, x2 - x1, y2 - y1]


def _ancestry(root):
    """uid cho mọi phần tử + danh sách uid tổ tiên — để biết phần tử nào là CON của hộp thoại/menu (lớp phủ)
    khi nền phía sau vẫn còn trong cây và còn nằm trong vùng hình học của lớp phủ."""
    uid, anc = {}, {}
    def walk(el, chain):
        uid[el] = len(uid); anc[el] = chain
        for c in el: walk(c, chain + [uid[el]])
    walk(root, [])
    return uid, anc


def android_tree(a):
    root = ET.parse(a.xml).getroot()
    uid, anc = _ancestry(root)
    sc = a.density / 160
    sw, sh = None, None
    nodes = []
    for el in root.iter():
        r = _bounds(el.get('bounds'))
        if not r: continue
        if sw is None or r[2] * r[3] > sw * sh: sw, sh = r[2], r[3]
        if el.get('displayed') == 'false' or r[2] <= 0 or r[3] <= 0: continue
        cls = (el.get('class') or el.tag).split('.')[-1]
        text, desc, hint = (el.get('text') or '').strip(), (el.get('content-desc') or '').strip(), (el.get('hint') or '').strip()
        rid = el.get('resource-id') or ''
        rd = [round(v / sc, 1) for v in r]
        base = {'cls': cls, 'rid': rid, 'rect': rd, 'px': r, 'uid': uid[el], 'anc': anc[el]}
        if 'Image' in cls:                                    # WebView đưa alt của <img> vào text — không phải chữ hiển thị
            if text or desc: nodes.append({'k': 'image', 'text': text or desc, **base})
        elif cls in ('EditText', 'AutoCompleteTextView'):
            val = text or hint
            nodes.append({'k': 'input', 'text': val, 'placeholder': bool(hint) and (not text or text == hint),
                          'password': el.get('password') == 'true', **base})
        elif text:
            nodes.append({'k': 'text', 'text': text, **base})
        elif desc:
            nodes.append({'k': 'image' if 'Image' in cls else 'label', 'text': desc, **base})
        if r[2] * r[3] < (sw or 1) * (sh or 1) * 0.95:
            nodes.append({'k': 'box', 'name': cls + (('#' + rid.split('/')[-1]) if rid else ''), 'cls': cls, 'rect': rd, 'px': r,
                          'uid': uid[el], 'anc': anc[el]})
    out = {'source': 'android', 'frame': {'w': round(sw / sc, 1), 'h': round(sh / sc, 1), 'px': [sw, sh], 'density': a.density},
           'scale': sc, 'top': round(a.top_px / sc, 1), 'bottom': round(a.bottom_px / sc, 1), 'png': a.png, 'nodes': nodes}
    _fill_colors(out)
    _write(out, a.out)


def ios_tree(a):
    root = ET.parse(a.xml).getroot()
    uid, anc = _ancestry(root)
    nodes, W, H = [], 0, 0
    for el in root.iter():
        try:
            r = [float(el.get(k)) for k in ('x', 'y', 'width', 'height')]
        except (TypeError, ValueError):
            continue
        W, H = max(W, r[0] + r[2]), max(H, r[1] + r[3])
        if el.get('visible') == 'false' or r[2] <= 0 or r[3] <= 0: continue
        t = el.get('type', el.tag).replace('XCUIElementType', '')
        label, value, name = (el.get('label') or '').strip(), (el.get('value') or '').strip(), (el.get('name') or '').strip()
        ph = (el.get('placeholderValue') or '').strip()
        base = {'cls': t, 'rid': name, 'rect': r, 'px': [v * a.scale for v in r], 'uid': uid[el], 'anc': anc[el]}
        if t in ('TextField', 'SecureTextField', 'TextView', 'SearchField'):
            nodes.append({'k': 'input', 'text': value if value and value != ph else ph, 'placeholder': not value or value == ph,
                          'password': t == 'SecureTextField', **base})
        elif t in ('StaticText', 'Button', 'Link', 'Cell') and (label or value):
            nodes.append({'k': 'text', 'text': label or value, **base})
        elif t == 'Image' and (label or name):
            nodes.append({'k': 'image', 'text': label or name, **base})
        if t not in ('Application', 'Window'):
            nodes.append({'k': 'box', 'name': t + ('#' + name if name else ''), 'cls': t, 'rect': r, 'px': base['px'],
                          'uid': uid[el], 'anc': anc[el]})
    out = {'source': 'ios', 'frame': {'w': W, 'h': H}, 'scale': a.scale, 'top': a.top, 'bottom': a.bottom, 'png': a.png, 'nodes': nodes}
    _fill_colors(out)
    _write(out, a.out)


def _fill_colors(spec):
    """App native không lộ màu/font qua cây phần tử → lấy mẫu màu trên ảnh chụp tại đúng vùng của phần tử."""
    if not spec.get('png'): return
    from PIL import Image
    img = Image.open(spec['png']).convert('RGB')
    for n in spec['nodes']:
        if n['k'] in ('text', 'input', 'label'):
            bg, fg = sample(img, n['px'])
            n['bg'], n['color'] = bg, fg
        elif n['k'] == 'box':
            x, y, w, h = n['px']
            if w < 12 or h < 12: continue
            pad = min(12 * spec['scale'], w / 5)
            bg, _ = sample(img, [x + pad * 0.5, y + h / 2 - 2, max(2, pad * 0.5), 4])
            n['fill'] = bg


def _write(obj, out):
    s = json.dumps(obj, ensure_ascii=False, indent=1)
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(s, encoding='utf-8')
        print('OK', out, '·', len(obj.get('nodes', [])), 'node')
    else:
        print(s)


# ───────────────────────── so khớp ─────────────────────────
QUOTES = str.maketrans({'’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-', '\u00a0': ' ', '…': '...'})


def norm(t):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', t or '').translate(QUOTES)).strip()


# kiểu dữ liệu đoán từ tên placeholder — tránh hai ô động (<tên> · <email>) khớp chéo nhau
SLOT = [(r'e-?mail|thư', r'[^\s@]+@[^\s@]+'), (r'^n$|số|number|count|total|qty|sl', r'[\d.,]+'),
        (r'tên|name|họ', r'[^\d@]{2,}'),
        (r'giờ|time', r'\d{1,2}:\d{2}'), (r'ngày|date', r'\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}'),
        (r'url|link|web', r'(?:https?://|www\.)\S+'), (r'phone|sđt|điện thoại|mobile', r'[\d +().-]{6,}')]


def shape_re(v):
    """Hình dạng của một giá trị mẫu: giữ loại ký tự, bỏ nội dung — 'bbbb' chỉ khớp chuỗi chữ liền, không khớp 'Upload photo'."""
    if '@' in v: return r'[^\s@]+@[^\s@]+'
    if re.fullmatch(r'[\d\s+().-]+', v): return r'[\d\s+().-]+'
    if ' ' in v.strip(): return r'[^@\n]+'                # tên/cụm chữ: dữ liệu thật có thể chứa số (auto_user_1791…)
    return r'\S+'


def slot_re(name):
    if name.startswith('mẫu:'):                           # + độ dài tối thiểu = nửa giá trị mẫu
        v = name[4:]; return f'(?=.{{{max(1, len(v) // 2)},}})' + shape_re(v), True
    for k, rx in SLOT:
        if re.search(k, name.strip().lower()): return rx, True
    return '.+?', False


def placeholder_re(t):
    """'total: <n> users' → khớp 'total: 3294 users'. Chữ trong <…> là dữ liệu động của thiết kế, không so nguyên văn."""
    nt = norm(t)
    # dữ liệu mẫu kiểu 09xxxxxxxx / xxx-xxx: chuỗi 'x' từ 3 ký tự trở lên là chỗ giữ dữ liệu
    nt = re.sub(r'(?<![A-Za-z])[xX]{3,}(?![A-Za-z])', '<x>', nt)
    slots = re.findall(r'<([^<>]{1,40})>', nt)
    if not slots: return None
    parts = re.split(r'<[^<>]{1,40}>', nt)
    slots = [x for x in slots]
    rx = re.escape(parts[0])
    typed = False
    for name, lit in zip(slots, parts[1:]):
        r, ty = slot_re(name); typed |= ty
        rx += r + re.escape(lit)
    return Slot(re.compile('^' + rx + '$', re.I | re.S), typed, not ''.join(parts).strip())


class Slot:
    def __init__(self, rx, typed, pure):
        self.rx, self.typed, self.pure, self.pattern = rx, typed, pure, rx.pattern

    def match(self, t):
        return self.rx.match(t)


def text_score(d, a):
    """Trả (điểm, kiểu khớp). 1.0 nguyên văn · .97 chỉ khác ký tự trình bày/hoa-thường · .9 placeholder · .75 chứa nhau · tỉ lệ giống ≥ .6"""
    if d == a: return 1.0, 'exact'
    nd, na = norm(d), norm(a)
    if nd == na: return .97, 'typo'                     # khác nháy cong/thẳng, khoảng trắng, NFC
    if nd.lower() == na.lower(): return .95, 'case'
    rx = placeholder_re(d)
    if rx and rx.match(na):
        # ô động thuần (cả chuỗi là <…>) khớp gần như mọi thứ → điểm thấp hơn, trừ khi đoán được kiểu dữ liệu
        return (.88 if rx.typed else .8 if rx.pure else .9), 'placeholder'
    # một bên là tiền tố của bên kia (VD dấu * bắt buộc nằm ở span riêng) — mép trái/trên vẫn đo được
    if min(len(nd), len(na)) >= 3 and (nd.lower().startswith(na.lower()) or na.lower().startswith(nd.lower()))             and min(len(nd), len(na)) >= .6 * max(len(nd), len(na)):
        return .78, 'prefix'
    # app gộp nhiều đoạn chữ thành một node (WebView hay gộp chữ của phần tử con, không chèn khoảng trắng)
    if len(nd) >= 3 and nd.lower() in na.lower(): return .75, 'contains'
    if rx and not rx.pure and re.compile(rx.pattern.strip('^$'), re.I | re.S).search(na): return .72, 'contains'
    # app tách một đoạn thiết kế thành nhiều node — chỉ nhận khi mảnh đủ dài, tránh 'Book' khớp vào cả câu dài
    if len(na) >= 3 and na.lower() in nd.lower() and len(na) >= .5 * len(nd): return .7, 'contains'
    r = difflib.SequenceMatcher(None, nd.lower(), na.lower()).ratio()
    return (r * .85, 'similar') if r >= .6 else (0, None)


def anchor_x(n, W):
    x, _, w, _ = n['rect']
    al = (n.get('align') or 'LEFT').upper()
    return x + w / 2 if al == 'CENTER' else x + w if al == 'RIGHT' else x


def x_dev(d, a, Wd, Wa):
    """Độ lệch ngang theo kiểu neo hợp lý nhất. Màn thật rộng khác khung Figma (412 vs 448 dp…) nên phần tử neo trái giữ x,
    neo phải dịch theo phần chênh, căn giữa dịch nửa phần chênh, co giãn theo tỉ lệ."""
    dx_ = anchor_x(d, Wd)
    ax_ = a['rect'][0] + a['rect'][2] / 2 if (d.get('align') or '').upper() == 'CENTER' else \
        a['rect'][0] + a['rect'][2] if (d.get('align') or '').upper() == 'RIGHT' else a['rect'][0]
    # chữ trong Figma có thể là hộp cố định rộng hơn chữ; với căn trái/phải, mép chữ app phải trùng mép hộp
    dW = Wa - Wd
    cands = {'trái': ax_ - dx_, 'phải': ax_ - (dx_ + dW), 'giữa': ax_ - (dx_ + dW / 2), 'tỉ lệ': ax_ - dx_ * Wa / Wd}
    if container(d, a):                                       # khung app lớn hơn chữ (tab gồm icon + nhãn) → so tâm với tâm
        dc_, ac_ = d['rect'][0] + d['rect'][2] / 2, a['rect'][0] + a['rect'][2] / 2
        cands.update({'tâm-trái': ac_ - dc_, 'tâm-phải': ac_ - (dc_ + dW), 'tâm-giữa': ac_ - (dc_ + dW / 2)})
    k = min(cands, key=lambda c: abs(cands[c]))
    return round(cands[k], 1), k


def container(d, a):
    """Node app là khung chứa chữ (kèm icon, padding) chứ không phải hộp chữ: cao/rộng hơn hẳn hộp chữ thiết kế.
    Cây phần tử của app (nhất là WebView) trả khung của phần tử, không trả khung chữ như Figma."""
    dw, dh, aw, ah = d['rect'][2], d['rect'][3], a['rect'][2], a['rect'][3]
    lh = d.get('lh') or dh
    return ah > max(dh * 1.8, dh + 2 * lh) or aw > dw * 1.6 + 16


def classify(v, tol, big):
    v = abs(v)
    return 'ok' if v <= tol else 'minor' if v <= big else 'diff'


def worst(*ss):
    order = ['ok', 'minor', 'diff']
    ss = [s for s in ss if s in order]
    return max(ss, key=order.index) if ss else 'ok'


def load(path):
    """Kết quả use_figma / tool MCP đôi khi bị mã hoá HTML (&lt; &gt; &amp;) khi chép ra file — giải mã lại ở đây."""
    obj = json.loads(Path(path).read_text(encoding='utf-8'))
    if 'f' in obj and 't' in obj:                          # định dạng gọn của figma_extract.js (COMPACT = true)
        fid, name, w, h, fill = obj['f']
        nodes = [{'k': 'text', 'text': t[0], 'rect': t[1:5], 'size': t[5], 'weight': t[6], 'lh': t[7], 'color': t[8],
                  'align': t[9], 'owner': t[10], 'font': t[11] if len(t) > 11 else None} for t in obj['t']]
        nodes += [{'k': 'box', 'name': b[0], 'rect': b[1:5], 'fill': b[5], 'stroke': b[6], 'radius': b[7], 'owner': b[8],
                   'path': '' if b[9] else b[8]} for b in obj['b']]
        obj = {'source': 'figma', 'frame': {'id': fid, 'name': name, 'w': w, 'h': h, 'fill': fill}, 'nodes': nodes,
               **({'scope': obj['scope']} if obj.get('scope') else {})}
    fix = lambda v: html.unescape(v) if isinstance(v, str) else v
    for n in obj.get('nodes', []):
        for k in ('text', 'path', 'name', 'owner'):
            if k in n: n[k] = fix(n[k])
    if 'frame' in obj and 'name' in obj['frame']: obj['frame']['name'] = fix(obj['frame']['name'])
    return obj


def match(a):
    D, A = load(a.design), load(a.actual)
    if a.sample:                                            # dữ liệu mẫu khai báo tay → coi như ô động <…>, ghi lại trong báo cáo
        for n in D['nodes']:
            if n['k'] == 'text':
                for smp in a.sample:
                    n['text'] = n['text'].replace(smp, f'<mẫu:{smp[:30]}>')
    Wd, Wa = D['frame']['w'], A['frame']['w']
    dtop = a.design_top if a.design_top is not None else next(
        (n['rect'][1] + n['rect'][3] for n in D['nodes'] if n['k'] == 'box' and n.get('name', '').lower().replace(' ', '') == 'statusbar'), 0)
    atop = a.actual_top if a.actual_top is not None else A.get('top', 0)
    abot = A.get('bottom', 0)
    view_h = A['frame']['h'] - atop - abot                       # chiều cao vùng nội dung thật đã chụp
    sys_owner = lambda n: (n.get('owner') or '').lower().replace(' ', '') in ('statusbar', 'navbar', 'homeindicator', 'keyboard')
    ds = [n for n in D['nodes'] if n['k'] == 'text' and not sys_owner(n) and n.get('text', '').strip()]
    # bỏ phần tử bị mép VẬT LÝ của màn cắt dở (cây phần tử trả khung đã bị cắt, chạm đúng mép) — đoạn cuộn khác sẽ đo.
    # Không cắt theo thanh điều hướng: app tràn viền vẽ bottom nav lấn xuống vùng thanh cử chỉ là chuyện bình thường.
    H = A['frame']['h']
    sbar = A.get('top', 0)          # status bar thật — chỉ loại phần tử nằm TRỌN trong đó (lớp phủ có thể lấn lên vùng này)
    as_ = [n for n in A['nodes'] if n['k'] in ('text', 'input', 'label') and n.get('text', '').strip()
           and n['rect'][2] >= 3 and n['rect'][3] >= 3                      # phần tử vô hình (input file ẩn 1×2) — không ai nhìn thấy
           and n['rect'][1] + n['rect'][3] > max(sbar, 1) + 2 and n['rect'][1] + n['rect'][3] < H - 1 and n['rect'][1] < H - abot]
    dy0 = lambda n: n['rect'][1] - dtop
    ay0 = lambda n: n['rect'][1] - atop
    # lớp phủ: nền phía sau thường VẪN nằm trong cây phần tử (modal không ẩn nền khỏi cây trợ năng) → chỉ giữ phần tử app
    # nằm trong khung lớp phủ: khung nhỏ nhất (không phải cả màn) chứa phần lớn chữ trùng nguyên văn với chữ thiết kế
    overlay_box = None
    in_overlay = lambda n: True
    if D.get('scope'):
        keys = {norm(d['text']).lower() for d in ds}
        hits = [n for n in as_ if norm(n['text']).lower() in keys]
        if hits:
            within = lambda r, b: r[0] >= b[0] - 1 and r[1] >= b[1] - 1 and r[0] + r[2] <= b[0] + b[2] + 1 and r[1] + r[3] <= b[1] + b[3] + 1
            boxes_ = [n for n in A['nodes'] if n['k'] == 'box' and n['rect'][2] * n['rect'][3] < A['frame']['w'] * A['frame']['h'] * .9]
            # có thông tin cây (uid/anc) → "nằm trong" = là con cháu; không có (web) → theo hình học
            inside_ov = lambda n, b: (b['uid'] in n['anc']) if 'uid' in b and 'anc' in n else within(n['rect'], b['rect'])
            scored = [(sum(inside_ov(h, b) for h in hits), -b['rect'][2] * b['rect'][3], b) for b in boxes_]
            scored = [x for x in scored if x[0] >= max(2, .6 * len(hits))]
            if scored:
                ob = max(scored, key=lambda x: (x[0], x[1]))[2]
                overlay_box = ob['rect']
                in_overlay = lambda n, ob=ob: inside_ov(n, ob)
                as_ = [n for n in as_ if in_overlay(n)]
    # WebView tách một dòng chữ thành nhiều node (mỗi span một node) → ghép node CÙNG DÒNG, sát nhau thành dòng,
    # và 2–3 dòng liền nhau thành đoạn; node ghép là ứng viên bổ sung, ghép trúng thì các mảnh không bị báo "thừa"
    frag = sorted([n for n in as_ if n['k'] == 'text'], key=lambda n: (round(n['rect'][1]), n['rect'][0]))
    lines, cur = [], []
    for n in frag:
        if cur and abs(n['rect'][1] - cur[-1]['rect'][1]) <= 2 and -4 <= n['rect'][0] - (cur[-1]['rect'][0] + cur[-1]['rect'][2]) <= 12:
            cur.append(n)
        else:
            if len(cur) > 1: lines.append(cur)
            cur = [n]
    if len(cur) > 1: lines.append(cur)
    def merged(parts):
        x1 = min(p['rect'][0] for p in parts); y1 = min(p['rect'][1] for p in parts)
        x2 = max(p['rect'][0] + p['rect'][2] for p in parts); y2 = max(p['rect'][1] + p['rect'][3] for p in parts)
        return {'k': 'text', 'text': ' '.join(p['text'] for p in parts), 'rect': [x1, y1, round(x2 - x1, 1), round(y2 - y1, 1)],
                'color': parts[0].get('color'), 'parts': [id(p) for p in parts], 'anc': parts[0].get('anc', [])}
    synth = [merged(l) for l in lines]
    # đoạn: dòng (đã ghép hoặc đơn) nối tiếp theo chiều dọc, cùng mép trái/giữa ±16
    line_units = synth + [n for n in frag if not any(id(n) in m['parts'] for m in synth)]
    line_units.sort(key=lambda n: n['rect'][1])
    cx = lambda n: n['rect'][0] + n['rect'][2] / 2
    for u in line_units:
        chain = [u]
        while len(chain) < 3:
            last = chain[-1]
            nxt = [v for v in line_units if v is not last and 0 <= v['rect'][1] - (last['rect'][1] + last['rect'][3]) <= 6
                   and (abs(cx(v) - cx(u)) <= 16 or abs(v['rect'][0] - u['rect'][0]) <= 4)]
            if not nxt: break
            chain.append(min(nxt, key=lambda v: v['rect'][1]))
            m = merged(chain); m['parts'] = [x for q in chain for x in (q.get('parts') or [id(q)])]
            synth.append(m)
    as_ += synth

    # 0) đoạn màn đã cuộn: tính độ cuộn TRƯỚC khi ghép, từ các cặp chữ trùng nguyên văn và chỉ xuất hiện một lần mỗi phía
    off, fixed, hidden, fix_bottom = 0, set(), set(), 0
    if a.auto_offset:
        # node nhãn trợ năng thường lặp lại đúng chữ của node chữ bên cạnh → không đếm, tránh loại oan cặp duy nhất
        cnt_d, cnt_a = Counter(norm(d['text']) for d in ds), Counter(norm(n['text']) for n in as_ if n['k'] != 'label')
        uniq = [(i, j) for i, d in enumerate(ds) for j, n in enumerate(as_)
                if n['k'] != 'label' and norm(d['text']) == norm(n['text']) and cnt_d[norm(d['text'])] == 1 and cnt_a[norm(n['text'])] == 1]
        dys = [ay0(as_[j]) - dy0(ds[i]) for i, j in uniq]
        if dys:
            # trung vị của nhóm đông nhất (phần tử cuộn theo trang) — phần tử cố định (header, bottom nav) có dy ≈ 0
            moving = [v for v in dys if abs(v) > a.tol] or dys
            off = statistics.median(moving)
            # phần tử cố định: đứng yên dù trang đã cuộn → đã đo ở đoạn đầu, bỏ qua ở đoạn này
            fixed = {i for (i, j), v in zip(uniq, dys) if abs(v) <= a.tol < abs(off)}
        # đáy vùng cố định phía trên = đáy KHỐI cha cấp 1 (VD AppHeader) của phần tử cố định, không phải đáy dòng chữ
        owner_bottom = {b['name']: b['rect'][1] + b['rect'][3] - dtop for b in D['nodes'] if b['k'] == 'box' and not b.get('path')}
        fix_bottom = max((max(dy0(ds[i]) + ds[i]['rect'][3], owner_bottom.get(ds[i].get('owner'), 0))
                          for i in fixed if dy0(ds[i]) < view_h / 3), default=0)
        # phần tử dự kiến đã cuộn khỏi màn hoặc nằm dưới header cố định → không ghép (tránh ghép nhầm chữ gần giống)
        hidden = {i for i, d in enumerate(ds) if i not in fixed and (dy0(d) + off + d['rect'][3] < fix_bottom or dy0(d) + off + d['rect'][3] > view_h)}   # khuất HẲN sau header mới bỏ

    # 0b) phần tử thiết kế nằm ngoài bề ngang khung (vùng cuộn ngang) → ngoài màn, không ghép
    hidden |= {i for i, d in enumerate(ds) if d['rect'][0] >= Wd - 2 or d['rect'][0] + d['rect'][2] <= 2}
    # 0c) hàng lặp (khối cùng tên + cùng kích thước ≥ 3 lần: UserRow, BookCard…) chứa DỮ LIỆU MẪU — không so nguyên văn
    from collections import defaultdict
    grp = defaultdict(list)
    for b in D['nodes']:
        if b['k'] == 'box' and b.get('name') and b['rect'][2] >= 24:
            grp[(b['name'], b['rect'][2], b['rect'][3])].append(b['rect'])
    inside_d = lambda r, b: r[0] >= b[0] - 1 and r[1] >= b[1] - 1 and r[0] + r[2] <= b[0] + b[2] + 1 and r[1] + r[3] <= b[1] + b[3] + 1
    # hàng danh sách chứa ≥ 2 chữ (tên + email + SĐT…); ô nhập lặp lại (TextField) chỉ có 1 placeholder → không phải danh sách
    # … và là HÀNG: tên kiểu Row/Card/Item/Cell/Tile/List, hoặc rộng ≥ 60 % khung. Ô điền sẵn (nhãn + giá trị) lặp lại không phải danh sách
    LISTY = re.compile(r'row|card|item|cell|tile|list|hàng|dòng', re.I)
    grp = {k: v for k, v in grp.items() if (len(v) >= 2 if LISTY.search(k[0]) else len(v) >= 3 and k[1] >= .6 * Wd)
           and all(sum(inside_d(d['rect'], r) for d in ds) >= 2 for r in v)}
    rows_rect = [r for v in grp.values() for r in v]
    sample = {i for i, d in enumerate(ds) if any(inside_d(d['rect'], r) for r in rows_rect)}
    list_top = min((r[1] for r in rows_rect), default=None)
    list_bot = max((r[1] + r[3] for r in rows_rect), default=None)

    # 1) ghép cặp theo chữ, ưu tiên điểm cao rồi khoảng cách gần
    cand = []
    # chữ app đã có đối tác "thật" (không phải ô động thuần) thì ô động thuần như <Tên tài khoản> không được giành
    is_pure = lambda t: bool(getattr(placeholder_re(t), 'pure', False))
    real = {j for j, n in enumerate(as_) for d in ds if not is_pure(d['text']) and text_score(d['text'], n['text'])[0] >= .7}
    for i, d in enumerate(ds):
        if i in hidden: continue
        pure = is_pure(d['text'])
        for j, n in enumerate(as_):
            if pure and j in real: continue
            if a.auto_offset and i not in fixed and ay0(n) + n['rect'][3] < fix_bottom: continue
            s, kind = text_score(d['text'], n['text'])
            if i in sample and kind != 'exact': continue           # dữ liệu mẫu chỉ ghép khi trùng nguyên văn
            if n['k'] == 'label': s *= .9                          # nhãn trợ năng chưa chắc là chữ hiển thị
            if s:
                ref = dy0(d) + (0 if i in fixed else off)
                # cùng chữ có nhiều node (nhãn + khung chứa gộp chữ) → ưu tiên node có cỡ gần hộp chữ thiết kế
                dist = abs(ay0(n) - ref) + abs(n['rect'][0] - d['rect'][0]) * .5 + abs(n['rect'][3] - d['rect'][3]) * .5
                cand.append((-s, dist, i, j, kind, s))
    cand.sort()
    pd, pa = {}, {}
    # chữ LẶP LẠI (nhãn "Field" ở mỗi hàng điều kiện, "Edit" ở mỗi hàng…): ghép theo THỨ TỰ trên → dưới bằng quy hoạch động,
    # không ghép theo khoảng cách gần nhất — gần nhất làm hàng 2 thiết kế ghép chéo sang hàng 1 của app khi cả khối bị xô
    from itertools import groupby
    keyf = lambda t: norm(t).lower()
    for txt, grp_d in groupby(sorted((i for i in range(len(ds)) if i not in hidden and i not in sample), key=lambda i: keyf(ds[i]['text'])), key=lambda i: keyf(ds[i]['text'])):
        di = sorted(grp_d, key=lambda i: dy0(ds[i]))
        aj = sorted((j for j, n in enumerate(as_) if keyf(n['text']) == txt and n['k'] != 'label'), key=lambda j: ay0(as_[j]))
        if len(di) < 2 or len(aj) < 2: continue
        dd, aa = [dy0(ds[i]) for i in di], [ay0(as_[j]) for j in aj]
        best = None
        for k in range(-(len(di) - 1), len(aj)):          # dịch chỉ số, ghép đơn điệu
            pairs = [(x, x + k) for x in range(len(di)) if 0 <= x + k < len(aj)]
            if not pairs: continue
            shift = statistics.median(aa[y] - dd[x] for x, y in pairs)
            cost = sum(abs(aa[y] - dd[x] - shift) for x, y in pairs) - 1000 * len(pairs)
            if best is None or cost < best[0]: best = (cost, pairs)
        for x, y in best[1]:
            pd[di[x]] = (aj[y], 'exact' if ds[di[x]]['text'] == as_[aj[y]]['text'] else 'typo', 1.0); pa.setdefault(aj[y], di[x])
    for _, dist, i, j, kind, s in cand:
        if i in pd or (j in pa and kind != 'contains'): continue
        pd[i] = (j, kind, s); pa.setdefault(j, i)

    # lớp phủ (menu, dialog, bottom sheet): vị trí của cả lớp phủ do màn quyết định (căn giữa, neo đáy, neo nút…) — đo chữ
    # TƯƠNG ĐỐI với khung lớp phủ; vị trí của chính lớp phủ báo ở bảng khối
    scope_note = None
    if D.get('scope') and not a.auto_offset:
        db = next((b for b in D['nodes'] if b['k'] == 'box' and b.get('name') == D['scope']), None)
        got = [as_[j]['rect'] for i, (j, k, s_) in pd.items() if k not in ('contains',)]
        if db and got:
            x1, y1 = min(r[0] for r in got), min(r[1] for r in got)
            x2, y2 = max(r[0] + r[2] for r in got), max(r[1] + r[3] for r in got)
            cont = [n for n in A['nodes'] if n['k'] == 'box' and n['rect'][0] <= x1 + 1 and n['rect'][1] <= y1 + 1
                    and n['rect'][0] + n['rect'][2] >= x2 - 1 and n['rect'][1] + n['rect'][3] >= y2 - 1
                    and n['rect'][2] < A['frame']['w'] * .99 + (Wa - Wd) and n['rect'][3] < A['frame']['h'] * .9]
            if cont:
                ab = min(cont, key=lambda n: n['rect'][2] * n['rect'][3])['rect']
                off = round((ab[1] - atop) - (db['rect'][1] - dtop), 1)
                scope_note = f"lớp phủ `{D['scope']}`: thiết kế y {db['rect'][1]:g} · app y {ab[1]:g} — chữ đo tương đối với khung lớp phủ (đã bù {off:+g})"

    # thiết kế tự ghi chú vẽ RÚT GỌN ("lược bớt", "rút gọn", "abridged"…) → vị trí không còn so được, chỉ so nội dung + màu
    ABR = re.compile(r'lược bớt|rút gọn|cắt bớt|bỏ bớt|abridged|omitted|simplified|truncated for', re.I)
    abridged = next((d['text'] for d in ds if ABR.search(d['text'])), None)
    if abridged:
        hidden |= {i for i, d in enumerate(ds) if ABR.search(d['text'])}
    # ghi chú của designer vẽ ngay trên khung ("… (đã cuộn xuống …)", "(Ảnh … lược bớt)") — không phải chữ của giao diện
    NOTE = re.compile(r'^\s*…|^\s*\(.{12,}\)\s*$')
    notes = {i for i, d in enumerate(ds) if NOTE.search(d['text'])}
    hidden |= notes

    rows = []
    order = sorted(range(len(ds)), key=lambda i: (dy0(ds[i]), ds[i]['rect'][0]))
    prev = None
    for i in order:
        d = ds[i]
        row = {'id': d.get('id'), 'design': d['text'], 'path': d.get('path'), 'drect': d['rect'], 'checks': []}
        if i in fixed:
            row.update({'status': 'na', 'actual': as_[pd[i][0]]['text'] if i in pd else '—'})
            row['checks'].append('phần tử cố định khi cuộn (header/bottom nav) — đã đo ở đoạn đầu')
            rows.append(row); continue
        if i in notes:
            row['status'] = 'na'; row['checks'].append('ghi chú của thiết kế — không phải chữ giao diện')
            rows.append(row); continue
        if i not in pd and i in sample:
            row['status'] = 'na'; row['checks'].append('dữ liệu mẫu trong hàng lặp — so cấu trúc hàng (cao, cột, căn) bằng ảnh, không so chữ')
            rows.append(row); continue
        if i not in pd and (d['rect'][0] >= Wd - 2 or d['rect'][0] + d['rect'][2] <= 2):
            row['status'] = 'offscreen'; row['checks'].append('nằm ngoài bề ngang khung — vùng cuộn ngang, so khi cuộn tới')
            rows.append(row); continue
        if i not in pd:
            # có trên app nhưng bị mép màn cắt dở / khuất sau header → ngoài màn, không phải thiếu
            clipped = any(text_score(d['text'], n['text'])[0] >= .7 for n in A['nodes']
                          if n['k'] in ('text', 'input', 'label') and n not in as_ and n.get('text') and in_overlay(n))
            row['status'] = 'offscreen' if clipped or i in hidden or dy0(d) + off + d['rect'][3] > view_h or dy0(d) + off < 0 else 'missing'
            if clipped: row['checks'].append('có trên app nhưng bị mép màn cắt dở — đo ở đoạn cuộn khác')
            rows.append(row); continue
        j, kind, s = pd[i]; n = as_[j]
        row.update({'actual': n['text'], 'arect': n['rect'], 'match': kind, 'akind': n['k'], 'asel': n.get('rid') or n.get('sel')})
        st = []
        if kind in ('exact', 'placeholder'):
            st.append('ok')
        elif kind in ('typo', 'case'):
            st.append('minor'); row['checks'].append(f"chữ khác ký tự trình bày/hoa-thường: “{d['text']}” ↔ “{n['text']}”")
        elif kind == 'prefix':
            st.append('minor'); row['checks'].append(f"chữ khác phần đuôi: “{d['text']}” ↔ “{n['text']}” (phần thiếu có thể nằm ở node/span riêng — xem ảnh)")
        elif kind == 'contains':
            st.append('na'); row['checks'].append(f"chữ có trên app nhưng nằm chung node “{n['text'][:40]}” — vị trí, màu không đo tự động, đối chiếu bằng ảnh")
        else:
            st.append('diff'); row['checks'].append(f"nội dung chữ khác: “{d['text']}” ↔ “{n['text']}”")
        if n['k'] == 'input' and n.get('placeholder') is False:
            row['checks'].append('ô nhập đang có giá trị — không phải placeholder')
        if kind != 'contains' and not abridged:
            box = container(d, n) and kind != 'prefix'
            dx, anc = x_dev(dict(d, align='LEFT') if kind == 'prefix' else d, n, Wd, Wa)
            # khung chứa lớn hơn chữ: so tâm dọc thay cho mép trên
            dy = round((ay0(n) + n['rect'][3] / 2) - (dy0(d) + d['rect'][3] / 2) - off, 1) if box else round(ay0(n) - dy0(d) - off, 1)
            row.update({'dx': dx, 'anchor': anc, 'dy': dy})
            st.append(classify(dx, a.tol, a.tol * 3))
            # Δy dồn: phần tử phía trên cao hơn thì mọi thứ bên dưới đều lệch theo. Chỉ phần tử có KHOẢNG CÁCH tới
            # phần tử khớp ngay phía trên thay đổi mới là chỗ khởi phát — các phần tử còn lại kế thừa, không tính lỗi lại.
            # phần tử neo đáy (bottom nav, nút cố định): so khoảng cách tới đáy vùng nội dung, không nối chuỗi khoảng cách
            d_bot = D['frame']['h'] - (dy0(d) + dtop + d['rect'][3])
            a_bot = A['frame']['h'] - abot - (n['rect'][1] + n['rect'][3])
            if d_bot < .15 * D['frame']['h'] and a_bot < .15 * view_h and not a.auto_offset and not scope_note:
                cd = (d['rect'][1] + d['rect'][3] / 2) if box else d['rect'][1] + d['rect'][3]
                ca = (n['rect'][1] + n['rect'][3] / 2) if box else n['rect'][1] + n['rect'][3]
                dy = round((ca - (A['frame']['h'] - abot)) - (cd - D['frame']['h']), 1)
                row.update({'dy': dy, 'anchor': anc + ' · neo đáy'})
                st.append(classify(dy, a.tol, a.tol * 3))
                row['checks'].append('neo đáy màn hình — Δy đo theo khoảng cách tới đáy vùng nội dung')
            elif prev is None:
                st.append(classify(dy, a.tol, a.tol * 3))
                if abs(dy) > a.tol: row['checks'].append(f'lệch {dy:+g} tính từ đầu vùng nội dung — nguyên nhân có thể nằm ở phần tử không có chữ phía trên (ảnh, banner, header)')
            else:
                pdd, pan, pbox = prev
                ref_a = ay0(pan) + (pan['rect'][3] / 2 if pbox else 0)
                ref_d = dy0(pdd) + (pdd['rect'][3] / 2 if pbox else 0)
                cur_a = ay0(n) + (n['rect'][3] / 2 if box else 0)
                cur_d = dy0(d) + (d['rect'][3] / 2 if box else 0)
                gap = round((cur_a - ref_a) - (cur_d - ref_d), 1)
                row['dgap'] = gap
                st.append(classify(gap, a.tol, a.tol * 3))
                if abs(gap) > a.tol: row['checks'].append(f'khoảng cách tới “{pdd["text"][:24]}” lệch {gap:+g} — điểm khởi phát xô lệch')
                elif abs(dy) > a.tol: row['checks'].append(f'Δy {dy:+g} kế thừa từ phía trên — không tính lỗi riêng')
            if 'neo đáy' not in row['anchor']: prev = (d, n, box)
            # chiều cao hộp chữ = line-height × số dòng → lệch lớn nghĩa là xuống dòng khác hoặc line-height khác
            dh = round(n['rect'][3] - d['rect'][3], 1)
            row['dh'] = dh
            if kind == 'prefix':
                pass
            elif box:
                row['checks'].append('khung phần tử app lớn hơn hộp chữ (gồm icon/padding) — không đo được số dòng, so theo tâm')
            elif d.get('lh') and abs(dh) >= d['lh'] * .6:
                row['checks'].append(f"cao {n['rect'][3]:g} vs {d['rect'][3]:g} — khác số dòng (≈{round(n['rect'][3] / d['lh'], 1)} vs {round(d['rect'][3] / d['lh'], 1)} dòng)")
                st.append('diff')
            elif abs(dh) > a.tol:
                st.append('minor')
        # kiểu chữ: web có số đo thật; app native chỉ có màu lấy mẫu trên ảnh
        if d.get('size') and n.get('size'):
            dsz = round(n['size'] - d['size'], 1); row['dsize'] = dsz
            if abs(dsz) > a.tol_size: st.append('diff' if abs(dsz) >= 2 else 'minor'); row['checks'].append(f"cỡ chữ {n['size']:g} vs {d['size']:g}")
        if d.get('weight') and n.get('weight') and abs(n['weight'] - d['weight']) >= 100:
            st.append('minor' if abs(n['weight'] - d['weight']) == 100 else 'diff'); row['checks'].append(f"độ đậm {n['weight']} vs {d['weight']}")
        if d.get('font') and n.get('font') and norm(d['font']).split(' ')[0].lower() not in norm(n['font']).lower():
            st.append('diff'); row['checks'].append(f"font {n['font']} vs {d['font']}")
        boxed = kind != 'contains' and container(d, n)
        if boxed and d.get('color') and n.get('color') and not n.get('size'):
            row['checks'].append('màu chữ không lấy mẫu được (khung có cả icon/nền) — đối chiếu bằng ảnh')
        elif kind != 'contains' and d.get('color') and n.get('color') and not (n['k'] == 'input' and n.get('placeholder') is False):
            de = round(delta_e(d['color'], n['color']), 1); row['dE'] = de; row['acolor'] = n['color']; row['dcolor'] = d['color']
            sv = 'ok' if de <= a.de_text else 'minor' if de <= a.de_text * 2.5 else 'diff'
            st.append(sv)
            if sv != 'ok': row['checks'].append(f"màu chữ {n['color']} vs {d['color']} (ΔE {de})")
        row['status'] = 'na' if 'na' in st and worst(*st) == 'ok' else worst(*st)
        rows.append(row)

    inside = lambda r, b, m=2: r[0] >= b[0] - m and r[1] >= b[1] - m and r[0] + r[2] <= b[0] + b[2] + m and r[1] + r[3] <= b[1] + b[3] + m
    # node cha gộp chữ của các con (WebView) — chữ đã được tính ở node con, không phải "thừa"
    group = lambda j: sum(1 for k in pa if k != j and inside(as_[k]['rect'], as_[j]['rect']) and norm(as_[k]['text']) in norm(as_[j]['text'])) >= 2
    # vùng danh sách trên app: từ đầu danh sách (theo thiết kế) tới phần tử khớp đầu tiên nằm dưới danh sách
    a_list = None
    if list_top is not None:
        below = [ay0(as_[pd[i][0]]) for i in pd if dy0(ds[i]) >= list_bot - dtop and pd[i][1] != 'contains' and i not in sample]
        a_list = (list_top - dtop + off - 8, min(below) if below else view_h)
    in_list = lambda n: a_list is not None and a_list[0] <= ay0(n) <= a_list[1]
    used_parts = {x for j in pa for x in (as_[j].get('parts') or [])}
    extras = [{'status': 'extra', 'actual': n['text'], 'arect': n['rect'], 'akind': n['k'], 'asel': n.get('rid') or n.get('sel')}
              for j, n in enumerate(as_) if j not in pa and n['k'] != 'label' and not group(j)
              and norm(n['text']) not in {norm(as_[k]['text']) for k in pa}
              and not (a.auto_offset and ay0(n) + n['rect'][3] < fix_bottom + 2)       # khuất sau header cố định
              and not in_list(n)                                                      # dữ liệu thật của danh sách
              and id(n) not in used_parts and not n.get('parts')]                     # mảnh đã ghép thành dòng/đoạn   # ô nhập mang câu lỗi/trợ giúp trong hint — đã tính ở node chữ

    # 3) khối có nền/viền (nút, card, ô nhập): ghép qua chữ nằm bên trong
    boxes = []
    abox = [n for n in A['nodes'] if n['k'] in ('box', 'input')]
    seen = set()
    for b in D['nodes']:
        if b['k'] != 'box' or sys_owner(b) or not (b.get('fill') or b.get('stroke')) or b['rect'][2] < 16 or b['rect'][3] < 16: continue
        key = tuple(b['rect'])
        if key in seen: continue
        seen.add(key)
        kids = [r for r in rows if r.get('arect') and r['match'] not in ('contains',) and inside(r['drect'], b['rect'])]
        if not kids: continue
        cont = [n for n in abox if all(inside(k['arect'], n['rect']) for k in kids)]
        exp_area = b['rect'][2] * b['rect'][3]
        cont = [n for n in cont if .4 < (n['rect'][2] * n['rect'][3]) / exp_area < 2.5]
        if not cont: continue
        # khung có diện tích gần khung thiết kế nhất (đã bù phần co giãn) — không lấy khung nhỏ nhất: ô nhập có icon thì
        # EditText chỉ là phần chữ, khung thật là phần tử cha
        exp = (b['rect'][2] + (Wa - Wd) * (b['rect'][2] > Wd * .5)) * b['rect'][3]
        n = min(cont, key=lambda n: abs(math.log(n['rect'][2] * n['rect'][3] / exp)))
        row = {'box': b.get('name'), 'path': b.get('path'), 'drect': b['rect'], 'arect': n['rect'], 'asel': n.get('name') or n.get('cls'), 'checks': []}
        st = []
        lm, rm = b['rect'][0], Wd - b['rect'][0] - b['rect'][2]
        # khối co giãn theo màn: sát hai mép, hoặc rộng quá nửa màn và cách đều hai mép (nút/ô nhập trong card)
        fluid = (lm <= 24 and rm <= 24) or (b['rect'][2] > Wd * .5 and abs(lm - rm) <= 8)
        dwf = round(n['rect'][2] - b['rect'][2] - (Wa - Wd if fluid else 0), 1)
        dhh = round(n['rect'][3] - b['rect'][3], 1)
        row.update({'dw': dwf, 'dh': dhh}); st += [classify(dwf, a.tol, a.tol * 3), classify(dhh, a.tol, a.tol * 3)]
        if abs(dhh) > a.tol: row['checks'].append(f"cao {n['rect'][3]:g} vs {b['rect'][3]:g}")
        if abs(dwf) > a.tol: row['checks'].append(f"rộng {n['rect'][2]:g} vs {b['rect'][2]:g}" + (' (đã trừ phần chênh bề ngang màn hình)' if fluid else ''))
        if b.get('fill') and n.get('fill') and '@' not in b['fill']:
            de = round(delta_e(b['fill'], n['fill']), 1); row.update({'dE': de, 'dcolor': b['fill'], 'acolor': n['fill']})
            sv = 'ok' if de <= a.de_fill else 'minor' if de <= a.de_fill * 2.5 else 'diff'; st.append(sv)
            if sv != 'ok': row['checks'].append(f"màu nền {n['fill']} vs {b['fill']} (ΔE {de})")
        row['status'] = worst(*st)
        boxes.append(row)

    if abridged:
        for r in rows:
            if r['status'] == 'offscreen' and ABR.search(r['design']): r['status'] = 'na'; r['checks'].append('ghi chú của thiết kế')
        for e in extras: e['status'] = 'na'
    res = {'abridged': abridged, 'scope_note': scope_note, 'sample': a.sample or [], 'design': a.design, 'actual': a.actual, 'frame': D['frame'].get('name'), 'design_w': Wd, 'actual_w': Wa,
           'design_top': dtop, 'actual_top': atop, 'offset': off, 'tol': a.tol, 'scale': A.get('scale', 1), 'png': A.get('png'),
           'rows': rows, 'extras': extras, 'boxes': boxes}
    if rows_rect:
        res['lists'] = [{'name': k[0], 'w': k[1], 'h': k[2], 'count': len(v)} for k, v in grp.items()]
    res['summary'] = dict(Counter(r['status'] for r in rows + extras + boxes))
    if a.redact:                                            # che dữ liệu cá nhân của app trong cả .json lẫn .md (bảng đo đi vào docs/)
        rx = re.compile('|'.join(f'(?:{r})' for r in a.redact))
        hide = lambda v: rx.sub('<đã che>', v) if isinstance(v, str) else v
        for r in rows + extras:
            if 'actual' in r: r['actual'] = hide(r['actual'])
            if 'checks' in r: r['checks'] = [hide(c) for c in r['checks']]
    _write(res, a.out + '.json')
    Path(a.out + '.md').write_text(to_md(res), encoding='utf-8')
    print('OK', a.out + '.md ·', ' · '.join(f"{ICON[k]} {LABEL[k]} {v}" for k, v in res['summary'].items()))


def _r(r):
    return '—' if not r else '[' + ', '.join(f'{v:g}' for v in r) + ']'


def to_md(res):
    L = [f"### `{res['frame']}` — bảng so khớp tự động",
         f"> Khung thiết kế rộng **{res['design_w']:g}** · màn thật rộng **{res['actual_w']:g}** (cùng đơn vị) · bỏ status bar: thiết kế {res['design_top']:g} / thật {res['actual_top']:g}"
         + (f" · đã bù lệch dọc chung {res['offset']:g} (= độ cuộn + lệch bố cục tích luỹ phía trên, không phải độ cuộn)" if res['offset'] else '') + f" · dung sai vị trí ±{res['tol']:g}",
         *([f"> Danh sách lặp trong thiết kế: " + ' · '.join(f"`{l['name']}` × {l['count']} (cao {l['h']:g})" for l in res['lists']) + " — chữ bên trong là dữ liệu mẫu; so chiều cao hàng, cột, căn lề bằng ảnh"] if res.get('lists') else []),
         *([f"> {res['scope_note']}"] if res.get('scope_note') else []),
         *([f"> ⚠️ Thiết kế ghi chú vẽ rút gọn (“{res['abridged'][:60]}”) — **không so vị trí**, chỉ so nội dung chữ + màu; chữ app không có trong thiết kế ghi ❔"] if res.get('abridged') else []),
         *([f"> Dữ liệu mẫu khai báo tay (coi như ô động): " + ' · '.join(f"`{x}`" for x in res['sample'])] if res.get('sample') else []),
         '', '**Tổng:** ' + ' · '.join(f"{ICON[k]} {LABEL[k]} **{v}**" for k, v in res['summary'].items()), '',
         '| # | Trạng thái | Chữ trong thiết kế | Trên app | Δx (neo) | Δy | Δ khoảng cách | Δ cao | Màu (thiết kế → app · ΔE) | Ghi chú |',
         '|---|---|---|---|---|---|---|---|---|---|']
    for k, r in enumerate(res['rows'], 1):
        col = f"`{r['dcolor']}` → `{r['acolor']}` · {r['dE']}" if r.get('dE') is not None else '—'
        dx = f"{r['dx']:+g} ({r['anchor']})" if 'dx' in r else '—'
        L.append(f"| {k} | {ICON[r['status']]} | {r['design']} | {r.get('actual', '—')} | {dx} | {r.get('dy', '—') if 'dy' not in r else format(r['dy'], '+g')} "
                 f"| {format(r['dgap'], '+g') if 'dgap' in r else '—'} | {format(r['dh'], '+g') if 'dh' in r else '—'} | {col} | {'<br>'.join(r['checks'])} |")
    if res['boxes']:
        L += ['', '> Khối có nền/viền ghép qua chữ nằm bên trong — **heuristic**: phần tử app được chọn là khung nhỏ nhất chứa đủ các chữ đó, màu nền lấy mẫu ở mép trái. Dòng ❌ ở đây phải xem ảnh trước khi tin.',
              '', '| # | Trạng thái | Khối (thiết kế) | Phần tử app | Δ rộng | Δ cao | Màu nền (thiết kế → app · ΔE) | Ghi chú |', '|---|---|---|---|---|---|---|---|']
        for k, r in enumerate(res['boxes'], 1):
            col = f"`{r['dcolor']}` → `{r['acolor']}` · {r['dE']}" if r.get('dE') is not None else '—'
            L.append(f"| B{k} | {ICON[r['status']]} | {r['box']} {_r(r['drect'])} | `{r['asel']}` {_r(r['arect'])} | {r['dw']:+g} | {r['dh']:+g} | {col} | {'<br>'.join(r['checks'])} |")
    if res['extras']:
        L += ['', '| ➕ Chữ có trên app nhưng không có trong thiết kế | Loại | Vị trí |', '|---|---|---|']
        for r in res['extras']:
            L.append(f"| {r['actual']} | {r['akind']} | {_r(r['arect'])} |")
    L += ['', '> Bảng này là **dữ liệu đo**, chưa phải kết luận. Mỗi dòng ❌ / ⚠️ / 🔍 / ➕ phải được người soát mở ảnh đối chiếu rồi mới ghi thành `DIFF` (rule `design_compare_rules.md` mục 4).']
    return '\n'.join(L) + '\n'


# ───────────────────────── ảnh ─────────────────────────
def _font(size, bold=True):
    from PIL import ImageFont
    names = ('arialbd.ttf', 'Arial Bold.ttf', 'DejaVuSans-Bold.ttf') if bold else ('arial.ttf', 'Arial.ttf', 'DejaVuSans.ttf')
    for name in names:
        for d in ('', 'C:/Windows/Fonts/', '/Library/Fonts/', '/usr/share/fonts/truetype/dejavu/'):
            try: return ImageFont.truetype(d + name, size)
            except OSError: pass
    return ImageFont.load_default()


def render(a):
    """Dựng ảnh SƠ ĐỒ từ figma.json khi không lấy được ảnh Figma (hết lượt gọi MCP, file bị khoá quyền xuất ảnh).
    Vẽ khối (nền + viền + bo góc) và chữ đúng toạ độ, cỡ, màu — đủ để đặt cạnh ảnh app và khoanh DIFF.
    KHÔNG thay được ảnh thật: icon, ảnh, đổ bóng, font không có. Ghi rõ "ảnh dựng lại từ dữ liệu" trong báo cáo."""
    from PIL import Image, ImageDraw
    D = load(a.design); W, H = D['frame']['w'], D['frame']['h']; U = a.unit_px
    img = Image.new('RGB', (round(W * U), round(H * U)), D['frame'].get('fill') or '#ffffff'); dr = ImageDraw.Draw(img)
    boxes = [n for n in D['nodes'] if n['k'] == 'box']
    for n in sorted(boxes, key=lambda n: -n['rect'][2] * n['rect'][3]):           # khối lớn vẽ trước, khối con đè lên
        x, y, w, h = n['rect']
        if n.get('name', '').lower().replace(' ', '') == 'statusbar': continue
        r = min(n.get('radius') or 0, w / 2, h / 2) * U
        dr.rounded_rectangle([x * U, y * U, (x + w) * U, (y + h) * U], radius=r, fill=n.get('fill'),
                             outline=n.get('stroke') or ('#d0d5da' if not n.get('fill') else None), width=max(1, round(U)))
    for n in (n for n in D['nodes'] if n['k'] == 'text'):
        x, y, w, h = n['rect']; f = _font(max(8, round((n.get('size') or 14) * U * .92)), (n.get('weight') or 400) >= 600)
        lh = n.get('lh') or (n.get('size') or 14) * 1.4
        lines, cur = [], ''
        for word in n['text'].split(' '):                     # ngắt dòng theo bề rộng hộp chữ như Figma
            if cur and dr.textlength(cur + ' ' + word, font=f) > w * U * 1.02 and len(lines) + 1 < max(1, round(h / lh)):
                lines.append(cur); cur = word
            else: cur = (cur + ' ' + word).strip()
        lines.append(cur)
        for i, t in enumerate(lines):
            while len(t) > 1 and dr.textlength(t, font=f) > max(w, 8) * U * 1.15: t = t[:-2] + '…'
            tx = x + (w - dr.textlength(t, font=f) / U) / 2 if n.get('align') == 'CENTER' else x
            dr.text((tx * U, (y + i * lh) * U), t, fill=n.get('color') or '#1c252e', font=f)
    dr.text((6, img.height - 18), 'ảnh dựng lại từ figma.json — không có icon/ảnh', fill='#ff5630', font=_font(round(7 * U) + 4))
    img.save(a.out); print(f'OK {a.out} · {W}×{H} · ×{U}')

def visual(a):
    """Ảnh đặt cạnh nhau (Figma | App) + ảnh chồng 50 % + bản đồ khác biệt. Chỉ để NGƯỜI nhìn — % giống nhau không phải tiêu chí đạt/trượt."""
    from PIL import Image, ImageChops, ImageDraw
    D = load(a.design) if a.design else None
    A = load(a.actual) if a.actual else None
    di, ai = Image.open(a.design_png).convert('RGB'), Image.open(a.actual_png).convert('RGB')
    dw = D['frame']['w'] if D else a.design_w
    aw = A['frame']['w'] if A else a.actual_w
    du, au = di.width / dw, ai.width / aw                          # pixel ảnh trên mỗi đơn vị
    dtop = a.design_top if a.design_top is not None else next((n['rect'][1] + n['rect'][3] for n in (D or {}).get('nodes', [])
                                                              if n['k'] == 'box' and n.get('name', '').lower() == 'statusbar'), 0)
    atop = a.actual_top if a.actual_top is not None else (A or {}).get('top', 0)
    abot = (A or {}).get('bottom', 0)
    off = 0
    if a.match:                                             # đoạn màn đã cuộn: cắt khung Figma từ đúng chỗ đoạn app bắt đầu
        off = json.loads(Path(a.match).read_text(encoding='utf-8')).get('offset', 0) or 0
    # offset âm = màn đã cuộn → cắt Figma xuống theo. Offset dương chỉ là app dài hơn thiết kế (lệch bố cục, không cuộn) → giữ nguyên
    di = di.crop((0, int((dtop - min(off, 0)) * du), di.width, di.height))
    ai = ai.crop((0, int(atop * au), ai.width, ai.height - int(abot * au)))
    U = a.unit_px
    di = di.resize((round(di.width / du * U), round(di.height / du * U)))
    ai = ai.resize((round(ai.width / au * U), round(ai.height / au * U)))
    H = min(max(di.height, ai.height), ai.height if a.clip else 10 ** 6)
    gap, head = 24, 44
    f = _font(20)
    side = Image.new('RGB', (di.width + ai.width + gap, H + head), 'white')
    side.paste(di.crop((0, 0, di.width, min(H, di.height))), (0, head)); side.paste(ai.crop((0, 0, ai.width, min(H, ai.height))), (di.width + gap, head))
    d = ImageDraw.Draw(side)
    d.text((8, 10), f'FIGMA · {dw:g} rộng', fill=(17, 24, 39), font=f); d.text((di.width + gap + 8, 10), f'APP · {aw:g} rộng', fill=(225, 29, 72), font=f)
    out = Path(re.sub(r'(_side)?\.png$', '', a.out)); out.parent.mkdir(parents=True, exist_ok=True)   # nhận cả -o X lẫn -o X_side.png
    side.save(str(out) + '_side.png')
    # chồng ảnh: canh trái-trên, cắt theo phần chung
    W2, H2 = min(di.width, ai.width), min(di.height, ai.height)
    dc, ac = di.crop((0, 0, W2, H2)), ai.crop((0, 0, W2, H2))
    Image.blend(ac, dc, .5).save(str(out) + '_overlay.png')
    diff = ImageChops.difference(dc, ac).convert('L').point(lambda v: 255 if v > a.threshold else 0)
    heat = Image.composite(Image.new('RGB', (W2, H2), (225, 29, 72)), ac.convert('L').convert('RGB'), diff)
    heat.save(str(out) + '_diff.png')
    pct = 100 - diff.histogram()[255] * 100 / (W2 * H2)
    print(f'OK {out}_side.png · _overlay.png · _diff.png · giống {pct:.1f}% (chỉ tham khảo — khác bề ngang {aw - dw:+g} làm phần bên phải lệch theo)')


def annotate(a):
    """Khoanh khung đỏ + số thứ tự lên ảnh app cho các dòng đã thành DIFF. Toạ độ lấy từ báo cáo so khớp (đơn vị → pixel)."""
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'user-guide'))
    from annotate import draw
    res = json.loads(Path(a.report).read_text(encoding='utf-8')) if a.report else {'rows': [], 'boxes': [], 'extras': []}
    A = load(a.actual) if a.actual else None
    sc = a.unit_px or res.get('scale') or (A or {}).get('scale')
    if not sc:                                                # đoán ×1 là khoanh lệch cả trang mà không báo lỗi — thà dừng
        sys.exit('Thiếu tỉ lệ px/đơn vị: truyền --actual <actual.json> hoặc --unit-px (VD 3 cho Android 480 dpi)')
    want = set(a.only.split(','))
    marks, n = [], 0
    pick = json.loads(a.map) if a.map else None              # {"<số dòng 1-based>": "DIFF-...-01"} — chỉ khoanh dòng đã xác nhận
    if a.text or a.rect:                                      # khoanh tay: không cần tra số dòng bảng đo
        pick = pick or {}
        for spec in a.text or []:                             # "regex=nhãn" — khung của phần tử app có chữ khớp (lấy phần tử nhỏ nhất)
            rx, lab = spec.rsplit('=', 1)
            hits = [nd for nd in (A or {}).get('nodes', []) if nd['k'] in ('text', 'input', 'label') and re.search(rx, nd.get('text') or '')]
            if not hits: print('KHÔNG thấy phần tử khớp:', rx); continue
            nd = min(hits, key=lambda nd: nd['rect'][2] * nd['rect'][3]); n += 1
            x, y, w, h = nd['rect']; marks.append({'box': [x * sc, y * sc, w * sc, h * sc], 'n': n, 'label': lab})
        for spec in a.rect or []:                             # "x,y,w,h=nhãn" — đơn vị dp/pt/px như actual.json
            xywh, lab = spec.split('=', 1); x, y, w, h = (float(v) for v in xywh.split(',')); n += 1
            marks.append({'box': [x * sc, y * sc, w * sc, h * sc], 'n': n, 'label': lab})
    for k, r in enumerate(res['rows'] + [dict(b, design=b['box']) for b in res['boxes']], 1):
        key = str(k) if k <= len(res['rows']) else 'B' + str(k - len(res['rows']))
        if pick is not None and key not in pick: continue
        if pick is None and r['status'] not in want: continue
        n += 1
        if r.get('arect'):
            x, y, w, h = r['arect']
        else:                                                 # thiếu trên app → khoanh chỗ đáng lẽ phải có
            x, y, w, h = r['drect']; y = y - res['design_top'] + res['actual_top'] + res.get('offset', 0)
            x = x * res['actual_w'] / res['design_w']
        lab = pick[key] if pick else f"{LABEL[r['status']]}: {(r.get('design') or r.get('actual'))[:28]}"   # không emoji — font vẽ ảnh không có glyph
        marks.append({'box': [x * sc, y * sc, w * sc, h * sc], 'n': n, 'label': lab})
    for r in (res['extras'] if pick is None and 'extra' in want else []):
        n += 1; x, y, w, h = r['arect']
        marks.append({'box': [x * sc, y * sc, w * sc, h * sc], 'n': n, 'label': 'Thừa trên app: ' + r['actual'][:28]})
    png = Path(a.png).resolve(); out = Path(a.out).resolve()
    from PIL import Image
    spec = {'image': str(png), 'out': str(out), 'marks': marks, 'scale': max(1, Image.open(png).width / 600)}
    if a.caption: spec['caption'] = a.caption
    draw(spec, Path('/'))
    print('đã khoanh', n, 'vùng — MỞ LẠI ẢNH xác nhận khung đúng chỗ')


def sections(a):
    """Dựng mục 4 "Chi tiết từng khung" của báo cáo từ các <mã>_match.md — page nhiều khung không phải chép tay.
    spec JSON: [{"title": "U-05 · Add user", "note": "> …", "images": [["Figma | App", "evidence/U-05_side.png"]],
                 "matches": [["đoạn 1", "reports/…/U-05p1_match.md"]], "redact": [["regex", "<đã che>"]]}]"""
    spec = json.loads(Path(a.spec).read_text(encoding='utf-8'))
    out = []
    for fr in spec:
        out.append(f"### {fr['title']}\n")
        if fr.get('note'): out.append(fr['note'] + '\n')
        for alt, img in fr.get('images', []): out.append(f"![{alt}]({img})\n")
        for label, mp in fr.get('matches', []):
            body = [l for l in Path(mp).read_text(encoding='utf-8').splitlines()[1:] if 'Bảng này là **dữ liệu đo**' not in l]
            for rx, rep in fr.get('redact', []): body = [re.sub(rx, rep, l) for l in body]
            while body and not body[0].strip(): body.pop(0)
            out += [f"<details><summary>Bảng đo tự động{(' — ' + label) if label else ''} (dc.py match)</summary>\n",
                    '\n'.join(body).rstrip() + '\n', '</details>\n']
    Path(a.out).write_text('\n'.join(out), encoding='utf-8')
    print('OK', a.out, '·', len(spec), 'khung — dán vào mục 4 của báo cáo')

def mask(a):
    """Che (làm vỡ hạt) vùng của phần tử có chữ khớp regex — dữ liệu cá nhân trước khi đưa ảnh vào docs/ (rule mục 7)."""
    from PIL import Image
    A = load(a.actual); sc = A.get('scale', 1)
    img = Image.open(a.png).convert('RGB')
    rx = re.compile(a.pattern)
    n = 0
    for nd in A['nodes']:
        if nd['k'] in ('text', 'input', 'label') and rx.search(nd.get('text') or ''):
            x, y, w, h = (int(round(v * sc)) for v in nd['rect'])
            box = (max(0, x), max(0, y), min(img.width, x + w), min(img.height, y + h))
            if box[2] - box[0] < 2 or box[3] - box[1] < 2: continue
            reg = img.crop(box); small = reg.resize((max(1, reg.width // 18), max(1, reg.height // 18)))
            img.paste(small.resize(reg.size, Image.NEAREST), box); n += 1
    img.save(a.out)
    print(f'OK {a.out} · đã che {n} vùng — MỞ LẠI ẢNH xác nhận')


def color(a):
    from PIL import Image
    img = Image.open(a.png).convert('RGB')
    r = [float(v) * a.unit_px for v in a.rect.split(',')]
    bg, fg = sample(img, r)
    print(json.dumps({'nen': bg, 'chu_hoac_vien': fg}, ensure_ascii=False))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    x = s.add_parser('android-tree'); x.add_argument('xml'); x.add_argument('--density', type=float, required=True)
    x.add_argument('--top-px', type=float, default=0, help='chiều cao status bar (px) — adb shell dumpsys window | grep statusBars')
    x.add_argument('--bottom-px', type=float, default=0, help='chiều cao thanh điều hướng (px)'); x.add_argument('--png'); x.add_argument('-o', '--out')
    x.set_defaults(fn=android_tree)
    x = s.add_parser('ios-tree'); x.add_argument('xml'); x.add_argument('--scale', type=float, required=True)
    x.add_argument('--top', type=float, default=0); x.add_argument('--bottom', type=float, default=0); x.add_argument('--png'); x.add_argument('-o', '--out')
    x.set_defaults(fn=ios_tree)
    x = s.add_parser('match'); x.add_argument('design'); x.add_argument('actual'); x.add_argument('-o', '--out', required=True)
    x.add_argument('--tol', type=float, default=4); x.add_argument('--tol-size', type=float, default=0.5)
    x.add_argument('--de-text', type=float, default=6); x.add_argument('--de-fill', type=float, default=3)
    x.add_argument('--design-top', type=float); x.add_argument('--actual-top', type=float)
    x.add_argument('--auto-offset', action='store_true', help='màn đã cuộn: bù độ lệch dọc chung bằng trung vị các cặp khớp chữ')
    x.add_argument('--redact', action='append', help='regex chữ cần che trong bảng đo (email/sđt/tên người thật) — lặp được; ảnh thì dùng lệnh mask')
    x.add_argument('--sample', action='append', help='chữ dữ liệu mẫu trong thiết kế (VD tên người trong hộp thoại) — coi như ô động; lặp được')
    x.set_defaults(fn=match)
    x = s.add_parser('visual'); x.add_argument('design_png'); x.add_argument('actual_png'); x.add_argument('-o', '--out', required=True)
    x.add_argument('--design'); x.add_argument('--actual'); x.add_argument('--design-w', type=float); x.add_argument('--actual-w', type=float)
    x.add_argument('--design-top', type=float); x.add_argument('--actual-top', type=float); x.add_argument('--unit-px', type=float, default=2)
    x.add_argument('--threshold', type=int, default=48); x.add_argument('--match', help='<tên>_match.json của đoạn cuộn (--auto-offset) — cắt Figma theo độ lệch dọc chung'); x.add_argument('--clip', action='store_true', help='cắt ảnh thiết kế theo chiều cao màn thật')
    x.set_defaults(fn=visual)
    x = s.add_parser('render'); x.add_argument('design'); x.add_argument('-o', '--out', required=True)
    x.add_argument('--unit-px', type=float, default=3, help='px ảnh trên mỗi đơn vị — để bằng mật độ ảnh app thì đặt cạnh không phải co giãn')
    x.set_defaults(fn=render)
    x = s.add_parser('annotate'); x.add_argument('report', nargs='?', help='<tên>_match.json — bỏ trống khi chỉ khoanh tay bằng --text/--rect')
    x.add_argument('--png', required=True); x.add_argument('-o', '--out', required=True)
    x.add_argument('--actual', help='actual.json — cần cho --text'); x.add_argument('--text', action='append', help='"regex=nhãn" — khoanh phần tử app có chữ khớp; lặp được')
    x.add_argument('--rect', action='append', help='"x,y,w,h=nhãn" theo đơn vị dp/pt/px; lặp được')
    x.add_argument('--only', default='diff,missing'); x.add_argument('--map', help='JSON {"3": "DIFF-AUTH-01", "B2": "DIFF-AUTH-02"}')
    x.add_argument('--unit-px', type=float); x.add_argument('--caption'); x.set_defaults(fn=annotate)
    x = s.add_parser('sections'); x.add_argument('spec'); x.add_argument('-o', '--out', required=True); x.set_defaults(fn=sections)
    x = s.add_parser('mask'); x.add_argument('png'); x.add_argument('--actual', required=True); x.add_argument('--pattern', required=True)
    x.add_argument('-o', '--out', required=True); x.set_defaults(fn=mask)
    x = s.add_parser('color'); x.add_argument('png'); x.add_argument('--rect', required=True); x.add_argument('--unit-px', type=float, default=1)
    x.set_defaults(fn=color)
    x = s.add_parser('deltae'); x.add_argument('c1'); x.add_argument('c2')
    x.set_defaults(fn=lambda a: print(round(delta_e(a.c1, a.c2), 2)))
    a = p.parse_args(); a.fn(a)


if __name__ == '__main__':
    main()
