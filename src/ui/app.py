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
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion.document_loader import DocumentLoader, TextSplitter
from src.embedding.vector_db import VectorDatabase
from src.rag.rag_system import RAGSystem

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

# Model seçimi
model = st.sidebar.selectbox(
    "Llama Model Seçin",
    [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
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
tab1, tab2, tab3 = st.tabs(["📤 Doküman Yükle", "❓ Soru Sor", "📊 Yönetim"])

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
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            submit_button = st.button("🔍 Ara", use_container_width=True)
        
        if submit_button and question:
            if not st.session_state.rag_system:
                st.error("❌ Groq API anahtarı ayarlanmamış!")
            else:
                with st.spinner("⏳ Cevap aranıyor..."):
                    try:
                        # RAG sistemini çalıştır
                        answer = st.session_state.rag_system.process_question(
                            question,
                            st.session_state.vector_db,
                            k_results=5
                        )
                        
                        # Cevabı göster
                        st.markdown("### 📝 Cevap")
                        st.success(answer if answer else "Üzgünüm, bu soruyla ilgili bilgi bulamadım.")
                        
                        # Benzer dokümanları göster
                        st.markdown("### 📚 Kaynaklar")
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

# TAB 3: Yönetim
with tab3:
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
