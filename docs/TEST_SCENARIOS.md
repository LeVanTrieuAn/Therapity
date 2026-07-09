# 🗼 Thapsang Mindset OS: Kịch Bản Kiểm Thử Toàn Diện (Comprehensive Test Scenarios)

Tài liệu này cung cấp toàn bộ các kịch bản kiểm thử (Test Scenarios) và trường hợp kiểm thử (Test Cases) chi tiết cho nền tảng **Thapsang (Mindset SaaS)**. Được xây dựng dựa trên kiến trúc Modular "Lighthouse" hiện đại, tài liệu phục vụ cho công tác kiểm thử thủ công (Manual Testing) và tự động hóa (Automation Testing) nhằm đảm bảo hệ thống vận hành trơn tru, bảo mật và đạt trải nghiệm người dùng cao cấp nhất.

---

## 🗺️ TỔNG QUAN HỆ THỐNG & CHIẾN LƯỢC KIỂM THỬ

### 1. Môi trường Kiểm thử (Test Environment)

* **Kiến trúc:** Modular Lighthouse (Frontend HTML phẳng + Alpine.js + TailwindCSS phục vụ tĩnh qua NGINX; Backend FastAPI RESTful engine).
* **Cơ sở dữ liệu:** Hệ cơ sở dữ liệu động JSON (`thapsang_db.json`, `aoa_db.json`, `cohort_db.json`).
* **Trình duyệt khuyến nghị:** Google Chrome, Microsoft Edge, Safari (hỗ trợ hiển thị mượt mà 60fps hiệu ứng Glassmorphism & Vis.js graph).

### 2. Định nghĩa các Cấp độ Đánh giá

* **Pass (Đạt):** Tính năng hoạt động đúng như kịch bản thiết kế, giao diện chuẩn chỉ, không lỗi rò rỉ DOM/HTML.
* **Fail (Không Đạt):** Xảy ra lỗi logic, rò rỉ dữ liệu, lỗi giao diện hoặc hiệu năng giật lag.
* **Block (Bị chặn):** Tính năng không thể kiểm thử do một lỗi khác nghiêm trọng hơn chặn đứng.

---

## 🔑 KỊCH BẢN TEST 1: HỆ THỐNG XÁC THỰC & BẢO MẬT (AUTH & SECURITY)

### TC-01: Đăng nhập với tài khoản hợp lệ

* **Mô tả:** Đảm bảo người dùng có thể đăng nhập thành công vào hệ thống bằng tài khoản mặc định hoặc tài khoản mới đăng ký.
* **Các bước thực hiện:**
  1. Truy cập trang chủ `/` (chuyển hướng sang `/login.html`).
  2. Nhập thông tin đăng nhập: Username: `user`, Password: `user123` (hoặc tài khoản đã đăng ký thành công).
  3. Nhấn nút "Đăng nhập".
* **Dữ liệu kiểm thử:** `user` / `user123`.
* **Kết quả kỳ vọng:** Đăng nhập thành công. Hệ thống lưu cookie `thapsang_session=active` và thông tin user trong `localStorage` (`thapsang_user`). Điều hướng tự động về màn hình AI Coach (`/coach`). Hiển thị Toast thông báo đăng nhập thành công.

### TC-02: Đăng nhập thất bại với thông tin sai lệch

* **Mô tả:** Đảm bảo hệ thống từ chối truy cập khi nhập sai tên tài khoản hoặc mật khẩu.
* **Các bước thực hiện:**
  1. Truy cập trang `/login.html`.
  2. Nhập Username không tồn tại (VD: `wronguser`) hoặc nhập sai Password.
  3. Nhấn "Đăng nhập".
* **Dữ liệu kiểm thử:** `wronguser` / `wrongpwd`.
* **Kết quả kỳ vọng:** Đăng nhập thất bại. Hệ thống hiển thị Toast thông báo lỗi màu đỏ đậm rực rỡ với nội dung: `"Sai thông tin đăng nhập"`. Người dùng vẫn ở lại màn hình đăng nhập. Không có dữ liệu session nào được lưu.

### TC-03: Đăng ký tài khoản mới & Xác thực OTP qua Email

* **Mô tả:** Kiểm tra quy trình đăng ký tài khoản mới sử dụng mã xác thực OTP gửi qua email.
* **Các bước thực hiện:**
  1. Truy cập trang đăng nhập, chuyển sang tab "Đăng ký".
  2. Nhập đầy đủ thông tin: Username, Email thật, Họ tên, Mật khẩu.
  3. Nhấn nút "Gửi mã OTP".
  4. Kiểm tra hòm thư email (hoặc Debug Console của backend nếu chưa cấu hình SMTP) để lấy mã OTP 6 chữ số.
  5. Nhập mã OTP vào ô xác thực và nhấn nút "Đăng ký".
