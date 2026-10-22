# scripts/design-compare — so thiết kế Figma với UI thật

Bộ công cụ của skill [`skills-figma-design-comparator`](../../.claude/skills/skills-figma-design-comparator/SKILL.md) · workflow `/compare-ui-from-figma-design` (Mode **WEB** / **MOBILE**) · rule [`design_compare_rules.md`](../../.claude/rules/design_compare_rules.md). Không gắn với hệ thống nào.

| File | Chạy ở đâu | Làm gì |
|---|---|---|
| `figma_extract.js` | Tool `use_figma` của Figma MCP (dán nội dung vào `code`) | **CHỈ ĐỌC.** `FRAME_IDS = []` → liệt kê mọi page + khung (kể cả khung trong section) · `FRAME_IDS = ['<id>', …]` → spec JSON từng khung: chữ (kể cả chữ trong component), toạ độ tương đối khung, cỡ/độ đậm/font/line-height, màu chữ, khối có nền/viền + bo góc. `SCOPE = '<tên khối>'` → chỉ lấy lớp phủ (menu, dialog). `COMPACT = true` → định dạng gọn, 3–4 khung một lần gọi |
| `collect_dom.js` | `browser_evaluate` của Playwright MCP, kèm `filename` | Spec JSON của trang web thật — computed style, **font thực sự được vẽ** (dò trong font-stack), khung chữ đo bằng Range. Bề ngang khung = `clientWidth` (trừ thanh cuộn); ghi `overflow_x` (trang tràn ngang) và `cut` (chữ bị cắt `…`). `ROOT_SELECTOR` để đo riêng dialog/menu |
| `dc.py` | Python 3.9+ · `pip install pillow` | Dựng spec từ page source mobile · so khớp · ảnh đặt cạnh nhau · dựng ảnh Figma từ JSON · khoanh DIFF · che dữ liệu · ghép mục báo cáo · lấy mẫu màu · ΔE |

## `dc.py` — lệnh con

```bash
# Spec của app từ page source (đơn vị dp/pt); --png bật lấy mẫu màu chữ/nền trên ảnh
python scripts/design-compare/dc.py android-tree source.xml --density 480 --top-px 159 --bottom-px 72 --png app.png -o actual.json
python scripts/design-compare/dc.py ios-tree source.xml --scale 3 --top 59 --bottom 34 --png app.png -o actual.json

# So khớp → <tên>.json (dữ liệu) + <tên>.md (bảng đọc được)
python scripts/design-compare/dc.py match figma.json actual.json -o out/A-01_match
#   --actual-top 40    mốc dọc = ĐỈNH HEADER của app (không phải status bar) — rule mục 3. Thiết kế tự lấy đáy khối StatusBar
#   --tol 4            dung sai vị trí/kích thước (web: 2)
#   --tol-size 0.5     cỡ chữ        --de-text 6 / --de-fill 3   ngưỡng ΔE2000 chữ / nền (web chữ: 3)
#   --auto-offset      đoạn màn ĐÃ CUỘN — lệch dọc chung (độ cuộn + lệch tích luỹ) từ cặp chữ trùng nguyên văn, bỏ phần tử cố định
#   --sample "Tên mẫu" chữ dữ liệu mẫu của thiết kế → ô động, so khuôn (lặp được). Danh sách lặp tự nhận, không cần khai
#   --redact "<regex>" che chữ của app (email/sđt/tên người thật) trong cả .md và .json (lặp được)

# Ảnh cho người soát: <tên>_side.png (Figma | App) · _overlay.png (chồng 50 %) · _diff.png (bản đồ khác biệt)
python scripts/design-compare/dc.py visual figma.png app.png --design figma.json --actual actual.json --actual-top 40 -o out/A-01
#   --match out/A-03p2_match.json   đoạn đã cuộn: cắt ảnh Figma theo độ lệch dọc chung (chỉ khi lệch âm = đã cuộn)

# Không có ảnh Figma (hết hạn mức MCP, file khoá xuất ảnh): dựng ảnh sơ đồ từ JSON — khối + chữ đúng toạ độ, cỡ, màu
python scripts/design-compare/dc.py render figma.json -o figma_render.png [--unit-px 3]

# Khoanh khung đỏ + nhãn DIFF lên ảnh app — chỉ DIFF đã xác nhận. Trộn được 3 cách trong một lệnh:
python scripts/design-compare/dc.py annotate --png app.png --actual actual.json -o evidence/B-08_marked.png \
       --text "^Create a new book$=DIFF-BK-BOOK-08" \
       --rect "272,216,160,224=DIFF-BK-BOOK-04"
#   --text "regex=nhãn"   khoanh phần tử app có chữ khớp (phần tử nhỏ nhất)
#   --rect "x,y,w,h=nhãn" vùng theo đơn vị dp/pt/px — cần --actual hoặc --unit-px, thiếu thì lệnh dừng
python scripts/design-compare/dc.py annotate out/A-01_match.json --png app.png -o evidence/A-01_marked.png \
       --map '{"3": "DIFF-AUTH-01", "B2": "DIFF-AUTH-02"}'   # theo số dòng / mã khối của bảng đo

# Che dữ liệu cá nhân trên ảnh (làm vỡ hạt vùng phần tử có chữ khớp regex)
python scripts/design-compare/dc.py mask app.png --actual actual.json --pattern "gmail\.com|^0[0-9]{9}$" -o app_masked.png

# Mục 4 "Chi tiết từng khung" của báo cáo — ghép các <mã>_match.md theo một file JSON mô tả khung
python scripts/design-compare/dc.py sections frames.json -o sections.md
#   frames.json: [{"title": "B-05 · Chi tiết sách", "note": "> …", "images": [["Figma | App", "evidence/B-05_side.png"]],
#                  "matches": [["đoạn 1", "reports/…/B-05p1_match.md"]], "redact": [["[\\w.+-]+@gmail[.]com", "<email đã che>"]]}]

python scripts/design-compare/dc.py color app.png --rect 120,437,368,28 --unit-px 3   # màu nền + màu chữ trong vùng (đơn vị × unit-px)
python scripts/design-compare/dc.py deltae "#42bc40" "#43bd41"                         # ΔE2000
```

