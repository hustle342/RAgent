"""
Quiz Oluşturma Modülü
PDF dokümanlarından otomatik sorular üretme
"""

import logging
from typing import List, Dict, Optional
from groq import Groq

logger = logging.getLogger(__name__)


class QuizGenerator:
    """PDF'ten quiz soruları oluştur"""
    
    def __init__(self, groq_api_key: Optional[str] = None):
        """Başlat"""
        self.client = Groq(api_key=groq_api_key)
        logger.info("Quiz Generator başlatıldı")
    
    def generate_quiz(self, document_text: str, num_questions: int = 5) -> List[Dict]:
        """
        Doküman'dan quiz soruları üret
        
        Args:
            document_text: Doküman metni
            num_questions: Kaç soru üretileceği
            
        Returns:
            Sorular listesi (soru, doğru cevap, seçenekler)
        """
        try:
            # Groq'dan sorular üret
            prompt = f"""Aşağıdaki metinde {num_questions} çoktan seçmeli soru oluştur.

Metin:
{document_text[:2000]}

Çıkış formatı (her soru için):
SORU: [Soru metni]
A) [Seçenek 1]
B) [Seçenek 2]
C) [Seçenek 3]
D) [Seçenek 4]
CEVAP: [A/B/C/D]

Soruları şimdi oluştur:"""
            
            message = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen bir eğitim sorusu yazarısın. Metnin ana konularından ilginç sorular yaz."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response = message.choices[0].message.content
            questions = self._parse_questions(response)
            logger.info(f"{len(questions)} soru oluşturuldu")
            return questions
            
        except Exception as e:
            logger.error(f"Quiz oluşturma hatası: {e}")
            return []
    
    def _parse_questions(self, response: str) -> List[Dict]:
        """Groq çıktısını parse et"""
        questions = []
        current_question = {}
        
        lines = response.split('\n')
        options = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith('SORU:'):
                # Yeni soru
                if current_question:
                    current_question['options'] = options
                    questions.append(current_question)
                    current_question = {}
                    options = {}
                
                current_question['question'] = line.replace('SORU:', '').strip()
            
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                # Seçenek
                option_key = line[0]  # A, B, C veya D
                option_text = line[2:].strip()
                options[option_key] = option_text
            
            elif line.startswith('CEVAP:'):
                # Cevap
                answer = line.replace('CEVAP:', '').strip()
                if answer in ['A', 'B', 'C', 'D']:
                    current_question['answer'] = answer
        
        # Son soruyu ekle
        if current_question:
            current_question['options'] = options
            questions.append(current_question)
        
        # Geçerli soruları filtrele
        valid_questions = [
            q for q in questions 
            if 'question' in q and 'options' in q and 'answer' in q
            and len(q['options']) >= 4
        ]
        
        return valid_questions[:5]  # Max 5 soru
