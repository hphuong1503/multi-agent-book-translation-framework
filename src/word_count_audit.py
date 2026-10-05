#!/usr/bin/env python3
import os
import json
import glob
import re
from utils import parse_book_arg, load_book_config, get_book_dir, get_book_subpath

def count_words(text):
    clean_text = re.sub(r'#+|[*_`~>|\-\+]', ' ', text)
    words = clean_text.split()
    return len(words)

def compile_parts_and_book(book_id):
    config = load_book_config(book_id)
    bdir = get_book_dir(book_id)

    draft_dir = os.path.join(bdir, "02_Draft_Translations")
    edited_dir = os.path.join(bdir, "03_Final_Edited")
    compiled_dir = os.path.join(bdir, "04_Compiled_Book")

    os.makedirs(edited_dir, exist_ok=True)
    os.makedirs(compiled_dir, exist_ok=True)

    parts_config = config.get("parts", [])
    output_basename = config.get("output_basename", f"{book_id.title()}_Full")

    compiled_part_contents = []

    for part_info in parts_config:
        part_id = part_info["id"]
        part_title = part_info["title"]
        chapters = part_info.get("chapters", [])

        part_md_files = []
        for chap_num in chapters:
            # Look in subdirectories of draft_dir or directly in draft_dir
            matching = glob.glob(os.path.join(draft_dir, "**", f"Chapter_{chap_num:02d}.md"), recursive=True) or \
                       glob.glob(os.path.join(draft_dir, "**", f"chap_{chap_num:02d}.md"), recursive=True)
            if matching:
                part_md_files.append(matching[0])

        part_content = []
        for fpath in sorted(part_md_files):
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    part_content.append(f.read().strip())

        if part_content:
            joined_part_md = "\n\n---\n\n".join(part_content)
            out_part_path = os.path.join(edited_dir, f"{part_id}.md")
            with open(out_part_path, "w", encoding="utf-8") as f:
                f.write(joined_part_md)

            compiled_part_contents.append(f"# {part_title}\n\n" + joined_part_md)

    # Master Full Book
    title_vi = config.get("title_vi", f"# {config.get('title_en', book_id)}")
    master_book_header = f"# {title_vi}\n\n"
    master_md = master_book_header + "\n\n" + "\n\n".join(compiled_part_contents)
    
    master_path = os.path.join(compiled_dir, f"{output_basename}.md")
    with open(master_path, "w", encoding="utf-8") as f:
        f.write(master_md)

    print(f"Compiled parts saved to '{edited_dir}/' and master book saved to '{master_path}'.")

def run_audit(book_id):
    config = load_book_config(book_id)
    extracted_dir = get_book_subpath(book_id, "storage", "extracted_src")
    draft_dir = get_book_subpath(book_id, "02_Draft_Translations")

    extracted_files = sorted(glob.glob(os.path.join(extracted_dir, "chapter_*.json")))
    
    print("\n" + "="*80)
    print(f"{'CHAPTER':<12} | {'ORIGINAL WORDS':<15} | {'TRANSLATED WORDS':<18} | {'RATIO (%)':<10} | {'STATUS':<10}")
    print("="*80)

    total_orig = 0
    total_trans = 0
    all_passed = True

    for ext_path in extracted_files:
        with open(ext_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        chap_num = data["chapter"]
        orig_words = data["word_count"]
        total_orig += orig_words

        # locate corresponding draft file
        draft_matches = glob.glob(os.path.join(draft_dir, "**", f"Chapter_{chap_num:02d}.md"), recursive=True) or \
                        glob.glob(os.path.join(draft_dir, "**", f"chap_{chap_num:02d}.md"), recursive=True)

        trans_words = 0
        if draft_matches and os.path.exists(draft_matches[0]):
            with open(draft_matches[0], "r", encoding="utf-8") as f:
                content = f.read()
            trans_words = count_words(content)

        total_trans += trans_words
        ratio = (trans_words / orig_words * 100) if orig_words > 0 else 0
        
        status = "PASSED"
        if ratio < 70:
            status = "FAIL (<70%)"
            all_passed = False
        elif ratio < 80 or ratio > 130:
            status = "WARNING"

        print(f"Chapter {chap_num:02d}    | {orig_words:<15} | {trans_words:<18} | {ratio:<9.1f}% | {status:<10}")

    overall_ratio = (total_trans / total_orig * 100) if total_orig > 0 else 0
    print("="*80)
    print(f"{'TOTAL':<12} | {total_orig:<15} | {total_trans:<18} | {overall_ratio:<9.1f}% | {'PASSED' if all_passed else 'NEEDS EXPANSION'}")
    print("="*80 + "\n")

    return all_passed

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 4: Word Count Audit & Book Compilation")
    compile_parts_and_book(book_id)
    run_audit(book_id)
