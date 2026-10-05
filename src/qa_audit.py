#!/usr/bin/env python3
import os
import json
import glob
import re
from utils import parse_book_arg, load_book_config, get_book_subpath

ALLOWED_EN_TERMS = {
    "management",
    "machine",
    "metaphor",
    "magisterium",
    "cybernetic",
    "regulating",
    "macrodeterminism",
    "conferences",
    "paradox",
    "jacob",
    "macy",
    "shiva",
    "emissions",
    "lockhart",
    "shroff",
    "zhabotinsky",
    "zeri",
    "julia",
    "jeﬀerson",
    "stream",
    "initiatives",
    "centers",
    "navdanya",
    "jefferson",
    "dehradun",
    "staff", "engineer", "senior", "principal", "distinguished", "fellow", "manager", "engineering",
    "individual", "contributor", "ic", "em", "tech", "lead", "architect", "solver", "right", "hand",
    "archetypes", "archetype", "locator", "topographical", "treasure", "map", "maps", "big", "picture",
    "vision", "strategy", "execution", "scope", "shape", "focus", "glue", "work", "snag", "sponsorship",
    "mentoring", "mentorship", "coaching", "visibility", "alignment", "guardrails", "role", "model",
    "rfc", "adr", "raci", "one-way", "two-way", "door", "doors", "unsticking", "cross-functional",
    "stakeholder", "cadence", "trade-offs", "tradeoffs", "sockmatcher", "oreilly", "github", "twitter",
    "medium", "google", "facebook", "amazon", "apple", "uber", "slack", "stripe", "camille", "fournier",
    "silvia", "botros", "tanya", "reilly", "jeff", "bezos", "douglas", "adams", "heidi", "waterhouse",
    "westrum", "overton", "nemawashi", "huston", "ship", "theseus",
    "david", "deutsch", "infinity", "beginning", "explanations", "explanation", "reach", "spark",
    "multiverse", "quantum", "solipsism", "empiricism", "rationalism", "fallibilism", "meme", "memes",
    "socrates", "popper", "turing", "bohr", "everett", "einstein", "newton", "galileo", "feynman",
    "viking", "penguin", "oxford", "cambridge", "agi", "optimism", "bad", "philosophy",
    # The Systems View of Life domain terms & names
    "capra", "fritjof", "luisi", "pier", "luigi", "maturana", "varela", "humberto", "francisco",
    "prigogine", "ilya", "bertalanffy", "ludwig", "bogdanov", "alexander", "bateson", "gregory",
    "lovelock", "james", "margulis", "lynn", "darwin", "charles", "mendel", "gregor", "lamarck",
    "wallace", "alfred", "wiener", "norbert", "von", "foerster", "heinz", "ashby", "ross",
    "mcculloch", "warren", "pitts", "walter", "shannon", "claude", "neumann", "john",
    "oparin", "alexander", "miller", "stanley", "urey", "harold", "kauffman", "stuart",
    "mandelbrot", "benoit", "lorenz", "edward", "feigenbaum", "mitchell", "poincare", "henri",
    "descartes", "rene", "newton", "isaac", "bacon", "francis", "galileo", "galilei", "locke", "john",
    "autopoiesis", "autopoietic", "self-organization", "self-organizing", "emergence", "emergent",
    "dissipative", "thermodynamics", "non-equilibrium", "nonlinear", "nonlinearity", "bifurcation",
    "attractor", "attractors", "fractal", "fractals", "cybernetics", "tektology", "homeostasis",
    "feedback", "symbiosis", "symbiogenesis", "epigenetics", "epigenetic", "prebiotic", "synthetic",
    "agroecology", "ecodesign", "sustainability", "biosphere", "ecosystem", "ecosystems", "daisyworld",
    "macromolecule", "ribosome", "vesicle", "vesicles", "micelle", "micelles", "membrane", "membranes",
    "paradigm", "paradigms", "reductionism", "reductionist", "holism", "holistic", "systemic",
    "mechanistic", "worldview", "cognition", "cognitive", "consciousness", "cartesian", "newtonian",
    "cambridge", "press", "university",
}

def is_code_or_markdown(line):
    s = line.strip()
    if not s:
        return True
    if s.startswith('#') or s.startswith('```') or s.startswith('> [!') or s.startswith('---') or s.startswith('$$'):
        return True
    if s.startswith('|') or s.startswith('!') or s.startswith('<http') or s.startswith('[^') or s.startswith('>'):
        return True
    return False

