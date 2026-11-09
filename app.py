import os
import json
import time

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from config import (
    ALLOWED_EXTENSIONS, CLIENT_ID_RE, CORS_ORIGINS, MAX_CONTENT_LENGTH,
    MAX_TEXT_LENGTH, RATE_LIMIT, RATE_WINDOW_SECONDS,
)
from samples import SAMPLE_RESULT, SAMPLE_TEXT
from services.ai_service import analyze
from services.document_service import extract_text
from services.storage import close_db, get_analysis, list_analyses, save_analysis

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
CORS(app, origins=CORS_ORIGINS)
REQUESTS = {}


def current_client_id():
    value = request.headers.get("X-Client-ID", "")
    return value if CLIENT_ID_RE.fullmatch(value) else None


def rate_limited(owner):
    now = time.time()
    recent = [stamp for stamp in REQUESTS.get(owner, []) if now - stamp < RATE_WINDOW_SECONDS]
    REQUESTS[owner] = recent
    if len(recent) >= RATE_LIMIT:
        return True
    recent.append(now)
    return False


app.teardown_appcontext(close_db)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok", service="legal-xray")


@app.route("/sample")
def sample():
    analysis_id, created_at = save_analysis(SAMPLE_RESULT, current_client_id() or "sample")
    return jsonify(text=SAMPLE_TEXT, result=SAMPLE_RESULT, analysis_id=analysis_id, created_at=created_at)


@app.route("/history")
def history():
    owner = current_client_id()
    if not owner:
        return jsonify(error="A valid X-Client-ID header is required."), 400
    return jsonify(items=[dict(row) for row in list_analyses(owner)])


@app.route("/history/<analysis_id>")
def history_detail(analysis_id):
    owner = current_client_id()
    if not owner:
        return jsonify(error="A valid X-Client-ID header is required."), 400
    row = get_analysis(analysis_id, owner)
    if row is None:
        return jsonify(error="Analysis not found."), 404
    return jsonify(
        analysis_id=row["id"], created_at=row["created_at"],
        result={"doc_type": row["doc_type"], "overall_risk": row["overall_risk"],
                "summary": json.loads(row["summary"]),
                "clauses": json.loads(row["clauses"])},
    )


@app.route("/analyze", methods=["POST"])
def run():
    if not os.getenv("OPENAI_API_KEY"):
        return jsonify(error="No API key set. Add OPENAI_API_KEY to .env, or try the sample."), 500
    owner = current_client_id()
    if not owner:
        return jsonify(error="A valid X-Client-ID header is required."), 400
    if rate_limited(owner):
        return jsonify(error="Hourly analysis limit reached. Please try again later."), 429
    try:
        uploaded = request.files.get("file")
        if uploaded and uploaded.filename:
            extension = os.path.splitext(uploaded.filename.lower())[1]
            if extension not in ALLOWED_EXTENSIONS:
                return jsonify(error="Unsupported file type."), 400
        text = extract_text(uploaded) if uploaded and uploaded.filename else request.form.get("text", "")
        text = text.strip()[:MAX_TEXT_LENGTH]
        if len(text) < 100:
            return jsonify(error="Could not find enough text. Upload a clear PDF, DOCX, TXT or photo, or paste the text."), 400
        result = analyze(text)
        analysis_id, created_at = save_analysis(result, owner)
        return jsonify(text=text, result=result, analysis_id=analysis_id, created_at=created_at)
    except (RuntimeError, ValueError) as error:
        return jsonify(error=str(error)), 502
    except Exception:
        app.logger.exception("Document analysis failed")
        return jsonify(error="We could not analyze this document. Please try again."), 500


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "").lower() == "true")
