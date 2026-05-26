import urllib.request
import zlib

uml_code = """
@startuml
skinparam backgroundColor #1e2230
skinparam Handwritten false
skinparam roundcorner 10
skinparam DefaultFontName sans-serif
skinparam DefaultFontColor white
skinparam ArrowColor #3b82f6
skinparam RectangleBorderColor #10b981

title TRtek Akıllı Servis Masası - Multimodal RAG Akış Şeması (Pipeline)

start

:Kullanıcı Ekran Görüntüsü Yükler\nve Sorusunu Yazar (React UI);
--> "React Frontend (Port: 5173)";

:FormData Yapısında .NET API'ye Gönderilir;
--> "ASP.NET Core Web API (Port: 5121)";

:Görsel ve Soru Python Yapay Zeka Servisine İletilir;
--> "Python AI Service (Port: 8000)";

partition "Görüntü İşleme & OCR Katmanı (Vision Layer)" {
  :OpenCV: Görsel Okunur, Gri Tonlama\nve Gaussian Blur ile Gürültü Azaltılır;
  :OpenCV: Canny Edge ile Hata Penceresi\n(Dikdörtgen Kontur) Tespiti Yapılır;
  :OpenCV: Tespit Edilen Alana Yeşil Kutu Çizilir;
  :EasyOCR: Sadece Aktif Hata Alanındaki\nTeknik Metinler Okunur;
  :Regex Filtreleme: Okunan Metinden Hata Kodu\n(0x... veya ORA-...) Ayıklanır;
}

--> "Ayrıştırılan Teknik Veriler .NET API'ye Döner";

partition "Multimodal Fusion & Bilgi Bankası Eşleşmesi (RAG)" {
  :Ayrıştırılan Hata Kodu ile Kullanıcı Sorusu\nHarmonize Edilir (Fusion);
  :PostgreSQL: Ayıklanan Kod 'KnowledgeBases'\nTablosundaki Uzman Çözümleriyle Eşleştirilir;
  :EF Core: Destek Talebi (Ticket) ve OCR Sonuçları\n'ImageLogs' Tablolarına İlişkisel Olarak Kaydedilir;
}

--> ".NET API Son Sonucu JSON Olarak Frontende Basar";

:Arayüzde Uzman Çözümü Listelenir\nve Analiz Raporu Paneli Güncellenir;

stop
@enduml
"""

def deflate(text):
    zlib_obj = zlib.compressobj(9, zlib.DEFLATED, -zlib.MAX_WBITS, zlib.DEF_MEM_LEVEL, zlib.Z_DEFAULT_STRATEGY)
    text_compressed = zlib_obj.compress(text.encode('utf-8'))
    text_compressed += zlib_obj.flush()
    return text_compressed

def encode_plantuml(text):
    compressed = deflate(text)
    puml_alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"
    res = ""
    for i in range(0, len(compressed), 3):
        b1 = compressed[i]
        b2 = compressed[i+1] if i+1 < len(compressed) else 0
        b3 = compressed[i+2] if i+2 < len(compressed) else 0
        res += puml_alphabet[b1 >> 2]
        res += puml_alphabet[((b1 & 0x3) << 4) | (b2 >> 4)]
        if i+1 < len(compressed): res += puml_alphabet[((b2 & 0xF) << 2) | (b3 >> 6)]
        if i+2 < len(compressed): res += puml_alphabet[b3 & 0x3F]
    return res

url = f"http://www.plantuml.com/plantuml/png/{encode_plantuml(uml_code)}"
print("RAG Akış Diyagramı oluşturuluyor...")

try:
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    with urllib.request.urlopen(req) as response, open("rag_akis_semasi.png", "wb") as out_file:
        out_file.write(response.read())
    print("Müjde Zeynep! RAG Akış Şeman da masaüstüne 'rag_akis_semasi.png' olarak başarıyla indi!")
except Exception as e:
    print("Hata:", e)
