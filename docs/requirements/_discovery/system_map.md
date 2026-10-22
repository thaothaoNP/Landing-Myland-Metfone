# Bản đồ hệ thống — MyLand Landing (Metfone)

> Tầng khám phá — **không chứa mã REQ**. Trạng thái recon chỉ ghi ở [`../README.md`](../README.md).
> Bản đồ 1 file (1 module) — không có thư mục `modules/`.

## 1. Bối cảnh khảo sát

| Mục | Giá trị |
|---|---|
| Ngày khảo sát | 22-10-2026 |
| Mode | **DOC** — chỉ đọc tài liệu, **chưa mở UI**. Mọi thông tin dưới đây là *dự kiến theo tài liệu*, chưa xác minh |
| Mặt | Web (landing trên trình duyệt điện thoại). Không có mặt mobile app, không có spec API |
| Nguồn | [`sources/nghiem_thu_luong_dang_ky_myland_landing.md`](sources/nghiem_thu_luong_dang_ky_myland_landing.md) — bản chép tài liệu nghiệm thu của @Quangnh, 20-10-2026 |
| URL | `.env` → `MYLAND_BASE_URL` (link chính) · `MYLAND_TEST_URL` (link `/?mps_test=1`) |
| Role | Người dùng cuối (khách vãng lai, không đăng nhập). Không có màn quản trị trong phạm vi |
| Môi trường dùng chung | Không — test không ảnh hưởng hệ thống, có tài khoản test riêng (user xác nhận 22-10-2026) |
| Phạm vi | Vào link chính · nhận diện số · đăng ký bằng OTP · vào game sau đăng ký · log trong DB |
| Ngoài phạm vi | Mua vật phẩm trong game (theo tài liệu) · gameplay |
| Tầng network | Chưa quan sát (mode DOC) |
| Điều kiện để thấy form đăng ký | ⚠️ **Điện thoại dùng 4G Metfone** + mở bằng `http://`. Máy tính, wifi, mạng khác, trang https → vào thẳng game. Playwright trên máy tính **không** tái hiện được luồng đăng ký |

## 2. Sơ đồ điều hướng

Không có menu — landing là một luồng quyết định một chiều (tài liệu mục "Luồng xử lý"):

```
/  (link chính, hoặc /?mps_test=1)
├─ Có token CamID ─────────────────────────────→ Game (tự đăng nhập bằng token)
├─ Không phải điện thoại ──────────────────────→ Game
└─ Điện thoại → gọi MPS nhận diện số (chờ ≤ 120 giây)
   ├─ Không nhận diện được ────────────────────→ Game
   ├─ Đã có gói ───────────────────────────────→ Game, đã đăng nhập
   └─ Chưa có gói → Landing (số điền sẵn, khoá)
      → Chọn gói → Đăng ký → SMS OTP → Nhập OTP → Xác nhận
         ├─ Sai OTP → nhập lại
         ├─ Thiếu tiền → báo lỗi, quay lại nhập OTP (PO chốt 22-10-2026)
         └─ Đúng → trừ tiền, ghi gói, cộng gold → Game, đã đăng nhập
```

| Route | Ghi chú | Trạng thái |
|---|---|---|
| `/` | Link chính | ❔ Chưa mở |
| `/?mps_test=1` | Bật nhận diện cho phiên khi `mps.detect_enabled = 'test'`. Hiện cấu hình là `true` nên cả 2 link đều nhận diện | ❔ Chưa mở |
| `/admin` | Tài liệu yêu cầu đã đóng (`404`) — điểm kiểm bảo mật, **không** phải module | ❔ Nghi có, chưa xác minh |
| Game | Đích của mọi nhánh — ngoài phạm vi khảo sát | — |

## 3. Bảng module

| Module | Bí danh | Prefix | Nền tảng | Loại màn hình | Story dự kiến | Risk | Ước REQ |
|---|---|---|---|---|---|---|---|
| Landing đăng ký gói MyLand | "luồng landing", "đăng ký gói MyLand" | `LANDING` | Web | Wizard 2 bước (chọn gói → nhập OTP) + màn chờ nhận diện | Điều hướng & nhận diện số · Đăng ký OTP & trừ tiền · Log đối soát | 🔴 Cao | 25–35 |

**Tổng: 1 module.**

### Chi tiết module `LANDING`

