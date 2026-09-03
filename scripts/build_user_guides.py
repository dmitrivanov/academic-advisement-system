"""Build attachment-ready student, administrator, and degree-tree guides."""

from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image as PILImage, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
GUIDE_DIR = ROOT / "docs" / "guides"
OUTPUT_DIR = ROOT / "output" / "pdf"
SCREENSHOT_DIR = GUIDE_DIR / "assets" / "screenshots"
DIAGRAM_DIR = GUIDE_DIR / "assets" / "diagrams"


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def draw_workflow(path: Path, title: str, nodes: list[tuple[str, str]], accent: str) -> None:
    width, height = 1600, 430
    canvas = PILImage.new("RGB", (width, height), "#f5f8fd")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((12, 12, width - 12, height - 12), radius=28, fill="#ffffff", outline="#cfdbeb", width=3)
    draw.text((58, 40), title, font=font(38, True), fill="#163968")
    box_w = 210
    gap = (width - 120 - box_w * len(nodes)) // max(1, len(nodes) - 1)
    y1, y2 = 145, 335
    for index, (label, note) in enumerate(nodes):
        x1 = 60 + index * (box_w + gap)
        x2 = x1 + box_w
        draw.rounded_rectangle((x1, y1, x2, y2), radius=22, fill=accent, outline="#7fa3cd", width=2)
        draw.text((x1 + 18, y1 + 24), label, font=font(24, True), fill="#17365f")
        words = note.split()
        lines, line = [], ""
        for word in words:
            candidate = f"{line} {word}".strip()
            if draw.textlength(candidate, font=font(18)) > box_w - 36:
                lines.append(line); line = word
            else:
                line = candidate
        if line:
            lines.append(line)
        for row, text in enumerate(lines[:4]):
            draw.text((x1 + 18, y1 + 70 + row * 25), text, font=font(18), fill="#314b6e")
        if index < len(nodes) - 1:
            start = (x2 + 10, (y1 + y2) // 2)
            end = (x2 + gap - 10, (y1 + y2) // 2)
            draw.line((start, end), fill="#4d78aa", width=5)
            draw.polygon([(end[0], end[1]), (end[0] - 18, end[1] - 11), (end[0] - 18, end[1] + 11)], fill="#4d78aa")
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def prepare_visual_assets() -> None:
    draw_workflow(
        DIAGRAM_DIR / "student_workflow.png",
        "Student advising workflow",
        [("Select", "Campus, program, concentration"), ("Record", "Completed courses and WI status"), ("Review", "Requirements, locks, and progress"), ("Plan", "Semesters and elective choices"), ("Confirm", "Download and meet an advisor")],
        "#e8f2ff",
    )
    draw_workflow(
        DIAGRAM_DIR / "admin_workflow.png",
        "Curriculum publication lifecycle",
        [("Source", "Catalog, program page, degree map"), ("Draft", "Metadata, bins, rules, adjustments"), ("Validate", "Structure, totals, references"), ("Review", "Approve or request changes"), ("Publish", "Verify students and retain rollback")],
        "#f0ecff",
    )
    draw_workflow(
        DIAGRAM_DIR / "chatbot_workflow.png",
        "AI Academic Advisement Chatbot workflow",
        [("Describe", "Student situation and career goal"), ("Refine", "Employment, interests, and skills"), ("Review", "Prior learning, AP, and coursework"), ("Explore", "Matched majors, maps, and trees"), ("Prepare", "Degree planner and advising summary")],
        "#e8f7f4",
    )
    for source_name in ["12-admin-dashboard.png", "15-major-constructor-list.png"]:
        source = SCREENSHOT_DIR / source_name
        if not source.exists():
            continue
        image = PILImage.open(source).convert("RGB")
        if image.height > image.width:
            crop_height = min(image.height, int(image.width * 0.72))
            image = image.crop((0, 0, image.width, crop_height))
        image.save(SCREENSHOT_DIR / source_name.replace(".png", "-crop.png"))


def markup(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"\[([^]]+)]\((https?://[^)]+)\)", r'<a href="\2" color="#1768c4">\1</a>', value)
    return value


class GuideDoc(BaseDocTemplate):
    def __init__(self, filename: Path, title: str, audience: str):
        super().__init__(str(filename), pagesize=letter, leftMargin=0.67 * inch, rightMargin=0.67 * inch, topMargin=0.62 * inch, bottomMargin=0.65 * inch, title=title, author="Academic Advisement System")
        self.audience = audience
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="guide", frames=[frame], onPage=self.page_decoration))

    def page_decoration(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d3dfed"))
        canvas.line(doc.leftMargin, 0.46 * inch, letter[0] - doc.rightMargin, 0.46 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#607089"))
        canvas.drawString(doc.leftMargin, 0.27 * inch, f"Academic Advisement System | {self.audience}")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.27 * inch, f"Page {doc.page}")
        canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("GuideTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=25, leading=30, textColor=colors.HexColor("#123f86"), alignment=TA_CENTER, spaceAfter=20),
        "h2": ParagraphStyle("GuideH2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=17, leading=21, textColor=colors.HexColor("#174f96"), spaceAfter=10, keepWithNext=True),
        "h3": ParagraphStyle("GuideH3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#315f93"), spaceBefore=10, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("GuideBody", parent=base["BodyText"], fontName="Helvetica", fontSize=9.7, leading=14.2, textColor=colors.HexColor("#17233c"), spaceAfter=7),
        "quote": ParagraphStyle("GuideQuote", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=9.4, leading=13.5, textColor=colors.HexColor("#38506f"), backColor=colors.HexColor("#eef5fd"), borderColor=colors.HexColor("#7da7d8"), borderWidth=0, borderPadding=9, leftIndent=10, rightIndent=10, spaceAfter=10),
        "list": ParagraphStyle("GuideList", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.5, textColor=colors.HexColor("#17233c")),
        "caption": ParagraphStyle("GuideCaption", parent=base["BodyText"], fontName="Helvetica-Oblique", fontSize=8.2, leading=11, alignment=TA_CENTER, textColor=colors.HexColor("#64748b"), spaceAfter=8),
        "table": ParagraphStyle("GuideTable", parent=base["BodyText"], fontName="Helvetica", fontSize=7.6, leading=10, textColor=colors.HexColor("#17233c")),
    }


def add_image(story: list, md_path: str, alt: str, style_map: dict) -> None:
    image_path = (GUIDE_DIR / md_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(image_path)
    with PILImage.open(image_path) as source:
        width, height = source.size
    max_w, max_h = 7.05 * inch, 5.15 * inch
    scale = min(max_w / width, max_h / height)
    flow = Image(str(image_path), width=width * scale, height=height * scale)
    flow.hAlign = "CENTER"
    story.extend([Spacer(1, 6), flow, Paragraph(markup(alt), style_map["caption"])])


def build_pdf(source: Path, output: Path, audience: str) -> None:
    style_map = styles()
    lines = source.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph: list[str] = []
    list_items: list[ListItem] = []
    ordered = False
    list_start = 1
    table_rows: list[list[str]] = []

    def flush_paragraph():
        if paragraph:
            story.append(Paragraph(markup(" ".join(paragraph)), style_map["body"])); paragraph.clear()

    def flush_list():
        nonlocal list_items
        if list_items:
            opts = dict(bulletType="1" if ordered else "bullet", leftIndent=19, bulletFontName="Helvetica", bulletFontSize=8.5, spaceAfter=6)
            if ordered: opts["start"] = list_start
            story.append(ListFlowable(list_items, **opts)); list_items = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        rows = table_rows
        if len(rows) > 1 and all(re.fullmatch(r":?-+:?", cell.replace(" ", "")) for cell in rows[1]):
            rows = [rows[0]] + rows[2:]
        data = [[Paragraph(markup(cell), style_map["table"]) for cell in row] for row in rows]
        cols = max(len(row) for row in rows)
        table = Table(data, colWidths=[7.0 * inch / cols] * cols, repeatRows=1, hAlign="CENTER")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceafe")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#17365f")),
            ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#bdccde")), ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([Spacer(1, 5), table, Spacer(1, 8)]); table_rows = []

    for line in lines:
        if line.strip() == "<!-- PAGEBREAK -->":
            flush_paragraph(); flush_list(); flush_table(); story.append(PageBreak()); continue
        image_match = re.match(r"^!\[([^]]*)]\(([^)]+)\)$", line.strip())
        if image_match:
            flush_paragraph(); flush_list(); flush_table(); add_image(story, image_match.group(2), image_match.group(1), style_map); continue
        if line.startswith("|") and line.endswith("|"):
            flush_paragraph(); flush_list(); table_rows.append([cell.strip() for cell in line.strip("|").split("|")]); continue
        flush_table()
        if not line.strip():
            flush_paragraph(); flush_list(); continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph(); flush_list(); level = len(heading.group(1)); story.append(Paragraph(markup(heading.group(2)), style_map[f"h{level}"])); continue
        if line.startswith("> "):
            flush_paragraph(); flush_list(); story.append(Paragraph(markup(line[2:]), style_map["quote"])); continue
        bullet = re.match(r"^\s*-\s+(.+)$", line)
        number = re.match(r"^\s*(\d+)\.\s+(.+)$", line)
        if bullet or number:
            flush_paragraph(); new_ordered = number is not None
            if list_items and new_ordered != ordered: flush_list()
            if not list_items and number: list_start = int(number.group(1))
            ordered = new_ordered
            text = bullet.group(1) if bullet else number.group(2)
            list_items.append(ListItem(Paragraph(markup(text), style_map["list"]), leftIndent=8, spaceAfter=3)); continue
        paragraph.append(line.strip())
    flush_paragraph(); flush_list(); flush_table()
    title = lines[0].removeprefix("# ").strip()
    output.parent.mkdir(parents=True, exist_ok=True)
    GuideDoc(output, title, audience).build(story)


def main() -> None:
    prepare_visual_assets()
    # Use compact crops in the PDF while retaining the original full screenshots.
    admin_text = (GUIDE_DIR / "ADMIN_GUIDE.md").read_text(encoding="utf-8")
    admin_text = admin_text.replace("assets/screenshots/12-admin-dashboard.png", "assets/screenshots/12-admin-dashboard-crop.png")
    admin_text = admin_text.replace("assets/screenshots/15-major-constructor-list.png", "assets/screenshots/15-major-constructor-list-crop.png")
    temp_admin = ROOT / "tmp" / "pdfs" / "guides" / "ADMIN_GUIDE_RENDER.md"
    temp_admin.parent.mkdir(parents=True, exist_ok=True)
    temp_admin.write_text(admin_text, encoding="utf-8")
    build_pdf(GUIDE_DIR / "STUDENT_GUIDE.md", OUTPUT_DIR / "academic_advisement_student_guide.pdf", "Student Guide")
    build_pdf(temp_admin, OUTPUT_DIR / "academic_advisement_admin_guide.pdf", "Administrator Guide")
    build_pdf(ROOT / "docs" / "DEGREE_TREE_CONSTRUCTOR_GUIDE.md", OUTPUT_DIR / "degree_map_tree_constructor_guide.pdf", "Degree Tree Constructor Guide")
    build_pdf(GUIDE_DIR / "AI_ACADEMIC_ADVISEMENT_CHATBOT_GUIDE.md", OUTPUT_DIR / "ai_academic_advisement_chatbot_guide.pdf", "Chatbot Guide")


if __name__ == "__main__":
    main()
