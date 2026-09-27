import os
from datetime import date

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()


class StudySession(BaseModel):
    type: str = Field(description="Either study or break")
    subject: str = Field(description="Subject name, or Break for breaks")
    minutes: int = Field(gt=0)
    task: str
    reason: str


class StudyPlan(BaseModel):
    title: str
    summary: str
    total_minutes: int = Field(gt=0)
    sessions: list[StudySession]
    tip: str


def create_app(test_config=None):
    app = Flask(__name__)
    if test_config:
        app.config.update(test_config)

    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500")
    origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]
    CORS(app, resources={r"/*": {"origins": origins}})

    @app.get("/")
    def home():
        return jsonify({
            "name": "AI Study Planner API",
            "status": "running",
            "endpoints": ["GET /health", "POST /generate-plan"],
        })

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.post("/generate-plan")
    def generate_plan():
        data = request.get_json(silent=True)
        validation_error = validate_request(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        try:
            client = OpenAI()
            response = client.responses.parse(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                instructions=(
                    "You are a practical academic planning assistant. Build a realistic plan "
                    "that fits within the exact available time, including breaks. Prioritize "
                    "closer deadlines and lower confidence. Use concrete, achievable tasks. "
                    "Never invent course requirements or claim that success is guaranteed."
                ),
                input=build_prompt(data),
                text_format=StudyPlan,
            )
            plan = response.output_parsed
            if plan is None:
                return jsonify({"error": "The AI could not create a plan. Please revise your input."}), 502

            return jsonify(plan.model_dump())
        except Exception as exc:
            app.logger.exception("OpenAI request failed: %s", type(exc).__name__)
            return jsonify({
                "error": "The plan could not be generated right now. Please try again shortly."
            }), 502

    return app


def validate_request(data):
    if not isinstance(data, dict):
        return "Send the request as JSON."

    subjects = data.get("subjects")
    if not isinstance(subjects, list) or not subjects:
        return "Add at least one subject."
    if len(subjects) > 8:
        return "Use no more than 8 subjects."

    for subject in subjects:
        if not isinstance(subject, dict):
            return "Each subject must contain a name, deadline, and confidence level."
        name = subject.get("name")
        confidence = subject.get("confidence")
        deadline = subject.get("deadline")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 60:
            return "Each subject needs a name of 60 characters or fewer."
        if confidence not in range(1, 6):
            return "Confidence must be a whole number from 1 to 5."
        if deadline:
            try:
                parsed_deadline = date.fromisoformat(deadline)
            except (TypeError, ValueError):
                return "Deadlines must be valid dates."
            if parsed_deadline < date.today():
                return "Deadlines cannot be in the past."

    for key, minimum, maximum in (
        ("available_minutes", 20, 480),
        ("session_minutes", 10, 120),
        ("break_minutes", 1, 30),
    ):
        value = data.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
            return f"{key.replace('_', ' ').title()} must be between {minimum} and {maximum}."

    return None


def build_prompt(data):
    subject_lines = []
    for subject in data["subjects"]:
        deadline = subject.get("deadline") or "No deadline provided"
        subject_lines.append(
            f'- {subject["name"].strip()}: deadline {deadline}; confidence '
            f'{subject["confidence"]}/5 (1 means least confident)'
        )

    return f"""Create a study plan for today ({date.today().isoformat()}).

Subjects:
{chr(10).join(subject_lines)}

The complete plan has {data['available_minutes']} minutes available.
Preferred study block: {data['session_minutes']} minutes.
Preferred break: {data['break_minutes']} minutes.

The sum of every session's minutes must not exceed the available time. Include breaks when useful.
For study sessions, name one specific task. For breaks, use subject "Break" and a short restorative task.
"""


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