## Cách `match` ghép và đo

1. **Ghép chữ**: nguyên văn → khác ký tự trình bày (nháy cong/thẳng, hoa-thường, khoảng trắng) → khuôn `<…>` / `--sample` (đoán kiểu dữ liệu: email, số, tên, ngày, giờ, URL, số điện thoại) → tiền tố → chứa nhau (app gộp/tách node) → gần giống ≥ 60 %. Chữ trùng nhau (hai ô *Equals (=)*) ghép theo thứ tự trên → dưới
2. **Danh sách lặp** (hàng/thẻ cùng tên, cùng cỡ, chứa ≥ 2 chữ — `UserRow`, `BookCard`…): chữ bên trong là dữ liệu mẫu → ❔, chữ app trong vùng danh sách không bị báo thừa
3. **Lớp phủ** (`SCOPE`): chọn khối app chứa nhiều chữ khớp nhất (theo quan hệ cha–con của cây), chỉ so trong khối đó, đo tương đối góc lớp phủ
4. **Δx** thử 4 kiểu neo (trái · phải · giữa · tỉ lệ; thêm "tâm" khi khung app lớn hơn chữ) vì màn thật thường rộng khác khung Figma
5. **Δy** tính từ mốc dọc; **Δ khoảng cách** tới phần tử khớp ngay phía trên chỉ ra **chỗ khởi phát** xô lệch — phần tử chỉ kế thừa độ lệch không bị tính lỗi lại. Phần tử neo đáy (bottom nav) đo tới đáy màn hình
6. **Thiết kế lược bớt** (ghi chú *"lược bớt / rút gọn"*): tắt so vị trí, chỉ so chữ + màu. Dòng ghi chú của designer (`(…)` dài, `… …`) → ❔
7. **Màu**: web đọc computed; mobile lấy mẫu ảnh — nền = màu nhiều nhất trong khung, chữ = màu nhiều nhất trong số pixel khác hẳn nền
8. **Khối** (nút, card, ô nhập): ghép qua chữ nằm bên trong, ưu tiên khung có diện tích gần nhất — heuristic, luôn xem ảnh

Bảng đo là **dữ liệu**, không phải kết luận — người soát xác nhận trên `_side.png` rồi mới ghi DIFF.

## Sửa `dc.py` → chạy kiểm thử hồi quy

```bash
python scripts/design-compare/tests/run_tests.py
```

`tests/fixtures/` là spec thật của **15 lượt đo** ngày 20-10-2026 — page AUTH (A-01 → A-06, trang dài 2 đoạn), USER (danh sách, bộ lọc có chữ trùng, hộp thoại lớp phủ, khung lược bớt + `--sample`, trạng thái rỗng) và BOOK (thẻ lặp, breadcrumb sai chữ, câu xác nhận thiếu dữ liệu). Số điện thoại trong fixture đã thay bằng số giả cùng khuôn. `run_tests.py` kiểm tổng trạng thái từng ca **và** các khẳng định ứng với bẫy đã gặp trên máy thật (placeholder ghép chéo, header sticky, phần tử bị mép màn cắt, node WebView gộp chữ, chữ trùng ghép nhầm, ô mẫu che mất lỗi thiếu dữ liệu…). Thay đổi hành vi có chủ đích → xem tay kết quả mới rồi mới `--update` expected; **không** sửa khẳng định để né.

## Đã kiểm chứng

| Ngày | Nền tảng | Kết quả |
|---|---|---|
| 20-10-2026 | Android 17 emulator (Pixel 10 Pro XL, density 480, 448 dp) · app Hybrid Capacitor (WebView không debug) · Figma wireframe 412 dp | **26 khung / 3 page** (AUTH 8 · USER 9 · BOOK 9) → `docs/design-reviews/_book-api/`. Form, validation, toast, trang dài nhiều đoạn có header sticky, hộp thoại cuộn bên trong, menu lớp phủ, danh sách lặp, trạng thái rỗng, khung lược bớt, khung theo vai trò (khách / đăng nhập), ảnh Figma dựng lại bằng `render` khi hết hạn mức MCP, che dữ liệu bằng `mask` + `--redact` |
| 20-10-2026 | Web (Chrome qua Playwright MCP 1600×750) | `collect_dom.js` qua `browser_evaluate` → bề ngang `clientWidth` (1585 khi có thanh cuộn), font thật dò đúng (`Segoe UI` từ stack `-apple-system, …`), cờ `cut` · `overflow_x`. **Chưa** có lượt so với khung Figma web thật |
| 20-10-2026 | iOS — page source XCUITest mẫu | `ios-tree` dựng spec đúng; **chưa** chạy trên máy iOS thật (cần macOS) |
