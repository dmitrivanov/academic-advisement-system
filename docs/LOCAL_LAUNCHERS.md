# Local Launchers

The protected Admin Dashboard provides self-updating local launchers for macOS and Windows. A signed-in administrator is required both to see the download controls and to access either download endpoint.

## Download addresses

- macOS: `/downloads/macos-launcher`
- Windows: `/downloads/windows-launcher`

Both downloads contain readable source scripts. They do not contain passwords, API keys, or binaries from third parties.

## What the launchers do

1. Verify Git and Python are installed.
2. Refuse to overwrite an unrelated existing `advising2_0` folder.
3. Clone the public repository into the user's home folder, or fast-forward an existing installation from `origin/main`.
4. Create a project-specific Python virtual environment.
5. Install the dependencies declared by the repository.
6. Create a Git-ignored `.env` file with a randomly generated session secret and local demonstration accounts.
7. Optionally store a Gemini key in that local `.env` file.
8. Seed the local database on first installation and after a Git revision changes.
9. Start the FastAPI application and open `http://127.0.0.1:8000`.

Default local accounts are `admin` / `admin` and `tester` / `tester`. They are intentionally limited to local demonstrations and must not be used as hosted credentials.

## macOS

Download and unzip `AI_Academic_Advisement_Mac.zip`. On the first run, Control-click `AI_Academic_Advisement_Mac.command`, choose **Open**, and approve the prompt. Later, double-click the same file to check for updates and launch the app.

The script is packaged with its executable permission. Gatekeeper may still require the Control-click procedure because the project does not distribute an Apple-signed application.

## Windows

Download and unzip `AI_Academic_Advisement_Windows.zip`, then double-click `AI_Academic_Advisement_Windows.cmd`. Windows may display a reputation warning for an unsigned script; review the script and choose to run it only when it came from the official project deployment.

## Safety and updates

- The launchers use `git pull --ff-only`; they do not reset, overwrite, or delete local Git changes.
- `.env`, `advisor.db`, the virtual environment, and the last-seeded marker remain outside Git tracking.
- A non-Git `advising2_0` directory causes the launcher to stop and ask the user to rename it.
- Closing or interrupting the launcher stops the local web server.
- Users can inspect the scripts in a text editor before running them.
