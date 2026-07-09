# Hướng Dẫn Deploy Thapsang lên Hệ Thống Quản Trị Headless CMS

> **Tài liệu này hướng dẫn cách ánh xạ toàn bộ dữ liệu và API của dự án Thapsang lên hệ thống quản trị Headless CMS / Low-code DB engine theo mô hình trong `ADMIN_GUIDE.md`.**

---

## 📋 Tổng Quan Kiến Trúc

Dự án **Thapsang Mindset OS** hiện tại sử dụng:

- **Backend**: FastAPI (Python) với JSON file-based database
- **Frontend**: Static HTML/CSS/JS (Alpine.js + TailwindCSS)
- **Database**: 3 file JSON chính (`thapsang_db.json`, `aoa_db.json`, `cohort_db.json`)

Để deploy lên hệ thống Headless CMS, chúng ta cần:

1. **Tạo Collections (Bảng)** tương ứng với các entity trong dự án
2. **Định nghĩa Schema (Trường dữ liệu)** cho từng collection
3. **Migrate dữ liệu** từ JSON files sang CMS database
4. **Tạo API Keys** và cấu hình môi trường
5. **Chuyển đổi API calls** từ FastAPI sang CMS REST API

---

## 🗄️ Phần 1: Cấu Trúc Collections & Schema

### 1.1. Collection: `users` (Người dùng)

**Mục đích**: Quản lý tài khoản, profile, và thông tin xác thực người dùng.

| Field Name          | Field Type          | Required | Default        | Description                  |
| ------------------- | ------------------- | -------- | -------------- | ---------------------------- |
| `id`              | UUID                | ✅       | auto           | ID duy nhất                 |
| `username`        | String              | ✅       | -              | Tên đăng nhập (unique)   |
| `password`        | Hash                | ✅       | -              | Mật khẩu đã mã hóa     |
| `email`           | Email               | ✅       | -              | Email (unique)               |
| `full_name`       | String              | ❌       | ""             | Tên đầy đủ              |
| `display_name`    | String              | ❌       | username       | Tên hiển thị              |
| `bio`             | Long Text           | ❌       | "Học hỏi..." | Tiểu sử                    |
| `avatar`          | String (URL/Base64) | ❌       | ""             | Ảnh đại diện             |
| `banner`          | String (URL/Base64) | ❌       | ""             | Ảnh bìa                    |
| `following_list`  | JSON                | ❌       | []             | Danh sách người theo dõi |
| `onboarded`       | Boolean             | ❌       | false          | Đã hoàn thành onboarding |
| `onboarding_data` | JSON                | ❌       | null           | Dữ liệu onboarding         |
| `created_at`      | DateTime            | ✅       | now()          | Ngày tạo                   |
| `updated_at`      | DateTime            | ✅       | now()          | Ngày cập nhật             |

### 1.2. Collection: `chat_sessions` (Phiên trò chuyện với AI Coach)

**Mục đích**: Lưu trữ lịch sử chat giữa user và AI Socratic Coach.

| Field Name       | Field Type       | Required | Default              | Description                      |
| ---------------- | ---------------- | -------- | -------------------- | -------------------------------- |
| `id`           | UUID             | ✅       | auto                 | ID phiên chat                   |
| `user_id`      | Relation (users) | ✅       | -                    | Liên kết tới user             |
| `username`     | String           | ✅       | -                    | Username (để query nhanh)      |
| `chat_history` | JSON             | ✅       | []                   | Mảng messages [{role, content}] |
| `graph_data`   | JSON             | ✅       | {nodes:[], edges:[]} | Dữ liệu mindmap graph          |
| `tasks`        | JSON             | ❌       | []                   | Tasks được AI extract         |
| `has_new_task` | Boolean          | ❌       | false                | Có task mới chưa xem          |
| `created_at`   | DateTime         | ✅       | now()                | Ngày tạo                       |
| `updated_at`   | DateTime         | ✅       | now()                | Ngày cập nhật                 |

---

### 1.3. Collection: `diary_entries` (Nhật ký Obsocratic)

