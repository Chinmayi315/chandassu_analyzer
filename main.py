from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from chandassu import analyze_syllables, check_kanda_padya

app = FastAPI(
    title="Chandassu Analyzer API",
    description="Kannada poetic meter (prosody) analysis — classifies syllables "
    "into Laghu (short) and Guru (long), and checks Kanda Padya matra patterns.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="A single line of Kannada text")


class AnalyzeResponse(BaseModel):
    text: str
    syllables: list[dict]
    matra_count: int


class KandaPadyaRequest(BaseModel):
    lines: list[str] = Field(..., min_length=4, max_length=4)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    syllables, total = analyze_syllables(req.text)
    return {
        "text": req.text,
        "syllables": [{"text": s, "weight": w} for s, w in syllables],
        "matra_count": total,
    }


@app.post("/api/check-kanda-padya")
def kanda_padya(req: KandaPadyaRequest):
    try:
        return check_kanda_padya(req.lines)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Serve the demo frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")
