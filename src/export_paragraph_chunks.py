#!/usr/bin/env python3
import json
import os
from utils import parse_book_arg, load_book_config, get_book_subpath

def export_chunks(book_id):
    config = load_book_config(book_id)
    extracted_dir = get_book_subpath(book_id, "storage", "extracted_src")
    chunk_dir = get_book_subpath(book_id, "storage", "extracted_chunks")
    os.makedirs(chunk_dir, exist_ok=True)

    chunk_defs = config.get("chunk_defs", [])
    if not chunk_defs:
        print(f"No custom chunk_defs defined in config for book '{book_id}'. Skipping chunk export.")
        return

    for item in chunk_defs:
        chap_num = item["chapter"]
        start_id = item["start_id"]
        end_id = item["end_id"]
        cname = item["cname"]

        ext_path = os.path.join(extracted_dir, f"chapter_{chap_num:02d}.json")
        if not os.path.exists(ext_path):
            print(f"Warning: Extracted source file '{ext_path}' missing. Skipping chunk {cname}.")
            continue

        with open(ext_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        filtered_paras = [p for p in data["paragraphs"] if start_id <= p["id"] <= end_id]
        
        chunk_data = {
            "chapter": chap_num,
            "title": data["title"],
            "start_id": start_id,
            "end_id": end_id,
            "paragraphs": filtered_paras,
            "word_count": sum(len(p["text"].split()) for p in filtered_paras)
        }

        out_path = os.path.join(chunk_dir, cname)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=2)

        print(f"Exported {cname}: Chapter {chap_num:02d} paras {start_id}..{end_id} ({len(filtered_paras)} paras, {chunk_data['word_count']} words)")

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 1: Export Paragraph Chunks for Context Management")
    export_chunks(book_id)
