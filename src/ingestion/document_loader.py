"""
PDF ve Web İçeriği İşleme Modülü
"""

from pathlib import Path
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:
    """Doküman yükleyicisi - PDF ve web içeriğini işler"""
    
    def __init__(self):
        """Başlat"""
        self.supported_formats = ['.pdf', '.txt']
    
    def load_pdf(self, file_path: str) -> Optional[str]:
        """
        PDF dosyasını yükle ve metni çıkar
        
        Args:
            file_path: PDF dosyasının yolu
            
        Returns:
            Çıkarılan metin
        """
        try:
            from PyPDF2 import PdfReader
            
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                logger.info(f"PDF yüklendi: {file_path}")
                return text
                
        except Exception as e:
            logger.error(f"PDF yükleme hatası: {e}")
            return None
    
    def load_text(self, file_path: str) -> Optional[str]:
        """
        Metin dosyasını yükle
        
        Args:
            file_path: Metin dosyasının yolu
            
        Returns:
            Dosya içeriği
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                logger.info(f"Metin dosyası yüklendi: {file_path}")
                return text
        except Exception as e:
            logger.error(f"Metin dosyası yükleme hatası: {e}")
            return None
    
    def load_document(self, file_path: str) -> Optional[str]:
        """
        Desteklenen herhangi bir dosyayı yükle
        
        Args:
            file_path: Dosyanın yolu
            
        Returns:
            Dosya içeriği
        """
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.pdf':
            return self.load_pdf(file_path)
        elif suffix == '.txt':
            return self.load_text(file_path)
        else:
            logger.error(f"Desteklenmeyen dosya formatı: {suffix}")
            return None


class TextSplitter:
    """Metni parçalara böl - RAG için hazırlık"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Başlat
        
        Args:
            chunk_size: Her parçanın maksimum karakteri
            overlap: Parçalar arasındaki örtüşme
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_text(self, text: str) -> List[str]:
        """
        Metni parçalara böl
        
        Args:
            text: Bölünecek metin
            
        Returns:
            Metin parçaları listesi
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Son kısım için word boundary'yi bul
            if end < len(text):
                # Parçanın sonundan geriye doğru space ara
                end = text.rfind(' ', start, end)
                if end == -1 or end <= start:
                    end = start + self.chunk_size
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Sonraki parça overlap kadar geri gitsin
            start = end - self.overlap
        
        logger.info(f"Metin {len(chunks)} parçaya bölündü")
        return chunks
