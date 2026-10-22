# Requirements — Landing đăng ký gói MyLand (`LANDING`)

> Index module — tên file bất biến. Danh mục hệ thống: [`../README.md`](../README.md) · Bản đồ hệ thống: [`../_discovery/system_map.md`](../_discovery/system_map.md)

## 1. Metadata

| Mục | Giá trị |
|---|---|
| **Module** | Landing đăng ký gói MyLand |
| **Prefix** | `LANDING` · TC ID `MYLAND_LANDING_TC_<3 số>` |
| **Nền tảng** | Web 🟨 — đã khảo sát nhánh máy tính + điện thoại ngoài mạng Metfone; nhánh đăng ký (4G Metfone) chưa khảo sát UI |
| **Nguồn** | Tài liệu nghiệm thu @Quangnh 20-10-2026 · PO chốt trong phiên 22-10-2026 · khảo sát UI 22-10-2026 |
| **Dải mã đã dùng** | `REQ-LANDING-01` → `REQ-LANDING-48` · `AMB-LANDING-01` → `AMB-LANDING-12` · `RISK-LANDING-01` → `RISK-LANDING-07` · `STORY-LANDING-01` → `STORY-LANDING-04` |
| **Mã kế tiếp** | `REQ-LANDING-49` · `AMB-LANDING-13` · `RISK-LANDING-08` · `STORY-LANDING-05` — **KHÔNG đánh lại từ 01** |
| **Ngày cập nhật** | 22-10-2026 |

## 2. Tổng quan

Landing cho thuê bao Metfone đăng ký gói game MyLand bằng OTP. Server và trình duyệt tự nhận diện số qua MPS Metfone; chỉ số **nhận diện được và chưa có gói** mới thấy form đăng ký, mọi trường hợp khác vào thẳng game.

- **Trong phạm vi:** điều hướng link chính (máy tính, điện thoại, https, CamID) · nhận diện số · form chọn gói · OTP (gửi, sai, hết hạn, gửi lại, giới hạn) · trừ tiền và cộng gold · vào game sau đăng ký · log đối soát `LANDING_REGISTER_LOG`.
- **Ngoài phạm vi:** mua vật phẩm trong game · gameplay · màn đăng nhập riêng của game (Phone / Get OTP / LOG IN) — chỉ dùng làm dấu hiệu "vào game chưa đăng nhập".

## Bản đồ tài liệu

| Nền tảng | File | Story | REQ bao phủ |
|---|---|---|---|
| Chung ≥ 2 nền tảng | — (module chỉ có Web) | — | — |
| Web | [web/requirements_landing_web.md](web/requirements_landing_web.md) | STORY-LANDING-01 → 04 | REQ-LANDING-01 → 48 |

## 3. Ma trận phân quyền

Module không có role đăng nhập. Rẽ nhánh theo **điều kiện truy cập**:

| Điều kiện truy cập | Thấy form đăng ký | Vào game | Đã đăng nhập khi vào game |
|---|---|---|---|
| Máy tính, `http` | ❌ | ✅ | ❌ |
| Máy tính, `https` | ❌ | ✅ | ❌ |
| Điện thoại ngoài mạng Metfone, `http` | ❌ | ✅ | ❌ |
| Điện thoại ngoài mạng Metfone, `https` | ❌ | ✅ | ❌ |
| App CamID, link có token | ⚠️❌ | ⚠️✅ | ⚠️✅ |
| Điện thoại 4G Metfone, số chưa có gói | ⚠️✅ | ⚠️❌ | — |
| Điện thoại 4G Metfone, số đã có gói | ⚠️❌ | ⚠️✅ | ⚠️✅ |

```
Tổng 21 ô = Đã kiểm chứng 12 · Suy diễn 8 · Chưa rõ 0 · Không áp dụng 1
Ô ⚠️ suy từ tài liệu nghiệm thu (không phải màn cấu hình) — chưa có SIM/link CamID để thử.
Ô "không áp dụng" là [4G Metfone chưa có gói × Đã đăng nhập] — người dùng ở lại landing, chưa vào game.
```

## 4. Ma trận trạng thái

Luồng đăng ký của một số thuê bao (theo tài liệu + PO; chưa khảo sát UI):

| Trạng thái hiện tại | Hành động | Trạng thái kế tiếp | `status` log | REQ |
|---|---|---|---|---|
| Landing (số điền sẵn) | Bấm đăng ký | Chờ nhập OTP | `otp_sent` | 22 |
| Landing | Bấm đăng ký, số khác số nhận diện | Bị từ chối | `blocked` | 20 |
| Chờ nhập OTP | Nhập sai OTP | Chờ nhập OTP | `wrong_otp` | 24, 25 |
| Chờ nhập OTP | Nhập OTP sau 60 giây | Chờ nhập OTP (phải gửi lại) | `otp_expired` | 27 |
| Chờ nhập OTP | Nhập đúng OTP, thiếu tiền | Chờ nhập OTP | `no_balance` | 28, 29 |
| Chờ nhập OTP | Bấm "Gửi lại" (lần ≤ 3 trong 10 phút) | Chờ nhập OTP (OTP mới) | `otp_sent` | 35, 38 |
| Chờ nhập OTP | Bấm "Gửi lại" lần 4 trong 10 phút | Bị chặn xin OTP | `limited` | 36 |
| Chờ nhập OTP | Nhập đúng OTP, đủ tiền | Đăng ký thành công → game đã đăng nhập | `success` | 31, 32 |

