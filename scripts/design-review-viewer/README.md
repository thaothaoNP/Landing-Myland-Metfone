# Design Review Viewer

Trang web nhỏ gọn để **xem và lọc kết quả so thiết kế Figma ↔ UI thật**. Trang có thống kê DIFF theo trạng thái, mức độ, loại và người xử lý; xem ảnh Figma | App đặt cạnh nhau cùng ảnh đánh dấu; xem bảng đo tự động của từng khung; xuất Excel.

Viewer đọc output của `/compare-ui-from-figma-design`: `docs/design-reviews/[_<hệ-thống>/]<module>/<nền-tảng>/run_<YYYYMMDD_HHMMSS>/design_compare_report.md` + `evidence/*.png`, và danh mục `README.md` của từng hệ thống.

---

## Dùng ngay (không cần cài gì)

Mở [`bundle.html`](bundle.html) bằng trình duyệt — double-click là được. Không cần build, không cần `node_modules`, chạy offline.

Kéo thả, hoặc bấm **+ Import thư mục** / **+ Import file .md** ở góc trên. Hai nút này luôn hiện, kể cả sau khi đã nạp dữ liệu, nên bấm thêm được bất cứ lúc nào mà không phải nạp lại từ đầu:

```
docs/design-reviews/_book-api/README.md                                        ← danh mục của hệ thống — Mã kế tiếp, DIFF mở (H/M/L), lần chạy gần nhất
docs/design-reviews/_book-api/auth/mobile/run_20261020_135829/design_compare_report.md   ← báo cáo 1 lần chạy
docs/design-reviews/_book-api/auth/mobile/run_20261020_135829/evidence/*.png   ← ảnh Figma | App, ảnh đánh dấu, ảnh từng đoạn cuộn
```

Cách nhanh nhất: kéo thả **nguyên thư mục `docs/design-reviews/`**. Cách này nạp một lần đủ danh mục, mọi báo cáo và mọi ảnh, của mọi module, nền tảng và lần chạy.

> ⚠️ **Hộp thoại "+ Import thư mục" chỉ chọn được 1 thư mục mỗi lần.** Đây là giới hạn của hộp thoại chọn thư mục của hệ điều hành, không phải do trang. Dữ liệu nạp nhiều lần sẽ **cộng dồn** chứ không ghi đè. Muốn chọn nhiều thư mục trong 1 lần thì dùng kéo-thả: giữ Ctrl chọn nhiều thư mục trong Explorer rồi kéo cả cụm vào trang.

> Toàn bộ xử lý chạy trong trình duyệt, không gửi dữ liệu đi đâu. Phần **chữ** của báo cáo được lưu vào `localStorage`, nên lần mở sau vẫn còn. **Ảnh thì không lưu được**: mỗi lần mở lại trang phải kéo thả lại thư mục (hoặc thư mục `evidence/`) để xem ảnh. Trang hiện cảnh báo *"Chưa nạp ảnh evidence"* để nhắc.

---

## Module · nền tảng · lần chạy lấy từ đâu

| Cách nạp | Viewer đọc từ |
|---|---|
| Kéo thả / Import thư mục | **Đường dẫn**: `[_<hệ-thống>/]<module>/<nền-tảng>/run_<…>/`. Thư mục bắt đầu bằng `_` là namespace hệ thống (không bắt buộc) |
| Import lẻ 1 file `.md` (trình duyệt không cho biết đường dẫn) | **Tiêu đề** `# So thiết kế Figma ↔ <nền tảng> — <tên> (`<PREFIX>`)`. Mã lần chạy suy từ ô *Ngày chạy* và được đánh dấu `≈` trong danh sách file |

Nạp lại đúng file đó kèm đường dẫn thì bản nạp lẻ được **thay thế**, không sinh dòng trùng.

---

## Nhiều lần chạy của cùng module × nền tảng

- **Lần chạy mới nhất** (so theo `run_<YYYYMMDD_HHMMSS>`) quyết định **trạng thái hiện tại** của mỗi mã DIFF.
- Mọi lần chạy có liệt kê mã đó được gom thành **Lịch sử qua các lần chạy** trong panel chi tiết DIFF. Panel cho biết mỗi lần chạy ghi trạng thái, mức độ và người xử lý gì; mô tả đổi thì hiện mô tả cũ.
- Nếu lần chạy mới nhất **không** liệt kê một mã đã có ở lần trước, trạng thái lấy theo lần gần nhất có mã đó, và panel ghi chú rõ điều này.
- Tab **Khung** mặc định chỉ hiện lần chạy mới nhất. Tick *"Hiện cả các lần chạy cũ"* để xem lại.

### Trạng thái DIFF

| Ghi trong báo cáo | Viewer hiểu là |
|---|---|
| `🔴 Mở` · ô trống · báo cáo cũ **không có** cột `Trạng thái` | 🔴 Mở |
| `✅ Đã khắc phục (run_…)` | ✅ Đã khắc phục |
| `⚪ Chấp nhận — …` | ⚪ Chấp nhận |
| `🗑️ Không còn áp dụng (…)` | 🗑️ Không còn áp dụng |

