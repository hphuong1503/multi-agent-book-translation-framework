#!/usr/bin/env python3
import os
import re
import glob
from utils import parse_book_arg, load_book_config, get_book_dir, get_book_subpath

def clean_markdown_formatting(text):
    # 1. Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 2. Fix Vietnamese punctuation spacing
    text = re.sub(r'[ \t]+([,\.\?\!:\;])', r'\1', text)
    text = re.sub(r'([,\.\?\!:\;])([a-zA-ZàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴĐ])', r'\1 \2', text)
    
    # 3. Fix quotes & brackets spacing
    text = re.sub(r'“\s+', '“', text)
    text = re.sub(r'\s+”', '”', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    text = re.sub(r'\[\s+', '[', text)
    text = re.sub(r'\s+\]', ']', text)
    
    # 4. Standardize headings
    text = re.sub(r'^(#{1,6})[ \t]*', r'\1 ', text, flags=re.MULTILINE)
    
    # 5. Standardize callouts & quotes
    text = re.sub(r'>\s*\[\s*!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\s*\]', r'> [!\1]', text, flags=re.IGNORECASE)
    
    # 6. Convert inline LaTeX arrows and symbols in plain text to clean Unicode
    text = re.sub(r'\$\\rightarrow\$|\\rightarrow', '→', text)
    text = re.sub(r'\$\\leftarrow\$|\\leftarrow', '←', text)
    text = re.sub(r'\$\\leftrightarrow\$|\\leftrightarrow', '↔', text)
    text = re.sub(r'\$\\Rightarrow\$|\\Rightarrow', '⇒', text)
    text = re.sub(r'\$\\Leftarrow\$|\\Leftarrow', '⇐', text)
    text = re.sub(r'\$\\Leftrightarrow\$|\\Leftrightarrow', '⇔', text)
    text = re.sub(r'\$\\dots\$|\\dots', '…', text)
    text = re.sub(r'\$\\times\$|\\times', '×', text)
    text = re.sub(r'\$\\pm\$|\\pm', '±', text)
    text = re.sub(r'\$\\approx\$|\\approx', '≈', text)
    text = re.sub(r'\$\\leq\$|\\leq', '≤', text)
    text = re.sub(r'\$\\geq\$|\\geq', '≥', text)
    text = re.sub(r'\$\\neq\$|\\neq', '≠', text)
    text = re.sub(r'\$\\infty\$|\\infty', '∞', text)
    
    # 7. Normalize multiple spaces & blank lines
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip() + '\n'

def audit_footnote_integrity(text):
    anchors = set(re.findall(r'\[\^(\d+)\](?!:)', text))
    definitions = set(re.findall(r'\[\^(\d+)\]:', text))
    
    missing_defs = anchors - definitions
    unused_defs = definitions - anchors
    
    return {
        "anchors_count": len(anchors),
        "definitions_count": len(definitions),
        "missing_definitions": sorted(list(missing_defs)),
        "unused_definitions": sorted(list(unused_defs))
    }

def format_and_proofread_book(book_id):
    config = load_book_config(book_id)
    output_basename = config.get("output_basename", "Master_Book_Full")
    master_file = get_book_subpath(book_id, "04_Compiled_Book", f"{output_basename}.md")
    
    if not os.path.exists(master_file):
        # Fallback to any markdown file in 04_Compiled_Book
        compiled_dir = get_book_subpath(book_id, "04_Compiled_Book")
        md_files = glob.glob(os.path.join(compiled_dir, "*.md"))
        if md_files:
            master_file = md_files[0]
        else:
            print(f"Warning: No compiled master file found for book '{book_id}'. Proofreading draft files instead.")
            master_files = glob.glob(os.path.join(get_book_dir(book_id), "02_Draft_Translations", "**", "*.md"), recursive=True)
            for mf in master_files:
                with open(mf, "r", encoding="utf-8") as f:
                    t = f.read()
                ct = clean_markdown_formatting(t)
                with open(mf, "w", encoding="utf-8") as f:
                    f.write(ct)
            return

    with open(master_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    print(f"Executing automated typography and layout formatting for book '{book_id}'...")
    cleaned_text = clean_markdown_formatting(raw_text)
    footnote_report = audit_footnote_integrity(cleaned_text)

    with open(master_file, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print("\n" + "="*75)
    print(f"      BÁO CÁO HIỆU ĐÍNH & CHUẨN HÓA ĐỊNH DẠNG SÁCH: [{book_id.upper()}]")
    print("="*75)
    print(f"-> File Master: {os.path.basename(master_file)}")
    print(f"-> Tổng dung lượng file: {len(cleaned_text):,} ký tự")
    print(f"-> Số lượng chú thích (Footnotes Anchors): {footnote_report['anchors_count']}")
    print(f"-> Số lượng định nghĩa chú thích (Footnotes Definitions): {footnote_report['definitions_count']}")
    
    if footnote_report['missing_definitions']:
        print(f"-> [CẢNH BÁO] Thiếu định nghĩa cho chú thích ID: {footnote_report['missing_definitions']}")
    else:
        print("-> [HOÀN HẢO] 100% chú thích chân trang (Footnotes) liên kết hoàn toàn chính xác!")

    print("="*75 + "\n")

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 4: Layout & Footnote Proofreading")
    format_and_proofread_book(book_id)
