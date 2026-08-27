from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "pdf" / "BMCC_Research_Office_FAQ_Prototype_Local_Run_Guide.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

teal = colors.HexColor("#087F7A")
dark = colors.HexColor("#18252D")
coral = colors.HexColor("#EC7C65")
wash = colors.HexColor("#EEF8F6")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="Cover", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=27, leading=32, textColor=dark, alignment=TA_CENTER, spaceAfter=18))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=13, leading=19, textColor=colors.HexColor("#60727C"), alignment=TA_CENTER))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=23, textColor=teal, spaceBefore=12, spaceAfter=9))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=dark, spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontSize=10.2, leading=15, textColor=dark, spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontSize=8.5, leading=12, textColor=colors.HexColor("#60727C")))
styles.add(ParagraphStyle(name="Codex", parent=styles["Code"], fontName="Courier", fontSize=8.3, leading=12, backColor=colors.HexColor("#F3F7F7"), borderPadding=7, spaceAfter=8))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D6E6E4")); canvas.line(0.7*inch, 0.55*inch, 7.8*inch, 0.55*inch)
    canvas.setFont("Helvetica", 8); canvas.setFillColor(colors.HexColor("#60727C"))
    canvas.drawString(0.7*inch, 0.35*inch, "BMCC Research Office FAQ Prototype")
    canvas.drawRightString(7.8*inch, 0.35*inch, f"Page {doc.page}")
    canvas.restoreState()


def p(text, style="Bodyx"):
    return Paragraph(text, styles[style])


story = [Spacer(1, 1.1*inch), p("BMCC Research Office<br/>FAQ Chatbot Prototype", "Cover"), p("Local setup, demonstration, administration, and architecture guide", "Sub"), Spacer(1, .45*inch)]
summary = Table([[p("STUDENT", "Smallx"), p("STAFF", "Smallx"), p("SAFETY", "Smallx")], [p("No-login chat with quick questions and free typing"), p("Search, add, edit, hide, delete, and CSV import"), p("Answers are grounded only in reviewed FAQ evidence")]], colWidths=[2.25*inch]*3)
summary.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),teal),("TEXTCOLOR",(0,0),(-1,0),colors.white),("BACKGROUND",(0,1),(-1,1),wash),("BOX",(0,0),(-1,-1),.6,teal),("INNERGRID",(0,0),(-1,-1),.3,colors.HexColor("#B9D8D4")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9)]))
story += [summary, Spacer(1,.55*inch), p("Prepared from the Research Office planning document Bot4BMCCResearchOffice. Prototype created as an isolated module; it is not committed or pushed to the Academic Advisement repositories.", "Smallx"), PageBreak()]

story += [p("1. What the prototype demonstrates", "H1x"), p("A student visits the local chatbot without logging in, enters a question or selects a quick question, and receives a concise answer from the reviewed FAQ database. Current seed coverage includes CRSP, BFF, CSTEP, undergraduate research, mentors, eligibility, applications, stipends, research experience, and presentations."), p("Each response indicates whether it came from deterministic matching or optional AI-assisted wording. Source links are displayed when the FAQ record contains an approved URL. If no reviewed answer matches, the assistant clearly says so instead of inventing a policy."), p("Staff workflow", "H2x"), p("Research Office staff open <b>/admin</b>, enter the local password, and manage Q&amp;A records. Changes become available to student retrieval immediately. A CSV import supports bulk additions without development help."), p("Document requirements implemented", "H2x")]
for item in ["Lightweight AI used only for language matching and grounded wording.","No open-web answer generation; evidence is restricted to provided/reviewed records.","Self-service staff search, add, edit, visibility control, delete, and import.","Separate design and database so the module can move to its own repository later."]:
    story.append(p("• "+item))
story.append(PageBreak())

story += [p("2. Run on macOS", "H1x"), p("Prerequisite: Python 3.11 or newer."), p("cd research_office_faq_module<br/>python3 -m venv .venv<br/>source .venv/bin/activate<br/>python -m pip install -r requirements.txt<br/>cp .env.example .env<br/>python -m uvicorn app:app --reload --port 8010", "Codex"), p("Edit <b>.env</b> before sharing the prototype. Replace <b>ADMIN_PASSWORD</b>. A Gemini key is optional; without one, deterministic FAQ retrieval remains fully functional."), p("Open <b>http://127.0.0.1:8010</b>. The staff manager is <b>http://127.0.0.1:8010/admin</b>. The included <b>start_mac.command</b> performs the setup and start sequence automatically."), p("3. Run on Windows", "H1x"), p("Install Python 3.11 or newer and enable Add Python to PATH during installation."), p("cd research_office_faq_module<br/>py -m venv .venv<br/>.\\.venv\\Scripts\\Activate.ps1<br/>python -m pip install -r requirements.txt<br/>Copy-Item .env.example .env<br/>python -m uvicorn app:app --reload --port 8010", "Codex"), p("If PowerShell blocks activation, run <b>Set-ExecutionPolicy -Scope Process Bypass</b> and activate again. The included <b>start_windows.bat</b> is the one-click alternative."), PageBreak()]

