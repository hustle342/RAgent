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
                metadatas = [{"source": "unknown", "labels": ""} for _ in texts]
            else:
                for meta in metadatas:
                    if 'labels' not in meta:
                        meta['labels'] = ""
                    elif isinstance(meta['labels'], list):
                        # Liste ise virgülle ayrılmış string'e çevir
                        meta['labels'] = ",".join(meta['labels'])
            
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
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        allowed_sources: Optional[List[str]] = None,
        required_labels: Optional[List[str]] = None,
        k: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
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
            
            # Backwards-compatibility: accept `k` param from callers
            if k is not None:
                query_size = max(k * 3, k)
            else:
                query_size = max(n_results * 3, n_results)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=query_size
            )
            
            # Formatla
            documents = []
            if results and results['documents']:
                # Debug: Tüm sonuçlardaki kaynak isimlerini logla
                all_sources = [results['metadatas'][0][i].get('source', 'N/A') for i in range(len(results['documents'][0]))]
                logger.info(f"DB'deki kaynak isimleri: {set(all_sources[:5])}")
                logger.info(f"Filtre: allowed_sources={allowed_sources}")
                
                for i, doc in enumerate(results['documents'][0]):
                    meta = results['metadatas'][0][i] if 'metadatas' in results else {}
                    source_name = meta.get('source')
                    labels_str = meta.get('labels', '') or ''
                    labels = [lbl.strip() for lbl in labels_str.split(',') if lbl.strip()] if labels_str else []

                    # Kaynak ve etiket filtreleri (sadece liste doluysa uygula)
                    if allowed_sources is not None and len(allowed_sources) > 0:
                        if source_name not in allowed_sources:
                            logger.debug(f"Chunk filtrelendi: '{source_name}' not in {allowed_sources}")
                            continue
                    if required_labels:
                        if not labels or not any(label in labels for label in required_labels):
                            continue

                    documents.append({
                        'text': doc,
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'metadata': meta
                    })

                    if len(documents) >= n_results:
                        break
            
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
    
    def delete_collection(self):
        """Koleksiyonu sil"""
        try:
            if self.client:
                self.client.delete_collection(name=self.collection_name)
                self.collection = None
                logger.info("Koleksiyon silindi")
                return True
        except Exception as e:
            logger.error(f"Koleksiyon silme hatası: {e}")
            return False
