"""Build Phase 9 PDF deliverables using the established phase-document renderer."""

from build_cuny_beyond_phase_7_pdfs import ROOT, build


DOCUMENTS = (
    (ROOT / "docs/CUNY_BEYOND_PHASE_9_PROGRESS.md", ROOT / "output/pdf/CUNY_Beyond_Phase_9_Progress.pdf", "CUNY Beyond | Phase 9 Progress"),
    (ROOT / "docs/CUNY_BEYOND_PHASE_9_TESTER_GUIDE.md", ROOT / "output/pdf/CUNY_Beyond_Phase_9_Tester_Guide.pdf", "CUNY Beyond | Phase 9 Tester Guide"),
)


if __name__ == "__main__":
    for document in DOCUMENTS:
        build(*document)
