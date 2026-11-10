# Legal X-ray

Legal X-ray helps people understand risky clauses in rental agreements, job offers, loan documents, and legal notices—in simple English, Hindi, or Kannada.

It is a complete hackathon application with:

- PDF, DOCX, TXT, image, and scanned-PDF input
- OpenAI-compatible text and vision models
- Risk scoring and clause-level explanations
- Clickable document highlights
- Negotiation suggestions for every flagged clause
- Anonymous analysis history without storing original files
- SQLite persistence, API validation, rate limiting, health checks, and tests
- Docker, Railway, Vercel, and Gunicorn deployment configuration

## Project structure

```text
app.py                    Flask routes and request orchestration
config.py                 Environment-backed application settings
services/ai_service.py    OpenAI-compatible analysis and validation
services/document_service.py  PDF, DOCX, text, and vision OCR extraction
services/storage.py       SQLite history persistence
templates/index.html      Responsive frontend
api/index.py              Vercel serverless entrypoint
tests/test_app.py         API and storage tests
```

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Add OPENAI_API_KEY to .env
python app.py
```

Open `http://127.0.0.1:5000`.

The sample button works without an API key. Real analysis requires `OPENAI_API_KEY`.

## Configuration

```env
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
DATABASE_PATH=legal_xray.db
CORS_ORIGINS=*
```

`OPENAI_BASE_URL` supports OpenAI-compatible gateways and local providers. For Groq, use `openai/gpt-oss-20b` for analysis and `qwen/qwen3.8-27b` for scanned-document OCR.

### Optional accounts and long-term storage

Set `SUPABASE_URL`, `SUPABASE_ANON_KEY`, and the server-only `SUPABASE_SERVICE_KEY` to enable email/password accounts, password reset emails, hosted analysis history, and original-file storage. Anonymous users can continue using the app with browser-scoped history.

Create a Supabase `analyses` table and `legal-documents` storage bucket before enabling this feature:

```sql
create table public.analyses (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null,
  doc_type text not null,
  overall_risk integer not null,
  summary jsonb not null,
  clauses jsonb not null,
  file_name text,
  file_path text,
  created_at timestamptz not null default now()
);
```

Keep the service-role key server-side only. Configure Supabase Auth email settings and storage policies before using this in production.

## Test

```powershell
pytest -q
```

## Deploy

### Railway

Deploy the repository, set `OPENAI_API_KEY`, and optionally set `OPENAI_MODEL`, `OPENAI_BASE_URL`, and `CORS_ORIGINS`. Railway detects the included `Dockerfile` or `Procfile` and uses `/health` as its health check.

### Vercel

The included `api/index.py` and `vercel.json` expose the Flask application as a Python serverless function. Import the repository into Vercel, keep the root directory at `legal-xray`, and configure `OPENAI_API_KEY` plus the optional model and CORS variables in Project Settings.

Vercel's filesystem is ephemeral, so SQLite history is only best-effort and may disappear when a serverless instance is replaced. The analysis itself still works. For durable history, replace `DATABASE_PATH` with a hosted database such as Vercel Postgres, Neon, or Supabase.

### Docker

```powershell
docker build -t legal-xray .
docker run --env-file .env -p 8080:8080 legal-xray
```

## Privacy and limitations

Original uploaded files are processed in memory and are not written to disk. Anonymous analysis metadata and explanations are stored in SQLite so the browser can show recent history. The extracted document text is returned to the browser for highlighting but is not stored in the database.

Results are educational explanations, not legal advice. OCR can be inaccurate for blurry images or handwriting, and AI output should be checked with a qualified lawyer before making an important decision.
