# Mode MOBILE — thu dữ liệu UI thật trên Android / iOS / Hybrid

> Bước 3 của skill. Thao tác phiên Appium, nhận diện loại app, locator: skill [`skills-mobile-debug-agent`](../../skills-mobile-debug-agent/SKILL.md) · [`appium_rules.md`](../../../rules/appium_rules.md).

---

## 1. Mở phiên & đo thông số thiết bị (một lần mỗi phiên)

```
appium_session_management(create) → appium_context(list) → appium_get_page_source → nhận diện loại app
appium_mobile_device_info(action=info)   → displayDensity · realDisplaySize · platformVersion · locale
```

| Thông số | Android | iOS |
|---|---|---|
| Hệ số px → đơn vị | `density / 160` (VD 480 → 3) — từ `displayDensity` hoặc `adb shell wm density` | `scale` 2 / 3 theo dòng máy — page source đã ở **pt** |
| Status bar (loại phần tử hệ thống) | `adb shell dumpsys window \| grep -E "type=statusBars"` → `frame=[0,0][W,<top-px>]` → `--top-px` của `android-tree` | Theo dòng máy (Dynamic Island 59 pt · notch 47 pt · không notch 20 pt) — ghi rõ nguồn |
| **Mốc dọc `--actual-top`** | **Đỉnh khối header** của app (y của View header trong spec, đơn vị dp) — đo một lần, dùng cho mọi khung. App tràn viền hay vẽ header lấn vào status bar: mốc status bar sẽ làm lệch giả mọi phần tử | Như Android — y của header (pt) |
| Thanh điều hướng đáy | `type=navigationBars` → chiều cao px | Home indicator 34 pt |
| Cỡ chữ hệ thống | `adb shell settings get system font_scale` → phải `1.0` | Settings › Display › Text Size mặc định — hỏi user nếu là máy thật |
| Dark mode | `adb shell cmd uimode night` → `no` (hoặc đúng chế độ Figma vẽ) | Settings › Display — theo khung Figma |

Ghi tất cả vào mục **Môi trường** của báo cáo — cùng app, đổi máy là đổi số đo.

**Loại app quyết định nguồn dữ liệu:**

| Loại (skill mobile-debug Bước 2) | Lấy chữ + khung | Lấy màu | Ghi chú |
|---|---|---|---|
| Native Android / iOS | Page source | Lấy mẫu trên ảnh (`--png`) | |
| Flutter đã bật semantics | Page source (`content-desc`) | Lấy mẫu trên ảnh | Chữ là `Semantics(label:)` — có thể là mã kiểu `login_button` chứ không phải chữ hiển thị → khớp kém, so chủ yếu bằng ảnh |
| Flutter **chưa** bật semantics | ❌ Không có cây | Ảnh | Chỉ so được bằng **ảnh đặt cạnh nhau** + soát tay; báo dev bật semantics |
| Hybrid — WebView **không** debug được (`appium_context` chỉ có `NATIVE_APP`) | Page source — WebView đưa chữ lên cây trợ năng | Lấy mẫu trên ảnh | Hay **gộp** chữ con (`User mgttotal: 3294 users`) và trả khung phần tử thay vì khung chữ |
| Hybrid — có `WEBVIEW_*` | Như trên (appium-mcp chưa có tool chạy JS trong WebView để lấy computed style) | Lấy mẫu trên ảnh | Muốn số đo font/màu chính xác: mở bản web của cùng app bằng mode WEB, cùng bề ngang |

---

## 2. Đưa app về đúng trạng thái khung vẽ

