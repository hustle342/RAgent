#!/usr/bin/env python3
"""Test quiz generator"""
import sys
import logging
sys.path.insert(0, '/home/serdarpop/Masaüstü/RAgent')

logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s')
logger = logging.getLogger(__name__)

from src.rag.quiz_generator import QuizGenerator
from dotenv import load_dotenv
import os

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    print("❌ GROQ_API_KEY bulunamadı!")
    sys.exit(1)

qg = QuizGenerator(groq_api_key)

test_text = """Sublingual apse, M. mylohyoideus'un iç yüzünde yer alır. 
Alt çene çevresinde meydana gelen iltihaplar arasında önemli bir konumdadır. 
Bu apse, submandibuler bölgede oluşan enfeksiyonların bir sonucu olabilir.
Perimandibuler abseler genellikle dişlerden kaynaklanan enfeksiyonlar sonucu oluşur."""

print("\n🎯 Test: 2 soru üret\n")
questions = qg.generate_quiz(test_text, 2)

print(f"\n\n✅ SONUÇ: {len(questions)} soru oluşturuldu\n")
for i, q in enumerate(questions, 1):
    print(f"Q{i}: {q['question']}")
    for opt in ['A', 'B', 'C', 'D']:
        print(f"  {opt}) {q['options'].get(opt, '❌ EKSIK')}")
    print(f"  ✓ Cevap: {q['answer']}\n")