**Mục đích**: Lưu trữ các ghi chép cá nhân trong Thapsang Vault.

| Field Name     | Field Type       | Required | Default | Description                                      |
| -------------- | ---------------- | -------- | ------- | ------------------------------------------------ |
| `id`         | UUID             | ✅       | auto    | ID entry                                         |
| `user_id`    | Relation (users) | ✅       | -       | Liên kết tới user                             |
| `username`   | String           | ✅       | -       | Username                                         |
| `title`      | String           | ✅       | -       | Tiêu đề ghi chép                             |
| `content`    | Long Text        | ❌       | ""      | Nội dung Markdown                               |
| `mood`       | Single Select    | ❌       | "Calm"  | Tâm trạng (Calm, Happy, Sad, Anxious, Excited) |
| `folder`     | String           | ❌       | ""      | Thư mục phân loại                            |
| `ai_insight` | Long Text        | ❌       | ""      | Phản hồi Socratic từ AI                       |
| `date`       | DateTime         | ✅       | now()   | Ngày viết                                      |
| `created_at` | DateTime         | ✅       | now()   | Ngày tạo                                       |
| `updated_at` | DateTime         | ✅       | now()   | Ngày cập nhật                                 |

**Cấu hình Single Select cho `mood`:**

- Options: `Calm` (Xanh dương), `Happy` (Vàng), `Sad` (Xám), `Anxious` (Đỏ), `Excited` (Cam)
- Default: `Calm`

### 1.4. Collection: `diary_folders` (Thư mục Diary)

**Mục đích**: Quản lý cấu trúc thư mục của Vault.

| Field Name     | Field Type       | Required | Default | Description          |
| -------------- | ---------------- | -------- | ------- | -------------------- |
| `id`         | UUID             | ✅       | auto    | ID thư mục         |
| `user_id`    | Relation (users) | ✅       | -       | Liên kết tới user |
| `username`   | String           | ✅       | -       | Username             |
| `name`       | String           | ✅       | -       | Tên thư mục       |
| `created_at` | DateTime         | ✅       | now()   | Ngày tạo           |

---

### 1.5. Collection: `aoa_posts` (Bài đăng AOA Feed)

**Mục đích**: Lưu trữ bài đăng trong mạng xã hội Ask Others Anything.

| Field Name        | Field Type       | Required | Default              | Description           |
| ----------------- | ---------------- | -------- | -------------------- | --------------------- |
| `id`            | UUID             | ✅       | auto                 | ID bài đăng        |
| `author_id`     | Relation (users) | ✅       | -                    | Liên kết tới user  |
| `author_name`   | String           | ✅       | -                    | Tên tác giả        |
| `author_avatar` | String           | ❌       | ""                   | Avatar tác giả      |
| `content`       | Long Text        | ✅       | -                    | Nội dung bài đăng |
| `graph_data`    | JSON             | ✅       | {nodes:[], edges:[]} | Mindmap đính kèm   |
| `likes`         | Integer          | ❌       | 0                    | Số lượt thích     |
| `shares`        | Integer          | ❌       | 0                    | Số lượt chia sẻ   |
| `timestamp`     | DateTime         | ✅       | now()                | Thời gian đăng     |
| `created_at`    | DateTime         | ✅       | now()                | Ngày tạo            |
| `updated_at`    | DateTime         | ✅       | now()                | Ngày cập nhật      |

---

### 1.6. Collection: `aoa_comments` (Bình luận AOA)

**Mục đích**: Lưu trữ bình luận trên các bài đăng AOA.

| Field Name        | Field Type           | Required | Default | Description                 |
| ----------------- | -------------------- | -------- | ------- | --------------------------- |
| `id`            | UUID                 | ✅       | auto    | ID comment                  |
| `post_id`       | Relation (aoa_posts) | ✅       | -       | Liên kết tới bài đăng |
| `author_id`     | Relation (users)     | ✅       | -       | Liên kết tới user        |
| `author_name`   | String               | ✅       | -       | Tên người bình luận    |
| `author_avatar` | String               | ❌       | ""      | Avatar                      |
| `content`       | Long Text            | ✅       | -       | Nội dung bình luận       |
| `timestamp`     | DateTime             | ✅       | now()   | Thời gian bình luận      |
| `created_at`    | DateTime             | ✅       | now()   | Ngày tạo                  |

