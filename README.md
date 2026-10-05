**English** | [Tiếng Việt](README.vi.md)

# Multi-Agent Book Translation & Multi-Format Publishing Framework

An end-to-end autonomous framework for **100% full-text book translation**, terminology standardization, diagram extraction, formatting proofreading, and **commercial-grade multi-format publishing (HTML5, DOCX, EPUB3)** powered by a collaborative Multi-Agent architecture.

---

## 🌟 Key Features

- **100% Full-Text Sentence-by-Sentence Translation**: Strict anti-summarization pipeline ensuring zero omission of paragraphs, formulas, code blocks, or footnotes.
- **Centralized Terminology Consistency**: Standardized domain-specific glossaries (`00_Glossary/Central_Glossary.md`) enforced across all translation agents.
- **Specialized Multi-Agent Roles**:
  - **Lead Orchestrator**: Coordinates tasks, parallel subagents, and automated validation scripts.
  - **Book Translator**: Performs sentence-level faithful translation with LaTeX formula and code preservation.
  - **QA Audit Checker**: Detects untranslated English fragments and verifies translation word-count ratios (80%–130%).
  - **Image & Diagram Editor**: Extracts vector/raster diagrams from PDF and contextually embeds captions into Markdown.
  - **Cover Designer**: Creates 2D minimalist typography covers (Pillow vector rendering or AI image generation).
  - **EPUB & Multi-Format Publisher**: Builds self-contained HTML5 (Base64 images + MathJax), styled DOCX, and fully validated EPUB3.
- **Multi-Book Isolation Pattern**: Each book is maintained in an isolated sandbox under `books/<book_id>/` with its own configuration, storage, assets, and builds.
- **Automated Validation**: Built-in verification scripts for XML/XHTML containers, EPUB navigation structures, footnote bi-directional anchors (`↩`), and image integrity.

---

## ⚡ Multi-Agent One-Prompt Trigger

Copy and prompt your AI coding agent (e.g. Antigravity) to translate and publish any new book end-to-end:

```markdown
Activate Antigravity Multi-Agent Book Translation Framework for the following book:

- **Book ID**: <book_id, e.g. ddia>
- **English Title**: <Original English Title>
- **Vietnamese Title**: <Vietnamese Title>
- **Author**: <Author Name>
- **PDF Path**: <Path to source PDF, e.g. ./source.pdf>

### Execution Requirements (Multi-Agent Workflow):
1. **Initialize**: Run `python3 src/create_book.py <book_id> <pdf_path>` and parse the PDF (`src/extract_pdf.py`, `src/export_paragraph_chunks.py`).
2. **Multi-Agent Translation**: Dispatch parallel subagents (`invoke_subagent`) to translate 100% full text chapter-by-chapter (no summarization, adhere to `00_Glossary/Central_Glossary.md`, save to `02_Draft_Translations/`).
3. **Cover & Figures**: Generate a minimalist 2D flat cover and extract/embed diagrams from the PDF (`src/embed_images.py`, `src/clean_duplicate_figures.py`).
4. **Proofreading & Publishing**: Compile and audit word counts (`src/word_count_audit.py`), auto-publish 3 formats in `05_Publication_Formats/` (HTML5 Base64, DOCX, EPUB3 with translated navigation TOC), and run verification (`src/verify_publications.py`).
```

---

## 📁 Multi-Book Directory Layout

Each book project is encapsulated inside `books/<book_id>/`:

```text
├── books/                                  # Multi-book workspace root
│   ├── staff_engineer/                     # Example project: The Staff Engineer
│   │   ├── config.json                     # Book metadata, page mapping & chapter definitions
│   │   ├── source.pdf                      # Original source PDF (git-ignored)
│   │   ├── 00_Glossary/                    # Domain terminology glossary
│   │   ├── storage/                        # Extracted JSON chapters & paragraph chunks
│   │   ├── 02_Draft_Translations/          # Raw chapter translations (Part_X/Chapter_YY.md)
│   │   ├── 03_Final_Edited/                # Consolidated parts (Part_I.md, Part_II.md...)
│   │   ├── 04_Compiled_Book/               # Master Full Book Markdown
│   │   ├── 05_Publication_Formats/         # Production files (HTML5, DOCX, EPUB3)
│   │   └── assets/images/                  # Extracted diagrams & book cover
│   └── <new_book_id>/                      # Isolated workspace for another book
├── prompts/                                # Agent system prompts & triggers
│   ├── TRIGGER_BOOK_PIPELINE.md            # One-prompt trigger template
│   ├── translation_prompt.md               # Translator agent prompt
│   ├── qa_prompt.md                        # QA auditor prompt
│   ├── image_editor_prompt.md              # Image editor prompt
│   ├── cover_designer_prompt.md            # Cover designer prompt
│   └── epub_publisher_prompt.md            # EPUB publisher prompt
└── src/                                    # Automation scripts & pipeline tools
    ├── utils.py                            # Central book path & configuration manager
    ├── create_book.py                      # Scaffold new book project directory
    ├── extract_pdf.py                      # PyMuPDF extractor (PDF to structured JSON)
    ├── export_paragraph_chunks.py          # Split long chapters into manageable chunks
    ├── generate_cover.py                   # Render minimalist 2D typography book cover
    ├── embed_images.py                     # Extract & map figures from PDF into Markdown
    ├── clean_duplicate_figures.py          # Clean duplicate images & fix captions
    ├── proofread_and_format.py             # Format punctuation, LaTeX symbols, & footnotes
    ├── word_count_audit.py                 # Compile book & audit translation word counts
    ├── generate_publications.py            # Multi-format publisher (HTML5, DOCX, EPUB3)
    ├── verify_publications.py              # Quality & container verification tests
    ├── qa_audit.py                         # Scan for untranslated text & word ratios
    └── run_pipeline.py                     # 1-Click end-to-end automation pipeline
```

---

## 🛠️ Installation & Setup

### 1. Requirements
- Python 3.10+
- Git

### 2. Environment Setup
```bash
# Clone the repository
git clone https://github.com/hphuong1503/multi-agent-book-translation-framework.git
cd multi-agent-book-translation-framework

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS / Linux
# or: .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 CLI Usage Guide

### 1. Create a New Book Project
```bash
python3 src/create_book.py --id <book_id> --title "<Original English Title>" --title-vi "<Vietnamese Title>" --pdf path/to/source.pdf
```

### 2. Run the Full Automation Pipeline
```bash
python3 src/run_pipeline.py --book <book_id>
```

### 3. Run Quality & Verification Audits
```bash
# Verify publication integrity (HTML5, DOCX, EPUB3)
python3 src/verify_publications.py --book <book_id>

# Run translation QA audit (check untranslated text & word-count ratio)
python3 src/qa_audit.py --book <book_id>
```

---

## 📄 License

This framework is licensed under the [MIT License](LICENSE).  
Original book documents and source PDFs remain the intellectual property of their respective authors and publishers.
