# Android WebView Wrapper for RAgent

RAgent web uygulamasını Android telefonda native app gibi çalıştırmak için bu yapıyı kullanın.

## Gereksinimler

- Android Studio
- Android SDK 21+
- Java Development Kit (JDK)

## Kurulum Adımları

### 1. Android Projesi Oluştur
```bash
android create project \
  --target android-21 \
  --name RAgentAndroid \
  --path ./RAgentAndroid \
  --activity RAgentActivity \
  --package com.ragent.app
```

### 2. MainActivity Düzenle

`src/main/java/com/ragent/app/MainActivity.java`:

```java
package com.ragent.app;

import android.os.Bundle;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    private WebView webView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        webView.setWebViewClient(new WebViewClient());
        
        // WebView ayarları
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        
        // Streamlit Cloud URL'ini yükle
        webView.loadUrl("https://your-app.streamlit.app");
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
```

### 3. Layout Dosyası

`src/main/res/layout/activity_main.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />
</LinearLayout>
```

### 4. AndroidManifest.xml Düzenle

İnternet izni ekle:

```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 5. Build ve Deploy

```bash
cd RAgentAndroid
./gradlew build
# Play Store'a yükle veya APK'yı doğrudan dağıt
```

## Streamlit Cloud URL

Deployment sonrasında buraya güncellenecek:
- **Web**: https://your-app.streamlit.app
- **Android Wrapper**: Yukarıdaki koda URL'i koy

## Avantajlar

✅ Tek codebase (Python/Streamlit)
✅ Web ve Android aynı anda çalışır
✅ Güncelleme = otomatik her tarafa yayılır
✅ Play Store üzerinde yayınlanabilir

