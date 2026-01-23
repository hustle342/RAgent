"""
Web Araması Modülü - Ücretsiz Kaynaklar
Dokümentlerde cevap bulunamazsa Wikipedia/DuckDuckGo'dan ara
"""

import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class FreeWebSearcher:
    """Ücretsiz web araması (Wikipedia + DuckDuckGo)"""
    
    def __init__(self):
        """Başlat"""
        # Disable optional web search integrations by default.
        # These integrations required external packages that may not be installed
        # in lightweight environments. Keeping them disabled avoids startup warnings.
        self.has_wikipedia = False
        self.has_duckduckgo = False
        self.wikipedia = None
        self.ddgs = None
        logger.info("FreeWebSearcher başlatıldı — Wikipedia/DuckDuckGo entegrasyonları devre dışı")
    
    def search(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Web'de ara (ücretsiz kaynaklar)
        
        Args:
            query: Arama sorgusu
            max_results: Maksimum sonuç
            
        Returns:
            Arama sonuçları
        """
        results = []
        
        # 1. Wikipedia'dan ara
        if self.has_wikipedia:
            try:
                wikipedia_results = self.wikipedia.search(query, results=max_results * 2)
                
                for title in wikipedia_results:
                    if len(results) >= max_results:
                        break
                    
                    try:
                        page = self.wikipedia.page(title, auto_suggest=True)
                        # Boş özet kontrolü
                        if page.summary and len(page.summary) > 50:
                            results.append({
                                'title': page.title,
                                'url': page.url,
                                'content': page.summary[:500],
                                'source': 'Wikipedia'
                            })
                    except self.wikipedia.exceptions.DisambiguationError:
                        # Disambiguation sayfası - geç
                        continue
                    except self.wikipedia.exceptions.PageError:
                        # Sayfa bulunamadı - geç
                        continue
                    except Exception as e:
                        # Diğer hatalar - log ve geç
                        logger.debug(f"Wikipedia page hatası ({title}): {e}")
                        continue
            except Exception as e:
                logger.warning(f"Wikipedia araması hatası: {e}")
        
        # 2. Fallback: DuckDuckGo araması (Wikipedia'dan sonuç yoksa)
        if not results and self.has_duckduckgo:
            try:
                with self.ddgs() as ddgs:
                    ddgs_results = list(ddgs.text(query, max_results=max_results))
                    for result in ddgs_results:
                        results.append({
                            'title': result.get('title', 'Başlık yok'),
                            'url': result.get('link', ''),
                            'content': result.get('body', '')[:500],
                            'source': 'DuckDuckGo'
                        })
            except Exception as e:
                logger.warning(f"DuckDuckGo araması hatası: {e}")
        
        logger.info(f"Web araması tamamlandı: {len(results)} sonuç")
        return results
    
    def search_and_answer(self, query: str, rag_system) -> Optional[str]:
        """
        Web'de ara ve cevapla
        
        Args:
            query: Soru
            rag_system: RAG sistemi instance
            
        Returns:
            Web sonuçlarına dayalı cevap
        """
        results = self.search(query)
        
        if not results:
            return "Üzgünüm, web'de bu konuyla ilgili bilgi bulamadım."
        
        # Web sonuçlarını birleştir - direkt return et
        answers = []
        for result in results:
            title = result.get('title', 'Başlık yok')
            content = result.get('content', '')
            if content:
                answers.append(f"**{title}**: {content}")
        
        if answers:
            full_answer = "\n\n".join(answers)
            logger.info(f"Web araması cevap döndürüldü: {query}")
            return full_answer
        
        return "Üzgünüm, web'de bu konuyla ilgili bilgi bulamadım."

