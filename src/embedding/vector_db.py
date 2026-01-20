"""
Vector Database (ChromaDB) Modülü
"""

import os
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VectorDatabase:
    """ChromaDB ile vektör veritabanı yönetimi"""
    
    def __init__(self, db_path: str = "./data/chroma_db", collection_name: str = "documents"):
        """
        Başlat
        
        Args:
            db_path: Veritabanı dizini
            collection_name: Koleksiyon adı
        """
        try:
            import chromadb
            
            # Dizin oluştur
            os.makedirs(db_path, exist_ok=True)
            
            # ChromaDB client
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            self.db_path = db_path
            self.collection_name = collection_name
            
            logger.info(f"Vector Database başlatıldı: {db_path}")
            
        except Exception as e:
            logger.error(f"Vector Database başlatma hatası: {e}")
            self.client = None
            self.collection = None
    
    def add_documents(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None):
        """
        Dokümanları veritabanına ekle
        
        Args:
            texts: Metin parçaları
            metadatas: Meta veriler
            ids: Doküman ID'leri
        """
        if self.collection is None:
            logger.error("Koleksiyon hazır değil")
            return False
        
        try:
            from src.embedding.embedder import EmbeddingManager
            
            embedder = EmbeddingManager()
            embeddings = embedder.embed_batch(texts)
            
            # ID'ler oluştur
            if ids is None:
                ids = [f"doc_{i}" for i in range(len(texts))]
            
            # Meta veriler
            if metadatas is None:
                metadatas = [{"source": "unknown"} for _ in texts]
            
            # ChromaDB'ye ekle
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"{len(texts)} doküman eklendi")
            return True
            
        except Exception as e:
            logger.error(f"Doküman ekleme hatası: {e}")
            return False
    
    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Sorgu yap ve benzer dokümanları bul
        
        Args:
            query: Arama metni
            n_results: Döndürülecek sonuç sayısı
            
        Returns:
            Benzer dokümanlar listesi
        """
        if self.collection is None:
            logger.error("Koleksiyon hazır değil")
            return []
        
        try:
            from src.embedding.embedder import EmbeddingManager
            
            embedder = EmbeddingManager()
            query_embedding = embedder.embed_text(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Formatla
            documents = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    documents.append({
                        'text': doc,
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'metadata': results['metadatas'][0][i] if 'metadatas' in results else {}
                    })
            
            logger.info(f"Arama tamamlandı: {len(documents)} sonuç")
            return documents
            
        except Exception as e:
            logger.error(f"Arama hatası: {e}")
            return []
    
    def get_documents(self):
        """Tüm dokümanları al"""
        try:
            if not self.collection:
                return []
            
            results = self.collection.get()
            
            documents = []
            if results and results['documents']:
                for i, doc in enumerate(results['documents']):
                    documents.append({
                        'text': doc,
                        'metadata': results['metadatas'][i] if 'metadatas' in results else {}
                    })
            
            logger.info(f"Toplam {len(documents)} doküman getirildi")
            return documents
        
        except Exception as e:
            logger.error(f"Doküman getirme hatası: {e}")
            return []
    
                self.client.delete_collection(name=self.collection_name)
                self.collection = None
                logger.info("Koleksiyon silindi")
                return True
        except Exception as e:
            logger.error(f"Koleksiyon silme hatası: {e}")
            return False
