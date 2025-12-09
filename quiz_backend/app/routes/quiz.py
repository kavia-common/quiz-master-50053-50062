from typing import Any, Dict, List, Optional, Tuple
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint

# In-memory data store for questions and user scores.
# This is a simple store; no persistence beyond process lifetime.
_QUESTIONS: List[Dict[str, Any]] = [
    {
        "id": 1,
        "text": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer_index": 2,
        "difficulty": "easy",
    },
    {
        "id": 2,
        "text": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Venus"],
        "answer_index": 1,
        "difficulty": "easy",
    },
    {
        "id": 3,
        "text": "What is 9 x 9?",
        "options": ["72", "81", "99", "108"],
        "answer_index": 1,
        "difficulty": "medium",
    },
]

# userId -> {"score": int, "total": int}
_USER_SCORES: Dict[str, Dict[str, int]] = {}

blp = Blueprint(
    "Quiz",
    "quiz",
    url_prefix="/api",
    description="Quiz operations: fetch questions, submit answers, and retrieve scores",
)

def _serialize_question_public(q: Dict[str, Any]) -> Dict[str, Any]:
    """Serialize question without exposing correct answer."""
    return {
        "id": q["id"],
        "text": q["text"],
        "options": q["options"],
        "difficulty": q.get("difficulty"),
    }

def _find_question(qid: int) -> Optional[Dict[str, Any]]:
    for q in _QUESTIONS:
        if q["id"] == qid:
            return q
    return None

def _validate_submit_payload(payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    """Validate the submit payload ensuring required fields and types exist.

    Returns:
        tuple: (error_message, user_id_or_none)
    """
    if not isinstance(payload, dict):
        return "Invalid JSON payload.", None

    user_id = payload.get("userId")
    if user_id is not None and not isinstance(user_id, str):
        return "userId must be a string if provided.", None

    answers = payload.get("answers")
    if answers is None or not isinstance(answers, list) or len(answers) == 0:
        return "answers must be a non-empty array.", None

    for idx, ans in enumerate(answers):
        if not isinstance(ans, dict):
            return f"answers[{idx}] must be an object.", None
        if "questionId" not in ans or "optionIndex" not in ans:
            return f"answers[{idx}] must include questionId and optionIndex.", None
        if not isinstance(ans["questionId"], int):
            return f"answers[{idx}].questionId must be an integer.", None
        if not isinstance(ans["optionIndex"], int):
            return f"answers[{idx}].optionIndex must be an integer.", None

        # Validate question existence and option index range
        q = _find_question(ans["questionId"])
        if q is None:
            return f"Question with id {ans['questionId']} not found.", None
        if ans["optionIndex"] < 0 or ans["optionIndex"] >= len(q["options"]):
            return f"answers[{idx}].optionIndex out of range for question {q['id']}.", None

    return None, user_id

@blp.route("/questions")
class QuestionsList(MethodView):
    """List available quiz questions (without exposing answers)."""

    # PUBLIC_INTERFACE
    def get(self):
        """Get all quiz questions.

        Returns:
            list: Array of questions with id, text, options, and difficulty (if any).
        """
        return [_serialize_question_public(q) for q in _QUESTIONS], 200

@blp.route("/submit")
class SubmitAnswers(MethodView):
    """Submit answers and receive per-question correctness and total score."""

    # PUBLIC_INTERFACE
    def post(self):
        """Submit answers to questions.

        Request JSON:
            {
              "userId": "string (optional)",
              "answers": [{ "questionId": int, "optionIndex": int }]
            }

        Returns:
            dict: {
              "results": [{ "questionId": int, "correct": bool }],
              "score": int,
              "total": int
            }
        """
        try:
            payload = request.get_json(silent=True)
        except Exception:
            return {"error": "Invalid JSON payload."}, 400

        error, user_id = _validate_submit_payload(payload or {})
        if error:
            return {"error": error}, 400

        answers = payload["answers"]
        results: List[Dict[str, Any]] = []
        score = 0
        total = len(answers)

        for ans in answers:
            q = _find_question(ans["questionId"])
            # _validate_submit_payload ensures q exists
            is_correct = ans["optionIndex"] == q["answer_index"]
            if is_correct:
                score += 1
            results.append({"questionId": q["id"], "correct": is_correct})

        # Persist score per user if provided
        if user_id:
            _USER_SCORES[user_id] = {"score": score, "total": total}

        return {"results": results, "score": score, "total": total}, 200

@blp.route("/score")
class GetScore(MethodView):
    """Get last computed score for a user."""

    # PUBLIC_INTERFACE
    def get(self):
        """Get score for a given userId via query param.

        Query:
            userId: string (required)

        Returns:
            dict: If found: {"userId": str, "score": int, "total": int}
                  If not found: {"message": "No score recorded for user.", "userId": str, "score": 0}
        """
        user_id = request.args.get("userId", type=str)
        if not user_id:
            return {"error": "Missing required query parameter: userId"}, 400

        record = _USER_SCORES.get(user_id)
        if record is None:
            return {"message": "No score recorded for user.", "userId": user_id, "score": 0}, 200
        return {"userId": user_id, "score": record["score"], "total": record["total"]}, 200
