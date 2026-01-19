import fitz  # PyMuPDF
from PIL import Image
import io

def load_pdf_images(pdf_bytes):
    """
    Convert PDF bytes to list of PIL Images using PyMuPDF (no Poppler needed)
    """
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Zoom for better OCR quality
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        images.append(img)
        
    pdf_document.close()
    return images

def load_image(image_bytes):
    """
    Load image bytes into PIL Image
    """
    return Image.open(io.BytesIO(image_bytes))
