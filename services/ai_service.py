import json
import os

from config import MODEL, OPENAI_BASE_URL

PROMPT = """You are a legal-document risk explainer for ordinary people in India.
Read the document and return ONLY valid JSON (no markdown) in this shape:
{"doc_type": str, "overall_risk": 0-100,
 "summary": {"en": str, "hi": str, "kn": str},
 "clauses": [{"quote": str, "risk": "high|medium|low", "category": str,
   "why_risky": {"en": str, "hi": str, "kn": str},
   "negotiate": {"en": str, "hi": str, "kn": str}}]}
Rules:
- "quote" must be copied word for word from the document, one sentence or less.
- Flag only unfair, one-sided, hidden-cost or unusual clauses. Skip normal boilerplate. 3 to 10 clauses.
- Explain in very simple words, no jargon. en = English, hi = Hindi, kn = Kannada.
- "negotiate" = one concrete thing the person can ask for.
- This is information, not legal advice."""


def validate_result(result):
    if not isinstance(result, dict):
        raise ValueError("The AI returned an invalid result.")
    if not isinstance(result.get("doc_type"), str) or not isinstance(result.get("summary"), dict):
        raise ValueError("The AI returned an incomplete result.")
    if any(not isinstance(result["summary"].get(language), str) for language in ("en", "hi", "kn")):
        raise ValueError("The AI returned incomplete summary translations.")
    if not isinstance(result.get("overall_risk"), int) or not 0 <= result["overall_risk"] <= 100:
        raise ValueError("The AI returned an invalid risk score.")
    clauses = result.get("clauses")
    if not isinstance(clauses, list) or not 3 <= len(clauses) <= 10:
        raise ValueError("The AI returned an invalid clause list.")
    for clause in clauses:
        if not isinstance(clause, dict) or clause.get("risk") not in {"high", "medium", "low"}:
            raise ValueError("The AI returned an invalid clause.")
        if any(not clause.get(field) for field in ("quote", "category", "why_risky", "negotiate")):
            raise ValueError("The AI returned an incomplete clause.")
        for field in ("why_risky", "negotiate"):
            if any(not isinstance(clause[field].get(language), str) for language in ("en", "hi", "kn")):
                raise ValueError("The AI returned incomplete translations.")


def analyze(text):
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=OPENAI_BASE_URL)
    for _ in range(2):
        response = client.chat.completions.create(
            model=MODEL, max_tokens=8000,
            messages=[{"role": "system", "content": PROMPT}, {"role": "user", "content": text}],
        )
        raw = response.choices[0].message.content or ""
        try:
            result = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
            validate_result(result)
            return result
        except (ValueError, json.JSONDecodeError):
            continue
    raise RuntimeError("The AI reply could not be read. Please try again.")