### 1.7. Collection: `tasks` (Công việc cá nhân)

**Mục đích**: Quản lý task board kiểu Todoist.

| Field Name       | Field Type       | Required | Default   | Description                             |
| ---------------- | ---------------- | -------- | --------- | --------------------------------------- |
| `id`           | UUID             | ✅       | auto      | ID task                                 |
| `user_id`      | Relation (users) | ✅       | -         | Liên kết tới user                    |
| `username`     | String           | ✅       | -         | Username                                |
| `title`        | String           | ✅       | -         | Tiêu đề task                         |
| `goal`         | String           | ❌       | ""        | Mục tiêu/Mô tả                      |
| `status`       | Single Select    | ✅       | "backlog" | Trạng thái task                       |
| `deadline`     | Date             | ❌       | null      | Hạn chót                              |
| `effort`       | Integer          | ❌       | 1         | Độ khó (1-5)                         |
| `subtasks`     | JSON             | ❌       | []        | Danh sách subtask [{title, completed}] |
| `context_link` | String           | ❌       | ""        | Liên kết ngữ cảnh                   |
| `created_at`   | DateTime         | ✅       | now()     | Ngày tạo                              |
| `updated_at`   | DateTime         | ✅       | now()     | Ngày cập nhật                        |

**Cấu hình Single Select cho `status`:**

- Options: `backlog` (Xám), `in_progress` (Vàng), `done` (Xanh lá)
- Default: `backlog`

---

### 1.8. Collection: `cohort_members` (Thành viên Cohort)

**Mục đích**: Quản lý thành viên trong chương trình học nhóm.

| Field Name        | Field Type       | Required | Default     | Description                     |
| ----------------- | ---------------- | -------- | ----------- | ------------------------------- |
| `id`            | UUID             | ✅       | auto        | ID member                       |
| `cohort_id`     | String           | ✅       | "cohort_04" | ID cohort                       |
| `user_id`       | Relation (users) | ❌       | null        | Liên kết tới user (nếu có) |
| `username`      | String           | ✅       | -           | Username                        |
| `display_name`  | String           | ✅       | -           | Tên hiển thị                 |
| `week_progress` | Integer          | ❌       | 0           | Tiến độ tuần (%)            |
| `buddy`         | String           | ❌       | ""          | Username của buddy             |
| `joined`        | Date             | ✅       | now()       | Ngày tham gia                  |
| `is_self`       | Boolean          | ❌       | false       | Đánh dấu user hiện tại     |
| `created_at`    | DateTime         | ✅       | now()       | Ngày tạo                      |
| `updated_at`    | DateTime         | ✅       | now()       | Ngày cập nhật                |

### 1.9. Collection: `cohort_syllabus` (Giáo trình Cohort)

**Mục đích**: Lưu trữ nội dung giáo trình theo tuần.

| Field Name      | Field Type    | Required | Default     | Description                             |
| --------------- | ------------- | -------- | ----------- | --------------------------------------- |
| `id`          | UUID          | ✅       | auto        | ID syllabus                             |
| `cohort_id`   | String        | ✅       | "cohort_04" | ID cohort                               |
| `week`        | Integer       | ✅       | -           | Số tuần                               |
| `phase`       | Single Select | ✅       | -           | Giai đoạn (unlearn, relearn, execute) |
| `title`       | String        | ✅       | -           | Tiêu đề tuần                        |
| `description` | Long Text     | ✅       | -           | Mô tả                                 |
| `status`      | Single Select | ✅       | "upcoming"  | Trạng thái (done, active, upcoming)   |
| `tasks`       | JSON          | ✅       | []          | Danh sách tasks [{id, title, type}]    |
| `created_at`  | DateTime      | ✅       | now()       | Ngày tạo                              |

**Cấu hình Single Select cho `phase`:**

