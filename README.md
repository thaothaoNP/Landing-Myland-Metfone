# Claude Testing Skills 🚀

👋 Chào mừng bạn đến với **Claude Testing Skills** phiên bản dành cho **Claude Code**!

Đây là bộ Skills được xây dựng và phát triển bởi **Anh Tester**, dành riêng cho **Học viên học khoá AI tại Anh Tester**. Mục tiêu của repo này là cung cấp sẵn các thiết lập, quy tắc hành vi (Rules), kỹ năng (Skills), và lệnh tùy chỉnh (Commands) chuẩn để hỗ trợ sử dụng AI Agent trên phần mềm **Claude Code** (bao gồm Claude Code CLI và Claude Code Desktop hoặc Claude Code dạng Extention trên VS Code).

Bộ Skills này **không chỉ dành riêng cho Automation** — mà được thiết kế toàn diện cho cả **Manual Testing** lẫn **Automation Testing**, bao phủ toàn bộ vòng đời kiểm thử phần mềm từ phân tích yêu cầu, thiết kế test cases cho đến thực thi và báo cáo kết quả.

Đặc biệt, mọi công đoạn đều được **tích hợp AI một cách có hệ thống**, tạo thành một **quy trình ứng dụng AI hoàn thiện (End-to-End AI Testing Workflow)** — giúp Tester làm việc thông minh hơn, nhanh hơn và hiệu quả hơn trong kỷ nguyên AI.

> 🔌 **Lần đầu cài đặt?** Đọc **[SETUP_CLAUDE.md](SETUP_CLAUDE.md)** — hướng dẫn add **Playwright MCP** thủ công, kết nối **Atlassian / Slack / GitHub / Claude in Chrome**, và setup **Cowork Schedule** để tự động chạy task theo lịch.
>
> 🔄 **Cài xong rồi, chạy cái gì trước?** Đọc **[AI_FULL_FLOW_MANUAL.md](AI_FULL_FLOW_MANUAL.md)** — quy trình 8 chặng cho tình huống phổ biến nhất: hệ thống chỉ có UI, không tài liệu, không bộ test cases. Từ `/discover-system` → requirements → test cases → chạy tay → bug report → retest → ma trận truy vết → báo cáo release.
>
> 🤖 **Đã có bộ test cases, muốn viết script?** Đọc **[AI_FULL_FLOW_AUTOMATION.md](AI_FULL_FLOW_AUTOMATION.md)** — quy trình 8 chặng Automation nối tiếp: `/generate-automation-framework` → sinh script → review code → chạy & tự sửa → bảo trì khi UI/requirements đổi → RTM → Xray.

---

## 🌟 Tính Năng Nổi Bật

- **🔁 Quy Trình AI Hoàn Thiện (End-to-End):** Được xây dựng thành một quy trình ứng dụng AI khép kín — từ phân tích yêu cầu (Requirements), thiết kế test cases (Manual), đến viết script tự động (Automation), tích hợp CI/CD và báo cáo kết quả — tất cả đều có AI hỗ trợ.
- **📋 Manual Testing Tiêu Chuẩn Cao (AI-RBT Framework):**
  - Đánh giá rủi ro theo 3 mức độ `High / Medium / Low Risk`.
  - Checklist validation **15 loại Input Field Types** (Text, Email, Phone, Date, Number, Dropdown, Checkbox/Radio, File Upload, Password, Textarea, OTP/MFA, Date Range, Rich Text, Multi-Select, Range Slider).
  - Tích hợp Scenarios Chuyên Sâu & Non-Functional (Race Condition, Session/Network Resilience, Localization/UTF-8/Emoji, Keyboard A11y, HTTP Status Codes).
  - **AI Self-Quality Gate (7 Tiêu chí):** Đảm bảo Unique TC ID, Step-Expected 1-1, Concrete Test Data, Field Coverage, Automation Metadata Ready, Requirement Coverage (đối soát mọi REQ có ≥1 TC), và **Evidence-verified** (bắt buộc mở hết ảnh evidence trước khi sinh TC — đối soát ảnh nào chống lưng cho TC nào).
  - **Truy vết REQ ID xuyên suốt:** Requirements được gán mã `REQ-<MODULE>-<SỐ>` → mỗi TC có cột `REQ ID` → Bảng Đối Soát Coverage chứng minh "đủ case", sẵn sàng cho `/generate-traceability-matrix`.