* **Dữ liệu kiểm thử:** Email thật, OTP nhận được.
* **Kết quả kỳ vọng:**
  * Khi nhấn "Gửi mã OTP": Hiển thị Toast thông báo gửi OTP thành công.
  * Khi nhấn "Đăng ký" với OTP đúng: Đăng ký thành công, hệ thống tự động ghi nhận tài khoản mới vào cơ sở dữ liệu `thapsang_db.json` dưới trường `_accounts` và `_profiles`. Tự động đăng nhập và chuyển về trang `/coach`.

### TC-04: Khôi phục mật khẩu bị quên bằng mã OTP

* **Mô tả:** Đảm bảo luồng khôi phục mật khẩu thông qua email xác thực hoạt động đúng đắn.
* **Các bước thực hiện:**
  1. Tại màn hình đăng nhập, click liên kết "Quên mật khẩu?".
  2. Nhập Email đã liên kết với tài khoản.
  3. Nhấn "Gửi mã OTP khôi phục".
  4. Lấy mã OTP từ hòm thư/console và nhập mật khẩu mới. Nhấn "Đặt lại mật khẩu".
* **Kết quả kỳ vọng:** Hệ thống gửi mã OTP khôi phục thành công. Sau khi đặt lại mật khẩu với OTP đúng, hiển thị thông báo thành công và chuyển hướng về màn hình đăng nhập để đăng nhập với mật khẩu mới.

### TC-05: Chặn truy cập trực tiếp khi chưa xác thực (Session Control)

* **Mô tả:** Ngăn chặn người dùng chưa đăng nhập cố tình truy cập trực tiếp các đường dẫn bảo mật qua thanh địa chỉ.
* **Các bước thực hiện:**
  1. Mở một cửa sổ ẩn danh trình duyệt mới.
  2. Nhập trực tiếp URL: `http://localhost/diary` hoặc `http://localhost/cohort`.
* **Kết quả kỳ vọng:** Hệ thống phát hiện không có cookie `thapsang_session` hoặc thông tin tài khoản trong `localStorage`, chặn quyền truy cập và tự động điều hướng ngay lập tức về trang `/` (login.html).

---

## 🗺️ KỊCH BẢN TEST 2: THAPSANG VAULT & GƯƠNG PHẢN TỈNH (OBSOCRATIC PKM & SOČRATIC DIARY)

### TC-06: Quản lý Thư mục trong Vault Explorer (Directory Tree)

* **Mô tả:** Kiểm tra các thao tác đóng/mở thư mục, tạo mới, sửa tên và xóa thư mục trong PKM Vault.
* **Các bước thực hiện:**
  1. Truy cập trang Nhật ký (`/diary`).
  2. Nhấp vào nút "Thêm Thư mục mới" (icon folder +). Nhập tên thư mục (VD: `Tư duy Hệ thống`) và lưu lại.
  3. Nhấp đúp vào tên thư mục để mở/đóng.
  4. Nhấn biểu tượng thùng rác bên cạnh thư mục để xóa.
* **Kết quả kỳ vọng:** Thư mục được tạo mới và hiển thị ngay trên cấu trúc cây bên trái. Thao tác đóng/mở diễn ra mượt mà. Xóa thư mục hoạt động chuẩn xác và cập nhật ngay lập tức vào database.

### TC-07: Soạn thảo văn bản với Trình soạn thảo Markdown chuyên sâu

* **Mô tả:** Đảm bảo trình soạn thảo render đúng và đủ các cú pháp Markdown trong chế độ Preview.
* **Các bước thực hiện:**
  1. Chọn một ghi chép hoặc nhấn "Thêm ghi chép mới" (icon note +).
  2. Soạn thảo nội dung chứa các cú pháp:
     * Tiêu đề: `# H1`, `## H2`, `### H3`
     * Định dạng chữ: `__Chữ in đậm__`, `_Chữ in nghiêng_`, `___Chữ in đậm và nghiêng___`
     * Danh sách: `- Gạch đầu dòng`, `1. Thứ tự`
     * Checklist tương tác: `- [ ] Việc cần unlearn`, `- [x] Việc đã relearn`
  3. Quan sát khung hiển thị Preview bên phải.
* **Kết quả kỳ vọng:** Khung Preview hiển thị chuẩn xác font chữ Inter/Montserrat cao cấp. Các thẻ tiêu đề, chữ đậm/nghiêng hiển thị sắc nét. Trạng thái checklist được đồng bộ thời gian thực.

