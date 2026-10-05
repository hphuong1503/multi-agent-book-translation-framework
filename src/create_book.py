#!/usr/bin/env python3
import os
import sys
import json
import shutil
import argparse
from utils import get_base_books_dir

def create_book(book_id, title_en, title_vi=None, pdf_path=None):
    books_dir = get_base_books_dir()
    target_dir = os.path.join(books_dir, book_id)
    
    if os.path.exists(target_dir):
        print(f"Warning: Directory '{target_dir}' already exists.")
    else:
        os.makedirs(target_dir, exist_ok=True)

    # Subdirectories
    subdirs = [
        "00_Glossary",
        "storage/extracted_src",
        "storage/extracted_chunks",
        "02_Draft_Translations",
        "03_Final_Edited",
        "04_Compiled_Book",
        "05_Publication_Formats",
        "assets/images"
    ]

    for sd in subdirs:
        os.makedirs(os.path.join(target_dir, sd), exist_ok=True)

    # Copy PDF if provided
    pdf_filename = "source.pdf"
    if pdf_path:
        if os.path.exists(pdf_path):
            shutil.copy(pdf_path, os.path.join(target_dir, pdf_filename))
            print(f"Copied PDF '{pdf_path}' -> '{target_dir}/{pdf_filename}'")
        else:
            print(f"Warning: Provided PDF path '{pdf_path}' does not exist.")

    # Create Glossary template
    glossary_path = os.path.join(target_dir, "00_Glossary", "Central_Glossary.md")
    if not os.path.exists(glossary_path):
        with open(glossary_path, "w", encoding="utf-8") as f:
            f.write(f"# Central Glossary: {title_en}\n\n| Thuật ngữ gốc (EN) | Thuật ngữ dịch (VI) | Ghi chú / Ngữ cảnh |\n| :--- | :--- | :--- |\n| | | |\n")

    # Create config.json
    output_basename = book_id.replace("-", "_").title() + "_Full"
    config = {
        "book_id": book_id,
        "title_en": title_en,
        "title_vi": title_vi or f"{title_en} (Bản Dịch Tiếng Việt)",
        "pdf_filename": pdf_filename,
        "output_basename": output_basename,
        "chapter_defs": [
            {"chapter": 0, "title": "Introduction", "start": 1, "end": 20, "part": "Part_0"}
        ],
        "parts": [
            {"id": "Part_0", "title": "Part 0: Introduction", "chapters": [0]}
        ],
        "chunk_defs": []
    }

    config_path = os.path.join(target_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    print(f"\n[SUCCESS] Successfully created book project: '{book_id}'")
    print(f"Path: {target_dir}")
    print(f"Config: {config_path}")
    print(f"Next step: Edit 'config.json' to define chapter page ranges, then run:")
    print(f"  python3 src/run_pipeline.py --book {book_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a new book translation project structure")
    parser.add_argument("--id", required=True, help="ID độc nhất của sách (ví dụ: clean_code)")
    parser.add_argument("--title", required=True, help="Tiêu đề gốc Tiếng Anh của sách")
    parser.add_argument("--title-vi", help="Tiêu đề dịch Tiếng Việt của sách")
    parser.add_argument("--pdf", help="Đường dẫn tới file PDF nguồn của sách")

    args = parser.parse_args()
    create_book(args.id, args.title, args.title_vi, args.pdf)
