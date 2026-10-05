#!/usr/bin/env python3
import os
import re
import glob
from utils import parse_book_arg, load_book_config, get_book_subpath, get_book_dir

def clean_file_figures(fpath, book_id):
    if not os.path.exists(fpath):
        return False

    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    assets_dir = get_book_subpath(book_id, "assets", "images")
    if not os.path.exists(assets_dir):
        return False

    all_imgs = sorted(os.listdir(assets_dir))

    # Map Figure number (e.g., "2-3" or "1-1") -> actual image path in assets/images/
    # We can match page numbers or figure captions from extracted images.
    # Let's build a map from Figure X-Y -> best matching asset image.
    fig_map = {}

    # Read config to get page bounds if needed, or scan images for figure numbers
    for img_fname in all_imgs:
        page_m = re.search(r'page_(\d+)', img_fname, re.IGNORECASE)
        if page_m:
            p_num = int(page_m.group(1))
            # Page range mapping for figures in Staff Engineer:
            # Page 31 -> 1-1, Page 37 -> 1-2, Page 52 -> 1-3
            # Page 77 -> 2-1, Page 80 -> 2-2, Page 84 -> 2-3, Page 85 -> 2-4, Page 87 -> 2-5
            # Page 91 -> 2-6, Page 92 -> 2-7, Page 100 -> 2-8, Page 104 -> 2-9, Page 107 -> 2-10
            # Page 117 -> 2-11, Page 119 -> 2-12, Page 122 -> 2-13, Page 124 -> 2-14
            # Page 136 -> 3-1, Page 156 -> 3-2, Page 167 -> 3-3
            # Page 194 -> 4-1, Page 413 -> 8-2, Page 457 -> 9-3, Page 12 -> P-1, Page 16 -> P-2, Page 18 -> P-3
            
            page_fig_map = {
                12: "P-1", 16: "P-2", 18: "P-3",
                31: "1-1", 37: "1-2", 52: "1-3",
                77: "2-1", 80: "2-2", 84: "2-3", 85: "2-4", 87: "2-5",
                91: "2-6", 92: "2-7", 100: "2-8", 104: "2-9", 107: "2-10",
                117: "2-11", 119: "2-12", 122: "2-13", 124: "2-14",
                136: "3-1", 156: "3-2", 167: "3-3",
                194: "4-1", 413: "8-2", 457: "9-3"
            }
            if p_num in page_fig_map:
                fig_key = page_fig_map[p_num]
                fig_map[fig_key] = f"assets/images/{img_fname}"

    # Replace dead figures/fig_X_Y.png or file:///... paths with assets/images/
    def fix_img_path(m):
        alt = m.group(1)
        src = m.group(2)
        
        # Check if alt has figure number
        fig_num_m = re.search(r'(?:Figure|Hình)\s*([\w\-]+)', alt, re.IGNORECASE)
        if fig_num_m:
            fkey = fig_num_m.group(1)
            if fkey in fig_map:
                return f"![{alt}]({fig_map[fkey]})"
        
        return m.group(0)

    # 1. First replace invalid image paths with valid ones if mapped
    new_content = re.sub(r'!\[(.*?)\]\((.*?)\)', fix_img_path, content)

    # 2. Collapse duplicate figure blocks (e.g. English figure tag + Vietnamese dead tag + italic text)
    # Regex to match consecutive image tags / figure captions
    lines = new_content.split('\n')
    cleaned_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        # Check if this line is an image tag
        if line_s.startswith('!['):
            # Look ahead for adjacent image tags or italic captions
            group = [line_s]
            j = i + 1
            while j < len(lines):
                next_s = lines[j].strip()
                if not next_s:
                    j += 1
                    continue
                if next_s.startswith('![') or (next_s.startswith('*Hình') and next_s.endswith('*')) or (next_s.startswith('*Figure') and next_s.endswith('*')):
                    group.append(next_s)
                    j += 1
                else:
                    break
            
            if len(group) > 1:
                # Deduplicate group: Select the BEST Vietnamese caption & BEST valid image path
                best_caption = ""
                best_path = ""
                
                for item in group:
                    if item.startswith('!['):
                        m = re.match(r'^!\[(.*?)\]\((.*?)\)', item)
                        if m:
                            cap, pth = m.group(1), m.group(2)
                            if "figures/" not in pth and "http" not in pth and pth.startswith("assets/images/"):
                                best_path = pth
                            if "Hình " in cap and not best_caption:
                                best_caption = cap
                            elif "Figure " in cap and not best_caption:
                                best_caption = cap
                    elif item.startswith('*') and item.endswith('*'):
                        italic_text = item.strip('*').strip()
                        if "Hình " in italic_text and not best_caption:
                            best_caption = italic_text

                if not best_caption:
                    best_caption = "Hình ảnh sơ đồ"
                
                if best_path:
                    cleaned_lines.append(f"![{best_caption}]({best_path})")
                else:
                    # Keep original if couldn't resolve
                    cleaned_lines.extend(group)
                
                i = j
                continue

        cleaned_lines.append(line)
        i += 1

    final_content = '\n'.join(cleaned_lines)
    
    # 3. Remove standalone duplicate italic captions right after an image tag
    final_content = re.sub(
        r'(!\[(Hình\s+[\w\-]+[^\n]*)\]\(([^\)]+)\))\s*\n+\*\2\*',
        r'\1',
        final_content
    )

    if final_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(final_content)
        return True
    return False

def clean_all(book_id):
    bdir = get_book_dir(book_id)
    md_files = sorted(glob.glob(os.path.join(bdir, "**", "*.md"), recursive=True))
    
    changed_count = 0
    for md_f in md_files:
        if "05_Publication_Formats" in md_f:
            continue
        if clean_file_figures(md_f, book_id):
            print(f"Fixed & deduplicated figures in: '{md_f}'")
            changed_count += 1
            
    print(f"-> Successfully cleaned figures in {changed_count} files for book '{book_id}'")

if __name__ == "__main__":
    book_id = parse_book_arg("Clean & Deduplicate Book Figures")
    clean_all(book_id)
