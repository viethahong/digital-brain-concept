# 🧠 DIGITAL BRAIN — Emerald Edition

Hệ thống quản trị tri thức cá nhân (PKM) tự động hóa hoàn toàn, vận hành dựa trên kiến trúc **LLM-Wiki** và hệ sinh thái **FPT AI**. Bộ não này không chỉ lưu trữ, mà còn chủ động **tinh gọn, kết nối và phản biện** để biến dữ liệu thô thành trí tuệ thực thụ.

---

## 🏛️ KIẾN TRÚC 5 TRỤ CỘT (PILLARS)

Hệ thống tổ chức thông tin theo 5 folder logic để AI nhận diện bản sắc tri thức:

1.  **`01_knowledge` (Tri thức lõi)**: Các Framework, phương pháp luận độc quyền (vd: GAMES, 4T, 5E).
2.  **`02_principles` (Nguyên tắc)**: Ranh giới Đúng/Sai và các quy luật vận hành cuộc sống/công việc.
3.  **`03_philosophies` (Triết lý)**: Hệ thống niềm tin và nhân sinh quan cá nhân.
4.  **`04_relationships` (Mối quan hệ)**: Mạng lưới con người (Biết - Quen - Thân - Thương - Yêu).
5.  **`05_incubator` (Vườn ươm)**: Nơi chứa tri thức từ bên ngoài (Outside) như tóm tắt sách, nghiên cứu, đang chờ được "nội hóa".

---

## ⚡ CÁC TÍNH NĂNG ĐỘC QUYỀN

### 1. 🤖 FPT AI Fallback Chain
Hệ thống sử dụng chuỗi mô hình thông minh để đảm bảo tốc độ và chất lượng xử lý:
-   **Primary**: `Llama-3.3-70B-Instruct` (Xử lý tác vụ phức tạp, dệt link).
-   **Secondary**: `gemma-4-31B-it` (Tinh gọn, tóm tắt).
-   **Tertiary**: `gemma-4-26B-A4B-it` (Dự phòng ổn định).

### 2. ✂️ Hệ thống Tinh gọn (Condensation)
Tính năng tự động hóa việc rút gọn các file tài liệu dài dòng trong `Incubator` nhưng vẫn bảo toàn Frontmatter và các liên kết tri thức quan trọng.

### 3. 🕸️ Tự động Tái dệt (Knowledge Weaving)
AI chủ động đọc nội dung và tự động chèn các liên kết `[[Link]]` giữa các file wiki dựa trên ngữ cảnh, tạo nên một mạng lưới tri thức dày đặc giúp bạn dễ dàng liên tưởng.

### 4. 🔗 Liên kết ngược (Backlinks)
Khả năng "truy vết" kiến thức: Khi xem một trang, bạn sẽ thấy danh sách tất cả các trang khác đang tham chiếu đến nó (Linked Mentions), giúp hiểu rõ tầm ảnh hưởng của một ý tưởng.

### 5. 🏷️ Phân loại Inside vs Outside
Hệ thống tự động gắn nhãn:
-   **Type: Inside**: Tài sản trí tuệ gốc của bạn (Ưu tiên bảo vệ).
-   **Type: Outside**: Kiến thức tham khảo từ người khác (Để học tập).

---

## 🚀 QUY TRÌNH VẬN HÀNH (WORKFLOW)

1.  **Nạp (Ingest)**: Thả file vào `raw/`. Chạy `brain_batch_ingest.py` để AI tự động phân loại vào các Trụ cột.
2.  **Chuẩn hóa (Clean)**: AI tự động sửa lỗi format, thêm Frontmatter chuẩn qua `brain_cleaner.py`.
3.  **Đồng bộ (Sync)**: Chạy `brain_sync.py` để cập nhật bản đồ kiến thức (Knowledge Graph) và Backlinks.
4.  **Kết nối (Weave)**: Chạy `brain_weaver.py` để AI đan cài các mối liên hệ mới giữa bộ não cũ và kiến thức mới.

---

## 🌐 GIAO DIỆN TƯƠNG TÁC

-   **Dashboard (`index.html`)**: Tổng quan sức khỏe bộ não.
-   **Wiki Hub (`wiki_hub.html`)**: Thư viện tri thức được trình bày premium.
-   **Brain Room (`brain_room.html`)**: Không gian tương tác và "hỏi ngược" với AI.
-   **Knowledge Graph (`graph.html`)**: Bản đồ trực quan 3D các điểm chạm tri thức.

---

*Hệ điều hành được cấu hình và thực thi bởi **Antigravity AI**. Chúc bạn xây dựng được một bộ não số vĩ đại.*