- **🌐 API Testing & OWASP Security Standards:**
  - Bao phủ đủ **12 HTTP Status Codes** tiêu chuẩn (`200`, `201`, `400`, `401`, `403`, `404`, `406`, `409`, `413`, `415`, `429`, `500`).
  - Tích hợp **OWASP API Security Checklist** (BOLA/IDOR, Mass Assignment, SQLi/XSS, ReDoS, Sensitive Data Masking).
  - Response time SLA (< 2 giây), Dynamic Auth Token, Teardown/Cleanup test data tự động.
- **🧠 Tối ưu cho QA/Tester:** Tất cả các prompt, rule và command đều được tinh chỉnh dựa trên tư duy và quy trình làm việc thực tế của cả **Manual Tester** lẫn **Automation Engineer**.
- **💻 Hỗ trợ Đa Nền Tảng:** Tương thích với các framework phổ biến như Web (Playwright, Selenium), Mobile (Appium), và API (Playwright API, REST Assured, Pytest Requests, Supertest).
- **🛡️ Tuân thủ Tiêu Chuẩn Cao (Strict Rules):** Đảm bảo AI luôn đi theo cấu trúc Page Object Model (POM), viết code rõ ràng, không đoán bừa locator và tự động sửa lỗi (Self-fix).
- **🇻🇳 Giao Tiếp Bằng Tiếng Việt:** AI được cấu hình để trao đổi, giải thích và báo cáo hoàn toàn bằng Tiếng Việt, thân thiện với người dùng Việt Nam.

---

## 📂 Cấu Trúc Thư Mục Chính

Repo chia làm 2 phần rõ rệt: **khung** (dùng lại cho mọi dự án) và **đầu ra** (dữ liệu của dự án đang làm).

