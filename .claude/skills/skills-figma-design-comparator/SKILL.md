---
name: skills-figma-design-comparator
description: Skill so bản thiết kế Figma với giao diện đã xây dựng thật — web (Playwright MCP) và app mobile Android/iOS/Hybrid (Appium MCP). Trích spec Figma bằng script chỉ-đọc (chữ, toạ độ, font, màu), thu cây phần tử + ảnh của UI thật, đo lệch theo đơn vị dp/pt/px có neo theo bề ngang màn hình, rồi người soát xác nhận trên ảnh đặt cạnh nhau trước khi ghi thành DIFF có loại · mức độ · ai xử lý. Dùng khi tester cần biết app/web có làm đúng thiết kế không, soát UI trước release, review pixel-perfect, đối chiếu mockup với bản build, kiểm màn hình theo Figma — kể cả khi user chỉ dán link figma.com và hỏi "app đã đúng design chưa".
---

# Figma Design Comparator

Purpose: Trả lời câu hỏi **"giao diện đã xây có đúng bản thiết kế không — lệch ở đâu, lệch bao nhiêu, ai phải sửa"** bằng số đo thật và ảnh đối chiếu, không bằng cảm giác nhìn hai ảnh.

Quy tắc bắt buộc (dung sai, đơn vị, phân loại DIFF, cấm): [`.claude/rules/design_compare_rules.md`](../../rules/design_compare_rules.md) — đọc trước khi đo.
Công cụ: [`scripts/design-compare/`](../../../scripts/design-compare/README.md) — `figma_extract.js` · `collect_dom.js` · `dc.py`.

---

## When to Use

- Có link Figma (khung màn hình) và một bản build web / app chạy được — cần biết làm đúng thiết kế chưa
- Soát UI trước release, sau khi dev báo "đã làm theo design", hoặc khi designer cập nhật Figma
- Đối chiếu một luồng nhiều màn (đăng nhập → dashboard → menu…) với bộ khung Figma tương ứng

**Không dùng khi:**

| Việc | Dùng cái khác |
|---|---|
| Đọc Figma để **rút requirements** (field, rule, message) | `skills-requirements-analyzer` mục 3.3 — Figma là tài liệu đầu vào, không phải chuẩn để chấm |
| So ảnh chụp **phiên bản app này với phiên bản trước** (visual regression) | Snapshot test của framework automation — đó là so app với chính nó |
| Dựng / sửa thiết kế trong Figma | Các skill Figma (`figma-use`…) — skill này **chỉ đọc** Figma |

---

## Chọn cách chạy — theo việc tester cần

Không phải lần nào cũng chạy đủ cả page. Chọn kiểu chạy **trước** Bước 1 — kiểu chạy quyết định có ghi `docs/` không và lấy mã DIFF thế nào:

| Tester cần | Kiểu chạy | Làm gì khác so với mặc định |
|---|---|---|
| Soát cả page / cả luồng | **Đầy đủ** (mặc định) | 6 bước, báo cáo + evidence vào `docs/design-reviews/`, cấp mã DIFF |
| Chỉ vài màn | **Chọn khung** — `khung=A-01,A-03` | Như đầy đủ, Bản đồ màn hình chỉ liệt kê khung đã chọn; *Phạm vi khung* ghi `n/m` |
| "Màn này đúng design chưa?" — hỏi nhanh, chưa cần lưu | **Xem nhanh** — `nhanh` | Bước 1–5 cho 1–2 khung; trả lời trong chat bằng ảnh đặt cạnh nhau + danh sách lệch **chưa cấp mã**. Không ghi `docs/`. User muốn lưu → chạy lại kiểu đầy đủ |
| Dev/designer báo đã sửa | **So lại** — `khung=còn-mở` | Chỉ các khung còn DIFF 🔴 Mở ở lần trước; thư mục `run_*` mới; giữ mã, đổi trạng thái (rule mục 6 — vòng đời) |
| Lượt trước bỏ dở vài khung, **cùng ngày, cùng bản build** | **Bổ sung** — `bổ sung` | Ghi thêm vào **chính** `run_*` gần nhất: dòng *Ngày chạy* thêm khoảng giờ bổ sung, cập nhật Tóm tắt / Bản đồ / mục 5. Khác bản build → phải là lượt **mới** |
| Có Figma nhưng không đưa app tới được trạng thái | Như trên + ❔ | Khung đó ghi ❔ kèm *cần gì để so* — không bỏ im lặng |