- Options: `unlearn` (Đỏ), `relearn` (Vàng), `execute` (Xanh lá)

**Cấu hình Single Select cho `status`:**

- Options: `done` (Xanh lá), `active` (Vàng), `upcoming` (Xám)

---

### 1.10. Collection: `analytics_assessments` (Đánh giá Analytics)

**Mục đích**: Lưu trữ kết quả đánh giá tư duy định kỳ.

| Field Name                  | Field Type       | Required | Default | Description                                |
| --------------------------- | ---------------- | -------- | ------- | ------------------------------------------ |
| `id`                      | UUID             | ✅       | auto    | ID assessment                              |
| `user_id`                 | Relation (users) | ✅       | -       | Liên kết tới user                       |
| `username`                | String           | ✅       | -       | Username                                   |
| `label`                   | String           | ✅       | -       | Nhãn mốc (Mốc 1, Mốc 2...)             |
| `decision_quality_score`  | Integer          | ✅       | -       | Điểm chất lượng quyết định (0-100) |
| `mindset_retention_score` | Integer          | ✅       | -       | Điểm duy trì tư duy (0-100)            |
| `ratings`                 | JSON             | ✅       | {}      | Chi tiết đánh giá {q1, q2, q3...}      |
| `created_at`              | DateTime         | ✅       | now()   | Ngày tạo                                 |

---

## 🔧 Phần 2: Thiết Lập Collections trong CMS

### Bước 1: Truy cập Settings → Datasources

1. Click vào **avatar Admin** → **Settings**
2. Chọn tab **Datasources**
3. Click **+ Create Collection** để tạo từng bảng

### Bước 2: Tạo Collection `users`

1. **Collection Name**: `users`
2. Click **Configure fields** và thêm các trường theo bảng 1.1
3. Đặt `username` và `email` là **Unique** (Settings → Validation → Unique)
4. Đặt `password` là **Hash** type với bcrypt algorithm
5. Click **Save**

### Bước 3: Tạo các Collections còn lại

Lặp lại quy trình tương tự cho:

- `chat_sessions` (bảng 1.2)
- `diary_entries` (bảng 1.3)
- `diary_folders` (bảng 1.4)
- `aoa_posts` (bảng 1.5)
- `aoa_comments` (bảng 1.6)
- `tasks` (bảng 1.7)
- `cohort_members` (bảng 1.8)
- `cohort_syllabus` (bảng 1.9)
- `analytics_assessments` (bảng 1.10)

### Bước 4: Thiết lập Relations (Quan hệ giữa các bảng)

Trong CMS, thiết lập các **Foreign Key Relations**:

| Collection                | Field         | Relation Type | Target Collection |
| ------------------------- | ------------- | ------------- | ----------------- |
| `chat_sessions`         | `user_id`   | Many-to-One   | `users`         |
| `diary_entries`         | `user_id`   | Many-to-One   | `users`         |
| `diary_folders`         | `user_id`   | Many-to-One   | `users`         |
| `aoa_posts`             | `author_id` | Many-to-One   | `users`         |
| `aoa_comments`          | `author_id` | Many-to-One   | `users`         |
| `aoa_comments`          | `post_id`   | Many-to-One   | `aoa_posts`     |
| `tasks`                 | `user_id`   | Many-to-One   | `users`         |
| `cohort_members`        | `user_id`   | Many-to-One   | `users`         |
| `analytics_assessments` | `user_id`   | Many-to-One   | `users`         |

---

## 📊 Phần 3: Migration Dữ Liệu

### Script Python để migrate từ JSON sang CMS API

Tạo file `migrate_to_cms.py`:

