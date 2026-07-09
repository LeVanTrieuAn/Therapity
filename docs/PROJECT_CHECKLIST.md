# 🗼 Thapsang: Hệ Điều Hành Tư Duy - Project Checklist

Danh sách tổng hợp toàn bộ các tính năng, kỹ thuật và tiến độ đã hoàn thành trong quá trình xây dựng dự án **Thapsang (Mindset SaaS)**. Bản cập nhật này phản ánh đầy đủ kiến trúc Modular "Lighthouse" hiện đại thay thế hoàn toàn nền tảng Streamlit cũ cùng với toàn bộ các cơ chế tương tác thông minh mới nhất.

---

## 1. 🔑 Hệ Thống Xác Thực & Bảo Mật (Authentication System)

- [x] **Giao diện Đăng nhập hiện đại:** Giao diện tối giản sang trọng với hình nền ngọn hải đăng được dịch chuyển tiêu cự hoàn hảo (`translateX(-0.7cm) scale(1.15)`) cho độ cân đối thị giác cao trên mọi màn hình.
- [x] **Dọn sạch tài khoản mặc định:** Loại bỏ hoàn toàn dòng chữ demo tài khoản trải nghiệm (`user/user123`) ở chân trang để chuyển sang chế độ sản xuất bảo mật.
- [x] **Giao diện Đăng ký & Xác thực OTP:** Tích hợp tab Đăng ký tài khoản mới gửi OTP xác nhận qua email để đảm bảo tính thực tế (Hỗ trợ cấu hình SMTP thật hoặc in ra console/terminal dạng Debug tiện lợi).
- [x] **Khôi phục Mật khẩu:** Luồng gửi mã OTP khôi phục mật khẩu trực tiếp qua email người dùng và tạo mật khẩu mới an toàn.
- [x] **Quản lý phiên (Session Control):** Chặn truy cập trực tiếp bằng cookie session (`thapsang_session=active`) và `localStorage`, tự động điều hướng về màn hình Đăng nhập nếu chưa xác thực.
- [x] **Đồng bộ hóa User Profile:** Lưu trữ thông tin định danh Base64 Avatar, Banner, Tên hiển thị, Bio và Danh sách theo dõi (`following_list`) ngay trong Local Storage và cơ sở dữ liệu `thapsang_db.json`.

---

## 2. 🧠 Kiến Trúc Lõi AI & Backend (FastAPI RESTful Engine)

- [x] **Đa dạng hóa Mô hình AI:** API chuyển đổi linh hoạt các model tiên tiến như `gemma-4`, `qwopus3.5`, `qwen3.5`, `qwen3.6` cấu hình thông qua biến môi trường `.env`.
- [x] **Triết lý Socratic Mirror Coach:** Xây dựng `SYSTEM_PROMPT` chuyên sâu định hình AI thành huấn luyện viên phản chiếu (Mirroring), không đưa lời khuyên trực tiếp mà đặt câu hỏi sắc bén để kích thích tư duy độc lập.
- [x] **Phản hồi Định dạng JSON Nghiêm ngặt:** Ép buộc AI phản hồi theo schema JSON chuẩn để frontend bóc tách các node, edge cấu thành sơ đồ tư duy thời gian thực.
- [x] **Cumulative Memory & Database:** Cơ sở dữ liệu JSON động (`aoa_db.json`, `thapsang_db.json`, `cohort_db.json`) lưu trữ lịch sử phản tư, tương tác xã hội và phân tích nhận thức bậc cao của từng tài khoản.

---

## 3. 🗺️ Thapsang Vault & Gương Phản Tỉnh (Obsocratic PKM & Socratic Diary)

- [x] **Thapsang Vault (Obsidian-Style):** Trình quản lý tài liệu cá nhân chuyên nghiệp với cấu trúc cây thư mục (Folder Tree Explorer) hỗ trợ đóng/mở thư mục, tạo mới, chỉnh sửa và xóa thư mục/ghi chép linh hoạt.
- [x] **Bộ soạn thảo Markdown Đa Năng:** Hỗ trợ render trực tiếp các cú pháp Markdown tiêu chuẩn:
  * Tiêu đề các cấp từ `# H1` đến `###### H6`
  * Chữ in đậm `__chữ__`, in nghiêng `_chữ_`, in vừa đậm vừa nghiêng `___chữ___`
  * Danh sách không thứ tự `- list`, danh sách có thứ tự `số. list`
  * Checklist chưa làm `- [ ]`, checklist đã làm `- [x]` với khả năng tương tác trực tiếp trên giao diện Preview.