### TC-08: Tương tác trực tiếp trên Checklist ở chế độ Preview

* **Mô tả:** Đảm bảo người dùng có thể nhấp chuột trực tiếp để check/uncheck các ô vuông công việc trong khung Preview và tự động lưu lại.
* **Các bước thực hiện:**
  1. Tại khung Preview của ghi chép đang hiển thị checklist, click vào một ô vuông chưa check `- [ ]`.
  2. Quan sát sự thay đổi trong trình soạn thảo Code Editor bên trái và nhấn lưu.
* **Kết quả kỳ vọng:** Ô vuông lập tức chuyển thành dấu tích xanh `- [x]`. Nội dung văn bản thô bên khung soạn thảo code tự động thay đổi từ `- [ ]` thành `- [x]` tương ứng. Dữ liệu được lưu trữ chuẩn xác khi nhấn nút Lưu.

### TC-09: Hệ thống Socratic WikiLinks (`[[Note Title]]` & `[(Note Title)]`) & Tự động tạo ghi chép

* **Mô tả:** Kiểm tra khả năng tự động nhận diện liên kết trang và cơ chế Auto-Creation ghi chép mới khi click.
* **Các bước thực hiện:**
  1. Trong ghi chép hiện tại, soạn thảo dòng chữ: `Hãy đọc thêm về [[Tư duy Socratic]] và liên kết [(Nhật ký Unlearn)]`.
  2. Quan sát khung Preview.
  3. Nhấp chuột vào hyperlink `Tư duy Socratic` vừa xuất hiện trong khung Preview (trang này chưa tồn tại trong hệ thống).
* **Kết quả kỳ vọng:**
  * Khung Preview nhận diện đúng cú pháp và render thành các liên kết màu vàng hoàng kim nổi bật.
  * Khi click vào link chưa tồn tại: Hệ thống tự động tạo mới một trang ghi chép trong Vault có tiêu đề `# Tư duy Socratic`, lưu vào cơ sở dữ liệu, đồng thời tự động cập nhật thêm một node mới tương ứng vào sơ đồ tư duy (Graph View) mà không cần reload trang.

### TC-10: Thanh kéo giãn ngang Gương Phản Tỉnh (Sideways Resizer)

* **Mô tả:** Đảm bảo thanh phân chia độ rộng hoạt động cực kỳ mượt mà, đạt hiệu suất 60fps và tự động cập nhật bản đồ tư duy khi thả chuột.
* **Các bước thực hiện:**
  1. Tại màn hình `/diary`, rê chuột vào biên trái của Gương phản tỉnh (nơi có thanh resizer mỏng biên độ 8px).
  2. Nhấn giữ chuột trái và kéo sang trái hoặc phải để điều chỉnh độ rộng của vùng viết nhật ký.
  3. Thả chuột trái ra.
* **Kết quả kỳ vọng:**
  * CSS transition tạm thời bị tắt hoàn toàn khi kéo để loại bỏ độ trễ (độ mượt đạt 60fps, không giật lag).
  * Khống chế giới hạn kéo tối đa 60% màn hình để tránh vỡ bố cục.
  * Khi thả chuột: Mạng lưới vis.js graph tự động tính toán lại kích thước và phân bổ lại tọa độ các node vô cùng mượt mà.

### TC-11: Bản Đồ Gương Phản Tỉnh (Obsidian-Style Graph View) bằng Vis.js

* **Mô tả:** Kiểm tra độ chính xác, tương tác và hiển thị của mạng lưới liên kết tri thức.
* **Các bước thực hiện:**
  1. Quan sát góc bản đồ tư duy Obsidian trong màn hình Nhật ký.
  2. Kiểm tra sự tồn tại của node trung tâm nhân tạo `'root'`.
  3. Rê chuột vào một node ghi chép, kéo thả node để thử độ phản hồi vật lý (Force-Directed).
  4. Click chọn một node bất kỳ trên bản đồ.
* **Kết quả kỳ vọng:**
  * **Authentic Layout:** Không tồn tại node trung tâm nhân tạo `'root'`, các node tự do trôi nổi và kết nối tự nhiên theo các cụm tri thức (knowledge clusters).
  * Node đang được chọn (Active) sẽ phóng to, có màu trắng sáng rực rỡ và viền vàng óng nổi bật. Các node bình thường có màu xám xanh dịu mát.
  * Hệ thống tự động mở ra nội dung ghi chép tương ứng với node vừa click trên bản đồ tư duy.

