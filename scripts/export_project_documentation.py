"""Export the standalone project Markdown documents to polished HTML and PDF."""

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
    KeepTogether,
    ListFlowable,
    ListItem,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "docs" / "attachments" / "project_documentation"
DOCUMENTS = {
    "FEATURES.md": "features",
    "USER_STORIES.md": "user_stories",
    "RUN_LOCAL_MACOS.md": "run_local_macos",
    "RUN_LOCAL_WINDOWS.md": "run_local_windows",
}

CSS = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: #edf3fb; color: #17233c; font-family: Inter, Arial, sans-serif; line-height: 1.58; }
main { max-width: 920px; margin: 36px auto; padding: 54px 64px; background: white; border: 1px solid #dbe5f2; border-radius: 18px; box-shadow: 0 14px 38px rgba(30, 62, 110, .10); }
h1 { margin: 0 0 30px; color: #123f86; font-size: 2.15rem; line-height: 1.18; border-bottom: 4px solid #4d8fdd; padding-bottom: 18px; }
h2 { margin: 34px 0 12px; color: #194f95; font-size: 1.42rem; }
h3 { margin: 26px 0 9px; color: #315f93; font-size: 1.12rem; }
p { margin: 10px 0; }
ul, ol { padding-left: 1.55rem; }
li { margin: 7px 0; }
code { padding: 2px 6px; border-radius: 6px; background: #edf3fa; color: #173a67; font-family: "SFMono-Regular", Consolas, monospace; }
pre { overflow-x: auto; margin: 14px 0 20px; padding: 18px; border-radius: 11px; background: #12213a; color: #f4f8ff; line-height: 1.45; }
pre code { padding: 0; background: transparent; color: inherit; }
a { color: #1768c4; }
.document-note { color: #5a6a82; font-size: .92rem; }
@media (max-width: 700px) { main { margin: 0; padding: 30px 22px; border: 0; border-radius: 0; } }
@media print { body { background: white; } main { max-width: none; margin: 0; padding: 0; border: 0; box-shadow: none; } }
"""


def inline_html(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\[([^]]+)]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', escaped)
    escaped = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1">\1</a>', escaped)
    return escaped


def markdown_to_html(markdown_text: str, title: str) -> str:
    lines = markdown_text.splitlines()
    parts: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            parts.append(f"<p>{inline_html(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            parts.append(f"</{list_kind}>")
            list_kind = None

    for line in lines:
        if line.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                parts.append(f"<pre><code>{html.escape(chr(10).join(code_lines))}</code></pre>")
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
            close_list()
            continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            parts.append(f"<h{level}>{inline_html(heading.group(2))}</h{level}>")
            continue
        bullet = re.match(r"^\s*-\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet or numbered:
            flush_paragraph()
            wanted = "ul" if bullet else "ol"
            if list_kind != wanted:
                close_list()
                list_kind = wanted
                parts.append(f"<{wanted}>")
            parts.append(f"<li>{inline_html((bullet or numbered).group(1))}</li>")
            continue
        paragraph.append(line.strip())
    flush_paragraph()
    close_list()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>{CSS}</style>
</head>
<body>
  <main>
    {''.join(parts)}
    <p class="document-note">Academic Advisement System project documentation</p>
  </main>
</body>
</html>
"""


def pdf_markup(text: str) -> str:
    value = html.escape(text)
    value = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', value)
    value = re.sub(r"\[([^]]+)]\((https?://[^)]+)\)", r'<a href="\2" color="#1768c4">\1</a>', value)
    value = re.sub(r"&lt;(https?://[^&]+)&gt;", r'<a href="\1" color="#1768c4">\1</a>', value)
    return value


class NumberedDocTemplate(BaseDocTemplate):
    def __init__(self, filename: Path, title: str):
        super().__init__(
            str(filename),
            pagesize=letter,
            leftMargin=0.72 * inch,
            rightMargin=0.72 * inch,
            topMargin=0.72 * inch,
            bottomMargin=0.68 * inch,
            title=title,
            author="Academic Advisement System",
        )
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, id="body")
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#d7e2f0"))
        canvas.line(doc.leftMargin, 0.48 * inch, letter[0] - doc.rightMargin, 0.48 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#607089"))
        canvas.drawString(doc.leftMargin, 0.28 * inch, "Academic Advisement System")
        canvas.drawRightString(letter[0] - doc.rightMargin, 0.28 * inch, f"Page {doc.page}")
        canvas.restoreState()


def markdown_to_pdf(markdown_text: str, output: Path, title: str) -> None:
    base = getSampleStyleSheet()
    styles = {
        "h1": ParagraphStyle("Title", parent=base["Title"], fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=colors.HexColor("#123f86"), spaceAfter=22, alignment=TA_CENTER),
        "h2": ParagraphStyle("Heading2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=colors.HexColor("#194f95"), spaceBefore=16, spaceAfter=7, keepWithNext=True),
        "h3": ParagraphStyle("Heading3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=colors.HexColor("#315f93"), spaceBefore=12, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.6, leading=14, textColor=colors.HexColor("#17233c"), spaceAfter=7),
        "list": ParagraphStyle("List", parent=base["BodyText"], fontName="Helvetica", fontSize=9.4, leading=13.5, textColor=colors.HexColor("#17233c")),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=8.1, leading=11, textColor=colors.HexColor("#183a66"), backColor=colors.HexColor("#edf3fa"), borderColor=colors.HexColor("#cfdded"), borderWidth=0.6, borderPadding=9, borderRadius=4, leftIndent=4, rightIndent=4, spaceBefore=5, spaceAfter=10),
    }
    story: list = []
    paragraph: list[str] = []
    list_items: list[ListItem] = []
    list_ordered = False
    list_start = 1
    in_code = False
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            story.append(Paragraph(pdf_markup(" ".join(paragraph)), styles["body"]))
            paragraph.clear()

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            options = {
                "bulletType": "1" if list_ordered else "bullet",
                "leftIndent": 18,
                "bulletFontName": "Helvetica",
                "bulletFontSize": 8.5,
                "spaceAfter": 6,
            }
            if list_ordered:
                options["start"] = list_start
            story.append(ListFlowable(list_items, **options))
            list_items = []

    for line in markdown_text.splitlines():
        if line.startswith("```"):
            flush_paragraph()
            flush_list()
            if in_code:
                story.append(Preformatted("\n".join(code_lines), styles["code"])); code_lines.clear(); in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_lines.append(line)
            continue
        if not line.strip():
            flush_paragraph(); flush_list(); continue
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph(); flush_list()
            level = len(heading.group(1))
            story.append(Paragraph(pdf_markup(heading.group(2)), styles[f"h{level}"]))
            if level == 1:
                story.append(Spacer(1, 3))
            continue
        bullet = re.match(r"^\s*-\s+(.+)$", line)
        numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if bullet or numbered:
            flush_paragraph()
            ordered = numbered is not None
            if list_items and ordered != list_ordered:
                flush_list()
            if not list_items and numbered:
                list_start = int(re.match(r"^\s*(\d+)\.", line).group(1))
            list_ordered = ordered
            content = Paragraph(pdf_markup((bullet or numbered).group(1)), styles["list"])
            list_items.append(ListItem(content, leftIndent=8, spaceAfter=3))
            continue
        paragraph.append(line.strip())
    flush_paragraph(); flush_list()
    NumberedDocTemplate(output, title).build(story)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, output_stem in DOCUMENTS.items():
        source = ROOT / "docs" / source_name
        content = source.read_text(encoding="utf-8")
        title = content.splitlines()[0].removeprefix("# ").strip()
        (OUTPUT_DIR / f"{output_stem}.html").write_text(markdown_to_html(content, title), encoding="utf-8")
        markdown_to_pdf(content, OUTPUT_DIR / f"{output_stem}.pdf", title)


if __name__ == "__main__":
    main()
