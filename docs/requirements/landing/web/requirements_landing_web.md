# Requirements — Landing đăng ký gói MyLand · Web

> Index module: [`../REQUIREMENTS_LANDING_SUMMARY.md`](../REQUIREMENTS_LANDING_SUMMARY.md) — Story, phân quyền, trạng thái, AMB/RISK, Nhật ký nằm ở đó.

## 1. Metadata khảo sát

| Mục | Giá trị |
|---|---|
| **Nền tảng** | Web — landing mở trên trình duyệt điện thoại; máy tính chỉ đi nhánh vào game |
| **Ngày khảo sát** | 22-10-2026 |
| **Trình duyệt khảo sát** | (1) Playwright MCP — Chromium **headless**, viewport `800×513`, UA desktop `HeadlessChrome/154`. ⚠️ Lệch chuẩn headed `1600×750` của dự án: server Playwright đang kết nối chạy từ project khác, không phải `.mcp.json` của project này<br>(2) Trình duyệt tích hợp Claude — Chrome 152 desktop, viewport `757×878`<br>(3) Trình duyệt tích hợp Claude — giả lập điện thoại, viewport `375×812`, UA `Android 14; Pixel 8 … Chrome/152 Mobile` |
| **Mạng khảo sát** | Mạng văn phòng — **không phải 4G Metfone**. MPS trả `RES=406` (không nhận diện được). Nhánh có số nhận diện được (form đăng ký, OTP, trừ tiền) **chưa khảo sát trên UI** |
| **Tầng network** | Quan sát thụ động request do trang phát sinh. Không gọi API trực tiếp. Mã nguồn landing đọc bằng `GET /` với UA điện thoại (tương đương view-source) |
| **Phạm vi chụp evidence** | Viewport — trang game không có dữ liệu cá nhân |

## 2. Bản đồ phủ tài liệu

Nguồn tài liệu: [`../../_discovery/sources/nghiem_thu_luong_dang_ky_myland_landing.md`](../../_discovery/sources/nghiem_thu_luong_dang_ky_myland_landing.md) (@Quangnh, 20-10-2026) + câu trả lời PO trong phiên 22-10-2026.

| Vùng chức năng | Tài liệu phủ | Mức phủ | Đã khảo sát UI | REQ liên quan |
|---|---|---|---|---|
| Điều hướng máy tính / https / mạng ngoài Metfone | "Luồng xử lý", kịch bản #7, #8 | 🟩 Đầy đủ | ✅ Đối chiếu khớp | REQ-LANDING-01, 02, 04, 05, 07 |
| Nhận diện số qua MPS (chờ, timeout) | "Giới hạn đã biết", cấu hình `mps.*` | 🟨 Một phần | 🟨 Thấy luồng gọi + mã nguồn; chưa có số nhận diện được | REQ-LANDING-04 → 10 |
| Link test `/?mps_test=1`, `/admin` | Phụ lục cấu hình, bước 3 | 🟩 Đầy đủ | ✅ (mps_test chỉ trên desktop) | REQ-LANDING-11, 12 |
| Form landing (gói, ô số) | Kịch bản #1, bảng gói cước | 🟨 Một phần | 🟨 Đọc mã nguồn HTML; chưa thấy form hiển thị | REQ-LANDING-13 → 21 |
| OTP & trừ tiền | Kịch bản #2 → #6, #9 + PO chốt | 🟨 Một phần | ⬜ Chưa — cần điện thoại 4G Metfone | REQ-LANDING-22 → 40 |
| Log đối soát DB | Mục "Log tra soát" | 🟩 Đầy đủ | ⬜ QA không có quyền DB — Dev xác minh | REQ-LANDING-41 → 48 |

