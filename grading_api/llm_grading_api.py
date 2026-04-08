import os
import re # I use it to remove of unwanted symbols
import json
import google.generativeai as genai

from typing import List, Optional
from answer_extractor.extractor import MarkScheme
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

SYSTEM_PROMPT = """You are an expert exam marker. Your job is to grade student answers
against a provided mark scheme and return a structured JSON result.

Rules:
- Be fair and consistent. Award a mark only if the student clearly demonstrates understanding of that point.
- Partial credit is NOT allowed — each marking point is either awarded (1) or not (0).
- Do NOT penalise for spelling/grammar unless it obscures meaning.
- Your response must be ONLY valid JSON — no preamble, no markdown, no explanation outside the JSON.

Return exactly this JSON schema:
{
  "score": <integer>,
  "max_score": <integer>,
  "feedback": "<one sentence summary of the answer quality>",
  "missing_points": ["<exact text of marking points NOT awarded>"],
  "awarded_points": ["<exact text of marking points that WERE awarded>"],
  "confidence": <float between 0.0 and 1.0 indicating your confidence in the grade>
}
"""
#=================================================================
class LLMGradingAPI:
    def __init__(self, score, max_score, feedback, missing_points, awarded_points, confidence):
        self.score = score
        self.max_score = max_score
        self.feedback = feedback
        self.missing_points = missing_points
        self.awarded_points = awarded_points
        self.confidence = confidence

    def to_dict(self):
        return {
            "score": self.score,
            "max_score": self.max_score,
            "feedback": self.feedback,
            "missing_points": self.missing_points,
            "awarded_points": self.awarded_points,
            "confidence": self.confidence,
        }

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)

#=================================================================
def _build_user_prompt(student_answer: str, mark_scheme: MarkScheme) -> str:
    template = (
        "--- MARK SCHEME ---\n"
        "{mark_scheme_text}\n\n"
        "--- STUDENT ANSWER ---\n"
        "{student_answer}\n"
        "Grade the student answer against every marking point listed above.\n"
        "Return only the JSON result."
    )

    return template.format(
        mark_scheme_text=mark_scheme.to_prompt_block(),
        student_answer=student_answer.strip()
    )
#=================================================================
def _parse_response(raw: str, max_score: int) -> LLMGradingAPI: # helping function
    cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON from model: {e}\nRaw output:\n{raw}")

    return LLMGradingAPI(
        score=int(data["score"]),
        max_score=int(data.get("max_score", max_score)),
        feedback=str(data["feedback"]),
        missing_points=list(data.get("missing_points", [])),
        awarded_points=list(data.get("awarded_points", [])),
        confidence=float(data.get("confidence", 0.8)),
    )

#=================================================================
def grade_answer_gemini(student_answer: str, mark_scheme: MarkScheme) -> LLMGradingAPI:
    """Grade student answer using Google's Gemini API"""
    
    api_key = os.getenv("GOOGLE_STUDIO_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_STUDIO_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",  # Free tier model, very fast
        system_instruction=SYSTEM_PROMPT
    )
    
    prompt = _build_user_prompt(student_answer, mark_scheme)

    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=1024,
            temperature=0.0,  # Deterministic output for grading
        ),
    )

    raw_text = response.text
    return _parse_response(raw_text, mark_scheme.max_score)