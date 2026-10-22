# Bản đồ phủ tài liệu — MyLand Landing

> Tầng khám phá · mode DOC · 22-10-2026. Index hệ thống: [`system_map.md`](system_map.md)

## 1. Danh mục tài liệu nguồn

| File | Loại | Tác giả · ngày | Ghi chú |
|---|---|---|---|
| [`sources/nghiem_thu_luong_dang_ky_myland_landing.md`](sources/nghiem_thu_luong_dang_ky_myland_landing.md) | Tài liệu nghiệm thu (UAT) | @Quangnh · 20-10-2026 | Bản **chép tay** từ Claude Docs (artifact không cho tải). Sơ đồ chuyển sang Mermaid. Đây là tài liệu nghiệm thu, **không** phải spec — có luồng và kỳ vọng, thiếu field spec và message |

## 2. Bản đồ phủ theo vùng của module `LANDING`

| Vùng | Phần tài liệu phủ | Mức phủ | Thiếu gì |
|---|---|---|---|
| Điều hướng vào link chính (CamID, máy tính, mạng khác) | "Luồng xử lý" + kịch bản #5, #7, #8 | 🟩 Đầy đủ | Không có giao diện để kiểm, chỉ kiểm điểm đến |
| Nhận diện số qua MPS | "Thông tin chung", "Giới hạn đã biết", cấu hình `mps.*` | 🟨 Một phần | Màn chờ, thông báo khi timeout |
| Form landing (chọn gói, số khoá) | Kịch bản #1, #2, bảng gói cước | 🟨 Một phần | Bố cục, text nút, gói mặc định, mô tả gói |
| OTP (gửi, nhập, sai, hết hạn, giới hạn) | Kịch bản #2, #3, #9, `otp.*`, enum status | 🟨 Một phần | Độ dài OTP, gửi lại, text message. Thời hạn 60 giây + giới hạn theo số do PO chốt 22-10-2026 (`AMB-SYS-07` lệch cấu hình) |
| Trừ tiền & kết quả đăng ký | Kịch bản #4, #6, sơ đồ | 🟨 Một phần | Nhánh thiếu tiền: PO chốt quay lại nhập OTP (`AMB-SYS-01` đã đóng) |
| Log đối soát `LANDING_REGISTER_LOG` | Bảng cột + 3 câu SQL + kịch bản #10 | 🟩 Đầy đủ | Danh sách đủ 30 cột (tài liệu chỉ nêu nhóm cột) |
| Bảo mật (chặn số khác, `/admin`) | "Giới hạn đã biết", phụ lục bước 3 | 🟨 Một phần | Cách server chặn, thông báo khi bị chặn |
| Đa ngôn ngữ | "Giới hạn đã biết" (2 câu tiếng Anh) | ⬜ Trắng | Ngôn ngữ mặc định, có chuyển ngôn ngữ không |

## 3. Lệch pha tài liệu ↔ UI

Chưa đối chiếu — mode DOC chưa mở UI. Lệch pha **bên trong** tài liệu: `AMB-SYS-01` (sơ đồ ↔ đoạn văn — đã chốt theo sơ đồ), `AMB-SYS-07` (cấu hình ↔ quyết định PO) ở [`system_map.md`](system_map.md) mục 8.
