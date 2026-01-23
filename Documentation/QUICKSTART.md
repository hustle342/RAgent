# 🚀 RAgent - Hızlı Başlangıç Rehberi

## 1️⃣ Kurulum (5 dakika)

### Linux (Pop!_OS / Debian) - Otomatik
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Kurulum
```bash
# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate

# Paketleri yükle
pip install -r requirements.txt
```

## 2️⃣ API Anahtarı Ayarla

### Groq API Anahtarı Elde Et
1. https://console.groq.com adresine git
2. Ücretsiz hesap oluştur
3. API anahtarı kopyala

### .env Dosyasını Düzenle
```bash
cp .env.example .env
# Editörle aç ve GROQ_API_KEY=your_key_here kısmını doldur
nano .env
```

## 3️⃣ Uygulamayı Başlat

### Streamlit ile (Web UI)
```bash
source venv/bin/activate
streamlit run src/ui/app.py
```

Tarayıcında açılır: `http://localhost:8501`

### Docker ile
```bash
docker-compose up --build
```

## 4️⃣ İlk Kullanım

### Demo'yu Çalıştır
```bash
source venv/bin/activate
python examples/demo.py
```

### Kendi Dokümanını Yükle
1. Streamlit uygulamasını aç
2. "📤 Doküman Yükle" sekmesine git
3. PDF veya TXT dosyasını seç
4. "❓ Soru Sor" sekmesine git ve sorunuzu yazın

## 📚 Dosya Yapısı

```
RAgent/
├── src/
│   ├── ingestion/          # PDF/Web işleme
│   ├── embedding/          # Embedding + Vector DB
│   ├── rag/               # RAG sistemi
│   └── ui/                # Streamlit arayüzü
├── examples/              # Demo scripti
├── data/                  # Yüklenen veriler
├── config/                # Konfigürasyon
├── setup.sh               # Linux kurulum scripti
├── docker-compose.yml     # Docker konfigürasyonu
└── requirements.txt       # Python paketleri
```

## 🔧 Sorun Giderme

### "GROQ_API_KEY bulunamadı" hatası
→ `.env` dosyasında `GROQ_API_KEY` satırını kontrol et

### "Module not found" hatası
→ Sanal ortamın aktif olduğundan emin ol: `source venv/bin/activate`

### Port 8501 zaten kullanılıyor
→ Farklı bir port kullan: `streamlit run src/ui/app.py --server.port 8502`

## 📖 Öğrenme Yolu

1. **Temel Konsept** (1 saat)
   - RAG nedir?
   - Embedding'ler nasıl çalışır?
   - Vector Database'in rolü

2. **Kodu Özelleştir** (2-3 saat)
   - Kendi modellerin ekle
   - Farklı Llama versiyonlarını dene
   - Web scraping'i öğren

3. **Ürünleştir** (1-2 gün)
   - Stripe entegrasyonu ekle
   - Multi-user desteği
   - GitHub'a yükle

## 🌟 Bir Adım İleri

### Agentic Workflow Ekle
İhtiyaçta internet araması yapan AI:
```python
# src/rag/agentic_rag.py dosyasını oluştur
from langchain.agents import Tool
from langchain_community.tools.tavily_search import TavilySearchResults
```

### Kendi Embedding Modeli Kulllan
```python
# Daha büyük model: 
# "all-mpnet-base-v2" (more powerful)
# "mixedbread-ai/mxbai-embed-large-v1" (latest)
```

### Veritabanı Analizi
```bash
# ChromaDB veritabanını görüntüle
python -c "
from chromadb import PersistentClient
client = PersistentClient('./data/chroma_db')
coll = client.get_collection('documents')
print(f'Toplam doküman: {coll.count()}')
"
```

## 📱 Sonraki Proje Fikirleri

- **Çoklu Dil Desteği**: Türkçe, İngilizce, Arapça
- **Video Analizi**: YouTube videolarını otomatik olarak transkripte et
- **Batch İşleme**: Binlerce PDF'yi toplu işle
- **API Sunucusu**: FastAPI ile kendi API'nı yayınla
- **Mobile Uygulaması**: React Native ile mobil versiyon

---

**Sorular mı var?** → GitHub Issues'da soru sor!
