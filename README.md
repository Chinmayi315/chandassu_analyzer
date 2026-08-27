# Chandassu Analyzer — API + Web Demo

Kannada poetic meter (prosody) analyzer. Classifies Kannada syllables into
**Laghu** (short, 1 matra) and **Guru** (long, 2 matras) using rule-based
Unicode text processing, and checks whether a 4-line poem matches the
**Kanda Padya** matra pattern (12-20-12-20).

This wraps the original notebook logic (`kanda_padya_chandassu.ipynb`) in a
FastAPI backend with a live web UI — same algorithm, now servable as a real
product instead of only runnable in a notebook.

## What's new vs. the original notebook
- Core logic extracted into `chandassu.py`, refactored to return structured
  data instead of `print()`ing to a notebook cell
- FastAPI backend (`main.py`) exposing:
  - `POST /api/analyze` — single line → syllable breakdown + matra count
  - `POST /api/check-kanda-padya` — 4 lines → per-line breakdown + verdict
  - `GET /api/health`
- A minimal web UI (`static/index.html`) to demo it live — type Kannada text,
  see each syllable colored by Laghu/Guru with matra weights

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
Then open http://localhost:8000

## Deploy (free, same pattern as your Samvad deployment)
1. Push this folder to a new GitHub repo (or a `webapp/` folder in the
   existing `chandassu_analyzer` repo)
2. Deploy to [Render](https://render.com) as a Web Service:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. You'll get a live URL to put in your resume/portfolio, e.g.
   `https://chandassu-analyzer.onrender.com`

## API example
```bash
curl -X POST https://your-app.onrender.com/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "ಕನ್ನಡ"}'
```
