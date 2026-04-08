import os, json
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from pdf_preprocessing.pdf_preprocessing import extract_text_from_bytes
from answer_extractor.extractor import load_mark_scheme, MarkScheme
from grading_api.llm_grading_api import grade_answer_gemini
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

app = FastAPI(title="AI Grading Tool")
UI_PATH = r"F:/Omar 3amora/AI Grading Sys/UI/ui.html"
OUTPUT_DIR = r"F:/Omar 3amora/AI Grading Sys/Output_result"

def save_result(result: dict, filename: str):
    path = os.path.join(OUTPUT_DIR, f"{filename}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return path

@app.get("/", response_class=HTMLResponse)
def index():
    with open(UI_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/grade/pdf")
async def grade_pdf(
    pdf: UploadFile = File(...),
    mark_scheme_json: str = Form(None),
    filename: str = Form("grading_result"), 
    ):
    if not pdf.filename.lower().endswith(".pdf"):
        return JSONResponse({"error": "Uploaded file must be a PDF."}, status_code=400)
    
    pdf_bytes = await pdf.read()
    try:
        student_answer = extract_text_from_bytes(pdf_bytes)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=422)
    
    scheme = load_mark_scheme_from_json(mark_scheme_json)

    # Check if API key is set
    api_key = os.getenv("GOOGLE_STUDIO_API_KEY")
    if not api_key:
        return JSONResponse(
            {"error": "GOOGLE_STUDIO_API_KEY environment variable is required"},
            status_code=400
        )
    
    try:
        result = grade_answer_gemini(student_answer, scheme)
        data = result.to_dict()
        save_result(data, filename)
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse(
            {"error": f"Grading failed: {str(e)}"},
            status_code=500
        )

@app.post("/grade/text")
async def grade_text(
    answer: str = Form(...),
    mark_scheme_json: str = Form(None),
    filename: str = Form("grading_result"),
):
    if not answer.strip():
        return JSONResponse({"error": "'answer' field cannot be empty."}, status_code=400)
    
    scheme = load_mark_scheme_from_json(mark_scheme_json)
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_STUDIO_API_KEY")
    if not api_key:
        return JSONResponse(
            {"error": "GOOGLE_STUDIO_API_KEY environment variable is required"},
            status_code=400
        )
    
    try:
        result = grade_answer_gemini(answer.strip(), scheme)
        data = result.to_dict()
        save_result(data, filename)
        return JSONResponse(data)
    except Exception as e:
        return JSONResponse(
            {"error": f"Grading failed: {str(e)}"},
            status_code=500
        )

def load_mark_scheme_from_json(mark_scheme_json: str):
    if mark_scheme_json:
        try:
            data = json.loads(mark_scheme_json)
            return MarkScheme(
                question=data["question"],
                max_score=data["max_score"],
                marking_points=data["marking_points"],
                topic=data.get("topic"),
            )
        except (json.JSONDecodeError, KeyError):
            return load_mark_scheme()
    return load_mark_scheme()