---

## Hai nguồn, một định dạng

Mọi phía đều quy về **spec JSON** cùng cấu trúc — `dc.py` so được bất kỳ cặp nào:

```
Figma ──(use_figma + figma_extract.js, CHỈ ĐỌC)──────────────┐
Web   ──(browser_evaluate + collect_dom.js, filename=…)──────┤→ spec JSON → dc.py match → bảng đo
Android ─(page source + ảnh + dc.py android-tree)──────────┤          dc.py visual → ảnh đặt cạnh nhau / chồng / khác biệt
iOS   ──(page source + ảnh + dc.py ios-tree)──────────────────┘          dc.py annotate → ảnh khoanh DIFF
```

| Nguồn | Có gì | Thiếu gì |
|---|---|---|
| Figma (`figma_extract.js`) | Chữ thật (kể cả chữ trong component), toạ độ tương đối khung, cỡ/độ đậm/font/line-height, màu chữ, màu nền/viền, bo góc | — (nguồn đầy đủ nhất) |
| Web (`collect_dom.js`) | Như Figma — computed style chính xác, khung chữ đo bằng Range (ink box) | Bóng đổ, gradient chỉ biết có/không |
| Android / iOS native | Chữ, khung phần tử (dp/pt) | **Không có** font, cỡ chữ, màu → màu lấy mẫu trên ảnh chụp; cỡ chữ suy từ chiều cao dòng |
| Hybrid WebView không bật debug | Như native — WebView đưa chữ lên cây trợ năng, hay **gộp** chữ của phần tử con | Như native |

> **Vì sao không dùng `get_metadata` / `get_design_context` làm nguồn chính:** `get_metadata` không trả chữ bên trong instance (nút chỉ hiện `name="Label"`), không có màu/font; `get_design_context` trả code React/Tailwind — trích được nhưng phải parse JSX. `figma_extract.js` qua `use_figma` trả thẳng `characters`, `fontSize`, `fills` của từng node — chính xác và gọn. Hai tool kia vẫn dùng để **xem** (ảnh, token biến `get_variable_defs`).

---

## Quy trình 6 bước

### Bước 1 — Bản đồ màn hình (Screen Map)

1. Chạy `figma_extract.js` với `FRAME_IDS = []` → danh sách **mọi page + khung cấp 1**. ⚠️ `get_metadata` không truyền `nodeId` chỉ liệt kê page **đã tải** trong Figma desktop — đừng kết luận file chỉ có 1 page từ đó
2. Lọc khung màn hình thật — bỏ section kit/component, khung caption, note, page header (nhận biết qua tên và kích thước: khung màn mobile ~360–430 rộng, web ~1280–1920)
3. Với mỗi khung: ghi **trạng thái** khung vẽ (mặc định · lỗi validation · đã đăng nhập · menu mở · có toast…) và **cách đưa app tới đúng trạng thái đó** (đường điều hướng, dữ liệu cần nhập, tài khoản cần dùng). Đọc `docs/requirements/_discovery/system_map.md` của dự án để có đường điều hướng — không tự dò lại
4. Khai báo **độ trung thực** (rule mục 2) — wireframe hay mockup quyết định cái gì được tính DIFF
5. **Đọc ghi chú trong khung** trước khi so: *"lược bớt"*, *"dữ liệu mẫu"*, *"đã cuộn xuống phần …"*, *"full scroll"*, vai trò (*khách / đã đăng nhập*). Mỗi ghi chú đổi cách đo (rule mục 5) — bỏ qua là ra hàng chục DIFF giả
6. **Ước lượng lượt gọi Figma MCP** — gói Starter giới hạn số lượt gọi; hết giữa chừng thì mất ảnh các khung còn lại. Cần ≈ `1` (liệt kê) + `⌈số khung ÷ 4⌉` (trích spec) + `số khung` (ảnh). Page lớn → trích + lấy ảnh **mọi** khung ngay đầu phiên, lưu vào `reports/`, các bước sau chỉ đọc file

