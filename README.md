# InvestSim

Sanal yatırım simülatörü ve portföy analiz aracı. Gerçek piyasa verileriyle risk almadan yatırım pratiği yapın!

## Özellikler

- **Sanal Yatırım Simülatörü** — Gerçek hisse senedi, kripto ve döviz fiyatlarıyla sanal al/sat yapın
- **Portföy Takibi** — Anlık portföy değeri, kar/zarar analizi ve işlem geçmişi
- **Senaryo Analizi** — "Eğer şu tarihte yatırım yapsaydım ne olurdu?" simülasyonları
- **Çeşitlendirme Analizi** — Portföyünüzün piyasa dağılımını görün

## Teknolojiler

- **Backend:** Python + FastAPI
- **Frontend:** HTML + CSS + Vanilla JavaScript
- **Veritabanı:** SQLite
- **API'ler:** Yahoo Finance (hisse/forex), CoinGecko (kripto)

## Kurulum

```bash
# 1. Repoyu klonlayın
git clone https://github.com/kullaniciadin/InvestSim.git
cd InvestSim

# 2. Sanal ortam oluşturun
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Uygulamayı başlatın
python run.py
```

## Kullanım

Tarayıcınızda `http://localhost:8000` adresine gidin.

### Sayfalar

| Sayfa | Açıklama |
|---|---|
| **Dashboard** | Bakiye, portföy değeri, hızlı al/sat ve mevcut pozisyonlar |
| **Piyasa** | Canlı fiyatlar (AAPL, TSLA, Bitcoin, Ethereum, EUR/USD, GBP/USD) |
| **Portföy** | Detaylı pozisyonlar ve tüm işlem geçmişi |
| **Analiz** | Performans metrikleri, çeşitlendirme raporu ve senaryo analizi |

### Başlangıç

Sanal bakiyeniz **$100,000 USD** olarak başlar. Piyasa sayfasından bir varlık seçip, dashboard'dan alım yaparak başlayabilirsiniz.

## Testler

```bash
pytest tests/ -v
```

## Mimari

```
InvestSim/
├── backend/          # FastAPI backend
│   ├── routers/      # API endpoint'leri
│   ├── services/     # Fiyat çekici ve cache
│   ├── models/       # Pydantic şemaları
│   └── database.py   # SQLite bağlantısı
├── frontend/         # Statik web arayüzü
│   ├── js/           # JavaScript modülleri
│   └── css/          # Stil dosyaları
└── tests/            # Birim testleri
```

## Gelecek Özellikler

- [ ] Çoklu kullanıcı desteği
- [ ] Gerçek zamanlı WebSocket fiyat akışı
- [ ] Daha fazla piyasa (tahvil, emtia)
- [ ] Gelişmiş grafikler ve teknik analiz
- [ ] Mobil uyumlu responsive tasarım

## Lisans

MIT
