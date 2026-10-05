#!/usr/bin/env python3
import os
import re
import html
import glob
import sys
import base64
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

import ebooklib
from ebooklib import epub
from utils import parse_book_arg, load_book_config, get_book_subpath, get_book_dir

def resolve_image_path(src, book_id):
    if not src:
        return None
    
    if os.path.isabs(src) and os.path.exists(src):
        return src
    
    bdir = get_book_dir(book_id)
    direct_path = os.path.join(bdir, src)
    if os.path.exists(direct_path):
        return direct_path

    basename = os.path.basename(src)
    assets_img_dir = get_book_subpath(book_id, "assets", "images")
    
    exact_match = os.path.join(assets_img_dir, basename)
    if os.path.exists(exact_match):
        return exact_match

    if os.path.exists(assets_img_dir):
        all_imgs = sorted(os.listdir(assets_img_dir))
        page_m = re.search(r'page_(\d+)', basename, re.IGNORECASE)
        if page_m:
            p_num = page_m.group(1)
            for img in all_imgs:
                if f"page_{p_num}" in img:
                    return os.path.join(assets_img_dir, img)

        fig_m = re.search(r'fig_(\d+)_(\d+)', basename, re.IGNORECASE)
        if fig_m:
            fig_str = f"fig_{fig_m.group(1)}_{fig_m.group(2)}"
            for img in all_imgs:
                if fig_str in img.lower():
                    return os.path.join(assets_img_dir, img)

    return None

def build_html_toc(config, is_epub=False, chap_file_map=None):
    parts = config.get("parts", [])
    chapter_defs = {c["chapter"]: c for c in config.get("chapter_defs", [])}

    if not parts:
        return ""

    if chap_file_map is None:
        chap_file_map = {}

    toc_parts_html = []

    for part_info in parts:
        part_title = part_info.get("title", "")
        chapters = part_info.get("chapters", [])

        chap_items_html = []
        for cnum in chapters:
            cdef = chapter_defs.get(cnum, {})
            ctitle = cdef.get("title", f"Chương {cnum}")
            cstart = cdef.get("start", "")
            page_str = f"Trang {cstart}" if cstart else ""

            if is_epub:
                target_href = chap_file_map.get(cnum, f"chap_{cnum:02d}.xhtml")
            else:
                target_href = f"#chapter-{cnum}"

            if is_epub:
                # E-reader clean table row layout
                chap_items_html.append(f'''
                <tr>
                    <td style="width:1%; white-space:nowrap; padding:6px 10px 6px 0; vertical-align:baseline;">
                        <a href="{target_href}" style="text-decoration:none; color:#1e293b;">
                            <span style="background:#e2e8f0; color:#334155; font-size:0.82em; font-weight:bold; padding:2px 6px; border-radius:3px; font-family:sans-serif;">Chương {cnum:02d}</span>
                        </a>
                    </td>
                    <td style="padding:6px 8px; vertical-align:baseline;">
                        <a href="{target_href}" style="text-decoration:none; color:#0f172a; font-weight:600;">
                            {html.escape(ctitle)}
                        </a>
                    </td>
                    <td style="width:1%; white-space:nowrap; text-align:right; color:#64748b; font-size:0.85em; font-family:sans-serif; vertical-align:baseline;">
                        {page_str}
                    </td>
                </tr>''')
            else:
                # Web HTML5 layout
                chap_items_html.append(f'''
                <div style="display:flex; align-items:baseline; margin: 10px 0; font-size:1.02rem;">
                    <a href="{target_href}" style="color:#0f172a; text-decoration:none; display:flex; align-items:baseline; gap:12px; flex-shrink:0;">
                        <span style="background:#e2e8f0; color:#334155; font-size:0.82rem; font-weight:bold; padding:3px 8px; border-radius:4px; font-family:-apple-system, BlinkMacSystemFont, sans-serif;">Chương {cnum:02d}</span>
                        <span style="font-weight:600; color:#0f172a;">{html.escape(ctitle)}</span>
                    </a>
                    <span style="flex-grow:1; border-bottom: 1px dotted #cbd5e1; margin: 0 12px; height: 1px; min-width: 20px;"></span>
                    <span style="color:#64748b; font-size:0.88rem; font-family:-apple-system, BlinkMacSystemFont, sans-serif; flex-shrink:0;">{page_str}</span>
                </div>''')

        chaps_joined = "".join(chap_items_html)

        if is_epub:
            toc_parts_html.append(f'''
            <div class="toc-part" style="margin-top:22px;">
                <div style="font-weight:bold; font-size:1.08em; color:#d97706; border-bottom:1.5px solid #e2e8f0; padding-bottom:5px; margin-bottom:10px; text-transform:uppercase; font-family:Georgia, serif;">
                    {html.escape(part_title)}
                </div>
                <table style="width:100%; border-collapse:collapse; margin:4px 0;">
                    <tbody>
                        {chaps_joined}
                    </tbody>
                </table>
            </div>''')
        else:
            toc_parts_html.append(f'''
            <div class="toc-part" style="margin-top:28px;">
                <div style="font-weight:bold; font-size:1.12rem; color:#d97706; border-bottom:1.5px solid #e2e8f0; padding-bottom:6px; margin-bottom:14px; text-transform:uppercase; letter-spacing:0.8px; font-family:Georgia, serif;">
                    {html.escape(part_title)}
                </div>
                <div class="toc-chapter-list">
                    {chaps_joined}
                </div>
            </div>''')

    all_parts_joined = "".join(toc_parts_html)

    if is_epub:
        return f'''
        <div class="toc-epub-wrapper" style="padding:10px 0; margin:10px 0;">
            <div style="text-align:center; margin-bottom:20px;">
                <h1 style="font-family:Georgia, serif; font-size:1.8em; color:#0f172a; margin:0 0 6px 0; letter-spacing:2px; text-align:center; border:none; padding:0;">MỤC LỤC</h1>
                <div style="width:60px; height:3px; background:#d97706; margin:0 auto;"></div>
            </div>
            {all_parts_joined}
        </div>'''
    else:
        return f'''
        <section class="table-of-contents-wrapper" style="background:#fafafa; border:1px solid #e2e8f0; border-radius:10px; padding:36px 42px; margin:40px 0 60px 0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
            <div style="text-align:center; margin-bottom:24px;">
                <h2 style="font-family:Georgia, serif; font-size:1.85rem; color:#0f172a; margin:0 0 8px 0; letter-spacing:3px; font-weight:700;">MỤC LỤC</h2>
                <div style="width:70px; height:3.5px; background:#d97706; margin:0 auto; border-radius:2px;"></div>
            </div>
            {all_parts_joined}
        </section>'''