```
claude-testing-skills/
│
│ ══════════ KHUNG — dùng lại cho mọi dự án ══════════
├── .claude/
│   ├── commands/            # 39 lệnh tùy chỉnh (slash commands)
│   ├── rules/               # 6 quy tắc bắt buộc AI phải tuân theo
│   ├── skills/              # 20 kỹ năng chuyên biệt cho AI
│   └── settings.json        # Cấu hình quyền hạn cho Claude Code
├── plans/
│   ├── manual/              # Quy trình 6 bước sinh Manual Test Cases (AI-RBT)
│   ├── automation/          # Quy trình 6 bước sinh Automation Scripts
│   └── cross-module/        # Quy trình phân tích Cross-Module & Ma trận kết hợp
├── prompts/                 # 36 prompt mẫu dùng nhanh (copy → paste → gửi)
├── scripts/
│   ├── testcases-viewer/    # Công cụ web xem/lọc test case
│   ├── execution-viewer/    # Công cụ web xem kết quả chạy, so sánh các lần chạy
│   ├── traceability-viewer/ # Công cụ web xem ma trận truy vết — độ phủ REQ theo module/Story, TC chưa automate, gap
│   ├── bugs-viewer/         # Công cụ web lọc bug theo Severity/Priority/Trạng thái, xem lịch sử retest
│   ├── design-compare/      # Bộ đo so thiết kế Figma ↔ UI thật (figma_extract.js · collect_dom.js · dc.py)
│   └── design-review-viewer/ # Công cụ web lọc DIFF thiết kế, xem ảnh Figma | App
├── CLAUDE.md                # Rule chung cho AI Agent (Claude Code đọc tự động)
├── SETUP_CLAUDE.md          # Hướng dẫn cài Playwright MCP, Connectors & Cowork Schedule
├── AI_FULL_FLOW_MANUAL.md      # Quy trình 8 chặng Manual Testing — chạy command nào, theo thứ tự nào
├── AI_FULL_FLOW_AUTOMATION.md  # Quy trình 8 chặng Automation — nối tiếp từ bộ TC đã review
│
│ ══════════ ĐẦU RA — dữ liệu của dự án đang làm ══════════
├── docs/
│   ├── requirements/
│   │   ├── README.md                          # DANH MỤC module: prefix đã chiếm, mã REQ kế tiếp
│   │   ├── _discovery/                        # bản đồ hệ thống: system_map.md (web + mobile) · api_map.md
│   │   └── <module>/                          # MỘT nghiệp vụ = MỘT thư mục, chung mọi nền tảng
│   │       ├── REQUIREMENTS_<TÊN_MODULE>_SUMMARY.md       # INDEX — tên file bất biến: phần chung + Bản đồ tài liệu
│   │       ├── web/                           # TẦNG NỀN TẢNG — chỉ 3 tên: web · mobile · api
│   │       │   ├── requirements_<module>_web.md
│   │       │   ├── evidence/*.png             # ảnh chụp khi khảo sát
│   │       │   └── stories/                   # khi file nền tảng bị tách
│   │       ├── mobile/                        # requirements_<module>_mobile.md · evidence/android_*.png · ios_*.png
│   │       ├── api/                           # requirements_<module>_api.md — Endpoint Catalog
│   │       ├── analysis/                      # phân tích ticket của module
│   │       └── impact/                        # Impact Report theo ticket
│   ├── testcases/
│   │   ├── README.md                          # DANH MỤC bộ TC: prefix TC ID, độ phủ REQ↔TC
│   │   └── <module>/
│   │       ├── TEST_CASES_<TÊN_MODULE>_SUMMARY.md         # INDEX — tên file bất biến, không chứa dòng TC
│   │       └── web/ · mobile/ · api/          # test_cases_<module>_<nền-tảng>.md · parts/ khi > 40 TC
│   ├── checklists/                            # checklist tick tay — <module>/<nền-tảng>/checklist_<loại>_<YYYYMMDD>.md · _release/<nền-tảng>/
│   ├── executions/
│   │   ├── _release/<nền-tảng>/run_<timestamp>/  # chạy checklist release-readiness
│   │   └── <module>/<nền-tảng>/run_<timestamp>/
│   │       ├── execution_report.md
│   │       └── evidence/*.png
│   ├── traceability/traceability_matrix.md    # RTM — tên file bất biến, ghi đè tại chỗ
│   ├── bugs/                                  # Bug report sinh từ TC FAIL
│   │   ├── README.md                          # DANH MỤC bug — có cột Nền tảng
│   │   └── <module>/<nền-tảng>/BUG_<module>_<ts>_<TC_ID>.md
│   ├── design-reviews/                        # So thiết kế Figma ↔ UI thật — DIFF + ảnh đặt cạnh nhau
│   │   └── <module>/<nền-tảng>/run_<timestamp>/design_compare_report.md
│   └── user-guides/                           # Hướng dẫn sử dụng cho người dùng cuối
│       ├── README.md                          # DANH MỤC — module × role × phiên bản phần mềm
│       └── <module>/user_guide_<module>.md    # INDEX — tên file bất biến
```

> **Chuyển sang dự án mới:** chỉ cần xoá phần **ĐẦU RA** — `rm -rf docs .playwright-mcp task.md .claude/settings.local.json`. Agent tự tạo lại cấu trúc `docs/` ở lần chạy workflow đầu tiên. Chi tiết xem [CLAUDE.md](CLAUDE.md) mục 6b.

### `.claude/` — Bộ não của AI Agent trên Claude Code

| Thư mục         | Vai trò                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `commands/`     | 40 slash commands: `/discover-system`, `/compare-ui-from-figma-design`, `/generate-automation-web`, `/generate-automation-mobile`, `/generate-automation-api`, `/generate-testcases-api`, `/generate-requirements-from-website`, `/generate-requirements-from-mobile`, `/generate-requirements-from-api`, `/update-requirements-from-ticket`, `/generate-testcases-manual-rbt`, `/update-testcases-from-impact`, `/generate-automation-from-testcases`, `/update-automation-from-impact`, `/run-and-fix-tests`, `/heal-locators`, `/review-automation-code`, `/execute-test-cases`, `/retest-fixed-bugs`, `/analyze-test-report`, `/create-bug-report`, `/review-testcases`, `/generate-traceability-matrix`, `/generate-master-test-plan`, `/generate-test-progress-report`, `/generate-test-summary-report`, `/generate-user-guide`, `/generate-api-mocks`... |
| `rules/`        | 7 quy tắc bắt buộc: automation chung, reporting (Allure), locator strategy, Playwright, Selenium, Appium, so thiết kế Figma                                                                                                                                                                                                                                                                                                                                                                |
| `skills/`       | 22 kỹ năng chuyên biệt: requirements analyzer, **figma design comparator**, automation engineer, manual testing, manual test executor, UI debug (web), **mobile debug (Appium — Native/Flutter/Hybrid)**, locator healer, test data generator, framework architect, jira integration, bug reporter, test report analyzer, **test progress reporter**, **test summary reporter**, **user guide writer** (DOC/LIVE/VIDEO · ảnh + video có highlight · đa ngôn ngữ · HTML nhúng media), testcase reviewer, automation code reviewer, coverage traceability, api mocking...                                                                                                                              |
| `settings.json` | Cấu hình quyền hạn: cho phép/cấm các hành động cụ thể (đọc file, chạy test, push code...). Riêng `settings.local.json` là cấu hình **cục bộ từng máy** — đã gitignore, không commit                                                                                                                                                                                                                                                                 |

