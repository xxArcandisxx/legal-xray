import json
import os
import urllib.error
import urllib.parse
import urllib.request


SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_SECRET_KEY")
    or ""
)
SUPABASE_BUCKET = os.getenv("SUPABASE_STORAGE_BUCKET", "legal-documents")


def enabled():
    return bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)


def _request(path, method="GET", body=None, token=None, content_type="application/json"):
    headers = {"apikey": SUPABASE_SERVICE_KEY}
    if path.startswith("/rest/v1/") and method == "POST":
        headers["Prefer"] = "return=representation"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    else:
        headers["Authorization"] = f"Bearer {SUPABASE_SERVICE_KEY}"
    if body is not None:
        headers["Content-Type"] = content_type
    data = body
    if content_type == "application/json" and isinstance(body, dict):
        data = json.dumps(body).encode()
    request = urllib.request.Request(
        f"{SUPABASE_URL}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            raw = response.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase request failed ({error.code}): {detail}") from error


def user_from_token(token):
    if not enabled() or not token:
        return None
    try:
        return _request("/auth/v1/user", token=token)
    except RuntimeError:
        return None


def save_analysis(user_id, result, filename, file_bytes):
    analysis = _request(
        "/rest/v1/analyses",
        method="POST",
        body={
            "user_id": user_id,
            "doc_type": result["doc_type"],
            "overall_risk": result["overall_risk"],
            "summary": result["summary"],
            "clauses": result["clauses"],
            "file_name": filename or None,
        },
    )
    analysis_id = analysis[0]["id"] if analysis else None
    if file_bytes and analysis_id:
        safe_name = urllib.parse.quote(filename or "document", safe="")
        path = f"{user_id}/{analysis_id}/{safe_name}"
        _request(
            f"/storage/v1/object/{SUPABASE_BUCKET}/{path}",
            method="POST",
            body=file_bytes,
            content_type="application/octet-stream",
        )
        _request(
            f"/rest/v1/analyses?id=eq.{urllib.parse.quote(analysis_id)}",
            method="PATCH",
            body={"file_path": path},
        )
    return analysis_id


def list_analyses(user_id):
    return _request(
        f"/rest/v1/analyses?user_id=eq.{urllib.parse.quote(user_id)}"
        "&select=id,doc_type,overall_risk,file_name,file_path,created_at"
        "&order=created_at.desc&limit=50",
    )


def get_analysis(analysis_id, user_id):
    rows = _request(
        f"/rest/v1/analyses?id=eq.{urllib.parse.quote(analysis_id)}"
        f"&user_id=eq.{urllib.parse.quote(user_id)}&select=*"
    )
    return rows[0] if rows else None


def delete_analysis(analysis_id, user_id):
    row = get_analysis(analysis_id, user_id)
    if not row:
        return False
    if row.get("file_path"):
        _request(
            f"/storage/v1/object/{SUPABASE_BUCKET}",
            method="DELETE",
            body={"prefixes": [row["file_path"]]},
        )
    _request(
        f"/rest/v1/analyses?id=eq.{urllib.parse.quote(analysis_id)}"
        f"&user_id=eq.{urllib.parse.quote(user_id)}",
        method="DELETE",
    )
    return True


def signed_file_url(analysis_id, user_id):
    row = get_analysis(analysis_id, user_id)
    if not row or not row.get("file_path"):
        return None
    result = _request(
        f"/storage/v1/object/sign/{SUPABASE_BUCKET}",
        method="POST",
        body={"paths": [row["file_path"]], "expiresIn": 300},
    )
    if not result:
        return None
    signed_path = result[0].get("signedURL") or result[0].get("signedUrl")
    return f"{SUPABASE_URL}/storage/v1{signed_path}" if signed_path else None
