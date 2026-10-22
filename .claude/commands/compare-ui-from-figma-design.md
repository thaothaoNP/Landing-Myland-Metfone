---
description: So bản thiết kế Figma với giao diện đã xây dựng thật — 2 mode WEB (Playwright MCP) và MOBILE (Appium MCP — Android/iOS/Hybrid). Trích spec Figma chỉ-đọc, đo lệch chữ · vị trí · khoảng cách · màu · cỡ chữ theo dp/pt/px, người soát xác nhận trên ảnh đặt cạnh nhau rồi ghi DIFF có loại · mức độ · ai xử lý. Xuất báo cáo + evidence vào docs/design-reviews/.
skills:
  - skills-figma-design-comparator
  - skills-mobile-debug-agent
  - skills-ui-debug-agent
---

# Workflow: So Thiết Kế Figma Với UI Thật

> **BẮT BUỘC (MANDATORY SKILL):** Nạp và đọc kỹ **`skills-figma-design-comparator`** (`.claude/skills/skills-figma-design-comparator/SKILL.md`) — quy trình 6 bước, cách đọc bảng đo, viết DIFF. Mode WEB đọc thêm `references/web.md`; mode MOBILE đọc `references/mobile.md` — **chỉ một** trong hai.
>
> **Rule bắt buộc:** [`.claude/rules/design_compare_rules.md`](../rules/design_compare_rules.md) — độ trung thực, đơn vị, dung sai, phân loại DIFF, cấm.
>
> Thao tác thiết bị: `skills-mobile-debug-agent` (MOBILE) · thao tác trình duyệt: `skills-ui-debug-agent` (WEB).

---

## Cú pháp

```
/compare-ui-from-figma-design <MODE> <link Figma> [module] [khung] [độ trung thực] [kiểu chạy]
```

| Tham số | Bắt buộc | Ví dụ |
|---|---|---|
| `MODE` | ✅ | `WEB` · `MOBILE` |
| Link Figma | ✅ | `https://www.figma.com/design/<fileKey>/...` — có `node-id` thì giới hạn vào page/khung đó |
| Module | Nên có | `auth` — để ghi đúng `docs/design-reviews/<module>/` và nối REQ/TC |
| Khung | Không | `A-01,A-02` hoặc `tất cả` (mặc định: mọi khung màn hình trong page của `node-id`) |
| Độ trung thực | Không | `wireframe` · `mockup` — không ghi thì agent tự nhận biết, không chắc thì hỏi |
| Kiểu chạy | Không | *(trống)* = đầy đủ · `nhanh` = xem nhanh, trả lời trong chat, **không** ghi `docs/` · `bổ sung` = ghi thêm khung vào lượt chạy gần nhất (cùng ngày, cùng bản build) · `khung=còn-mở` = so lại các khung còn DIFF 🔴 — skill mục *Chọn cách chạy* |

Ví dụ:

```
/compare-ui-from-figma-design MOBILE https://www.figma.com/design/<fileKey>/Book?node-id=7-1 user
/compare-ui-from-figma-design MOBILE https://www.figma.com/design/<fileKey>/Book?node-id=6-607 auth A-07,A-08 bổ sung
/compare-ui-from-figma-design WEB https://www.figma.com/design/<fileKey>/CRM?node-id=12-40 customers nhanh
/compare-ui-from-figma-design MOBILE https://www.figma.com/design/<fileKey>/Book?node-id=9-1 book khung=còn-mở
```

Đích so sánh: MODE WEB lấy URL từ `.env` / tài liệu module, hoặc user đưa · MODE MOBILE dùng app đã khai trong `capabilities.json` (Android) hoặc user đưa bundle id (iOS).

---

## ⚠️ Ranh giới của workflow này

| Workflow này **CÓ** làm | Workflow này **KHÔNG** làm |
|---|---|
| Đọc Figma **chỉ đọc**, so với UI thật, ghi DIFF có số đo + ảnh | ❌ Sửa file Figma · ❌ sửa code app |
| Đưa app/web tới đúng trạng thái khung vẽ (đăng nhập, mở menu, gây lỗi validation) | ❌ Lưu/Xoá dữ liệu thật trên môi trường dùng chung để tạo trạng thái |
| Khung không tới được → ❔ kèm lý do | ❌ Rút requirements từ Figma — việc của `skills-requirements-analyzer` 3.3 |
| Gợi ý DIFF nào thành bug, DIFF nào cần PO | ❌ Tự tạo bug — user gọi `/create-bug-report` |

---

## Các bước thực hiện

### Bước 0: Tiếp nhận & đọc trạng thái repo

