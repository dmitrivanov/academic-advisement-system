"""Build the share-ready CUNY Beyond module documentation PDFs."""

from build_cuny_beyond_phase_7_pdfs import ROOT, build


SOURCE = ROOT / "docs/cuny_beyond_module"
OUTPUT = ROOT / "output/pdf/cuny_beyond_module"
DOCUMENTS = (
    (SOURCE / "ACCESS_AND_ROUTES.md", OUTPUT / "CUNY_Beyond_Access_and_Routes.pdf", "CUNY Beyond | Access and Routes"),
    (SOURCE / "RUN_LOCAL_MACOS.md", OUTPUT / "CUNY_Beyond_Run_Local_macOS.pdf", "CUNY Beyond | macOS Setup"),
    (SOURCE / "RUN_LOCAL_WINDOWS.md", OUTPUT / "CUNY_Beyond_Run_Local_Windows.pdf", "CUNY Beyond | Windows Setup"),
    (SOURCE / "FEATURES.md", OUTPUT / "CUNY_Beyond_Features.pdf", "CUNY Beyond | Features"),
    (SOURCE / "USER_STORIES.md", OUTPUT / "CUNY_Beyond_User_Stories.pdf", "CUNY Beyond | User Stories"),
)


if __name__ == "__main__":
    for document in DOCUMENTS:
        build(*document)