| Mã khung | Tên khung Figma | node-id | Trạng thái vẽ | Cách tới trên app | Đạt được? |
|---|---|---|---|---|---|
| A-01 | Sign in | `6:123` | Mặc định, ô trống | Avatar → *Sign in* | ✅ |
| A-02 | Sign in — validation | `6:168` | Bấm Login khi để trống | A-01 + bấm *Login account* | ✅ |

Khung không đưa app tới được (cần dữ liệu đặc biệt, quyền admin không có) → ❔ kèm lý do ở báo cáo, **không** bỏ qua im lặng.

### Bước 2 — Trích spec Figma

Mỗi khung trong phạm vi:

1. `figma_extract.js` với `FRAME_IDS = ['<id>', …]` (3–4 khung một lần với `COMPACT = true` — tiết kiệm lượt gọi mà kết quả vẫn gọn) → ghi kết quả **nguyên văn** ra `reports/design-compare/<run>/figma_<id>.json` (`:` → `-`). Kết quả có `&lt;` `&gt;` là do tool mã hoá — `dc.py` tự giải mã, không cần sửa tay. Khung vẽ **lớp phủ** (menu, dialog) trên nền màn khác → đặt `SCOPE = '<tên khối lớp phủ>'` (rule mục 5)
2. `get_screenshot` (`contentsOnly: true`) → `curl -f -L -o figma_<id>.png "<url>"` ngay (URL hết hạn nhanh). Ảnh trả về tối đa **1×** kích thước khung — đủ cho ảnh đặt cạnh nhau. Khung cao hơn 1024 → truyền `maxDimension` = chiều cao khung, không thì ảnh bị thu nhỏ
3. Cần token (màu thương hiệu, style chữ) → `get_variable_defs` một lần cho cả file, ghi vào đầu báo cáo

**Hết hạn mức ảnh (`get_screenshot` báo *tool call limit*):** spec đã trích vẫn đủ để đo. Dựng ảnh sơ đồ cho phần đặt cạnh nhau:

```bash
python scripts/design-compare/dc.py render figma_<id>.json -o figma_<id>.png     # khối + chữ đúng toạ độ, cỡ, màu — không có icon/ảnh
```

Evidence đặt tên `_figma_render.png`; báo cáo ghi rõ khung nào dùng ảnh dựng lại, mục 5 ghi việc lấy lại ảnh thật ở lần chạy sau.

**Đường dự phòng — khi `use_figma` không chạy được** (bị từ chối quyền, gói Figma không cho phép): `get_metadata` cho khung + toạ độ (node TEXT thường lấy nội dung làm tên; chữ trong instance **không** có), `get_design_context` cho chữ thật (props `label=…`, nội dung thẻ `<p>`) + class màu/cỡ chữ (`text-[15px]`, `text-[color:…,#hex]`). Dựng tay spec JSON cùng định dạng cho các chữ và khối chính, ghi dòng `Nguồn spec: dự phòng (get_metadata + get_design_context)` vào đầu báo cáo. **Không** đoán số đo khi không có trong dữ liệu.

### Bước 3 — Đưa UI thật về đúng trạng thái & thu dữ liệu

Chi tiết theo nền tảng — đọc **đúng một** file:

- Mobile (Android / iOS / Hybrid): [`references/mobile.md`](references/mobile.md)
- Web: [`references/web.md`](references/web.md)

Chung cho cả hai: đưa về **cấu hình mặc định** trước khi chụp (cỡ chữ hệ thống, dark mode, màu chủ đề người dùng tự chọn, ngôn ngữ) — ghi lại cấu hình vào báo cáo.

