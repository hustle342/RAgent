"""
RAgent Web Arayüzü - GERÇEK ÇALIŞAN VERSİYON
Streamlit ile yapay zeka asistanı
"""

import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Proje root'u ekle
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.document_loader import DocumentLoader, TextSplitter
from src.embedding.vector_db import VectorDatabase
from src.rag.rag_system import RAGSystem
from src.rag.web_search import FreeWebSearcher
from src.rag.quiz_generator import QuizGenerator
from src.utils.voice import VoiceHandler

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# .env yükle
load_dotenv()

# Streamlit config
st.set_page_config(
    page_title="RAgent 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 30px;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Session State'e veri yükle
if 'vector_db' not in st.session_state:
    st.session_state.vector_db = None
if 'rag_system' not in st.session_state:
    st.session_state.rag_system = None
if 'document_loaded' not in st.session_state:
    st.session_state.document_loaded = False
if 'voice_handler' not in st.session_state:
    st.session_state.voice_handler = VoiceHandler()
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = {}
if 'web_searcher' not in st.session_state:
    st.session_state.web_searcher = None

# Sidebar
st.sidebar.markdown("# ⚙️ Ayarlar")
st.sidebar.markdown("---")

# API anahtarı kontrol
groq_api_key = os.getenv('GROQ_API_KEY')
if not groq_api_key:
    st.sidebar.error("⚠️ GROQ_API_KEY .env dosyasında ayarlanmadı!")
    st.sidebar.info("Lütfen `.env` dosyasını düzenle ve Groq API anahtarını ekle.")
else:
    st.sidebar.success("✅ Groq API bağlı")
    # RAG sistemini başlat
    if st.session_state.rag_system is None:
        st.session_state.rag_system = RAGSystem(groq_api_key=groq_api_key)
        st.session_state.web_searcher = FreeWebSearcher()
        st.session_state.quiz_generator = QuizGenerator(groq_api_key=groq_api_key)

# Sesli özellikler
st.sidebar.markdown("---")
st.sidebar.markdown("### 🎤 Sesli Özellikler")
use_voice = st.sidebar.checkbox("Sesli input/output kullan", value=False)

if use_voice:
    voice_status = st.session_state.voice_handler.is_available()
    if voice_status['both']:
        st.sidebar.success("✅ Sesli özellikler aktif")
    else:
        st.sidebar.warning("⚠️ Mikrofon erişimi gerekli")

# Web araması
st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Web Araması")
use_web_search = st.sidebar.checkbox("Dokümentlerde bulunmazsa web'de ara", value=True)

# Model seçimi
model = st.sidebar.selectbox(
    "Llama Model Seçin",
    [
        "llama-3.1-8b-instant",
        "llama-3.2-70b-versatile",
    ]
)

# Arayüz
st.markdown("""
<div class='main-header'>
    <h1>🤖 RAgent - Kişisel Bilgi Asistanı</h1>
    <p>Kendi dokümanlarınla konuşan AI</p>
</div>
""", unsafe_allow_html=True)

# Tab'lar
tab1, tab2, tab3, tab4 = st.tabs(["📤 Doküman Yükle", "❓ Soru Sor", "🎓 Quiz", "📊 Yönetim"])

# TAB 1: Doküman Yükleme
with tab1:
    st.subheader("Doküman Yükle")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "PDF veya TXT dosyasını seç",
            type=["pdf", "txt"],
            help="PDF veya metin dosyası yükleyebilirsin"
        )
    
    with col2:
        st.info("💡 **İpucu:** PDF'ler otomatik olarak metne dönüştürülür.")
    
    if uploaded_file:
        st.success(f"✅ Dosya seçildi: {uploaded_file.name}")
        
        if st.button("📥 Dokümanı İşle"):
            with st.spinner("⏳ Doküman işleniyor..."):
                try:
                    # 1. Dosyayı geçici olarak kaydet
                    temp_path = f"/tmp/{uploaded_file.name}"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 2. Dokümanı yükle
                    loader = DocumentLoader()
                    text = loader.load_document(temp_path)
                    
                    if not text:
                        st.error("❌ Doküman yüklenemedi!")
                    else:
                        # 3. Metni parçalara böl
                        splitter = TextSplitter(chunk_size=1000, overlap=200)
                        chunks = splitter.split_text(text)
                        
                        # 4. Vector DB oluştur ve ekle
                        st.session_state.vector_db = VectorDatabase(
                            db_path="./data/chroma_db",
                            collection_name="documents"
                        )
                        
                        metadatas = [
                            {"source": uploaded_file.name, "chunk": i}
                            for i in range(len(chunks))
                        ]
                        
                        st.session_state.vector_db.add_documents(chunks, metadatas=metadatas)
                        st.session_state.document_loaded = True
                        
                        st.success("✅ Doküman başarıyla işlendi!")
                        st.info(f"""
                        📊 İstatistikler:
                        - Toplam metin: {len(text)} karakter
                        - Parça sayısı: {len(chunks)}
                        - Dosya adı: {uploaded_file.name}
                        """)
                        
                        # Dosyayı sil
                        os.remove(temp_path)
                        
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
                    logger.error(f"Doküman işleme hatası: {e}")

