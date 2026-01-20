"""
Özet Oluşturma Modülü
PDF dokümanlarının özetini oluştur
"""

import logging
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
            if summary_type == "bullet":
                prompt = f"""Aşağıdaki metni 5-7 ana nokta olarak özetle. 
Her nokta bir maddede olmalı (•).

Metin:
{document_text[:3000]}

Özet (Madde Başında):"""
            elif summary_type == "detailed":
                prompt = f"""Aşağıdaki metni detaylı olarak özetle. 
2-3 paragraf, tüm önemli noktaları içermeli.

Metin:
{document_text[:3000]}

Detaylı Özet:"""
            else:  # general
                prompt = f"""Aşağıdaki metni kısa ve öz olarak özetle.
1-2 paragraf, ana konuları içermeli.

Metin:
{document_text[:3000]}

Özet:"""
            
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
                max_tokens=1500
            )
            
            summary = message.choices[0].message.content
            logger.info(f"Özet oluşturuldu: {len(summary)} karakter")
            return summary
            
        except Exception as e:
            logger.error(f"Özet oluşturma hatası: {e}")
            return f"❌ Özet oluşturmada hata: {str(e)}"
