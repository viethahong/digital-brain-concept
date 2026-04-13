# 🧠 DIGITAL BRAIN — Emerald Edition

Hệ thống ghi chép và tự động tổ chức tri thức cá nhân theo kiến trúc **LLM-Wiki** của Andrej Karpathy, được tùy chỉnh sâu sắc cho tư duy **5 Trụ cột cốt lõi**, bổ sung thêm về chức năng học tập phát triển từ những vùng tri thức mới.

---

## 🏛️ 5 TRỤ CỘT (PILLARS)

### 📊 TRI THỨC SỐNG (KNOWLEDGE)
- **Cấu trúc:** `#level/1_biet` (Biết), `#level/2_hieu` (Hiểu), `#level/3_hanh` (Hành), `#level/4_thong` (Thông), `#level/5_tue` (Tuệ).
- AI sẽ liên tục hỏi bạn về quá trình thực hành để nâng cấp tri thức.

### ⚖️ NGUYÊN TẮC SỐNG (PRINCIPLES)
- Ranh giới Đúng/Sai (Đạo đức, Pháp luật, Quan điểm cá nhân).

### 🧘 TRIẾT LÝ SỐNG (PHILOSOPHIES)
- Hệ thống Niềm tin, không có Đúng/Sai.

### 🤝 MỐI QUAN HỆ (RELATIONSHIPS)
- Cấu trúc: **5W1H** (Who, What, Where, When, Why, How).
- Cấp độ: `Biết` -> `Quen` -> `Thương` -> `Yêu`.

### 🧪 DỮ LIỆU THÔ (RAW DATA)
- Nơi thả các ý tưởng, transcript, bài báo chưa phân loại.

---

## ⚙️ CƠ CHẾ "HỎI NGƯỢC" (ASKING BACK)

Bộ não số này **không chỉ là nơi bạn nạp dữ liệu**. Khi bạn nạp một thông tin mới:
1. AI sẽ đọc và phân loại vào 1 trong 5 trụ cột.
2. AI sẽ chủ động **đặt câu hỏi gợi mở** (từ 1-2 câu) để khai thác sâu hơn.
3. Nếu là Mối quan hệ, AI sẽ hỏi về **Câu chuyện**. Nếu là Tri thức, AI sẽ hỏi về **Hành động**.

### Cách kích hoạt:
- **Chủ động:** "Hãy dùng bộ khung 5W1H để phỏng vấn tôi về dự án này."
- **Tự động:** Chỉ cần kể một mẩu chuyện, AI sẽ tự chọn câu hỏi phù hợp nhất từ [Exploration Framework](/wiki/templates/exploration-framework.md) để hỏi lại bạn.

---

## 🚀 CÁCH SỬ DỤNG

1. **Giao diện Dashboard:** Mở file `index.html` bằng trình duyệt để xem tình trạng bộ não và các "Magic Chips" gợi ý.
2. **Nạp tri thức:** "Hãy ingest file [tên file] trong raw" hoặc "Hãy lắng nghe tâm sự của tôi và hỏi ngược lại để xây dựng wiki".
3. **Tra cứu:** "Dùng 5 trụ cột để tư vấn cho tôi về vấn đề [vấn đề cụ thể]".
4. **Bảo trì:** "Hãy lint hệ thống, tìm các trang đang bị 'quên' (trọng số thấp) và nhắc lại cho tôi".

---

*Hệ điều hành được cấu hình trong `CLAUDE.md`. Chúc bạn xây dựng được một bộ não số vĩ đại.*
