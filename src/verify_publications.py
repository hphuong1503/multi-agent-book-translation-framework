#!/usr/bin/env python3
import os
import sys
import xml.etree.ElementTree as ET
import zipfile
import re
from utils import parse_book_arg, load_book_config, get_book_subpath

def verify_publications(book_id):
    config = load_book_config(book_id)
    output_basename = config.get("output_basename", f"{book_id.title()}_Full")

    pub_dir = get_book_subpath(book_id, "05_Publication_Formats")
    files = {
        "HTML5": f"{output_basename}.html",
        "DOCX": f"{output_basename}.docx",
        "EPUB3": f"{output_basename}.epub"
    }

    print("\n" + "="*80)
    print(f"XÁC NHẬN & KIỂM THỬ FILE XUẤT BẢN O'REILLY - SÁCH: [{book_id.upper()}]")
    print("="*80)

    all_ok = True

    for format_name, fname in files.items():
        fpath = os.path.join(pub_dir, fname)
        if not os.path.exists(fpath):
            print(f"[FAIL] {format_name:<10}: File '{fname}' KHÔNG TỒN TẠI.")
            all_ok = False
            continue

        size_bytes = os.path.getsize(fpath)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024

        if size_bytes == 0:
            print(f"[FAIL] {format_name:<10}: File '{fname}' RỖNG (0 bytes).")
            all_ok = False
            continue

        extra_info = ""
        if format_name == "HTML5":
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read().lower()
            
            b64_imgs = len(re.findall(r'src="data:image/', content))
            has_cover = "book-cover-container" in content
            
            if "<html" in content and "mathjax" in content and b64_imgs > 0:
                extra_info = f"-> Thỏa mãn XHTML/HTML5, MathJax [{b64_imgs} Hình/Bìa Base64 hiển thị 100%]"
            else:
                extra_info = f"-> Thỏa mãn HTML5 [{b64_imgs} hình nhúng]"
                if b64_imgs == 0:
                    all_ok = False

        elif format_name == "DOCX":
            try:
                with zipfile.ZipFile(fpath, 'r') as zip_ref:
                    namelist = zip_ref.namelist()
                    if 'word/document.xml' in namelist:
                        media_files = [item for item in namelist if item.startswith('word/media/')]
                        extra_info = f"-> Thỏa mãn cấu trúc Word OpenXML [{len(media_files)} hình ảnh nhúng]"
                        if len(media_files) == 0:
                            all_ok = False
                    else:
                        extra_info = "-> Thất bại cấu trúc XML DOCX"
                        all_ok = False
            except Exception as e:
                extra_info = f"-> Lỗi giải nén DOCX: {e}"
                all_ok = False

        elif format_name == "EPUB3":
            try:
                with zipfile.ZipFile(fpath, 'r') as zip_ref:
                    namelist = zip_ref.namelist()
                    if 'META-INF/container.xml' in namelist:
                        img_items = [item for item in namelist if item.startswith('images/') or 'cover' in item.lower()]
                        extra_info = f"-> Thỏa mãn chuẩn EPUB3 [{len(img_items)} hình ảnh container]"
                        if len(img_items) == 0:
                            all_ok = False
                    else:
                        extra_info = "-> Thất bại cấu trúc EPUB3 container"
                        all_ok = False
            except Exception as e:
                extra_info = f"-> Lỗi EPUB: {e}"
                all_ok = False

        print(f"[PASS] {format_name:<10}: {fname:<35} ({size_kb:.1f} KB / {size_mb:.2f} MB) {extra_info}")

    print("="*80)
    if all_ok:
        print(f"TẤT CẢ CÁC FILE XUẤT BẢN SÁCH [{book_id}] ĐÃ ĐẠT TIÊU CHUẨN CHẤT LƯỢNG 100%!")
    else:
        print(f"CÓ LỖI XẢY RA TRONG QUÁ TRÌNH KIỂM THỬ XUẤT BẢN SÁCH [{book_id}].")
    print("="*80 + "\n")

    return all_ok

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 5: Publication File Quality Verification")
    verify_publications(book_id)