### TC-12: Chế độ Focus Mode (Không gian viết lách tập trung)

* **Mô tả:** Kiểm tra tính năng ẩn toàn bộ giao diện gây nhiễu để tập trung viết lách.
* **Các bước thực hiện:**
  1. Nhấn nút "Focus Mode" (icon phóng to / full màn hình) cạnh tiêu đề nhật ký.
  2. Quan sát giao diện. Nhấn phím `ESC` hoặc click nút thoát Focus để trở lại.
* **Kết quả kỳ vọng:** Toàn bộ thanh Sidebar bên trái, thanh tiêu đề và trình quản lý cây thư mục bên trái biến mất với hiệu ứng slide-fade nhẹ nhàng. Không gian viết nhật ký mở rộng ra toàn màn hình nền kính mờ (glassmorphism) bán trong suốt sang trọng. Trở lại trạng thái bình thường chuẩn xác khi thoát.

### TC-13: Bảng tra cứu phím tắt Markdown Cheat Sheet

* **Mô tả:** Đảm bảo bảng cheat sheet trượt mượt mà khi click biểu tượng bóng đèn.
* **Các bước thực hiện:**
  1. Click vào biểu tượng bóng đèn phát sáng bên cạnh tiêu đề Vault.
  2. Kiểm tra nội dung bảng hướng dẫn hiển thị và nút đóng `x`.
* **Kết quả kỳ vọng:** Ngăn kéo hướng dẫn cú pháp Markdown trượt ra mượt mà từ bên phải. Hiển thị rõ ràng các hướng dẫn định dạng chữ, list, checklist và WikiLinks. Click nút đóng `x` thu gọn ngăn kéo chuẩn chỉ.

---

## 🧠 KỊCH BẢN TEST 3: SOCRATIC MIRROR COACH (AI COACH)

### TC-14: Trò chuyện và Phản chiếu Nhận thức bằng phương pháp Socratic

* **Mô tả:** Kiểm tra tính năng chat với AI huấn luyện viên phản chiếu, không đưa ra lời khuyên mà đặt câu hỏi sâu sắc.
* **Các bước thực hiện:**
  1. Truy cập trang AI Coach (`/coach`).
  2. Chọn một mô hình AI bất kỳ (VD: `qwen3.5`).
  3. Nhập câu hỏi/nỗi lòng của bạn: `"Tôi luôn cảm thấy trì hoãn công việc mặc dù hạn chót đã cận kề."` và nhấn Gửi.
* **Kết quả kỳ vọng:** AI Coach trả về câu trả lời bằng tiếng Việt cực kỳ ấm áp và trí tuệ. AI tuân thủ triết lý **Socratic Mirror Coach**: Không đưa lời khuyên sáo rỗng hay trực tiếp, thay vào đó đặt ra 1-2 câu hỏi sâu sắc phản chiếu tư duy giúp người dùng tự soi xét bản thân.

### TC-15: AI tự động phân tích & đề xuất bài tập hành động (Dynamic Tasks Generation)

* **Mô tả:** Kiểm tra khả năng trích xuất nhiệm vụ tự động của AI Coach sau cuộc hội thoại.
* **Các bước thực hiện:**
  1. Thực hiện một cuộc trò chuyện ngắn với AI Coach về việc cải thiện khả năng tập trung sâu.
  2. Nhấp vào nút "AI trích xuất Task hành động" hoặc quan sát chỉ báo nhiệm vụ.
* **Kết quả kỳ vọng:** AI tự động phân tích ngữ cảnh cuộc trò chuyện và đề xuất danh sách các bài tập hành động (VD: *Thử nghiệm 25 phút Deep Work không điện thoại*). Đồng thời, biểu tượng "Tasks" trên thanh Sidebar xuất hiện **Chấm Đỏ Nhấp Nháy (Red Dot Indicator)** phát sáng báo hiệu có bài tập mới chưa đọc được giao.

---

## 🌐 KỊCH BẢN TEST 4: MẠNG XÃ HỘI AOA (ASK OTHERS ANYTHING FEED)

### TC-16: Xuất bản Bản đồ tư duy cá nhân lên Newsfeed cộng đồng

* **Mô tả:** Đảm bảo người dùng có thể chia sẻ ghi chép kèm Mindmap cá nhân lên bảng tin chung chỉ với 1 click.
* **Các bước thực hiện:**
  1. Tại màn hình viết nhật ký (`/diary`), chọn một ghi chép có sơ đồ tư duy đẹp mắt.
  2. Nhấn nút "Chia sẻ lên AOA Feed".
  3. Truy cập trang `/aoa`.
