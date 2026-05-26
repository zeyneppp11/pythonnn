import urllib.request
import zlib

uml_code = """
@startuml
skinparam backgroundColor #1e2230
skinparam Handwritten false
skinparam roundcorner 10
skinparam DefaultFontName sans-serif
skinparam DefaultFontColor white
skinparam EntityBorderColor #3b82f6

title TRtek Akıllı Servis Masası - Veritabanı ER Diyagramı

entity "Users (Kullanıcılar)" as Users #3b82f6 {
  * Id : Guid [PK]
  --
  Name : String
  Email : String
}

entity "Tickets (Destek Talepleri)" as Tickets #2d3248 {
  * Id : Guid [PK]
  --
  * UserId : Guid [FK]
  UserPrompt : Text
  FinalResponse : Text
  Status : Varchar
  CreatedAt : DateTime
}

entity "ImageLogs (Görsel ve OCR Analizleri)" as ImageLogs #2d3248 {
  * Id : Guid [PK]
  --
  * TicketId : Guid [FK] (Unique)
  OriginalImagePath : Varchar
  ProcessedImagePath : Varchar
  RawOcrText : Text
  DetectedErrorCode : Varchar
  ConfidenceScore : Integer
}

entity "KnowledgeBases (Uzman Bilgi Bankası)" as KnowledgeBases #10b981 {
  * Id : Guid [PK]
  --
  ErrorCode : Varchar (Unique)
  Category : Varchar
  SolutionText : Text
}

Users ||--o{ Tickets : "1 -> N (Açar)"
Tickets ||--|| ImageLogs : "1 -> 1 (İçerir)"

note right of KnowledgeBases
  Mantıksal RAG Eşleşmesi:
  ImageLogs.DetectedErrorCode = KnowledgeBases.ErrorCode
end note

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
print("Diyagram oluşturuluyor...")

try:
    # 403 Hatasını engellemek için tarayıcı (Chrome) gibi davranıyoruz
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    with urllib.request.urlopen(req) as response, open("er_diyagrami.png", "wb") as out_file:
        out_file.write(response.read())
    print("Harika! Veritabanı ER Diyagramı masaüstüne 'er_diyagrami.png' olarak başarıyla indi!")
except Exception as e:
    print("Hata:", e)