1. Tách `fileKey` và `node-id` từ link (`node-id=1-2` → `1:2`)
2. Đọc **danh mục** `docs/design-reviews/README.md` — hệ thống thứ hai trong namespace thì `docs/design-reviews/_<hệ-thống>/README.md` (chưa có → tạo theo `references/report_template.md`) → mã DIFF kế tiếp của module
3. **Đã từng so module × nền tảng này?** Mở báo cáo `run_*` gần nhất (danh mục có link) → lấy danh sách DIFF 🔴 Mở và ⚪ Chấp nhận — lượt này phải đối chiếu lại **từng** DIFF đó (rule mục 6 — vòng đời DIFF)
4. Đọc `docs/requirements/README.md` + `_discovery/system_map.md` (hoặc của namespace) → **đường điều hướng** tới từng màn hình, môi trường dùng chung hay không. Có tài liệu module thì mở index để biết REQ nào nói về màn hình sắp so
5. Đọc bảng **Thành phần dùng chung** trong danh mục — lệch ở header, bottom nav, ô nhập… đã có mã thì lượt này chỉ dẫn chiếu
6. Ước lượng lượt gọi Figma MCP (skill Bước 1 mục 6) — gói Starter có hạn mức; page nhiều khung thì lấy spec + ảnh **mọi** khung ngay đầu phiên
7. Công bố một câu: *"So `<n>` khung page `<tên>` với **Android** `emulator-5554` (448 dp, density 480) — thiết kế mức **wireframe**, kiểu chạy **đầy đủ**, DIFF bắt đầu từ `DIFF-<MODULE>-<nn>`."*

### Bước 1: Bản đồ màn hình — skill Bước 1

`figma_extract.js` (`FRAME_IDS = []`) → danh sách khung → bảng Screen Map (mã khung · node-id · trạng thái vẽ · cách tới · đạt được?). Khai báo độ trung thực.

### Bước 2: Trích spec Figma — skill Bước 2

Mỗi khung: `figma_extract.js` (3–4 khung một lần) → `reports/design-compare/<run>/figma_<id>.json` · `get_screenshot` → `curl` **ngay** → `figma_<id>.png`. Hết hạn mức ảnh → `dc.py render figma_<id>.json -o figma_<id>.png`, evidence đặt tên `_figma_render.png`.

`<run>` = `<module>_<nền-tảng>_<YYYYMMDD_HHMMSS>` — trùng với thư mục `run_*` sẽ ghi ở `docs/`.

### Bước 3: Thu dữ liệu UI thật — theo MODE

| | MODE **MOBILE** (`references/mobile.md`) | MODE **WEB** (`references/web.md`) |
|---|---|---|
| Mở | `appium_session_management create` → nhận diện loại app → `appium_mobile_device_info` | `browser_navigate` → `browser_resize` về bề ngang khung (≤ cửa sổ) → chờ `document.fonts.ready` |
| Cấu hình chuẩn | density · status bar · nav bar · **đỉnh header** (mốc dọc) · `font_scale = 1.0` · dark mode theo khung | viewport = bề ngang khung · font đã tải |
| Tới trạng thái | Locator + `appium_gesture tap` · ẩn bàn phím | Locator từ `browser_snapshot` |
| Ảnh | `adb exec-out screencap -p` (Android) | `browser_take_screenshot fullPage scale=css filename=…` |
| Cây / spec | `appium_get_page_source saveToFile` → `dc.py android-tree` / `ios-tree --png` | `browser_evaluate` + `collect_dom.js` + `filename=…` |
| Màn dài | Cuộn từng đoạn, chồng lấn, `--auto-offset` — **luôn cuộn hết màn thật** dù khung Figma chỉ vẽ một màn | Full page một lần |
| Lớp phủ (menu, dialog) | `SCOPE` khi trích Figma — cây chỉ còn lớp phủ | `ROOT_SELECTOR` trong `collect_dom.js` |

**Mở lại ảnh app** trước khi đo — sai trạng thái thì chụp lại.

### Bước 4: Đo — skill Bước 4

```bash
python scripts/design-compare/dc.py match  figma_<id>.json <mã>_actual.json --actual-top <đỉnh header> -o <run>/<mã>_match   # WEB: --tol 2 --de-text 3
python scripts/design-compare/dc.py visual figma_<id>.png  <mã>_app.png --design figma_<id>.json --actual <mã>_actual.json --actual-top <đỉnh header> -o <run>/<mã>
```

### Bước 5: Soát trên ảnh → DIFF — skill Bước 5

Mở `<mã>_side.png`, đi từng dòng ❌ ⚠️ 🔍 ➕ ❔ của bảng đo + checklist soát tay. Mỗi lệch thật = 1 DIFF (cùng nguyên nhân gộp một; đã có mã ở module khác → dẫn chiếu). Gán **loại · mức độ · ai xử lý** theo rule mục 6 — lỗi hiển nhiên (chữ sai nghĩa, thiếu dữ liệu trong câu, lỗi dính từ form khác, thông tin khuất) là `Dev` dù thiết kế vẽ theo app. DIFF hành vi giao Dev → **tái hiện lại** một lần từ trạng thái sạch.

Khoanh ảnh (chỉ DIFF đã xác nhận): `dc.py annotate --actual <mã>_actual.json --text "<regex>=<mã DIFF>"` hoặc `--rect "x,y,w,h=<mã DIFF>"` — hoặc `--map` theo dòng bảng đo. Mở lại ảnh.

