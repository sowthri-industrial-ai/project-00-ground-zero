"""Generate synthetic invoice PDF for Document Intelligence demo."""
from pathlib import Path
try:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    print("reportlab not installed · run: uv pip install reportlab")
    raise SystemExit(1)


def main():
    out = Path("data/sample-form.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(out), pagesize=LETTER)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("<b>INVOICE</b>", styles["Title"]),
        Spacer(1, 12),
        Paragraph("Invoice #: INV-2026-0042 &nbsp;&nbsp; Date: 2026-04-24", styles["Normal"]),
        Paragraph("Bill to: Hello AI Demo Customer · Dammam, KSA", styles["Normal"]),
        Spacer(1, 18),
    ]
    data = [
        ["Item", "Qty", "Unit", "Total"],
        ["GPT-4o-mini inference (1K tokens)", "1000", "$0.00015", "$0.15"],
        ["Embedding (1K tokens)", "500", "$0.00002", "$0.01"],
        ["AI Search queries", "250", "$0.00100", "$0.25"],
    ]
    t = Table(data, colWidths=[220, 60, 80, 80])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))
    story += [t, Spacer(1, 12), Paragraph("<b>Total due: $0.41</b>", styles["Normal"])]
    doc.build(story)
    print(f"✓ {out}")


if __name__ == "__main__":
    main()