```python
import json
import requests
import os
from datetime import datetime

# CMS Configuration
CMS_BASE_URL = "https://your-cms-domain.com/api"
API_KEY = "your_api_key_here"  # Lấy từ Settings → API Keys

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def migrate_users(data):
    """Migrate users từ _accounts và _profiles"""
    accounts = data.get("_accounts", {})
    profiles = data.get("_profiles", {})
  
    for username, password in accounts.items():
        profile = profiles.get(username, {})
        user_data = {
            "username": username,
            "password": password,  # CMS sẽ tự hash
            "email": profile.get("email", f"{username}@thapsang.local"),
            "full_name": profile.get("full_name", ""),
            "display_name": profile.get("displayName", username),
            "bio": profile.get("bio", ""),
            "avatar": profile.get("avatar", ""),
            "banner": profile.get("banner", ""),
            "following_list": profile.get("following_list", []),
            "onboarded": bool(profile.get("onboarding")),
            "onboarding_data": profile.get("onboarding")
        }
      
        response = requests.post(
            f"{CMS_BASE_URL}/users",
            headers=HEADERS,
            json=user_data
        )
        print(f"Migrated user: {username} - Status: {response.status_code}")
```

def migrate_diary_entries(data):
    """Migrate diary entries từ _diaries"""
    diaries = data.get("_diaries", {})

    for username, entries in diaries.items():
        # Lấy user_id từ CMS
        user_response = requests.get(
            f"{CMS_BASE_URL}/users?filter[username][_eq]={username}",
            headers=HEADERS
        )
        if user_response.status_code != 200:
            continue
        users = user_response.json().get("data", [])
        if not users:
            continue
        user_id = users[0]["id"]

    for entry in entries:
            entry_data = {
                "user_id": user_id,
                "username": username,
                "title": entry.get("title", ""),
                "content": entry.get("content", ""),
                "mood": entry.get("mood", "Calm"),
                "folder": entry.get("folder", ""),
                "ai_insight": entry.get("ai_insight", ""),
                "date": entry.get("date", datetime.now().isoformat())
            }

    response = requests.post(
                f"{CMS_BASE_URL}/diary_entries",
                headers=HEADERS,
                json=entry_data
            )
            print(f"Migrated diary: {entry.get('title')} - Status: {response.status_code}")

def migrate_aoa_posts(aoa_data):
    """Migrate AOA posts và comments"""
    posts = aoa_data.get("posts", [])

    for post in posts:
        # Lấy author_id
        author_name = post.get("author_name", "")
        user_response = requests.get(
            f"{CMS_BASE_URL}/users?filter[username][_eq]={author_name}",
            headers=HEADERS
        )
        if user_response.status_code != 200:
            continue
        users = user_response.json().get("data", [])
        if not users:
            continue
        author_id = users[0]["id"]

    post_data = {
            "author_id": author_id,
            "author_name": author_name,
            "author_avatar": post.get("author_avatar", ""),
            "content": post.get("content", ""),
            "graph_data": post.get("graph_data", {}),
            "likes": post.get("likes", 0),
            "shares": post.get("shares", 0),
            "timestamp": post.get("timestamp", datetime.now().isoformat())
        }

    response = requests.post(
            f"{CMS_BASE_URL}/aoa_posts",
            headers=HEADERS,
            json=post_data
        )

    if response.status_code == 200:
            post_id = response.json()["data"]["id"]
            print(f"Migrated post: {post_id}")

    # Migrate comments
            for comment in post.get("comments", []):
                comment_data = {
                    "post_id": post_id,
                    "author_id": author_id,  # Cần lookup thực tế
                    "author_name": comment.get("author_name", ""),
                    "author_avatar": comment.get("author_avatar", ""),
                    "content": comment.get("content", ""),
                    "timestamp": comment.get("timestamp", datetime.now().isoformat())
                }
                requests.post(
                    f"{CMS_BASE_URL}/aoa_comments",
                    headers=HEADERS,
                    json=comment_data
                )

# Main migration

if __name__ == "__main__":
    thapsang_data = load_json("../database/thapsang_db.json")
    aoa_data = load_json("../database/aoa_db.json")
    cohort_data = load_json("../database/cohort_db.json")

    print("Starting migration...")
    migrate_users(thapsang_data)
    migrate_diary_entries(thapsang_data)
    migrate_aoa_posts(aoa_data)
    print("Migration completed!")

