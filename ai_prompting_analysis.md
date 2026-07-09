# Báo cáo Phân tích Sử dụng AI Prompting trong dự án Thapsang

Tài liệu này tổng hợp và phân tích toàn bộ các file, hàm và endpoint sử dụng AI Prompting (LLM) trong hệ thống Thapsang (đã được tối ưu hóa tham số `temperature` và `top_p` để cho ra kết quả ổn định và chính xác nhất).

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
    * `mbti_suggestions`: Top 3 MBTI gợi ý kèm tỉ lệ % và lý do chi tiết bằng song ngữ.
* **Tham số LLM:**
  * Model: `LLM_MODEL` (lấy phần tử đầu tiên, ví dụ: `thapsang`).
  * `stream`: `False` (Mặc định không stream)
  * `temperature`: `0.2` (Đã hạ từ 0.4 để đảm bảo trích xuất cấu trúc JSON chính xác)
  * `top_p`: `0.9` (Đã cấu hình để tăng độ tập trung nhận thức)

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
  * Model: `LLM_MODEL` (lấy phần tử đầu tiên)
  * `stream`: `False`
  * `temperature`: `0.2`
  * `max_tokens`: `300`
  * `top_p`: `0.9`

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
  * Model: `LLM_MODEL` (lấy phần tử đầu tiên)
  * `stream`: `False`
  * `temperature`: `0.1`
  * `max_tokens`: `250`
  * `top_p`: `0.9`

---

## 3. Các API AI chính của Server Lighthouse

### [main.py](file:///d:/thapsang/backend/main.py)