### Bước 4 — Đo

```bash
python scripts/design-compare/dc.py match   figma.json actual.json --actual-top <đỉnh header app> -o reports/design-compare/<run>/<mã>_match
python scripts/design-compare/dc.py visual  figma.png  app.png --design figma.json --actual actual.json --actual-top <đỉnh header app> -o reports/design-compare/<run>/<mã>
```

**Mốc dọc** = đỉnh header ở cả hai phía (rule mục 3): thiết kế tự lấy đáy khối `StatusBar`; app truyền `--actual-top` = y của khối header trong spec app (mobile) — đo một lần, dùng cho mọi khung.

| Tình huống | Thêm tham số |
|---|---|
| Thiết kế có dữ liệu mẫu **ngoài** danh sách lặp (tên trong hộp thoại, giá trong form sửa) | `--sample "Tên sách mẫu" --sample "50.000 ₫"` — chữ đó thành ô động, so khuôn. Danh sách lặp (`UserRow` × 5, thẻ lặp) **tự** nhận, không cần khai |
| Đoạn màn **đã cuộn**, hoặc khung vẽ sẵn ở vị trí đã cuộn | `--auto-offset` (match) · `--match <mã>_match.json` (visual — cắt ảnh Figma theo độ cuộn). Màn **không** cuộn mà vẫn lệch dọc → đó là lệch bố cục, đừng dùng `--auto-offset` để "bù" |
| Bảng đo có dữ liệu người thật (email, số điện thoại, tên người khác) | `--redact "<regex>"` — che trong cả `.md` và `.json` |
| Web | `--tol 2 --de-text 3` (đo tới khung chữ thật, màu đọc trực tiếp) |
| Khung lược bớt | Không cần gì — `match` tự nhận ghi chú *"lược bớt / rút gọn"* và tắt so vị trí |

`match` ghép cặp chữ (nguyên văn → khác ký tự trình bày → khuôn `<…>` (đoán kiểu dữ liệu từ tên: `<email…>`, `<n>`, `<ngày>`…) → tiền tố → chứa nhau → gần giống), rồi đo:

| Cột | Nghĩa | Đọc thế nào |
|---|---|---|
| Δx (neo) | Lệch ngang theo kiểu neo khớp nhất (trái · phải · giữa · tỉ lệ · tâm-…) | Neo `tỉ lệ` mà vẫn lệch → phần tử co giãn sai |
| Δy | Lệch dọc tính từ dưới status bar (hoặc từ đáy với phần tử `neo đáy`) | Lớn mà Δ khoảng cách nhỏ → **kế thừa**, không phải lỗi của phần tử này |
| Δ khoảng cách | Khoảng cách tới phần tử khớp ngay phía trên, app trừ thiết kế | **Đây là cột tìm chỗ khởi phát xô lệch** |
| Δ cao | Chiều cao khung app − khung chữ thiết kế | ≥ 0,6 × line-height → xuống dòng khác |
| Màu · ΔE | Màu thiết kế → màu app (web: computed · mobile: lấy mẫu ảnh) | So ngưỡng rule mục 4 |

Bảng khối (B1, B2…) ghép khối có nền/viền qua chữ bên trong — **heuristic**, phải xem ảnh.

### Bước 5 — Soát trên ảnh → quyết định DIFF

**Mở `<mã>_side.png`** (Figma | App). Đi lần lượt từng dòng ❌ ⚠️ 🔍 ➕ ❔ của bảng đo, mỗi dòng trả lời: *thấy bằng mắt không? nguyên nhân thật là gì? thuộc loại nào?*