```


---

## 🔑 Phần 4: Tạo API Keys & Cấu Hình

### Bước 1: Tạo API Key

1. Vào **Settings** → **API Keys**
2. Click **+ Add API Key**
3. Điền thông tin:
   - **Name**: `thapsang_production`
   - **Role**: `admin` (toàn quyền CRUD)
   - **Expiration**: `Never`
4. Click **Save** và **Copy** token ngay lập tức
5. Lưu token vào file `.env`:

```env
CMS_API_KEY=your_copied_token_here
CMS_BASE_URL=https://your-cms-domain.com/api
OPENAI_API_KEY=your_openai_key
LLM_BASE_URL=https://llmapi.digiforce.vn/v1
LLM_MODEL=thapsang
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Bước 2: Cấu hình Environment Variables trong CMS

1. Vào **Settings** → **Environment Config**
2. Thêm các biến:

| Name               | Type       | Value                          |
| ------------------ | ---------- | ------------------------------ |
| `openai_api_key` | Encrypted  | (API key của OpenAI)          |
| `smtp_user`      | Plain text | (Gmail address)                |
| `smtp_password`  | Encrypted  | (Gmail app password)           |
| `llm_base_url`   | Plain text | https://llmapi.digiforce.vn/v1 |
| `llm_model`      | Plain text | thapsang                       |

---

## 🌐 Phần 5: API Endpoints Mapping

### 5.1. Authentication APIs

| Endpoint Cũ (FastAPI)                   | Endpoint Mới (CMS)                             | Method | Description        |
| ---------------------------------------- | ----------------------------------------------- | ------ | ------------------ |
| `POST /api/v1/auth/login`              | `POST /auth/login`                            | POST   | Đăng nhập       |
| `POST /api/v1/auth/register`           | `POST /users`                                 | POST   | Đăng ký         |
| `POST /api/v1/auth/request-otp`        | Custom Flow                                     | POST   | Gửi OTP           |
| `GET /api/v1/auth/profile/{username}`  | `GET /users?filter[username][_eq]={username}` | GET    | Lấy profile       |
| `POST /api/v1/auth/profile/{username}` | `PATCH /users/{id}`                           | PATCH  | Cập nhật profile |

### 5.2. Diary APIs

| Endpoint Cũ                                       | Endpoint Mới                                           | Method | Description           |
| -------------------------------------------------- | ------------------------------------------------------- | ------ | --------------------- |
| `GET /api/v1/diary/{username}`                   | `GET /diary_entries?filter[username][_eq]={username}` | GET    | Lấy danh sách diary |
| `POST /api/v1/diary/{username}`                  | `POST /diary_entries`                                 | POST   | Tạo diary mới       |
| `DELETE /api/v1/diary/{username}/{entry_id}`     | `DELETE /diary_entries/{id}`                          | DELETE | Xóa diary            |
| `GET /api/v1/diary/{username}/folders`           | `GET /diary_folders?filter[username][_eq]={username}` | GET    | Lấy folders          |
| `POST /api/v1/diary/{username}/folders`          | `POST /diary_folders`                                 | POST   | Tạo folder           |
| `DELETE /api/v1/diary/{username}/folders/{name}` | `DELETE /diary_folders/{id}`                          | DELETE | Xóa folder           |

### 5.3. AOA Feed APIs

| Endpoint Cũ                     | Endpoint Mới                                   | Method | Description   |
| -------------------------------- | ----------------------------------------------- | ------ | ------------- |
| `GET /api/v1/db/aoa`           | `GET /aoa_posts?sort=-created_at`             | GET    | Lấy feed     |
| `POST /api/v1/db/aoa`          | `POST /aoa_posts`                             | POST   | Tạo post     |
| `GET /aoa_posts/{id}/comments` | `GET /aoa_comments?filter[post_id][_eq]={id}` | GET    | Lấy comments |
| `POST /aoa_comments`           | `POST /aoa_comments`                          | POST   | Tạo comment  |

### 5.4. Tasks APIs

