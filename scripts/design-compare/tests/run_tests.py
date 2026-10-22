"""Kiểm thử hồi quy cho dc.py match — dữ liệu thật của các lượt chạy 20-10-2026 (app Hybrid Android, Figma wireframe 412 dp):
page AUTH (A-…), USER (U-…), BOOK (B-…). Số điện thoại trong fixture đã thay bằng số giả cùng khuôn.

    python scripts/design-compare/tests/run_tests.py            # chạy, báo PASS/FAIL
    python scripts/design-compare/tests/run_tests.py --update   # ghi lại expected.json SAU KHI đã xem tay kết quả mới là đúng

Mỗi ca kiểm 2 lớp: (1) tổng số theo trạng thái khớp expected.json — bắt mọi thay đổi hành vi;
(2) khẳng định ngữ nghĩa — các bẫy đã gặp trên máy thật, KHÔNG được sửa expected để né.
"""
import json, subprocess, sys, tempfile
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding='utf-8', errors='replace')
HERE = Path(__file__).resolve().parent
FX = HERE / 'fixtures'
DC = HERE.parent / 'dc.py'

CASES = {  # tên: (figma, actual, tham số thêm)
    'A-01': ('figma_6-123.json', 'A-01_actual.json', ['--actual-top', '40']),
    'A-02': ('figma_6-168.json', 'A-02_actual.json', ['--actual-top', '40']),
    'A-03p1': ('figma_6-220.json', 'A-03p1_actual.json', ['--actual-top', '40']),
    'A-03p2': ('figma_6-220.json', 'A-03p2_actual.json', ['--actual-top', '40', '--auto-offset']),
    'A-04': ('figma_6-317.json', 'A-04_actual.json', ['--actual-top', '40']),
    'A-05': ('figma_6-405.json', 'A-05_actual.json', ['--actual-top', '40']),
    'A-06': ('figma_6-497.json', 'A-06_actual.json', ['--actual-top', '40']),
    'U-01': ('figma_7-570.json', 'U-01_actual.json', ['--actual-top', '40']),
    'U-03': ('figma_7-990.json', 'U-03_actual.json', ['--actual-top', '40']),
    'U-05p1': ('figma_7-1373_dialog.json', 'U-05p1_actual.json', ['--actual-top', '40']),
    'U-06': ('figma_7-1608_dialog.json', 'U-06_actual.json', ['--actual-top', '40', '--sample', 'b' * 44]),
    'U-09': ('figma_7-2243.json', 'U-09_actual.json', ['--actual-top', '40']),
    'B-01': ('figma_9-570.json', 'B-01_actual.json', ['--actual-top', '40', '--sample', 'Danh mục A', '--sample', 'Danh mục B', '--sample', 'Danh mục C']),
    'B-08p1': ('figma_9-1555.json', 'B-08p1_actual.json', ['--actual-top', '40', '--sample', 'Tên sách mẫu', '--sample', 'ten-sach-mau',
                                                           '--sample', 'Danh mục A', '--sample', '50000', '--sample', '50.000 VNĐ']),
    'B-09': ('figma_9-1705_dialog.json', 'B-09_actual.json', ['--actual-top', '40', '--auto-offset', '--sample', 'Tên sách mẫu']),
}


def row(res, text):
    return next(r for r in res['rows'] if r['design'] == text)


