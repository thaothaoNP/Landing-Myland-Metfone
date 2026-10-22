# Mẫu báo cáo — `design_compare_report.md`

> Bước 6 của skill. Ghi tại `docs/design-reviews/<module>/<nền-tảng>/run_<YYYYMMDD_HHMMSS>/design_compare_report.md` (namespace hệ thống thứ hai: `docs/design-reviews/_<hệ-thống>/<module>/…`). Ngày trong nội dung viết `DD-MM-YYYY`.

````markdown
# So thiết kế Figma ↔ <Web | Android | iOS> — <Tên module> (`<PREFIX>`)

| Mục | Giá trị |
|---|---|
| Mode | WEB / MOBILE |
| Ngày chạy | DD-MM-YYYY HH:MM – HH:MM (kiểu **Bổ sung**: thêm `· bổ sung <khung>: DD-MM-YYYY HH:MM – HH:MM (cùng bản build)`) |
| Figma | `<tên file>` · page `<tên page>` · <link figma.com/design/<fileKey>> |
| Độ trung thực thiết kế | Wireframe / Mockup / Prototype — <căn cứ nhận biết> |
| Bản build | <URL môi trường web · hoặc app id + version (build)> |
| Môi trường | <Trình duyệt + viewport · hoặc thiết bị, OS, density, status bar, cỡ chữ hệ thống, dark mode, ngôn ngữ> |
| Mốc dọc | Đỉnh header: thiết kế <n> ↔ app <n> (`--actual-top`) — web: không có |
| Dung sai | Vị trí ±<n> · cỡ chữ ±<n> · ΔE chữ ≤ <n> · ΔE nền ≤ <n> (rule `design_compare_rules.md` mục 4 / quy định dự án) |
| Phạm vi khung | <n>/<m> khung (<mã đầu> → <mã cuối>) · <k> ❔ không đưa app tới được |
| Ảnh Figma | `get_screenshot` · hoặc ghi rõ khung nào **dựng lại từ JSON** (`dc.py render`) và vì sao |
| Dữ liệu | Môi trường dùng chung? Đã tạo/sửa/xoá gì (mặc định: không) · đã che dữ liệu gì trên ảnh / bảng đo |
| Tài liệu liên quan | REQ: `docs/requirements/<module>/…` · TC: `docs/testcases/<module>/…` |

## 1. Tóm tắt

| Mức độ | DIFF 🔴 Mở | Dev | Design | Cần PO quyết | ✅ Khắc phục lượt này | ⚪ Chấp nhận |
|---|---|---|---|---|---|---|
| High | | | | | | |
| Medium | | | | | | |
| Low | | | | | | |
| **Tổng** | | | | | | |

**Nhận xét chung:** 2–4 câu — app bám thiết kế tới đâu, nhóm lệch lớn nhất là gì, có khung nào không so được.

**Dùng chung với module khác (không cấp mã mới):** <thành phần> → `DIFF-<…>` · … — bỏ dòng này nếu không có.

## 2. Bản đồ màn hình

| Mã khung | Khung Figma (node-id) | Trạng thái vẽ | Cách tới trên app | Kết quả | DIFF |
|---|---|---|---|---|---|
| A-01 | Sign in (`6:123`) | Mặc định | Avatar › Sign in | ✅ Khớp / ⚠️ n DIFF / ❔ không tới được — <lý do> | DIFF-…-01, 02 |

## 3. Danh sách DIFF

| Mã | Trạng thái | Khung | Loại | Mức độ | Ai xử lý | Mô tả | Thực tế (số đo) | Thiết kế (số đo) | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| DIFF-<MODULE>-01 | 🔴 Mở | A-01 | CONTENT | Low | Dev | | | | [side](evidence/…_side.png) · [marked](evidence/…_marked.png) |

> Loại: `CONTENT` · `MISSING` · `EXTRA` · `LAYOUT` · `STYLE` · `ASSET` · `STATE` — rule mục 6.
> Cột *Khung*: `A-01 · A-03` · dải `B-01 → B-04` · khung module khác `(+ B-09)` (thành phần dùng chung).
> Trạng thái: `🔴 Mở` · `✅ Đã khắc phục (run_<timestamp>)` · `⚪ Chấp nhận — <ai>, <ngày>, <lý do>` · `🗑️ Không còn áp dụng (Figma đổi <ngày>)`. Chạy lại: DIFF cũ **giữ mã và giữ dòng**, chỉ đổi trạng thái + số đo; cột *Mô tả* ghi thêm `(phát hiện lần đầu: run_<timestamp>)` với DIFF không mới.

## 4. Chi tiết từng khung

### A-01 · Sign in

![Figma | App](evidence/A-01_sign_in_side.png)

**Kết luận khung:** <khớp / n DIFF>. **Đã soát tay:** icon · ảnh · bo góc · chữ bị cắt · phần tử bị che · trạng thái — <ghi điểm nào không áp dụng>.

> Ghi chú khung khi có: thiết kế **lược bớt** (chỉ so chữ + trạng thái) · **dữ liệu mẫu** đã khai `--sample` · ảnh Figma **dựng lại** · dữ liệu đã **che** · thao tác chỉ mở rồi *Cancel*.

Màn nhiều đoạn cuộn: mỗi đoạn một ảnh đặt cạnh nhau + một khối `<details>` bảng đo (ghi `đoạn n` / `--auto-offset`).

<details><summary>Bảng đo tự động (dc.py match)</summary>

<dán nội dung <mã>_match.md — đây là số liệu thô, kết luận nằm ở mục 3>

</details>

## 5. Khung không so được

| Khung | Lý do | Cần gì để so |
|---|---|---|

## 6. Ghi chú tham khảo (không tính DIFF)

Khác biệt nằm ngoài phạm vi theo độ trung thực (VD wireframe: màu nền gradient, ảnh thật thay khung giữ chỗ) — ghi để designer biết, không giao việc.

## 7. Việc tiếp theo

- DIFF `Dev` mức High/Medium → `/create-bug-report` (bug trỏ `DIFF-…` + link evidence ở đây, không nhân bản ảnh)
- DIFF `Design` → gửi designer cập nhật Figma
- DIFF `Cần PO quyết` → mở `AMB-<MODULE>-<nn>` trong tài liệu requirements của module
````

**Danh mục** `docs/design-reviews/README.md` — tạo ở lần chạy đầu, mỗi lần chạy cập nhật đúng dòng của module × nền tảng:

```markdown
# Danh mục So thiết kế Figma

| Module | Nền tảng | Figma (page) | Lần chạy gần nhất | Khung đã so | DIFF đã dùng | Mã kế tiếp | DIFF mở (H/M/L) | Báo cáo |
|---|---|---|---|---|---|---|---|---|

## Nhật ký

| Ngày | Lần chạy | Ghi chú |
|---|---|---|

## Thành phần dùng chung — DIFF ghi một lần

| Thành phần | Mã DIFF | Gặp ở |
|---|---|---|
```

`DIFF đã dùng` / `Mã kế tiếp` đếm **theo module**, dùng chung mọi nền tảng (giống dải REQ) — DIFF web và DIFF Android của cùng module không trùng số.
