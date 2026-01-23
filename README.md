güncel
**RAgent — Local Development & Release**

- **What:** Combined Streamlit fallback UI and React Native mobile features for RAgent project.
- **This release:** current workspace snapshot including Streamlit app (`app.py`) and RN code.

How to run locally (Streamlit):

- Create and activate your Python venv and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Run Streamlit locally (only on this machine):

```bash
streamlit run app.py --server.port 8501 --server.address 127.0.0.1
# open http://localhost:8501
```

Expose temporarily (optional):
- Use ngrok (recommended for protected access):

```bash
ngrok config add-authtoken <YOUR_AUTHTOKEN>
ngrok http 8501 --basic-auth="username:strongpassword"
```

- Or use localtunnel for a quick public URL (no auth):

```bash
npx --yes localtunnel --port 8501
```

Notes & Security:
- Do not commit ngrok authtokens or secrets. Revoke any token accidentally shared.
- LocalTunnel URLs are public while the tunnel runs; prefer ngrok with `--basic-auth` for restricted access.

Handoff / next steps for team:
- Branch: `release/v1.0.0` contains this snapshot.
- CI/CD: add GitHub Actions workflow if you want automatic deployment.
- For mobile QA: build `android/app/build/outputs/apk/debug/app-debug.apk` and install on test device.

Contact: Serdar KORKMAZ (repo owner) — update release notes in this file as needed.
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
