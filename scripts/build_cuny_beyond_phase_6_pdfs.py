"""Build the two Phase 6 PDF deliverables from their Markdown sources."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Preformatted, Spacer


ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    (ROOT / "docs/CUNY_BEYOND_PHASE_6_PROGRESS.md", ROOT / "output/pdf/CUNY_Beyond_Phase_6_Progress.pdf", "CUNY Beyond | Phase 6 Progress"),
    (ROOT / "docs/CUNY_BEYOND_PHASE_6_TESTER_GUIDE.md", ROOT / "output/pdf/CUNY_Beyond_Phase_6_Tester_Guide.pdf", "CUNY Beyond | Phase 6 Tester Guide"),
)


def inline(text):
    value = html.escape(text)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"(https?://[^\s<]+)", r'<a href="\1" color="#1768c4">\1</a>', value)
    return value


class PhaseDoc(BaseDocTemplate):
    def __init__(self, output, title, footer):
        self.footer = footer
        super().__init__(str(output), pagesize=letter, leftMargin=.7*inch, rightMargin=.7*inch,
                         topMargin=.72*inch, bottomMargin=.65*inch, title=title,
                         author="Academic Advisement System")
        self.addPageTemplates(PageTemplate(id="body", frames=[Frame(self.leftMargin, self.bottomMargin, self.width, self.height)], onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState(); canvas.setFillColor(colors.HexColor("#174ea6")); canvas.rect(0, letter[1]-.18*inch, letter[0], .18*inch, fill=1, stroke=0)
        canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#617089")); canvas.drawString(doc.leftMargin, .28*inch, self.footer)
        canvas.drawRightString(letter[0]-doc.rightMargin, .28*inch, f"Page {doc.page}"); canvas.restoreState()


def build(source, output, footer):
    output.parent.mkdir(parents=True, exist_ok=True)
    base = getSampleStyleSheet()
    styles = {
        "h1": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#123f86"), spaceAfter=14),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=colors.HexColor("#174f96"), spaceBefore=11, spaceAfter=6, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13.3, textColor=colors.HexColor("#17233c"), spaceAfter=6),
        "list": ParagraphStyle("List", parent=base["BodyText"], fontName="Helvetica", fontSize=9, leading=12.7, leftIndent=16, firstLineIndent=-10, textColor=colors.HexColor("#17233c"), spaceAfter=4),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.8, leading=10.5, backColor=colors.HexColor("#edf3fa"), borderPadding=8),
    }
    story, paragraph, code = [], [], []
    in_code = False

    def flush():
        if paragraph:
            story.append(Paragraph(inline(" ".join(paragraph)), styles["body"])); paragraph.clear()

    for line in source.read_text(encoding="utf-8").splitlines():
        if line.startswith("```"):
            flush()
            if in_code: story.append(Preformatted("\n".join(code), styles["code"])); code.clear()
            in_code = not in_code; continue
        if in_code: code.append(line); continue
        if not line.strip(): flush(); continue
        if line.startswith("# "): flush(); story.append(Spacer(1, 6)); story.append(Paragraph(inline(line[2:]), styles["h1"])); continue
        if line.startswith("## "): flush(); story.append(Paragraph(inline(line[3:]), styles["h2"])); continue
        numbered = re.match(r"^(\d+)\. (.+)$", line)
        if numbered: flush(); story.append(Paragraph(inline(numbered.group(2)), styles["list"], bulletText=numbered.group(1)+".")); continue
        if re.match(r"^[-*] ", line): flush(); story.append(Paragraph(inline(line[2:]), styles["list"], bulletText="•")); continue
        paragraph.append(line.strip())
    flush()
    PhaseDoc(output, source.stem.replace("_", " ").title(), footer).build(story)


if __name__ == "__main__":
    for document in DOCUMENTS:
        build(*document)