Trạng thái `success_after_timeout`, `already_subscribed`, `failed`, `timeout` chưa rõ phát sinh ở bước nào — AMB-LANDING-01, AMB-LANDING-10.

## 5. Điểm mơ hồ

| Mã | Câu hỏi | Nguy cơ | Mức độ | Assumption tạm | Trạng thái | Kết luận |
|---|---|---|---|---|---|---|
| AMB-LANDING-01 | `success_after_timeout` nghĩa là gì, xảy ra khi nào? | Không viết được TC đối soát cho trường hợp timeout; dễ cộng/trừ hai lần | 🔴 | Coi như thành công (đã trừ tiền), như câu SQL đối soát | ❓ Chờ trả lời | Chuyển từ AMB-SYS-03 |
| AMB-LANDING-02 | Mã "đã gửi OTP" của MPS là `0` hay `100`? | Log ghi sai trạng thái bước OTP | 🟡 | Cả hai là thành công | ❓ Chờ trả lời | Chuyển từ AMB-SYS-04 — xác nhận ở lần test thật đầu tiên |
| AMB-LANDING-03 | 2 câu thông báo (quá số lần xin OTP, hết phiên OTP) còn tiếng Anh — sửa trước nghiệm thu không? | TC kỳ vọng ngôn ngữ sai | 🟡 | Giới hạn đã biết, không chặn | ❓ Chờ trả lời | Chuyển từ AMB-SYS-05 |
| AMB-LANDING-04 | Phiên bản production mang hậu tố `-local` | Nhầm bản build | 🟢 | Chỉ là nhãn | ❓ Chờ trả lời | Chuyển từ AMB-SYS-06 |
| AMB-LANDING-05 | Cấu hình ghi `otp.max_send` "/ 10 phút / **phiên**", PO chốt **theo số thuê bao** — code đếm theo cách nào? | Lách giới hạn bằng phiên mới → spam SMS | 🔴 | Kỳ vọng theo PO; TC REQ-LANDING-37 kiểm lách | ❓ Chờ trả lời | Chuyển từ AMB-SYS-07 — nghi lỗi |
| AMB-LANDING-06 | `/mps-detect` trả khối `debug` (kết quả giải mã MPS, `RES`, `MOBILE`, lý do) về trình duyệt và trang in log `[MPS]` ra console trên production — cố ý giữ? | Lộ thông tin kỹ thuật/số thuê bao trên máy người dùng | 🟡 | Đang bật debug cho đợt nghiệm thu | ❓ Chờ trả lời | Phát hiện khảo sát 22-10-2026 |
| AMB-LANDING-07 | Text nguyên văn: sai OTP, hết hạn, không đủ tiền, thành công, quá số lần, số bị chặn; giao diện màn nhập OTP, nút Xác nhận, nút "Gửi lại", độ dài OTP | TC không có expected text | 🔴 | Kiểm theo nghĩa, chưa kiểm câu chữ | ❓ Chờ ảnh từ điện thoại 4G Metfone | — |
| AMB-LANDING-08 | URL game mang `cp=laoId1` — mã CP đúng cho thị trường Campuchia? | Sai đối tác/nguồn ghi nhận | 🟢 | Đúng | ❓ Chờ trả lời | Phát hiện khảo sát 22-10-2026 |
| AMB-LANDING-09 | Mã nguồn landing còn nhánh cho nhập số tay khi không nhận diện được, nhưng cấu hình hiện tại luôn vào game — nhánh này có còn dùng? | TC thừa/thiếu khi đổi `otp.detected_only` | 🟢 | Không dùng (`otp.detected_only = true`) | ❓ Chờ trả lời | — |
| AMB-LANDING-10 | Mỗi giá trị `status` thuộc bước `OTP` hay `REGISTER`? | Đối soát sai bước | 🟡 | Theo bảng mục 4 | ❓ Chờ trả lời | — |
| AMB-LANDING-11 | Hết 10 phút từ lần xin đầu thì được xin tiếp bao nhiêu lần (3 lần mới?) | Kỳ vọng REQ-LANDING-40 chưa đủ | 🟡 | 3 lần mới, mốc tính lại từ lần xin kế tiếp | ❓ Chờ trả lời | — |
| AMB-LANDING-12 | `price` lưu cho gói Tuần và Tháng là bao nhiêu? | TC đối soát giá sai | 🟢 | Cùng quy đổi như gói Ngày | ❓ Chờ trả lời | — |

## 6. Rủi ro

