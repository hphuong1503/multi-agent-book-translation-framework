#!/usr/bin/env python3
import os
import re
import glob
from utils import parse_book_arg, get_book_dir

def clean_html_footnotes_in_text(text):
    text = re.sub(r'<sup>\[?(\d+)\]?(?:\(#fn\d+\))?</sup>', r'[^\1]', text)
    text = re.sub(r'<sup>(\d+)</sup>', r'[^\1]', text)
    
    text = re.sub(r'<a name=["\']fn(\d+)["\']>\d+</a>\.\s*', r'[^\1]: ', text)
    text = re.sub(r'<a name=["\']fn(\d+)["\']>\d+</a>', r'[^\1]: ', text)

    text = re.sub(r'</?sup>', '', text)
    text = re.sub(r'<a name=["\']\w+["\']>.*?</a>', '', text)

    text = re.sub(r'\[!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\]\s*(#{1,6})', r'\2', text, flags=re.IGNORECASE)

    text = re.sub(r'\n{3,}', '\n\n', text)

    return text

def process_all_markdown_files(book_id):
    bdir = get_book_dir(book_id)
    targets = sorted(glob.glob(os.path.join(bdir, "02_Draft_Translations", "**", "*.md"), recursive=True)) + \
              sorted(glob.glob(os.path.join(bdir, "03_Final_Edited", "*.md"))) + \
              sorted(glob.glob(os.path.join(bdir, "04_Compiled_Book", "*.md")))

    cleaned_count = 0
    for fpath in targets:
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            
            cleaned = clean_html_footnotes_in_text(content)
            if cleaned != content:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(cleaned)
                cleaned_count += 1
                print(f"Cleaned HTML/Footnote tags in '{fpath}'")

    print(f"\nCompleted cleaning HTML/Footnote formatting across {cleaned_count} Markdown files for book '{book_id}'.")

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 2: Clean HTML & Encode Footnote Anchors")
    process_all_markdown_files(book_id)
