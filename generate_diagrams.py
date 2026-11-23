"""
Generate all project diagrams as PNG images for PPT/IEEE paper use.
Output folder: docs/images/
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import os

os.makedirs("docs/images", exist_ok=True)

BG      = "#0f1117"
CARD    = "#1a1d27"
CARD2   = "#22263a"
BORDER  = "#2e3250"
ACCENT  = "#6c63ff"
GREEN   = "#4ecca3"
YELLOW  = "#ffd166"
RED     = "#ff6b6b"
TEXT    = "#e8eaf6"
MUTED   = "#8b90b0"
WHITE   = "#ffffff"

def set_dark(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

def rounded_box(ax, x, y, w, h, color, text, fontsize=9, text_color=WHITE, radius=0.15, alpha=1.0, bold=False):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                         boxstyle=f"round,pad=0.05,rounding_size={radius}",
                         linewidth=1.2, edgecolor=BORDER,
                         facecolor=color, alpha=alpha, zorder=3)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha='center', va='center',
            fontsize=fontsize, color=text_color, fontweight=weight, zorder=4,
            wrap=True)

def arrow_down(ax, x, y_start, y_end, color=MUTED):
    ax.annotate("", xy=(x, y_end), xytext=(x, y_start),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), zorder=2)

def arrow_right(ax, x_start, x_end, y, color=MUTED):
    ax.annotate("", xy=(x_end, y), xytext=(x_start, y),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.5), zorder=2)

# ═══════════════════════════════════════════════════════════════
# DIAGRAM 1 — Full System Workflow
# ═══════════════════════════════════════════════════════════════
def diagram_workflow():
    fig, ax = plt.subplots(figsize=(10, 16))
    set_dark(fig, ax)
    ax.set_ylim(0, 18)

    title_txt = "Healthcare Literature Analyzer — System Workflow"
    ax.text(5, 17.5, title_txt, ha='center', va='center',
            fontsize=12, color=WHITE, fontweight='bold')

    steps = [
        (16.8, ACCENT,  "🔍  User Research Question",             "e.g. 'ML methods for diabetic retinopathy'", 10),
        (15.5, CARD2,   "Research Agent",                         "Decomposes question → generates search queries",  9),
        (14.2, CARD2,   "Literature Retrieval",                   "PubMed API  +  Semantic Scholar API",             9),
        (12.9, CARD2,   "Deduplication & Normalisation",          "Merge sources · Remove duplicates by DOI/PMID",   9),
        (11.6, CARD2,   "Document Processing",                    "Abstract → Clean Text → Sentence Chunks",         9),
        (10.3, CARD2,   "RAG Ingestion",                          "Embed chunks → Store in Qdrant vector DB",        9),
        ( 9.0, CARD2,   "Evidence Extraction Agent",              "Objective · Dataset · Methodology · Results",     9),
        ( 7.7, CARD2,   "Evidence Validation Agent",              "Claim ↔ Source Passage → Supported/Unsupported",  9),
        ( 6.4, CARD2,   "Synthesis Agent",                        "Cross-paper comparison · Contradiction detection",9),
        ( 5.1, CARD2,   "Gap Analysis Agent",                     "Research gaps from paper limitations",            9),
        ( 3.8, CARD2,   "Report Generation Agent",                "Assembles structured report + citations",         9),
        ( 2.3, GREEN,   "📄  Structured Research Report",         "Findings · Evidence · Gaps · References",        10),
    ]

    for y, color, label, sublabel, fs in steps:
        rounded_box(ax, 5, y, 8.5, 0.9, color, label, fontsize=fs, bold=(color!=CARD2))
        if sublabel:
            ax.text(5, y - 0.32, sublabel, ha='center', va='center',
                    fontsize=7.5, color=MUTED, style='italic', zorder=4)

    for i in range(len(steps) - 1):
        y_top = steps[i][0] - 0.45
        y_bot = steps[i+1][0] + 0.45
        arrow_down(ax, 5, y_top, y_bot, color=ACCENT)

    # Side labels
    side = [
        (15.5, "LangGraph"),
        (14.2, "API layer"),
        (12.9, "metadata.py"),
        (11.6, "processor.py"),
        (10.3, "pipeline.py"),
        ( 9.0, "evidence_agent.py"),
        ( 7.7, "validation_agent.py"),
        ( 6.4, "synthesis_agent.py"),
        ( 5.1, "gap_agent.py"),
        ( 3.8, "report_agent.py"),
    ]
    for y, label in side:
        ax.text(9.6, y, label, ha='left', va='center',
                fontsize=7, color=MUTED, style='italic', zorder=4)

    plt.tight_layout(pad=0.5)
    plt.savefig("docs/images/01_system_workflow.png", dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("✓ 01_system_workflow.png")


# ═══════════════════════════════════════════════════════════════
# DIAGRAM 2 — Agent Architecture
# ═══════════════════════════════════════════════════════════════
def diagram_agents():
    fig, ax = plt.subplots(figsize=(12, 7))
    set_dark(fig, ax)
    ax.set_ylim(0, 8)
    ax.set_xlim(0, 12)

    ax.text(6, 7.6, "Multi-Agent Architecture", ha='center', fontsize=13,
            color=WHITE, fontweight='bold')

    # Orchestrator
    rounded_box(ax, 6, 6.6, 5, 0.75, ACCENT, "LangGraph Orchestrator\n(workflow.py)", fontsize=10, bold=True)

    agents = [
        (1.2,  4.5, "🔎 Research\nAgent",     CARD2),
        (3.2,  4.5, "🧪 Evidence\nAgent",     CARD2),
        (5.2,  4.5, "✅ Validation\nAgent",   CARD2),
        (7.2,  4.5, "🔗 Synthesis\nAgent",    CARD2),
        (9.2,  4.5, "🕳️ Gap\nAgent",         CARD2),
        (11.2, 4.5, "📄 Report\nAgent",       CARD2),
    ]

    for x, y, label, color in agents:
        rounded_box(ax, x, y, 1.7, 1.1, color, label, fontsize=8)
        # Arrow from orchestrator
        ax.annotate("", xy=(x, y + 0.55), xytext=(6, 6.22),
                    arrowprops=dict(arrowstyle="-|>", color=BORDER, lw=1.2), zorder=2)

    # Shared resources row
    resources = [
        (2.5, 2.2, "PubMed\nAPI",        "#1e3a5f"),
        (4.5, 2.2, "Semantic\nScholar",  "#1e3a5f"),
        (6.5, 2.2, "Qdrant\nVector DB",  "#2d1f5e"),
        (8.5, 2.2, "Gemini\n2.5 Flash",  "#1f3d2e"),
        (10.5,2.2, "PostgreSQL\nDB",     "#3d2a1e"),
    ]
    ax.text(6, 3.0, "Shared Resources", ha='center', fontsize=9, color=MUTED)
    for x, y, label, color in resources:
        rounded_box(ax, x, y, 1.7, 0.9, color, label, fontsize=8)

    # Connect evidence agent to Gemini
    ax.plot([3.2, 8.5], [3.95, 2.65], color=BORDER, lw=0.8, linestyle='--', zorder=1)
    ax.plot([1.2, 2.5], [3.95, 2.65], color=BORDER, lw=0.8, linestyle='--', zorder=1)
    ax.plot([5.2, 6.5], [3.95, 2.65], color=BORDER, lw=0.8, linestyle='--', zorder=1)

    # Sequential flow arrow
    ax.annotate("Sequential execution →", xy=(11.8, 4.5), xytext=(0.3, 4.5),
                fontsize=7.5, color=MUTED, ha='left',
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=0.8))

    ax.text(6, 0.5, "AgentState (Pydantic) passed through each node — carries question, papers, evidence, claims, report",
            ha='center', fontsize=7.5, color=MUTED, style='italic')

    plt.tight_layout(pad=0.5)
    plt.savefig("docs/images/02_agent_architecture.png", dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("✓ 02_agent_architecture.png")


# ═══════════════════════════════════════════════════════════════
# DIAGRAM 3 — RAG Pipeline
# ═══════════════════════════════════════════════════════════════
def diagram_rag():
    fig, ax = plt.subplots(figsize=(12, 6))
    set_dark(fig, ax)
    ax.set_ylim(0, 7)
    ax.set_xlim(0, 12)

    ax.text(6, 6.6, "RAG Pipeline — Ingestion & Retrieval", ha='center',
            fontsize=13, color=WHITE, fontweight='bold')

    # --- Ingestion row ---
    ax.text(6, 5.9, "INGESTION (at startup — once per paper)", ha='center',
            fontsize=9, color=GREEN, fontweight='bold')

    ingest = [
        (1.0, 4.9, "📄 Paper\nAbstract / PDF",  CARD2),
        (3.0, 4.9, "🧹 Text\nCleaning",          CARD2),
        (5.0, 4.9, "✂️ Sentence\nChunking",      CARD2),
        (7.0, 4.9, "🔢 Embedding\n(BGE model)",  "#2d1f5e"),
        (9.5, 4.9, "🗃️ Qdrant\nVector Store",   "#1f3d2e"),
    ]
    for x, y, label, color in ingest:
        rounded_box(ax, x, y, 1.7, 0.9, color, label, fontsize=8)
    for i in range(len(ingest)-1):
        arrow_right(ax, ingest[i][0]+0.85, ingest[i+1][0]-0.85, 4.9, color=ACCENT)

    # Metadata note
    ax.text(9.5, 4.3, "Stored with metadata:\ntitle · authors · year · DOI\nsection · chunk_id",
            ha='center', fontsize=7, color=MUTED, style='italic')

    # --- Retrieval row ---
    ax.text(6, 3.6, "RETRIEVAL (at query time — per research question)", ha='center',
            fontsize=9, color=YELLOW, fontweight='bold')

    retrieval = [
        (1.0, 2.7, "❓ Research\nQuestion",       ACCENT),
        (3.0, 2.7, "🔢 Query\nEmbedding",         "#2d1f5e"),
        (5.0, 2.7, "🔍 Cosine\nSimilarity Search","#2d1f5e"),
        (7.0, 2.7, "📋 Top-8\nChunks",            CARD2),
        (9.5, 2.7, "📝 Context\nfor LLM",         "#1e3a5f"),
    ]
    for x, y, label, color in retrieval:
        rounded_box(ax, x, y, 1.7, 0.9, color, label, fontsize=8)
    for i in range(len(retrieval)-1):
        arrow_right(ax, retrieval[i][0]+0.85, retrieval[i+1][0]-0.85, 2.7, color=YELLOW)

    # Qdrant connects down
    ax.annotate("", xy=(9.5, 3.15), xytext=(9.5, 4.45),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.5, linestyle='dashed'))
    ax.text(9.9, 3.8, "search", fontsize=7, color=GREEN, rotation=90)

    # --- Generation row ---
    ax.text(6, 1.9, "GENERATION", ha='center', fontsize=9, color=RED, fontweight='bold')

    gen = [
        (3.0, 1.1, "🤖 Gemini 2.5\nFlash (LLM)",   "#1f3d2e"),
        (6.5, 1.1, "✅ Validation\nAgent",           CARD2),
        (10.0,1.1, "📄 Evidence-grounded\nResponse", GREEN),
    ]
    for x, y, label, color in gen:
        rounded_box(ax, x, y, 2.4, 0.9, color, label, fontsize=8)
    for i in range(len(gen)-1):
        arrow_right(ax, gen[i][0]+1.2, gen[i+1][0]-1.2, 1.1, color=RED)

    ax.annotate("", xy=(3.0, 1.55), xytext=(9.5, 2.25),
                arrowprops=dict(arrowstyle="-|>", color=YELLOW, lw=1.2))

    plt.tight_layout(pad=0.5)
    plt.savefig("docs/images/03_rag_pipeline.png", dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("✓ 03_rag_pipeline.png")


# ═══════════════════════════════════════════════════════════════
# DIAGRAM 4 — Evidence Validation
# ═══════════════════════════════════════════════════════════════
def diagram_validation():
    fig, ax = plt.subplots(figsize=(11, 7))
    set_dark(fig, ax)
    ax.set_ylim(0, 8)
    ax.set_xlim(0, 11)

    ax.text(5.5, 7.6, "Evidence Validation — How Claims Are Verified", ha='center',
            fontsize=12, color=WHITE, fontweight='bold')

    # Input
    rounded_box(ax, 5.5, 6.7, 7, 0.8, ACCENT, "Generated Output from LLM (synthesis / findings)", fontsize=10, bold=True)

    # Claim extraction
    rounded_box(ax, 5.5, 5.6, 5, 0.75, CARD2, "Claim Extractor\nBreaks output into individual verifiable statements", fontsize=8.5)
    arrow_down(ax, 5.5, 6.3, 5.98, color=ACCENT)

    # Claims
    claims = [
        (1.5, 4.3, '"CNNs achieve 97%\nAUC on EyePACS"'),
        (4.5, 4.3, '"Transfer learning\nimproves small datasets"'),
        (7.5, 4.3, '"Model deployed in\n50 hospitals"'),
        (10.0,4.3, '"Transformers outperform\nCNNs on all metrics"'),
    ]
    for x, y, text in claims:
        rounded_box(ax, x, y, 2.4, 0.85, CARD2, text, fontsize=7.5)
        ax.annotate("", xy=(x, y+0.43), xytext=(5.5, 5.22),
                    arrowprops=dict(arrowstyle="-|>", color=BORDER, lw=1.0))

    # Qdrant retrieval
    rounded_box(ax, 5.5, 2.95, 4, 0.7, "#2d1f5e", "Qdrant: Retrieve top-3 matching source passages", fontsize=8.5)
    for x, _, _ in claims:
        ax.annotate("", xy=(5.5, 3.3), xytext=(x, 3.87),
                    arrowprops=dict(arrowstyle="-|>", color=BORDER, lw=0.9))

    # Entailment check
    rounded_box(ax, 5.5, 2.1, 4, 0.65, CARD2, "LLM Entailment Check: Does passage support claim?", fontsize=8.5)
    arrow_down(ax, 5.5, 2.6, 2.43, color=YELLOW)

    # Result labels
    results = [
        (1.5,  1.1, "✅ Supported",              GREEN,  '"CNNs achieve 97%..."'),
        (4.0,  1.1, "✅ Supported",              GREEN,  '"Transfer learning..."'),
        (6.8,  1.1, "❌ Unsupported",            RED,    '"Deployed in 50..."'),
        (9.5,  1.1, "⚠️ Partially\nSupported", YELLOW, '"Transformers beat..."'),
    ]
    for x, y, label, color, _ in results:
        rounded_box(ax, x, y, 2.2, 0.75, color+"22", label, fontsize=8.5, text_color=color, bold=True)
        ax.annotate("", xy=(x, y+0.38), xytext=(5.5, 1.77),
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=1.1))

    # Legend
    legend_items = [
        (GREEN,  "Supported — passage directly confirms claim"),
        (YELLOW, "Partially Supported — related but incomplete"),
        (RED,    "Unsupported — no passage confirms claim"),
        (MUTED,  "Insufficient Evidence — inconclusive"),
    ]
    for i, (color, label) in enumerate(legend_items):
        ax.add_patch(plt.Rectangle((0.1, 0.55 - i*0.0), 0.25, 0.18, color=color, zorder=5))
        ax.text(0.45, 0.64 - i*0.0, label, fontsize=7, color=MUTED, va='center', zorder=5)

    plt.tight_layout(pad=0.5)
    plt.savefig("docs/images/04_evidence_validation.png", dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("✓ 04_evidence_validation.png")


# ═══════════════════════════════════════════════════════════════
# DIAGRAM 5 — Output Report Structure
# ═══════════════════════════════════════════════════════════════
def diagram_output():
    fig, ax = plt.subplots(figsize=(12, 7))
    set_dark(fig, ax)
    ax.set_ylim(0, 8)
    ax.set_xlim(0, 12)

    ax.text(6, 7.6, "System Output — Structured Research Report", ha='center',
            fontsize=13, color=WHITE, fontweight='bold')

    # Input box
    rounded_box(ax, 6, 6.8, 9, 0.75, ACCENT,
                "Input: \"What are ML approaches for early detection of diabetic retinopathy?\"",
                fontsize=9.5, bold=True)

    # Output sections — 2 rows of 3
    sections = [
        # Row 1
        (1.8, 5.3, "📋 Executive\nSummary",
         "150-word overview of\nall retrieved findings", GREEN),
        (5.0, 5.3, "📌 Key Findings",
         "5–8 bullet points\nextracted from papers", GREEN),
        (8.5, 5.3, "📚 Papers Analyzed",
         "Title · Authors · Year\nAbstract · DOI · URL", GREEN),
        # Row 2
        (1.8, 3.3, "🧾 Validated Claims",
         "Each claim labeled:\nSupported / Partial /\nUnsupported", YELLOW),
        (5.0, 3.3, "🔗 Literature\nSynthesis",
         "Cross-paper comparison\nMethodology · Contradictions", YELLOW),
        (8.5, 3.3, "🕳️ Research\nGaps",
         "Dataset · Methodology\nPopulation · Reproducibility", YELLOW),
        # Row 3 center
        (6.0, 1.4, "📖 References",
         "Formatted citations for every paper retrieved\nAuthor · Year · Title · DOI · URL", GREEN),
    ]

    for x, y, label, sublabel, color in sections:
        rounded_box(ax, x, y, 2.9, 1.5, CARD2, label, fontsize=9.5, bold=True)
        ax.text(x, y - 0.35, sublabel, ha='center', va='center',
                fontsize=7.5, color=MUTED, style='italic', zorder=4)
        # Colour accent bar at top of card
        rounded_box(ax, x, y + 0.62, 2.9, 0.26, color, "", fontsize=1, alpha=0.5, radius=0.1)

        # Arrow from input
        ax.annotate("", xy=(x, y+0.75), xytext=(6, 6.42),
                    arrowprops=dict(arrowstyle="-|>", color=BORDER, lw=0.9), zorder=1)

    ax.text(6, 0.3,
            "Every section is traceable to retrieved papers  ·  No hallucinated references  ·  Claims show evidence status",
            ha='center', fontsize=8, color=MUTED, style='italic')

    plt.tight_layout(pad=0.5)
    plt.savefig("docs/images/05_output_structure.png", dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("✓ 05_output_structure.png")


# ═══════════════════════════════════════════════════════════════
# DIAGRAM 6 — Problem vs Solution comparison
# ═══════════════════════════════════════════════════════════════
def diagram_problem_solution():
    fig, ax = plt.subplots(figsize=(12, 7))
    set_dark(fig, ax)
    ax.set_ylim(0, 8)
    ax.set_xlim(0, 12)

    ax.text(6, 7.6, "Problem vs Solution", ha='center',
            fontsize=13, color=WHITE, fontweight='bold')

    # Divider
    ax.plot([6, 6], [0.3, 7.1], color=BORDER, lw=1.5, linestyle='--')
    ax.text(3, 7.1, "❌  Without This System", ha='center', fontsize=11,
            color=RED, fontweight='bold')
    ax.text(9, 7.1, "✅  With This System", ha='center', fontsize=11,
            color=GREEN, fontweight='bold')

    pairs = [
        ("Manual search across multiple\ndatabases — days of work",
         "Automatic multi-source retrieval\nfrom PubMed + Semantic Scholar"),
        ("Read & compare 20–50 papers\none by one",
         "Structured evidence extracted\nfrom every paper automatically"),
        ("AI chatbots hallucinate\npaper titles and statistics",
         "Every claim validated against\nthe actual source passage"),
        ("No way to know if AI output\nis supported by real evidence",
         "Claims labeled: Supported /\nPartial / Unsupported / Insufficient"),
        ("Research gaps identified only\nby expert domain knowledge",
         "Gaps identified from paper\nlimitations sections automatically"),
        ("Output is a chat message\nwith no citations",
         "Structured report with formatted\nreferences and DOIs"),
    ]

    for i, (prob, sol) in enumerate(pairs):
        y = 6.3 - i * 0.98
        rounded_box(ax, 3, y, 5.5, 0.75, "#2d1215", prob, fontsize=8.5, text_color="#ffaaaa")
        rounded_box(ax, 9, y, 5.5, 0.75, "#122d1a", sol,  fontsize=8.5, text_color="#aaffcc")

    plt.tight_layout(pad=0.5)
    plt.savefig("docs/images/06_problem_solution.png", dpi=150, bbox_inches='tight',
                facecolor=BG)
    plt.close()
    print("✓ 06_problem_solution.png")


# ── Run all ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("Generating diagrams...\n")
    diagram_workflow()
    diagram_agents()
    diagram_rag()
    diagram_validation()
    diagram_output()
    diagram_problem_solution()
    print("\nAll diagrams saved to docs/images/")
    print("Files:")
    for f in sorted(os.listdir("docs/images")):
        print(f"  docs/images/{f}")