| Hạng mục | Theo tài liệu |
|---|---|
| Gói cước | `NGAY` 15 cents · `TUAN` 50 cents · `THANG` 1,5 USD |
| Field | Số thuê bao (điền sẵn, khoá) · chọn gói · OTP |
| CRUD | Không — chỉ tạo đăng ký |
| Status flow | Có — `LANDING_REGISTER_LOG.status`: `otp_sent` · `success` · `success_after_timeout` · `wrong_otp` · `otp_expired` · `no_balance` · `already_subscribed` · `failed` · `timeout` · `blocked` · `limited` |
| Business rule chính | Chỉ số MPS nhận diện được mới đăng ký · server chặn số khác (`blocked`) · tối đa 3 lần xin OTP / 10 phút **/ số thuê bao** (`limited`, PO chốt 22-10-2026) — 10 phút **tính từ lần xin đầu tiên**; lần xin lại sau khi sai / hết hạn OTP **vẫn bị đếm** · xin lại bằng nút **"Gửi lại"**, mỗi lần bấm đều đếm vào giới hạn (PO chốt 22-10-2026) · OTP hết hạn sau **60 giây** (`otp_expired`, PO chốt 22-10-2026) · thiếu tiền → báo lỗi, quay lại nhập OTP (`no_balance`) · sai OTP cho nhập lại, không trừ tiền · thành công → sau 3 giây vào game đã đăng nhập, gold/diamond cộng 1 lần |
| Message đã biết | 2 câu tiếng Anh chưa dịch Khmer: xin OTP quá nhiều lần · hết phiên OTP. Text nguyên văn **chưa có** |
| Risk 🔴 vì | Trừ tiền thật · nhận diện danh tính thuê bao · cộng tài sản game · cấu hình giới hạn OTP lệch với quyết định PO (`AMB-SYS-07`) |
| Evidence | Chưa có — mode DOC không mở UI |

## 4. Bản đồ entity & phụ thuộc

| Thành phần | Vai trò | Quan hệ |
|---|---|---|
| MPS Metfone `mobile.html` | Nhận diện số thuê bao | Gọi **từ trình duyệt** điện thoại, chỉ có `http` |
| API `registerPackage` (Java farm-business) | Đăng ký gói, gọi MPS `otp.html` để gửi OTP và trừ tiền | Landing (server) → Java → MPS |
| `LANDING_REGISTER_LOG` (DB `game_farm`) | 1 dòng mỗi lần bấm Đăng ký / Xác nhận OTP, phân biệt bằng `step` (`OTP` · `REGISTER`) | `req_id` = `cpRequestId` của `VP_BILLING_ACTIVITY` |
| `VP_BILLING_ACTIVITY` | Lịch sử trừ tiền phía Java | Đối soát với log landing |
| App CamID | Mở link kèm token | Bỏ qua landing, vào game |
| Game MyLand | Đích cuối, nhận `jwt` khi đăng ký thành công | Ngoài phạm vi |
| Đối tác truyền thông | Nhận báo đăng ký (`partner_notify`), nguồn `utm_source` / `click_id` | Ngoài hệ thống |

## 5. Ma trận phân quyền sơ bộ

Không có phân quyền theo role. Rẽ nhánh theo **điều kiện truy cập**, không theo tài khoản:

| Điều kiện | Thấy form đăng ký | Nguồn |
|---|---|---|
| Điện thoại · 4G Metfone · `http` · chưa có gói | ✅ | Tài liệu — ⚠️ chưa xác minh |
| Điện thoại · 4G Metfone · đã có gói | ❌ vào game | Tài liệu — ⚠️ chưa xác minh |
| Wifi / mạng khác / https / MPS lỗi | ❌ vào game | Tài liệu — ⚠️ chưa xác minh |
| Máy tính | ❌ vào game | Tài liệu — ⚠️ chưa xác minh |
| Có token CamID | ❌ vào game | Tài liệu — ⚠️ chưa xác minh |

## 6. Thứ tự khảo sát đã chốt

| # | Module | Ghi chú |
|---|---|---|
| 1 | `LANDING` | Nhánh "vào game" (máy tính, có token) khảo sát được bằng Playwright; nhánh đăng ký chạy trên **điện thoại thật có SIM 4G Metfone test** (QA đã có SIM — 22-10-2026). Kịch bản #10 (kiểm DB) do đội Dev xác minh — QA không có quyền truy vấn CSDL |

## 7. Vùng chưa xác minh

- Toàn bộ UI — mode DOC, chưa mở trang nào
- Text nguyên văn các message (sai OTP, thiếu tiền, quá số lần, hết phiên, đăng ký thành công)
- Độ dài OTP; nút "Gửi lại" (đã chốt có) — text nguyên văn, có đếm ngược / bị khoá trước khi OTP hết hạn không (thời hạn đã chốt 60 giây)
- Màn hình chờ nhận diện (tối đa 120 giây) trông thế nào, có thông báo gì
- `/admin` có thực sự trả `404`
- Ngôn ngữ giao diện (Khmer / tiếng Anh) và có chuyển ngôn ngữ không