Phần ghi chú sau nhãn (lần chạy khắc phục, lý do chấp nhận…) được giữ nguyên. Ghi chú này hiện khi rê chuột lên nhãn, trong panel chi tiết, và ở cột *Ghi chú trạng thái* khi xuất file.

---

## Tính năng

| Nhóm | Chi tiết |
|---|---|
| **Import** | Kéo thả, hoặc 2 nút cố định **+ Import thư mục** / **+ Import file .md**. Nạp nhiều lần để gộp nhiều hệ thống, module, nền tảng. File `.md` không phải báo cáo so thiết kế thì bị bỏ qua |
| **Danh mục** | Bảng danh mục `README.md` (Module · Nền tảng · Figma · Lần chạy gần nhất · Khung đã so · DIFF đã dùng · Mã kế tiếp · DIFF mở) và bảng Nhật ký, đặt trong khối gập được ở đầu trang. Khi đã có báo cáo thì khối này tự gập |
| **Thống kê** | DIFF đang mở · High đang mở · Dev / Design / Cần PO quyết (mở) · Đã khắc phục · Khung đã so / tổng · ❔ Không so được · Số báo cáo. Thẻ thống kê tính theo module/nền tảng đang chọn; chip lọc không ảnh hưởng |
| **Cảnh báo tự động** | Xem mục dưới |
| **Tab DIFF** | Bảng Mã · Trạng thái · Module · Nền tảng · Khung · Loại · Mức độ · Ai xử lý · Mô tả. Click header để sort; Mức độ, Trạng thái và Ai xử lý sort theo thứ bậc, không theo chữ cái. Chip lọc Trạng thái / Mức độ / Loại / Ai xử lý · chọn Module, Nền tảng · tìm toàn văn (mã, mô tả, số đo thực tế/thiết kế, mã/tên khung, tên ảnh evidence) |
| **Tab Khung** | Lưới khung theo từng báo cáo, mỗi thẻ gồm: mã · node-id · tên · kết quả · các mã DIFF (bấm để mở DIFF) · ảnh Figma \| App. Bấm thẻ để mở chi tiết khung: thông tin bản đồ màn hình, ảnh lớn, mọi ảnh evidence khác cùng tiền tố mã khung (`A-03_*.png`), và **bảng đo tự động** (`<details>` của mục 4) đã dựng thành bảng |
| **Tab Báo cáo** | Mỗi lần chạy một thẻ. Thẻ có số DIFF theo trạng thái, số khung đã so, toàn bộ bảng thông tin đầu báo cáo (Mode · Ngày chạy · Figma · Độ trung thực · Bản build · Môi trường · Dung sai · Phạm vi…), và các mục 1 Tóm tắt · 5 Không so được · 6 Ghi chú tham khảo · 7 Việc tiếp theo |
| **Chi tiết DIFF** | Đủ mọi cột, gồm cả *Thực tế (số đo)* và *Thiết kế (số đo)*. Ảnh evidence (side + marked) hiện thành thumbnail, bấm để xem giữa màn hình. Panel có thêm bảng lịch sử qua các lần chạy |
| **Xem ảnh** | Lightbox giữa màn hình, phím ← → để lướt các ảnh trong cùng panel, Esc để đóng |
| **Export** | **CSV** và **Excel (.xlsx)**: xuất đúng bảng DIFF đang hiển thị sau lọc/tìm. Cột Trạng thái tô màu (Mở đỏ · Đã khắc phục xanh · Chấp nhận xám · Không còn áp dụng tím), cột Mức độ cũng tô màu |
| **Xoá tất cả** | Xoá hết báo cáo và ảnh đã nạp (kể cả trong `localStorage`), rồi quay về màn hình kéo thả trống |

---

## Cảnh báo tự động

| Cảnh báo | Kích hoạt khi | Vì sao quan trọng |
|---|---|---|
| 🔴 **DIFF High đang mở** | Có DIFF mức High mà trạng thái hiện tại là Mở | Lệch nặng nhất, xử lý trước |
| 🟡 **DIFF "Cần PO quyết" còn mở** | Ai xử lý = Cần PO quyết, trạng thái Mở | Dev và Design đều chưa làm được gì cho tới khi PO chốt |
| 🔵 **Khung ❔ chưa so được** | Bản đồ màn hình của lần chạy mới nhất có khung với kết quả `❔ …`. Cảnh báo liệt kê luôn các dòng của mục 5 (gồm cả trạng thái con không so được, VD toast) | Phần thiết kế chưa được kiểm, dễ tưởng nhầm là đã so đủ |
| 🟡 **DIFF mở thiếu link evidence** | Cột Evidence không có link ảnh nào | Người nhận DIFF không có bằng chứng để xem |
| 🔵 **Chưa nạp ảnh evidence** | Đã có báo cáo nhưng chưa có ảnh nào (VD vừa mở lại trang) | Ảnh không được lưu giữa các lần mở |
| 🔵 **Báo cáo nạp lẻ không có đường dẫn** | Mã lần chạy phải suy từ *Ngày chạy* | Nạp cả thư mục để có đúng module / nền tảng / lần chạy |

