# Danh mục Requirements — MyLand Landing (Metfone)

> Điểm vào cấp hệ thống. Đọc file này **đầu tiên** trước mọi tác vụ đụng `docs/`.
> Bản đồ hệ thống: [`_discovery/system_map.md`](_discovery/system_map.md) · Bản đồ phủ tài liệu: [`_discovery/doc_inventory.md`](_discovery/doc_inventory.md)

## Thuộc tính dự án

| Thuộc tính | Giá trị |
|---|---|
| **Hệ thống** | MyLand Landing — landing đăng ký gói game MyLand cho thuê bao Metfone |
| **Mặt hệ thống** | Web (landing mở trên trình duyệt điện thoại). Không có spec API — chưa mở mặt API |
| **Tiền tố TC ID** | `MYLAND_` → `MYLAND_LANDING_TC_<3 số>` · user xác nhận 22-10-2026 |
| **Môi trường** | User xác nhận 22-10-2026: test **không ảnh hưởng hệ thống**, có **tài khoản test riêng**. 2 điểm vào dùng được: link chính và link `/?mps_test=1`. URL + tài khoản ở `.env` (`MYLAND_BASE_URL`, `MYLAND_TEST_URL`, `MYLAND_TEST_*`) |
| **Môi trường dùng chung** | Không — theo user. Vẫn chỉ đăng ký thật bằng số test được cấp, vì luồng `REGISTER` trừ tiền thật qua MPS |
| **Năng lực kiểm thử của QA** | Chốt 22-10-2026 — dùng cho nhánh Vòng 3 của **mọi** bộ TC:<br>• SIM 4G Metfone test: ✅ có — chạy được nhánh nhận diện số + đăng ký OTP<br>• Gọi API (`registerPackage`): ❌ không có quyền — đội Dev xác minh<br>• Truy vấn CSDL `game_farm` (`LANDING_REGISTER_LOG`, `VP_BILLING_ACTIVITY`): ❌ không có quyền — đội Dev xác minh (kịch bản nghiệm thu #10)<br>• Đọc log server (`landing-debug-*.log`): ❌ không có quyền — đội Dev xác minh<br>• DevTools trình duyệt: ✅ có |

## 1. Bảng danh mục module

| Module | Prefix | Nền tảng | Trạng thái recon | Mức phủ tài liệu | Tài liệu | REQ đã dùng | Mã kế tiếp | AMB treo | Story | Cập nhật |
|---|---|---|---|---|---|---|---|---|---|---|
| Landing đăng ký gói MyLand | `LANDING` | Web 🟨 | 🟨 Đang khảo sát — chờ ảnh nhánh đăng ký từ điện thoại 4G Metfone | 🟨 Một phần | [`landing/REQUIREMENTS_LANDING_SUMMARY.md`](landing/REQUIREMENTS_LANDING_SUMMARY.md) | 01 → 48 | `REQ-LANDING-49` | `AMB-LANDING-01` · `AMB-LANDING-05` · `AMB-LANDING-07` (🔴) + 9 mức thấp hơn | 4 (`STORY-LANDING-01` → 04) | 22-10-2026 |

**Bảng mã trạng thái recon:** ⬜ Chưa khảo sát · 🟨 Đang khảo sát · ✅ Đã có tài liệu · ⏸️ Hoãn · ⚪ Chưa implement

### Prefix đã chiếm

| Prefix | Module | Ghi chú |
|---|---|---|
| `LANDING` | Landing đăng ký gói MyLand | Gộp điều hướng + nhận diện số + đăng ký OTP + log đối soát (user chốt 22-10-2026) |
| `SYS` | — | **Dành riêng** cho AMB/RISK cấp hệ thống, không cấp cho module |

## 2. Trạng thái REQ toàn hệ thống


| Module | 🟢 Active | 🟡 Changed | 🔴 Deprecated | ⚪ Chưa implement |
|---|---|---|---|---|
| `LANDING` | 48 | 0 | 0 | 0 |

## 3. Ambiguity 🔴 High còn treo

| Mã | Nội dung | Chặn gì |
|---|---|---|
| `AMB-LANDING-01` | `success_after_timeout` nghĩa là gì (← `AMB-SYS-03`) | TC đối soát sau timeout, nguy cơ trừ/cộng hai lần |
| `AMB-LANDING-05` | Cấu hình ghi giới hạn OTP "/ phiên", PO chốt theo số thuê bao (← `AMB-SYS-07`) | TC lách giới hạn — nghi lỗi |
| `AMB-LANDING-07` | Text nguyên văn các thông báo + giao diện màn OTP chưa khảo sát | Expected text của S2, S3 — cần ảnh từ điện thoại 4G Metfone |

AMB cấp hệ thống `AMB-SYS-01`, `02`, `08` đã trả lời; `AMB-SYS-03 → 07` đã chuyển về module. Chi tiết: [`landing/REQUIREMENTS_LANDING_SUMMARY.md`](landing/REQUIREMENTS_LANDING_SUMMARY.md) mục 5.

## 4. Cấu trúc thư mục chuẩn

```
docs/requirements/
├── README.md                                   ← file này
├── _discovery/
│   ├── system_map.md                           ← INDEX bản đồ hệ thống — tên bất biến
│   ├── doc_inventory.md                        ← bản đồ phủ tài liệu
│   ├── sources/                                ← bản gốc / bản chép tài liệu QA cung cấp
│   └── evidence/                               ← 1 ảnh tổng quan mỗi module (chưa có — mode DOC)
└── landing/
    ├── REQUIREMENTS_LANDING_SUMMARY.md         ← INDEX module — tên bất biến
    └── web/
        ├── requirements_landing_web.md
        └── evidence/*.png
```

## 5. Quy trình sử dụng

| Tình huống | Workflow | Ghi vào đâu |
|---|---|---|
| Sinh REQ cho module từ UI thật | `/generate-requirements-from-website landing` | `landing/` |
| Phân tích thêm tài liệu / ticket | `/analyze-requirement-document` | `landing/analysis/` |
| Ticket đổi nghiệp vụ module đã có tài liệu | `/update-requirements-from-ticket` | `landing/` + `landing/impact/` |
| Phát hiện module bị sót / hệ thống có thêm mặt | `/discover-system` mode ADD | `_discovery/` + file này |

## 6. Nhật ký danh mục

| Ngày | Thay đổi | Nguồn |
|---|---|---|
| 22-10-2026 | `LANDING` sang 🟨 Đang khảo sát: 48 REQ, 12 AMB, 7 RISK, 4 Story. `AMB-SYS-03 → 07` chuyển thành `AMB-LANDING-01 → 05` | `/generate-requirements-from-website landing` |
| 22-10-2026 | Đóng `AMB-SYS-08` — xin lại OTP bằng nút "Gửi lại", mỗi lần bấm đều đếm vào giới hạn 3 lần | User |
| 22-10-2026 | Chốt cách đếm giới hạn OTP (10 phút từ lần xin đầu, xin lại sau sai/hết hạn có bị đếm). Mở `AMB-SYS-08` | User |
| 22-10-2026 | Chốt tiền tố TC `MYLAND_`, năng lực QA (chỉ có SIM 4G Metfone test). Đóng `AMB-SYS-01`, `AMB-SYS-02`; `AMB-SYS-03` đóng một phần; mở `AMB-SYS-07` | User trả lời checkpoint |
| 22-10-2026 | Khởi tạo danh mục. 1 module `LANDING` (user chốt gộp thay vì tách `ENTRY` + `REG`). Mode DOC | `/discover-system` · tài liệu "Nghiệm thu luồng đăng ký gói MyLand trên landing" (20-10-2026) |
