"""
RAG (Retrieval Augmented Generation) Sistemi
"""

import os
import time
from typing import Optional, List, Dict, Any, Tuple
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# .env dosyasını yükle
load_dotenv()


class RAGSystem:
    """RAG Sistemi - Sorgu ve Cevaplama"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """
        Başlat
        
        Args:
            groq_api_key: Groq API anahtarı
        """
        self.groq_api_key = groq_api_key or os.getenv('GROQ_API_KEY')
        
        if not self.groq_api_key:
            logger.error("Groq API anahtarı bulunamadı")
            self.client = None
        else:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.groq_api_key)
                logger.info("Groq client başlatıldı")
            except Exception as e:
                logger.error(f"Groq client başlatma hatası: {e}")
                self.client = None
    
    def generate_answer(self, query: str, context: List[str], model: str = "llama-3.1-8b-instant", from_web: bool = False) -> Optional[str]:
        """
        Sorguya cevap üret - Kontekst temelinde
        
        Args:
            query: Kullanıcının sorusu
            context: İlgili doküman parçaları
            model: Kullanılacak model
            from_web: Web aramasından mı?
            
        Returns:
            Üretilen cevap
        """
        if self.client is None:
            logger.error("Groq client hazır değil")
            return None
        
        try:
            # Konteksti metin olarak formatla
            context_text = "\n\n".join(context)
            
            # System prompt - web veya doküman kaynağına göre değiştir
            if from_web:
                system_prompt = """Sen bir yardımcı asistansın. Verilen web araması sonuçlarına dayanarak soruyu cevapla.
Kısa ve öz cevap ver. Bilgi varsa paylaş, yoksa "Bilgiye ulaşamadım" de."""
            else:
                system_prompt = """Sen bir yardımcı asistansın. Verilen doküman parçalarına dayanarak soruyu cevapla.
Mümkün olduğunca dokümanın içeriğini kullan. Kısa ve öz cevap ver."""
            
            # User message
            user_message = f"""Bağlam:
{context_text}

Soru: {query}

Verilen bağlama göre kısa ve özlü cevap ver."""
            
            # Basit retry ile rate-limit ve geçici hataları yakala
            retries = 3
            backoff = 2
            last_err = None

            for attempt in range(1, retries + 1):
                try:
                    message = self.client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                    answer = message.choices[0].message.content
                    logger.info("Cevap üretildi")
                    return answer
                except Exception as inner_e:
                    last_err = inner_e
                    err_text = str(inner_e)
                    if "429" in err_text or "Rate limit" in err_text or attempt < retries:
                        sleep_for = backoff * attempt
                        logger.warning(f"Groq cevabı alınamadı (deneme {attempt}/{retries}): {err_text}. {sleep_for}s bekleniyor.")
                        time.sleep(sleep_for)
                    else:
                        raise
            if last_err:
                raise last_err
            
        except Exception as e:
            logger.error(f"Cevap üretme hatası: {e}")
            return None
    
    def process_question(
        self,
        query: str,
        vector_db,
        k_results: int = 5,
        model: str = "llama-3.1-8b-instant",
        allowed_sources: Optional[List[str]] = None,
        required_labels: Optional[List[str]] = None,
        return_sources: bool = False,
    ) -> Optional[Any]:
        """
        Tam RAG akışı - Arama + Cevaplama
        
        Args:
            query: Kullanıcının sorusu
            vector_db: Vector Database instance
            k_results: Döndürülecek doküman sayısı
            model: Kullanılacak LLM modeli
            
        Returns:
            Üretilen cevap
        """
        try:
            # 1. Vektör veritabanında ara
            search_results = vector_db.search(
                query,
                n_results=k_results,
                allowed_sources=allowed_sources,
                required_labels=required_labels,
            )
            
            if not search_results:
                message = "Üzgünüm, bu soruyla ilgili bilgi bulamadım."
                return {"answer": message, "sources": []} if return_sources else message
            
            # 2. Konteksti çıkar
            context = [result['text'] for result in search_results]
            
            # 3. Cevap üret
            answer = self.generate_answer(query, context, model=model)
            
            if return_sources:
                return {"answer": answer, "sources": search_results}
            return answer
            
        except Exception as e:
            logger.error(f"Soru işleme hatası: {e}")
            return None