- [x] **Hệ thống Socratic WikiLinks (`[[Note Title]]` & `[(Note Title)]`):**
  * Tự động nhận diện cú pháp liên kết trang để tạo hyperlink nội bộ.
  * **Auto-Creation:** Khi viết liên kết tới trang chưa tồn tại (ví dụ: `[[Ghi chép mới]]`), người dùng chỉ cần nhấn vào liên kết đó để hệ thống tự động tạo mới trang với preset tiêu đề `# Ghi chép mới`, đồng thời cập nhật ngay lập tức sơ đồ tư duy!
- [x] **Thanh Kéo Giãn Ngang Gương Phản Tỉnh (Sideways Resizer):**
  * Thiết kế thanh kéo absolute biên độ 8px centered (`-left-1`) siêu nhạy trên biên trái của Gương phản tỉnh.
  * Tự động tắt CSS transition khi kéo để đảm bảo không giật lag (độ mượt 60fps), khống chế độ rộng tối đa 60% màn hình, tự động co giãn và phân bổ lại tọa độ vis.js graph mượt mà khi thả chuột.
- [x] **Bản Đồ Gương Phản Tỉnh (Obsidian Graph View):**
  * Sơ đồ tư duy dạng Force-Directed bằng Vis.js cực kỳ trực quan, mô tả mối quan hệ giữa các notes và thư mục.
  * **Authentic Obsidian Layout:** Loại bỏ hoàn toàn node trung tâm `'root'` nhân tạo để các node notes và folders tự do kết nối và trôi nổi tự nhiên, tạo cụm tri thức (knowledge clusters) thực tế.
  * Phân biệt rõ rệt Node đang Active (màu trắng sáng, viền vàng rực, cỡ lớn) và Node thường (màu xám xanh, cỡ nhỏ).
- [x] **Chế độ Focus Mode:** Làm biến mất toàn bộ thanh bên trái và trình quản lý để bạn chìm đắm trong không gian viết lách bán trong suốt (glassmorphism) với các hiệu ứng slide-fade nhẹ nhàng.
- [x] **Bảng Hướng Dẫn Markdown Tích Hợp (Cheat Sheet Lightbulb):**
  * Biểu tượng bóng đèn phát sáng cạnh tiêu đề Vault mở ra ngăn kéo trượt chứa toàn bộ hướng dẫn cú pháp định dạng chữ, list, checklist và WikiLinks.
  * Nút đóng `x` được thiết kế tương tác mượt mà và trực quan.

---

## 4. 🎨 Kiến Trúc Modular "Lighthouse" (Modern HTML/CSS UI/UX)

- [x] **Loại bỏ 100% Streamlit:** Chuyển đổi toàn bộ dự án sang cấu trúc HTML phẳng chạy NGINX phục vụ tĩnh và FastAPI làm API backend.
- [x] **Trải Nghiệm Premium Hóa:** Sử dụng bộ màu HSL tối, màu vàng hoàng kim làm điểm nhấn thương hiệu (`#ffd700`, `#ffe16d`), kính mờ (Glassmorphism), viền mỏng neon và đổ bóng sâu cao cấp.
- [x] **Hiệu Ứng Trượt Mờ Đồng Bộ (Entrance Slide-Fade):** Mọi trang khi truy cập (Tasks, Coach, AOA, Analytics, Cohort, Diary) đều được phủ hiệu ứng `.animate-page-fade` trượt nhẹ từ dưới lên và mờ dần vô cùng nghệ thuật.
- [x] **Sidebar Hệ Thống Hợp Nhất:** Thanh công cụ bên trái được đồng bộ hóa tuyệt đối trên tất cả các trang, tự động kích hoạt trạng thái "active" có viền vàng bên trái và gradient mờ sang ngang.

---

## 5. 📊 AI Analytics & Radar Chart Engine

