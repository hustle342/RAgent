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
import hashlib
import re

# Proje root'u ekle
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.document_loader import DocumentLoader, TextSplitter
from src.embedding.vector_db import VectorDatabase
from src.rag.rag_system import RAGSystem
from src.rag.web_search import FreeWebSearcher
from src.rag.quiz_generator import QuizGenerator
from src.rag.summarizer import Summarizer
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
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Space Grotesk', sans-serif;
        background: radial-gradient(circle at 20% 20%, #f4f7ff 0, #eef2fb 25%, #e6ebff 45%, #f6f8ff 70%);
    }
    .main-header {
        text-align: center;
        color: #0f172a;
        margin-bottom: 30px;
        padding: 26px 18px;
        border-radius: 16px;
        background: linear-gradient(135deg, #e0f2ff 0%, #e6e9ff 50%, #f7f7ff 100%);
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    }
    .main-header h1 {
        margin-bottom: 6px;
        font-weight: 700;
    }
    .main-header p {
        margin: 0;
        color: #475569;
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.72);
        border: 1px solid rgba(255, 255, 255, 0.5);
        border-radius: 14px;
        padding: 18px 18px 12px 18px;
        box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
        backdrop-filter: blur(6px);
    }
    .info-box {
        background-color: #eef2ff;
        padding: 14px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #dfe3ff;
        color: #1f2a4d;
    }
    .success-box {
        background-color: #ecfdf3;
        padding: 14px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #bbf7d0;
    }
    .error-box {
        background-color: #fff1f2;
        padding: 14px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #fecdd3;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        border-radius: 12px;
        background: #eef2ff;
        color: #0f172a;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        color: white;
        box-shadow: 0 10px 24px rgba(99,102,241,0.35);
    }
    .stButton>button {
        border-radius: 12px;
        border: none;
        padding: 10px 16px;
        font-weight: 600;
        background: linear-gradient(135deg, #2563eb, #4f46e5);
        color: white;
        box-shadow: 0 10px 24px rgba(37,99,235,0.25);
        transition: transform 0.12s ease, box-shadow 0.12s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 30px rgba(37,99,235,0.32);
    }
    .stDownloadButton>button {
        border-radius: 12px;
        border: 1px solid #cbd5e1;
        background: white;
        color: #0f172a;
        font-weight: 600;
        padding: 10px 16px;
    }
    /* Smaller captions */
    .stCaption, .stMarkdown p {
        color: #475569;
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
if 'quiz_results_shown' not in st.session_state:
    st.session_state.quiz_results_shown = False
if 'web_searcher' not in st.session_state:
    st.session_state.web_searcher = None
if 'summarizer' not in st.session_state:
    st.session_state.summarizer = None
if 'loaded_documents' not in st.session_state:
    st.session_state.loaded_documents = {}  # {doc_name: {data, active}}
if 'active_documents' not in st.session_state:
    st.session_state.active_documents = []  # Aktif dokümanlarin adları
if 'selected_labels' not in st.session_state:
    st.session_state.selected_labels = []  # Etiket filtreleri
if 'summary_audio' not in st.session_state:
    st.session_state.summary_audio = None
if 'summary_text' not in st.session_state:
    st.session_state.summary_text = ""
if 'summary_cache' not in st.session_state:
    st.session_state.summary_cache = {}
if 'answer_cache' not in st.session_state:
    st.session_state.answer_cache = {}
if 'last_error' not in st.session_state:
    st.session_state.last_error = None
if 'last_failed_query' not in st.session_state:
    st.session_state.last_failed_query = None
if 'last_failed_params' not in st.session_state:
    st.session_state.last_failed_params = {}


def get_active_documents_text():
    """Aktif dokümanlardan birleştirilmiş text döndür"""
    active_texts = []
    for doc_name, doc_info in st.session_state.loaded_documents.items():
        if doc_info.get('active', False):
            active_texts.append(doc_info.get('text', ''))
    return "\n\n---\n\n".join(active_texts)


def get_all_labels():
    """Tüm dokümanlardan benzersiz etiket listesini al"""
    labels = set()
    for doc_info in st.session_state.loaded_documents.values():
        for label in doc_info.get('labels', []):
            labels.add(label)
    return sorted(labels)


def get_allowed_sources(selected_labels=None):
    """Aktiflik ve etiket filtrelerine göre kaynak doküman isimlerini döndür"""
    selected_labels = selected_labels or []
    allowed = []
    for doc_name, doc_info in st.session_state.loaded_documents.items():
        if not doc_info.get('active', False):
            continue
        labels = doc_info.get('labels', [])
        if selected_labels:
            if not labels or not any(label in labels for label in selected_labels):
                continue
        allowed.append(doc_name)
    return allowed


def highlight_snippet(text: str, query: str, max_len: int = 220) -> str:
    """Sorgu anahtar kelimelerini snippet içinde kalın göster"""
    keywords = [w for w in re.split(r"[^\wçğıöşüÇĞİÖŞÜ]+", query) if len(w) >= 4]
    snippet = text[:max_len]
    for kw in keywords:
        try:
            snippet = re.sub(rf"({re.escape(kw)})", r"**\1**", snippet, flags=re.IGNORECASE)
        except re.error:
            continue
    return snippet

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
        st.session_state.summarizer = Summarizer(groq_api_key=groq_api_key)

# Yüklenen Dokümanlar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 Yüklenen Dokümanlar")
if st.session_state.loaded_documents:
    for doc_name in st.session_state.loaded_documents:
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            is_active = st.sidebar.checkbox(
                doc_name,
                value=st.session_state.loaded_documents[doc_name].get('active', True),
                key=f"doc_{doc_name}"
            )
            st.session_state.loaded_documents[doc_name]['active'] = is_active
            labels = st.session_state.loaded_documents[doc_name].get('labels', [])
            if labels:
                st.sidebar.caption(f"Etiketler: {', '.join(labels)}")
            else:
                st.sidebar.caption("Etiket: Yok")
        with col2:
            if st.sidebar.button("🗑️", key=f"del_{doc_name}", help="Sil"):
                del st.session_state.loaded_documents[doc_name]
                st.rerun()
else:
    st.sidebar.info("📝 Henüz doküman yüklenmedi")

# Etiket filtreleme
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏷️ Etiket Filtresi")
all_labels = get_all_labels()
if all_labels:
    selected = st.sidebar.multiselect(
        "Kullanılacak etiketler",
        options=all_labels,
        default=st.session_state.selected_labels,
        help="Seçili etiketlere sahip aktif dokümanlar aranır"
    )
    st.session_state.selected_labels = selected
else:
    st.sidebar.info("Henüz etiket eklenmedi")

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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📤 Doküman Yükle", "❓ Soru Sor", "🎓 Quiz", "📊 Yönetim", "📝 Özet"])

# TAB 1: Doküman Yükleme
with tab1:
    st.subheader("Doküman Yükle")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_files = st.file_uploader(
            "Dosyaları seç (PDF, DOCX, PPTX, TXT)",
            type=["pdf", "txt", "docx", "pptx"],
            accept_multiple_files=True,
            help="Bir veya birden fazla dosya yükleyebilirsin"
        )
    
    with col2:
        st.info("💡 **Desteklenen Formatlar:** PDF, DOCX, PPTX, TXT")
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} dosya seçildi")
        
        if st.button("📥 Dokümanları İşle", use_container_width=True):
            with st.spinner("⏳ Dokümanlar işleniyor..."):
                try:
                    # Eğer veritabanı yok ise oluştur
                    if st.session_state.vector_db is None:
                        st.session_state.vector_db = VectorDatabase()
                    
                    all_success = True
                    
                    for uploaded_file in uploaded_files:
                        try:
                            # 1. Dosyayı geçici olarak kaydet
                            temp_dir = os.path.join(os.getcwd(), "temp_uploads")
                            os.makedirs(temp_dir, exist_ok=True)
                            temp_path = os.path.join(temp_dir, uploaded_file.name)
                            
                            logger.info(f"Dosya kaydediliyor: {temp_path}, boyut: {uploaded_file.size} bytes")
                            with open(temp_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            logger.info(f"Dosya kaydedildi: {temp_path}")
                            
                            # 2. Dokümanı yükle
                            loader = DocumentLoader()
                            text = loader.load_document(temp_path)
                            
                            if not text:
                                st.error(f"❌ {uploaded_file.name} yüklenemedi!")
                                all_success = False
                                continue
                            
                            # 3. Metni parçala
                            splitter = TextSplitter()
                            chunks = splitter.split_text(text)
                            
                            # 4. Metadataya doc adını ekle
                            metadatas = [
                                {"source": uploaded_file.name, "chunk": i, "labels": ""}
                                for i in range(len(chunks))
                            ]
                            
                            # 5. Benzersiz ID'ler oluştur (doc adı + chunk index)
                            import hashlib
                            doc_hash = hashlib.md5(uploaded_file.name.encode()).hexdigest()[:8]
                            ids = [f"{doc_hash}_{i}" for i in range(len(chunks))]
                            
                            # 6. Dokümanları veritabanına ekle
                            success = st.session_state.vector_db.add_documents(
                                chunks, 
                                metadatas=metadatas,
                                ids=ids
                            )
                            
                            if not success:
                                st.error(f"❌ {uploaded_file.name} veritabanına eklenemedi!")
                                all_success = False
                                continue
                            
                            logger.info(f"ChromaDB'ye eklendi: {uploaded_file.name} ({len(chunks)} chunk, ids: {ids[:2]}...)")
                            
                            # 7. Session state'e ekle
                            st.session_state.loaded_documents[uploaded_file.name] = {
                                'text': text,
                                'chunks': chunks,
                                'active': True,
                                'type': uploaded_file.name.split('.')[-1].upper(),
                                'labels': []
                            }
                            
                            st.success(f"✅ {uploaded_file.name} işlendi ({len(chunks)} parça)")
                            
                            # Geçici dosyayı temizle
                            try:
                                os.remove(temp_path)
                            except:
                                pass
                            
                        except Exception as e:
                            error_msg = f"Hata ({uploaded_file.name}): {str(e)}"
                            st.error(f"❌ {error_msg}")
                            logger.error(f"Dosya işleme hatası: {error_msg}", exc_info=True)
                            all_success = False
                    
                    if all_success:
                        st.session_state.document_loaded = True
                        st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
                    logger.error(f"Doküman işleme hatası: {e}")
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # Yüklenen dokümanlar listesi
    if st.session_state.loaded_documents:
        st.subheader("📄 İşlenen Dokümanlar")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        for doc_name, doc_info in st.session_state.loaded_documents.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                status = "✅ Aktif" if doc_info['active'] else "⏸️ Pasif"
                st.write(f"**{doc_name}** ({doc_info.get('type', 'UNKNOWN')}) - {status}")
                labels = doc_info.get('labels', [])
                if labels:
                    st.caption(f"Etiketler: {', '.join(labels)}")
                else:
                    st.caption("Etiket: Yok")
            with col2:
                st.caption(f"{len(doc_info.get('chunks', []))} parça")
        st.markdown("</div>", unsafe_allow_html=True)

# TAB 2: Soru Soruşturma
with tab2:
    st.subheader("Sorunuzu Sorun")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    retry_trigger = False
    if st.session_state.last_error:
        cols_err = st.columns([4, 1])
        with cols_err[0]:
            st.warning(f"⚠️ Son istekte hata: {st.session_state.last_error}")
        with cols_err[1]:
            if st.button("🔄 Yeniden dene", key="retry_last_error"):
                retry_trigger = True
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
        default_question = st.session_state.last_failed_query if retry_trigger and st.session_state.last_failed_query else ""
        question = st.text_area(
            "Sorunuzu yazın:",
            value=default_question,
            placeholder="Doküman hakkında sormak istediğin soru...",
            height=100
        )
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submit_button = st.button("🔍 Ara", use_container_width=True) or retry_trigger
        
        if submit_button and question:
            if not st.session_state.rag_system:
                st.error("❌ Groq API anahtarı ayarlanmamış!")
            else:
                with st.spinner("⏳ Cevap aranıyor..."):
                    try:
                        selected_labels = st.session_state.selected_labels
                        allowed_sources = get_allowed_sources(selected_labels)
                        # Eğer hiç doküman yoksa veya hepsi pasifse None kullan (filtresiz ara)
                        if not allowed_sources:
                            allowed_sources = None
                        cache_key = (
                            question.strip(),
                            tuple(sorted(allowed_sources)) if allowed_sources else ('all',),
                            model
                        )

                        if allowed_sources is not None and len(allowed_sources) == 0:
                            st.warning("⚠️ Seçili etiket/aktif doküman eşleşmesi yok. Etiket filtresini temizle veya bir dokümanı aktif et.")
                            answer = None
                            source = "❌ Bulunamadı"
                            search_results = []
                        elif cache_key in st.session_state.answer_cache:
                            cached = st.session_state.answer_cache[cache_key]
                            answer = cached.get("answer")
                            search_results = cached.get("sources", [])
                            source = cached.get("source", "📄 Önbellekten")
                            st.info("⚡ Önbellekten yanıt getirildi")
                        else:
                            # 1. Dokümanlarda filtreli arama
                            logger.info(f"Arama başlatılıyor: allowed_sources={allowed_sources}, soru='{question[:50]}...'")
                            search_results = st.session_state.vector_db.search(
                                question,
                                n_results=8,
                                allowed_sources=allowed_sources
                            )
                            logger.info(f"Arama sonucu: {len(search_results)} chunk bulundu")
                            has_good_result = False
                            best_distance = 1.0

                            if search_results:
                                best_distance = search_results[0].get('distance', 1)
                                has_good_result = best_distance < 1.0
                                logger.info(
                                    f"Benzerlik distance: {best_distance}, Threshold: 1.0, Başarı: {has_good_result}"
                                )

                            # 2. Cevap bulunduysa kullan
                            if has_good_result:
                                st.info(
                                    f"📄 Filtreli dokümanlardan bulundu (benzerlik: {best_distance:.3f}), cevap oluşturuluyor..."
                                )
                                response = st.session_state.rag_system.process_question(
                                    question,
                                    st.session_state.vector_db,
                                    k_results=8,
                                    model=model,
                                    allowed_sources=allowed_sources,
                                    return_sources=True,
                                )
                                answer = response.get("answer") if isinstance(response, dict) else response
                                search_results = response.get("sources", search_results) if isinstance(response, dict) else search_results

                                if not answer or len(answer.strip()) < 20 or "bilmiyorum" in answer.lower() or "bilgi bulamadım" in answer.lower():
                                    logger.warning(f"Doküman bulundu ama cevap verilemedi: {answer}")
                                    st.warning("⚠️ Doküman bulundu ama cevap oluşturulamadı, web'de aranıyor...")
                                    if use_web_search and st.session_state.web_searcher:
                                        answer = st.session_state.web_searcher.search_and_answer(
                                            question,
                                            st.session_state.rag_system
                                        )
                                        source = "🌐 Web'den (fallback)"
                                    else:
                                        answer = (
                                            f"Dokümanlardan benzerlik buldum ({best_distance:.1%}) ama cevap oluşturamadım. "
                                            "Web araması devre dışı."
                                        )
                                        source = "❌ Hata"
                                else:
                                    source = "📄 Filtreli dokümanlardan"
                                    st.session_state.answer_cache[cache_key] = {
                                        "answer": answer,
                                        "sources": search_results,
                                        "source": source,
                                    }

                            # 3. Bulunmadıysa web'de ara
                            elif use_web_search and st.session_state.web_searcher:
                                st.warning("📄 Filtreli dokümanlarda tam cevap bulunamadı, web'de arıyor...")
                                answer = st.session_state.web_searcher.search_and_answer(
                                    question,
                                    st.session_state.rag_system
                                )
                                if answer:
                                    source = "🌐 Web'den"
                                    st.session_state.answer_cache[cache_key] = {
                                        "answer": answer,
                                        "sources": [],
                                        "source": source,
                                    }
                                else:
                                    answer = "Üzgünüm, web'de de bu konuyla ilgili bilgi bulamadım."
                                    source = "❌ Bulunamadı"
                            else:
                                answer = "Üzgünüm, bu soruyla ilgili bilgi bulamadım."
                                source = "❌ Bulunamadı"

                        st.session_state.last_error = None

                        # 3. Cevabı göster
                        st.markdown("### 📝 Cevap")
                        st.success(answer if answer else "Üzgünüm, bu soruyla ilgili bilgi bulamadım.")
                        
                        # 5. Kaynak göster
                        st.markdown("### 📎 Kaynaklar")
                        if source.startswith("📄") and search_results:
                            for i, result in enumerate(search_results, 1):
                                meta = result.get('metadata', {})
                                distance = result.get('distance', None)
                                doc_name = meta.get('source', 'Bilinmiyor')
                                chunk_id = meta.get('chunk', '-')
                                distance_txt = f"{distance:.3f}" if distance is not None else "N/A"
                                snippet = highlight_snippet(result['text'], question)
                                st.markdown(
                                    f"""
                                    <div class='info-box'>
                                    <strong>[{i}] {doc_name}</strong> • Parça {chunk_id} • Benzerlik: {distance_txt}<br>
                                    {snippet}...
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.info(source)
                        
                    except Exception as e:
                        err_text = str(e)
                        st.error(f"❌ Hata: {err_text}")
                        st.session_state.last_error = err_text
                        st.session_state.last_failed_query = question
                        st.session_state.last_failed_params = {
                            "model": model,
                            "labels": selected_labels,
                            "allowed_sources": allowed_sources,
                        }
                        logger.error(f"Soru işleme hatası: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 3: Quiz
with tab3:
    st.subheader("🎓 Quiz Soruları")
    
    if not st.session_state.loaded_documents:
        st.warning("⚠️ Önce bir doküman yükleyin")
    else:
        active_docs = [name for name, info in st.session_state.loaded_documents.items() if info.get('active')]
        
        if not active_docs:
            st.warning("⚠️ En az bir doküman aktif etmen gerekiyor")
        else:
            st.info(f"💡 {len(active_docs)} aktif doküman seçildi")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                num_quiz_questions = st.slider("Soru Sayısı", min_value=1, max_value=10, value=5)
                if st.button("📝 Sorular Oluştur", use_container_width=True):
                    with st.spinner("🤔 Sorular oluşturuluyor..."):
                        # Aktif dokümanlardan text al
                        full_text = get_active_documents_text()
                        if full_text.strip():
                            questions = st.session_state.quiz_generator.generate_quiz(full_text, num_questions=num_quiz_questions)
                            st.session_state.quiz_questions = questions
                            st.session_state.quiz_answers = {}
                            st.session_state.quiz_results_shown = False
                            st.success(f"✅ {len(questions)} soru oluşturuldu!")
                        else:
                            st.error("❌ Doküman metni bulunamadı")
            
            # Soruları göster
            if hasattr(st.session_state, 'quiz_questions') and st.session_state.quiz_questions:
                questions = st.session_state.quiz_questions
                
                for idx, q in enumerate(questions, 1):
                    st.markdown(f"### Soru {idx}: {q['question']}")
                    
                    # Radio seçimi - başlangıçta seçili olmayacak
                    selected = st.radio(
                        "Cevabı seçin:",
                        options=list(q['options'].keys()),
                        format_func=lambda x: f"{x}) {q['options'][x]}",
                        key=f"q{idx}",
                        index=None  # Başlangıçta seçili olmayan
                    )
                    
                    # Cevabı kaydet
                    if selected:
                        st.session_state.quiz_answers[idx] = selected
                    
                    st.divider()
                
                # Sonuçları göster
                if st.button("✅ Cevapları Kontrol Et", use_container_width=True):
                    st.session_state.quiz_results_shown = True
                    correct = 0
                    results = {}
                    
                    for idx, q in enumerate(questions, 1):
                        if idx in st.session_state.quiz_answers:
                            user_answer = st.session_state.quiz_answers[idx]
                            is_correct = user_answer == q['answer']
                            if is_correct:
                                correct += 1
                            results[idx] = {
                                'user_answer': user_answer,
                                'correct_answer': q['answer'],
                                'is_correct': is_correct
                            }
                    
                    score = (correct / len(questions)) * 100
                    
                    st.markdown("---")
                    st.markdown(f"## 📊 Sonuç: {correct}/{len(questions)} ({score:.0f}%)")
                    
                    if score >= 80:
                        st.success("🎉 Harika! Çok başarılısın!")
                    elif score >= 60:
                        st.info("👍 İyi gidiş! Biraz daha çalışabilirsin.")
                    else:
                        st.warning("⚠️ Dokümanı daha dikkatli oku ve tekrar dene.")
                    
                    st.markdown("---")
                    st.markdown("### 📋 Detaylı Sonuçlar")
                    
                    # Sorular ve sonuçları göster
                    for idx, q in enumerate(questions, 1):
                        if idx in results:
                            res = results[idx]
                            correct_answer = q['answer']
                            user_answer = res['user_answer']
                            
                            if res['is_correct']:
                                # Doğru cevap - yeşil
                                st.markdown(f"✅ **Soru {idx}:** {q['question']}")
                                st.markdown(f"   🟢 **Cevabınız:** {user_answer}) {q['options'][user_answer]}")
                            else:
                                # Yanlış cevap - kırmızı ve yeşil göster
                                st.markdown(f"❌ **Soru {idx}:** {q['question']}")
                                st.markdown(f"   🔴 **Yanlış Cevap:** {user_answer}) {q['options'][user_answer]}")
                                st.markdown(f"   🟢 **Doğru Cevap:** {correct_answer}) {q['options'][correct_answer]}")
                        else:
                            st.markdown(f"⚠️ **Soru {idx}:** Cevaplayılmadı")
                        
                        st.divider()

                    # AI tabanlı analiz ve öneriler
                    try:
                        if hasattr(st.session_state, 'quiz_generator') and st.session_state.quiz_generator:
                            analysis = st.session_state.quiz_generator.analyze_results(questions, results)
                        else:
                            analysis = []
                    except Exception as e:
                        logger.error(f"Analiz oluşturulurken hata: {e}")
                        analysis = []

                    if analysis:
                        st.markdown("---")
                        st.markdown("### 📈 Analiz ve Öneriler")
                        for a in analysis:
                            # New topic-level feedback format
                            if isinstance(a, dict) and 'topic' in a:
                                topic = a.get('topic')
                                advice = a.get('advice') or a.get('note') or ''
                                confidence = a.get('confidence')
                                conf_text = f" (Güven: {confidence:.0%})" if isinstance(confidence, float) else ''
                                st.markdown(f"**Konu:** {topic} — {advice}{conf_text}")
                            elif isinstance(a, dict) and 'index' in a:
                                idx = a.get('index')
                                note = a.get('note') or a.get('advice') or ''
                                st.markdown(f"**Soru {idx}:** {note}")
                            elif isinstance(a, dict) and 'notes' in a:
                                st.markdown(f"*{a.get('notes')}*")
                            else:
                                st.markdown(f"- {a}")
                    else:
                        st.info("Analiz bulunamadı veya tüm sorular doğru. Daha fazla geri bildirim için soruları cevaplayın.")


# TAB 4: Yönetim
with tab4:
    st.subheader("📊 Veritabanı Yönetimi")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if st.session_state.document_loaded:
        st.success("✅ Doküman yüklü")
        st.info("Dokümanlar /data/chroma_db/ klasöründe saklanmaktadır.")
    else:
        st.info("ℹ️ Henüz doküman yüklenmedi")
    
    st.divider()

    st.subheader("🏷️ Etiket Yönetimi")
    if st.session_state.loaded_documents:
        for doc_name, doc_info in st.session_state.loaded_documents.items():
            current_labels = ", ".join(doc_info.get('labels', []))
            new_labels = st.text_input(
                f"{doc_name} etiketleri (virgülle)",
                value=current_labels,
                key=f"labels_{doc_name}"
            )
            # Güncelleme
            parsed_labels = [lbl.strip() for lbl in new_labels.split(',') if lbl.strip()]
            st.session_state.loaded_documents[doc_name]['labels'] = parsed_labels
        st.info("Etiket değişiklikleri anında uygulanır. Soru-cevapta etiket filtresi kullanılır.")
    else:
        st.caption("Etiket eklemek için önce doküman yükleyin.")
    
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
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 5: Özet Oluştur
with tab5:
    st.subheader("📝 Doküman Özeti Oluştur")
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    if not st.session_state.loaded_documents:
        st.warning("⚠️ Önce bir doküman yükle")
    else:
        active_docs = [name for name, info in st.session_state.loaded_documents.items() if info.get('active')]
        
        if not active_docs:
            st.warning("⚠️ En az bir doküman aktif etmen gerekiyor")
        else:
            st.info(f"💡 {len(active_docs)} aktif doküman seçildi")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                summary_type = st.selectbox(
                    "Özet Türü",
                    ["Kısa Özet", "Detaylı Özet", "Madde Başında Özet"],
                    key="summary_type"
                )
            
            with col2:
                st.write("")
            
            type_map = {
                "Kısa Özet": "general",
                "Detaylı Özet": "detailed",
                "Madde Başında Özet": "bullet"
            }
            
            if st.button("🔄 Özet Oluştur", key="generate_summary", use_container_width=True):
                try:
                    # Aktif dokümanlardan text al
                    full_text = get_active_documents_text()
                    cache_key = None
                    if full_text.strip():
                        cache_key = hashlib.md5((full_text + type_map[summary_type]).encode('utf-8')).hexdigest()
                    
                    if not full_text.strip():
                        st.error("❌ Doküman bulunamadı")
                    else:
                        if cache_key and cache_key in st.session_state.summary_cache:
                            cached = st.session_state.summary_cache[cache_key]
                            summary = cached.get("text", "")
                            st.session_state.summary_text = summary
                            st.session_state.summary_audio = cached.get("audio")
                            st.info("⚡ Önbellekten özet getirildi")
                        else:
                            with st.spinner("📝 Özet oluşturuluyor..."):
                                summary = st.session_state.summarizer.summarize(
                                    full_text, 
                                    type_map[summary_type]
                                )
                                st.session_state.summary_text = summary
                                st.session_state.summary_audio = None
                                audio_bytes = st.session_state.voice_handler.synthesize(summary)
                                if audio_bytes:
                                    st.session_state.summary_audio = audio_bytes
                                st.session_state.summary_cache[cache_key] = {
                                    "text": summary,
                                    "audio": st.session_state.summary_audio,
                                }
                        
                        st.success("✅ Özet oluşturuldu!")
                        st.markdown(f"""
                        <div style='background-color: #f0f2f6; padding: 15px; border-radius: 5px;'>
                        {summary}
                        </div>
                        """, unsafe_allow_html=True)

                        # Sesli özet oynatıcı
                        if st.session_state.summary_audio:
                            st.markdown("#### 🔊 Sesli Özet")
                            st.audio(st.session_state.summary_audio, format="audio/mp3")
                            st.caption("Oynatıcıyı kullanarak durdur/play/ileri-geri sarabilirsin.")
                        else:
                            st.info("Sesli özet oluşturmak için TTS (gTTS) gerekli; mevcut ortamda üretilemedi.")
                        
                        # İndir butonu
                        st.download_button(
                            label="📥 Özeti İndir (TXT)",
                            data=summary,
                            file_name="ozet.txt",
                            mime="text/plain",
                            key="download_summary"
                        )
                
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
                    logger.error(f"Özet hata: {e}")
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>RAgent v0.1.0 | Kişisel Bilgi Asistanı</p>
    <p style='font-size: 0.8em;'>Python + LangChain + Groq + ChromaDB + Streamlit</p>
</div>
""", unsafe_allow_html=True)
