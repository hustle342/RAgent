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
    
    def generate_quiz(self, document_text: str, num_questions: int = 5, difficulty: Optional[str] = None) -> List[Dict]:
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
            prompt = f"""TAMAMEN {num_questions} soru oluştur. KESIN FORMAT:

Metin: {document_text[:1500]}

FORMAT (SAPMA YAPMA):
Q1: [Soru]
A) [Cevap A]
B) [Cevap B]
C) [Cevap C]
D) [Cevap D]
ANSWER: A

Q2: [Soru]
A) [Cevap A]
B) [Cevap B]
C) [Cevap C]
D) [Cevap D]
ANSWER: B

Her soru tam {num_questions} satır olacak. ANSWER: satırını UNUTMA!
Sadece soruları yaz, başka hiçbir şey yazma.

ŞİMDİ {num_questions} SORU:"""
            
            message = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a quiz question generator. ALWAYS follow the exact format. Every question MUST have an ANSWER: line with A, B, C, or D. Never skip the ANSWER line."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=4000
            )
            
            response = message.choices[0].message.content
            logger.info(f"Groq yanıt uzunluğu: {len(response)} karaktere")
            logger.debug(f"Tam yanıt:\n{response}")
            # difficulty currently not used but accepted for API compatibility
            questions = self._parse_questions(response, num_questions)
            logger.info(f"{len(questions)} soru oluşturuldu")
            return questions
            
        except Exception as e:
            logger.error(f"Quiz oluşturma hatası: {e}")
            return []
    
    def _parse_questions(self, response: str, num_questions: int = 5) -> List[Dict]:
        """Groq çıktısını parse et - esnek format desteği"""
        questions = []
        current_question = None
        
        lines = response.split('\n')
        logger.info(f"Parse başladı: {len(lines)} satır")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            logger.debug(f"Line {i}: '{line[:60]}'")
            
            # Yeni soru: Q1:, Q2:, vs. ile başla
            if line and line[0] == 'Q' and ':' in line:
                # Önceki soruyu kaydet
                if current_question:
                    is_valid = self._is_valid_question(current_question)
                    logger.debug(f"Soru kontrol: {is_valid}, options={len(current_question.get('options', {}))}, answer={current_question.get('answer')}")
                    if is_valid:
                        questions.append(current_question)
                
                # Soru numarasını kontrol et
                parts = line.split(':', 1)
                if len(parts) > 1:
                    current_question = {
                        'question': parts[1].strip(),
                        'options': {},
                        'raw_lines': []
                    }
                    logger.debug(f"Yeni soru: {current_question['question'][:50]}")
            
            # Seçenek: A), B), C), D) ile başla
            if current_question and line and len(line) > 1:
                first_char = line[0].upper()
                if first_char in ['A', 'B', 'C', 'D'] and ')' in line:
                    parts = line.split(')', 1)
                    if len(parts) > 1:
                        current_question['options'][first_char] = parts[1].strip()
                        logger.debug(f"Seçenek {first_char} eklendi")
            
            # Cevap: ANSWER: A veya ANSWER:A
            if current_question and 'ANSWER' in line.upper():
                answer_line = line.upper()
                logger.debug(f"ANSWER satırı: '{answer_line}'")
                if ':' in answer_line:
                    answer = answer_line.split(':')[1].strip().upper()
                    logger.debug(f"Extracted answer: '{answer}', len={len(answer)}")
                    if answer and answer[0] in ['A', 'B', 'C', 'D']:
                        current_question['answer'] = answer[0]
                        logger.debug(f"Cevap set edildi: {current_question['answer']}")
                    else:
                        logger.debug(f"Answer validation failed: answer='{answer}', first_char='{answer[0] if answer else 'EMPTY'}'")
                else:
                    logger.debug(f"No colon in ANSWER line: '{answer_line}'")
        
        # Son soruyu ekle
        if current_question:
            is_valid = self._is_valid_question(current_question)
            logger.debug(f"Son soru kontrol: {is_valid}, options={len(current_question.get('options', {}))}, answer={current_question.get('answer')}")
            if is_valid:
                questions.append(current_question)
        
        # Geçerli soruları filtrele
        valid_questions = [q for q in questions if self._is_valid_question(q)]
        
        logger.info(f"Parse edildi: {len(valid_questions)}/{len(questions)} soru geçerli")
        return valid_questions[:num_questions]
    
    def _is_valid_question(self, q: Dict) -> bool:
        """Sorunun geçerli formatında olup olmadığını kontrol et"""
        return (
            'question' in q and q['question'].strip() and
            'options' in q and len(q.get('options', {})) == 4 and
            'answer' in q and q.get('answer') in ['A', 'B', 'C', 'D']
        )
