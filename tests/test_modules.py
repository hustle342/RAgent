"""
Test dosyası - Modüllerin çalışıp çalışmadığını kontrol et
Kullanım: python tests/test_modules.py
"""

import sys
from pathlib import Path

# Proje root'u ekle
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Tüm modüllerin import edilebilmesini test et"""
    print("🧪 Modül İçeri Aktarma Testleri")
    print("-" * 40)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Document Loader
    try:
        from src.ingestion.document_loader import DocumentLoader, TextSplitter
        print("✅ DocumentLoader")
        tests_passed += 1
    except Exception as e:
        print(f"❌ DocumentLoader: {e}")
        tests_failed += 1
    
    # Test 2: Embedder
    try:
        from src.embedding.embedder import EmbeddingManager
        print("✅ EmbeddingManager")
        tests_passed += 1
    except Exception as e:
        print(f"❌ EmbeddingManager: {e}")
        tests_failed += 1
    
    # Test 3: Vector DB
    try:
        from src.embedding.vector_db import VectorDatabase
        print("✅ VectorDatabase")
        tests_passed += 1
    except Exception as e:
        print(f"❌ VectorDatabase: {e}")
        tests_failed += 1
    
    # Test 4: RAG System
    try:
        from src.rag.rag_system import RAGSystem
        print("✅ RAGSystem")
        tests_passed += 1
    except Exception as e:
        print(f"❌ RAGSystem: {e}")
        tests_failed += 1
    
    # Test 5: Config
    try:
        from config.config import GROQ_API_KEY, CHUNK_SIZE
        print("✅ Config")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Config: {e}")
        tests_failed += 1
    
    print("-" * 40)
    print(f"Başarılı: {tests_passed} | Başarısız: {tests_failed}")
    print()
    
    return tests_failed == 0


def test_document_loader():
    """DocumentLoader'ı test et"""
    print("🧪 DocumentLoader Testi")
    print("-" * 40)
    
    try:
        from src.ingestion.document_loader import DocumentLoader, TextSplitter
        
        # Test metin oluştur
        test_text = "Bu bir test metnidir. " * 50
        
        # TextSplitter test et
        splitter = TextSplitter(chunk_size=100, overlap=20)
        chunks = splitter.split_text(test_text)
        
        print(f"✅ Metin {len(chunks)} parçaya bölündü")
        print(f"   - İlk parça: {chunks[0][:50]}...")
        print(f"   - Son parça: {chunks[-1][:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        return False


def main():
    print("=" * 40)
    print("🚀 RAgent Modül Testleri")
    print("=" * 40)
    print()
    
    result1 = test_imports()
    print()
    result2 = test_document_loader()
    
    print()
    print("=" * 40)
    if result1 and result2:
        print("✅ Tüm testler başarılı!")
    else:
        print("⚠️ Bazı testler başarısız oldu")
    print("=" * 40)


if __name__ == "__main__":
    main()
