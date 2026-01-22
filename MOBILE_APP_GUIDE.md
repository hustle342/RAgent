# 📱 RAgent Mobile App - React Native Guide

## ✅ Backend Hazır!

API çalışıyor: **http://192.168.1.164:8000**

### 🔌 API Endpoints

```
GET  /                      → Health check
POST /api/upload            → Dosya yükle
GET  /api/documents         → Dökümanları listele
POST /api/question          → Soru sor
POST /api/quiz              → Quiz oluştur
POST /api/summary           → Özet çıkar
DELETE /api/documents/{id}  → Döküman sil
```

API Docs: http://192.168.1.164:8000/docs

---

## 🚀 React Native Kurulum

### 1. React Native CLI Kur

```bash
# Node.js zaten kurulu, React Native CLI kur
npm install -g react-native-cli

# Yeni proje oluştur
cd ~/Masaüstü
npx react-native init RAgentMobile
cd RAgentMobile
```

### 2. Gerekli Paketleri Yükle

```bash
# Navigation
npm install @react-navigation/native @react-navigation/native-stack
npm install react-native-screens react-native-safe-area-context

# UI Components
npm install react-native-paper react-native-vector-icons

# File Picker
npm install react-native-document-picker

# HTTP Client
npm install axios

# Animations
npm install react-native-reanimated
npm install lottie-react-native
```

### 3. API Service Dosyası

`src/services/api.js`:

\`\`\`javascript
import axios from 'axios';

const API_BASE = 'http://192.168.1.164:8000/api';

export const api = {
  // Dosya yükle
  uploadDocument: async (fileUri, fileName, labels = []) => {
    const formData = new FormData();
    formData.append('file', {
      uri: fileUri,
      type: 'application/pdf',
      name: fileName,
    });
    formData.append('labels', labels.join(','));
    
    return axios.post(\`\${API_BASE}/upload\`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  // Dökümanları getir
  getDocuments: () => axios.get(\`\${API_BASE}/documents\`),

  // Soru sor
  askQuestion: (question, documentIds = []) => 
    axios.post(\`\${API_BASE}/question\`, { question, document_ids: documentIds }),

  // Quiz oluştur
  generateQuiz: (documentIds = [], numQuestions = 5) =>
    axios.post(\`\${API_BASE}/quiz\`, { document_ids: documentIds, num_questions: numQuestions }),

  // Özet çıkar
  generateSummary: (documentIds = [], summaryType = 'genel') =>
    axios.post(\`\${API_BASE}/summary\`, { document_ids: documentIds, summary_type: summaryType }),
};
\`\`\`

---

## 🎨 UI Tasarım Önerileri

### Ana Ekranlar

1. **Splash Screen** (1-2 saniye animasyon)
   - Lottie animation
   - App logo fade-in

2. **Home Screen** (Döküman Listesi)
   - Kartlar halinde dökümanlar
   - Swipe to delete
   - FAB button (+ yeni döküman)

3. **Upload Screen**
   - Drag & drop zone
   - Progress bar
   - Label input

4. **Q&A Screen**
   - Chat UI (bubble messages)
   - Typing indicator
   - Source chips (tıklanabilir)

5. **Quiz Screen**
   - Swipeable cards
   - Progress indicator
   - Skor animasyonu

6. **Summary Screen**
   - Sekmeler (Genel/Detaylı/Maddeler)
   - Share button
   - TTS play button

### Renk Paleti

\`\`\`
Primary: #6366f1 (Indigo)
Secondary: #8b5cf6 (Purple)
Success: #10b981 (Green)
Error: #ef4444 (Red)
Background: #0f172a (Dark Blue)
Card: #1e293b (Slate)
Text: #f1f5f9 (Light)
\`\`\`

### Animasyonlar

- **Page Transitions**: Slide from right (300ms)
- **Card Entry**: Fade + Scale (200ms stagger)
- **Button Press**: Scale down 0.95
- **Loading**: Skeleton screens

---

## 📦 Proje Yapısı

\`\`\`
RAgentMobile/
├── src/
│   ├── screens/
│   │   ├── SplashScreen.js
│   │   ├── HomeScreen.js
│   │   ├── UploadScreen.js
│   │   ├── QuestionScreen.js
│   │   ├── QuizScreen.js
│   │   └── SummaryScreen.js
│   ├── components/
│   │   ├── DocumentCard.js
│   │   ├── ChatBubble.js
│   │   ├── QuizCard.js
│   │   └── LoadingSpinner.js
│   ├── services/
│   │   └── api.js
│   ├── navigation/
│   │   └── AppNavigator.js
│   └── theme/
│       └── colors.js
├── android/
├── ios/
└── package.json
\`\`\`

---

## 🎬 Sonraki Adımlar

### Şimdi Yapılacaklar:

1. **React Native Proje Oluştur**
   \`\`\`bash
   cd ~/Masaüstü
   npx react-native init RAgentMobile
   \`\`\`

2. **Paketleri Yükle** (yukarıdaki liste)

3. **Temel Navigation Kur**
   - Stack Navigator
   - Bottom Tabs

4. **İlk Ekranı Yap** (HomeScreen)
   - API'den dökümanları çek
   - Liste göster

### Test:

\`\`\`bash
# Android
npx react-native run-android

# iOS (Mac gerekir)
npx react-native run-ios
\`\`\`

---

## 🐛 Debug

API'ye erişim testi:

\`\`\`bash
# Terminal'den
curl http://192.168.1.164:8000/

# Telefondan (Chrome)
http://192.168.1.164:8000/docs
\`\`\`

---

## 📤 Play Store'a Yükleme

1. **APK Oluştur**
   \`\`\`bash
   cd android
   ./gradlew assembleRelease
   # APK: android/app/build/outputs/apk/release/app-release.apk
   \`\`\`

2. **AAB Oluştur** (Play Store için)
   \`\`\`bash
   ./gradlew bundleRelease
   # AAB: android/app/build/outputs/bundle/release/app-release.aab
   \`\`\`

3. **Keystore Oluştur** (imzalama için)
   \`\`\`bash
   keytool -genkeypair -v -storetype PKCS12 -keystore my-release-key.keystore \\
     -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
   \`\`\`

4. **Play Console'a Yükle**
   - https://play.google.com/console
   - Yeni uygulama oluştur
   - AAB dosyasını yükle
   - Metadata (açıklama, ekran görüntüleri)
   - Yayınla

---

## 🎯 Özellikler Roadmap

- [x] Backend API
- [ ] React Native temel yapı
- [ ] Döküman listesi & yükleme
- [ ] Q&A ekranı
- [ ] Quiz ekranı
- [ ] Özet ekranı
- [ ] Dark/Light mode
- [ ] Offline cache
- [ ] Push notifications
- [ ] Paylaşım özellikleri

---

**Hadi başlayalım! React Native projesini oluşturmak ister misin?**