| Mã | Rủi ro | Mô tả | Mitigation |
|---|---|---|---|
| RISK-LANDING-01 | Trừ tiền thật | Môi trường là link chính thức; mỗi lần đăng ký thành công trừ tiền thuê bao | Chỉ đăng ký bằng SIM test; đối soát ngay sau mỗi lần |
| RISK-LANDING-02 | Nhánh đăng ký không tái hiện được trên máy tính | Cần điện thoại thật + 4G Metfone; automation desktop chỉ phủ S1 phần vào game | Chạy S2/S3 thủ công trên điện thoại hoặc Appium thiết bị thật |
| RISK-LANDING-03 | Lách giới hạn OTP | Nếu đếm theo phiên (AMB-LANDING-05) → gửi SMS không giới hạn | Ưu tiên TC REQ-LANDING-37 |
| RISK-LANDING-04 | Lộ thông tin debug | Khối `debug` + log console (AMB-LANDING-06) | Báo Dev tắt trước go-live |
| RISK-LANDING-05 | Chờ nhận diện quá lâu | MPS treo → spinner không chữ tới 120 giây | TC đo thời gian; đề xuất giảm timeout |
| RISK-LANDING-06 | Đối soát phụ thuộc Dev | QA không có quyền CSDL — S4 do Dev chạy SQL | Gửi Dev danh sách giao dịch (thời điểm, số, gói) sau mỗi đợt test |
| RISK-LANDING-07 | Trừ tiền / cộng gold hai lần | Timeout rồi thành công muộn (`success_after_timeout`) | TC kiểm REQ-LANDING-33, 34 sau timeout; chờ AMB-LANDING-01 |

## 7. Phân rã Epic / Story

| Story ID | Tên Story | REQ bao phủ | Số REQ | AMB / RISK liên quan | Ghi chú phạm vi |
|---|---|---|---|---|---|
| STORY-LANDING-01 | Điều hướng & nhận diện số | REQ-LANDING-01 → 12 | 12 | AMB-LANDING-06, 08, 09 · RISK-LANDING-04, 05 | Máy tính, https, CamID, MPS, link test, `/admin` |
| STORY-LANDING-02 | Form landing & giao diện | REQ-LANDING-13 → 21 | 9 | — | Gói, ô số, validate client, ngôn ngữ |
| STORY-LANDING-03 | OTP & trừ tiền | REQ-LANDING-22 → 40 | 19 | AMB-LANDING-01, 02, 03, 05, 11 · RISK-LANDING-03, 07 | Gửi, sai, hết hạn, thiếu tiền, thành công, giới hạn |
| STORY-LANDING-04 | Log đối soát | REQ-LANDING-41 → 48 | 8 | AMB-LANDING-10, 12 · RISK-LANDING-06 | Dev xác minh |

`Tổng: 4 Story / 48 REQ — 12 + 9 + 19 + 8 = 48 ✔ — mọi REQ thuộc đúng một Story`

| Nhóm | Mã | Nằm ở đâu |
|---|---|---|
| AMB thuộc Story | AMB-LANDING-01, 02, 03, 05, 06, 08, 09, 10, 11, 12 | Bảng Story |
| AMB cấp Epic | AMB-LANDING-04 (phiên bản) · AMB-LANDING-07 (text + màn OTP — cắt ngang S2, S3) | Hạng mục cấp Epic |
| RISK thuộc Story | RISK-LANDING-03, 04, 05, 06, 07 | Bảng Story |
| RISK cấp Epic | RISK-LANDING-01, 02 | Rủi ro mức module |

**Hạng mục cấp Epic:** ma trận phân quyền (mục 3) và ma trận trạng thái (mục 4) — cắt ngang S1–S3 · NFR (file web mục 8) · AMB-LANDING-04, 07 · RISK-LANDING-01, 02.

**Thứ tự triển khai đề xuất:**
1. STORY-LANDING-01 — làm được ngay, phần lớn đã kiểm chứng
2. STORY-LANDING-02 — cần một lần mở trên điện thoại 4G Metfone để chụp form
3. STORY-LANDING-03 — `BLOCKED` một phần bởi AMB-LANDING-07 (expected text) và AMB-LANDING-05; vẫn viết TC theo nghĩa
4. STORY-LANDING-04 — chạy cùng S3, Dev đối soát

## 8. Yêu cầu phi chức năng chung

Không có NFR áp nhiều nền tảng — xem [web/requirements_landing_web.md](web/requirements_landing_web.md) mục 8.

## 9. Nhật ký thay đổi

| Ngày | Nguồn | REQ ảnh hưởng | Loại | Tóm tắt thay đổi | TC cần xử lý |
|---|---|---|---|---|---|
| 22-10-2026 | UI recon + tài liệu nghiệm thu + PO | REQ-LANDING-01 → 48 | 🟢 Thêm | Khởi tạo tài liệu. 12 AMB (5 chuyển từ AMB-SYS-03 → 07), 7 RISK, 4 Story | — (viết TC mới) |
