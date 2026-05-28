ACADEMIC ADVISEMENT ASSISTANT (LOCAL)

This app is a local AI assistant that answers academic advising questions
using your own PDF/TXT documents.

--------------------------------------------------
MAC INSTALLATION
--------------------------------------------------

1. Install Python
   brew install python

2. Install Ollama
   https://ollama.com

3. Pull models
   ollama pull llama3.2
   ollama pull nomic-embed-text

4. Go to project folder
   cd ~/advisor_bot

5. Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

6. Install dependencies
   pip install fastapi uvicorn chromadb pypdf requests python-multipart

7. Build index
   python ingest.py

--------------------------------------------------
RUN THE APP
--------------------------------------------------

Start backend:
   cd ~/advisor_bot
   source venv/bin/activate
   uvicorn app:app --reload

Start frontend (new terminal):
   cd ~/advisor_bot
   python3 -m http.server 5500

Open browser:

Chat:
http://127.0.0.1:5500/frontend/index.html

Admin:
http://127.0.0.1:5500/frontend/admin.html

--------------------------------------------------
UPDATING DOCUMENTS
--------------------------------------------------

1. Add files to:
   docs/

2. Run:
   python ingest.py

--------------------------------------------------
SUPPORTED FILES
--------------------------------------------------

- PDF (.pdf)
- TXT (.txt)

--------------------------------------------------
NOTES
--------------------------------------------------

- Ollama must be installed
- Models must be downloaded
- Uploaded student files are temporary
- App runs fully locally (no cloud)

--------------------------------------------------