* **Kết quả kỳ vọng:** Bài viết lập tức xuất hiện trên đầu bảng tin Newsfeed của AOA dưới dạng bài đăng hiện đại (Style Twitter/X) hiển thị đầy đủ: Ảnh đại diện, tên người dùng, nội dung ghi chép và sơ đồ tư duy Vis.js mini đính kèm.

### TC-17: Tương tác trên Bản đồ tư duy nhúng (Embedded Mindmaps)

* **Mô tả:** Kiểm tra tính tương tác của khung Vis.js mini trong từng bài đăng trên Newsfeed.
* **Các bước thực hiện:**
  1. Lướt bảng tin AOA, tìm một bài viết có đính kèm Mindmap.
  2. Dùng chuột để rê kéo các node, zoom in/out bằng con lăn chuột ngay trong khung bài viết đó.
* **Kết quả kỳ vọng:** Khung Vis.js mini phản hồi nhạy bén, cho phép thu phóng, kéo trượt các node tư duy của người khác mượt mà mà không ảnh hưởng đến chuyển động cuộn trang tự nhiên của trình duyệt.

### TC-18: Tương tác Like, Comment và Theo dõi (Follow System)

* **Mô tả:** Kiểm tra các tương tác mạng xã hội bền vững và đồng bộ danh sách Following.
* **Các bước thực hiện:**
  1. Nhấn nút Like (icon tim) trên bài viết của thành viên khác.
  2. Viết một bình luận thông thái vào ô phản hồi của bài viết đó và nhấn Gửi.
  3. Click vào nút "Theo dõi" (Follow) bên cạnh tên tác giả bài đăng.
  4. F5 reload lại trang để kiểm tra sự bền vững của dữ liệu.
* **Kết quả kỳ vọng:**
  * Lượt thích tăng lên tương ứng và lưu giữ trạng thái khi reload.
  * Bình luận mới hiển thị ngay lập tức dưới bài đăng với đầy đủ avatar và tên.
  * Nút "Theo dõi" chuyển thành "Đang theo dõi". Danh sách theo dõi (`following_list`) trong Local Storage và `thapsang_db.json` được cập nhật đồng thời.

---

## 📋 KỊCH BẢN TEST 5: QUẢN LÝ NHIỆM VỤ (TODOIST-STYLE TASK MANAGER)

### TC-19: Kéo Cohort Task hoặc chấp nhận AI Task vào danh sách cá nhân

* **Mô tả:** Đảm bảo luồng chuyển giao nhiệm vụ từ Cohort/AI sang Todoist cá nhân hoạt động chuẩn xác.
* **Các bước thực hiện:**
  1. Tại trang Cohort (`/cohort`), tab **PLAN**, tìm một bài tập trong Syllabus tuần hiện tại.
  2. Nhấn nút "+ Thêm vào Task" bên cạnh bài tập.
  3. Chuyển sang trang Nhiệm vụ (`/tasks`).
* **Kết quả kỳ vọng:** Bài tập từ Cohort lập tức được thêm vào cột "Chưa hoàn thành" trong danh sách Task cá nhân với đầy đủ nguồn ngữ cảnh liên kết. Nếu thêm lại task đã tồn tại, hiển thị Toast cảnh báo và nút hành động chuyển nhanh sang tab DO.

### TC-20: Quản lý chi tiết Nhiệm vụ (Subtasks, Effort, Deadline)

* **Mô tả:** Kiểm tra độ chi tiết và khả năng phân loại, hoàn thành nhiệm vụ cá nhân.
* **Các bước thực hiện:**
  1. Click vào một nhiệm vụ để mở bảng chi tiết.
  2. Thực hiện thêm các Subtasks (nhiệm vụ con) chi tiết.
  3. Cài đặt mức độ nỗ lực (Effort) từ 1 đến 5 và Deadline cụ thể.
  4. Nhấn chọn hoàn thành các Subtask và Task chính.
* **Kết quả kỳ vọng:** Giao diện thẻ nhiệm vụ cập nhật trực quan tiến độ hoàn thành các subtask con (VD: *2/4 hoàn thành*). Khi check hoàn thành task chính, thẻ nhiệm vụ lập tức di chuyển mượt mà sang khu vực "Đã hoàn thành" với hiệu ứng gạch ngang chữ tinh tế. Dữ liệu đồng bộ trực tiếp vào Local Storage `thapsang_pdca_tasks`.

---

## 🔥 KỊCH BẢN TEST 6: CHƯƠNG TRÌNH HỌC TẬP COHORT-BASED PATH