# TAB 2: Soru Soruşturma
with tab2:
    st.subheader("Sorunuzu Sorun")
    
    if not st.session_state.document_loaded:
        st.warning("⚠️ Önce bir doküman yükle!")
    else:
        # Örnek soruları göster
        with st.expander("💡 Örnek Sorular"):
            st.write("""
            - "Bu doküman hakkında temel bilgiler nedir?"
            - "Belgedeki ana temalar nelerdir?"
            - "Spesifik bir konu hakkında detay verir misin?"
            """)
        
        # Soru input
        question = st.text_area(
            "Sorunuzu yazın:",
            placeholder="Doküman hakkında sormak istediğin soru...",
            height=100
        )
        
        # Sesli input
        if use_voice:
            col_text, col_voice = st.columns([3, 1])
            with col_voice:
                if st.button("🎤 Sesle Sor"):
                    with st.spinner("🎧 Dinleniyor..."):
                        voice_text = st.session_state.voice_handler.listen(timeout=5)
                        if voice_text:
                            question = voice_text
                            st.success(f"✅ Tanınan: {voice_text}")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submit_button = st.button("🔍 Ara", use_container_width=True)
        
        if submit_button and question:
            if not st.session_state.rag_system:
                st.error("❌ Groq API anahtarı ayarlanmamış!")
            else:
                with st.spinner("⏳ Cevap aranıyor..."):
                    try:
                        # 1. Dokümentlerde ara
                        search_results = st.session_state.vector_db.search(question, n_results=3)
                        
                        has_good_result = False
                        best_distance = 1.0
                        
                        if search_results:
                            # Distance kontrolü
                            best_distance = search_results[0].get('distance', 1)
                            has_good_result = best_distance < 0.8  # Threshold 0.8'e çıkar
                            
                            # Debug info
                            logger.info(f"Benzerlik distance: {best_distance}, Threshold: 0.8, Başarı: {has_good_result}")
                        
                        # 2. Cevap bulunduysa kullan
                        if has_good_result:
                            st.info(f"📄 Dokümanlardan bulundu (benzerlik: {best_distance:.3f}), cevap oluşturuluyor...")
                            answer = st.session_state.rag_system.process_question(
                                question,
                                st.session_state.vector_db,
                                k_results=3,
                                model=model
                            )
                            
                            # Cevap kontrol
                            if not answer or "bilmiyorum" in answer.lower():
                                logger.warning(f"Doküman bulundu ama cevap verilemedi: {answer}")
                                st.warning("⚠️ Doküman bulundu ama cevap oluşturulamadı, web'de aranıyor...")
                                if use_web_search and st.session_state.web_searcher:
                                    answer = st.session_state.web_searcher.search_and_answer(
                                        question,
                                        st.session_state.rag_system
                                    )
                                    source = "🌐 Web'den (fallback)"
                                else:
                                    answer = f"Dokümanlardan benzerlik buldum ({best_distance:.1%}) ama cevap oluşturamadım. Web araması devre dışı."
                                    source = "❌ Hata"
                            else:
                                source = "📄 Dokümanlardan"
                        
                        # 3. Bulunmadıysa web'de ara
                        elif use_web_search and st.session_state.web_searcher:
                            st.warning("📄 Dokümentlerde tam cevap bulunamadı, web'de arıyor...")
                            answer = st.session_state.web_searcher.search_and_answer(
                                question,
                                st.session_state.rag_system
                            )
                            if answer:
                                source = "🌐 Web'den"
                            else:
                                answer = "Üzgünüm, web'de de bu konuyla ilgili bilgi bulamadım."
                                source = "❌ Bulunamadı"
                        else:
                            answer = "Üzgünüm, bu soruyla ilgili bilgi bulamadım."
                            source = "❌ Bulunamadı"
                        
                        # 3. Cevabı göster
                        st.markdown("### 📝 Cevap")
                        st.success(answer if answer else "Üzgünüm, bu soruyla ilgili bilgi bulamadım.")
                        
                        # 4. Sesle oku
                        if use_voice and answer:
                            if st.button("🔊 Sesle Oku"):
                                with st.spinner("🎤 Seslendirilyor..."):
                                    st.session_state.voice_handler.speak(answer)
                                    st.success("✅ Seslendirildi!")
                        
                        # 5. Kaynak göster
                        st.markdown(f"### {source}")
                        if source.startswith("📄"):
                            search_results = st.session_state.vector_db.search(question, n_results=3)
                            if search_results:
                                for i, result in enumerate(search_results, 1):
                                    distance = result.get('distance', 'N/A')
                                    text_preview = result['text'][:200] + "..."
                                    st.write(f"**[{i}] Benzerlik: {distance:.3f}**")
                                    st.write(text_preview)
                                    st.divider()
                        
                    except Exception as e:
                        st.error(f"❌ Hata: {str(e)}")
                        logger.error(f"Soru işleme hatası: {e}")

