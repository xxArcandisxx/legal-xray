import io
import os
import base64

from config import IMG_TYPES, OPENAI_BASE_URL, VISION_MODEL


def _ocr(data, media_type):
    from openai import OpenAI

    images = []
    if media_type == "application/pdf":
        import fitz
        document = fitz.open(stream=data, filetype="pdf")
        for page_number in range(min(8, len(document))):
            page = document[page_number]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
            images.append(("image/png", pixmap.tobytes("png")))
    else:
        images.append((media_type, data))
    content = [{"type": "text", "text":
                "Transcribe all the text in these document pages exactly as written, in reading order. Return only the text."}]
    content.extend({
        "type": "image_url",
        "image_url": {"url": f"data:{image_type};base64,{base64.b64encode(image).decode()}"},
    } for image_type, image in images)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url=OPENAI_BASE_URL)
    response = client.chat.completions.create(
        model=VISION_MODEL, max_tokens=8000, messages=[{"role": "user", "content": content}]
    )
    return response.choices[0].message.content or ""


def extract_text(file):
    extension = os.path.splitext(file.filename.lower())[1]
    data = file.read()
    if extension == ".pdf":
        import pdfplumber
        try:
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages[:15])
        except (OSError, ValueError):
            text = ""
        if len(text.strip()) < 100:
            import fitz
            document = fitz.open(stream=data, filetype="pdf")
            text = "\n".join(page.get_text() for page in document[:15])
        return text if len(text.strip()) >= 100 else _ocr(data, "application/pdf")
    if extension in IMG_TYPES:
        return _ocr(data, IMG_TYPES[extension])
    if extension == ".docx":
        import docx
        return "\n".join(paragraph.text for paragraph in docx.Document(io.BytesIO(data)).paragraphs)
    return data.decode("utf-8", errors="ignore")