**Thang `Nguồn`:** `Kiểm chứng thực tế` = đã thao tác và quan sát · `Tài liệu + kiểm chứng thực tế` = tài liệu nêu, đã xác nhận khớp · `UI thực tế · mã nguồn HTML` = đọc từ HTML trang trả về, chưa thấy hiển thị · `Tài liệu · <mục>` = chỉ có trong tài liệu · `PO chốt 22-10-2026` = câu trả lời của PO trong phiên.

## 3. Yêu cầu chức năng

> REQ không ghi trạng thái khác = 🟢 Active. Story: S1 = `STORY-LANDING-01` … S4 = `STORY-LANDING-04` (xem index).

### S1 — Điều hướng & nhận diện số

| REQ ID | Tên yêu cầu | Mô tả | Acceptance Criteria | Trạng thái | Cập nhật lần cuối | Nguồn |
|---|---|---|---|---|---|---|
| REQ-LANDING-01 | Máy tính mở link chính được chuyển vào game | Người dùng máy tính không thấy landing | Trình duyệt UA desktop mở `http://<MYLAND_BASE_URL>/` → `GET /` trả `302`, `Location` = `/assets/` → trang game `/assets/index.html?cp=…&data=&token=&t=<timestamp>`; tiêu đề trang `MY LAND`; **không** có request `POST /mps-detect`. Game hiện popup "WELCOME TO MYLAND" có ô `Phone`, `OTP`, nút `Get OTP`, `LOG IN` | 🟢 | — | Tài liệu + kiểm chứng thực tế (kịch bản #8) |
| REQ-LANDING-02 | Máy tính mở link https được chuyển vào game http | Trang https không ở lại landing | UA desktop mở `https://…/` → `302` với `Location: http://…/assets/` → trang game (http) | 🟢 | — | Kiểm chứng thực tế |
| REQ-LANDING-03 | Mở từ app CamID có token thì vào game đã đăng nhập | Bỏ qua landing | Mở link từ app CamID (link có token) → vào game ngay, game tự đăng nhập bằng token CamID, không hiện landing | 🟢 | — | Tài liệu · "Luồng xử lý" |
| REQ-LANDING-04 | Điện thoại mở link chính thì tải landing để nhận diện số | Chỉ điện thoại vào luồng landing | UA điện thoại mở `http://…/` → `GET /` trả `200` (trang `MYLANDKH`, `html lang="km"`); lớp chờ `#loading` hiện ngay (`wait = 0`); trang gọi MPS `…/MPS/mobile.html?…CMD=MSISDN&SER=Vtech_MyLand…` rồi `POST /mps-detect` | 🟢 | — | Kiểm chứng thực tế + mã nguồn HTML |
| REQ-LANDING-05 | Không nhận diện được số thì vào game chưa đăng nhập | Wifi, mạng khác, MPS lỗi | Điện thoại ngoài mạng 4G Metfone mở link chính → MPS trả nội dung có `DATA`, `/mps-detect` trả `action = game` (giải mã `RES=406`, không có số) → chuyển `location.replace` sang `/assets/` → URL game có `token=` **rỗng**. Không hiện form đăng ký. Đo được ≈ 0,7 giây trên mạng văn phòng | 🟢 | — | Tài liệu + kiểm chứng thực tế (kịch bản #7) |
| REQ-LANDING-06 | Chờ MPS tối đa 120 giây rồi vào game | Giới hạn thời gian nhận diện | MPS không trả lời → lớp chờ hiển thị tới hết **120 giây** (`timeout = 120000` ms) → trang gửi `/mps-detect` không có `DATA` → vào game. Trong lúc chờ không có ô nhập số tay (`wait = 0`) | 🟢 | — | Tài liệu · "Giới hạn đã biết" + mã nguồn HTML (chưa tái hiện MPS treo) |
| REQ-LANDING-07 | Điện thoại mở link https được chuyển về http để nhận diện | MPS chỉ có http | UA điện thoại mở `https://…/` → trang cuối là `http://…/?mps_http=1`, tải landing và gọi `/mps-detect` như REQ-LANDING-04 | 🟢 | — | Tài liệu + kiểm chứng thực tế |
| REQ-LANDING-08 | Trang vẫn ở https thì không gọi MPS và vào game | Ví dụ Chrome ẩn danh giữ https | Landing chạy trên `https:` → bỏ qua gọi MPS, gửi `/mps-detect` với lỗi "trang mở bằng https" → vào game | 🟢 | — | Tài liệu · "Giới hạn đã biết" + mã nguồn HTML (chưa tái hiện được — server luôn chuyển https về http) |
| REQ-LANDING-09 | Số nhận diện được, đã có gói thì vào game đã đăng nhập | Không cho đăng ký lại | Điện thoại 4G Metfone, số đã đăng ký → `/mps-detect` trả `url` game → vào game, đã đăng nhập (không hiện popup đăng nhập của game) | 🟢 | — | Tài liệu · kịch bản #5 |
| REQ-LANDING-10 | Số nhận diện được, chưa có gói thì được điền sẵn trên landing | Điều kiện duy nhất thấy form | Điện thoại 4G Metfone, số chưa đăng ký → `/mps-detect` trả `action = fill` → ô `#msisdn` được điền số, lớp chờ ẩn | 🟢 | — | Tài liệu · kịch bản #1 + mã nguồn HTML |
| REQ-LANDING-11 | Link test `/?mps_test=1` có cùng điều hướng như link chính | Cấu hình `mps.detect_enabled = true` | UA desktop mở `/?mps_test=1` → vào game giống REQ-LANDING-01. Nhánh điện thoại: ❔ chưa khảo sát | 🟢 | — | Kiểm chứng thực tế (desktop) · Tài liệu · phụ lục cấu hình |
| REQ-LANDING-12 | Trang quản trị đã đóng | Bảo mật | `GET /admin` trả `404 Not Found` | 🟢 | — | Tài liệu + kiểm chứng thực tế (phụ lục bước 3) |

### S2 — Form landing & giao diện

| REQ ID | Tên yêu cầu | Mô tả | Acceptance Criteria | Trạng thái | Cập nhật lần cuối | Nguồn |
|---|---|---|---|---|---|---|
| REQ-LANDING-13 | Landing hiển thị 3 gói cước | Ngày · Tuần · Tháng | Nhóm `role="radiogroup"` có đúng **3** `input[name=package]`: `daily` (ảnh `card_daily.png`, alt `15 Cents`), `weekly` (`card_weekly.png`, `50 Cents`), `monthly` (`card_monthly.png`, `1,5 USD`) | 🟢 | — | Tài liệu (bảng gói cước) + UI thực tế · mã nguồn HTML |
| REQ-LANDING-14 | Gói Ngày được chọn sẵn | Mặc định | Khi tải landing, `input[value=daily]` có `checked`; thẻ gói Ngày có class `selected` và chiếm cả hàng (`featured`) | 🟢 | — | UI thực tế · mã nguồn HTML |
| REQ-LANDING-15 | Chỉ chọn được một gói | Radio group | Chọn gói khác → gói trước bỏ chọn; luôn đúng 1 thẻ có class `selected` | 🟢 | — | UI thực tế · mã nguồn HTML |
| REQ-LANDING-16 | Ô số thuê bao không sửa được | Chặn đăng ký số khác | `#msisdn` (`type=tel`) có thuộc tính `readonly`; người dùng không gõ được vào ô | 🟢 | — | Tài liệu · kịch bản #1 + mã nguồn HTML |
| REQ-LANDING-17 | Số không hợp lệ thì không gửi form | Validate phía trình duyệt | Bấm đăng ký khi số sau chuẩn hoá (REQ-LANDING-19) không khớp `^\d{8,9}$` → form **không** gửi (không có request `POST /callback/get-otp`), ô số thêm class `invalid` | 🟢 | — | UI thực tế · mã nguồn HTML (chưa trigger — ô readonly) |
| REQ-LANDING-18 | Thông báo số không hợp lệ | Message tiếng Khmer | Trường hợp REQ-LANDING-17 → `#msisdn-error` hiện nguyên văn mục 5 · M-01 | 🟢 | — | UI thực tế · mã nguồn HTML |
| REQ-LANDING-19 | Số được chuẩn hoá trước khi gửi | Cùng quy tắc `to_msisdn()` phía server | Bỏ ký tự không phải số → nếu dài hơn 9 số và bắt đầu `855` thì bỏ `855` → bỏ một số `0` đầu → giá trị gửi đi trong field `msisdn` là số nội địa 8–9 chữ số | 🟢 | — | UI thực tế · mã nguồn HTML |
| REQ-LANDING-20 | Server từ chối số khác số MPS nhận diện | Không đăng ký hộ số khác | Gửi đăng ký với số khác số đã nhận diện → bị từ chối, không gửi OTP; log `status = blocked` | 🟢 | — | Tài liệu · "Giới hạn đã biết" |
| REQ-LANDING-21 | Landing hiển thị bằng tiếng Khmer | Ngôn ngữ giao diện | `html lang="km"`; nút đăng ký nguyên văn `ចុះឈ្មោះឥឡូវនេះ`; placeholder ô số `សូមបញ្ចូលលេខទូរស័ព្ទ` | 🟢 | — | UI thực tế · mã nguồn HTML |

### S3 — OTP & trừ tiền

| REQ ID | Tên yêu cầu | Mô tả | Acceptance Criteria | Trạng thái | Cập nhật lần cuối | Nguồn |
|---|---|---|---|---|---|---|
| REQ-LANDING-22 | Bấm đăng ký thì nhận SMS OTP và hiện ô nhập OTP | Bước xin OTP | Từ trạng thái REQ-LANDING-10, chọn gói, bấm `ចុះឈ្មោះឥឡូវនេះ` → form `POST /callback/get-otp` (`package`, `msisdn`) → số nhận SMS OTP; màn hình hiện ô nhập OTP | 🟢 | — | Tài liệu · kịch bản #2 + mã nguồn HTML (form action) |
| REQ-LANDING-23 | Xin OTP không trừ tiền | Chỉ bước xác nhận mới trừ | Sau REQ-LANDING-22, số dư tài khoản không đổi | 🟢 | — | Tài liệu · "Log tra soát" (`step = OTP`: chưa trừ tiền) |
| REQ-LANDING-24 | Nhập sai OTP thì báo OTP sai | | Nhập OTP sai, bấm Xác nhận → hiện thông báo OTP sai (text: ❔ AMB-LANDING-07) | 🟢 | — | Tài liệu · kịch bản #3 |
| REQ-LANDING-25 | Nhập sai OTP thì được nhập lại | | Sau REQ-LANDING-24, vẫn ở màn nhập OTP, ô OTP nhập được, gửi lại được | 🟢 | — | Tài liệu · kịch bản #3 + sơ đồ |
| REQ-LANDING-26 | Nhập sai OTP không trừ tiền | | Sau REQ-LANDING-24, số dư tài khoản không đổi | 🟢 | — | Tài liệu · kịch bản #3 |
| REQ-LANDING-27 | OTP hết hạn sau 60 giây | | Nhập OTP đúng sau khi đã quá **60 giây** kể từ lúc gửi → không đăng ký được, báo OTP hết hạn; log `status = otp_expired` | 🟢 | — | PO chốt 22-10-2026 |
| REQ-LANDING-28 | Thiếu tiền thì báo không đủ tiền | | Số dư thấp hơn giá gói, nhập đúng OTP → hiện thông báo không đủ tiền (text: ❔ AMB-LANDING-07) | 🟢 | — | Tài liệu · kịch bản #6 |
| REQ-LANDING-29 | Thiếu tiền thì quay lại bước nhập OTP | | Sau REQ-LANDING-28, màn hình quay về bước nhập OTP | 🟢 | — | PO chốt 22-10-2026 (khớp sơ đồ; đoạn văn tài liệu lỗi thời) |
| REQ-LANDING-30 | Thiếu tiền không trừ tiền | | Sau REQ-LANDING-28, số dư không đổi, gói không được ghi | 🟢 | — | Tài liệu · kịch bản #6 |
| REQ-LANDING-31 | Đúng OTP, đủ tiền thì báo đăng ký thành công | | Nhập đúng OTP còn hạn, số dư ≥ giá gói → hiện thông báo đăng ký thành công (text: ❔ AMB-LANDING-07) | 🟢 | — | Tài liệu · kịch bản #4 |
| REQ-LANDING-32 | Sau đăng ký thành công 3 giây thì vào game đã đăng nhập | | Sau REQ-LANDING-31 khoảng **3 giây** → tự chuyển vào game, không hiện popup đăng nhập của game | 🟢 | — | Tài liệu · kịch bản #4 |
| REQ-LANDING-33 | Trừ đúng giá gói đã chọn | | Số dư giảm đúng: Ngày 15 cents · Tuần 50 cents · Tháng 1,5 USD | 🟢 | — | Tài liệu · kịch bản #4 + bảng gói cước |
| REQ-LANDING-34 | Gold/diamond chỉ được cộng một lần | | Sau một lần đăng ký thành công, gold/diamond trong game tăng đúng một lần | 🟢 | — | Tài liệu · kịch bản #4 |
| REQ-LANDING-35 | Có nút "Gửi lại" để xin lại OTP | | Ở màn nhập OTP có nút "Gửi lại" (text nguyên văn: ❔ AMB-LANDING-07); bấm → gửi OTP mới | 🟢 | — | PO chốt 22-10-2026 |
| REQ-LANDING-36 | Tối đa 3 lần xin OTP trong 10 phút | Lần thứ 4 bị chặn | Xin OTP lần 1 lúc T, lần 2 và 3 trong 10 phút → đều gửi được; lần 4 trước T + 10 phút → báo đã xin OTP quá nhiều lần, không gửi SMS; log `status = limited` | 🟢 | — | Tài liệu · kịch bản #9 + cấu hình `otp.max_send = 3` + PO chốt 22-10-2026 (mốc tính từ lần xin đầu) |
| REQ-LANDING-37 | Giới hạn xin OTP tính theo số thuê bao | Không reset khi đổi phiên | (1) Xin 3 lần → (2) xoá cookie/dữ liệu trang **hoặc** mở trình duyệt khác cùng SIM → (3) xác nhận phiên mới (không còn cookie cũ) → (4) xin lần 4 trước T + 10 phút → vẫn bị chặn như REQ-LANDING-36 | 🟢 | — | PO chốt 22-10-2026 (lệch cấu hình "/ phiên" — AMB-LANDING-05) |
| REQ-LANDING-38 | Bấm "Gửi lại" được đếm vào giới hạn | | Bấm Đăng ký (lần 1) + "Gửi lại" 2 lần (lần 2, 3) → lần "Gửi lại" thứ 3 bị chặn | 🟢 | — | PO chốt 22-10-2026 |
| REQ-LANDING-39 | Xin lại sau khi sai hoặc hết hạn OTP vẫn được đếm | | Xin OTP → nhập sai → xin lại → để OTP hết hạn → xin lại → lần xin kế tiếp (lần 4) bị chặn | 🟢 | — | PO chốt 22-10-2026 |
| REQ-LANDING-40 | Hết 10 phút từ lần xin đầu thì xin OTP lại được | | Đã bị chặn ở lần 4 → xin lại lúc ≥ T + 10 phút → gửi được OTP (số lần được xin tiếp: ❔ AMB-LANDING-11) | 🟢 | — | PO chốt 22-10-2026 |

### S4 — Log đối soát (Dev xác minh — QA không có quyền CSDL)

| REQ ID | Tên yêu cầu | Mô tả | Acceptance Criteria | Trạng thái | Cập nhật lần cuối | Nguồn |
|---|---|---|---|---|---|---|
| REQ-LANDING-41 | Mỗi lần xin OTP ghi một dòng log `step = OTP` | | Sau mỗi lần bấm Đăng ký / Gửi lại, `LANDING_REGISTER_LOG` (DB `game_farm`) có thêm đúng 1 dòng `step = 'OTP'`, đúng `msisdn`, `package` | 🟢 | — | Tài liệu · "Log tra soát" + kịch bản #10 |
| REQ-LANDING-42 | Mỗi lần xác nhận OTP ghi một dòng log `step = REGISTER` | | Sau mỗi lần bấm Xác nhận OTP, có thêm đúng 1 dòng `step = 'REGISTER'` | 🟢 | — | Tài liệu · "Log tra soát" |
| REQ-LANDING-43 | Hai bước của cùng giao dịch có cùng `req_id` | | Dòng `OTP` và dòng `REGISTER` của một lần đăng ký có `req_id` bằng nhau | 🟢 | — | Tài liệu · "Log tra soát" |
| REQ-LANDING-44 | `req_id` khớp `cpRequestId` bên Java | Đối soát trừ tiền | Với mỗi dòng `REGISTER` đã gọi API, `VP_BILLING_ACTIVITY` có dòng `cpRequestId = req_id` | 🟢 | — | Tài liệu · "Log tra soát" (câu SQL đối chiếu) |
| REQ-LANDING-45 | Giá lưu theo đơn vị MPS | | Gói Ngày 15 cents lưu `price = 150000`. Giá trị lưu cho gói Tuần / Tháng: ❔ tài liệu chỉ nêu ví dụ gói Ngày (AMB-LANDING-12) | 🟢 | — | Tài liệu · "Log tra soát" |
| REQ-LANDING-46 | OTP trong URL log được che | Không lộ mã OTP | Cột `api_url` không chứa mã OTP thật; vị trí OTP hiện `***` | 🟢 | — | Tài liệu · "Log tra soát" |
| REQ-LANDING-47 | `status` chỉ nhận giá trị trong danh mục | | `status` ∈ {`otp_sent`, `success`, `success_after_timeout`, `wrong_otp`, `otp_expired`, `no_balance`, `already_subscribed`, `failed`, `timeout`, `blocked`, `limited`} | 🟢 | — | Tài liệu · "Log tra soát" |
| REQ-LANDING-48 | Log ghi nguồn quảng cáo và thiết bị | | Mỗi dòng có `utm_source`, `click_id` (khi URL có), `ip`, `user_agent` | 🟢 | — | Tài liệu · "Log tra soát" |

## 4. Đặc tả trường dữ liệu

Form `#register-form` · `method="post"` · `action="/callback/get-otp"` · `data-cc="855"` · `data-local-max="9"` · `data-local-regex="\d{8,9}"`

| Field (Label) | Loại UI | Required | Ràng buộc | REQ liên quan | Ghi chú |
|---|---|---|---|---|---|
| Gói cước (`package`) | Radio group — 3 thẻ ảnh | Có (luôn có 1 gói chọn) | `daily` · `weekly` · `monthly`; mặc định `daily` | 13, 14, 15 | Input radio ẩn (`opacity:0`), chọn bằng bấm thẻ ảnh |
| Số thuê bao (`msisdn`, `#msisdn`) | `input type=tel`, `inputmode=numeric`, `autocomplete=tel` | Có | `readonly`; giá trị do nhận diện điền; sau chuẩn hoá phải khớp `^\d{8,9}$` | 10, 16, 17, 19 | Placeholder `សូមបញ្ចូលលេខទូរស័ព្ទ` |
| Nút đăng ký | `button type=submit .btn-primary` | — | Text `ចុះឈ្មោះឥឡូវនេះ`; bấm hợp lệ → hiện lớp chờ | 21, 22 | Có hiệu ứng nhấp nháy `pulse` |
| Ô nhập OTP | ❔ chưa khảo sát | — | Độ dài OTP chưa biết; hết hạn 60 giây | 22, 24, 27 | Cần ảnh từ điện thoại 4G Metfone |
| Nút "Gửi lại" | ❔ chưa khảo sát | — | Mỗi lần bấm đếm vào giới hạn 3 lần | 35, 38 | |
| Nút Xác nhận OTP | ❔ chưa khảo sát | — | | 24, 31 | |

## 5. Business Rules & Validation Messages

| Mã | REQ ID | Rule / Trigger | Thông báo (nguyên văn) | Nguồn |
|---|---|---|---|---|
| M-01 | REQ-LANDING-18 | Số không hợp lệ khi bấm đăng ký | `សូមបញ្ចូលលេខទូរស័ព្ទឱ្យបានត្រឹមត្រូវ` | Mã nguồn HTML |
| M-02 | REQ-LANDING-24 | Sai OTP | ❔ chưa thu thập | AMB-LANDING-07 |
| M-03 | REQ-LANDING-27 | OTP hết hạn / hết phiên OTP | ❔ — tài liệu nói đang là tiếng Anh | AMB-LANDING-03, 07 |
| M-04 | REQ-LANDING-28 | Không đủ tiền | ❔ chưa thu thập | AMB-LANDING-07 |
| M-05 | REQ-LANDING-31 | Đăng ký thành công | ❔ chưa thu thập | AMB-LANDING-07 |
| M-06 | REQ-LANDING-36 | Xin OTP quá nhiều lần | ❔ — tài liệu nói đang là tiếng Anh | AMB-LANDING-03, 07 |
| M-07 | REQ-LANDING-20 | Số khác số nhận diện | ❔ chưa thu thập | AMB-LANDING-07 |

## 6. Luồng xử lý (User Flow)

1. Người dùng mở link chính.
2. Máy tính → `302` sang `/assets/` → game, popup đăng nhập của game (REQ-LANDING-01, 02).
3. Điện thoại https → server chuyển `http://…/?mps_http=1` (REQ-LANDING-07).
4. Điện thoại http → landing tải, lớp chờ hiện, trình duyệt gọi MPS `mobile.html` → nhận `DATA`/`SIG` → `POST /mps-detect` (field `req`, `mr`, `d`) (REQ-LANDING-04).
5. `/mps-detect` trả JSON:
    - `action = fill` + `msisdn` → điền số, ẩn lớp chờ (REQ-LANDING-10)
    - có `url` → vào game đã đăng nhập (REQ-LANDING-09)
    - không có kết quả → vào game chưa đăng nhập (REQ-LANDING-05)
6. Quá 120 giây không có trả lời MPS → gửi rỗng → vào game (REQ-LANDING-06).
7. Chọn gói → bấm đăng ký → `POST /callback/get-otp` → SMS OTP → nhập OTP → Xác nhận (REQ-LANDING-22).
8. Sai OTP / thiếu tiền → báo lỗi, ở lại bước nhập OTP; hết hạn sau 60 giây; "Gửi lại" tối đa tới lần 3 trong 10 phút (REQ-LANDING-24 → 40).
9. Thành công → trừ tiền, ghi gói, cộng gold → sau 3 giây vào game đã đăng nhập (REQ-LANDING-31 → 34).

## 7. Tầng network quan sát được

| Request | Kết quả quan sát | Ghi chú |
|---|---|---|
| `GET /` (UA desktop) | `302` → `/assets/` | Server phân nhánh theo user-agent |
| `GET /` (UA điện thoại) | `200`, trang landing | |
| `GET https://…/` (UA desktop) | `302` → `http://…/assets/` | |
| `GET https://…/` (UA điện thoại) | Trang cuối `http://…/?mps_http=1` | Chuỗi chuyển hướng không bắt được ở công cụ |
| `GET paymentgateway.metfone.com.kh/MPS/mobile.html?PRO=Vtech&CMD=MSISDN&SER=Vtech_MyLand&SUB=Vtech_MyLand_Daily&DATA=<chuỗi mã hoá theo phiên>&SIG=<chữ ký>` | `200`, body chứa `DATA=<chuỗi mã hoá>` | Gọi từ trình duyệt (CORS). Ngoài mạng Metfone vẫn kết nối được, nhưng không nhận diện số |
| `GET …/MPS/favicon.ico` | Thăm dò kết nối tới MPS | Chỉ để ghi log |
| `POST /mps-detect` (`req=<mã phiên L1_…>`, `mr=<DATA/SIG>`, `d=<JSON diễn biến>`) | `200`, JSON `{action, url \| msisdn, debug}` | ⚠️ Có khối `debug` (kết quả giải mã MPS, `RES`, `MOBILE`, lý do) trả về trình duyệt — AMB-LANDING-06 |
| `POST /callback/get-otp` (`package`, `msisdn`) | ❔ chưa quan sát | Cần điện thoại 4G Metfone |
| `GET /assets/index.html?cp=laoId1&data=&token=&t=<timestamp>` | Trang game | `cp=laoId1` — AMB-LANDING-08 |
| `GET /admin` | `404` | |
| Bên thứ ba | Google Analytics `G-6FPCEQ61ME` (landing) · `api.gameanalytics.com` · `api-mylandkh.gamebatta.com/api/farm/logSession/create` (game) | |

Console trình duyệt in từng bước nhận diện với tiền tố `[MPS]` (thời gian, URL MPS, nội dung MPS trả về, kết quả giải mã).

## 8. Yêu cầu phi chức năng (quan sát được)

| Hạng mục | Quan sát | Nguồn |
|---|---|---|
| Thời gian nhận diện (ngoài mạng Metfone) | ≈ 0,3 giây tới MPS, ≈ 0,7 giây tới lúc chuyển vào game | Kiểm chứng thực tế (console `[MPS]`) |
| Thời gian chờ tối đa | 120 giây | Mã nguồn + tài liệu |
| Giao thức | Landing phải chạy `http` để gọi được MPS | Tài liệu + mã nguồn |
| Bố cục | Trang rộng tối đa `480px`, căn giữa — thiết kế cho điện thoại | Mã nguồn CSS |
| Game trên viewport dọc `375×812` | Game hiển thị xoay ngang (canvas) | Ảnh evidence mobile |

## 9. Danh mục Evidence

| Tệp | Màn hình | Trạng thái | REQ chứng minh |
|---|---|---|---|
| [`evidence/desktop_vao_game_chua_dang_nhap_viewport.jpg`](evidence/desktop_vao_game_chua_dang_nhap_viewport.jpg) | Game trên máy tính (Chrome 152, `757×878`) | Đã chuyển từ link chính, popup "WELCOME TO MYLAND" chưa đăng nhập | REQ-LANDING-01 |
| [`evidence/mobile_ngoai_metfone_vao_game_viewport.jpg`](evidence/mobile_ngoai_metfone_vao_game_viewport.jpg) | Game trên điện thoại giả lập (`375×812`, UA Android) | Mạng ngoài Metfone, đã chuyển vào game | REQ-LANDING-05 |

**Chưa có ảnh:** form landing (trang chuyển vào game sau ≈ 0,7 giây khi không nhận diện được), màn OTP, các thông báo. REQ-LANDING-13 → 21 có nguồn là mã nguồn HTML với số liệu ghi trong AC; REQ-LANDING-22 → 40 chỉ có nguồn tài liệu/PO — cần ảnh từ điện thoại 4G Metfone.
