# Streamlit Cloud Deployment

Bu rehber, RAgent'i Streamlit Cloud'da deploy etmek için adım adım talimatları içerir.

## Ön Koşullar

- GitHub hesabı
- Streamlit Cloud hesabı (https://streamlit.io)
- Groq API anahtarı

## Deployment Adımları

### 1. GitHub'a Push Et

```bash
cd ~/Masaüstü/RAgent
git remote add origin https://github.com/YOUR_USERNAME/RAgent.git
git branch -M main
git push -u origin main
```

### 2. Streamlit Cloud'da Deploy Et

1. https://share.streamlit.io adresine git
2. "New app" butonuna tıkla
3. GitHub repository'i seç: `YOUR_USERNAME/RAgent`
4. Main file path: `app.py`
5. "Deploy" butonuna tıkla

### 3. Secrets Ekle

Deployment sonrasında:
1. App ayarlarına git (üç çizgi menü)
2. "Secrets" seçeneğine tıkla
3. `.streamlit/secrets.toml` dosyasını edit et:

```toml
GROQ_API_KEY = "gsk_your_actual_key_here"
```

### 4. Android Wrapper'ı Kurulum

[ANDROID_SETUP.md](./ANDROID_SETUP.md) dosyasını okuyun.

## Deployment Sonrası URL

Streamlit Cloud size bir URL verecek, örnek:
```
https://ragent.streamlit.app
```

Bu URL'yi:
- ✅ Mobil tarayıcıda kullan
- ✅ Android WebView wrapper'ına koy
- ✅ Müşterilerinize ver

## Temel Unsurlar

| Bileşen | Konum |
|---------|--------|
| Web Uygulaması | Streamlit Cloud |
| Backend | Streamlit (Python) |
| Database | ChromaDB (local) |
| LLM | Groq API |
| Web Search | Wikipedia + DuckDuckGo |

## Sorun Giderme

**Hata: `ModuleNotFoundError`**
- `requirements.txt` dosyasının güncel olduğundan emin ol
- GitHub'a push et, Streamlit yeniden deploy edecek

**Hata: `GROQ_API_KEY not found`**
- Secrets'i kontrol et
- `.streamlit/secrets.toml` dosyasını doğru ayarla

**Yavaş Yükleme**
- Embeddings cached olduğundan ilk seferde yavaş olur
- Sonraki istekler hızlı olacak

## Güncellemeler

Kod güncellemesi yapmak için:
```bash
git add -A
git commit -m "Update"
git push origin main
```
Streamlit otomatik deploy edecek!

