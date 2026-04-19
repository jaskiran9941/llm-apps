"""
Converts the eBay Live knowledge base (system prompt) into a formatted PDF.
Output: knowledge-base/ebay_live_knowledge_base.pdf
"""

import re
from pathlib import Path
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "stage-1-chatbot" / "backend" / "system_prompt.md"
OUTPUT_PATH = Path(__file__).parent / "ebay_live_knowledge_base.pdf"


def build_styles():
    styles = getSampleStyleSheet()
    custom = {
        "title": ParagraphStyle("title", fontSize=22, fontName="Helvetica-Bold",
                                 textColor=colors.HexColor("#e43142"), spaceAfter=6, alignment=TA_CENTER),
        "subtitle": ParagraphStyle("subtitle", fontSize=11, fontName="Helvetica",
                                    textColor=colors.HexColor("#555555"), spaceAfter=20, alignment=TA_CENTER),
        "h2": ParagraphStyle("h2", fontSize=14, fontName="Helvetica-Bold",
                              textColor=colors.HexColor("#e43142"), spaceBefore=16, spaceAfter=6),
        "body": ParagraphStyle("body", fontSize=10, fontName="Helvetica",
                                leading=16, spaceAfter=4, textColor=colors.HexColor("#222222")),
        "bullet": ParagraphStyle("bullet", fontSize=10, fontName="Helvetica",
                                  leading=16, spaceAfter=3, leftIndent=16,
                                  textColor=colors.HexColor("#222222")),
        "bold_bullet": ParagraphStyle("bold_bullet", fontSize=10, fontName="Helvetica-Bold",
                                       leading=16, spaceAfter=3, leftIndent=16,
                                       textColor=colors.HexColor("#222222")),
    }
    return custom


def parse_and_build(md_text: str, styles: dict) -> list:
    story = []
    story.append(Paragraph("eBay Live Knowledge Base", styles["title"]))
    story.append(Paragraph("Source of truth used by the eBay Live Support Chatbot", styles["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#e43142")))
    story.append(Spacer(1, 0.2 * inch))

    for line in md_text.splitlines():
        line = line.strip()
        if not line:
            story.append(Spacer(1, 0.05 * inch))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], styles["h2"]))
        elif line.startswith("# "):
            pass  # skip top-level title, we have our own
        elif line.startswith("You are a helpful"):
            pass  # skip system prompt persona line
        elif line.startswith("- **") and "**:" in line:
            # Bold label: rest of text
            parts = line[2:].split("**:", 1)
            label = parts[0].replace("**", "")
            rest = parts[1].strip() if len(parts) > 1 else ""
            text = f"<b>{label}:</b> {rest}"
            story.append(Paragraph(f"• {text}", styles["bullet"]))
        elif line.startswith("- "):
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line[2:])
            story.append(Paragraph(f"• {text}", styles["bullet"]))
        else:
            text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
            story.append(Paragraph(text, styles["body"]))

    return story


def generate():
    md_text = SYSTEM_PROMPT_PATH.read_text()
    styles = build_styles()
    story = parse_and_build(md_text, styles)

    OUTPUT_PATH.parent.mkdir(exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=LETTER,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
    )
    doc.build(story)
    print(f"PDF saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