- [x] **Đánh Giá Nhận Thức 6 Chiều:** AI tự động phân tích hành vi viết nhật ký, tương tác AOA để chấm điểm: Dữ liệu (Data), Tổng quan (Big Picture), Cảm xúc (Emotion), Sáng tạo (Creativity), Cẩn trọng (Caution), Lạc quan (Optimism).
- [x] **Radar Chart SVG Thuần:** Vẽ biểu đồ SVG tròn trực tiếp trên màn hình, tối ưu hóa hiệu năng vượt trội so với các thư viện biểu đồ nặng nề.
- [x] **Phân tích Xu hướng & Định vị Bản thân (Mindset DNA):** Phân tích sâu sắc thói quen sử dụng từ ngữ trong nhật ký cá nhân và các bài đăng trên AOA Feed để định vị phong cách tư duy của người dùng qua các chiều kích nhận thức.
- [x] **Gợi Ý Kiểu MBTI bằng AI (AI MBTI Profiler):** Phân tích sâu sắc các bài viết tự sự và lịch sử hội thoại với Coach để gợi ý 3 nhóm tính cách MBTI tương thích nhất, kèm theo tỷ lệ phần trăm và lý do phân tích cụ thể cho từng nhóm.
- [x] **Đo Lường Thế Mạnh Tư Duy:** Trích xuất từ 5 đến 8 từ khóa thế mạnh nhận thức dựa trên dữ liệu ngữ nghĩa thực tế.
- [x] **Auto-Submit Success Toast & DOM Fix:**
  * Sửa lỗi rò rỉ thẻ HTML (tag leakage) xung quanh khối toast gửi đánh giá thành công.
  * Tích hợp cơ chế tự động đóng popup gửi thành công sau 2 giây (`closeSubmission`), tự động đưa người dùng trở lại màn hình phân tích trực quan mà không cần thao tác thủ công.

---

## 6. 🌐 Mạng Xã Hội AOA (Ask Others Anything Feed)

- [x] **Xuất Bản Bản Đồ Trí Tuệ (AOA Feed):** Chia sẻ trực tiếp suy nghĩ hoặc sơ đồ tư duy từ nhật ký cá nhân lên bảng tin cộng đồng chỉ với 1 click.
- [x] **Giao diện Dòng Thời Gian (Style Twitter/X):** Newsfeed tối giản, hiển thị ảnh đại diện tròn, tên người dùng, thời gian đăng bài và nội dung định dạng tinh tế.
- [x] **Bản Đồ Nhúng Tương Tác (Embedded Mindmaps):** Mỗi bài đăng có chứa Mindmap đính kèm đều hiển thị một khung Vis.js mini, cho phép người dùng lướt qua, zoom và click xem các node của người khác trực quan.
- [x] **Hệ thống Follow/Unfollow linh hoạt:** Cho phép theo dõi các bộ não khác trong cộng đồng để xây dựng vòng tròn tri thức cộng hưởng, đồng bộ hóa danh sách theo dõi ngay trong database.
- [x] **Bộ Lọc Phân Tách Bảng Tin:** Hỗ trợ tab chuyển đổi nhanh giữa dòng tin "Cộng đồng" toàn cầu và tab "Cá nhân" (hiển thị bài đăng/bình luận riêng của mình).
- [x] **Tương Tác Xã Hội Bền Vững:** Hệ thống lưu trữ lượt thích (Like) và danh sách bình luận (Comment) bền vững theo thời gian.

---

## 7. 📋 Quản Lý Nhiệm Vụ (Todoist-Style Task Manager)

- [x] **Gợi Ý Bài Tập Từ AI Coach:** AI tự động trích xuất các bài tập hành động từ cuộc trò chuyện hoặc nhật ký phản tư để giao cho người dùng.
- [x] **Chấm Điểm & Phân Loại:** Giao diện thẻ nhiệm vụ 2 khu vực: "Chưa hoàn thành" (Backlog / In Progress) và "Đã hoàn thành" với nút bấm check/uncheck mượt mà.
- [x] **Quản lý Subtasks & Độ nỗ lực (Effort Scale):** Hỗ trợ thêm/bớt và check/uncheck subtask chi tiết cho từng nhiệm vụ lớn, thiết lập mức độ nỗ lực (Effort) và hạn chót hoàn thành (Deadline) rõ ràng.
- [x] **Chấm Đỏ Thông Báo (Red Dot Indicator):** Hiệu ứng chấm đỏ nhấp nháy phát sáng ngay cạnh icon "Tasks" trên Sidebar mỗi khi có bài tập mới chưa đọc được giao.
- [x] **Lưu Trữ Đồng Bộ:** Kết hợp đồng bộ dữ liệu nhiệm vụ cá nhân giữa `localStorage` (`thapsang_pdca_tasks`) và API Backend.

---