| Bảng đo báo | Thường là | Xác nhận bằng |
|---|---|---|
| 🔍 Thiếu trên app | Thật sự thiếu · **hoặc** app thay bằng ảnh/icon (chữ "A" của avatar thành ảnh) · **hoặc** trạng thái thoáng qua chưa tái tạo (toast) | Ảnh đặt cạnh nhau |
| ➕ Thừa trên app | Thật sự thừa (khối thiết kế chưa vẽ) · hoặc chữ nằm dưới thanh điều hướng/bị che | Cuộn xem; ảnh app |
| ❔ chung node | WebView gộp chữ (`User mgttotal: 3294 users`) — chữ **có**, chỉ không đo tự động được | Nhìn ảnh: vị trí/màu có lệch thấy rõ không |
| ❌ Δy ở phần tử đầu | Nguyên nhân thường ở khối **không có chữ** phía trên (banner, ảnh, header cao hơn) | Ảnh: khối nào cao hơn → DIFF ghi cho **khối đó** |
| ⚠️/❌ màu ở khối | Thiết kế nền phẳng, app nền gradient/đổ bóng — lấy mẫu một điểm không đại diện | Ảnh; wireframe thì chỉ ghi "tham khảo" |
| ❌ chữ `<mẫu:…>` "khác nội dung" | Dữ liệu thật khác **hình dạng** mẫu (tên có chữ số) — không phải lệch · **hoặc** app bỏ trống đúng chỗ dữ liệu (`delete , after…`) — lệch thật | Đọc cột *Trên app*: còn phần cố định của câu mà thiếu dữ liệu → DIFF |
| 🔍 dấu `/` breadcrumb, chữ trong nút chỉ có icon | Dấu phân cách / icon vẽ bằng ảnh trên app — không có node chữ | Ảnh; không phải DIFF |
| 🔍 ở khung lược bớt | Phần tử có thể nằm ngoài đoạn đã chụp (không suy được vị trí khi tắt so hình học) | Cuộn chụp thêm trước khi kết luận thiếu |
| ❌ Δx rất lớn, phần tử app ở x gần bề ngang màn | Bảng / hàng nút rộng hơn màn, cuộn ngang → phần tử **khuất** | Ảnh: có nhìn thấy không? Không → DIFF `LAYOUT` (rule mục 5) |
| Cùng lệch đã có mã ở module khác | Thành phần dùng chung (header, bottom nav, ô nhập, nút hộp thoại) | Dẫn chiếu mã cũ, **không** cấp mã mới (rule mục 6) |

**Rồi soát tay những thứ máy không đo** (đi hết danh sách cho mỗi màn):

- [ ] Icon: đúng hình, đúng chỗ, đủ số lượng (wireframe: chỉ có/không)
- [ ] Ảnh/banner: có, đúng tỉ lệ khung, không méo, không vỡ
- [ ] Bo góc, viền, đường phân cách, đổ bóng (mockup)
- [ ] Chữ bị cắt `…`, tràn khung, chồng lên nhau
- [ ] Phần tử bị che (bởi bàn phím, bottom nav, status bar)
- [ ] Trạng thái: nút disabled/enabled, ô nhập focus/lỗi — đúng như khung vẽ
- [ ] Thứ tự đọc và căn lề tổng thể của khối

Mỗi dòng xác nhận lệch thật → một `DIFF` (mã nối tiếp theo danh mục, rule mục 6). Nhiều dòng cùng **một nguyên nhân** → **một** DIFF (VD 5 tab bottom nav cùng lệch −6,8 do thanh cao hơn = 1 DIFF cho thanh).

Khoanh ảnh — **chỉ** các dòng đã thành DIFF. Ba cách, dùng chung được trong một lệnh — chọn cách tiện nhất cho từng DIFF:

```bash
# theo CHỮ trên app — tiện nhất, không phải tra số dòng
python scripts/design-compare/dc.py annotate --png <mã>_app.png --actual <mã>_actual.json \
       --text "^Create a new book$=DIFF-BK-BOOK-08" --rect "272,216,160,224=DIFF-BK-BOOK-04" -o evidence/<mã>_<mô_tả>_marked.png
# --rect: theo VÙNG (dp/pt/px như actual.json) — khối không có chữ: menu, bảng, khoảng trống
```