### TC-21: Bản đồ nhiệt Tiến độ Cohort (Cohort Progress Heatmap)

* **Mô tả:** Kiểm tra khả năng đồng bộ dữ liệu tiến độ và hiển thị màu sắc theo chuẩn thiết kế.
* **Các bước thực hiện:**
  1. Truy cập trang Cohort (`/cohort`), nhấn tab **DO**.
  2. Quan sát bảng lưới Heatmap tiến độ của lớp. Rê chuột vào ô đại diện của chính mình và của thành viên khác.
* **Kết quả kỳ vọng:**
  * Bảng Heatmap hiển thị đầy đủ các ô tương ứng với số lượng thành viên trong cơ sở dữ liệu `cohort_db.json`.
  * Ô đại diện cho chính người dùng hiển thị màu vàng hoàng kim rực rỡ kèm hiệu ứng phát sáng chuyển động (`pulse-gold`).
  * Các ô của thành viên khác hiển thị dải màu xanh lục bảo tương thích với tiến độ tuần học của họ (VD: 80% hoàn thành là màu lục bảo đậm rực rỡ, 0% là màu xám tối).
  * Rê chuột hiển thị tooltip chính xác thông tin: Tên hiển thị và phần trăm tiến độ của thành viên đó.

### TC-22: Ghép cặp Bạn đồng hành & Đánh giá chéo Peer Review (5-Star Slide-out Panel)

* **Mô tả:** Kiểm tra quy trình ghép cặp bạn đồng hành (Accountability Buddy) và thực hiện đánh giá chéo 5 sao chuẩn xác.
* **Các bước thực hiện:**
  1. Tại tab **DO** của trang Cohort, kiểm tra khu vực "Accountability Buddy" để xác định bạn đồng hành tuần này (đã được ghép cặp trong `cohort_db.json`).
  2. Nhấp nút "Review chéo Task".
  3. Tại bảng trượt bên phải (Right-side slide-out modal) vừa mở ra, thực hiện đánh giá cho từng nhiệm vụ của Buddy:
     * Nhấp chọn số sao tương tác từ 1 đến 5 sao (Quan sát nhãn tương ứng: *Chưa đạt, Cần cải thiện, Đạt yêu cầu, Tốt, Xuất sắc*).
     * Nhập nhận xét ngắn vào ô bình luận của từng task.
  4. Nhấn nút "Gửi Review cho Buddy".
* **Kết quả kỳ vọng:**
  * Panel trượt mở ra mượt mà từ rìa phải màn hình với hiệu ứng transition cao cấp.
  * Việc nhấp chọn sao hiển thị hiệu ứng tô vàng sao cực nhạy (`font-variation-settings: 'FILL' 1`). Nhãn hiển thị đúng theo số sao đã chọn.
  * Sau khi nhấn gửi: Hiển thị Toast thông báo gửi đánh giá thành công rực rỡ. Nút "Review chéo" đổi trạng thái thành "Cập nhật Review". Trực tiếp đẩy một sự kiện mới có viền vàng óng đặc biệt lên dòng thời gian Live Resonance (VD: *"Bạn đã review task tuần này cho [Tên Buddy]"*). Lịch sử review lưu trữ bền vững trong Local Storage `cohort_reviews`.

### TC-23: Phân tích Rào cản nhận thức & Tham gia AI Retrospective

* **Mô tả:** Đảm bảo hệ thống AI tổng hợp rào cản cả lớp và phản hồi câu hỏi Socratic cuối tuần.
* **Các bước thực hiện:**
  1. Truy cập tab **CHECK** của trang Cohort.
  2. Kiểm tra thanh đo tỉ lệ phần trăm các điểm nghẽn nhận thức chung của lớp (VD: *Rào cản Sợ hãi thất bại 42%*).
  3. Nhấn nút "Tham gia Retrospective với AI Coach" (hoặc tải lại nếu đã tải).
* **Kết quả kỳ vọng:** Hệ thống hiển thị hiệu ứng loading xoay tròn tinh tế của AI Coach đang phân tích. Sau đó hiển thị đoạn nhận xét phản tư bằng tiếng Việt sâu sắc định hướng Socratic để cả lớp cùng nhìn nhận vấn đề.

### TC-24: Cơ chế tự động thích ứng lộ trình (Dynamic Pivot)

* **Mô tả:** Đảm bảo hệ thống phát hiện rào cản chung để đề xuất điều chỉnh lộ trình học tập.
* **Các bước thực hiện:**
  1. Truy cập tab **ACT** của trang Cohort.
  2. Kiểm tra phần gợi ý điều chỉnh lộ trình ở ô "Dynamic Pivot".
  3. Nhấp nút "Chấp nhận" để tích hợp nhiệm vụ phụ trợ được gợi ý.