## 8. 🔥 Chương Trình Học Tập Đỉnh Cao (Cohort-Based Path)

- [x] **Lộ Trình Tái Thiết Tư Duy 3 Giai Đoạn:**
  * **Phase 1: Unlearn** (Nhận diện & Phá bỏ thiên kiến cũ)
  * **Phase 2: Relearn** (Thiết lập cấu trúc tư duy mới với Socratic)
  * **Phase 3: Execute** (Vận hành & Ứng dụng thực tế)
- [x] **Thẻ Học Tập Glassmorphism:** Các thẻ Cohort được thiết kế bắt mắt với tiến độ học, thông tin giảng viên và danh sách thành viên cùng khóa.
- [x] **Bản Đồ Nhiệt Tiến Độ Nhóm (Cohort Progress Heatmap):** Bản đồ dạng lưới hiển thị trực quan tiến độ hoàn thành bài tập của tất cả thành viên trong nhóm. Phân biệt rõ rệt vị trí của chính người dùng (`heatmap-cell-self` kèm hiệu ứng phát sáng hoàng kim `pulse-gold`) và các thành viên khác theo các cấp độ xanh lục bảo (nhạt đến đậm tùy tiến độ).
- [x] **Hệ Thống Accountability Buddy & Đánh Giá Chéo (Interactive Peer Review):**
  * Ghép cặp tự động bạn đồng hành (Accountability Buddy) trong tuần hiện tại.
  * **Interactive Peer Review Panel:** Giao diện trượt mượt mà từ bên phải (Right-side slide-out modal) cho phép chấm điểm chéo các nhiệm vụ của Buddy.
  * **5-Star Rating & Comments:** Hệ thống đánh giá 5 sao tương tác trực quan đi kèm các nhãn phản hồi rõ ràng (*Chưa đạt, Cần cải thiện, Đạt yêu cầu, Tốt, Xuất sắc*) cùng khung nhập nhận xét/góp ý chi tiết cho từng nhiệm vụ (Cả Core và Supplementary Tasks).
  * **Live Feedback Sync:** Review được lưu trữ an toàn trong `localStorage` (`cohort_reviews`), hiển thị trạng thái "Đã review" và tự động gửi cập nhật hoạt động lên dòng thời gian Live Resonance.
- [x] **Dòng Cộng Hưởng Hoạt Động (Live Resonance Feed):** Cập nhật thời gian thực các sự kiện học tập trong Cohort như: hoàn thành bài tập, review chéo bạn đồng hành, tham gia retrospective,... tạo không khí học tập sôi nổi.
- [x] **Phân Tích Rào Cản & AI Retrospective:** Phân tích điểm nghẽn nhận thức chung của Cohort từ AI Coach đi kèm các thanh đo tỷ lệ rào cản nhận thức phổ biến. Hỗ trợ kích hoạt AI Retrospective cuối tuần để nhận định và đặt câu hỏi Socratic sâu sắc cho cả nhóm.
- [x] **Cơ Chế Thích Ứng Lộ Trình (Dynamic Pivot):** Tự động phát hiện rào cản chung của lớp để gợi ý và cho phép người dùng chủ động thêm các nhiệm vụ phụ trợ (supplementary tasks) vào danh sách cá nhân để điều chỉnh lộ trình thích nghi.
- [x] **Sự Tiến Hóa Tư Duy (Mind Map Evolution):** Trực quan hóa tiến trình dịch chuyển tư duy từ trạng thái Unlearn (nút đỏ, trì hoãn) sang Relearn (nút xanh lục phát sáng, Deep Work) được kết nối bằng đường vẽ SVG động đẹp mắt có chấm chuyển động mượt mà.

---

## 9. ⚙️ Cơ Sở Hạ Tầng & Triển Khai (DevOps / Architecture)

- [x] **Hợp Nhất NGINX & Docker Compose:** Cấu hình Docker hóa tách biệt frontend phục vụ tĩnh qua NGINX và backend FastAPI proxy qua cổng `/api`.
- [x] **Persistence Data Management:** File JSON lưu trữ dữ liệu bền vững đặt tại thư mục dự án (`database/`) giúp dễ dàng di chuyển, bảo trì và không làm mất dữ liệu khi restart container.
- [x] **Sử Dụng Biến Môi Trường (`.env`):** Bảo mật tuyệt đối khóa API của các mô hình ngôn ngữ lớn và cấu hình SMTP.
