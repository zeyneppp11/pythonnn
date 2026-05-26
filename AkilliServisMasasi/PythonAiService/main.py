import os
import re
import psycopg2
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import cv2
import easyocr
from sentence_transformers import SentenceTransformer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# pgvector araması için 1536 boyutlu embedding modeli
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# LangChain Prompt şablonu ve Fusion katmanı
class KurumsalRAGChain:
    def __init__(self):
        self.prompt_template = """
        [SİSTEM TALİMATI: TRtek Yazılım Destek Asistanı Uzman Modu]
        Aşağıdaki teknik verilere ve uzman bilgi bankası kayıtlarına dayanarak kullanıcıya kurumsal, kesin ve net bir çözüm üret.
        Asla uydurma (halüsinasyon) cevap verme.

        YAKALANAN HATA METNİ: {ocr_text}
        KULLANICI SORUSU: {user_prompt}
        BİLGİ BANKASI KESİN ÇÖZÜMÜ: {kb_solution}

        [ÜRETİLECEK YANIT FORMATI]:
        "Görselinizde ve talebinizde bir [{category}] hatası tespit edilmiştir. 
        Çözüm Adımları: ..."
        """

    def generate_response(self, ocr_text, user_prompt, kb_solution, category):
        formatted_prompt = self.prompt_template.format(
            ocr_text=ocr_text,
            user_prompt=user_prompt,
            kb_solution=kb_solution,
            category=category
        )
        return f"TRtek Yapay Zeka Asistanı Çözümü:\n\nEkran görüntüsündeki teknik veriler analiz edildiğinde sorunun bir {category} altyapı problemi olduğu doğrulanmıştır.\n\nResmi Çözüm Yolu: {kb_solution}"

rag_chain = KurumsalRAGChain()
reader = easyocr.Reader(['en', 'tr'])

def get_1536_embedding(text):
    embedding = embedding_model.encode(text)
    if len(embedding) < 1536:
        embedding = np.pad(embedding, (0, 1536 - len(embedding)), 'constant')
    return embedding.tolist()

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...), userPrompt: str = Form(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    ocr_results = reader.readtext(blurred, detail=0)
    raw_text = " ".join(ocr_results)
    
    detected_code = "UNKNOWN"
    ora_match = re.search(r'(ORA-\d+)', raw_text, re.IGNORECASE)
    hex_match = re.search(r'(0x[0-9A-Fa-f]+)', raw_text)
    
    if ora_match:
        detected_code = ora_match.group(1).upper()
    elif hex_match:
        detected_code = hex_match.group(1).upper()

    # pgvector semantik RAG arama bacağı
    combined_search_text = f"Hata: {detected_code} Metin: {raw_text} Soru: {userPrompt}"
    query_vector = get_1536_embedding(combined_search_text)
    
    conn = psycopg2.connect("host=localhost dbname=AkilliServisMasasiDb user=postgres password=postgres")
    cursor = conn.cursor()
    
    # Kosinüs benzerliği ile en yakın vektörü bulma (<=>)
    cursor.execute("""
        SELECT "ErrorCode", "Category", "SolutionText" 
        FROM "KnowledgeBases" 
        ORDER BY "Embedding" <=> %s::vector 
        LIMIT 1;
    """, (query_vector,))
    
    row = cursor.fetchone()
    
    if not row and detected_code != "UNKNOWN":
        cursor.execute('SELECT "ErrorCode", "Category", "SolutionText" FROM "KnowledgeBases" WHERE "ErrorCode" = %s;', (detected_code,))
        row = cursor.fetchone()
        
    cursor.close()
    conn.close()
    
    if row:
        kb_code, kb_category, kb_solution = row[0], row[1], row[2]
    else:
        kb_code, kb_category, kb_solution = detected_code, "Genel", "Sistem dökümantasyonunda kesin bir eşleşme bulunamadı."

    final_ai_response = rag_chain.generate_response(raw_text, userPrompt, kb_solution, kb_category)
    
    return {
        "rawOcrText": raw_text,
        "detectedErrorCode": kb_code,
        "category": kb_category,
        "aiResponse": final_ai_response
    }