Kiểu `nhanh`: dừng ở đây — trả lời trong chat bằng ảnh đặt cạnh nhau + danh sách lệch (chưa cấp mã), hỏi user có muốn lưu thành lượt chạy đầy đủ không.

Có lần chạy trước → **trước khi cấp mã mới**, đối chiếu từng lệch với DIFF cũ: còn lệch → giữ mã cũ · hết lệch → `✅ Đã khắc phục` · lệch đã `⚪ Chấp nhận` → không báo lại. Chỉ lệch chưa có DIFF mới được cấp mã nối tiếp.

### Bước 6: Ghi báo cáo & danh mục

1. **Che dữ liệu** người khác trước khi copy: ảnh `dc.py mask` (rồi dựng lại `_side` từ ảnh đã che) · bảng đo `match --redact`
2. Copy evidence vào `docs/design-reviews/<module>/<nền-tảng>/run_<timestamp>/evidence/` — mỗi khung: `<mã>_<mô_tả>_figma.png` (hoặc `_figma_render.png`) · `_app.png` · `_side.png` (+ `_marked.png` nếu có DIFF; nhiều đoạn cuộn thêm `_part<n>`). **Không** copy page source, spec JSON, ảnh chồng, bản đồ khác biệt
3. Viết `design_compare_report.md` theo `references/report_template.md` — mục 4 sinh bằng `dc.py sections` từ các `<mã>_match.md`. Kiểu `bổ sung`: sửa báo cáo của `run_*` gần nhất thay vì tạo thư mục mới
4. Kiểm mọi link `evidence/…` trỏ tới file có thật
5. Cập nhật danh mục (`docs/design-reviews/README.md` hoặc `_<hệ-thống>/README.md`): dòng module × nền tảng · Nhật ký · bảng *Thành phần dùng chung*
6. Đóng phiên: `appium_session_management delete` (MOBILE) · `browser_resize 1600×750` (WEB)

### Checklist bàn giao

- [ ] Đã khai báo độ trung thực + dung sai ở đầu báo cáo; DIFF không vượt phạm vi của độ trung thực
- [ ] Mọi khung trong phạm vi có kết quả: ✅ / DIFF / ❔ kèm lý do — không khung nào biến mất im lặng
- [ ] Mỗi DIFF có số đo ở cả **Thực tế** và **Thiết kế**, có loại · mức độ · ai xử lý, có link ảnh
- [ ] Không DIFF nào chỉ dựa trên bảng đo tự động mà chưa xem ảnh đặt cạnh nhau
- [ ] Lệch dây chuyền đã gộp về chỗ khởi phát — không 5 DIFF cho cùng một nguyên nhân
- [ ] Đã mở lại mọi ảnh trong `evidence/`; ảnh khoanh đúng chỗ
- [ ] File Figma không bị sửa; `docs/` không có page source, credentials, dữ liệu khách hàng thật — kiểm cả **ảnh** lẫn **bảng đo** trong báo cáo
- [ ] Không tạo / sửa / xoá bản ghi thật nào để có trạng thái (form chỉ submit khi validation chặn, hộp xoá chỉ *Cancel*)
- [ ] Lệch ở thành phần dùng chung đã dẫn chiếu mã cũ, không cấp mã trùng nghĩa ở module khác
- [ ] Khung dùng ảnh Figma dựng lại (`render`) được ghi rõ ở đầu báo cáo và ở mục 5
- [ ] Danh mục `docs/design-reviews/README.md` đã cập nhật mã kế tiếp
- [ ] Chạy lại: mọi DIFF 🔴 Mở / ⚪ Chấp nhận của lần trước đều có trạng thái mới trong báo cáo này — không DIFF cũ nào biến mất, không cấp mã mới cho lệch cũ

**Báo cáo cho user:** số khung đã so / ❔ · số DIFF theo mức độ và người xử lý · 3 DIFF quan trọng nhất · link báo cáo · lệnh kế tiếp.

---

## Mối quan hệ với workflows khác

```
Figma ──→ /compare-ui-from-figma-design ──→ DIFF (Dev, High/Medium) ──→ /create-bug-report ──→ /retest-fixed-bugs
                       │                         DIFF (Cần PO quyết) ──→ AMB trong requirements (/update-requirements-from-ticket)
                       └── dùng system_map.md (đường điều hướng) · REQUIREMENTS_<MODULE>_SUMMARY.md (đối chiếu REQ)
```

| Tình huống | Workflow |
|---|---|
| Chưa biết app có những màn hình nào | `/discover-system` |
| Figma là tài liệu nghiệp vụ duy nhất, cần REQ | `/analyze-requirement-document` hoặc nhánh tài liệu của `/generate-requirements-from-website` / `-mobile` |
| Ghi bug cho DIFF | `/create-bug-report` — bug trỏ mã DIFF + link evidence trong `docs/design-reviews/` |
| Dev/designer đã sửa, so lại | Chạy lại workflow này cho đúng khung — lần chạy mới **giữ mã** DIFF cũ, đổi trạng thái (rule mục 6 — vòng đời DIFF) |