def check_untranslated_text(text):
    paragraphs = text.split('\n\n')
    untranslated_issues = []

    for idx, p in enumerate(paragraphs, 1):
        lines = p.strip().split('\n')
        non_code_lines = [l for l in lines if not is_code_or_markdown(l)]
        p_text = " ".join(non_code_lines).strip()
        if not p_text:
            continue

        words = re.findall(r'\b[a-zA-Z]+\b', p_text)
        if len(words) >= 12:
            non_allowed_en = [w.lower() for w in words if w.lower() not in ALLOWED_EN_TERMS]
            vn_chars = len(re.findall(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', p_text.lower()))
            if len(non_allowed_en) > 10 and vn_chars < 5:
                snippet = p_text[:120] + "..." if len(p_text) > 120 else p_text
                untranslated_issues.append({
                    "paragraph_index": idx,
                    "en_word_count": len(non_allowed_en),
                    "snippet": snippet
                })
    return untranslated_issues

def run_qa_audit(book_id):
    config = load_book_config(book_id)
    extracted_dir = get_book_subpath(book_id, "storage", "extracted_src")
    draft_dir = get_book_subpath(book_id, "02_Draft_Translations")

    extracted_files = sorted(glob.glob(os.path.join(extracted_dir, "chapter_*.json")))

    title_display = config.get("title_en", book_id).upper()
    print("\n" + "="*85)
    print(f"      HỆ THỐNG KIỂM THỬ CHẤT LƯỢNG (QA AUDIT SYSTEM) - SÁCH: {title_display}")
    print("="*85)
    print(f"{'CHAPTER':<12} | {'ORIG PARAS':<10} | {'DRAFT PARAS':<11} | {'EN WORDS':<10} | {'VI WORDS':<10} | {'RATIO':<8} | {'QA STATUS'}")
    print("-"*85)

    all_passed = True
    total_orig_words = 0
    total_trans_words = 0
    total_untranslated_blocks = 0

    for ext_path in extracted_files:
        with open(ext_path, "r", encoding="utf-8") as f:
            ext_data = json.load(f)

        chap_num = ext_data["chapter"]
        orig_words = ext_data["word_count"]
        orig_paras = len(ext_data["paragraphs"])
        total_orig_words += orig_words

        draft_matches = glob.glob(os.path.join(draft_dir, "**", f"Chapter_{chap_num:02d}.md"), recursive=True) or \
                        glob.glob(os.path.join(draft_dir, "**", f"chap_{chap_num:02d}.md"), recursive=True)

        trans_words = 0
        draft_paras = 0
        untranslated_issues = []

        if draft_matches and os.path.exists(draft_matches[0]):
            with open(draft_matches[0], "r", encoding="utf-8") as f:
                content = f.read()

            clean_text = re.sub(r'#+|[*_`~>|\-\+]', ' ', content)
            trans_words = len(clean_text.split())
            draft_paras = len([p for p in content.split('\n\n') if p.strip() and not p.strip().startswith('#')])
            untranslated_issues = check_untranslated_text(content)
            total_untranslated_blocks += len(untranslated_issues)

        total_trans_words += trans_words
        ratio = (trans_words / orig_words * 100) if orig_words > 0 else 0

        status_flags = []
        if ratio < 80.0:
            status_flags.append("THIEU SO TU (<80%)")
            all_passed = False
        elif ratio > 160.0:
            status_flags.append("THUA SO TU (>160%)")

        if len(untranslated_issues) > 0:
            status_flags.append(f"CON {len(untranslated_issues)} DOAN CHUA DICH")
            all_passed = False

        status_str = ", ".join(status_flags) if status_flags else "100% HOAN HAO (PASS)"
        print(f"Chapter {chap_num:02d}    | {orig_paras:<10} | {draft_paras:<11} | {orig_words:<10} | {trans_words:<10} | {ratio:<7.1f}% | {status_str}")

    overall_ratio = (total_trans_words / total_orig_words * 100) if total_orig_words > 0 else 0
    print("="*85)
    print(f"TONG CONG   | -          | -           | {total_orig_words:<10} | {total_trans_words:<10} | {overall_ratio:<7.1f}% | {'100% DAT CHUAN QA' if all_passed else 'CAN KIEM TRA'}")
    print("="*85)

    print(f"\nTong so doan nghi van chua dich (Untranslated Blocks): {total_untranslated_blocks}")
    print("="*85 + "\n")

    return all_passed

if __name__ == "__main__":
    book_id = parse_book_arg("Phase 5: Translation Quality & Coverage Audit")
    run_qa_audit(book_id)