def format_inline_markdown(raw_text):
    s = raw_text
    # Convert inline LaTeX math arrows and symbols to Unicode
    s = re.sub(r'\$\\rightarrow\$|\\rightarrow', '→', s)
    s = re.sub(r'\$\\leftarrow\$|\\leftarrow', '←', s)
    s = re.sub(r'\$\\leftrightarrow\$|\\leftrightarrow', '↔', s)
    s = re.sub(r'\$\\Rightarrow\$|\\Rightarrow', '⇒', s)
    s = re.sub(r'\$\\Leftarrow\$|\\Leftarrow', '⇐', s)
    s = re.sub(r'\$\\Leftrightarrow\$|\\Leftrightarrow', '⇔', s)
    s = re.sub(r'\$\\dots\$|\\dots', '…', s)
    s = re.sub(r'\$\\times\$|\\times', '×', s)
    s = re.sub(r'\$\\pm\$|\\pm', '±', s)
    s = re.sub(r'\$\\approx\$|\\approx', '≈', s)
    s = re.sub(r'\$\\leq\$|\\leq', '≤', s)
    s = re.sub(r'\$\\geq\$|\\geq', '≥', s)
    s = re.sub(r'\$\\neq\$|\\neq', '≠', s)
    s = re.sub(r'\$\\infty\$|\\infty', '∞', s)

    s = html.escape(s)
    s = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*(.*?)\*', r'<em>\1</em>', s)
    s = re.sub(r'`(.*?)`', r'<code style="font-family:monospace; background:#e2e8f0; padding:2px 4px; border-radius:3px;">\1</code>', s)
    s = re.sub(r'\[\^(\d+)\](?!:)', r'<sup class="footnote-ref"><a href="#fn-\1" id="fnref-\1">[\1]</a></sup>', s)
    s = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color:#d97706; text-decoration:underline;">\1</a>', s)
    return s

