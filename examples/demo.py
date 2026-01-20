"""
RAgent Demo - Tam İş Akışı Gösterimi
Örnek kullanım: python examples/demo.py
"""

import os
import sys
from pathlib import Path

# Proje root'u ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.document_loader import DocumentLoader, TextSplitter
from src.embedding.embedder import EmbeddingManager
from src.embedding.vector_db import VectorDatabase
from src.rag.rag_system import RAGSystem

def create_sample_document():
    """Örnek doküman oluştur"""
    sample_text = """
    Python Programlama Dili
    
    Python, 1991 yılında Guido van Rossum tarafından oluşturulan yüksek seviyeli bir programlama dilidir.
    Python, basit ve okunması kolay söz dizimi ile bilinir. 
    
    Python'un Özellikleri:
    1. Basit ve Okunabilir: Python kodu diğer programlama dillerine kıyasla çok daha okunabilir.
    2. Geniş Kütüphane: Python binlerce kütüphaneye sahiptir.
    3. Dinamik Yazı Tiplemesi: Python değişkenlerin veri türlerini otomatik olarak belirler.
    4. Taşınabilirlik: Python Windows, Mac, Linux gibi birçok işletim sisteminde çalışır.
    
    Python Kullanım Alanları:
    - Web Geliştirme (Django, Flask)
    - Veri Analizi ve Makine Öğrenmesi (Pandas, NumPy, Scikit-learn)
    - Yapay Zeka (TensorFlow, PyTorch)
    - Otomasyon (Selenium, PyAutoGUI)
    - Bilimsel Hesaplama
    
    Python Kurulumu:
    Python'u https://www.python.org adresinden indirebilirsin.
    Kurulum sonrası terminal veya komut satırında 'python --version' yazarak versiyonunu kontrol edebilirsin.
    """
    
    # Örnek dosya oluştur
    sample_file = Path(__file__).parent.parent / "data" / "sample.txt"
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_text)
    
    print(f"✅ Örnek doküman oluşturuldu: {sample_file}")
    return str(sample_file)


def main():
    print("=" * 60)
    print("🤖 RAgent Demo - Tam İş Akışı")
    print("=" * 60)
    
    # 1. Örnek doküman oluştur
    print("\n📄 Adım 1: Örnek Doküman Oluşturuluyor...")
    sample_file = create_sample_document()
    
    # 2. Dokümanı yükle
    print("\n📂 Adım 2: Doküman Yükleniyor...")
    loader = DocumentLoader()
    text = loader.load_document(sample_file)
    if text:
        print(f"✅ Doküman yüklendi ({len(text)} karakter)")
    else:
        print("❌ Doküman yükleme başarısız")
        return
    
    # 3. Metni parçalara böl
    print("\n✂️ Adım 3: Metin Parçalanıyor...")
    splitter = TextSplitter(chunk_size=500, overlap=100)
    chunks = splitter.split_text(text)
    print(f"✅ {len(chunks)} parça oluşturuldu")
    
    # 4. Embedding oluştur
    print("\n🔢 Adım 4: Embedding'ler Oluşturuluyor...")
    embedder = EmbeddingManager()
    print("✅ Embedding modeli yüklendi")
    
    # 5. Vector Database'e ekle
    print("\n💾 Adım 5: Vektör Veritabanına Ekleniyor...")
    db = VectorDatabase(
        db_path="./data/chroma_db",
        collection_name="sample_documents"
    )
    
    # Meta veriler
    metadatas = [
        {"source": "sample.txt", "chunk": i}
        for i in range(len(chunks))
    ]
    
    db.add_documents(chunks, metadatas=metadatas)
    print(f"✅ {len(chunks)} parça veritabanına eklendi")
    
    # 6. RAG Sistemi ile sorgu
    print("\n❓ Adım 6: Sorgu ve Cevaplama...")
    rag = RAGSystem()
    
    test_questions = [
        "Python nedir?",
        "Python'un özellikleri nelerdir?",
        "Python hangi alanlarda kullanılır?"
    ]
    
    for question in test_questions:
        print(f"\n🔍 Soru: {question}")
        
        # Vektör DB'den ara
        search_results = db.search(question, n_results=2)
        print(f"   Benzer dokümanlar bulundu: {len(search_results)}")
        
        if search_results:
            # Birinci 2 sonucu göster
            for i, result in enumerate(search_results[:2], 1):
                distance = result.get('distance', 'N/A')
                text_preview = result['text'][:100] + "..."
                print(f"   [{i}] (Benzerlik: {distance:.3f}) {text_preview}")
    
    print("\n" + "=" * 60)
    print("✅ Demo Tamamlandı!")
    print("=" * 60)
    print("\n💡 Sonraki Adımlar:")
    print("1. Groq API anahtarını .env dosyasına ekle")
    print("2. Streamlit uygulamasını başlat: streamlit run src/ui/app.py")
    print("3. PDF'ler ve web içeriği yüklemeyi öğren")
    print("\n")


if __name__ == "__main__":
    main()