* **Kết quả kỳ vọng:** Hệ thống nhận diện đúng tỷ lệ thành viên trễ tiến độ để tự động đề xuất một Task phụ trợ thích ứng (VD: thêm bài nghe Podcast giảm căng thẳng). Khi click "Chấp nhận", task này tự động được đẩy vào danh sách Tasks cá nhân của người dùng.

### TC-25: Sự Tiến Hóa Tư Duy (Mind Map Evolution) bằng SVG động

* **Mô tả:** Đảm bảo trực quan hóa chuyển dịch tư duy bằng SVG động chạy mượt mà.
* **Các bước thực hiện:**
  1. Tại tab **CHECK** của trang Cohort, quan sát ô "Sự tiến hóa Tư duy" bên phải.
  2. Rê chuột vào hộp Unlearn (nút đỏ nét đứt) và hộp Relearn (nút xanh lục glow).
* **Kết quả kỳ vọng:** Hiển thị rõ nét sự tiến hóa tư duy từ Unlearn (Trì hoãn) sang Relearn (Deep Work) qua đường dẫn cong SVG chuyển màu nghệ thuật. Chấm sáng dash chạy liên tục mượt mà dọc theo đường dẫn biểu thị luồng chuyển dịch nhận thức sống động.

---

## 📊 KỊCH BẢN TEST 7: AI ANALYTICS & RADAR CHART ENGINE

### TC-26: Phân tích Radar Nhận Thức 6 Chiều bằng SVG thuần

* **Mô tả:** Kiểm tra độ chính xác của biểu đồ phân tích 6 chỉ số nhận thức vẽ trực tiếp bằng SVG.
* **Các bước thực hiện:**
  1. Truy cập trang Phân Tích (`/analytics`).
  2. Quan sát biểu đồ mạng nhện SVG 6 góc.
  3. Đối chiếu với dữ liệu 6 chiều từ API trả về để đảm bảo các điểm chấm đỉnh khớp chính xác với tỷ lệ.
* **Kết quả kỳ vọng:** Biểu đồ Radar SVG hiển thị sắc nét trên mọi mật độ điểm ảnh màn hình, các đa giác biểu diễn năng lực nhận thức vẽ chuẩn xác, cân đối. Các nhãn văn bản của 6 chiều (*Dữ liệu, Tổng quan, Cảm xúc, Sáng tạo, Cẩn trọng, Lạc quan*) định vị đúng các đỉnh.

### TC-27: AI MBTI Profiler & Phân tích Thế mạnh nhận thức

* **Mô tả:** Kiểm tra tính năng dự đoán MBTI thông minh của AI dựa trên dữ liệu nhật ký & hội thoại.
* **Các bước thực hiện:**
  1. Tại trang Phân Tích, tìm khu vực "Dự đoán Kiểu Tính Cách MBTI".
  2. Kiểm tra hiển thị top 3 MBTI đề xuất kèm phần trăm khớp và phân tích lý luận chi tiết của AI Coach.
  3. Kiểm tra các từ khóa thế mạnh tư duy nổi bật.
* **Kết quả kỳ vọng:** Hệ thống hiển thị 3 thẻ MBTI cao cấp được định dạng tinh tế. Mỗi thẻ ghi rõ mã MBTI (VD: *INTJ*), tỷ lệ phần trăm tương thích, và lý giải logic thuyết phục từ AI Coach dựa trên hành vi viết nhật ký và nhắn tin thực tế của người dùng. Trích xuất đúng 5-8 từ khóa thế mạnh sắc nét.

### TC-28: Gửi đánh giá nhận thức thành công & Toast Auto-Close

* **Mô tả:** Đảm bảo sửa lỗi rò rỉ HTML tag và tự động đóng Toast gửi đánh giá để chuyển cảnh mượt mà.
* **Các bước thực hiện:**
  1. Tại trang Phân Tích, nhấp vào nút gửi phản hồi/đánh giá nhận thức lên hệ thống.
  2. Quan sát Toast thành công hiển thị trên màn hình.
  3. Đợi trong 2 giây mà không cần tương tác chuột.
* **Kết quả kỳ vọng:**
  * Toast thông báo thành công hiển thị rực rỡ, không có bất kỳ thẻ HTML thô nào bị rò rỉ ra giao diện (đã fix triệt để lỗi tag leakage).
  * Đúng 2 giây sau khi hiển thị, Toast tự động đóng lại nhẹ nhàng (`closeSubmission`) và đưa người dùng trở lại giao diện phân tích nhận thức trực quan mà không cần click tắt thủ công.

