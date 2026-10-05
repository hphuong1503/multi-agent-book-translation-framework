#!/usr/bin/env python3
import os
import re
import glob
import json
try:
    import pymupdf
except ImportError:
    import fitz as pymupdf

from utils import parse_book_arg, load_book_config, get_book_subpath, get_book_dir

def extract_and_map_figures(book_id):
    config = load_book_config(book_id)
    pdf_filename = config.get("pdf_filename", "source.pdf")
    pdf_path = get_book_subpath(book_id, pdf_filename)

    assets_dir = get_book_subpath(book_id, "assets", "images")
    os.makedirs(assets_dir, exist_ok=True)

    if not os.path.exists(pdf_path):
        print(f"Warning: Source PDF '{pdf_path}' missing. Skipping image extraction.")
        return []

    doc = pymupdf.open(pdf_path)
    figures = []
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        page_num = page_idx + 1
        text = page.get_text()
        
        fig_matches = re.findall(r'(Figure\s+[\w\-]+[\.:\s]*[^\n]*)', text, re.IGNORECASE)
        
        images = page.get_images(full=True)
        for img_idx, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)
            img_bytes = base_image['image']
            img_ext = base_image['ext']
            
            if len(img_bytes) < 3000:
                continue
                
            img_name = f"page_{page_num:03d}_img_{img_idx+1}.{img_ext}"
            img_rel_path = f"assets/images/{img_name}"
            img_full_path = os.path.join(assets_dir, img_name)
            
            with open(img_full_path, "wb") as f:
                f.write(img_bytes)
                
            caption = fig_matches[0].strip() if fig_matches else f"Hình trang {page_num}"
            figures.append({
                "page": page_num,
                "path": img_rel_path,
                "abs_path": img_full_path,
                "caption": caption
            })

    print(f"Extracted {len(figures)} figure images into assets/images/ for book '{book_id}'")
    return figures

def embed_images_in_file(fpath, figures):
    if not os.path.exists(fpath):
        return 0

    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    inserted_count = 0
    
    for fig in figures:
        caption = fig["caption"]
        m = re.search(r'Figure\s+([\w\-]+)', caption, re.IGNORECASE)
        if m:
            fig_id = m.group(1)
            # Match standalone figure title / caption lines, not inline references like "(Figure 7.4)"
            pattern = re.compile(rf'(?m)^(\s*\*{0,2}(?:Hình|Figure)\s+{re.escape(fig_id)}[:\s][^\n]*)')
            
            if pattern.search(content):
                if fig['path'] not in content:
                    content = pattern.sub(rf'\1\n\n![{caption}]({fig["path"]})\n', content, count=1)
                    inserted_count += 1

    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content)

    return inserted_count

def embed_all(book_id):
    figures = extract_and_map_figures(book_id)
    if not figures:
        print("No figures extracted or found. Skipping embedding.")
        return

    bdir = get_book_dir(book_id)
    draft_files = sorted(glob.glob(os.path.join(bdir, "02_Draft_Translations", "**", "*.md"), recursive=True))
    for df in draft_files:
        cnt = embed_images_in_file(df, figures)
        if cnt > 0:
            print(f"Embedded {cnt} images into '{df}'")

    master_files = sorted(glob.glob(os.path.join(bdir, "04_Compiled_Book", "*.md")))
    for master_file in master_files:
        cnt_master = embed_images_in_file(master_file, figures)
        if cnt_master > 0:
            print(f"Embedded {cnt_master} images into '{master_file}'")

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 3: Image Extraction & Markdown Embedding")
    embed_all(book_id)
