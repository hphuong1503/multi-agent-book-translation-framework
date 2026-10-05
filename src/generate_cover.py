#!/usr/bin/env python3
import os
import sys
import argparse
from utils import parse_book_arg, load_book_config, get_book_subpath

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        pymupdf = None

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def generate_minimalist_cover(book_id, force=False, theme="white"):
    config = load_book_config(book_id)
    assets_dir = get_book_subpath(book_id, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    cover_path_png = os.path.join(assets_dir, "cover.png")
    cover_path_jpg = os.path.join(assets_dir, "cover.jpg")

    if not force and (os.path.exists(cover_path_png) or os.path.exists(cover_path_jpg)):
        target_path = cover_path_png if os.path.exists(cover_path_png) else cover_path_jpg
        print(f"Book cover already exists for '{book_id}' at path: '{target_path}'. Skipping generation.")
        return target_path

    title_en = config.get("title_en", book_id.replace("_", " ").title())
    title_vi = config.get("title_vi", f"{title_en} (Bản Dịch Tiếng Việt)")
    author = config.get("author", "Fritjof Capra & Pier Luigi Luisi")

    width, height = 1600, 2400

    if HAS_PIL:
        if theme == "white":
            # 2D Flat Full-bleed Minimalist Clean White Edition (#ffffff / #fafafa)
            img = Image.new("RGB", (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)

            try:
                font_badge = ImageFont.truetype("Helvetica", 30)
                font_title = ImageFont.truetype("Helvetica-Bold", 82)
                font_subtitle = ImageFont.truetype("Helvetica", 42)
                font_author = ImageFont.truetype("Helvetica-Bold", 42)
                font_foot = ImageFont.truetype("Helvetica", 28)
            except Exception:
                font_badge = ImageFont.load_default()
                font_title = ImageFont.load_default()
                font_subtitle = ImageFont.load_default()
                font_author = ImageFont.load_default()
                font_foot = ImageFont.load_default()

            # Header Badge
            draw.text((width // 2, 230), "C A M B R I D G E   U N I V E R S I T Y   P R E S S", fill=(100, 116, 139), font=font_badge, anchor="mm")

            # Top Minimalist Accent Line
            draw.line([(width // 2 - 140, 290), (width // 2 + 140, 290)], fill=(217, 119, 6), width=3)

            # Main Title (Massive Bold Dark Obsidian Typography)
            # Handle multiline if title is long
            words = title_en.upper().split()
            if len(words) > 4:
                half = len(words) // 2
                line1 = " ".join(words[:half])
                line2 = " ".join(words[half:])
                draw.text((width // 2, 480), line1, fill=(15, 23, 42), font=font_title, anchor="mm")
                draw.text((width // 2, 580), line2, fill=(15, 23, 42), font=font_title, anchor="mm")
            else:
                draw.text((width // 2, 530), title_en.upper(), fill=(15, 23, 42), font=font_title, anchor="mm")

            # Subtitle (Vietnamese Title)
            draw.text((width // 2, 720), title_vi, fill=(71, 85, 105), font=font_subtitle, anchor="mm")

            # Minimalist Central Geometric System Visualization (2D Flat Interconnected Concentric Rings & Nodes)
            cx, cy = width // 2, 1320
            # Outer Ring
            draw.ellipse([cx - 240, cy - 240, cx + 240, cy + 240], outline=(226, 232, 240), width=3)
            # Amber Dynamic System Ring
            draw.ellipse([cx - 170, cy - 170, cx + 170, cy + 170], outline=(217, 119, 6), width=4)
            # Inner Subtle Ring
            draw.ellipse([cx - 90, cy - 90, cx + 90, cy + 90], outline=(148, 163, 184), width=2)
            # Center Core Node
            draw.ellipse([cx - 16, cy - 16, cx + 16, cy + 16], fill=(15, 23, 42))

            # Satellite Interconnected Nodes
            for angle_offset in [(-170, 0), (170, 0), (0, -170), (0, 170)]:
                nx, ny = cx + angle_offset[0], cy + angle_offset[1]
                draw.ellipse([nx - 10, ny - 10, nx + 10, ny + 10], fill=(217, 119, 6))

            # Author Typography
            draw.text((width // 2, height - 360), author.upper(), fill=(15, 23, 42), font=font_author, anchor="mm")
            draw.line([(width // 2 - 80, height - 300), (width // 2 + 80, height - 300)], fill=(217, 119, 6), width=2)
            draw.text((width // 2, height - 240), "FULL-TEXT TRANSLATION • ANTIGRAVITY FRAMEWORK", fill=(100, 116, 139), font=font_foot, anchor="mm")

            img.save(cover_path_png, "PNG")
            print(f"[SUCCESS] Generated 2D Flat Minimalist White PNG cover -> '{cover_path_png}'")
            return cover_path_png

    # SVG Fallback
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
        <!-- Clean 2D Flat White Background -->
        <rect width="100%" height="100%" fill="#ffffff"/>
        
        <!-- Header Badge -->
        <text x="{width/2}" y="230" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="30" font-weight="600" fill="#64748b" text-anchor="middle" letter-spacing="6">CAMBRIDGE UNIVERSITY PRESS</text>
        <line x1="{width/2-140}" y1="290" x2="{width/2+140}" y2="290" stroke="#d97706" stroke-width="3"/>

        <!-- Main Title -->
        <text x="{width/2}" y="520" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="82" font-weight="800" fill="#0f172a" text-anchor="middle" letter-spacing="2">{title_en.upper()}</text>
        
        <!-- Subtitle -->
        <text x="{width/2}" y="680" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="42" font-weight="500" fill="#475569" text-anchor="middle">{title_vi}</text>

        <!-- Minimalist Graphic Interconnected System Rings -->
        <circle cx="{width/2}" cy="1320" r="240" fill="none" stroke="#e2e8f0" stroke-width="3"/>
        <circle cx="{width/2}" cy="1320" r="170" fill="none" stroke="#d97706" stroke-width="4"/>
        <circle cx="{width/2}" cy="1320" r="90" fill="none" stroke="#94a3b8" stroke-width="2"/>
        <circle cx="{width/2}" cy="1320" r="16" fill="#0f172a"/>
        <circle cx="{width/2 - 170}" cy="1320" r="10" fill="#d97706"/>
        <circle cx="{width/2 + 170}" cy="1320" r="10" fill="#d97706"/>
        <circle cx="{width/2}" cy="{1320 - 170}" r="10" fill="#d97706"/>
        <circle cx="{width/2}" cy="{1320 + 170}" r="10" fill="#d97706"/>

        <!-- Author & Footer -->
        <text x="{width/2}" y="{height-360}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="42" font-weight="700" fill="#0f172a" text-anchor="middle" letter-spacing="4">{author.upper()}</text>
        <line x1="{width/2-80}" y1="{height-300}" x2="{width/2+80}" y2="{height-300}" stroke="#d97706" stroke-width="2"/>
        <text x="{width/2}" y="{height-240}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="28" fill="#64748b" text-anchor="middle" letter-spacing="3">FULL-TEXT TRANSLATION • ANTIGRAVITY FRAMEWORK</text>
    </svg>'''
    
    svg_path = os.path.join(assets_dir, "cover.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    if pymupdf:
        try:
            doc = pymupdf.open(svg_path)
            page = doc[0]
            pix = page.get_pixmap(dpi=150)
            pix.save(cover_path_png)
            print(f"[SUCCESS] Rendered Minimalist White PNG cover from SVG -> '{cover_path_png}'")
            return cover_path_png
        except Exception as e:
            print(f"Warning: PyMuPDF SVG rendering failed: {e}")

    print(f"[SUCCESS] Generated Minimalist White SVG cover -> '{svg_path}'")
    return svg_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="2D Flat Minimalist Book Cover Generation Tool")
    parser.add_argument("--book", "-b", type=str, help="ID của cuốn sách (ví dụ: the_system_view_of_life)")
    parser.add_argument("--force", action="store_true", help="Ghi đè bìa sách nếu đã tồn tại")
    parser.add_argument("--theme", type=str, default="white", choices=["white", "dark"], help="Màu nền bìa sách (white/dark)")
    
    args = parser.parse_args()
    book_id = parse_book_arg("Generate Minimalist Style Book Cover")
    generate_minimalist_cover(book_id, force=args.force, theme=args.theme)