def render_callout_box(quote_lines):
    full_q = "\n".join(quote_lines)
    m = re.match(r'^\s*\[!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\]\s*(.*)$', full_q, re.DOTALL | re.IGNORECASE)
    if m:
        c_type = m.group(1).upper()
        rest_text = m.group(2).strip()

        type_styles = {
            'NOTE': ('📌 GHI CHÚ', '#d97706', '#fffbeb', '#78350f'),
            'WARNING': ('⚠️ CẢNH BÁO', '#dc2626', '#fef2f2', '#991b1b'),
            'IMPORTANT': ('🚨 QUAN TRỌNG', '#dc2626', '#fef2f2', '#991b1b'),
            'TIP': ('💡 MẸO HAY', '#16a34a', '#f0fdf4', '#166534'),
            'CAUTION': ('🛑 THẬN TRỌNG', '#e11d48', '#fff1f2', '#9f1239'),
        }
        label, border_c, bg_c, text_c = type_styles.get(c_type, ('📌 GHI CHÚ', '#d97706', '#fffbeb', '#78350f'))

        inner_items = []
        for line in rest_text.split('\n'):
            line_s = line.strip()
            if not line_s:
                continue
            if line_s.startswith('#'):
                hm = re.match(r'^(#{1,6})\s*(.*)$', line_s)
                if hm:
                    h_text = format_inline_markdown(hm.group(2))
                    inner_items.append(f'<h4 style="margin-top:8px; margin-bottom:4px; font-weight:bold; color:{text_c}; text-align:left;">{h_text}</h4>')
                    continue
            p_text = format_inline_markdown(line_s)
            inner_items.append(f'<p style="margin: 4px 0; color:{text_c}; text-align:justify;">{p_text}</p>')

        content_html = "".join(inner_items) if inner_items else "<p></p>"

        return f'''<div class="callout callout-{c_type.lower()}" style="border-left: 4px solid {border_c}; background-color: {bg_c}; padding: 14px 18px; margin: 1.5em 0; border-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-weight: bold; font-size: 0.92rem; color: {border_c}; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">{label}</div>
            <div style="font-size: 0.95rem; line-height: 1.6;">{content_html}</div>
        </div>'''
    else:
        rendered_lines = []
        for l in quote_lines:
            rendered_lines.append(format_inline_markdown(l))
        q_html = "<br/>".join(rendered_lines)
        return f'<blockquote style="border-left: 4px solid #d97706; background: #fffbeb; padding: 12px 20px; margin: 1.5em 0; color: #78350f; font-style: italic; border-radius: 4px; text-align:justify;">{q_html}</blockquote>'