| Endpoint Cũ                   | Endpoint Mới                                   | Method | Description     |
| ------------------------------ | ----------------------------------------------- | ------ | --------------- |
| `GET /tasks?user={username}` | `GET /tasks?filter[username][_eq]={username}` | GET    | Lấy tasks      |
| `POST /tasks`                | `POST /tasks`                                 | POST   | Tạo task       |
| `PATCH /tasks/{id}`          | `PATCH /tasks/{id}`                           | PATCH  | Cập nhật task |
| `DELETE /tasks/{id}`         | `DELETE /tasks/{id}`                          | DELETE | Xóa task       |

### 5.5. Cohort APIs

| Endpoint Cũ                            | Endpoint Mới                                             | Method | Description         |
| --------------------------------------- | --------------------------------------------------------- | ------ | ------------------- |
| `GET /api/v1/cohort/members`          | `GET /cohort_members?filter[cohort_id][_eq]=cohort_04`  | GET    | Lấy members        |
| `GET /api/v1/cohort/syllabus`         | `GET /cohort_syllabus?filter[cohort_id][_eq]=cohort_04` | GET    | Lấy syllabus       |
| `POST /api/v1/cohort/member-progress` | `PATCH /cohort_members/{id}`                            | PATCH  | Cập nhật progress |

---

## 🔄 Phần 6: Chuyển Đổi Frontend API Calls

### Ví dụ: Chuyển đổi Login API

**Code cũ (FastAPI):**

```javascript
const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
});
const data = await response.json();
```

**Code mới (CMS):**

```javascript
const response = await fetch('https://your-cms.com/api/auth/login', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: JSON.stringify({ email: username, password })
});
const data = await response.json();
```

### Tạo API Wrapper Helper

Tạo file `frontend/api-helper.js`:

```javascript
const CMS_BASE_URL = 'https://your-cms.com/api';
const API_KEY = 'your_api_key';

const apiCall = async (endpoint, method = 'GET', body = null) => {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${API_KEY}`
        }
    };
  
    if (body) {
        options.body = JSON.stringify(body);
    }
  
    const response = await fetch(`${CMS_BASE_URL}${endpoint}`, options);
    return await response.json();
};

