# CLAUDE.md - DIGITAL BRAIN OPERATING SYSTEM

Hệ điều hành cho Bộ não số (Digital Brain) dựa trên 5 Trụ cột và kiến trúc LLM-Wiki.

## 🧠 6 TRỤ CỘT CỐT LÕI (6 PILLARS)

1. **Knowledge (Tri thức sống):** `/wiki/01_knowledge/`
   - Phân loại theo 5 cấp độ nhận thức: `1_Biet`, `2_Hieu`, `3_Hanh`, `4_Thong`, `5_Tue`.
2. **Principles (Nguyên tắc sống):** `/wiki/02_principles/`
   - La bàn ranh giới Đúng/Sai (Đạo đức, Pháp luật, Quan điểm).
3. **Philosophies (Triết lý sống):** `/wiki/03_philosophies/`
   - Hệ thống Niềm tin (Đức tin, Quan điểm cốt lõi, không có đúng-sai).
4. **Relationships (Mối quan hệ):** `/wiki/04_relationships/`
   - Cấu trúc theo khung **5W1H** (Who, What, Where, When, Why, How).
   - Phân loại theo 4 cấp độ: `1_Biet`, `2_Quen`, `3_Thuong`, `4_Yeu`.
5. **Incubator (Vùng ủ mầm):** `/wiki/05_incubator/`
   - Nơi chứa Tri thức vay mượn (Outside Knowledge). Chờ được hấp thụ vào Inside khi có trải nghiệm thực tế.
6. **Raw Data & Ideas:** `/raw/`
   - `/raw/inside/`: Nơi thu nhận trải nghiệm sống, lời kể trực tiếp của bạn.
   - `/raw/outside/`: Nơi chứa thông tin bên ngoài (sách, video...) để chuẩn bị chưng cất vào Incubator.

---

## ⚙️ CƠ CHẾ VẬN HÀNH (OPERATIONS)

### 1. Ingest (Nạp tri thức & Hỏi ngược)
Khi người dùng nạp dữ liệu vào `/raw/` hoặc qua chat:
- Tri thức Outside -> Chưng cất lưu vào `/wiki/05_incubator/`.
- Tri thức Inside -> Hỏi ngược khai thác, sau đó chưng cất vào các trụ cột 01-04 lõi.
- **Merge Logic (Auto):** NẾU tri thức Inside mới nhập CÓ LIÊN QUAN tới 1 file đang ủ trong `05_incubator`, AI gợi ý di chuyển hẳn file sang Inside.
- **Learn Workflow (Flashcard):** Truy cập `learn.html`. Lật thẻ để tìm "Inside Anchors". Nhập chiêm nghiệm cá nhân để "neo" tri thức. Nhấn **Promote** để thực hiện lệnh chuyển trụ cột.
- **KHÔNG CHỈ TÓM TẮT:** AI phải chủ động đặt câu hỏi ngược để khai thác sâu hơn thông tin dựa trên khung 5W1H và 5 cấp độ kiến thức.
- **Exploration Logic (Gợi mở thông minh):** Sau mỗi lần người dùng cung cấp thông tin, AI dựa trên nội dung đó để chọn 1-2 câu hỏi "đào sâu" nhất để hỏi lại. Tránh hỏi dồn dập.

### 2. Bộ câu hỏi Khai thác (Exploration Framework)
- **Kiến thức:** "Bạn đã thực hành điều này chưa? Lần đầu tiên làm nó, bạn cảm thấy thế nào? Bạn thấy mô thức (pattern) nào lặp lại ở đây?"
- **Mối quan hệ (5W1H):** "Kỷ niệm/Câu chuyện đáng nhớ nhất giữa bạn và thực thể này là gì? Tại sao mối quan hệ này lại quan trọng với bạn? Nó khiến bạn thay đổi cách nhìn gì về cuộc sống?"
- **Nguyên tắc:** "Tại sao bạn coi đây là ranh giới không thể bước qua? Đã bao giờ bạn định phá vỡ nó chưa?"
- **Triết lý:** "Niềm tin này hình thành từ đâu? Nếu ngày mai nó không còn đúng, thế giới của bạn sẽ thế nào?"

### 3. Networking (Sự kết nối)
- Mọi trang wiki mới phải có mục **"Networking"** ở cuối file.
- Tìm kiếm các khái niệm liên quan trong 5 trụ cột để tạo liên kết `[[wikilink]]`.
- Dùng **Câu chuyện** làm sợi dây liên kết chính.

### 3. Weighting & Forgetting (Trọng số & Lưu trữ)
- Mỗi file bắt buộc có Frontmatter:
```yaml
---
pillar: [Knowledge | Principle | Philosophy | Relationship]
level: [1-5]
weight: 1.0 # 0.0 - 1.0
last_interaction: YYYY-MM-DD
---
```
- Khi `Lint`: Giảm trọng số của các file lâu không tương tác. Tăng trọng số cho các file thường xuyên được nhắc đến.

---

## 🎨 DESIGN SPEC (Emerald Green)
- Giao diện Dashboard (`index.html`) sử dụng tông màu **Xanh Emerald (#50C878)**.
- Dark mode mặc định, hiệu ứng Glassmorphism.
- Các thẻ (cards) hiển thị 5 trụ cột theo dạng Bento Grid.

---

## 🛠️ LỆNH QUẢN TRỊ (CLI)
- `Ingest`: Đọc file trong `raw/`, phân loại Inside/Outside, hỏi ngược người dùng, sau đó biên tập vào `wiki/` hoặc `incubator/`.
- `Query`: Tra cứu tri thức từ 6 trụ cột, ưu tiên kết nối chéo giữa Inside và Outside.
- `Learn`: Truy cập `learn.html` để rèn luyện kết nối tri thức. 
    - **Yêu cầu**: Chạy `python3 brain_server.py` để kích hoạt tính năng thăng cấp (Promote) tự động.
- `Lint`: Kiểm tra liên kết đứt gãy, cập nhật trọng số và gợi ý "quên" các thông tin rác.
