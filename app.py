import os
import json
import time

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from config import (
    ALLOWED_EXTENSIONS, CLIENT_ID_RE, CORS_ORIGINS, MAX_CONTENT_LENGTH,
    MAX_TEXT_LENGTH, RATE_LIMIT, RATE_WINDOW_SECONDS,
    SUPABASE_ANON_KEY, SUPABASE_URL,
)
from samples import SAMPLE_RESULT, SAMPLE_TEXT
from services.ai_service import analyze
from services.document_service import extract_text
from services.storage import close_db, get_analysis, list_analyses, save_analysis
from services import supabase_service

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
CORS(app, origins=CORS_ORIGINS)
REQUESTS = {}


def current_client_id():
    value = request.headers.get("X-Client-ID", "")
    return value if CLIENT_ID_RE.fullmatch(value) else None


def current_user():
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return None
    return supabase_service.user_from_token(authorization[7:].strip())


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


@app.route("/auth-config")
def auth_config():
    return jsonify(url=SUPABASE_URL, anon_key=SUPABASE_ANON_KEY)


@app.route("/sample")
def sample():
    user = current_user()
    if user:
        analysis_id = supabase_service.save_analysis(user["id"], SAMPLE_RESULT, None, None)
        created_at = None
    else:
        analysis_id, created_at = save_analysis(SAMPLE_RESULT, current_client_id() or "sample")
    return jsonify(text=SAMPLE_TEXT, result=SAMPLE_RESULT, analysis_id=analysis_id, created_at=created_at)


@app.route("/history")
def history():
    user = current_user()
    if user:
        return jsonify(items=supabase_service.list_analyses(user["id"]))
    owner = current_client_id()
    if not owner:
        return jsonify(error="A valid X-Client-ID header is required."), 400
    return jsonify(items=[dict(row) for row in list_analyses(owner)])


@app.route("/history/<analysis_id>")
def history_detail(analysis_id):
    user = current_user()
    if user:
        row = supabase_service.get_analysis(analysis_id, user["id"])
        if row is None:
            return jsonify(error="Analysis not found."), 404
        return jsonify(
            analysis_id=row["id"], created_at=row["created_at"],
            result={"doc_type": row["doc_type"], "overall_risk": row["overall_risk"],
                    "summary": row["summary"], "clauses": row["clauses"]},
        )
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
    user = current_user()
    owner = current_client_id()
    if not user and not owner:
        return jsonify(error="A valid X-Client-ID header is required."), 400
    rate_owner = user["id"] if user else owner
    if rate_limited(rate_owner):
        return jsonify(error="Hourly analysis limit reached. Please try again later."), 429
    try:
        uploaded = request.files.get("file")
        file_bytes = uploaded.read() if uploaded and uploaded.filename else None
        if uploaded and uploaded.filename:
            uploaded.stream.seek(0)
        if uploaded and uploaded.filename:
            extension = os.path.splitext(uploaded.filename.lower())[1]
            if extension not in ALLOWED_EXTENSIONS:
                return jsonify(error="Unsupported file type."), 400
        text = extract_text(uploaded) if uploaded and uploaded.filename else request.form.get("text", "")
        text = text.strip()[:MAX_TEXT_LENGTH]
        if len(text) < 100:
            return jsonify(error="Could not find enough text. Upload a clear PDF, DOCX, TXT or photo, or paste the text."), 400
        result = analyze(text)
        if user:
            analysis_id = supabase_service.save_analysis(
                user["id"], result, uploaded.filename if uploaded else None, file_bytes
            )
            created_at = None
        else:
            analysis_id, created_at = save_analysis(result, owner)
        return jsonify(text=text, result=result, analysis_id=analysis_id, created_at=created_at)
    except (RuntimeError, ValueError) as error:
        return jsonify(error=str(error)), 502
    except Exception:
        app.logger.exception("Document analysis failed")
        return jsonify(error="We could not analyze this document. Please try again."), 500


@app.route("/history/<analysis_id>", methods=["DELETE"])
def delete_history(analysis_id):
    user = current_user()
    if not user:
        return jsonify(error="Sign in to delete a saved analysis."), 401
    if not supabase_service.delete_analysis(analysis_id, user["id"]):
        return jsonify(error="Analysis not found."), 404
    return jsonify(ok=True)


@app.route("/history/<analysis_id>/file")
def history_file(analysis_id):
    user = current_user()
    if not user:
        return jsonify(error="Sign in to access saved files."), 401
    url = supabase_service.signed_file_url(analysis_id, user["id"])
    if not url:
        return jsonify(error="No original file is saved for this analysis."), 404
    return jsonify(url=url)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "").lower() == "true")