> **📌 Lưu ý về cấu trúc:** Trong Claude Code, **workflows** được gọi là **commands** và đặt trong `.claude/commands/`. Tên file dùng dấu gạch dưới (`_`). Ví dụ: `generate-automation-from-testcases.md`.

---

## `plans/` — Quy Trình 6 Bước Chuyên Sâu

Dành cho các tác vụ phức tạp, cần thực hiện **tuần tự trong cùng 1 conversation**.

| Plan                  | Mô tả                                                                                                                 | Bắt đầu nhanh                           |
| --------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------- |
| `plans/manual/`       | Sinh Manual Test Cases theo quy trình **AI-RBT 6 bước** (Risk-Based Testing, 15 field types, OWASP & AI Quality Gate) | Xem `plans/manual/QUICK_START.md`       |
| `plans/automation/`   | Sinh Automation Scripts theo **6 bước** từ context → review                                                           | Xem `plans/automation/QUICK_START.md`   |
| `plans/cross-module/` | Phân tích tính năng **đa module** & sinh **ma trận kết hợp** (Output-Class/Pairwise/Cartesian)                        | Xem `plans/cross-module/QUICK_START.md` |

**Cách dùng:** Mở `QUICK_START.md` → Làm theo từng bước → Gửi prompt mỗi bước vào Claude Code.

### `prompts/` — Prompt Mẫu Dùng Nhanh

Dành cho tác vụ **đơn lẻ**, chỉ cần copy → thay `[...]` bằng dữ liệu thực → paste → gửi.

