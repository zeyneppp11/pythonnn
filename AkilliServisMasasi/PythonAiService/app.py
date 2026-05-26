import cv2
import easyocr
import re
import os
import shutil
from fastapi import FastAPI, UploadFile, File

app = FastAPI(title="Akilli Servis Masasi - Vision Layer")

# EasyOCR modeli İngilizce ve Türkçe olarak yükleniyor
reader = easyocr.Reader(['en', 'tr'], gpu=False)

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 1. GÖRSEL ÖN İŞLEME (OpenCV)
    image = cv2.imread(temp_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    processed_img = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    processed_filename = f"processed_{file.filename}"
    cv2.imwrite(processed_filename, processed_img)
    
    # 2. OCR (EasyOCR)
    ocr_results = reader.readtext(gray, detail=0)
    full_text = " ".join(ocr_results)
    
    # 3. REGEX İLE HATA KODU AYIKLAMA
    oracle_pattern = r"ORA-\d+"
    windows_hex_pattern = r"0x[0-9a-fA-F]+"
    
    oracle_errors = re.findall(oracle_pattern, full_text)
    windows_errors = re.findall(windows_hex_pattern, full_text)
    
    detected_code = "UNKNOWN"
    if oracle_errors:
        detected_code = oracle_errors[0]
    elif windows_errors:
        detected_code = windows_errors[0]
        
    if os.path.exists(temp_path):
        os.remove(temp_path)
        
    return {
        "raw_text": full_text,
        "detected_error_code": detected_code,
        "processed_image_path": os.path.abspath(processed_filename)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
