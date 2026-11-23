"""
Generate realistic UI output mockup images showing expected system output.
Saved to docs/images/output_mockups/
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

os.makedirs("docs/images/output_mockups", exist_ok=True)

BG     = "#0f1117"
CARD   = "#1a1d27"
CARD2  = "#22263a"
BORDER = "#2e3250"
ACCENT = "#6c63ff"
GREEN  = "#4ecca3"
YELLOW = "#ffd166"
RED    = "#ff6b6b"
TEXT   = "#e8eaf6"
MUTED  = "#8b90b0"

def set_dark(fig, ax_list):
    fig.patch.set_facecolor(BG)
    for ax in ax_list:
        ax.set_facecolor(BG)
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values(): s.set_visible(False)

def rbox(ax, x, y, w, h, fc, text="", fs=9, tc=TEXT, bold=False, alpha=1.0, radius=0.3):
    box = FancyBboxPatch((x-w/2, y-h/2), w, h,
        boxstyle=f"round,pad=0.05,rounding_size={radius}",
        linewidth=1, edgecolor=BORDER, facecolor=fc, alpha=alpha, zorder=3)
    ax.add_patch(box)
    if text:
        ax.text(x, y, text, ha='center', va='center', fontsize=fs,
                color=tc, fontweight='bold' if bold else 'normal', zorder=4,
                wrap=True, multialignment='center')

def label(ax, x, y, text, fs=9, color=TEXT, ha='left', bold=False, style='normal'):
    ax.text(x, y, text, ha=ha, va='center', fontsize=fs, color=color,
            fontweight='bold' if bold else 'normal', style=style, zorder=4)


# ═══════════════════════════════════════════════════════════
# IMAGE 1 — UI Search Box (input state)
# ═══════════════════════════════════════════════════════════
def mockup_input():
    fig, ax = plt.subplots(figsize=(12, 5))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,6)

    # Header
    rbox(ax, 6, 5.5, 12, 0.8, CARD)
    label(ax, 0.4, 5.5, "Healthcare Literature Analyzer", fs=13, bold=True)
    label(ax, 0.4, 5.2, "Agentic AI  |  RAG  |  Evidence Grounding", fs=8, color=MUTED)
    # Status dot
    circle = plt.Circle((11.3, 5.5), 0.1, color=GREEN, zorder=5)
    ax.add_patch(circle)
    label(ax, 11.5, 5.5, "API Online", fs=8, color=GREEN)

    # Search card
    rbox(ax, 6, 3.5, 11.5, 3.5, CARD)
    label(ax, 0.6, 4.9, "Enter Your Research Question", fs=11, bold=True)

    # Textarea
    rbox(ax, 6, 3.9, 10.8, 1.4, CARD2, radius=0.2)
    label(ax, 1.0, 4.3, "What deep learning methods are used to detect diabetic retinopathy", fs=9.5, color=TEXT)
    label(ax, 1.0, 3.9, "from fundus eye images?", fs=9.5, color=TEXT)
    label(ax, 1.0, 3.5, "_", fs=10, color=ACCENT)  # cursor

    # Options row
    rbox(ax, 1.8, 2.7, 2.8, 0.55, CARD2, "Max papers:  3", fs=9, radius=0.2)
    rbox(ax, 5.2, 2.7, 4.2, 0.55, CARD2, "Sources:  PubMed + Semantic Scholar", fs=9, radius=0.2)

    # Button
    rbox(ax, 10.1, 2.7, 2.5, 0.6, ACCENT, "Analyze Literature", fs=10, bold=True, tc="#ffffff")

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/01_input_ui.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("1 01_input_ui.png")


# ═══════════════════════════════════════════════════════════
# IMAGE 2 — Progress Stepper (running state)
# ═══════════════════════════════════════════════════════════
def mockup_progress():
    fig, ax = plt.subplots(figsize=(12, 3))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,4)

    rbox(ax, 6, 2, 11.5, 3.5, CARD)
    label(ax, 0.6, 3.5, "Extracting evidence from papers...", fs=11, bold=True, color=ACCENT)

    steps = [
        (1.0,  "Retrieve",   "done"),
        (3.0,  "Extract",    "active"),
        (5.0,  "Validate",   "wait"),
        (7.0,  "Synthesize", "wait"),
        (9.0,  "Gaps",       "wait"),
        (11.0, "Report",     "wait"),
    ]
    for x, name, state in steps:
        if state == "done":
            fc, tc, border = "#122d1a", GREEN, GREEN
            mark = "checkmark"
        elif state == "active":
            fc, tc, border = CARD2, ACCENT, ACCENT
            mark = "active"
        else:
            fc, tc, border = CARD2, MUTED, BORDER
            mark = ""

        box = FancyBboxPatch((x-0.85, 0.4), 1.7, 1.8,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            linewidth=1.5, edgecolor=border, facecolor=fc, zorder=3)
        ax.add_patch(box)
        ax.text(x, 1.65, name, ha='center', va='center', fontsize=9,
                color=tc, fontweight='bold', zorder=4)
        if mark == "checkmark":
            ax.text(x+0.7, 2.1, "v", ha='center', fontsize=8, color=GREEN, zorder=5, fontweight='bold')
        elif mark == "active":
            # spinner dot
            circle = plt.Circle((x, 1.0), 0.15, color=ACCENT, zorder=5)
            ax.add_patch(circle)

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/02_progress_stepper.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("2 02_progress_stepper.png")


# ═══════════════════════════════════════════════════════════
# IMAGE 3 — Executive Summary + Stats
# ═══════════════════════════════════════════════════════════
def mockup_summary():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,7)

    # Summary box
    rbox(ax, 6, 5.8, 11.5, 2.2, "#1a1f35", radius=0.3)
    label(ax, 0.6, 6.6, "EXECUTIVE SUMMARY", fs=8, color=GREEN, bold=True)
    summary = (
        "Recent studies demonstrate that deep learning models, particularly convolutional neural\n"
        "networks (CNNs) and transformer-based architectures, achieve high accuracy in automated\n"
        "diabetic retinopathy detection from fundus photographs. Studies report AUC values ranging\n"
        "from 0.94 to 0.99 on benchmark datasets such as EyePACS and APTOS. EfficientNet and\n"
        "ResNet variants dominate the literature, while Vision Transformers show competitive\n"
        "performance with better global feature capture. Dataset imbalance and limited external\n"
        "validation remain consistent challenges across all reviewed studies."
    )
    ax.text(0.6, 5.9, summary, ha='left', va='top', fontsize=8.5,
            color=TEXT, zorder=4, linespacing=1.6)

    # Stats pills
    stats = [
        (1.5,  3.8, "8  papers",           ACCENT),
        (3.8,  3.8, "6  findings",         GREEN),
        (6.1,  3.8, "4/7  claims supported", YELLOW),
        (9.0,  3.8, "3  research gaps",    RED),
    ]
    for x, y, text, color in stats:
        rbox(ax, x, y, 2.8, 0.55, CARD2, text, fs=9.5, tc=color, bold=True, radius=0.4)

    # Tabs
    tabs = ["Key Findings", "Papers", "Evidence", "Research Gaps", "Synthesis", "References"]
    colors = [ACCENT, MUTED, MUTED, MUTED, MUTED, MUTED]
    for i, (tab, tc) in enumerate(zip(tabs, colors)):
        x = 1.0 + i * 1.85
        rbox(ax, x, 2.9, 1.65, 0.5, CARD if tc == ACCENT else BG,
             tab, fs=8, tc=tc, radius=0.1)
        if tc == ACCENT:
            ax.plot([x-0.82, x+0.82], [2.65, 2.65], color=ACCENT, lw=2, zorder=5)

    ax.plot([0.3, 11.7], [2.65, 2.65], color=BORDER, lw=0.8, zorder=2)

    # Active tab content — Key Findings
    findings = [
        "Deep CNN models (ResNet, EfficientNet) achieve >90% sensitivity on standard DR benchmarks",
        "Vision Transformer (ViT) models show competitive AUC with better global feature capture",
        "Multi-task learning simultaneously grades DR severity and detects lesions",
        "Dataset imbalance (few severe DR cases) is a consistent challenge across all 8 studies",
        "Real-world clinical performance drops significantly compared to benchmark results",
        "Transfer learning from ImageNet substantially reduces required training data",
    ]
    for i, f in enumerate(findings):
        y = 2.1 - i * 0.33
        rbox(ax, 6, y, 11.2, 0.28, CARD2, "", radius=0.1)
        ax.plot([0.5, 0.65], [y, y], color=ACCENT, lw=3, zorder=5)
        ax.text(0.75, y, f, ha='left', va='center', fontsize=8, color=TEXT, zorder=4)

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/03_summary_findings.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("3 03_summary_findings.png")


# ═══════════════════════════════════════════════════════════
# IMAGE 4 — Papers Tab
# ═══════════════════════════════════════════════════════════
def mockup_papers():
    fig, ax = plt.subplots(figsize=(12, 7))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,8)

    label(ax, 6, 7.7, "Papers Retrieved (8 total)", fs=12, bold=True, ha='center')

    papers = [
        ("Deep Learning System for Detecting Diabetic Retinopathy in Retinal Fundus Photographs",
         "Gulshan V, Peng L, Coram M et al.", "2024", "PubMed",  "10.1056/xxx",  "#ff9999"),
        ("EfficientNet-Based Grading of Diabetic Retinopathy Severity",
         "Chen L, Wang F, Zhang Y",           "2023", "S2",      "10.1109/xxx",  "#a9a4ff"),
        ("Vision Transformer for Retinal Disease Classification",
         "Park S, Kim J, Lee H et al.",        "2023", "PubMed",  "10.1038/xxx",  "#ff9999"),
        ("Multi-Task Learning for Joint DR Detection and Lesion Segmentation",
         "Liu Z, Zhao R, Sun Q",              "2022", "S2",      "10.1007/xxx",  "#a9a4ff"),
        ("Benchmarking CNN Architectures for Fundus Image Analysis",
         "Fernandez A, Torres M et al.",       "2023", "PubMed",  "10.1016/xxx",  "#ff9999"),
    ]

    for i, (title, authors, year, source, doi, sbadge) in enumerate(papers):
        y = 6.8 - i * 1.25
        rbox(ax, 6, y, 11.5, 1.1, CARD2, radius=0.2)
        # Title
        ax.text(0.6, y+0.3, title[:70] + ("..." if len(title)>70 else ""),
                ha='left', va='center', fontsize=9, color=TEXT, fontweight='bold', zorder=4)
        # Meta
        ax.text(0.6, y-0.05, f"  {authors}    {year}    DOI: {doi}",
                ha='left', va='center', fontsize=7.5, color=MUTED, zorder=4)
        # Source badge
        rbox(ax, 11.0, y+0.3, 0.9, 0.3, sbadge+"33", source, fs=7.5, tc=sbadge, radius=0.3)
        # Abstract snippet
        ax.text(0.6, y-0.35,
                "Abstract: Automated detection of diabetic retinopathy using deep learning on 50,000+ fundus images...",
                ha='left', va='center', fontsize=7.5, color=MUTED, style='italic', zorder=4)

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/04_papers_tab.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("4 04_papers_tab.png")


# ═══════════════════════════════════════════════════════════
# IMAGE 5 — Evidence Validation Tab
# ═══════════════════════════════════════════════════════════
def mockup_evidence():
    fig, ax = plt.subplots(figsize=(12, 7))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,8)

    label(ax, 6, 7.7, "Validated Claims (7 total)", fs=12, bold=True, ha='center')

    claims = [
        ("CNNs achieve 97% AUC on the EyePACS dataset for diabetic retinopathy grading",
         "supported", GREEN, "SUPPORTED",
         "Source: 'Deep Learning System...' (2024) — Results section: AUC 0.97 reported on EyePACS holdout set of 10,000 images"),
        ("Transfer learning from ImageNet improves performance on small retinal datasets",
         "supported", GREEN, "SUPPORTED",
         "Source: 'EfficientNet-Based Grading...' (2023) — Methods: ImageNet pretrained weights used, 15% improvement reported"),
        ("Vision Transformers outperform CNNs on all diabetic retinopathy metrics",
         "partially_supported", YELLOW, "PARTIALLY SUPPORTED",
         "Source: 'Vision Transformer...' (2023) — ViT achieves higher AUC but lower sensitivity; not superior on all metrics"),
        ("The model was clinically deployed in 50 hospitals across India",
         "unsupported", RED, "UNSUPPORTED",
         "No retrieved passage confirms clinical deployment. Fabricated statistic — not in any analyzed paper"),
        ("Multi-task learning reduces annotation cost compared to single-task models",
         "partially_supported", YELLOW, "PARTIALLY SUPPORTED",
         "Source: 'Multi-Task Learning...' — Indirect evidence; annotation efficiency mentioned but not quantified"),
        ("Dataset imbalance between severity grades affects model generalization",
         "supported", GREEN, "SUPPORTED",
         "Source: 3 papers mention class imbalance as limitation — EyePACS has 73% mild DR cases"),
        ("Federated learning preserves patient privacy in retinopathy screening",
         "insufficient_evidence", MUTED, "INSUFFICIENT EVIDENCE",
         "No retrieved paper discusses federated learning for DR detection specifically"),
    ]

    for i, (claim, status, color, label_text, source) in enumerate(claims):
        y = 7.0 - i * 0.93
        # Card with colored left border
        rbox(ax, 6, y, 11.5, 0.82, CARD2, radius=0.15)
        ax.plot([0.3, 0.3], [y-0.41, y+0.41], color=color, lw=4, zorder=5, solid_capstyle='round')
        # Status badge
        rbox(ax, 1.7, y+0.2, 2.2, 0.28, color+"22", label_text, fs=7, tc=color, bold=True, radius=0.25)
        # Claim text
        ax.text(0.55, y-0.08, claim[:85] + ("..." if len(claim)>85 else ""),
                ha='left', va='center', fontsize=8.5, color=TEXT, zorder=4)
        # Source
        ax.text(0.55, y-0.3, source[:95] + "...",
                ha='left', va='center', fontsize=7, color=MUTED, style='italic', zorder=4)

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/05_evidence_tab.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("5 05_evidence_tab.png")


# ═══════════════════════════════════════════════════════════
# IMAGE 6 — Research Gaps Tab
# ═══════════════════════════════════════════════════════════
def mockup_gaps():
    fig, ax = plt.subplots(figsize=(12, 5.5))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,7)

    label(ax, 6, 6.7, "Research Gaps Identified (3 gaps)", fs=12, bold=True, ha='center')

    gaps = [
        ("DATASET",
         "Most studies use only EyePACS or APTOS datasets collected primarily from Asian populations. "
         "External validation on demographically diverse, multi-center datasets is absent in all 8 reviewed papers.",
         "#ffd16633", YELLOW),
        ("METHODOLOGY",
         "No study provides a head-to-head comparison of CNN vs. Vision Transformer architectures under "
         "identical experimental conditions (same dataset, same train/test split, same evaluation protocol).",
         "#6c63ff33", ACCENT),
        ("EXPLAINABILITY",
         "While 6 of 8 papers use Grad-CAM visualizations for saliency mapping, none formally evaluate "
         "whether these explanations are clinically meaningful or actionable for ophthalmologists.",
         "#4ecca333", GREEN),
    ]

    for i, (gap_type, desc, fc, tc) in enumerate(gaps):
        y = 5.5 - i * 1.7
        rbox(ax, 6, y, 11.5, 1.45, CARD2, radius=0.2)
        rbox(ax, 1.1, y+0.42, 1.8, 0.35, fc, gap_type, fs=8, tc=tc, bold=True, radius=0.25)
        ax.text(0.55, y-0.05,
                desc[:110] + "\n" + desc[110:] if len(desc) > 110 else desc,
                ha='left', va='center', fontsize=8.5, color=TEXT, zorder=4, linespacing=1.5)

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/06_gaps_tab.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("6 06_gaps_tab.png")


# ═══════════════════════════════════════════════════════════
# IMAGE 7 — References Tab
# ═══════════════════════════════════════════════════════════
def mockup_references():
    fig, ax = plt.subplots(figsize=(12, 6))
    set_dark(fig, [ax])
    ax.set_xlim(0,12); ax.set_ylim(0,7)

    label(ax, 6, 6.7, "References (8 papers)", fs=12, bold=True, ha='center')

    refs = [
        "[1] Gulshan V, Peng L, Coram M et al. (2024). Deep Learning System for Detecting Diabetic Retinopathy.  DOI: 10.1056/xxx  https://pubmed.ncbi.nlm.nih.gov/38001234/",
        "[2] Chen L, Wang F, Zhang Y (2023). EfficientNet-Based Grading of Diabetic Retinopathy Severity.  DOI: 10.1109/xxx  https://www.semanticscholar.org/paper/abc123",
        "[3] Park S, Kim J, Lee H et al. (2023). Vision Transformer for Retinal Disease Classification.  DOI: 10.1038/xxx  https://pubmed.ncbi.nlm.nih.gov/37654321/",
        "[4] Liu Z, Zhao R, Sun Q (2022). Multi-Task Learning for Joint DR Detection and Lesion Segmentation.  DOI: 10.1007/xxx",
        "[5] Fernandez A, Torres M et al. (2023). Benchmarking CNN Architectures for Fundus Image Analysis.  DOI: 10.1016/xxx",
        "[6] Wang H, Li X (2023). Attention Mechanisms in Retinal Fundus Image Classification.  DOI: 10.1109/yyy",
        "[7] Zhao Y et al. (2022). Self-Supervised Learning for Medical Image Analysis.  DOI: 10.1038/yyy  https://pubmed.ncbi.nlm.nih.gov/36123456/",
        "[8] Kumar R, Patel S, Singh A (2024). Class Imbalance Solutions in Ophthalmic AI.  DOI: 10.1016/yyy",
    ]

    for i, ref in enumerate(refs):
        y = 6.0 - i * 0.73
        ax.plot([0.3, 11.7], [y-0.3, y-0.3], color=BORDER, lw=0.5, zorder=2)
        ax.text(0.5, y, ref[:105] + ("..." if len(ref)>105 else ""),
                ha='left', va='center', fontsize=8, color=MUTED, zorder=4)

    plt.tight_layout(pad=0.3)
    plt.savefig("docs/images/output_mockups/07_references_tab.png", dpi=150,
                bbox_inches='tight', facecolor=BG)
    plt.close()
    print("7 07_references_tab.png")


if __name__ == "__main__":
    print("Generating output mockup images...\n")
    mockup_input()
    mockup_progress()
    mockup_summary()
    mockup_papers()
    mockup_evidence()
    mockup_gaps()
    mockup_references()
    print("\nAll saved to docs/images/output_mockups/")
