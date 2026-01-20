# RAgent 🤖 - Kişisel Bilgi Asistanı

Kullanıcının yüklediği PDF, YouTube linki veya web sitesi içeriğini analiz edip, sadece o kaynaklara dayanarak soruları cevaplayan bir Kişisel Bilgi Asistanı.

## 🌟 Özellikler

- **PDF İşleme**: PDF dosyalarını otomatik olarak analiz et
- **Web Scraping**: YouTube ve blog yazılarından bilgi topla
- **Vektör Tabanı**: ChromaDB ile hızlı arama
- **Llama 3 AI**: Groq API üzerinden güçlü AI modeli
- **Web Arayüzü**: Streamlit ile kullanıcı dostu interface
- **Agentic Workflow**: İhtiyaçta internet araması yapabilen akıllı sistem
- **Docker Support**: Konteynerized çalışma ortamı

## 🛠 Teknoloji Stack

- **Python 3.10+**
- **LangChain**: AI workflow yönetimi
- **Groq API**: Llama 3 modeli (hızlı yanıt)
- **ChromaDB**: Vector database
- **Streamlit**: Web UI
- **HuggingFace Embeddings**: Metin vektörleştirme

## 📋 Kurulum

### Linux (Pop!_OS / Debian)

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

# .env dosyasını düzenle
cp .env.example .env
# Groq API anahtarını ekle
```

## 🚀 Kullanım

```bash
# Sanal ortamı aktifleştir
source venv/bin/activate

# Streamlit uygulamasını başlat
streamlit run src/ui/app.py
```

## 📁 Proje Yapısı

```
RAgent/
├── src/
│   ├── ingestion/      # PDF ve web içeriği işleme
│   ├── embedding/      # Vektörleştirme
│   ├── rag/           # RAG sistemi
│   └── ui/            # Streamlit arayüzü
├── data/              # Depolanan veritabanı
├── config/            # Konfigürasyon dosyaları
├── requirements.txt   # Python paketleri
├── setup.sh          # Linux kurulum scripti
└── README.md         # Bu dosya
```

## 🔑 API Anahtarları

Şunları elde etmen gerekli:

1. **Groq API**: https://console.groq.com
2. **Wikipedia API** (Ücretsiz - Otomatik olarak kullanılıyor)

## 📚 Adım Adım Geliştirme

- [ ] 1. Veri İşleme (PDF, Web)
- [ ] 2. Vektörleştirme (Embeddings)
- [ ] 3. ChromaDB İntegrasyonu
- [ ] 4. RAG Sistemi
- [ ] 5. Streamlit UI
- [ ] 6. Agentic Workflow
- [ ] 7. Docker Konfigürasyonu

## 📄 Lisans

MIT

## 👨‍💻 Geliştirici

Serdar Pop

---

**Not**: Bu proje aktif olarak geliştirilmektedir.
