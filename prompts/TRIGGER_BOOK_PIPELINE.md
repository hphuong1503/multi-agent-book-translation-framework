# Prompt Kích Hoạt Dịch Sách Tự Động (Multi-Agent Pipeline)

Sao chép prompt dưới đây để bắt đầu dịch bất kỳ cuốn sách mới nào với hệ thống Multi-Agent của Antigravity:

---

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
