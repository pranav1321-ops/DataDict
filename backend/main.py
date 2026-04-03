# backend/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware   # ← Added
from pydantic import BaseModel
from question_processor import process_question

app = FastAPI(title="Olist AI Analytics API")

# ==================== CORS FIX ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =================================================

class QuestionRequest(BaseModel):
    question: str


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid format. Send {\"question\": \"your question\"}"}
    )


@app.get("/")
def health_check():
    return {"status": "API running"}


@app.post("/ask")
def ask_question(request: QuestionRequest):
    print(f"[API] Received: {request.question}")
    return process_question(request.question)