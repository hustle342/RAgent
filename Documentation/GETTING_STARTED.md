# 🚀 RAgent - Başlangıç Rehberi

> Kişisel Bilgi Asistanı: Dokümanlarınla konuşan AI

## 📖 İçerik Tablosu
1. [Hızlı Kurulum](#hızlı-kurulum)
2. [Sistem Gereksinimleri](#sistem-gereksinimleri)
3. [Adım Adım Kurulum](#adım-adım-kurulum)
4. [İlk Kullanım](#ilk-kullanım)
5. [Sorun Giderme](#sorun-giderme)
6. [Sonraki Adımlar](#sonraki-adımlar)

---

## 🏃 Hızlı Kurulum

**Linux (Pop!_OS / Debian):**
```bash
cd ~/Masaüstü/RAgent
chmod +x setup.sh
./setup.sh
```

**Manual:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

---

## 💻 Sistem Gereksinimleri

### İşletim Sistemi
- Linux (Pop!_OS, Debian, Ubuntu) ✅
- macOS (Terminal üzerinden)
- Windows (WSL2 önerilir)

### Minimum Donanım
- **CPU**: 2-core (4-core önerilir)
- **RAM**: 4GB (8GB önerilir embedding'ler için)
- **Disk**: 2GB (ChromaDB + modeller için)

### Yazılım Gereksinimleri
- Python 3.10+
- pip (Python paket yöneticisi)
- Git (opsiyonel, fakat önerilir)
- Docker (opsiyonel, containerized çalışma için)

---

## 🔧 Adım Adım Kurulum

### Adım 1: Repositoryi Klonla (veya indirmeyi bitir)

```bash
cd ~/Masaüstü
# Repo zaten var, bu adımı atla
cd RAgent
```

### Adım 2: Python Sanal Ortamı Oluştur

```bash
# Sanal ortamı oluştur
python3 -m venv venv

# Aktifleştir (Linux/macOS)
source venv/bin/activate

# Aktifleştir (Windows - PowerShell)
venv\Scripts\Activate.ps1
```

### Adım 3: Bağımlılıkları Yükle

```bash
# pip'i güncelle
pip install --upgrade pip

# Paketleri yükle
pip install -r requirements.txt
```

**Bu işlem 5-10 dakika sürebilir.** ☕

### Adım 4: API Anahtarları Ayarla

#### 4.1 Groq API Anahtarı

1. **https://console.groq.com** adresine git
2. Google/GitHub hesabıyla giriş yap
3. Sol menüden "API Keys" seç
4. Yeni anahtar oluştur (+ Create New API Key)
5. Anahtarı kopyala

#### 4.2 .env Dosyasını Düzenle

```bash
# Şablondan .env kopyala
cp .env.example .env

# Editörle aç
nano .env
```

Dosyaya ekle:
```env
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
```

**Ctrl+O** → **Enter** → **Ctrl+X** ile kaydet.

---

## 🎯 İlk Kullanım

### Seçenek 1: Web Arayüzü ile (Önerilir)

```bash
# Sanal ortamı aktifleştir
source venv/bin/activate

# Streamlit uygulamasını başlat
streamlit run src/ui/app.py
```

Tarayıcı otomatik açılmalı: `http://localhost:8501`

**Ne yapabilirsin?**
- 📤 PDF veya TXT dosyalarını yükle
- ❓ Doküman hakkında soru sor
- 📊 Veri tabanını yönet

### Seçenek 2: Demo Script ile

```bash
# Sanal ortamı aktifleştir
source venv/bin/activate

# Demo çalıştır (15 saniye)
python examples/demo.py
```

Output:
```
🤖 RAgent Demo - Tam İş Akışı
============================================================
📄 Adım 1: Örnek Doküman Oluşturuluyor...
✅ Örnek doküman oluşturuldu: ...
...
✅ Demo Tamamlandı!
```

### Seçenek 3: Docker ile

```bash
docker-compose up --build
```

Tarayıcı açılacak: `http://localhost:8501`

---

## 📚 İlk Proje: Makale Analizi

### Adım 1: Metin Dosyası Oluştur
```bash
# data/ klasörüne bir .txt dosyası oluştur
nano data/my_article.txt
```

Örnek içerik:
```
Yapay Zeka (AI) Nedir?

Yapay zeka, bilgisayarların insan benzeri görevleri yapabilmesi 
yeteneğidir. Makine öğrenmesi, derin öğrenme, doğal dil işleme 
gibi teknikler AI'ın temelini oluşturur.

Kullanım Alanları:
1. Sağlık (Teşhis)
2. Finans (Risk Analizi)
3. Eğitim (Kişisel Öğrenme)
...
```

### Adım 2: Streamlit'i Aç

```bash
streamlit run src/ui/app.py
```

### Adım 3: Dosyayı Yükle
- "📤 Doküman Yükle" sekmesine tıkla
- `data/my_article.txt` dosyasını seç
- Yükleme tamamlanmasını bekle

### Adım 4: Sorular Sor
- "❓ Soru Sor" sekmesine tıkla
- Örnek sorular:
  - "Yapay zeka nedir?"
  - "AI'ın kullanım alanları neler?"
  - "Makine öğrenmesi ne anlama geliyor?"

---

## 🐛 Sorun Giderme

### Problem: "GROQ_API_KEY bulunamadı"

**Çözüm 1: .env dosyasını kontrol et**
```bash
cat .env | grep GROQ_API_KEY
```

Boşsa doldur:
```bash
echo "GROQ_API_KEY=your_key_here" >> .env
```

**Çözüm 2: Ortam değişkenini doğrudan ayarla**
```bash
export GROQ_API_KEY="gsk_xxxxxxxxxxxx"
streamlit run src/ui/app.py
```

---

### Problem: "Module not found" hatası

**Sebep**: Sanal ortam aktif değil

**Çözüm**:
```bash
# Sanal ortamı kontrol et
which python
# Eğer venv klasörü yoksa:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### Problem: "Port 8501 already in use"

**Çözüm 1: Başka port kullan**
```bash
streamlit run src/ui/app.py --server.port 8502
```

**Çözüm 2: Eski işlemi sonlandır**
```bash
# Kullanılan işlemi bul
lsof -i :8501

# PID'i öldür (örn: 1234)
kill 1234
```

---

### Problem: "ModuleNotFoundError: No module named 'torch'"

**Sebep**: Ağır modeller kurulmamış (normal)

**Çözüm**: İlk embedding'ler yüklenirken indirme yapılır (5-10 dakika)

```bash
# Manuel indirme (opsiyonel)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## 🎓 Sonraki Adımlar

### 1. Kendi Dokümanlarını Yükle (15 dakika)
- ✅ Tamamlandı: Demo kullandın
- 📋 Sonraki: Kendi PDF'lerini yükle
  ```bash
  # data/ klasörüne PDF kopyala
  cp ~/Downloads/my_document.pdf data/
  # Streamlit'te yükle
  ```

### 2. Daha Güçlü Model Kullan (1 saat)
- Şu anda: `all-MiniLM-L6-v2` (hızlı, hafif)
- Daha iyi: `all-mpnet-base-v2` (daha doğru)
- Upgrade:
  ```python
  # src/embedding/embedder.py içinde değiştir:
  model_name="sentence-transformers/all-mpnet-base-v2"
  ```

### 3. Web Araması Ekle (2 saat)
- Tavily API'sini entegre et
- RAG sistemine "eğer bulunmazsa internette ara" özelliği
- `src/rag/agentic_rag.py` oluştur

### 4. Üyelik Sistemi Ekle (1-2 gün)
- Stripe ile ödeme sistemi
- Kullanıcı yönetimi
- API endpoint'leri

### 5. GitHub'a Yükle (30 dakika)
```bash
git init
git add .
git commit -m "Initial commit: RAgent v0.1.0"
git branch -M main
git remote add origin https://github.com/username/RAgent.git
git push -u origin main
```

---

## 📊 Başarılı Kurulum Kontrol Listesi

- [ ] Python 3.10+ yüklü (`python --version`)
- [ ] Sanal ortam oluşturuldu (`ls venv/`)
- [ ] Paketler yüklendi (`pip list | grep langchain`)
- [ ] .env dosyası dolduruldu (`cat .env | grep GROQ`)
- [ ] Demo çalıştırıldı (`python examples/demo.py`)
- [ ] Streamlit başlatıldı (`streamlit run src/ui/app.py`)
- [ ] PDF/TXT yüklendi (Web UI)
- [ ] Soru sorma test edildi (Web UI)

---

## 💡 İpuçları

1. **Embedding Modeli Cache'leme**
   ```bash
   # İlk download sonrasında cache'lenmesi otomatik
   # ~/.cache/huggingface/ klasörüne kaydedilir
   ```

2. **ChromaDB Veri Tabanını Görüntüle**
   ```bash
   python -c "
   from chromadb import PersistentClient
   client = PersistentClient('./data/chroma_db')
   coll = client.get_collection('documents')
   print(f'Toplam doküman: {coll.count()}')
   "
   ```

3. **Groq API Kullanımını Kontrol Et**
   - https://console.groq.com/keys adresinden kullanım istatistiklerini gör
   - Ücretsiz plan: 30 isteği/dakika

4. **Makefile Kullanarak Hızlıca Komutu Çalıştır**
   ```bash
   make run       # Streamlit başlat
   make demo      # Demo çalıştır
   make test      # Testleri çalıştır
   make docker-up # Docker başlat
   ```

---

## 📞 Yardım İste

1. **QUICKSTART.md** dosyasını oku (hızlı referans)
2. **PROJECT_SETUP.md** dosyasını oku (detaylı yapı)
3. Test dosyasını çalıştır: `python tests/test_modules.py`
4. GitHub Issues'da bir soru aç

---

## 🎉 Tebrikler!

Artık RAgent projesini çalıştıracak teknik bilgiye sahipsin. Sonraki adımlar:

1. ✅ Groq API anahtarını ekle
2. ✅ Streamlit uygulamasını aç
3. ✅ İlk dokümanını yükle
4. ✅ Soru sor ve cevap al
5. ✅ Özellikleri geliştir
6. ✅ GitHub'a yükle
7. ✅ Produksiyona al

**Happy Coding! 🚀**

---

**Sürüm**: 0.1.0 | **Son Güncelleme**: 20 Ocak 2026