def markdown_to_html_body(md_text, book_id=None, embed_base64=True, is_epub=False):
    footnotes_dict = {}
    lines = md_text.split('\n')
    filtered_lines = []

    for line in lines:
        fn_match = re.match(r'^\s*\[\^(\d+)\]:\s*(.*)$', line)
        if fn_match:
            fn_id = fn_match.group(1)
            fn_text = fn_match.group(2).strip()
            footnotes_dict[fn_id] = fn_text
        else:
            filtered_lines.append(line)

    html_lines = []
    in_code_block = False
    code_lines = []
    in_quote = False
    quote_lines = []
    in_list = False

    def flush_quote():
        nonlocal quote_lines, in_quote
        if quote_lines:
            html_lines.append(render_callout_box(quote_lines))
            quote_lines = []
            in_quote = False

    def flush_list():
        nonlocal in_list
        if in_list:
            html_lines.append('</ul>')
            in_list = False

    for line in filtered_lines:
        line_s = line.strip()

        if line_s.startswith('```'):
            if in_code_block:
                code_content = html.escape('\n'.join(code_lines))
                html_lines.append(f'<pre style="background:#09090b; color:#f4f4f5; padding:16px; border-radius:6px; overflow-x:auto; font-size:0.9rem; border-left:4px solid #d97706; text-align:left;"><code>{code_content}</code></pre>')
                code_lines = []
                in_code_block = False
            else:
                flush_quote()
                flush_list()
                in_code_block = True
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        if line_s.startswith('>'):
            flush_list()
            in_quote = True
            q_line = re.sub(r'^\s*>\s?', '', line)
            quote_lines.append(q_line)
            continue
        else:
            if in_quote:
                flush_quote()

        if not line_s:
            flush_list()
            continue

        if line_s == '---':
            flush_list()
            html_lines.append('<hr style="border:0; height:1px; background:#e2e8f0; margin:2.5em 0;"/>')
            continue

        if line_s.startswith('#'):
            flush_list()
            m = re.match(r'^(#{1,6})\s*(.*)$', line_s)
            if m:
                level = len(m.group(1))
                heading_raw = m.group(2)
                heading_text = format_inline_markdown(heading_raw)
                
                chap_m = re.search(r'Chapter\s*(\d+)|Chương\s*(\d+)', heading_raw, re.IGNORECASE)
                anchor_attr = ""
                if chap_m:
                    c_num = int(chap_m.group(1) or chap_m.group(2))
                    anchor_attr = f'id="chapter-{c_num}"'
                else:
                    h_id = re.sub(r'[^\w\-]', '', heading_raw.lower().replace(' ', '-'))
                    anchor_attr = f'id="{h_id}"'
                
                color = "#0f172a" if level <= 2 else "#334155"
                border_b = "border-bottom: 2px solid #d97706; padding-bottom: 6px;" if level == 1 else ("border-bottom: 1px solid #cbd5e1; padding-bottom: 4px;" if level == 2 else "")
                html_lines.append(f'<h{level} {anchor_attr} style="margin-top:1.8em; margin-bottom:0.6em; color:{color}; font-family:Georgia, serif; text-align:left; {border_b}">{heading_text}</h{level}>')
            continue

        # Handle Markdown Image Links ![alt](src)
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)', line_s)
        if img_match:
            flush_list()
            alt_text = format_inline_markdown(img_match.group(1))
            raw_src = img_match.group(2)

            resolved_path = resolve_image_path(raw_src, book_id) if book_id else None
            
            if is_epub:
                basename = os.path.basename(resolved_path) if resolved_path else os.path.basename(raw_src)
                img_src = f"images/{basename}"
            elif embed_base64 and resolved_path and os.path.exists(resolved_path):
                ext = os.path.splitext(resolved_path)[1].lower().replace('.', '')
                mime = "image/png" if ext == "png" else ("image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}")
                with open(resolved_path, "rb") as img_file:
                    b64_str = base64.b64encode(img_file.read()).decode('utf-8')
                img_src = f"data:{mime};base64,{b64_str}"
            else:
                img_src = raw_src

            html_lines.append(f'''<figure style="text-align:center; margin:2.5em 0;">
                <img src="{img_src}" alt="{alt_text}" style="max-width:100%; height:auto; border-radius:4px; border:1px solid #e2e8f0; box-shadow:0 4px 6px -1px rgba(0,0,0,0.1); margin:0 auto; display:block;"/>
                <figcaption style="font-size:0.85rem; color:#64748b; margin-top:10px; font-style:italic; font-family:Georgia, serif; text-align:center;">{alt_text}</figcaption>
            </figure>''')
            continue

        if line_s.startswith('- ') or line_s.startswith('* '):
            if not in_list:
                html_lines.append('<ul style="margin:1em 0; padding-left:1.5em; line-height:1.7; text-align:left;">')
                in_list = True
            item_text = format_inline_markdown(line_s[2:].strip())
            html_lines.append(f'<li style="margin:4px 0;">{item_text}</li>')
            continue

        flush_list()
        para_text = format_inline_markdown(line_s)
        html_lines.append(f'<p style="margin:1em 0; line-height:1.75; color:#1e293b; font-size:1.02rem; text-align:justify; text-justify:inter-word;">{para_text}</p>')

    flush_quote()
    flush_list()

    if footnotes_dict:
        html_lines.append('<hr style="border:0; height:1px; background:#d97706; margin:3.5em 0 1.5em 0;"/>')
        html_lines.append('<section class="footnotes" style="font-size:0.88rem; color:#475569; background:#fafafa; padding:18px 24px; border-radius:6px; border:1px solid #e2e8f0; border-left:4px solid #d97706;">')
        html_lines.append('<h4 style="margin-top:0; margin-bottom:12px; font-size:0.95rem; color:#d97706; font-family:Georgia, serif; text-align:left;">📌 CHÚ THÍCH CHÂN TRANG (FOOTNOTES)</h4>')
        html_lines.append('<ol style="padding-left:20px; margin:0; text-align:left;">')
        for fn_id, fn_text in sorted(footnotes_dict.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
            fn_text_fmt = format_inline_markdown(fn_text)
            html_lines.append(f'<li id="fn-{fn_id}" style="margin-bottom:8px;">{fn_text_fmt} <a href="#fnref-{fn_id}" title="Quay lại văn bản" style="color:#d97706; text-decoration:none; font-weight:bold;">↩</a></li>')
        html_lines.append('</ol></section>')

    return "\n".join(html_lines)

def generate_html(md_text, out_path, title="Book", cover_path=None, book_id=None):
    config = load_book_config(book_id) if book_id else {}
    toc_html = build_html_toc(config, is_epub=False)
    body_html = markdown_to_html_body(md_text, book_id=book_id, embed_base64=True, is_epub=False)
    
    cover_html = ""
    if cover_path and os.path.exists(cover_path):
        ext = os.path.splitext(cover_path)[1].lower().replace('.', '')
        mime = "image/png" if ext == "png" else ("image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}")
        with open(cover_path, "rb") as c_file:
            b64_c = base64.b64encode(c_file.read()).decode('utf-8')
        cover_html = f'''<div class="book-cover-container" style="text-align:center; margin: 0 0 50px 0; padding: 0; width: 100%; border-radius: 8px; overflow: hidden; box-shadow: 0 12px 36px rgba(0,0,0,0.12);">
            <img src="data:{mime};base64,{b64_c}" alt="Bìa sách {title}" style="width:100%; height:auto; display:block; margin:0 auto;"/>
        </div>'''

    full_html = f'''<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <style>
        body {{ font-family: Georgia, "Times New Roman", Merriweather, serif; line-height: 1.8; color: #1c1917; max-width: 880px; margin: 0 auto; padding: 40px 24px; background-color: #fcf9f2; text-align: justify; text-justify: inter-word; }}
        h1, h2, h3, h4 {{ font-family: Georgia, "Times New Roman", serif; font-weight: 700; text-align: left; }}
        h1 {{ font-size: 2.2rem; color: #0c0a09; border-bottom: 2px solid #d97706; padding-bottom: 0.4em; margin-top: 1.5em; }}
        h2 {{ font-size: 1.6rem; color: #0c0a09; border-bottom: 1px solid #e7e5e4; padding-bottom: 0.3em; margin-top: 1.4em; }}
        a {{ color: #d97706; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
{cover_html}
{toc_html}
{body_html}
</body>
</html>'''
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"-> Published Refined HTML5 (with Upgraded TOC & Cover): '{out_path}'")