#### A. Trò chuyện AI Socratic Mirror Coach
* **Hàm:** `process_chat(req: ChatRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 2906](file:///d:/thapsang/backend/main.py#L2906) (endpoint POST `/api/v1/chat`)
* **Mục đích:** Xử lý hội thoại thời gian thực, tự động tích lũy sơ đồ tư duy (Mindmap) và đưa ra các câu hỏi Socratic phản chiếu sâu sắc.
* **Cấu trúc Prompt:**
  * Sử dụng cấu trúc **`SYSTEM_PROMPT`** chính ở dòng 2661 (Đã tinh chỉnh cho mảng tâm lý học):
    * **Vai trò:** "Socratic Mirror Coach" phản chiếu khách quan, thông tuệ, kiên nhẫn và sâu sắc. Đóng vai trò chiếc gương soi chiếu trí tuệ thay vì lạnh lùng hay đồng cảm hời hợt.
    * **Quy tắc dẫn dắt:** Dẫn dắt khách quan, không đưa lời khuyên/câu trả lời trực tiếp mà đặt câu hỏi gợi mở để người dùng tự khám phá chính họ. Chỉ phân tích dựa trên sự thật và thông tin người dùng cung cấp để **ngăn ngừa triệt để suy diễn ảo tưởng**.
    * **Nhiệm vụ:** Đặt đúng 1 câu hỏi duy nhất kích hoạt "Đứt gãy nhận thức" (Cognitive Rupture) giúp người dùng tự thấy sự ngụy biện logic.
* **Tham số LLM (Cơ chế tự động fallback):**
  * **Cơ chế gọi 1 (Ưu tiên - Streaming):**
    * `stream`: `True`
    * `temperature`: `0.2`
    * `top_p`: `0.9`
  * **Cơ chế gọi 2 (Fallback - Non-streaming):**
    * `stream`: `False`
    * `temperature`: `0.2`
    * `max_tokens`: `3000`
    * `top_p`: `0.9`

#### B. Tạo lời chào và câu hỏi Socratic ban đầu
* **Hàm:** `generate_welcome(req: WelcomeRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 2730](file:///d:/thapsang/backend/main.py#L2730) (endpoint POST `/api/v1/chat/welcome`)
* **Mục đích:** Sinh ra câu hỏi Socratic mở đầu cá nhân hóa cao dựa trên hồ sơ Core Context của người dùng.
* **Cấu trúc Prompt:**
  * **System Prompt:** Chào mừng bằng tên người dùng, đọc kỹ Core Context để đặt 1 câu hỏi Socratic sâu sắc, tinh tế xoáy vào bận tâm lớn nhất của họ mà không đưa ra lời khuyên hay an ủi hời hợt, dẫn dắt tự phản tỉnh không phán xét hay suy diễn ảo tưởng.
* **Tham số LLM:**
  * **Cơ chế gọi 1 (Ưu tiên - Streaming):**
    * `stream`: `True`
    * `temperature`: `0.2`
    * `top_p`: `0.9`
  * **Cơ chế gọi 2 (Fallback - Non-streaming):**
    * `stream`: `False`
    * `temperature`: `0.2`
    * `max_tokens`: `3000`
    * `top_p`: `0.9`

#### C. Cá nhân hóa lộ trình học tập tuần (Weekly Syllabus Personalization)
* **Hàm:** `personalize_week_endpoint(req: PersonalizeWeekRequest, ...)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 762](file:///d:/thapsang/backend/main.py#L762) (endpoint POST `/api/v1/cohort/personalize-week`)
* **Tham số LLM:**
  * **Cơ chế gọi 1 (Ưu tiên - Streaming):**
    * `stream`: `True`
    * `temperature`: `0.3`
    * `top_p`: `0.95`
  * **Cơ chế gọi 2 (Fallback - Non-streaming):**
    * `stream`: `False`
    * `temperature`: `0.3`
    * `max_tokens`: `1024`
    * `top_p`: `0.95`

#### D. Tạo bài trắc nghiệm soi chiếu Socratic cuối tuần
* **Hàm:** `generate_quiz_endpoint(req: GenerateQuizRequest)` và helper `auto_generate_quiz_for_week(...)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 3160](file:///d:/thapsang/backend/main.py#L3160) (endpoint POST `/api/v1/cohort/generate-quiz`) và [main.py:Dòng 477](file:///d:/thapsang/backend/main.py#L477)
* **Tham số LLM cho `generate_quiz_endpoint`:**
  * `stream`: `False`
  * `temperature`: `0.3`
  * `presence_penalty`: `0.6`
  * `frequency_penalty`: `0.6`
  * `max_tokens`: `3000`
  * `top_p`: `0.9`
* **Tham số LLM cho helper `auto_generate_quiz_for_week`:**
  * **Cơ chế gọi 1 (Ưu tiên - Streaming):**
    * `stream`: `True`
    * `temperature`: `0.2`
    * `top_p`: `0.9`
    * `max_tokens`: `3000`
  * **Cơ chế gọi 2 (Fallback - Non-streaming):**
    * `stream`: `False`
    * `temperature`: `0.2`
    * `top_p`: `0.9`
    * `max_tokens`: `3000`

#### E. Đánh giá bài luận chiêm nghiệm (Essay Grading)
* **Hàm:** `submit_quiz_endpoint(req: SubmitQuizRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 3554](file:///d:/thapsang/backend/main.py#L3554) (endpoint POST `/api/v1/cohort/submit-quiz`)
* **Tham số LLM:**
  * `stream`: `False`
  * `temperature`: `0.2`
  * `max_tokens`: `1024`
  * `top_p`: `0.9`

#### F. Phân tích điểm nghẽn và Gợi ý điều chỉnh hành động (Bottleneck & Pivot)
* **Hàm:** `get_ai_bottleneck(req: AIBottleneckRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 1491](file:///d:/thapsang/backend/main.py#L1491) (endpoint POST `/api/v1/cohort/ai-bottleneck`)
* **Tham số LLM:**
  * `stream`: `False`
  * `temperature`: `0.2`
  * `top_p`: `0.9`
  * `max_tokens`: `1024`

#### G. Nhận xét Retrospective cá nhân hóa
* **Hàm:** `generate_retrospective_helper(...)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 1397](file:///d:/thapsang/backend/main.py#L1397) (endpoint GET/POST `/api/v1/cohort/ai-retrospective`)
* **Tham số LLM:**
  * `stream`: `False`
  * `temperature`: `0.4`
  * `max_tokens`: `1024`
  * `top_p`: `0.95`

#### H. Chia nhỏ nhiệm vụ (Pomodoro Microsteps Generator)
* **Hàm:** `generate_microsteps_endpoint(req: MicrostepsRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 3753](file:///d:/thapsang/backend/main.py#L3753) (endpoint POST `/api/v1/tasks/generate-microsteps`)
* **Tham số LLM:**
  * **Cơ chế gọi 1 (Ưu tiên - Streaming):**
    * `stream`: `True`
    * `temperature`: `0.2`
    * `top_p`: `0.9`
  * **Cơ chế gọi 2 (Fallback - Non-streaming):**
    * `stream`: `False`
    * `temperature`: `0.2`
    * `max_tokens`: `1024`
    * `top_p`: `0.9`

#### I. Phân tích xu hướng cộng đồng (AOA Community Trend Analyzer)
* **Hàm:** `get_aoa_trending()`
* **Vị trí trong mã nguồn:** [main.py:Dòng 2382](file:///d:/thapsang/backend/main.py#L2382) (endpoint GET `/api/v1/aoa/trending`)
* **Tham số LLM:**
  * `stream`: `False`
  * `temperature`: `0.2`
  * `top_p`: `0.9`

#### J. Phản hồi Socratic cho Nhật ký (Diary Socratic Feedback)
* **Hàm:** `create_diary(username: str, req: DiaryEntryRequest)`
* **Vị trí trong mã nguồn:** [main.py:Dòng 1856](file:///d:/thapsang/backend/main.py#L1856) (endpoint POST `/api/v1/diary/{username}`)
* **Mục đích:** Phản hồi tức thì của AI Coach ngay sau khi người dùng lưu một bài nhật ký mới.
* **Cấu trúc Prompt:** Đọc tiêu đề, cảm xúc và nội dung nhật ký để đưa ra phản hồi Socratic dưới 80 từ bằng tiếng Việt ấm áp, thông tuệ, đặt 1 câu hỏi giúp người dùng tự soi chiếu sâu sắc thay vì khuyên nhủ.
* **Tham số LLM:**
  * `stream`: `False`
  * `temperature`: `0.4`
  * `max_tokens`: `200`
  * `top_p`: `0.95`