def semantics(name, res):
    """Mỗi khẳng định ứng với một bẫy đã gặp — xem skill mục 'Bẫy đã gặp'."""
    out = []
    ok = lambda cond, msg: out.append((cond, msg))
    if name == 'A-06':  # hai ô động thuần không được ghép chéo
        ok(row(res, '<Tên tài khoản>').get('actual') == 'Anh Tester Example', 'placeholder <Tên> ghép đúng tên')
        ok(row(res, '<email tài khoản>').get('actual') == 'anhtester@example.com', 'placeholder <email> ghép đúng email')
        ok(not res['extras'], 'node cha gộp chữ con không bị báo thừa')
    if name == 'A-05':  # bottom nav neo đáy, không xô theo nội dung
        ok('neo đáy' in row(res, 'Dashboard').get('anchor', ''), 'bottom nav đo theo neo đáy')
        ok(row(res, 'total: <n> users')['status'] == 'na', 'chữ WebView gộp → ❔ chứ không phải thiếu')
        ok(row(res, 'Login successfully.')['status'] == 'missing', 'toast không có lúc chụp → thiếu (người soát quyết ❔)')
    if name == 'A-01':  # tiền tố (dấu * ở span riêng) vẫn đo vị trí; khối ô nhập chọn đúng khung cha
        ok(row(res, 'Email address *').get('match') == 'prefix' and 'dy' in row(res, 'Email address *'), 'tiền tố vẫn có Δy')
        ok(all(b['status'] == 'ok' for b in res['boxes']), 'ô nhập + nút ghép đúng khung, co giãn được bù')
    if name == 'A-02':
        ok(not res['extras'], 'câu lỗi nằm trong hint ô nhập không bị báo thừa lần 2')
    if name == 'A-03p1':  # phần tử bị mép màn cắt dở là ngoài màn, không phải thiếu
        ok(row(res, 'Password Confirmation *')['status'] == 'offscreen', 'phần tử bị mép màn cắt → ⤵️')
    if name == 'A-03p2':  # header sticky đứng yên, phần đã cuộn đi không ghép nhầm
        ok(row(res, 'Need help?')['status'] == 'na', 'header cố định → ❔ đã đo ở đoạn đầu')
        ok(row(res, 'Sign up')['status'] == 'offscreen', 'tiêu đề đã cuộn đi → ⤵️, không ghép nhầm "Sign in"')
        # độ cuộn thật (so cùng node giữa 2 đoạn) = −225 dp; đoạn 1 đã lệch bố cục ~+55 → lệch dọc chung ≈ −171
        ok(abs(res['offset'] + 171) <= 3, 'lệch dọc chung ≈ −171 dp (độ cuộn −225 + lệch tích luỹ ~+55)')
        ok(not res['extras'], 'chữ khuất sau header không bị báo thừa')
    rows = lambda text: [r for r in res['rows'] if r['design'] == text]
    if name == 'U-01':  # hàng lặp = danh sách: chữ trong hàng là dữ liệu mẫu
        ok(row(res, 'Nguyễn Văn An')['status'] == 'na', 'chữ trong UserRow lặp → ❔ dữ liệu mẫu, không báo thiếu')
        ok(row(res, 'Phone').get('actual') == 'Phone', 'đầu cột Phone vẫn ghép được dù bị đẩy ra mép phải')
    if name == 'U-03':  # chữ trùng nhau ghép theo thứ tự dọc, không giẫm lên nhau
        eq = [r.get('arect') for r in rows('Equals (=)')]
        ok(len(eq) == 2 and all(eq) and eq[0][1] < eq[1][1], 'hai "Equals (=)" ghép 2 phần tử khác nhau, đúng thứ tự trên → dưới')
        ok(row(res, 'Clear filter')['status'] == 'missing', 'nút không có trên app → 🔍 thiếu')
    if name == 'U-05p1':  # mất dấu phân cách là khác nội dung, không được nuốt thành "khớp"
        al = next(r for r in res['rows'] if r['design'].startswith('Allowed'))
        ok(al['status'] == 'diff', 'dòng định dạng ảnh thiếu dấu phẩy → ❌')
    if name == 'U-06':  # thiết kế lược bớt: tắt so vị trí, vẫn so chữ
        ok(bool(res.get('abridged')), 'nhận ra ghi chú "lược bớt" của thiết kế')
        ok(not any('dy' in r for r in res['rows']), 'khung lược bớt không có Δy nào')
        ok(row(res, 'Name must be less than 250 characters.')['status'] == 'ok', 'thông báo lỗi vẫn so nguyên văn')
        ok(any(r['design'].startswith('<mẫu:') and r['status'] == 'ok' for r in res['rows']), '--sample: chuỗi mẫu dài khớp theo khuôn')
    if name == 'U-09':  # phần tử bị đẩy gần mép phải vẫn ghép được để người soát thấy Δx
        nd = row(res, 'No Data')
        ok(nd['status'] == 'diff' and nd['arect'][0] >= 400, '"No Data" lệch sang mép phải (x ≥ 400) → ❌')
    if name == 'B-01':  # thẻ lặp (BookCard) = danh sách
        ok(row(res, 'Tên sách mẫu')['status'] == 'na', 'chữ trong BookCard lặp → ❔')
    if name == 'B-08p1':  # cùng chữ xuất hiện 2 lần: tiêu đề có, breadcrumb sai → lần thứ hai phải thiếu
        mb = rows('Modify book')
        ok(len(mb) == 2 and mb[0].get('actual') == 'Modify book' and mb[1]['status'] == 'missing',
           'breadcrumb "Modify book" bị thay chữ → 🔍, không ghép nhầm vào tiêu đề')
    if name == 'B-09':  # ô mẫu trong câu không được che mất việc app bỏ trống tên
        st = next(r for r in res['rows'] if r['design'].startswith('Do you want delete'))
        ok(st['status'] == 'diff' and st.get('match') != 'placeholder', 'câu xác nhận thiếu tên sách → ❌, không coi là khớp khuôn')
    return out


def main():
    update = '--update' in sys.argv
    exp_path = HERE / 'expected.json'
    expected = json.loads(exp_path.read_text(encoding='utf-8')) if exp_path.exists() else {}
    got, fails = {}, 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, (fg, ac, extra) in CASES.items():
            out = Path(tmp) / name
            subprocess.run([sys.executable, str(DC), 'match', str(FX / fg), str(FX / ac), '-o', str(out), *extra],
                           check=True, capture_output=True)
            res = json.loads((Path(str(out) + '.json')).read_text(encoding='utf-8'))
            got[name] = dict(sorted(res['summary'].items()))
            if not update and expected.get(name) != got[name]:
                fails += 1; print(f'FAIL {name} tổng trạng thái: {got[name]} ≠ {expected.get(name)}')
            for cond, msg in semantics(name, res):
                if not cond: fails += 1
                print(('PASS ' if cond else 'FAIL ') + f'{name} · {msg}')
    if update:
        exp_path.write_text(json.dumps(got, ensure_ascii=False, indent=1), encoding='utf-8'); print('đã ghi expected.json')
    print('—' * 40); print('KẾT QUẢ:', 'PASS' if not fails else f'{fails} FAIL')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
