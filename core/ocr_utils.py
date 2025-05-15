import traceback
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import concurrent.futures

# Custom OCR config
OCR_CONFIG = r'--oem 1 --psm 6'

def extract_text_from_file(file_path):
    try:
        # Convert to absolute path and normalize
        abs_path = os.path.abspath(file_path)
        print(f"🔍 Attempting to process: {abs_path}")
        
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Path doesn't exist: {abs_path}")
            
        # Handle URL-encoded spaces (%20) and +
        cleaned_path = abs_path.replace('+', ' ')
        if cleaned_path != abs_path:
            os.rename(abs_path, cleaned_path)
            abs_path = cleaned_path
            
        if abs_path.lower().endswith('.pdf'):
            return extract_text_from_pdf(abs_path)
        return extract_text_from_image(abs_path)
        
    except Exception as e:
        print(f"❌ Extraction failed: {traceback.format_exc()}")
        return ""

def process_pdf_page(index, page):
    temp_img_path = f"/tmp/page_{index}.jpg"
    page.save(temp_img_path, 'JPEG')
    try:
        text = pytesseract.image_to_string(Image.open(temp_img_path), lang='eng', config=OCR_CONFIG)
    finally:
        os.remove(temp_img_path)
    return text

def extract_text_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path, dpi=200)
    text_chunks = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_pdf_page, i, page) for i, page in enumerate(pages)]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    text_chunks.append(result)
            except Exception as e:
                print(f"Error processing page: {e}")
    return "\n".join(text_chunks)

def extract_text_from_image(image_path):
    return pytesseract.image_to_string(Image.open(image_path), lang='eng', config=OCR_CONFIG)