Viewer **không** phát hiện được trường hợp cùng một mã DIFF mang nghĩa khác nhau ở hai lần chạy. Quy ước của workflow là không đánh lại mã, nên trường hợp này không được kiểm.

---

## Evidence (ảnh)

Giống `bugs-viewer`: trình duyệt không tự đọc được ảnh trên đĩa khi mở qua `file://`, nên ảnh phải do người dùng nạp vào trang. Viewer khớp ảnh theo **tên file**. Nếu nhiều lần chạy có ảnh trùng tên (VD `A-01_sign_in_side.png` ở hai `run_*`), viewer ưu tiên ảnh nằm trong đúng thư mục `run_<…>` của báo cáo đang xem. Nạp lẻ ảnh không kèm đường dẫn thì dùng ảnh nạp sau cùng.

Link ảnh trong ô bảng (`[A-01 side](evidence/A-01_sign_in_side.png)`) được hiển thị thành nút 🖼. Link ảnh chưa nạp thì hiện nút gạch đứt *"chưa nạp"*.

---

## Định dạng Markdown được hỗ trợ

| Phần | Nhận diện bằng |
|---|---|
| File báo cáo | Tiêu đề `# So thiết kế Figma ↔ …`, hoặc có cả mục `## … Bản đồ màn hình` lẫn `## … Danh sách DIFF` |
| File danh mục | Tiêu đề `# Danh mục So thiết kế …`, hoặc có bảng với cột `Mã kế tiếp` |
| Thông tin đầu báo cáo | Bảng 2 cột `Mục \| Giá trị` trước mục `## 1.` |
| Bản đồ màn hình | Bảng có cột `Mã khung`, cùng `Khung Figma (node-id)` · `Trạng thái vẽ` · `Cách tới trên app` · `Kết quả` · `DIFF`. Cột DIFF ghi số ngắn (`01 · 02`) thì tự ghép tiền tố mã DIFF của báo cáo |
| Danh sách DIFF | Bảng có cột `Mã`. Các cột còn lại tìm **theo tên**, không theo vị trí, nên thiếu cột `Trạng thái` (báo cáo cũ) vẫn đọc được |
| Chi tiết từng khung | Heading `### <mã khung> · <tên>` · ảnh `![…](evidence/…)` · khối `<details><summary>…</summary> … </details>` chứa bảng đo |
| Mục 5 · 6 · 7 | Tìm heading theo chữ (*không so được* · *ghi chú tham khảo* · *việc tiếp theo*), không phụ thuộc số thứ tự |
| Ô bảng | `**đậm**` · `*nghiêng*` · `` `code` `` · `<br>` · `\*` · link ảnh (thành nút xem ảnh) · link `https://` (mở tab mới) · link `.md` tương đối (chỉ hiện chữ — trang không mở được file khác qua `file://`) |

Ô placeholder (`—`, `-`, `N/A`) được coi là **không có dữ liệu**.

---

## Hook cho kiểm thử tự động

`window.__loadTexts({ "<đường/dẫn/design_compare_report.md>": "<nội dung>" , … })` nạp markdown bằng đúng luồng mà kéo thả dùng: đọc module, nền tảng và lần chạy từ đường dẫn, lưu `localStorage`, render lại. Hàm trả về số file đã nhận. Hook dùng để kiểm thử bằng Playwright mà không cần thao tác hộp thoại chọn file, và không đổi hành vi gì với người dùng thường. Với Playwright, cách gần thực tế nhất vẫn là `page.setInputFiles('#folder', '<đường dẫn thư mục docs/design-reviews>')`.

---

## Vì sao là 1 file HTML thuần

Cùng lý do với `execution-viewer`, xem [`../execution-viewer/README.md`](../execution-viewer/README.md) mục cuối. File `.xlsx` được dựng thủ công bằng zip + Office Open XML (cùng bộ hàm với `bugs-viewer`, không dùng SheetJS) để giữ `bundle.html` nhẹ và mở offline được.

Muốn đổi giao diện thì sửa thẳng trong `bundle.html`: CSS nằm ở `<style>` đầu file, logic nằm ở `<script>` cuối file, chia sẵn các khối `PARSER (generic)` · `PARSER (đặc thù design-compare)` · `STATE` · `MARKDOWN → HTML` · `DERIVED` · `RENDER` · `EXPORT` · `EVENTS`.

Màu thương hiệu `#4DBD44` (xanh) khai báo ở biến CSS `--brand`, đồng bộ với các viewer khác. Riêng logo dùng tím (`--design`) để nhận ra ngay đây là trang so thiết kế.
