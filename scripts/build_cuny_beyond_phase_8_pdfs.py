"""Build Phase 8 PDF deliverables using the established phase-document renderer."""

from build_cuny_beyond_phase_7_pdfs import ROOT, build


DOCUMENTS = (
    (ROOT / "docs/CUNY_BEYOND_PHASE_8_PROGRESS.md", ROOT / "output/pdf/CUNY_Beyond_Phase_8_Progress.pdf", "CUNY Beyond | Phase 8 Progress"),
    (ROOT / "docs/CUNY_BEYOND_PHASE_8_TESTER_GUIDE.md", ROOT / "output/pdf/CUNY_Beyond_Phase_8_Tester_Guide.pdf", "CUNY Beyond | Phase 8 Tester Guide"),
)


if __name__ == "__main__":
    for document in DOCUMENTS:
        build(*document)
