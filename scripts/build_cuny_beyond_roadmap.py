"""Build the shareable CUNY Beyond implementation roadmap PDF."""

from __future__ import annotations

import html
import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "CUNY_BEYOND_IMPLEMENTATION_ROADMAP.md"
OUTPUT = ROOT / "output" / "pdf" / "CUNY_Beyond_Implementation_Roadmap.pdf"


def markup(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(
        r"\[([^]]+)]\((https?://[^)]+)\)",
        r'<a href="\2" color="#1768c4">\1</a>',
        value,
    )
    value = re.sub(
        r"(?<!href=&quot;)(https?://[^\s<]+)",
        r'<a href="\1" color="#1768c4">\1</a>',
        value,
    )
    return value


class RoadmapDoc(BaseDocTemplate):
    def __init__(self, filename: Path):
        super().__init__(
            str(filename),
            pagesize=letter,
            leftMargin=0.68 * inch,
            rightMargin=0.68 * inch,
            topMargin=0.68 * inch,
            bottomMargin=0.66 * inch,
            title="CUNY Beyond Implementation Roadmap",
            author="Academic Advisement System",
            subject="Career-first advisement and CUNY Global Search integration roadmap",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="roadmap", frames=[frame], onPage=self.decorate))

    def decorate(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.HexColor("#123f86"))
        canvas.rect(0, letter[1] - 0.18 * inch, letter[0], 0.18 * inch, fill=1, stroke=0)
        canvas.setStrokeColor(colors.HexColor("#d7e2f0"))
        canvas.line(doc.leftMargin, 0.46 * inch, letter[0] - doc.rightMargin, 0.46 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#607089"))
        canvas.drawString(doc.leftMargin, 0.27 * inch, "CUNY Beyond | Implementation Roadmap")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.27 * inch, f"Page {doc.page}")
        canvas.restoreState()


def styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle(
            "RoadmapTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=25,
            leading=30,
            textColor=colors.HexColor("#123f86"),
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h2": ParagraphStyle(
            "RoadmapH2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=colors.HexColor("#174f96"),
            spaceBefore=14,
            spaceAfter=7,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "RoadmapH3",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=11.5,
            leading=14.5,
            textColor=colors.HexColor("#315f93"),
            spaceBefore=9,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "RoadmapBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9.2,
            leading=13.4,
            textColor=colors.HexColor("#17233c"),
            spaceAfter=6,
        ),
        "list": ParagraphStyle(
            "RoadmapList",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#17233c"),
        ),
        "code": ParagraphStyle(
            "RoadmapCode",
            parent=base["Code"],
            fontName="Courier",
            fontSize=7.8,
            leading=10.5,
            textColor=colors.HexColor("#183a66"),
            backColor=colors.HexColor("#edf3fa"),
            borderColor=colors.HexColor("#cfdded"),
            borderWidth=0.6,
            borderPadding=8,
            leftIndent=3,
            rightIndent=3,
            spaceBefore=4,
            spaceAfter=9,
        ),
    }


def build() -> None:
    style = styles()
    story: list = []
    paragraph: list[str] = []
    list_items: list[ListItem] = []
    ordered = False
    list_start = 1
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(markup(" ".join(paragraph)), style["body"]))
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_items
        if not list_items:
            return
        options = {
            "bulletType": "1" if ordered else "bullet",
            "leftIndent": 19,
            "bulletFontName": "Helvetica",
            "bulletFontSize": 8.3,
            "spaceAfter": 5,
        }
        if ordered:
            options["start"] = list_start
        story.append(ListFlowable(list_items, **options))
        list_items = []

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), style["code"]))
                code_lines.clear()
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            if level == 2 and heading.group(2).startswith("Phase "):
                story.append(PageBreak())
            story.append(Paragraph(markup(heading.group(2)), style[f"h{level}"]))
            if level == 1:
                story.append(Spacer(1, 3))
            continue
        bullet = re.match(r"^\s*-\s+(.+)$", line)
        number = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
        if bullet or number:
            flush_paragraph()
            new_ordered = number is not None
            if list_items and new_ordered != ordered:
                flush_list()
            if not list_items and number:
                list_start = int(number.group(1))
            ordered = new_ordered
            value = bullet.group(1) if bullet else number.group(2)
            list_items.append(ListItem(Paragraph(markup(value), style["list"])))
            continue
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    RoadmapDoc(OUTPUT).build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build()
