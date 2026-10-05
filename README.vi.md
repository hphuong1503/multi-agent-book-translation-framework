[English](README.md) | **Tiếng Việt**

# Reusable Framework: Dịch Thuật Toàn Văn 100% & Xuất Bản Sách Đa Định Dạng (Multi-Agent System)

Framework tự động hóa quy trình **Dịch thuật Toàn văn 100% bằng hệ thống Multi-Agent song song**, **Hiệu đính**, **Nhúng sơ đồ** và **Xuất bản đa định dạng (HTML5, DOCX, EPUB3)** độc lập cho từng cuốn sách.

---

## ⚡ Prompt Kích Hoạt Nhanh (Multi-Agent One-Prompt Trigger)

Copy đoạn prompt ngắn gọn sau và gửi cho Antigravity để dịch bất kỳ cuốn sách mới nào:

```markdown
Kích hoạt Antigravity Multi-Agent Book Translation Framework để dịch cuốn sách sau:

- **Book ID**: <id_sach, vd: ddia>
- **Tên Tiếng Anh**: <Tên sách tiếng Anh>
- **Tên Tiếng Việt**: <Tên sách tiếng Việt>
- **Tác Giả**: <Tên tác giả>
- **File PDF**: <Đường dẫn file PDF, vd: ./source.pdf>

### Yêu cầu thực thi (Multi-Agent Workflow):
1. **Khởi tạo**: Chạy `python3 src/create_book.py <book_id> <pdf_path>` và bóc tách PDF (`src/extract_pdf.py`, `src/export_paragraph_chunks.py`).
2. **Multi-Agent Translation**: Điều phối nhiều Subagent chạy song song (`invoke_subagent`) để dịch toàn văn 100% từng chương (không tóm tắt, chuẩn thuật ngữ `00_Glossary/Central_Glossary.md`, lưu vào `02_Draft_Translations/`).
3. **Bìa & Hình ảnh**: Tạo bìa 2D Flat tối giản (nền trắng, tác giả & tên sách chuẩn) và trích xuất hình ảnh/sơ đồ từ PDF (`src/embed_images.py`, `src/clean_duplicate_figures.py`).
4. **Hiệu đính & Xuất bản**: Hợp nhất và kiểm tra số từ (`src/word_count_audit.py`), tự động xuất bản 3 định dạng tại `05_Publication_Formats/` (HTML5 Base64, DOCX, EPUB3 mục lục Tiếng Việt 100%) và chạy kiểm thử `src/verify_publications.py`.
```

---

## 📁 Cấu Trúc Thư Mục Hệ Thống Đa Sách (Multi-Book Layout)

Toàn bộ dữ liệu của từng cuốn sách được đóng gói cô lập trong thư mục `books/<book_id>/`:

```text
├── books/                                  # Thư mục chứa các dự án sách
│   ├── staff_engineer/                     # Dự án sách: The Staff Engineer
│   │   ├── config.json                     # Cấu hình riêng (PDF, mục lục, trang, Part)
│   │   ├── source.pdf                      # File PDF gốc của sách
│   │   ├── 00_Glossary/                    # Bảng thuật ngữ chuyên ngành chuẩn hóa
│   │   ├── storage/                        # Dữ liệu bóc tách JSON & Chunks
│   │   ├── 02_Draft_Translations/          # Các file Markdown bản dịch theo từng Phần/Chương
│   │   ├── 03_Final_Edited/                # Bản thảo hợp nhất theo từng Phần (Part I, Part II...)
│   │   ├── 04_Compiled_Book/               # Master Full Book Markdown
│   │   ├── 05_Publication_Formats/         # File xuất bản (HTML5, DOCX, EPUB3)
│   │   └── assets/images/                  # Hình ảnh/sơ đồ trích xuất từ sách này
│   └── <book_id_moi>/                      # Dự án sách mới
│       ├── config.json
│       └── source.pdf
├── prompts/                                # System Prompts dùng chung
│   └── TRIGGER_BOOK_PIPELINE.md            # Mẫu prompt kích hoạt Multi-Agent
└── src/                                    # Hệ thống mã nguồn xử lý tự động
    ├── utils.py                            # Quản lý đường dẫn & cấu hình sách
    ├── create_book.py                      # Tự động tạo khung dự án sách mới
    ├── extract_pdf.py                      # Bóc tách PDF sang JSON
    ├── export_paragraph_chunks.py          # Chia nhỏ đoạn văn bản
    ├── generate_cover.py                   # Tạo bìa sách đồ họa 2D phẳng
    ├── embed_images.py                     # Trích xuất và nhúng sơ đồ từ PDF
    ├── clean_duplicate_figures.py          # Dọn dẹp ô ảnh hỏng & caption trùng lặp
    ├── proofread_and_format.py             # Hiệu đính trình bày & chú thích
    ├── word_count_audit.py                 # Hợp nhất sách & kiểm thử số từ
    ├── generate_publications.py            # Xuất bản HTML5, DOCX, EPUB3
    ├── verify_publications.py              # Kiểm thử chất lượng xuất bản 100%
    └── run_pipeline.py                     # Pipeline tự động 1-click
```

---

## 🛠️ Cài Đặt Môi Trường (Installation)

### 1. Yêu cầu hệ thống:
- Python 3.10 trở lên
- Git

### 2. Thiết lập môi trường ảo:
```bash
# Clone repository
git clone https://github.com/hphuong1503/multi-agent-book-translation-framework.git
cd multi-agent-book-translation-framework

# Khởi tạo và kích hoạt virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

### 3. Hướng dẫn sử dụng CLI:
```bash
# 1. Tạo dự án sách mới:
python3 src/create_book.py --id <book_id> --title "<Tên Sách Tiếng Anh>" --title-vi "<Tên Sách Tiếng Việt>" --pdf path/to/source.pdf

# 2. Chạy pipeline toàn diện cho một cuốn sách:
python3 src/run_pipeline.py --book <book_id>

# 3. Kiểm thử chất lượng xuất bản:
python3 src/verify_publications.py --book <book_id>
python3 src/qa_audit.py --book <book_id>
```

---

## 📄 Bản Quyền & Giấy Phép (License)

Dự án này được phát hành dưới giấy phép [MIT License](LICENSE).  
Các tài liệu và file sách gốc (PDF) thuộc bản quyền của các tác giả và nhà xuất bản tương ứng.
