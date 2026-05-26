import os
import re
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import easyocr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Proje Formu Gereksinimi: EasyOCR Motoru Başlatılıyor
reader = easyocr.Reader(['en', 'tr'], gpu=False)

UPLOAD_DIR = "../DotNetBackend/ServisMasasi.Api/Uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_image_with_opencv(image_path, output_path):
    """
    PROJE GEREKSİNİMİ 1: OpenCV ile Hata Penceresi (Dikdörtgen Alan) Tespiti
    Ve Görsel Ön İşleme (Gri tonlama, Gürültü azaltma, Kontrast artırma)
    """
    # 1. Görseli oku
    img = cv2.imread(image_path)
    if img is None:
        return "Görsel okunamadı", "UNKNOWN"
        
    org_height, org_width = img.shape[:2]
    
    # 2. Görsel Ön İşleme Standartları (Gri Tonlama ve Gürültü Azaltma)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 3. Kenar Belirleme (Canny Edge Detection)
    edged = cv2.Canny(blurred, 30, 150)
    
    # 4. Dikdörtgen Alanların Kontur Analizi
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detected_box = None
    max_area = 0
    
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        
        # Eğer kontur 4 köşeliyse (Dikdörtgen/Kare hata penceresi ise)
        if len(approx) == 4:
            area = cv2.contourArea(c)
            # Ekranın çok küçük bir parçası veya tamamı olmasın, mantıklı bir hata penceresi boyutu
            if area > (org_width * org_height * 0.02) and area < (org_width * org_height * 0.95):
                if area > max_area:
                    max_area = area
                    detected_box = approx

    # 5. Odak Noktası Belirleme ve Kutulama
    # Eğer özel bir hata penceresi bulunamazsa tüm ekranı hedef al, bulunursa etrafına yeşil kutu çiz
    ocr_zone = gray
    if detected_box is not None:
        x, y, w, h = cv2.boundingRect(detected_box)
        ocr_zone = gray[y:y+h, x:x+w] # Sadece aktif hata penceresine odaklan
        cv2.drawContours(img, [detected_box], -1, (0, 255, 0), 3) # Yeşil kutu çiz
    else:
        # Hata penceresi ayrıştırılamadıysa görselin ortasına sembolik bir analiz odağı çiz
        cv2.rectangle(img, (int(org_width*0.1), int(org_height*0.1)), (int(org_width*0.9), int(org_height*0.9)), (0, 255, 0), 2)

    # İşlenmiş görseli kaydet (React'te yeşil kutulu hali görünecek)
    cv2.imwrite(output_path, img)

    # 6. OCR ile Teknik Metin Çıkarılması
    results = reader.readtext(ocr_zone)
    raw_text = " ".join([res[1] for res in results])
    
    # 7. REGEX ile Hata Kodlarının Ayıklanması (0x... veya ORA-...)
    detected_code = "UNKNOWN"
    oracle_match = re.search(r'(ORA-\d{5})', raw_text, re.IGNORECASE)
    windows_match = re.search(r'(0x[0-9A-Fa-f]{8})', raw_text)
    
    if oracle_match:
        detected_code = oracle_match.group(1).toUpperCase()
    elif windows_match:
        detected_code = windows_match.group(1)
        
    return raw_text, detected_code

@app.post("/process-screenshot")
async def process_screenshot(
    file: UploadFile = File(...),
    user_prompt: str = Form("")
):
    # Dosya yollarını ayarla
    orig_filename = f"orig_{file.filename}"
    proc_filename = f"proc_{file.filename}"
    
    orig_path = os.path.join(UPLOAD_DIR, orig_filename)
    proc_path = os.path.join(UPLOAD_DIR, proc_filename)
    
    # Orijinal dosyayı kaydet
    with open(orig_path, "wb") as buffer:
        buffer.write(await file.read())
        
    # OpenCV ve OCR boru hattını (Pipeline) çalıştır
    raw_ocr_text, detected_code = process_image_with_opencv(orig_path, proc_path)
    
    return JSONResponse({
        "raw_ocr_text": raw_ocr_text,
        "detected_code": detected_code,
        "ai_image_url": f"http://localhost:5121/images/{proc_filename}"
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