| #   | Prompt                                          | Mục đích                                                                |
| --- | ----------------------------------------------- | ----------------------------------------------------------------------- |
| 00  | `prompt_00_discover_system.txt`                 | **[Mới]** Khám phá hệ thống chưa có tài liệu — bản đồ module + prefix   |
| 01  | `prompt_01_generate_requirements.txt`           | Phân tích website sinh Requirements                                     |
| 02  | `prompt_02_generate_test_cases.txt`             | **[Mới]** Sinh manual TCs RBT chuẩn 15 field types & Quality Gate       |
| 03  | `prompt_03_create_framework_playwright.txt`     | Dựng framework Playwright TS                                            |
| 03  | `prompt_03_create_framework_selenium.txt`       | Dựng framework Selenium Java                                            |
| 03  | `prompt_03_create_framework_appium.txt`         | Dựng framework Appium Java (Mobile)                                     |
| 04  | `prompt_04_generate_script_playwright.txt`      | Viết test script Playwright TS                                          |
| 04  | `prompt_04_generate_script_selenium.txt`        | Viết test script Selenium Java                                          |
| 05  | `prompt_05_convert_manual_to_automation.txt`    | Chuyển manual TC sang automation                                        |
| 06  | `prompt_06_review_automation_code.txt`          | **[Mới]** Review chất lượng automation code theo Definition of Done     |
| 07  | `prompt_07_generate_test_data.txt`              | Sinh test data có cấu trúc                                              |
| 08  | `prompt_08_analyze_flaky_tests.txt`             | Phân tích test không ổn định                                            |
| 09  | `prompt_09_generate_api_tests.txt`              | **[Mới]** Viết test API 12 status codes & OWASP Security                |
| 10  | `prompt_10_create_bug_report.txt`               | **[Mới]** Sinh bug report chuẩn từ test FAIL, tùy chọn đẩy Jira         |
| 11  | `prompt_11_analyze_test_report.txt`             | **[Mới]** Phân tích test report, gom nhóm failure theo root cause       |
| 12  | `prompt_12_review_testcases.txt`                | **[Mới]** Review chất lượng manual TCs theo rubric 6 tiêu chí · Mode AUTOMATION: TC nào làm automation được |
| 13  | `prompt_13_generate_traceability_matrix.txt`    | **[Mới]** Sinh ma trận truy vết RTM 3 tầng                              |
| 14  | `prompt_14_generate_api_mocks.txt`              | **[Mới]** Sinh API mocks + tests cho edge cases                         |
| 15  | `prompt_15_generate_checklist.txt`              | **[Mới]** Sinh checklist tick tay (smoke / regression / release)        |
| 16  | `prompt_16_execute_test_cases.txt`              | **[Mới]** Thực thi manual TC trên browser thật, xuất execution report   |
| 17  | `prompt_17_run_and_fix_tests.txt`               | **[Mới]** Chạy suite có sẵn, phân loại failure, tự sửa nhóm sửa được    |
| 18  | `prompt_18_heal_locators.txt`                   | **[Mới]** Rà & sửa locator trong Page Object sau khi UI đổi             |
| 19  | `prompt_19_update_automation_from_impact.txt`   | **[Mới]** Cập nhật script đã có theo Impact Report (delta mode)         |
| 20  | `prompt_20_analyze_requirement_document.txt`    | **[Mới]** Phân tích ticket/tài liệu → tài liệu phân tích, KHÔNG sinh TC |
| 21  | `prompt_21_update_requirements_from_ticket.txt` | **[Mới]** Cập nhật requirements từ ticket (delta mode) + Impact Report  |
| 22  | `prompt_22_generate_testcases_quick.txt`        | **[Mới]** Sinh manual TCs QUICK mode — 1 lượt, không qua 6 bước RBT     |
| 23  | `prompt_23_retest_fixed_bugs.txt`               | **[Mới]** Retest bug đã fix + regression quanh vùng fix                 |
| 24  | `prompt_24_generate_test_summary_report.txt`    | **[Mới]** Báo cáo tổng hợp tại mốc release — khuyến nghị go/no-go       |
| 25  | `prompt_25_generate_master_test_plan.txt`       | **[Mới]** Master Test Plan — phạm vi, tiêu chí vào/ra, lịch, rủi ro     |
| 26  | `prompt_26_generate_automation_mobile_flow.txt` | **[Mới]** Sinh automation Appium từ flow chạy thật — Native/Flutter/Hybrid |
| 27  | `prompt_27_update_testcases_from_impact.txt`    | **[Mới]** Cập nhật TC đã có theo Impact Report (delta mode), giữ TC ID  |
| 28  | `prompt_28_generate_user_guide.txt`             | **[Mới]** Hướng dẫn sử dụng cho người dùng cuối — tổ chức theo việc cần làm  |
| 29  | `prompt_29_generate_requirements_from_api.txt`  | **[Mới]** Sinh REQ cho module API từ Swagger/Scalar/Postman — kiểm chứng bằng gọi thật |
| 30  | `prompt_30_generate_requirements_from_mobile.txt` | **[Mới]** Sinh REQ cho module trên app mobile — Native/Flutter/Hybrid, qua Appium MCP |
| 31  | `prompt_31_generate_automation_api.txt`         | **[Mới]** Sinh automation API từ file TC API — fixture 2 tài khoản BOLA, dọn dữ liệu |
| 32  | `prompt_32_generate_test_progress_report.txt`   | **[Mới]** Báo cáo tiến độ một kỳ trong đợt — so với lịch plan, trở ngại, rủi ro mới |

> Danh mục đầy đủ chia theo 7 nhóm tra cứu: [`prompts/README.md`](prompts/README.md)

---

## ✳️ Hướng Dẫn Sử Dụng Trong Claude Code

### Cách 1: Claude Code CLI (Terminal)

1. **Clone Repo này về máy:**
   Hoặc bạn có thể copy trực tiếp thư mục `.claude` từ repo này.

2. **Tích hợp vào dự án của bạn:**
   Copy thư mục `.claude` vào thư mục gốc (root directory) của dự án Automation hoặc Manual Test mà bạn đang làm việc.

