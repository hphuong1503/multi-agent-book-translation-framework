#!/usr/bin/env python3
import os
import sys
import json
import glob
import argparse
from utils import parse_book_arg, load_book_config, get_book_dir, get_book_subpath

def show_status(book_id):
    config = load_book_config(book_id)
    extracted_dir = get_book_subpath(book_id, "storage", "extracted_src")
    draft_dir = get_book_subpath(book_id, "02_Draft_Translations")

    extracted_files = sorted(glob.glob(os.path.join(extracted_dir, "chapter_*.json")))
    
    print("\n" + "="*80)
    print(f"TRẠNG THÁI TIẾN ĐỘ DỊCH THUẬT (ANTIGRAVITY AGENT) - SÁCH [{book_id.upper()}]")
    print("="*80)
    print(f"{'CHAPTER':<10} | {'ORIG PARAS':<12} | {'ORIG WORDS':<12} | {'DRAFT FILE':<30} | {'STATUS'}")
    print("-"*80)

    for ext_path in extracted_files:
        with open(ext_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        chap_num = data["chapter"]
        orig_paras = len(data["paragraphs"])
        orig_words = data["word_count"]

        draft_matches = glob.glob(os.path.join(draft_dir, "**", f"Chapter_{chap_num:02d}.md"), recursive=True) or \
                        glob.glob(os.path.join(draft_dir, "**", f"chap_{chap_num:02d}.md"), recursive=True)

        if draft_matches and os.path.exists(draft_matches[0]):
            rel_draft = os.path.relpath(draft_matches[0], get_book_dir(book_id))
            status = "DONE (Bản dịch tồn tại)"
        else:
            rel_draft = f"Chưa có (Cần dịch)"
            status = "PENDING (Đang chờ dịch)"

        print(f"Chapter {chap_num:02d} | {orig_paras:<12} | {orig_words:<12} | {rel_draft:<30} | {status}")

    print("="*80 + "\n")

def get_chapter_source(book_id, chap_num):
    extracted_dir = get_book_subpath(book_id, "storage", "extracted_src")
    chap_file = os.path.join(extracted_dir, f"chapter_{chap_num:02d}.json")
    
    if not os.path.exists(chap_file):
        print(f"Error: Chapter file '{chap_file}' not found.")
        sys.exit(1)

    with open(chap_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n--- DANH SÁCH ĐOẠN VĂN NGUỒN CHAPTER {chap_num:02d}: '{data['title']}' ---")
    print(f"Tổng số đoạn: {len(data['paragraphs'])}, Tổng số từ: {data['word_count']}\n")
    print(json.dumps(data, ensure_ascii=False, indent=2))

def save_draft_chapter(book_id, chap_num, part_name, md_content):
    draft_dir = get_book_subpath(book_id, "02_Draft_Translations", part_name)
    os.makedirs(draft_dir, exist_ok=True)
    
    out_path = os.path.join(draft_dir, f"Chapter_{chap_num:02d}.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[SUCCESS] Saved draft translation for Chapter {chap_num:02d} -> '{out_path}'")

def main():
    parser = argparse.ArgumentParser(description="Antigravity Agent Translation Helper Utility")
    parser.add_argument("--book", "-b", type=str, help="ID của cuốn sách (ví dụ: staff_engineer)")
    parser.add_argument("--status", action="store_true", help="Hiển thị bảng tiến độ dịch từng chương")
    parser.add_argument("--get-chapter", type=int, help="Lấy dữ liệu nguồn JSON của chương N")
    parser.add_argument("--save-chapter", type=int, help="Lưu bản dịch Markdown cho chương N")
    parser.add_argument("--part", type=str, default="Part_I", help="Tên thư mục Part (ví dụ: Part_I, Part_II)")
    parser.add_argument("--content-file", type=str, help="Đường dẫn file chứa nội dung Markdown cần lưu")

    args = parser.parse_args()
    book_id = parse_book_arg("Antigravity Agent Translation Helper")

    if args.status:
        show_status(book_id)
    elif args.get_chapter is not None:
        get_chapter_source(book_id, args.get_chapter)
    elif args.save_chapter is not None and args.content_file:
        with open(args.content_file, "r", encoding="utf-8") as f:
            content = f.read()
        save_draft_chapter(book_id, args.save_chapter, args.part, content)
    else:
        show_status(book_id)

if __name__ == "__main__":
    main()