- Đi theo **đường điều hướng** đã ghi ở Screen Map — bấm bằng locator (`appium_find_element` → `appium_gesture action=tap elementUUID`), **không** bấm toạ độ
- Nút **chỉ có icon** (⋮ của dòng, bút sửa, ×) thường không có chữ lẫn `content-desc` → XPath **tương đối** theo chữ cùng hàng: `//*[@text='<chữ của dòng>']/following::android.widget.Button[1]` (đổi `following`/`preceding` theo vị trí icon). Hết cách mới hỏi tester, **không** bấm toạ độ
- **Khung theo vai trò** (khách / đã đăng nhập): gom các khung cùng vai trò chụp liền nhau, đổi vai trò một lần (đăng xuất ↔ đăng nhập) — đỡ phải gõ mật khẩu nhiều lần
- Trạng thái lỗi validation: thực hiện đúng hành động (để trống rồi bấm nút) như khung Figma mô tả
- Nhập dữ liệu: dùng dữ liệu **cùng độ dài** với chữ mẫu trong Figma khi có thể (tên dài/ngắn làm xuống dòng khác)
- **Xoá ô trước khi nhập** — app hay giữ giá trị cũ khi quay lại màn (Back), chữ mới bị nối vào sau. `appium_set_value` thay toàn bộ giá trị; `adb shell input text` thì **nối thêm**
- WebView (React/MUI…) đôi khi **không nhận** giá trị của `appium_set_value` (ô hiện chữ nhưng form vẫn báo *"is required"*): kiểm lại bằng page source / ảnh trước khi chụp khung. Không nhận → gõ bằng `adb shell input text` sau khi chạm vào ô
- Đăng nhập: tài khoản test từ `.env`, **không** ghi vào báo cáo. **Mật khẩu không truyền vào tham số tool Appium** (giá trị hiện trong log) — gõ bằng `adb` trong **một lệnh shell** đọc thẳng từ `.env`, bọc thêm **nháy đơn** để shell của thiết bị không nuốt ký tự đặc biệt (`$ & ! * …`):

  ```bash
  P=$(grep '^<KEY>_PASSWORD=' .env | cut -d= -f2- | tr -d '\r"'); adb -s <udid> shell input text "'$P'"
  ```

  Kiểm đã gõ đủ mà không in mật khẩu: so độ dài ô (page source) với độ dài trong `.env` bằng một đoạn script chỉ in `True/False`. Mật khẩu có nháy đơn hoặc dấu cách → nhờ tester gõ (gom mọi bước cần tester vào một lần)
- **Thứ tự chụp form**: khung *"form sạch"* (Update, Edit) phải vào từ trạng thái sạch — đi qua một khung lỗi validation (Add) trước có thể để lại lỗi trên form sau. Thấy lỗi dính → tái hiện riêng từ đầu: nếu lặp lại thì đó là **lỗi app**, ghi DIFF `STATE` cho Dev
- Đường điều hướng thật có thể khác bản đồ (VD *Logout* chuyển thẳng tới Sign in thay vì Dashboard): đi theo app, ghi đường đi thật vào cột *Cách tới* của Bản đồ màn hình
- Toast/snackbar: chụp **ngay** sau hành động (lệnh chụp kế tiếp, không xen bước khác). Toast biến khỏi cây phần tử sau ~2 giây — **ảnh là bằng chứng**, vị trí đo trên ảnh
- Menu/dialog/bottom sheet mở: cây phần tử chỉ còn lớp phủ → trích Figma với `SCOPE = '<tên khối lớp phủ>'`
- **Đóng lớp phủ bằng chính nó** (chọn một mục, *Cancel*, nút ×) — nút Back hệ thống trên app Hybrid thường **rời cả màn** chứ không đóng menu
- Hộp xác nhận xoá / form lưu trên môi trường dùng chung: mở để chụp rồi **Cancel** — không bao giờ bấm nút hành động thật
- **Ẩn bàn phím** (`appium_mobile_keyboard action=hide`) trước khi chụp — trừ khi khung Figma vẽ bàn phím
- Xoá thông báo trên status bar nếu cần ảnh sạch (không ảnh hưởng số đo vì status bar bị cắt)

---

## 3. Chụp ảnh + page source

```bash
# Ảnh — Android: adb nhanh và không đổ base64 vào ngữ cảnh
adb -s <udid> exec-out screencap -p > reports/design-compare/<run>/<mã>_app.png
```

- `appium_screenshot` (iOS, hoặc khi không có `adb`): tool lưu file **và** trả kèm base64 rất lớn (hàng triệu ký tự) — chỉ dùng khi không có cách khác, lấy `filepath` từ kết quả rồi copy
- Page source: `appium_get_page_source` với `saveToFile: true` → tool trả `filepath` → copy vào `reports/design-compare/<run>/<mã>_source.xml`. **Không** đưa page source vào `docs/`
- Chụp ảnh và page source **liền nhau** ở cùng một trạng thái — giữa hai lệnh không thao tác gì
- WebView vẽ chậm hơn cây phần tử: sau khi bấm, **chờ phần tử đích xuất hiện** (`appium_find_element` chữ của màn mới) rồi mới chụp — chụp ngay thường ra page source của màn **trước**
- Chụp nhiều khung liên tiếp: gói 3 bước (ảnh · page source · `android-tree` + `match`) vào **một** script nhỏ trong scratchpad, gọi `<run> <mã> <đường page source> [figma.json] [tham số match]` — mỗi khung một lệnh, in sẵn tóm tắt để kiểm đúng trạng thái
- **Mở lại ảnh** (`Read`) xác nhận đúng trạng thái trước khi đo