3. **Mở terminal và khởi chạy Claude Code:**

   ```bash
   claude
   ```

   Claude Code tự động nhận diện thư mục `.claude` và file `CLAUDE.md` ở thư mục gốc, áp dụng ngay các Rule, Skill, Command của **Anh Tester** đã thiết lập sẵn.

4. **Sử dụng slash commands:**
   Gõ `/` trong Claude Code để xem danh sách commands có sẵn. Ví dụ:
   ```
   /generate-automation-from-testcases
   /generate-testcases-manual-rbt
   /generate-cross-module-test-plan
   ```

### Cách 2: Claude Code trong VS Code

1. **Cài đặt extension Claude Code** từ VS Code Marketplace.

2. **Mở dự án** đã chứa thư mục `.claude` trong VS Code.

3. **Mở Claude Code panel** (Ctrl+Shift+P → "Claude Code: Open").

4. **Bắt đầu trò chuyện** — Claude Code sẽ tự động nhận diện cấu hình `.claude` và `CLAUDE.md`.

### Bước tiếp theo: Kết nối công cụ → [SETUP_CLAUDE.md](SETUP_CLAUDE.md)

Copy `.claude` vào dự án là AI đã có **Rule / Skill / Command**. Nhưng để AI **mở được browser thật**, **đọc Jira**, hay **gửi báo cáo vào Slack**, bạn cần kết nối thêm công cụ bên ngoài.

📖 **Xem hướng dẫn đầy đủ tại [SETUP_CLAUDE.md](SETUP_CLAUDE.md):**

| Nội dung                                                       | Vì sao cần                                                                                                                                                                     |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Cài Playwright MCP thủ công** (Developer → Local MCP Server) | **Bắt buộc** cho `/discover-system`, `/execute-test-cases`, `/generate-requirements-from-website`, `/generate-automation-web` — không có thì AI không mở được browser |
| **Connectors: Atlassian / Slack / GitHub / Claude in Chrome**  | Kéo requirement từ Jira, gửi report vào Slack, đọc log CI từ GitHub Actions                                                                                                    |
| **Cowork Schedule** — tự động chạy task theo lịch              | Ví dụ sẵn: mỗi sáng đọc task từ Slack và ước lượng effort · cuối ngày tổng hợp kết quả GitHub Actions gửi vào kênh Slack                                                       |
| **Checklist nghiệm thu & bảng lỗi thường gặp**                 | Xử lý nhanh `spawn npx ENOENT` trên Windows, connector kẹt OAuth, task chạy sai múi giờ                                                                                        |

> ⚡ **Cài nhanh nhất:** nếu chỉ cần Playwright MCP cho Claude Code CLI, chạy đúng 1 lệnh ở thư mục gốc dự án:
>
> ```bash
> claude mcp add --scope project playwright -- npx -y @playwright/mcp --viewport-size "1600,750" --config ".claude/playwright-mcp-config.json"
> ```
>
> `1600×750` là viewport headed vừa màn hình 1920×1080 — cửa sổ browser **không nở được sau khi launch**, nên đặt ở đây chứ không resize sau. Màn hình khác thì tính lại theo công thức trong [SETUP_CLAUDE.md](SETUP_CLAUDE.md) mục 1.4.

---

## 🤝 Cộng đồng học tập

- Tham gia cộng đồng **Anh Tester** để cùng trao đổi:
  - 📘 **Fanpage Facebook:** [Anh Tester](https://www.facebook.com/anhtester)
  - 👥 **Group Facebook Automation:** [Cộng đồng Automation Testing](https://www.facebook.com/groups/automationtest)
  - 👥 **Group Facebook Manual:** [Cộng đồng Manual Testing](https://www.facebook.com/groups/manualtest)
  - ✈️ **Telegram Automation:** [Cộng đồng Automation Testing](https://t.me/+kSUGJ3pVvxkyZWU1)
  - ✈️ **Telegram Manual:** [Cộng đồng Manual Testing](https://t.me/+8eChRz7OVqliZWRl)

---

## 📄 License

Dự án này CÓ PHÍ, chỉ dành cho HỌC VIÊN chính thức của Anh Tester.

---

Anh Tester Automation Testing 🎯  
https://anhtester.com
