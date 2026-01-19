import pytesseract
from app.utils.pdf_utils import load_pdf_images, load_image

def ocr_agent(state):
    file_bytes = state["file_bytes"]
    file_type = state["file_type"]

    images = []
    text = ""

    if file_type == "pdf":
        images = load_pdf_images(file_bytes)
        # Optional: Skip local Tesseract for 10+ pages to save time
        # We only do it for small files as a fallback
        if len(images) < 3:
            for img in images:
                text += pytesseract.image_to_string(img)
    else:
        img = load_image(file_bytes)
        images = [img]
        text = pytesseract.image_to_string(img)

    return {
        "images": images,
        "raw_text": text
    }