## 8. Ambiguity cấp hệ thống

| Mã | Mức | Nội dung | Assumption tạm |
|---|---|---|---|
| `AMB-SYS-01` | ✅ Đã trả lời | Thiếu tiền: sơ đồ quay lại *Nhập OTP*; đoạn văn viết *"về landing để đăng ký lại sau khi nạp tiền"* | **PO chốt 22-10-2026: quay lại bước nhập OTP** (khớp sơ đồ). Đoạn văn trong tài liệu nguồn lỗi thời |
| `AMB-SYS-02` | ✅ Đã trả lời | `otp.max_send = 3` tính theo phiên hay theo số? | **PO chốt 22-10-2026: theo số thuê bao.** Cấu hình ghi "/ phiên" → mở `AMB-SYS-07` |
| `AMB-SYS-03` | 🔴 High — đóng một phần | Thời hạn OTP không nêu; `success_after_timeout` nghĩa là gì | **PO chốt 22-10-2026: OTP hết hạn sau 60 giây.** Còn mở: nghĩa của `success_after_timeout` → chuyển thành `AMB-LANDING-01` (22-10-2026) |
| `AMB-SYS-04` | 🟡 Medium | Mã "đã gửi OTP" của MPS nhận `0` hoặc `100` — tài liệu tự ghi cần xác nhận qua lần test thật đầu tiên | Cả hai đều là thành công → chuyển thành `AMB-LANDING-02` (22-10-2026) |
| `AMB-SYS-05` | 🟡 Medium | Hai câu thông báo đang tiếng Anh, chưa dịch Khmer — giới hạn đã biết hay sẽ sửa trước nghiệm thu? | Giới hạn đã biết, ghi nhận không chặn → chuyển thành `AMB-LANDING-03` (22-10-2026) |
| `AMB-SYS-07` | 🔴 High | Tài liệu cấu hình ghi `otp.max_send` = "Số lần xin OTP tối đa / 10 phút / **phiên**", PO chốt tính **theo số thuê bao**. Nếu code đếm theo phiên thì mở phiên mới (xoá cookie, trình duyệt khác) là lách được giới hạn | Nghi lỗi — kỳ vọng theo PO; TC phải kiểm cả lách bằng phiên mới → chuyển thành `AMB-LANDING-05` (22-10-2026) |
| `AMB-SYS-08` | ✅ Đã trả lời | Gửi lại OTP: nút riêng hay bấm Đăng ký lại? Có bị đếm vào giới hạn không? | **PO chốt 22-10-2026: bấm nút "Gửi lại".** **Lần bấm "Gửi lại" có đếm vào giới hạn 3 lần** (PO chốt 22-10-2026) |
| `AMB-SYS-06` | 🟢 Low | Phiên bản chạy trên link chính có hậu tố `-local` (`20261020-1026-f929127-local`) | Chỉ là nhãn build → chuyển thành `AMB-LANDING-04` (22-10-2026) |

Khi sinh tài liệu module → chuyển thành `AMB-LANDING-nn`, dòng ở đây ghi `→ chuyển thành AMB-LANDING-nn`.

## 9. Nhật ký khám phá

| Ngày | Mode | Mặt | Thay đổi | Nguồn |
|---|---|---|---|---|
| 22-10-2026 | UI recon | Web | `/generate-requirements-from-website landing`: 48 REQ. Bản đồ cập nhật: điện thoại https → `http://…/?mps_http=1`; nhận diện qua `POST /mps-detect`; máy tính vào game ở popup đăng nhập của game. `AMB-SYS-03 → 07` chuyển thành `AMB-LANDING-01 → 05` | UI thực tế |
| 22-10-2026 | DOC | Web | Đóng `AMB-SYS-08`: xin lại OTP bằng nút "Gửi lại", mỗi lần bấm đều đếm vào giới hạn 3 lần | User |
| 22-10-2026 | DOC | Web | PO chốt cách đếm giới hạn OTP: 10 phút tính từ lần xin đầu tiên, xin lại sau sai/hết hạn OTP có bị đếm. Mở `AMB-SYS-08` (gửi lại OTP) | User |
| 22-10-2026 | DOC | Web | User trả lời checkpoint: đóng `AMB-SYS-01`, `AMB-SYS-02`, đóng một phần `AMB-SYS-03`, mở `AMB-SYS-07`; QA có SIM 4G Metfone test | User |
| 22-10-2026 | DOC | Web | Khởi tạo bản đồ. 1 module `LANDING` (user chốt gộp). 6 AMB cấp hệ thống | Tài liệu nghiệm thu @Quangnh 20-10-2026 · user bổ sung 2 link test + môi trường không dùng chung |
