"""
Vektörleştirme (Embedding) Modülü
"""

from typing import List
import logging

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """HuggingFace Embeddings ile metin vektörleştirme"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Başlat
        
        Args:
            model_name: HuggingFace model adı
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name, device="cpu")
            self.model_name = model_name
            logger.info(f"Embedding modeli yüklendi: {model_name}")
        except Exception as e:
            logger.error(f"Embedding modeli yükleme hatası: {e}")
            self.model = None
    
    def embed_text(self, text: str):
        """
        Metni vektöre dönüştür
        
        Args:
            text: Vektörleştirilecek metin
            
        Returns:
            Vektör (numpy array)
        """
        if self.model is None:
            logger.error("Model yüklenemedi")
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding
        except Exception as e:
            logger.error(f"Embedding hatası: {e}")
            return None
    
    def embed_batch(self, texts: List[str]):
        """
        Metin listesini vektörleştir
        
        Args:
            texts: Metin listesi
            
        Returns:
            Vektör listesi
        """
        if self.model is None:
            logger.error("Model yüklenemedi")
            return []
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            logger.info(f"{len(texts)} metin vektörleştirildi")
            return embeddings
        except Exception as e:
            logger.error(f"Batch embedding hatası: {e}")
            return []