story += [p("4. Reproducible professor/tester demonstration", "H1x")]
steps=[("1","Open the student chatbot","Visit http://127.0.0.1:8010. No login is required."),("2","Verify a financial answer","Ask: How much does CRSP pay? Confirm the $5,000 total and Fall/Spring/Summer split."),("3","Verify program distinctions","Ask: Can an international student apply to CSTEP? Confirm that CSTEP is distinguished from CRSP and BFF."),("4","Verify safe failure","Ask: Where can I park? Confirm the chatbot reports that no reviewed answer is available."),("5","Add knowledge","Open /admin, enter the .env password, select New FAQ, add a test Q&amp;A, and save."),("6","Verify immediate retrieval","Return to the chatbot and ask the new question. The saved answer should appear without restarting.")]
t=Table([[p("STEP","Smallx"),p("ACTION","Smallx"),p("EXPECTED RESULT","Smallx")]]+[[p(a,"Bodyx"),p(b,"Bodyx"),p(c,"Bodyx")] for a,b,c in steps],colWidths=[.45*inch,1.65*inch,4.65*inch],repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),teal),("TEXTCOLOR",(0,0),(-1,0),colors.white),("GRID",(0,0),(-1,-1),.35,colors.HexColor("#B9D8D4")),("VALIGN",(0,0),(-1,-1),"TOP"),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,wash]),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7)]));story += [t,PageBreak()]

story += [p("5. Architecture and operating modes", "H1x"), p("The FastAPI application serves two static interfaces and JSON endpoints. SQLite stores the knowledge base. The retriever tokenizes the question and ranks FAQ question text, category, and staff keywords with frequency weighting."), p("Deterministic mode", "H2x"), p("When GEMINI_API_KEY is empty or AI assistance is switched off, the best reviewed FAQ answer is returned verbatim. This is the lowest-cost and most predictable operating mode."), p("Grounded AI mode", "H2x"), p("When enabled, only the top retrieved FAQ records are supplied to Gemini. The system prompt forbids adding policies, dates, links, or facts absent from that evidence. A generation failure automatically falls back to the deterministic answer."), p("Approved website references", "H2x"), p("The prototype stores official BMCC URLs as answer citations. It intentionally does not browse or scrape the open web at question time. A later phase can add a controlled, scheduled import of approved BMCC pages with staff review before publication."), p("CSV fields", "H2x"), p("Required: category, question, answer. Optional: keywords, source_url. Use UTF-8 CSV and quote fields that contain commas."), PageBreak()]

story += [p("6. Production readiness roadmap", "H1x")]
for title, body in [("Identity and permissions","Replace the prototype password with BMCC staff single sign-on and role-based permissions."),("Editorial governance","Add draft, reviewed, published, and archived states with reviewer identity and change history."),("Evidence lifecycle","Add review dates, record owners, expiration alerts, and controlled synchronization of approved BMCC pages."),("Quality controls","Test conflicting policies, high-risk eligibility questions, dates, stipend amounts, and no-answer behavior."),("Operations","Add backups, monitoring, structured logs, rate limits, accessibility testing, and deployment configuration."),("Continuous improvement","Record privacy-safe unanswered-question analytics so staff can identify which FAQs to add next.")]:
    story += [p(title,"H2x"),p(body)]
story += [Spacer(1,.2*inch),p("Prototype status", "H2x"), p("Locally runnable and verified for deterministic retrieval, complete stipend data, official source links, staff database loading, and retrieval unit tests. Not yet intended for public production use.")]

doc=SimpleDocTemplate(str(OUT),pagesize=letter,rightMargin=.7*inch,leftMargin=.7*inch,topMargin=.68*inch,bottomMargin=.72*inch,title="BMCC Research Office FAQ Prototype Local Run Guide",author="Academic Advisement Project")
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
