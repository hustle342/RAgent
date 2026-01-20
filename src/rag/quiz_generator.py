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
            prompt = f"""Aşağıdaki metindan {num_questions} çoktan seçmeli soru oluştur.

Metin:
{document_text[:2000]}

Çıkış formatı (her soru için ayrı satırlar):
Q1: [Soru metni]
A) [Seçenek 1]
B) [Seçenek 2]
C) [Seçenek 3]
D) [Seçenek 4]
ANSWER: [A/B/C/D]

Q2: [Soru metni]
...

Başla:"""
            
            message = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "Kullanıcı tarafından verilen metin hakkında çoktan seçmeli sorular oluştur. Soruları verilen formatta yaz."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            response = message.choices[0].message.content
            logger.info(f"Groq yanıt: {response[:200]}")
            questions = self._parse_questions(response)
            logger.info(f"{len(questions)} soru oluşturuldu")
            return questions
            
        except Exception as e:
            logger.error(f"Quiz oluşturma hatası: {e}")
            return []
    
    def _parse_questions(self, response: str) -> List[Dict]:
        """Groq çıktısını parse et"""
        questions = []
        current_question = None
        
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Yeni soru
            if line.startswith('Q') and ':' in line:
                if current_question and 'answer' in current_question:
                    questions.append(current_question)
                
                current_question = {
                    'question': line.split(':', 1)[1].strip(),
                    'options': {}
                }
            
            # Seçenek
            elif current_question and line and line[0] in ['A', 'B', 'C', 'D'] and ')' in line:
                option_key = line[0]
                option_text = line.split(')', 1)[1].strip()
                current_question['options'][option_key] = option_text
            
            # Cevap
            elif current_question and line.upper().startswith('ANSWER:'):
                answer = line.split(':', 1)[1].strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    current_question['answer'] = answer
        
        # Son soruyu ekle
        if current_question and 'answer' in current_question:
            questions.append(current_question)
        
        # Geçerli soruları filtrele
        valid_questions = [
            q for q in questions 
            if 'question' in q and 'options' in q and 'answer' in q
            and len(q['options']) == 4
        ]
        
        logger.info(f"Parse edildi: {len(valid_questions)}/{len(questions)} soru geçerli")
        return valid_questions[:5]  # Max 5 soru