// Wrapper functions
const API = {
    // Users
    login: (username, password) => 
        apiCall('/auth/login', 'POST', { email: username, password }),
  
    getProfile: (username) => 
        apiCall(`/users?filter[username][_eq]=${username}`),
  
    updateProfile: (userId, data) => 
        apiCall(`/users/${userId}`, 'PATCH', data),
  
    // Diary
    getDiaries: (username) => 
        apiCall(`/diary_entries?filter[username][_eq]=${username}&sort=-date`),
  
    createDiary: (data) => 
        apiCall('/diary_entries', 'POST', data),
  
    deleteDiary: (id) => 
        apiCall(`/diary_entries/${id}`, 'DELETE'),
  
    // AOA
    getAOAPosts: () => 
        apiCall('/aoa_posts?sort=-created_at&limit=50'),
  
    createAOAPost: (data) => 
        apiCall('/aoa_posts', 'POST', data),
  
    getComments: (postId) => 
        apiCall(`/aoa_comments?filter[post_id][_eq]=${postId}`),
  
    createComment: (data) => 
        apiCall('/aoa_comments', 'POST', data),
  
    // Tasks
    getTasks: (username) => 
        apiCall(`/tasks?filter[username][_eq]=${username}`),
  
    createTask: (data) => 
        apiCall('/tasks', 'POST', data),
  
    updateTask: (id, data) => 
        apiCall(`/tasks/${id}`, 'PATCH', data),
  
    deleteTask: (id) => 
        apiCall(`/tasks/${id}`, 'DELETE')
};
```

---

## 🧪 Phần 7: Testing API với Swagger

### Bước 1: Truy cập Open API Specs

1. Vào **Settings** → **Open API Specs**
2. Chọn collection muốn test (ví dụ: `users`)

### Bước 2: Test CRUD Operations

#### Test 1: Create User (POST /users)

```json
{
  "username": "testuser",
  "password": "Test@123",
  "email": "test@thapsang.com",
  "display_name": "Test User",
  "bio": "Testing Thapsang deployment"
}
```

**Expected**: `200 OK` với `id` được tạo

#### Test 2: Read Users (GET /users)

```
GET /users?filter[username][_eq]=testuser
```

**Expected**: Trả về user vừa tạo

#### Test 3: Update User (PATCH /users/)

```json
{
  "bio": "Updated bio for testing",
  "avatar": "data:image/png;base64,..."
}
```

**Expected**: `200 OK` với dữ liệu đã cập nhật

#### Test 4: Delete User (DELETE /users/)

```
DELETE /users/{id}
```

**Expected**: `204 No Content`

---

## 🚀 Phần 8: Deployment Checklist

### Pre-Deployment

- [ ] Tạo đầy đủ 10 collections trong CMS
- [ ] Cấu hình đúng field types và validations
- [ ] Thiết lập relations giữa các bảng
- [ ] Tạo API Key với role `admin`
- [ ] Cấu hình Environment Variables
- [ ] Chạy migration script để import dữ liệu
- [ ] Test tất cả endpoints qua Swagger

### Frontend Migration

- [ ] Tạo file `api-helper.js` với wrapper functions
- [ ] Cập nhật tất cả `fetch()` calls trong:
  - [ ] `login.html`
  - [ ] `coach.html`
  - [ ] `diary.html`
  - [ ] `aoa.html`
  - [ ] `tasks.html`
  - [ ] `cohort.html`
  - [ ] `analytics.html`
- [ ] Thay đổi base URL từ `/api/v1` sang CMS URL
- [ ] Thêm Authorization header vào mọi request

### Backend Migration

- [ ] Giữ lại FastAPI backend cho AI processing (Coach, Retrospective)
- [ ] Chuyển database operations sang CMS API
- [ ] Cập nhật `main.py` để gọi CMS thay vì JSON files
- [ ] Thiết lập Webhook từ CMS về FastAPI (nếu cần)

### Testing

- [ ] Test đăng nhập/đăng ký
- [ ] Test tạo/sửa/xóa diary entries
- [ ] Test AOA feed và comments
- [ ] Test task board operations
- [ ] Test cohort progress tracking
- [ ] Test AI Coach integration
- [ ] Test analytics dashboard

### Production

- [ ] Deploy CMS lên production server
- [ ] Deploy FastAPI backend lên server
- [ ] Deploy frontend lên CDN/NGINX
- [ ] Cấu hình CORS cho CMS
- [ ] Thiết lập SSL certificates
- [ ] Backup database định kỳ
- [ ] Monitor API performance

---

## 📝 Phần 9: Lưu Ý Quan Trọng

### 1. Bảo Mật

- **KHÔNG** hardcode API Key trong frontend code
- Sử dụng environment variables hoặc server-side proxy
- Implement rate limiting trên CMS
- Enable HTTPS cho tất cả endpoints

### 2. Performance

- Sử dụng pagination cho danh sách lớn:
  ```
  GET /diary_entries?limit=20&offset=0
  ```
- Cache dữ liệu ít thay đổi (syllabus, user profiles)
- Optimize JSON field queries với filters

### 3. Data Consistency

- Luôn validate dữ liệu trước khi gửi lên CMS
- Xử lý lỗi network gracefully
- Implement retry logic cho failed requests
- Sync localStorage với CMS database

### 4. AI Integration

- FastAPI backend vẫn cần thiết cho:
  - AI Coach conversations
  - Socratic reflection generation
  - Cohort retrospective analysis
  - Mindset DNA calculation
- CMS chỉ lưu trữ dữ liệu, không xử lý AI logic

---

## 🔗 Tài Liệu Tham Khảo

- [ADMIN_GUIDE.md](./ADMIN_GUIDE.md) - Hướng dẫn sử dụng CMS
- [README.md](./README.md) - Tổng quan dự án Thapsang
- [USER_MANUAL.md](./USER_MANUAL.md) - Hướng dẫn người dùng
- [TEST_SCENARIOS.md](./TEST_SCENARIOS.md) - Kịch bản test

---

**Tác giả**: INNORIA Development Team
**Phiên bản**: 1.0.0
**Ngày cập nhật**: 2026-05-22
