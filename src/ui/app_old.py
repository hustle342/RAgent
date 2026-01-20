"""
Streamlit Web Arayüzü - RAgent
"""

import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

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

# Model seçimi
model = st.sidebar.selectbox(
    "Llama Model Seçin",
    [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama-3.1-405b-reasoning"
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
        
        with st.spinner("⏳ Doküman işleniyor..."):
            # İşlem simulasyonu (gerçek uygulamada veri işlenecek)
            st.info("""
            🔄 Şu şekilde işleniyor:
            1. PDF metne dönüştürülüyor
            2. Metin parçalara bölünüyor
            3. Her parça vektöre dönüştürülüyor
            4. ChromaDB'ye kaydediliyor
            """)
        
        st.success("✅ Doküman başarıyla işlendi!")
        st.info(f"📊 İstatistikler:\n- Dosya boyutu: ~{len(uploaded_file.getvalue()) / 1024:.1f} KB")

# TAB 2: Soru Soruşturma
with tab2:
    st.subheader("Sorunuzu Sorun")
    
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
        with st.spinner("⏳ Cevap aranıyor..."):
            st.info("""
            🔄 İşlem:
            1. Sorunuz vektöre dönüştürülüyor
            2. Benzer dokümanlar aranıyor
            3. Llama 3 ile cevap oluşturuluyor
            """)
        
        # Örnek cevap
        st.markdown("### 📝 Cevap")
        st.success("""
        Belirttiğiniz soruya ilişkin olarak, dokümanın içeriğine göre:

        [Cevap burada gösterilecek]

        **Kaynaklar:**
        - Doküman parçası 1 (benzerlik: 0.92)
        - Doküman parçası 2 (benzerlik: 0.87)
        """)

# TAB 3: Yönetim
with tab3:
    st.subheader("📊 Veritabanı Yönetimi")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📄 Yüklenen Doküman", "0")
    with col2:
        st.metric("🔤 Metin Parçaları", "0")
    with col3:
        st.metric("💾 Veritabanı Boyutu", "0 MB")
    
    st.divider()
    
    st.subheader("🧹 Veri İşlemleri")
    
    if st.button("Veritabanını Temizle", help="Tüm dokümanları sil"):
        st.warning("⚠️ Bu işlem geri alınamaz!")
        if st.button("Evet, sil"):
            st.success("✅ Veritabanı temizlendi")
    
    st.divider()
    
    st.subheader("ℹ️ Sistem Bilgileri")
    st.info(f"""
    - **Seçili Model:** {model}
    - **Embedding Modeli:** sentence-transformers/all-MiniLM-L6-v2
    - **Vector DB:** ChromaDB
    - **Sürüm:** 0.1.0
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>RAgent v0.1.0 | Kişisel Bilgi Asistanı</p>
    <p style='font-size: 0.8em;'>Python + LangChain + Groq + ChromaDB + Streamlit</p>
</div>
""", unsafe_allow_html=True)
