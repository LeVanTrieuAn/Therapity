# Hướng Dẫn Quản Trị Hệ Thống

---

## 1. Quản lý Datasource & Cấu trúc Collection (Bảng dữ liệu)

Hệ thống sử dụng kiến trúc **Headless CMS / Low-code DB engine**. Khi thao tác trên giao diện, hệ thống sẽ tự động map (ánh xạ) trực tiếp xuống cơ sở dữ liệu bên dưới để thay đổi schema mà không cần viết lệnh `SQL ALTER TABLE`.

### Bước 1: Truy cập cấu hình hệ thống

* Click vào avatar **Admin** ở góc phải màn hình **$\rightarrow$** Chọn **Settings** (Cài đặt) để mở menu root quản trị hệ thống.
* Click vào thẻ **Datasources** (Nguồn dữ liệu). Tại đây bạn sẽ thấy danh sách các bảng (Collections) đang có sẵn trong database như `roles`, `users`, `tasks`...

### Bước 2: Thiết lập Schema (Cấu hình trường dữ liệu)

Chọn bảng `tasks` (Công việc) và click vào **Configure fields** để bắt đầu định nghĩa các thuộc tính. Hệ thống cung cấp cơ chế kéo thả và chọn kiểu dữ liệu rất trực quan:

* **Tạo trường văn bản dài (Long text) cho `description` (Mô tả):**
  * Click **+ Add field** **$\rightarrow$** Chọn **Long text** tại ô  *Field interface* . Kiểu này tương đương với kiểu `TEXT` hoặc `LONGTEXT` trong database, cho phép lưu trữ đoạn văn dài.
  * *Field display name* (Tên hiển thị trên giao diện): Nhập `Description`.
  * *Field name* (Tên cột chuẩn hóa trong DB): Nhập `description` (viết thường, không dấu, không khoảng trắng).
  * Click  **Save** .
* **Tạo trường lựa chọn (Single select) cho `status` (Trạng thái):**
  * Click **+ Add field** **$\rightarrow$** Chọn **Single select** (Tương đương kiểu `ENUM` trong cơ sở dữ liệu).
  * Định nghĩa tên trường là `Status` và `status`.
  * Tại cấu hình **Options** (Các giá trị hợp lệ), bạn thiết lập các "Option value" (giá trị lưu vào DB) và "Option label" (nhãn hiển thị màu sắc trên UI):
    * Thêm Option 1: Value = `done`, Label = `Done` (Chọn tag màu xanh lá - Green).
    * Thêm Option 2: Value = `pending`, Label = `Pending` (Chọn tag màu vàng - Gold).
    * Thêm Option 3: Value = `new`, Label = `New` (Chọn tag màu xám - Default).
  * Điền `new` vào ô **Default value** (Giá trị mặc định). Nghĩa là bất kỳ khi nào có một task mới được tạo mà không truyền trạng thái, hệ thống sẽ tự gán nó là `new`. Click  **Save** .

### Bước 3: Đưa dữ liệu ra giao diện người dùng (UI)

Sau khi cấu hình DB xong, các trường này chưa tự động xuất hiện trên màn hình quản lý công việc.

1. Quay lại màn hình danh sách **tasks**.
2. Click vào nút **Fields** ở góc phải bảng.
3. Bật công tắc (**Toggle ON**) cho hai mục **Description** và **Status** để hệ thống render thêm cột trên giao diện.

---

## 2. Quản lý Người dùng (User Management) & Luồng công việc (Workflow)

### User Management (Quản lý phân quyền người dùng)

Nằm tại mục **Users Management** trong Settings. Đây là nơi quản trị áp dụng mô hình  **RBAC (Role-Based Access Control)** :

* **Tạo tài khoản / Thêm User:** Quản trị viên nhập thông tin Email, Username, Mật khẩu để cấp tài khoản cho nhân viên/thành viên dự án.
* **Gán vai trò (Roles):** Mỗi user sẽ thuộc về một hoặc nhiều nhóm quyền (ví dụ: `admin` - toàn quyền, `root` - quyền tối cao hệ thống, `user` - chỉ xem/sửa dữ liệu được giao). Quyền hạn này quyết định việc User đó có thể gọi các API nào ở bước sau.