def build_docx_toc(doc, config):
    parts = config.get("parts", [])
    chapter_defs = {c["chapter"]: c for c in config.get("chapter_defs", [])}

    if not parts:
        return

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("MỤC LỤC")
    r_title.font.name = 'Georgia'
    r_title.font.size = Pt(20)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)

    p_line = doc.add_paragraph()
    p_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_line.paragraph_format.space_after = Pt(24)
    r_line = p_line.add_run("═════════════════════════════════════════")
    r_line.font.color.rgb = RGBColor(217, 119, 6)
    r_line.font.size = Pt(10)

    for part_info in parts:
        part_title = part_info.get("title", "")
        chapters = part_info.get("chapters", [])

        p_part = doc.add_paragraph()
        p_part.paragraph_format.space_before = Pt(16)
        p_part.paragraph_format.space_after = Pt(8)
        r_part = p_part.add_run(part_title.upper())
        r_part.font.name = 'Georgia'
        r_part.font.size = Pt(12)
        r_part.font.bold = True
        r_part.font.color.rgb = RGBColor(217, 119, 6)

        for cnum in chapters:
            cdef = chapter_defs.get(cnum, {})
            ctitle = cdef.get("title", f"Chương {cnum}")
            cstart = cdef.get("start", "")
            page_str = f"Trang {cstart}" if cstart else ""

            p_chap = doc.add_paragraph()
            p_chap.paragraph_format.left_indent = Inches(0.2)
            p_chap.paragraph_format.space_before = Pt(2)
            p_chap.paragraph_format.space_after = Pt(4)

            r_num = p_chap.add_run(f"[Chương {cnum:02d}]  ")
            r_num.font.name = 'Georgia'
            r_num.font.bold = True
            r_num.font.size = Pt(10)
            r_num.font.color.rgb = RGBColor(71, 85, 105)

            r_txt = p_chap.add_run(f"{ctitle} ")
            r_txt.font.name = 'Georgia'
            r_txt.font.size = Pt(10.5)
            r_txt.font.color.rgb = RGBColor(15, 23, 42)

            r_dots = p_chap.add_run(" . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . ")
            r_dots.font.name = 'Georgia'
            r_dots.font.size = Pt(9)
            r_dots.font.color.rgb = RGBColor(203, 213, 225)

            r_pg = p_chap.add_run(f"  {page_str}")
            r_pg.font.name = 'Georgia'
            r_pg.font.size = Pt(10)
            r_pg.font.color.rgb = RGBColor(100, 116, 139)

    doc.add_page_break()

