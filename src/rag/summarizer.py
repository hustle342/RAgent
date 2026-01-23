"""
Özet Oluşturma Modülü
PDF dokümanlarının özetini oluştur
"""

import logging
import time
from typing import Optional
from groq import Groq

logger = logging.getLogger(__name__)


class Summarizer:
    """Dokümanlardan özet oluştur"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Başlat"""
        self.client = Groq(api_key=groq_api_key)
        logger.info("Summarizer başlatıldı")
    
    def summarize(self, document_text: str, summary_type: str = "general") -> str:
        """
        Dokümanın özetini oluştur
        
        Args:
            document_text: Doküman metni
            summary_type: Özet türü - "general", "detailed", "bullet"
            
        Returns:
            Özet metni
        """
        try:
            if not document_text.strip():
                return "📝 Özet oluşturmak için doküman metni gerekli."
            
            # Özet türüne göre prompt
            trimmed_text = document_text[:6000]

            if summary_type == "bullet":
                prompt = f"""Aşağıdaki metni 6-9 ana madde olarak özetle. 
Her madde tek satır ve açık olsun (• kullan).

Metin:
{trimmed_text}

Özet (Madde Başında):"""
            elif summary_type == "detailed":
                prompt = f"""Aşağıdaki metni kapsamlı şekilde özetle.
4-6 paragraf yaz; bağlam, ana argümanlar, önemli bulgular ve çıkarımları dahil et.
Gerekirse kısa alt örnekler ve rakamlar ekle.

Metin:
{trimmed_text}

Detaylı Özet:"""
            else:  # general
                prompt = f"""Aşağıdaki metni kısa ve öz olarak özetle.
1-2 paragraf, ana konuları içermeli.

Metin:
{trimmed_text}

Özet:"""
            
            retries = 3
            backoff = 2
            last_err = None

            for attempt in range(1, retries + 1):
                try:
                    message = self.client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {
                                "role": "system",
                                "content": "Sen yetkin bir özetci asistansın. Verilen metni kısa, anlaşılır ve bilgilendirici şekilde özetle."
                            },
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3,
                        max_tokens=2200
                    )
                    summary = message.choices[0].message.content
                    logger.info(f"Özet oluşturuldu: {len(summary)} karakter")
                    return summary
                except Exception as inner_e:
                    last_err = inner_e
                    err_text = str(inner_e)
                    if "429" in err_text or "Rate limit" in err_text or attempt < retries:
                        sleep_for = backoff * attempt
                        logger.warning(f"Özet alınamadı (deneme {attempt}/{retries}): {err_text}. {sleep_for}s bekleniyor.")
                        time.sleep(sleep_for)
                    else:
                        raise
            if last_err:
                raise last_err
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return f"❌ Özet oluşturmada hata: {str(e)}"
