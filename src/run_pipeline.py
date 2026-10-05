#!/usr/bin/env python3
import os
import sys
import argparse
import subprocess
from utils import list_available_books

def run_step(cmd_args, description):
    print("\n" + "="*80)
    print(f"STEP: {description}")
    print(f"COMMAND: {' '.join(cmd_args)}")
    print("="*80)
    res = subprocess.run(cmd_args)
    if res.returncode != 0:
        print(f"Error executing step: {description}")
        return False
    return True

def run_pipeline_for_book(book_id):
    print(f"""
    ===================================================================
    FRAMEWORK DỊCH THUẬT TOÀN VĂN & XUẤT BẢN - SÁCH [{book_id.upper()}]
    ===================================================================
    """)
    
    python_bin = sys.executable

    steps = [
        ([python_bin, "src/extract_pdf.py", "--book", book_id], f"Phase 1: Extraction - Bóc tách PDF sang JSON [{book_id}]"),
        ([python_bin, "src/export_paragraph_chunks.py", "--book", book_id], f"Phase 1: Chunking - Chia nhỏ các đoạn văn [{book_id}]"),
        ([python_bin, "src/clean_footnotes_and_html.py", "--book", book_id], f"Phase 2: Cleaning - Loại bỏ thẻ HTML rác & mã hóa chú thích [{book_id}]"),
        ([python_bin, "src/generate_cover.py", "--book", book_id], f"Phase 3: Cover Design - Kiểm tra & Tạo bìa sách [{book_id}]"),
        ([python_bin, "src/embed_images.py", "--book", book_id], f"Phase 3: Image Embedding - Trích xuất & Nhúng sơ đồ vào Markdown [{book_id}]"),
        ([python_bin, "src/clean_duplicate_figures.py", "--book", book_id], f"Phase 3: Figure Clean - Chuẩn hóa & loại bỏ trùng lặp hình ảnh [{book_id}]"),
        ([python_bin, "src/proofread_and_format.py", "--book", book_id], f"Phase 4: Proofreading - Hiệu đính định dạng văn bản [{book_id}]"),
        ([python_bin, "src/word_count_audit.py", "--book", book_id], f"Phase 4: Audit & Compilation - Hợp nhất sách & Kiểm thử số từ [{book_id}]"),
        ([python_bin, "src/generate_publications.py", "--book", book_id], f"Phase 5: Publishing - Tạo file HTML5, DOCX, EPUB3 với bìa sách [{book_id}]"),
        ([python_bin, "src/verify_publications.py", "--book", book_id], f"Phase 5: Verification - Kiểm thử chất lượng file xuất bản [{book_id}]"),
        ([python_bin, "src/qa_audit.py", "--book", book_id], f"Phase 5: QA Audit - Quét lỗi chưa dịch & đối chiếu tỷ lệ từ [{book_id}]"),
    ]

    for cmd, desc in steps:
        ok = run_step(cmd, desc)
        if not ok:
            print(f"\n[FAIL] Quy trình bị dừng tại bước: {desc}")
            return False

    print("\n" + "="*80)
    print(f" [SUCCESS] TOÀN BỘ QUY TRÌNH DỊCH THUẬT VÀ XUẤT BẢN ĐÃ HOÀN TẤT 100% CHO [{book_id.upper()}]!")
    print("="*80 + "\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="Chạy Pipeline Dịch thuật & Xuất bản cho Đa Sách")
    parser.add_argument("--book", "-b", type=str, help="ID của cuốn sách (ví dụ: staff_engineer)")
    parser.add_argument("--all", action="store_true", help="Chạy pipeline cho tất cả các sách")
    
    args = parser.parse_args()
    available_books = list_available_books()

    if not available_books:
        print("Error: No books found in 'books/' directory.")
        sys.exit(1)

    if args.all:
        print(f"Running pipeline for ALL available books: {', '.join(available_books)}")
        for b in available_books:
            ok = run_pipeline_for_book(b)
            if not ok:
                sys.exit(1)
        print("\n🎉 ALL BOOKS PROCESSED SUCCESSFULLY!")
        return

    book_id = args.book
    if not book_id:
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            book_id = sys.argv[1]
        elif len(available_books) == 1:
            book_id = available_books[0]
        else:
            print("DANH SÁCH DỰ ÁN SÁCH HIỆN CÓ:")
            for idx, b in enumerate(available_books, 1):
                print(f"  {idx}. {b}")
            print("\nVui lòng chỉ định sách bằng cách dùng tham số `--book <book_id>`")
            print("Ví dụ: python3 src/run_pipeline.py --book staff_engineer")
            sys.exit(0)

    if book_id not in available_books:
        print(f"Error: Book '{book_id}' not found. Available books: {', '.join(available_books)}")
        sys.exit(1)

    ok = run_pipeline_for_book(book_id)
    if not ok:
        sys.exit(1)

if __name__ == "__main__":
    main()
