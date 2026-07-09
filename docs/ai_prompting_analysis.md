# Báo cáo Phân tích Sử dụng AI Prompting trong dự án Thapsang

Tài liệu này tổng hợp và phân tích toàn bộ các file, hàm và endpoint sử dụng AI Prompting (LLM) trong hệ thống Thapsang.

---

## 1. Phân tích tư duy người dùng (Mindset Analyzer)

### [mindset_analyzer.py](file:///d:/thapsang/backend/mindset_analyzer.py)

#### Hàm: `_ai_analyze(username, aoa_text, coach_text, onboarding_context)`

* **Vị trí trong mã nguồn:** [mindset_analyzer.py:Dòng 123](file:///d:/thapsang/backend/mindset_analyzer.py#L123)
* **Mục đích:** Phân tích sâu sắc tư duy và tính cách người dùng từ các bài đăng trên AOA, các cuộc hội thoại với Coach và thông tin onboarding.
* **Cấu trúc Prompt:**
  * **System Prompt:**
    ```text
    Bạn là chuyên gia phân tích tâm lý, hành vi và tư duy AI của nền tảng Thapsang.
    Nhiệm vụ của bạn là đọc hiểu sâu sắc bối cảnh người dùng (context) và ngôn từ thực tế của họ
    để phân loại tính cách (MBTI) và tư duy một cách cá nhân hóa và chính xác nhất.
    Kết luận phải bám sát vào những gì họ thực sự đã viết.
    Hãy phân tích và trả về JSON THUẦN TÚY (không có markdown).
    ```
  * **User Prompt:** Cung cấp thông tin văn bản gộp (tối đa 4000 ký tự AOA và 4000 ký tự hội thoại Coach) cùng schema cấu trúc JSON trả về bắt buộc gồm:
    * `radar_stats`: Các chỉ số 0-100 của Khách quan, Cảm xúc, Tiêu cực, Tích cực, Sáng tạo, Tổng quan.
    * `keywords`: Danh sách từ khóa thế mạnh dịch song ngữ Anh - Việt.
    * `analysis_text`: Nhận xét tổng quan song ngữ (2-4 câu).
    * `mbti_suggestions`: Top 3 MBTI gợi ý èm tỉ lệ % và lý do chi tiết bằng song ngữ.
* **Tham số LLM:**
  * Model mặc định: lấy từ biến môi trường `LLM_MODEL` (thường là `thapsang`).
  * `temperature`: `0.4`

---

## 2. Học và đúc kết ngữ cảnh người dùng (Context Learning)

### [context_learner.py](file:///d:/thapsang/backend/context_learner.py)

#### Hàm: `learn_contexts()`

* **Vị trí trong mã nguồn:** [context_learner.py:Dòng 40](file:///d:/thapsang/backend/context_learner.py#L40)
* **Mục đích:** Quét toàn bộ Nhật ký (Diary) của người dùng trên CMS để đúc kết thành **"Ngữ cảnh cốt lõi" (Core Context)** dài hạn.
* **Cấu trúc Prompt:**
  * **System Prompt:**
    ```text
    Bạn là một chuyên gia phân tích tâm lý học và quản lý tri thức.
    Nhiệm vụ của bạn là đọc các đoạn Nhật ký (Diary) của người dùng và tóm tắt lại thành một
    'Ngữ cảnh cốt lõi' (Core Context) ngắn gọn (dưới 150 từ).
    Mục đích của đoạn tóm tắt này là để lưu trữ vào bộ nhớ dài hạn, giúp AI hiểu được ngay:
    tính cách, những vấn đề bận tâm chính, thói quen và cảm xúc chủ đạo của người dùng.
    Tuyệt đối không đưa ra lời khuyên, chỉ đúc kết sự thật khách quan về người dùng.
    ```
  * **User Prompt:** Cung cấp thông tin nhật ký gộp theo định dạng có tiêu đề, ngày, cảm xúc và nội dung.
* **Tham số LLM:**
  * `temperature`: `0.3`
  * `max_tokens`: `300`

#### Hàm: `generate_context_from_onboarding(username, onboarding)`

* **Vị trí trong mã nguồn:** [context_learner.py:Dòng 106](file:///d:/thapsang/backend/context_learner.py#L106)
* **Mục đích:** Tạo nhanh Core Context ban đầu ngay từ câu trả lời khảo sát Onboarding của người dùng mới.
* **Cấu trúc Prompt:**
  * **System Prompt:**
    ```text
    Bạn là một chuyên gia phân tích tâm lý học và quản lý tri thức.
    Nhiệm vụ của bạn là đọc tóm tắt lựa chọn onboarding của người dùng và tạo một 'Ngữ cảnh cốt lõi' (Core Context) ngắn gọn dưới 150 từ.
    Đoạn này phải nêu rõ tính cách sơ bộ, những bận tâm chính, ưu tiên mục tiêu, và các điều kiện nhạy cảm nếu có.
    Tuyệt đối không đưa lời khuyên, chỉ tóm tắt các thông tin khách quan.
    ```
  * **User Prompt:** Cung cấp thông tin tuổi/ngày sinh, giới tính, sở thích, vấn đề chính, mục tiêu của người dùng.
* **Tham số LLM:**
  * `temperature`: `0.2`
  * `max_tokens`: `250`

---

## 3. Các API AI chính của Server Lighthouse

### [main.py](file:///d:/thapsang/backend/main.py)

#### A. Trò chuyện AI Socratic Mirror Coach

* **Hàm:** `process_chat(req: ChatRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 2906](file:///d:/thapsang/backend/main.py#L2906) (endpoint POST `/api/v1/chat`)
* **Mục đích:** Xử lý hội thoại thời gian thực, tự động tích lũy sơ đồ tư duy (Mindmap) và đưa ra các câu hỏi Socratic phản chiếu sâu sắc.
* **Cấu trúc Prompt:**
  * Sử dụng cấu trúc **`SYSTEM_PROMPT`** chính ở dòng 2661:
    * **Vai trò:** "Socratic Mirror Coach" phản chiếu khách quan, lạnh lùng, lý trí, sắc bén. Tuyệt đối không an ủi, không đưa lời khuyên.
    * **Nhiệm vụ:** Đặt đúng 1 câu hỏi duy nhất kích hoạt "Đứt gãy nhận thức" (Cognitive Rupture) giúp người dùng thấy sự vô lý/mâu thuẫn trong niềm tin của họ.
    * **Yêu cầu JSON:** Định dạng JSON nghiêm ngặt chứa `title` (tiêu đề phiên chat), `reasoning` (suy luận của AI), `question` (câu hỏi Socratic), `nodes` (các nút tư duy trên bản đồ), `edges` (mối nối), `suggested_replies` (3 gợi ý phản hồi phù hợp bối cảnh) và `tasks` (nhiệm vụ được giao).
  * **Các chỉ thị bổ sung (Dynamic Directives):**
    * **Cumulative Mindmap:** Hướng dẫn AI không ghi đè node cũ mà tạo node mới (`n3`, `n4`, `n5`...) và liên kết với node trước đó để đồ thị phát triển lớn dần.
    * **Language Sync:** Tự động phát hiện ngôn ngữ của tin nhắn mới nhất để dịch toàn bộ thông tin JSON sang ngôn ngữ đó.
    * **Task Assignment:** Nếu số lượt chat của người dùng chia hết cho 5, bắt buộc AI sinh đúng 1 nhiệm vụ hành động thực tế cá nhân hóa trong mảng `tasks` để giải tỏa điểm nghẽn của họ. Nếu không chia hết cho 5, mảng `tasks` phải để rỗng.
* **Tham số LLM:**
  * `temperature`: `0.2`

#### B. Tạo lời chào và câu hỏi Socratic ban đầu

* **Hàm:** `generate_welcome(req: WelcomeRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 2730](file:///d:/thapsang/backend/main.py#L2730) (endpoint POST `/api/v1/chat/welcome`)
* **Mục đích:** Sinh ra câu hỏi Socratic mở đầu cá nhân hóa cao dựa trên hồ sơ Core Context của người dùng.
* **Cấu trúc Prompt:**
  * **System Prompt:** Yêu cầu chào mừng thân thiện bằng tên hiển thị của người dùng, đọc kỹ Core Context để viết lời dẫn ngắn gọn, tập trung vào nỗi lo/mục tiêu lớn nhất của họ và đặt đúng 1 câu hỏi Socratic sâu sắc để họ bắt đầu chia sẻ.
* **Tham số LLM:**
  * `temperature`: `0.3`

#### C. Cá nhân hóa lộ trình học tập tuần (Weekly Syllabus Personalization)

* **Hàm:** `personalize_week_endpoint(req: PersonalizeWeekRequest, ...)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 762](file:///d:/thapsang/backend/main.py#L762) (endpoint POST `/api/v1/cohort/personalize-week`)
* **Mục đích:** Tùy biến syllabus của tuần học hiện tại dựa trên hội thoại và nhật ký gần đây của người dùng.
* **Cấu trúc Prompt:** Yêu cầu thiết lập **chính xác 1 nhiệm vụ cốt lõi (core)** và **1 nhiệm vụ bổ trợ (supplementary)**. Tự thiết kế tiêu đề, mô tả hướng dẫn chi tiết và thời lượng ước tính cho từng nhiệm vụ dưới định dạng JSON song ngữ.
* **Tham số LLM:**
  * `temperature`: `0.7`

#### D. Tạo bài trắc nghiệm soi chiếu Socratic cuối tuần

* **Hàm:** `generate_quiz_endpoint(req: GenerateQuizRequest)` và helper `auto_generate_quiz_for_week(...)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 3160](file:///d:/thapsang/backend/main.py#L3160) (endpoint POST `/api/v1/cohort/generate-quiz`) và [main.py:Dòng 477](file:///d:/thapsang/backend/main.py#L477)
* **Mục đích:** Tạo bài trắc nghiệm trắc nghiệm soi chiếu cá nhân hóa cuối tuần sau khi người dùng hoàn thành các nhiệm vụ.
* **Cấu trúc Prompt:** Sinh ra **đúng 8 câu hỏi trắc nghiệm Socratic độc nhất** (4 lựa chọn mỗi câu). Câu hỏi phải gắn liền với nhiệm vụ của tuần, các cảm xúc nhật ký và rào cản nhận thức thực tế của họ. Tuyệt đối không hỏi câu hỏi định nghĩa lý thuyết suông. Định dạng cấu trúc song ngữ Anh - Việt tách biệt trong JSON.
* **Tham số LLM:**
  * `temperature`: `0.8` (hoặc `0.4` trong hàm tự động chạy ngầm)
  * `presence_penalty`: `0.6`
  * `frequency_penalty`: `0.6`
  * `max_tokens`: `3000`

#### E. Đánh giá bài luận chiêm nghiệm (Essay Grading)

* **Hàm:** `submit_quiz_endpoint(req: SubmitQuizRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 3554](file:///d:/thapsang/backend/main.py#L3554) (endpoint POST `/api/v1/cohort/submit-quiz`)
* **Mục đích:** Phân tích và đánh giá chất lượng bài viết chiêm nghiệm (reflection essay) của người dùng để tặng điểm thưởng và phản hồi.
* **Cấu trúc Prompt:** Cung cấp tiêu đề bài học và bài luận của 2 nhiệm vụ học tập tuần. Đánh giá độ sâu sắc, sự trung thực và unlearning insight để trả về điểm thưởng (1-20 điểm) cùng lời nhận xét định tính (80-120 từ) tương ứng.
* **Tham số LLM:**
  * `temperature`: `0.3`
  * `max_tokens`: `1024`

#### F. Phân tích điểm nghẽn và Gợi ý điều chỉnh hành động (Bottleneck & Pivot)

* **Hàm:** `get_ai_bottleneck(req: AIBottleneckRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 1491](file:///d:/thapsang/backend/main.py#L1491) (endpoint POST `/api/v1/cohort/ai-bottleneck`)
* **Mục đích:** Phân tích các nhiệm vụ còn tồn đọng và tiến độ hoàn thành tuần của người học để đề xuất hành động thay đổi nhỏ.
* **Cấu trúc Prompt:** Nhìn vào danh sách các nhiệm vụ đã làm và chưa làm. Đưa ra chiêm nghiệm Socratic (dưới 60 từ) giải thích lý do bị nghẽn, chấm điểm mức độ cản trở (0-100%) của 1-3 điểm nghẽn và đề xuất một nhiệm vụ phụ trợ rất nhỏ (pivot task) giúp họ dễ dàng bắt đầu lại.
* **Tham số LLM:**
  * `temperature`: `0.5`
  * `top_p`: `0.9`

#### G. Nhận xét Retrospective cá nhân hóa

* **Hàm:** `generate_retrospective_helper(...)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 1397](file:///d:/thapsang/backend/main.py#L1397) (endpoint GET/POST `/api/v1/cohort/ai-retrospective`)
* **Mục đích:** Tạo lời nhận xét chiêm nghiệm cuối tuần dựa trên tiến độ và kết quả thực hiện nhiệm vụ.
* **Cấu trúc Prompt:** Viết lời bình luận đánh giá cá nhân hóa (80-120 từ) thấu cảm, thúc đẩy sự tự nhận thức và đặt thêm 1 câu hỏi tự vấn Socratic về cách thức cam kết hành động hoặc quản lý thời gian của họ.
* **Tham số LLM:**
  * `temperature`: `0.5`
  * `max_tokens`: `1024`

#### H. Chia nhỏ nhiệm vụ (Pomodoro Microsteps Generator)

* **Hàm:** `generate_microsteps_endpoint(req: MicrostepsRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 3753](file:///d:/thapsang/backend/main.py#L3753) (endpoint POST `/api/v1/tasks/generate-microsteps`)
* **Mục đích:** Băm nhỏ một nhiệm vụ lớn thành các bước hành động cụ thể tương ứng các phiên làm việc tập trung Pomodoro 25 phút.
* **Cấu trúc Prompt:** Nhận tiêu đề, mục tiêu và tham số `effort` (số bước). Yêu cầu tạo đúng `effort` bước nhỏ cụ thể và thực tế dưới dạng JSON danh sách, tiêu đề mỗi bước định dạng song ngữ phân cách bởi `|||`.
* **Tham số LLM:**
  * `temperature`: `0.5`
  * `max_tokens`: `1024`

#### I. Phân tích xu hướng cộng đồng (AOA Community Trend Analyzer)

* **Hàm:** `get_aoa_trending()`
* **Vị trí trong mã nguồn:** [main.py:Dòng 2382](file:///d:/thapsang/backend/main.py#L2382) (endpoint GET `/api/v1/aoa/trending`)
* **Mục đích:** Tổng hợp và phân tích xu hướng thảo luận chung của cộng đồng từ các bài viết trên mạng xã hội AOA.
* **Cấu trúc Prompt:** Đọc toàn bộ nội dung của các bài đăng gần đây để trả về JSON chứa top hashtags phổ biến, 3 xu hướng nổi bật song ngữ (category, label, title) và 1 đoạn tóm tắt chủ đề thảo luận chung (2-3 câu song ngữ).
* **Tham số LLM:**
  * `temperature`: `0.3`

#### J. Phản hồi Socratic cho Nhật ký (Diary Socratic Feedback)

* **Hàm:** `create_diary(username: str, req: DiaryEntryRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 1856](file:///d:/thapsang/backend/main.py#L1856) (endpoint POST `/api/v1/diary/{username}`)
* **Mục đích:** Phản hồi tức thì của AI Coach ngay sau khi người dùng lưu một bài nhật ký mới.
* **Cấu trúc Prompt:** Đọc tiêu đề, cảm xúc và nội dung nhật ký để đưa ra phản hồi Socratic dưới 80 từ bằng tiếng Việt ấm áp, thông tuệ, đặt 1 câu hỏi giúp người dùng tự soi chiếu sâu sắc thay vì khuyên nhủ.
* **Tham số LLM:**
  * `max_tokens`: `200`

---

## 4. Các file phụ trợ, công cụ kiểm thử (Test / Debug)

* **[backend/debug_join_full.py](file:///d:/thapsang/backend/debug_join_full.py):** Tập tin kiểm thử mô phỏng toàn bộ quy trình Onboarding và Personal Roadmap, gọi LLM với một prompt test ngắn để kiểm tra kết nối proxy.
* **[test_openai.py](file:///d:/thapsang/test_openai.py):** Script nhỏ kiểm tra tính khả dụng của API Key, gọi kiểm thử model `thapsang` thông qua DigitalForce API gateway bằng cách gửi tin nhắn `"Hello"`.
* **[test_chat.py](file:///d:/thapsang/test_chat.py):** Script kiểm thử endpoint `/api/v1/chat` để đảm bảo hệ thống phản hồi đúng cấu trúc JSON quy định.
