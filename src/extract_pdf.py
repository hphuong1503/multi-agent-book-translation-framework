#!/usr/bin/env python3
try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

import json
import re
import os
import sys
from utils import parse_book_arg, load_book_config, get_book_subpath

def clean_paragraph_text(text):
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        cleaned_lines.append(line_s)
    
    full_text = ""
    for l in cleaned_lines:
        if full_text.endswith('-'):
            full_text = full_text[:-1] + l
        else:
            if full_text:
                full_text += " " + l
            else:
                full_text = l
    return full_text

def is_header_or_footer(text, y0, y1, page_height):
    text_s = text.strip()
    if text_s.isdigit() and (y0 < 70 or y1 > page_height - 70):
        return True
    if y1 < 50 or y0 > page_height - 50:
        return True
    return False

def extract_chapters(book_id):
    config = load_book_config(book_id)
    pdf_filename = config.get("pdf_filename", "source.pdf")
    pdf_path = get_book_subpath(book_id, pdf_filename)
    output_dir = get_book_subpath(book_id, "storage", "extracted_src")

    if not os.path.exists(pdf_path):
        print(f"Error: Source PDF '{pdf_path}' not found for book '{book_id}'.")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    doc = pymupdf.open(pdf_path)
    
    chapter_defs = config.get("chapter_defs", [])
    if not chapter_defs:
        print(f"Warning: No chapter_defs found in config.json for book '{book_id}'.")
        return

    extracted_summary = []

    for cdef in chapter_defs:
        chap_num = cdef["chapter"]
        chap_title = cdef["title"]
        start_p = cdef["start"] - 1
        end_p = cdef["end"] - 1

        paragraphs = []
        para_id = 1
        total_words = 0

        for p_no in range(start_p, min(end_p + 1, len(doc))):
            page = doc[p_no]
            page_height = page.rect.height
            blocks = page.get_text("blocks")

            for b in blocks:
                if len(b) >= 5 and b[6] == 0:
                    x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4]
                    if is_header_or_footer(text, y0, y1, page_height):
                        continue

                    cleaned = clean_paragraph_text(text)
                    if not cleaned:
                        continue

                    words = len(cleaned.split())
                    if words == 0:
                        continue

                    paragraphs.append({
                        "id": para_id,
                        "text": cleaned
                    })
                    para_id += 1
                    total_words += words

        chap_data = {
            "chapter": chap_num,
            "title": chap_title,
            "paragraphs": paragraphs,
            "word_count": total_words
        }

        out_filename = f"chapter_{chap_num:02d}.json"
        out_path = os.path.join(output_dir, out_filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chap_data, f, ensure_ascii=False, indent=2)

        extracted_summary.append({
            "chapter": chap_num,
            "file": out_filename,
            "paragraphs_count": len(paragraphs),
            "word_count": total_words
        })
        print(f"Extracted Chapter {chap_num:02d}: '{chap_title}' -> {len(paragraphs)} paragraphs, {total_words} words.")

    print(f"\n--- EXTRACTION COMPLETE FOR [{book_id}] ---")
    total_book_words = sum(s["word_count"] for s in extracted_summary)
    print(f"Total extracted words across book: {total_book_words}")

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 1: Extract PDF to JSON per Chapter")
    extract_chapters(book_id)
