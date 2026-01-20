#!/bin/bash

# RAgent - Kişisel Bilgi Asistanı - Kurulum Scripti (Pop!_OS/Debian)

set -e

echo "🚀 RAgent Kurulum Başlıyor..."
echo "================================"

# Sistem paketleri
echo "📦 Sistem paketleri yükleniyor..."
sudo apt-get update
sudo apt-get install -y \
    python3.10 \
    python3.10-venv \
    python3.10-dev \
    python3-pip \
    build-essential \
    git \
    curl

# Python sanal ortamı
echo "🐍 Python sanal ortamı oluşturuluyor..."
python3.10 -m venv venv
source venv/bin/activate

# Pip güncelleme
echo "📦 pip güncelleniyor..."
pip install --upgrade pip setuptools wheel

# Gerekli paketler
echo "📚 Python paketleri yükleniyor..."
pip install -r requirements.txt

# Veri klasörü oluştur
echo "📁 Veri klasörleri oluşturuluyor..."
mkdir -p data/chroma_db
mkdir -p logs

# .env dosyası
if [ ! -f .env ]; then
    echo "📝 .env dosyası oluşturuluyor..."
    cp .env.example .env
    echo ""
    echo "⚠️  ÖNEMLI: .env dosyasını düzenle ve Groq API anahtarını ekle!"
    echo "Düzenlemek için: nano .env"
    echo ""
fi

echo ""
echo "✅ Kurulum tamamlandı!"
echo ""
echo "📋 Sonraki Adımlar:"
echo "1. Sanal ortamı aktifleştir: source venv/bin/activate"
echo "2. .env dosyasını düzenle: nano .env"
echo "3. Streamlit'i başlat: streamlit run src/ui/app.py"
echo ""
echo "📦 Docker ile çalıştırmak için: docker-compose up --build"
echo "================================"