`--rect` cần tỉ lệ px/đơn vị: truyền `--actual` (hoặc `--unit-px 3`) — thiếu thì lệnh dừng chứ không đoán ×1. Ảnh đã che dữ liệu thì khoanh trên **ảnh đã che**. Cách cũ theo **dòng bảng đo** vẫn dùng được:

```bash
python scripts/design-compare/dc.py annotate <mã>_match.json --png <mã>_app.png -o evidence/<mã>_<mô_tả>_marked.png \
       --map '{"3": "DIFF-AUTH-02 Welcome thấp hơn 15dp", "B2": "DIFF-AUTH-03 Tab active nền trắng"}' --caption "A-05 · Dashboard"
```

Khoá của `--map` là số dòng trong bảng đo (`3`) hoặc mã khối (`B2`). **Mở lại ảnh** sau khi khoanh — gom các ảnh khoanh thành một tấm nhỏ để soát một lượt.

### Bước 6 — Ghi báo cáo

Theo mẫu [`references/report_template.md`](references/report_template.md) → `docs/design-reviews/<module>/<nền-tảng>/run_<YYYYMMDD_HHMMSS>/design_compare_report.md` + `evidence/`. Cập nhật danh mục `docs/design-reviews/README.md` (DIFF đã dùng · mã kế tiếp · DIFF mở · bảng *Thành phần dùng chung*).

Mục 4 *Chi tiết từng khung* dán bảng đo của **mọi** đoạn chụp — sinh bằng `dc.py sections frames.json -o sections.md` (mỗi khung: tiêu đề · ghi chú · ảnh · các `<mã>_match.md` · regex che dữ liệu), đừng chép tay. Trước khi ghi `docs/`:

- [ ] Ảnh có dữ liệu người khác → `dc.py mask` (ảnh `_app`, rồi dựng lại `_side` **từ ảnh đã che**); bảng đo → `match --redact`. Mở lại vùng đã che
- [ ] Mọi link `evidence/…` trong báo cáo trỏ tới file có thật
- [ ] Lệch đã có mã ở module khác → dẫn chiếu, không cấp mã mới

---

## Viết một DIFF

```markdown
| DIFF-BK-BOOK-11 | 🔴 Mở | B-09 | CONTENT | Medium | Dev | Câu xác nhận xoá **thiếu tên sách** — người dùng không biết đang xoá sách nào | `Do you want delete , after delete you can't undo` | `Do you want delete <tên sách>, after delete you can't undo` | [side](evidence/B-09_delete_book_confirm_side.png) · [marked](evidence/B-09_delete_book_confirm_marked.png) |
| DIFF-BK-AUTH-08 | 🔴 Mở | A-04 · A-05 | LAYOUT | Medium | Design | Banner cao hơn khung giữ chỗ → mọi khối bên dưới xô xuống | Banner 416 × **218 dp** · tiêu đề thẻ **+28 dp** | 380 × 180 dp (cùng tỉ lệ ở 416 dp = 197 dp) | [side](evidence/A-04_dashboard_guest_side.png) |
```

Ô **Thực tế** và **Thiết kế** ghi **số đo** hoặc **nguyên văn chữ**, không ghi "trông hơi to". Ô **Mô tả** nói hậu quả với người dùng khi có (*"không biết đang xoá sách nào"*) — đó là thứ giúp PO xếp ưu tiên. Nguyên nhân chỉ ghi khi đã xác định trên ảnh/số đo; chưa rõ thì thôi — không suy diễn code của dev. DIFF hành vi giao `Dev` ghi thêm các bước tái hiện + `tái hiện n/n lần`.

---

## Bẫy đã gặp

