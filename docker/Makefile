.PHONY: help install test run demo docker-build docker-up docker-down clean

help:
	@echo "🤖 RAgent - Makefile Komutları"
	@echo "================================"
	@echo "make install        - Paketleri yükle (venv gerekli)"
	@echo "make test           - Testleri çalıştır"
	@echo "make demo           - Demo'yu çalıştır"
	@echo "make run            - Streamlit uygulamasını başlat"
	@echo "make docker-build   - Docker imajını oluştur"
	@echo "make docker-up      - Docker konteynerini başlat"
	@echo "make docker-down    - Docker konteynerini durdur"
	@echo "make clean          - Cache ve geçici dosyaları sil"
	@echo "make lint           - Kod kalitesini kontrol et"

install:
	pip install -r requirements.txt

test:
	python tests/test_modules.py

demo:
	python examples/demo.py

run:
	streamlit run src/ui/app.py

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d
	@echo "✅ RAgent çalışıyor: http://localhost:8501"

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache 2>/dev/null || true
	@echo "✅ Temizlik tamamlandı"

lint:
	@echo "Not: pylint/black'i yüklersen otomatik kontrol yapılabilir"
	python -m py_compile src/**/*.py tests/*.py

.DEFAULT_GOAL := help