# TAB 3: Quiz
with tab3:
    st.subheader("🎓 Quiz Soruları")
    
    if not st.session_state.document_loaded:
        st.warning("⚠️ Önce bir PDF dosyası yükleyin")
    else:
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if st.button("📝 Sorular Oluştur", use_container_width=True):
                with st.spinner("🤔 Sorular oluşturuluyor..."):
                    # Doküman metnini al
                    doc_chunks = st.session_state.vector_db.get_documents()
                    if doc_chunks:
                        full_text = " ".join([chunk['text'] for chunk in doc_chunks])
                        questions = st.session_state.quiz_generator.generate_quiz(full_text, num_questions=5)
                        st.session_state.quiz_questions = questions
                        st.session_state.quiz_answers = {}
                        st.success(f"✅ {len(questions)} soru oluşturuldu!")
        
        # Soruları göster
        if hasattr(st.session_state, 'quiz_questions') and st.session_state.quiz_questions:
            questions = st.session_state.quiz_questions
            
            for idx, q in enumerate(questions, 1):
                st.markdown(f"### Soru {idx}: {q['question']}")
                
                # Seçenekler
                selected = st.radio(
                    "Cevabı seçin:",
                    options=list(q['options'].keys()),
                    format_func=lambda x: f"{x}) {q['options'][x]}",
                    key=f"q{idx}"
                )
                
                # Cevabı kaydet
                st.session_state.quiz_answers[idx] = selected
                
                st.divider()
            
            # Sonuçları göster
            if st.button("✅ Cevapları Kontrol Et", use_container_width=True):
                correct = 0
                for idx, q in enumerate(questions, 1):
                    if idx in st.session_state.quiz_answers:
                        if st.session_state.quiz_answers[idx] == q['answer']:
                            correct += 1
                
                score = (correct / len(questions)) * 100
                
                st.markdown("---")
                st.markdown(f"## 📊 Sonuç: {correct}/{len(questions)} ({score:.0f}%)")
                
                if score >= 80:
                    st.success("🎉 Harika! Çok başarılısın!")
                elif score >= 60:
                    st.info("👍 İyi gidiş! Biraz daha çalışabilirsin.")
                else:
                    st.warning("⚠️ Dokümanı daha dikkatli oku ve tekrar dene.")

# TAB 4: Yönetim
with tab4:
    st.subheader("📊 Veritabanı Yönetimi")
    
    if st.session_state.document_loaded:
        st.success("✅ Doküman yüklü")
        st.info("Dokümanlar /data/chroma_db/ klasöründe saklanmaktadır.")
    else:
        st.info("ℹ️ Henüz doküman yüklenmedi")
    
    st.divider()
    
    st.subheader("🧹 Veri İşlemleri")
    
    if st.button("🗑️ Veritabanını Temizle", help="Tüm dokümanları sil"):
        if st.session_state.vector_db:
            if st.button("⚠️ Evet, sil"):
                try:
                    st.session_state.vector_db.delete_collection()
                    st.session_state.document_loaded = False
                    st.session_state.vector_db = None
                    st.success("✅ Veritabanı temizlendi")
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
    
    st.divider()
    
    st.subheader("ℹ️ Sistem Bilgileri")
    st.info(f"""
    - **Seçili Model:** {model}
    - **Embedding Modeli:** sentence-transformers/all-MiniLM-L6-v2
    - **Vector DB:** ChromaDB
    - **Sürüm:** 0.1.0
    - **Groq Bağlı:** {'✅ Evet' if groq_api_key else '❌ Hayır'}
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>RAgent v0.1.0 | Kişisel Bilgi Asistanı</p>
    <p style='font-size: 0.8em;'>Python + LangChain + Groq + ChromaDB + Streamlit</p>
</div>
""", unsafe_allow_html=True)