---

## 4. Dựng spec JSON của app

```bash
# Android
python scripts/design-compare/dc.py android-tree <mã>_source.xml --density 480 --top-px 159 --bottom-px 72 \
       --png <mã>_app.png -o reports/design-compare/<run>/<mã>_actual.json

# iOS (page source đã ở pt)
python scripts/design-compare/dc.py ios-tree <mã>_source.xml --scale 3 --top 59 --bottom 34 \
       --png <mã>_app.png -o reports/design-compare/<run>/<mã>_actual.json
```

`--png` bật lấy mẫu màu: mỗi node chữ lấy **màu nền** (màu nhiều nhất trong khung) và **màu chữ** (màu nhiều nhất trong số pixel khác hẳn nền) — kết quả kiểm chứng: `#00b8d9` thiết kế → `#00b8d8` app, ΔE 0,3.

---

## 5. Màn hình dài hơn một màn (khung Figma "full scroll")

1. Đoạn đầu: chụp + `match` bình thường (không `--auto-offset`) — đo được vị trí tuyệt đối. Ảnh Figma của khung dài: `get_screenshot` với `maxDimension` ≥ chiều cao khung (mặc định 1024 sẽ thu nhỏ)
2. Cuộn **một lượng vừa phải** (`appium_gesture action=scroll direction=down`, hoặc `scroll_to_element` tới mốc có chữ) — mỗi đoạn mới phải **chồng lấn** đoạn trước ít nhất một phần tử có chữ
3. Chụp + page source đoạn mới → `match ... --auto-offset` — `dc.py` tính **độ lệch dọc chung** (= độ cuộn + lệch bố cục đã tích luỹ phía trên — không phải độ cuộn) từ các cặp chữ khớp nguyên văn **trước** khi ghép, nhận ra phần tử **cố định** (header sticky, bottom nav — đứng yên dù trang cuộn → ghi ❔ "đã đo ở đoạn đầu"), và bỏ phần tử đã cuộn khỏi màn hoặc nằm khuất **hẳn** sau header cố định
4. Lặp tới cuối khung. Dòng `⤵️ Ngoài màn hình đã chụp` ở đoạn này phải được phủ ở một đoạn khác — cuối cùng **không** được còn dòng ⤵️ nào chưa phủ

Phần tử neo đáy (bottom nav) xuất hiện ở **mọi** đoạn — chỉ tính DIFF ở đoạn đầu.

**Hộp thoại cao hơn màn** (form *Add / Update* vẽ "full"): app cuộn **bên trong** hộp thoại, header + chân hộp thoại đứng yên. Cuộn trong vùng nội dung của hộp thoại (truyền `elementUUID` của vùng đó cho `appium_gesture scroll`), so từng đoạn với `--auto-offset` như màn dài.

**Khung vẽ sẵn ở vị trí đã cuộn** (ghi chú *"đã cuộn xuống phần …"*): cuộn app tới đúng phần đó rồi so **một** đoạn với `--auto-offset`.

---

## 6. Đặc thù mobile phải soát tay

- [ ] Vùng chạm của nút/ô nhập ≥ 48 dp (Android) / 44 pt (iOS) — thiết kế vẽ nhỏ hơn thì ghi DIFF `Design`
- [ ] Nội dung không chui dưới status bar / notch / home indicator (safe area)
- [ ] Bàn phím mở không che ô đang nhập và nút gửi (nếu khung Figma có trạng thái nhập)
- [ ] Chữ dài (tên, email) cắt `…` hay xuống dòng đúng như thiết kế
- [ ] Hộp thoại, bottom sheet, menu: đúng vị trí neo (giữa màn / đáy / cạnh nút)
- [ ] Bảng, hàng nút lọc, tab ngang: có phần nào **khuất ngoài mép phải** không (phần tử trong cây có `x` gần / vượt bề ngang màn) — màn hẹp hay lộ lỗi này nhất
- [ ] Trạng thái rỗng (*No data*): hình + chữ nằm giữa vùng **nhìn thấy**, không phải giữa bề ngang của bảng