def generate_docx(md_text, out_path, cover_path=None, book_id=None):
    config = load_book_config(book_id) if book_id else {}
    doc = docx.Document()

    for p in doc.paragraphs:
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)

    if cover_path and os.path.exists(cover_path):
        cover_section = doc.sections[0]
        cover_section.top_margin = Inches(0)
        cover_section.bottom_margin = Inches(0)
        cover_section.left_margin = Inches(0)
        cover_section.right_margin = Inches(0)
        cover_section.page_width = Inches(8.5)
        cover_section.page_height = Inches(11.0)

        p_cover = doc.add_paragraph()
        p_cover.paragraph_format.space_before = Pt(0)
        p_cover.paragraph_format.space_after = Pt(0)
        p_cover.paragraph_format.left_indent = Inches(0)
        p_cover.paragraph_format.right_indent = Inches(0)
        p_cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cover = p_cover.add_run()
        run_cover.add_picture(cover_path, width=Inches(8.5), height=Inches(11.0))

        # Add content section with standard 1-inch margins
        body_section = doc.add_section()
        body_section.top_margin = Inches(1.0)
        body_section.bottom_margin = Inches(1.0)
        body_section.left_margin = Inches(1.0)
        body_section.right_margin = Inches(1.0)
        body_section.page_width = Inches(8.5)
        body_section.page_height = Inches(11.0)
    else:
        for section in doc.sections:
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

    build_docx_toc(doc, config)

    lines = md_text.split('\n')
    in_code = False
    code_lines = []

    def sanitize_xml(s):
        if not s:
            return ""
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', str(s))

    for line in lines:
        line_s = line.strip()
        if line_s.startswith('```'):
            if in_code:
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.4)
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(4)
                run = p.add_run(sanitize_xml('\n'.join(code_lines)))
                run.font.name = 'Courier New'
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(30, 41, 59)
                code_lines = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_lines.append(line)
            continue

        if not line_s:
            continue

        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)', line_s)
        if img_match:
            alt_text = img_match.group(1)
            raw_src = img_match.group(2)
            resolved_img = resolve_image_path(raw_src, book_id) if book_id else None
            
            if resolved_img and os.path.exists(resolved_img):
                try:
                    p_img = doc.add_paragraph()
                    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p_img.paragraph_format.space_before = Pt(12)
                    p_img.paragraph_format.space_after = Pt(4)
                    r_img = p_img.add_run()
                    r_img.add_picture(resolved_img, width=Inches(5.2))
                    
                    if alt_text:
                        p_cap = doc.add_paragraph()
                        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_cap.paragraph_format.space_after = Pt(12)
                        r_cap = p_cap.add_run(sanitize_xml(alt_text))
                        r_cap.font.italic = True
                        r_cap.font.size = Pt(9.5)
                        r_cap.font.color.rgb = RGBColor(100, 116, 139)
                except Exception as e:
                    print(f"Warning: Failed inserting DOCX image '{resolved_img}': {e}")
            continue

        if line_s.startswith('#'):
            m = re.match(r'^(#{1,6})\s*(.*)$', line_s)
            if m:
                level = len(m.group(1))
                h_text = re.sub(r'\[!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\]', '', m.group(2), flags=re.IGNORECASE).strip()
                heading = doc.add_heading(level=min(level, 4))
                run = heading.add_run(sanitize_xml(h_text))
                run.font.name = 'Georgia'
                run.font.color.rgb = RGBColor(217, 119, 6) if level == 1 else RGBColor(15, 23, 42)
            continue

        if line_s.startswith('>'):
            q_text = re.sub(r'^\s*>\s?', '', line_s)
            q_text = re.sub(r'\[!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\]', r'\1:', q_text, flags=re.IGNORECASE)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.right_indent = Inches(0.5)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            run = p.add_run(sanitize_xml(q_text))
            run.italic = True
            run.font.name = 'Georgia'
            run.font.color.rgb = RGBColor(217, 119, 6)
            continue

        clean_p = re.sub(r'\*\*(.*?)\*\*', r'\1', line_s)
        clean_p = re.sub(r'\*(.*?)\*', r'\1', clean_p)
        clean_p = re.sub(r'`(.*?)`', r'\1', clean_p)
        clean_p = sanitize_xml(clean_p)

        p = doc.add_paragraph(clean_p)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if p.runs:
            p.runs[0].font.name = 'Georgia'

    doc.save(out_path)
    print(f"-> Published DOCX (with Refined TOC & Cover): '{out_path}'")

def generate_epub(md_text, out_path, title="Book", author="David Deutsch", cover_path=None, book_id=None):
    config = load_book_config(book_id) if book_id else {}
    author = config.get("author", author)
    book = epub.EpubBook()
    book.set_identifier("book-" + re.sub(r'\W+', '', title.lower()))
    book.set_title(title)
    book.set_language("vi")
    book.add_author(author)

    cover_page = None
    if cover_path and os.path.exists(cover_path):
        ext = os.path.splitext(cover_path)[1].lower()
        cover_name = f"cover{ext}"
        with open(cover_path, "rb") as cover_file:
            book.set_cover(cover_name, cover_file.read(), create_page=False)
        
        cover_page = epub.EpubHtml(title="Bìa Sách", file_name="cover.xhtml", lang="vi")
        cover_page_html = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="vi">
