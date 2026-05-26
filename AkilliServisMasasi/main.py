from fastapi import FastAPI, File, UploadFile
import easyocr
import cv2
import numpy as np
import os
import re

app = FastAPI(title="Akıllı Servis Masası AI Motoru")

# Mac M1 üzerinde CPU modunda EasyOCR modelini yüklüyoruz
reader = easyocr.Reader(['tr', 'en'], gpu=False)

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    results = reader.readtext(image)
    
    raw_text = ""
    for (bbox, text, prob) in results:
        raw_text += text + " "
    
    detected_error_code = "UNKNOWN"
    
    # Regex Taramaları
    oracle_match = re.search(r"ORA-\d+", raw_text, re.IGNORECASE)
    windows_match = re.search(r"0x[0-9A-Fa-f]{8}", raw_text, re.IGNORECASE)
    
    if oracle_match:
        detected_error_code = oracle_match.group(0).upper()
    elif windows_match:
        detected_error_code = "0x" + windows_match.group(0)[2:].upper()
    
    # Görsel üzerine kutu çizme
    for (bbox, text, prob) in results:
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    
    outputs_folder = "Outputs"
    if not os.path.exists(outputs_folder):
        os.makedirs(outputs_folder)
        
    processed_image_path = os.path.join(outputs_folder, f"processed_{file.filename}")
    cv2.imwrite(processed_image_path, image)
    
    return {
        "raw_text": raw_text.strip(),
        "detected_error_code": detected_error_code,
        "processed_image_path": processed_image_path
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