---

## 🎨 KỊCH BẢN TEST 8: GIAO DIỆN & TRẢI NGHIỆM PHI CHỨC NĂNG (NON-FUNCTIONAL UI/UX)

### TC-29: Responsive & Hiển thị trên Thiết bị Di động (Mobile Layout)

* **Mô tả:** Kiểm tra tính co giãn linh hoạt và trải nghiệm trên các màn hình có chiều rộng hẹp.
* **Các bước thực hiện:**
  1. Sử dụng tính năng DevTools (F12) của trình duyệt, chọn chế độ giả lập điện thoại di động (VD: iPhone 12/13/14 Pro, Samsung Galaxy S22).
  2. Duyệt qua tất cả các trang: Login, Coach, Diary, AOA, Tasks, Analytics, Cohort.
* **Kết quả kỳ vọng:**
  * Toàn bộ nội dung co giãn thích ứng tuyệt vời, không xảy ra hiện tượng tràn lề ngang (x-overflow) gây vỡ trang.
  * Sidebar bên trái tự động chuyển đổi thành menu Hamburger hoặc thanh điều hướng rút gọn tiện dụng dưới chân trang (hoặc ẩn mượt mà tùy kích thước).
  * Trải nghiệm kéo vuốt tự nhiên, font chữ tự động điều chỉnh tỷ lệ hiển thị dễ đọc.

### TC-30: Kiểm tra hiệu ứng chuyển động trang (Entrance Slide-Fade)

* **Mô tả:** Đảm bảo tất cả các trang thuộc kiến trúc modular đều sở hữu hiệu ứng trượt nhẹ từ dưới lên đồng nhất khi truy cập.
* **Các bước thực hiện:**
  1. Nhấp liên tiếp vào các mục trên Sidebar để di chuyển giữa: `Coach`, `Diary`, `AOA Feed`, `Tasks`, `Analytics`, `Cohort`.
  2. Quan sát hiệu ứng xuất hiện của nội dung chính ở tâm màn hình.
* **Kết quả kỳ vọng:**
  * Mỗi khi một trang mới tải xong, nội dung chính được phủ hiệu ứng `.animate-page-fade` trượt mượt mà từ dưới lên khoảng 12px đồng thời mờ dần ra vô cùng nghệ thuật và nhất quán.
  * Không có hiện tượng giật cục, chớp nhoáng trắng màn hình gây khó chịu thị giác.

---

## 📋 MẪU PHIẾU BÁO CÁO LỖI (BUG REPORT TEMPLATE FOR QA/QC)

Khi phát hiện tính năng không đạt yêu cầu (Fail) trong quá trình thực hiện kịch bản test trên, QA/QC điền thông tin báo cáo lỗi theo cấu trúc chuẩn sau để gửi đội ngũ phát triển:

```markdown
### 🗼 [THAPSANG BUG REPORT] - [Tên Tiêu Đề Ngắn Gọn Của Lỗi]

* **Mã Kịch Bản Liên Quan:** [VD: TC-22 (Đánh giá chéo Accountability Buddy)]
* **Mức Độ Nghiêm Trọng:** [Blocker / Critical / Major / Minor / Tweak]
* **Môi Trường Kiểm Thử:** [VD: Chrome 124.0 / Windows 11 / localhost:80]
* **Tài Khoản Đăng Nhập:** [VD: user / user123]

#### 📝 Các Bước Tái Hiện Lỗi (Steps to Reproduce)
1. Truy cập trang ...
2. Nhấp chọn ...
3. Nhập dữ liệu ...
4. Nhấn nút ...

#### 📉 Kết Quả Thực Tế (Actual Result)
* Mô tả chi tiết lỗi xảy ra (VD: Panel trượt bị treo không mở ra, console báo lỗi biến undefined).

#### 📈 Kết Quả Kỳ Vọng (Expected Result)
* Mô tả tính năng hoạt động đúng theo kịch bản (VD: Panel trượt mở ra mượt mà từ rìa phải màn hình và hiển thị danh sách task đánh giá).

#### 🖼️ Hình Ảnh / Video Minh Họa (Screenshots / Media)
* [Đính kèm link hình ảnh hoặc video quay màn hình lỗi tại đây]
```

---

*Tài liệu Kịch Bản Kiểm Thử Thapsang OS được biên soạn hoàn tất và đóng dấu lưu trữ tại thư mục dự án `docs/TEST_SCENARIOS.md`.*