### Workflow (Quản lý luồng công việc)

Nằm tại mục **Workflow** trong Settings. Công cụ này đóng vai trò tự động hóa quy trình (Automation):

* Bạn có thể thiết lập các hàm Trigger (Kích hoạt). Ví dụ: *Khi trường `status` của một dòng trong bảng `tasks` thay đổi thành `done`* **$\rightarrow$** Hệ thống tự động kích hoạt một Webhook gửi tín hiệu về Discord/Telegram của nhóm, hoặc tự động cập nhật ngày hoàn thành ở một bảng khác.

## 3. Tạo API Keys & Cấu hình Môi trường (Environment Config)

Hệ thống của bạn sử dụng cơ chế bảo mật bằng **API Key mã hóa (Token-based)** để bảo vệ các endpoint, chặn các truy cập trái phép từ bên ngoài.

### Cách tạo và lưu trữ API Key:

1. Vào **Settings** **$\rightarrow$** Chọn  **API Keys** .
2. Click  **+ Add API Key** .
3. Điền tên định danh Key (ví dụ: `admin_integration`), chọn **Role** là `admin` (để Key này thừa hưởng toàn bộ quyền đọc/ghi dữ liệu của Admin) và chọn **Expiration** là **Never** (Không bao giờ hết hạn).
4. Nhấn  **Save** . Lúc này hệ thống sẽ hiển thị một pop-up chứa chuỗi mã hóa Token rất dài (Dạng JWT).
5. **QUAN TRỌNG:** Bạn phải click nút **Copy** để sao chép chuỗi này ngay lập tức và lưu vào một file text bảo mật. Hệ thống chỉ hiển thị chuỗi này **duy nhất một lần** vì lý do an toàn. Nếu bạn tắt cửa sổ, bạn sẽ không thể xem lại mã này nữa mà buộc phải xóa đi tạo cái mới.

### Cách cấu hình biến Môi trường (Environment Config)

Mục này đóng vai trò như một file `.env` tập trung của hệ thống, giúp bạn truyền các thông số cấu hình một cách bảo mật mà không cần can thiệp vào mã nguồn code backend.

1. Vào **Settings** **$\rightarrow$** Chọn  **Environment Config** .
2. Click  **+ Add variable** .
3. Ô  **Name** : Nhập tên biến đại diện (Ví dụ: `api_key`).
4. Ô  **Type** : Chọn **Plain text** hoặc **Encrypted** (Mã hóa).
5. Ô  **Value** : Dán toàn bộ chuỗi API Key bạn vừa copy ở bước trên vào đây **$\rightarrow$** Nhấn  **Save** .

---

## 4. Kiểm thử API (API Testing) qua Swagger & Postman

Hệ thống cung cấp một môi trường thử nghiệm API chuẩn hóa (giao diện Open API/Swagger) giúp lập trình viên test nhanh các chức năng CRUD (Create - Read - Update - Delete) của bảng dữ liệu mà không cần viết code frontend.

### Thao tác Test các API của bảng `tasks`

Vào mục **Open API Specs** → Chọn cấu hình bảng `tasks`. Hệ thống tự động sinh ra các endpoint:

| Phương thức HTTP | Endpoint        | Chức năng                                                  | Kết quả                                                                                                                                                                    |
| ------------------- | --------------- | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `POST`            | `/tasks`      | **Create** — Tạo mới một công việc vào bảng    | Truyền Body JSON → Trả về `200 OK` kèm `"id": "2026..."` (định danh duy nhất)                                                                                    |
| `GET`             | `/tasks`      | **Read List** — Lấy toàn bộ danh sách công việc | Trả về mảng JSON tất cả các task đã tạo                                                                                                                             |
| `PUT` / `PATCH` | `/tasks/{id}` | **Update** — Chỉnh sửa task cụ thể qua ID         | Truyền ID vào URL, thay đổi thuộc tính → Trả về `200 OK`                                                                                                          |
| `DELETE`          | `/tasks/{id}` | **Delete** — Xóa hoàn toàn task khỏi database     | Truyền ID của task cần xóa**$\rightarrow$** Hệ thống thực thi lệnh xóa, khi quay lại bảng `tasks` ngoài UI, dòng dữ liệu đó sẽ biến mất hoàn toàn. |
