"""Build the CUNY Beyond Phase 4 implementation record PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, ListFlowable, ListItem, PageTemplate, Paragraph, Preformatted, Spacer


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "CUNY_BEYOND_PHASE_4_IMPLEMENTATION.md"
OUTPUT = ROOT / "output" / "pdf" / "CUNY_Beyond_Phase_4_Implementation.pdf"


def inline(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" color="#1768c4">\1</a>', value)
    return value


class PhaseDoc(BaseDocTemplate):
    def __init__(self):
        super().__init__(str(OUTPUT), pagesize=letter, leftMargin=.68*inch, rightMargin=.68*inch, topMargin=.7*inch, bottomMargin=.65*inch,
                         title="CUNY Beyond Phase 4 Implementation", author="Academic Advisement System")
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="phase", frames=[frame], onPage=self.decorate))

    @staticmethod
    def decorate(canvas, doc):
        canvas.saveState(); canvas.setFillColor(colors.HexColor("#174ea6")); canvas.rect(0, letter[1]-.18*inch, letter[0], .18*inch, fill=1, stroke=0)
        canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#617089")); canvas.drawString(doc.leftMargin, .28*inch, "CUNY Beyond | Phase 4 Implementation")
        canvas.drawRightString(letter[0]-doc.rightMargin, .28*inch, f"Page {doc.page}"); canvas.restoreState()


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    base = getSampleStyleSheet()
    styles = {
        "h1": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=colors.HexColor("#123f86"), spaceAfter=16),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#174f96"), spaceBefore=12, spaceAfter=6, keepWithNext=True),
        "h3": ParagraphStyle("H3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=colors.HexColor("#17233c"), spaceBefore=7, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.2, textColor=colors.HexColor("#17233c"), spaceAfter=6),
        "list": ParagraphStyle("List", parent=base["BodyText"], fontName="Helvetica", fontSize=9, leading=12.8, textColor=colors.HexColor("#17233c")),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.8, leading=10.5, backColor=colors.HexColor("#edf3fa"), borderColor=colors.HexColor("#cfdded"), borderWidth=.6, borderPadding=8, spaceAfter=8),
    }
    story, paragraph, items, code = [], [], [], []
    in_code = False

    def flush_paragraph():
        if paragraph: story.append(Paragraph(inline(" ".join(paragraph)), styles["body"])); paragraph.clear()

    def flush_items():
        if items:
            story.append(Spacer(1, 3))
            for item in items:
                bullet_style = ParagraphStyle("BulletRow", parent=styles["list"], leftIndent=16, firstLineIndent=-10, spaceAfter=4)
                story.append(Paragraph(inline(item), bullet_style, bulletText="•"))
            items.clear()

    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            flush_paragraph(); flush_items()
            if in_code: story.append(Preformatted("\n".join(code), styles["code"])); code.clear()
            in_code = not in_code; continue
        if in_code: code.append(line); continue
        if not line.strip(): flush_paragraph(); flush_items(); continue
        if line.startswith("# "):
            flush_paragraph(); flush_items(); story.append(Spacer(1, .15*inch)); story.append(Paragraph(inline(line[2:]), styles["h1"])); continue
        if line.startswith("### "):
            flush_paragraph(); flush_items(); story.append(Paragraph(inline(line[4:]), styles["h3"])); continue
        if line.startswith("## "):
            flush_paragraph(); flush_items(); story.append(Paragraph(inline(line[3:]), styles["h2"])); continue
        if re.match(r"^[-*] ", line):
            flush_paragraph(); items.append(line[2:]); continue
        numbered = re.match(r"^\d+\. (.+)$", line)
        if numbered:
            flush_paragraph(); items.append(numbered.group(1)); continue
        paragraph.append(line.strip())
    flush_paragraph(); flush_items(); PhaseDoc().build(story)


if __name__ == "__main__":
    build()