<head>
    <title>Bìa Sách</title>
    <style type="text/css">
        @page {{ margin: 0; padding: 0; }}
        body {{ margin: 0; padding: 0; text-align: center; background-color: #fcf9f2; width: 100vw; height: 100vh; overflow: hidden; }}
        div.cover-wrapper {{ margin: 0; padding: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }}
        img.cover-image {{ width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; display: block; margin: 0 auto; }}
    </style>
</head>
<body>
    <div class="cover-wrapper">
        <img class="cover-image" src="{cover_name}" alt="Bìa sách {html.escape(title)}" />
    </div>
</body>
</html>'''
        cover_page.set_content(cover_page_html.encode('utf-8'))
        book.add_item(cover_page)
        print(f"-> Embedded EPUB3 Full-Screen Book Cover: '{cover_name}'")

    img_matches = re.findall(r'!\[.*?\]\((.*?)\)', md_text)
    added_images = set()
    
    for idx, raw_src in enumerate(img_matches):
        resolved_img = resolve_image_path(raw_src, book_id) if book_id else None
        if resolved_img and os.path.exists(resolved_img):
            basename = os.path.basename(resolved_img)
            if basename not in added_images:
                added_images.add(basename)
                ext = os.path.splitext(basename)[1].lower().replace('.', '')
                mime = "image/png" if ext == "png" else ("image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}")
                with open(resolved_img, "rb") as img_f:
                    img_item = epub.EpubItem(
                        uid=f"img_{idx}",
                        file_name=f"images/{basename}",
                        media_type=mime,
                        content=img_f.read()
                    )
                    book.add_item(img_item)

    # Clean, professional e-reader CSS for EPUB
    style = '''
    @namespace epub "http://www.idpf.org/2007/ops";
    body {
        font-family: Georgia, "Times New Roman", serif;
        line-height: 1.7;
        color: #1e293b;
        padding: 0 4%;
        margin: 0;
        text-align: justify;
        text-justify: inter-word;
    }
    p {
        margin: 0.7em 0;
        text-align: justify;
        text-justify: inter-word;
    }
    h1, h2, h3, h4 {
        font-family: Georgia, serif;
        font-weight: bold;
        text-align: left;
        page-break-after: avoid;
    }
    h1 {
        color: #d97706;
        border-bottom: 2px solid #d97706;
        padding-bottom: 0.3em;
        margin-top: 1.4em;
        margin-bottom: 0.8em;
    }
    h2 {
        color: #0f172a;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 0.2em;
        margin-top: 1.3em;
    }
    img {
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1.2em auto;
    }
    figure {
        margin: 1.5em 0;
        text-align: center;
        page-break-inside: avoid;
    }
    figcaption {
        font-size: 0.85em;
        color: #64748b;
        font-style: italic;
        margin-top: 0.5em;
        text-align: center;
    }
    .callout {
        padding: 12px 16px;
        margin: 1.3em 0;
        border-left: 4px solid #d97706;
        background-color: #fffbeb;
        page-break-inside: avoid;
        text-align: justify;
    }
    pre {
        background: #09090b;
        color: #f4f4f5;
        padding: 12px;
        border-radius: 4px;
        overflow-x: auto;
        font-size: 0.85em;
        border-left: 4px solid #d97706;
        text-align: left;
    }
    code {
        font-family: monospace;
        background: #f1f5f9;
        padding: 2px 4px;
        border-radius: 3px;
        font-size: 0.9em;
    }
    pre code {
        background: transparent;
        padding: 0;
        border-radius: 0;
    }
    a {
        color: #d97706;
        text-decoration: none;
    }
    a:hover {
        text-decoration: underline;
    }
    table {
        border-collapse: collapse;
        width: 100%;
    }
    td, th {
        vertical-align: baseline;
    }
    '''
    css_item = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(css_item)

    # Dictionary mapping English Part headers to Vietnamese translated titles
    part_title_map = {
        "part 0: introduction": "Phần 0: Lời Nói Đầu & Giới Thiệu",
        "part i: the big picture": "Phần I: Bức Tranh Toàn Cảnh",
        "part ii: execution": "Phần II: Thực Thi",
        "part iii: leveling up": "Phần III: Nâng Tầm Ảnh Hưởng"
    }
    for p in config.get("parts", []):
        if "title_en" in p and "title" in p:
            part_title_map[p["title_en"].strip().lower()] = p["title"].strip()
        if "id" in p and "title" in p:
            part_title_map[p["id"].strip().lower().replace("_", " ")] = p["title"].strip()

    # 1. Parse all chapter chunks from markdown
    chapters_raw = re.split(r'\n(?=# )', md_text)
    epub_chapters = []
    chap_file_map = {}

    # Map chapter number to its exact EPUB xhtml filename
    for idx, chap_raw in enumerate(chapters_raw):
        if not chap_raw.strip():
            continue
        fname = f"chap_{idx:02d}.xhtml"
        first_line = chap_raw.strip().split('\n')[0]
        
        chap_m = re.search(r'Chapter\s*(\d+)|Chương\s*(\d+)', first_line, re.IGNORECASE)
        if chap_m:
            cnum = int(chap_m.group(1) or chap_m.group(2))
            chap_file_map[cnum] = fname
        elif "lời nói đầu" in first_line.lower() or "introduction" in first_line.lower() or "part 0" in first_line.lower():
            chap_file_map[0] = fname

    # 2. Build Dedicated TOC Page with exact chapter filename links
    toc_html_body = build_html_toc(config, is_epub=True, chap_file_map=chap_file_map)
    toc_page = epub.EpubHtml(title="Mục Lục", file_name="toc.xhtml", lang="vi")
    toc_page_html = f"<html><head><title>Mục Lục</title><link rel='stylesheet' href='style/nav.css' type='text/css'/></head><body>{toc_html_body}</body></html>"
    toc_page.set_content(toc_page_html.encode('utf-8'))
    book.add_item(toc_page)

    # 3. Create XHTML content items for all chapters
    for idx, chap_raw in enumerate(chapters_raw):
        if not chap_raw.strip():
            continue
        first_line = chap_raw.strip().split('\n')[0]
        chap_title = re.sub(r'^#+\s*', '', first_line)
        chap_title = re.sub(r'\[!(NOTE|WARNING|IMPORTANT|TIP|CAUTION)\]', '', chap_title, flags=re.IGNORECASE).strip()
        
        # Translate Part Titles if matching English raw titles
        chap_key = chap_title.strip().lower()
        if chap_key in part_title_map:
            chap_title = part_title_map[chap_key]
            
        if not chap_title:
            chap_title = f"Chương {idx}"

        c_body = markdown_to_html_body(chap_raw, book_id=book_id, is_epub=True)
        if not c_body.strip():
            c_body = f"<h1>{html.escape(chap_title)}</h1><p></p>"

        c_item = epub.EpubHtml(title=chap_title, file_name=f"chap_{idx:02d}.xhtml", lang="vi")
        c_item_html = f"<html><head><title>{html.escape(chap_title)}</title><link rel='stylesheet' href='style/nav.css' type='text/css'/></head><body>{c_body}</body></html>"
        c_item.set_content(c_item_html.encode('utf-8'))
        book.add_item(c_item)
        epub_chapters.append(c_item)

    # 4. Build Hierarchical Native EPUB TOC and Spine
    nav_toc_list = ([cover_page] if cover_page else []) + [toc_page] + epub_chapters
    for c_item in epub_chapters:
        pass

    book.toc = tuple(nav_toc_list)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # IMPORTANT: Spine contains cover_page (if present) + toc_page (the single translated TOC page) + chapter content pages.
    book.spine = ([cover_page] if cover_page else []) + [toc_page] + epub_chapters

    epub.write_epub(out_path, book, {})
    print(f"-> Published Single TOC EPUB3 (Fully Translated & No Duplicate Pages): '{out_path}'")

def build_all_publications(book_id):
    config = load_book_config(book_id)
    output_basename = config.get("output_basename", f"{book_id.title()}_Full")
    title_vi = config.get("title_vi", config.get("title_en", book_id))

    master_path = get_book_subpath(book_id, "04_Compiled_Book", f"{output_basename}.md")
    pub_dir = get_book_subpath(book_id, "05_Publication_Formats")
    os.makedirs(pub_dir, exist_ok=True)

    if not os.path.exists(master_path):
        print(f"Error: Master file '{master_path}' not found for book '{book_id}'.")
        return

    with open(master_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    cover_png = get_book_subpath(book_id, "assets", "cover.png")
    cover_jpg = get_book_subpath(book_id, "assets", "cover.jpg")
    cover_path = cover_png if os.path.exists(cover_png) else (cover_jpg if os.path.exists(cover_jpg) else None)

    if cover_path:
        print(f"Detected book cover image at: '{cover_path}'")

    print(f"Building all publication formats (HTML5, DOCX, EPUB3) with Single Translated EPUB TOC for book [{book_id}]...")
    generate_html(md_text, os.path.join(pub_dir, f"{output_basename}.html"), title=title_vi, cover_path=cover_path, book_id=book_id)
    generate_docx(md_text, os.path.join(pub_dir, f"{output_basename}.docx"), cover_path=cover_path, book_id=book_id)
    generate_epub(md_text, os.path.join(pub_dir, f"{output_basename}.epub"), title=title_vi, cover_path=cover_path, book_id=book_id)

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 5: Multi-Format Publishing (Single Translated EPUB TOC)")
    build_all_publications(book_id)