| Bẫy | Hậu quả | Cách tránh |
|---|---|---|
| `get_metadata` không `nodeId` chỉ liệt kê page đã tải | Tưởng file chỉ có 1 page | Liệt kê bằng `figma_extract.js` (`FRAME_IDS = []`) |
| Chữ trong instance không có trong `get_metadata` | Bỏ sót chữ của nút, ô nhập | Dùng `figma_extract.js` |
| Bounds mobile là khung phần tử, không phải khung chữ | Báo "khác số dòng" giả, Δx lệch | `dc.py` nhận diện khung chứa → so tâm; vẫn phải xem ảnh |
| WebView gộp chữ con không có khoảng trắng | Thiếu/không khớp giả | `dc.py` khớp kiểu "chứa"; xác nhận trên ảnh |
| Lấy status bar làm mốc dọc (thiết kế 36 · thật 53 dp, app lại vẽ header ở 40 dp) | Mọi Δy lệch giả cùng một lượng | Mốc = đỉnh header cả hai phía (`--actual-top`) |
| Menu/dialog mở → cây phần tử chỉ còn lớp phủ | Cả màn nền báo "thiếu" | `SCOPE` trong `figma_extract.js` — so riêng lớp phủ |
| Một khung Figma vẽ hai trạng thái không cùng lúc | Không bao giờ tái tạo được khung | Tái tạo từng trạng thái, DIFF `STATE` cho thiết kế |
| Toast biến khỏi cây phần tử sau ~2 giây | Không đo được bằng page source | Ảnh chụp ngay là bằng chứng, đo vị trí trên ảnh |
| Form giữ giá trị cũ khi quay lại màn | Chữ nhập mới bị nối vào sau, trạng thái sai | Xoá ô trước khi nhập (`appium_set_value` thay toàn bộ) |
| `get_screenshot` khung cao > 1024 | Ảnh Figma bị thu nhỏ, ảnh đặt cạnh nhau lệch tỉ lệ | `maxDimension` = chiều cao khung |
| So khung "có toast" lúc toast đã tắt | DIFF "thiếu" giả | Tái tạo hành động rồi chụp ngay; không kịp → ❔ |
| Phần trang dưới màn đầu không có trong khung Figma (khung cố định một màn) | Bỏ sót cả khối chức năng app có mà thiết kế không vẽ | Luôn **cuộn hết** màn thật một lượt dù khung Figma không ghi "full scroll" |
| Màn thật rộng hơn khung | Phần bên phải lệch toàn bộ trên ảnh chồng | Đọc ảnh đặt cạnh nhau, không đọc ảnh chồng; tin cột Δx (neo) |
| Ảnh chụp sai trạng thái (menu chưa mở, dữ liệu chưa tải) | Cả màn DIFF giả | Mở lại ảnh app trước khi đo |
| Hết hạn mức gọi Figma MCP giữa phiên | Mất ảnh các khung còn lại | Trích + lấy ảnh mọi khung ngay đầu phiên; hết rồi → `dc.py render` |
| `visual --match` cho đoạn **không** cuộn | Ảnh Figma bị cắt sai chỗ, đặt cạnh nhau lệch hẳn | Chỉ truyền `--match` cho đoạn đã cuộn |
| Thông báo lỗi của form trước còn ở form sau (Add → Update) | Khung "form sạch" chụp ra trạng thái lỗi — tưởng DIFF thiết kế | Vào mỗi khung form từ trạng thái sạch; thấy lỗi dính → tái hiện riêng — có thể là **lỗi app thật** |
| Dữ liệu người dùng khác trong danh sách / chi tiết | Lộ email, tên thật vào `docs/` qua ảnh **và** bảng đo | `mask` + `--redact` (Bước 6) |

---

## Tham chiếu

| File | Khi nào đọc |
|---|---|
| [`references/mobile.md`](references/mobile.md) | Bước 3 — mode MOBILE |
| [`references/web.md`](references/web.md) | Bước 3 — mode WEB |
| [`references/report_template.md`](references/report_template.md) | Bước 6 |
| [`.claude/rules/design_compare_rules.md`](../../rules/design_compare_rules.md) | Trước Bước 4 — dung sai, phân loại |
| [`scripts/design-compare/README.md`](../../../scripts/design-compare/README.md) | Tham số đầy đủ của `dc.py` |
