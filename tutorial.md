# InvestSim — Sıfırdan Tam Tur

> Bu doküman, **bu klasördeki** InvestSim projesinin **her dosyasını**, kullanılan **dillerin syntax'ını** ve **dosyalar arası bağlamı** sıfırdan başlayan biri için anlatır. Sonunda hem projeyi tamamen anlamış, hem de yeni özellik eklemek istediğinde nereye dokunacağını bilmiş olursun.

---

## İçindekiler

0. [Önsöz ve Nasıl Okunmalı](#0-önsöz-ve-nasıl-okunmalı)
1. [Projeye 30 Saniyelik Bakış](#1-projeye-30-saniyelik-bakış)
2. [Kullanılan Teknolojiler — "Bunlar Ne, Niye Var?"](#2-kullanılan-teknolojiler--bunlar-ne-niye-var)
3. [Yüksek-Düzey Dizin Haritası](#3-yüksek-düzey-dizin-haritası)
4. [Konfigürasyon Dosyaları](#4-konfigürasyon-dosyaları)
5. [Uygulama Açılışı (`run.py` → `backend/main.py`)](#5-uygulama-açılışı)
6. [Veritabanı Katmanı](#6-veritabanı-katmanı)
7. [Pydantic Şemalar](#7-pydantic-şemalar)
8. [Konfigürasyon & Ortam](#8-konfigürasyon--ortam)
9. [Servis Katmanı — Fiyat Çekme](#9-servis-katmanı--fiyat-çekme)
10. [Servis Katmanı — Cache](#10-servis-katmanı--cache)
11. [Routerlar — Market](#11-routerlar--market)
12. [Routerlar — Emirler](#12-routerlar--emirler)
13. [Routerlar — Portföy](#13-routerlar--portföy)
14. [Routerlar — Analiz](#14-routerlar--analiz)
15. [Frontend Mimarisi](#15-frontend-mimarisi)
16. [Frontend Sayfaları](#16-frontend-sayfaları)
17. [Test Kapsamı](#17-test-kapsamı)
18. [Tipik Geliştirici Akışları (Mini Tarifler)](#18-tipik-geliştirici-akışları)
19. [Hızlı Syntax Kartı](#19-hızlı-syntax-kartı)
20. [Sözlük ve Kısaltmalar](#20-sözlük-ve-kısaltmalar)
21. [İleri Adımlar / Önerilen Egzersizler](#21-ileri-adımlar--önerilen-egzersizler)

---

## 0. Önsöz ve Nasıl Okunmalı

### Hedef kitle
Bu doküman, **Python temellerine aşina** ama FastAPI, Pydantic, SQLite, pytest veya modern JavaScript tecrübesi olmayan biri için yazılmıştır. Sıkça karşılaşılan syntax'lar her bölümde tekrar tekrar açıklanır; bu yüzden korkmadan baştan okuyabilirsin.

### Ön gereksinimler
- **Python 3.11+** (`python --version` ile kontrol et)
- **pip** (Python paket yöneticisi)
- Modern bir tarayıcı (Chrome, Edge, Firefox)
- Bir terminal (zsh, bash, PowerShell hepsi olur)

### Hızlı kurulum komutları

```bash
cd InvestSim
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py               # http://localhost:8000
```

Kaynak: `InvestSim/requirements.txt`, `InvestSim/run.py:1-4`.

Testleri çalıştırmak için:

```bash
pytest tests/ -v
```

### Sıfırdan başlıyorum, nasıl okumalıyım?
Tutorial **sıralı okunmak için** tasarlandı, ama acelen varsa şu rota en hızlı kavramaya yarar:

1. Bölüm 1 → projenin ne olduğunu anla.
2. Bölüm 2 → kullanılan teknolojileri öğren.
3. Bölüm 4 → konfigürasyon dosyalarını gör.
4. Bölüm 5 → uygulama hangi sırayla başlıyor anla.
5. Bölüm 6 → veritabanı şemasını gör (her şey buna dayanıyor).
6. Bölüm 11-14 → router'ları ve endpoint'leri öğren.
7. Bölüm 15-16 → frontend'in backend'e nasıl bağlandığını incele.
8. Bölüm 18 → "Yeni özellik eklemek istesem ne yapardım?" tariflerini oku.

Geri kalan bölümleri sırayla ya da ihtiyaç anında ziyaret edebilirsin.

### Bu projedeki dil tercihi
Uygulama arayüzü **Türkçe**. Kod yorumları çoğunlukla Türkçe, ama değişken isimleri İngilizce. API yanıtları ve UI metinleri Türkçe yer alır.

> **Not:** Kod örneklerini okurken yorum satırları `#` ile başlar (Python) veya `//` ile başlar (JavaScript). Çoklu satır yorum Python'da `""" ... """`, JavaScript'te `/* ... */` ile yazılır.

---

## 1. Projeye 30 Saniyelik Bakış

**InvestSim**, kullanıcıya sanal bir başlangıç bakiyesi (100.000 USD) veren, gerçek piyasa verileriyle sanal al/sat yapabileceği, portföyünü takip edebileceği ve "ya öyle yapsaydım" senaryolarını analiz edebileceği web tabanlı bir sanal yatırım simülatörüdür.

Önemli özellikler:

- **Sanal Yatırım Simülatörü:** Hisse senedi, kripto para ve döviz için sanal alım/satım.
- **Portföy Takibi:** Mevcut pozisyonlar, maliyet ortalaması, kar/zarar (realized & unrealized).
- **Piyasa Ekranı:** Canlı fiyatlar (Yahoo Finance, CoinGecko).
- **Senaryo Analizi:** "Eğer X tarihinde Y hissesine Z tutar yatırsaydım, bugün ne olurdu?"
- **Çeşitlendirme Analizi:** Portföyün varlık türüne göre dağılımı.
- **Cache:** API çağrılarını önbelleğe alarak limit aşımını önleme.

### Üst-düzey veri akışı

```
                +-------------------+
                |   Kullanıcı       |
                +---------+---------+
                          | tıklar, form doldurur
                          v
+-------------------+     |     +-------------------+
|   HTML/CSS/JS     | <---+---> |   Tarayıcı        |
|   (frontend/)     |           |   (Vanilla JS)    |
+---------+---------+           +---------+---------+
          | fetch()
          v
+-------------------+
|   FastAPI         |
|   (backend/main)  |
+---------+---------+
          |
    +-----+-----+
    |           |
    v           v
+--------+  +--------+
| SQLite |  | Harici |
| (local)|  | API'ler|
+--------+  +--------+
    |           |
    |     Yahoo Finance
    |     CoinGecko
    v
+--------+
| Cache  |
| (mem)  |
+--------+
```

Akış şöyle işler:
1. Kullanıcı tarayıcıda bir sayfaya gider (örn. `index.html`).
2. JavaScript `fetch()` ile FastAPI backend'e istek atar.
3. FastAPI router'ı isteği alır; veritabanından veya harici API'den veri çeker.
4. Fiyat verisi önce cache'e bakılır; yoksa harici API çağrılır ve cache'e yazılır.
5. Sonuç JSON olarak frontend'e döner, JavaScript DOM'u günceller.

**İlişkili dosyalar:** `run.py`, `backend/main.py`, `frontend/index.html`, `frontend/js/api.js`.

---

## 2. Kullanılan Teknolojiler — "Bunlar Ne, Niye Var?"

Bu bölümün amacı her teknolojiyi tek başına işine yaradığı kadar tanıtmak. Detaylı kullanımları sonraki bölümlerde.

### 2.1. Python 3.11+ ve Tip İpuçları (Type Hints)

Python tip ipuçları, değişken ve fonksiyonların beklenen türlerini belirtir. **Zorunlu değildir** (Python hâlâ dinamik tipli), ama IDE otomatik tamamlama ve hata yakalama sağlar.

```python
def topla(x: int, y: int) -> int:
    return x + y

isim: str = "InvestSim"
fiyat: float | None = None   # "float ya da None"
```

Sık karşılaşacağın syntax'lar:

| Syntax | Anlam | Örnek |
|---|---|---|
| `-> int` | Dönüş tipi | `def f() -> int:` |
| `float \| None` | Union (biri ya da diğeri) | `price: float \| None` |
| `list[dict]` | Generic tip | `def foo() -> list[dict]:` |
| `Literal["a","b"]` | Sadece bu stringler | `asset_type: Literal["stock","crypto"]` |
| `:=` | Walrus (atama + kullanma) | `if (n := len(x)) > 5:` |

### 2.2. FastAPI

**FastAPI**, Python'da modern, hızlı (async destekli) web API'leri yazmak için kullanılan bir framework'tür. Otomatik olarak:
- **OpenAPI** şema üretir (http://localhost:8000/docs)
- **Request/response validation** yapar (Pydantic üzerinden)
- **Path/query parametreleri**ni tip güvenli şekilde çözer

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"Merhaba {name}"}
```

### 2.3. Uvicorn

**Uvicorn**, Python'da **ASGI** sunucusudur. FastAPI uygulamalarını çalıştırmak için kullanılır. `uvicorn[standard]` ekstra bağımlılıkları (httptools, uvloop) içerir, daha hızlıdır.

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- `backend.main:app` → `backend/main.py` içindeki `app` nesnesini bul.
- `--reload` → kod değişince sunucuyu otomatik yeniden başlat (geliştirme modu).

### 2.4. Pydantic

**Pydantic**, Python veri sınıfları için **runtime validation** (çalışma zamanı doğrulama) sağlar. FastAPI request body'leri Pydantic modelleriyle otomatik doğrular.

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str
    age: int = Field(gt=0)   # 0'dan büyük olmalı

u = User(name="Ali", age=25)   # OK
u = User(name="Ali", age=-1)   # ValidationError!
```

### 2.5. SQLite

**SQLite**, sunucusuz, dosya tabanlı bir SQL veritabanıdır. Kurulum gerektirmez, tek bir `.db` dosyası olarak çalışır. Python'da `sqlite3` modülü yerleşiktir.

```python
import sqlite3
conn = sqlite3.connect("investsim.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
```

### 2.6. Requests

**Requests**, Python'da HTTP istekleri atmak için en popüler kütüphanedir. Harici API'lere (Yahoo Finance, CoinGecko) istek atmak için kullanılır.

```python
import requests
resp = requests.get("https://api.example.com/data", timeout=10)
resp.raise_for_status()   # 4xx/5xx varsa exception atar
data = resp.json()         # JSON yanıtı Python dict'e çevirir
```

### 2.7. Vanilla JS (HTML5 + Fetch API)

Bu projede frontend framework (React, Vue vb.) **kullanılmaz**. Tarayıcının yerleşik **Fetch API**'si kullanılır:

```javascript
const resp = await fetch('/market/assets');
const data = await resp.json();
```

Vanilla JS'de DOM elemanları doğrudan manipüle edilir:

```javascript
const el = document.getElementById('balance');
el.textContent = '$' + value.toFixed(2);
```

### 2.8. pytest

**pytest**, Python ekosisteminin en yaygın test framework'üdür. `assert` ifadeleriyle çalışır, zengin hata raporları üretir.

```python
def test_toplam():
    assert topla(2, 3) == 5
```

- `@pytest.fixture` → testler arası paylaşılan kaynak (örn. test veritabanı).
- `pytest -v` → ayrıntılı çıktı.

### 2.9. httpx

**httpx**, Requests'e alternatif modern bir HTTP kütüphanesidir. Async desteği vardır. Bu projede test bağımlılığı olarak `requirements.txt`'ye eklenmiştir.

**İlişkili dosyalar:** `requirements.txt`.

---

## 3. Yüksek-Düzey Dizin Haritası

```
InvestSim/
├── .venv/                              # Python sanal ortam (gitignore)
├── .gitignore
├── requirements.txt                    # Python bağımlılıkları
├── run.py                              # Uvicorn başlatıcı
├── backend/
│   ├── __init__.py
│   ├── main.py                         # FastAPI app, CORS, router mount
│   ├── config.py                       # Sabitler, ortam değişkenleri
│   ├── database.py                     # SQLite bağlantı, şema, CRUD helper
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                  # Pydantic request/response modelleri
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── market.py                   # Varlık listesi, fiyat sorgusu
│   │   ├── orders.py                   # Al/sat emirleri
│   │   ├── portfolio.py                # Portföy, işlem geçmişi, bakiye
│   │   └── analytics.py                # Performans, senaryo, çeşitlendirme
│   └── services/
│       ├── __init__.py
│       ├── price_fetcher.py            # Yahoo Finance, CoinGecko entegrasyonu
│       └── cache.py                    # Bellek içi cache (TTL)
├── frontend/
│   ├── index.html                      # Dashboard (ana sayfa)
│   ├── market.html                     # Piyasa ekranı
│   ├── portfolio.html                  # Portföy detayları
│   ├── analytics.html                  # Analiz ve senaryolar
│   ├── css/
│   │   └── styles.css                  # Global stil (koyu tema)
│   └── js/
│       ├── api.js                      # Backend API client (fetch wrapper)
│       ├── dashboard.js                # Dashboard sayfa mantığı
│       ├── market.js                   # Piyasa sayfa mantığı
│       ├── portfolio.js                # Portföy sayfa mantığı
│       └── analytics.js                # Analiz sayfa mantığı
├── tests/
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixture'ları + DB oluşturma testi
│   ├── test_analytics.py               # Performans ve senaryo testleri
│   ├── test_cache.py                   # Cache TTL testleri
│   ├── test_orders.py                  # Al/sat mantığı testleri
│   ├── test_portfolio.py               # Portföy okuma testleri
│   └── test_price_fetcher.py           # Gerçek API entegrasyon testleri
└── docs/
    └── superpowers/
        ├── plans/
        │   └── 2026-05-31-investsim-implementation.md   # Implementasyon planı
        └── specs/
            └── 2026-05-31-investsim-design.md           # Tasarım dokümanı
```

> **Not:** `.venv/`, `__pycache__/`, `*.db` dosyaları **elle düzenlenmez** ve git'e atılmaz (`.gitignore` içindedir).

**İlişkili dosyalar:** Tüm proje.

---

## 4. Konfigürasyon Dosyaları

### 4.1. `requirements.txt`

```txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
requests==2.32.0
pytest==8.3.0
httpx==0.27.0
```

Kaynak: `InvestSim/requirements.txt:1-6`.

- `fastapi` → Web framework.
- `uvicorn[standard]` → ASGI sunucusu (`[standard]` = hızlı C bağımlılıkları).
- `pydantic` → Veri doğrulama ve serileştirme.
- `requests` → Harici HTTP API çağrıları.
- `pytest` → Test framework'ü.
- `httpx` → Modern HTTP client (testlerde veya async kullanım için).

> **Not:** `==` sabit sürüm demektir. Bu, farklı ortamlarda aynı davranışı garanti eder.

### 4.2. `run.py`

```python
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
```

Kaynak: `InvestSim/run.py:1-4`.

Açıklama:
- `if __name__ == "__main__":` → Dosya doğrudan çalıştırıldığında (`python run.py`) bu blok çalışır; import edildiğinde çalışmaz.
- `uvicorn.run("backend.main:app", ...)` → `backend/main.py` içindeki `app` nesnesini bulur ve sunar.
- `host="0.0.0.0"` → Tüm ağ arayüzlerinden erişilebilir (sadece localhost değil).
- `port=8000` → HTTP portu.
- `reload=True` → Kod değişince sunucuyu otomatik yeniden başlatır (geliştirme modu; production'da kapatılır).

**İlişkili dosyalar:** `requirements.txt`, `backend/main.py`.

---

## 5. Uygulama Açılışı

### 5.1. `run.py` → `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.database import init_db
from backend.routers import market, orders, portfolio, analytics

app = FastAPI(title="InvestSim API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(market.router)
app.include_router(orders.router)
app.include_router(portfolio.router)
app.include_router(analytics.router)

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
```

Kaynak: `InvestSim/backend/main.py:1-26`.

Açıklama, satır satır:

1. **`FastAPI(title="InvestSim API")`** → Uygulama nesnesi oluşturulur. `title` OpenAPI docs'ta görünür.
2. **`StaticFiles`** → `frontend/` klasöründeki HTML/CSS/JS dosyalarını statik olarak servis eder.
3. **`CORSMiddleware`** → **Cross-Origin Resource Sharing**. Tarayıcı güvenliği nedeniyle farklı origin'den (örn. `localhost:8000` vs `localhost:3000`) gelen istekleri engeller. Geliştirme için `"*"` (herkes) izin verilir. Production'da daraltılmalıdır.
4. **`@app.on_event("startup")`** → Uygulama başlarken **bir kere** çalışan fonksiyon. Burada `init_db()` çağrılarak SQLite tabloları oluşturulur ve varsayılan kullanıcı eklenir.
5. **`app.include_router(...)`** → Her router'ı FastAPI uygulamasına bağlar. Bu sayede `/market/*`, `/orders/*`, `/portfolio/*`, `/analytics/*` endpoint'leri aktif olur.
6. **`app.mount("/", ...)`** → Kök URL (`/`) ve altındaki tüm istekleri `frontend/` klasöründeki dosyalara yönlendirir. `html=True` → dizin yerine `index.html` servis eder.

### Endpoint ağacı (mount sonrası)

```
/
├── /                           → frontend/index.html (StaticFiles)
├── /market/assets              → market.list_assets
├── /market/price/{symbol}      → market.get_price
├── /orders/buy                 → orders.buy
├── /orders/sell                → orders.sell
├── /portfolio/                 → portfolio.read_portfolio
├── /portfolio/history          → portfolio.read_history
├── /portfolio/balance          → portfolio.read_balance
├── /analytics/performance      → analytics.read_performance
├── /analytics/scenario         → analytics.run_scenario
├── /analytics/diversification  → analytics.read_diversification
└── /docs                       → FastAPI otomatik Swagger UI
```

> **Not:** `http://localhost:8000/docs` adresine giderek tüm endpoint'leri ve şemaları interaktif olarak deneyebilirsin.

**İlişkili dosyalar:** `backend/main.py`, `backend/database.py`, tüm `backend/routers/*.py`.

---

## 6. Veritabanı Katmanı

### 6.1. `backend/database.py`

```python
import sqlite3
from contextlib import contextmanager
from backend.config import DATABASE_URL, DEFAULT_VIRTUAL_BALANCE, DEFAULT_CURRENCY

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    virtual_balance REAL NOT NULL,
    currency TEXT NOT NULL DEFAULT 'USD',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    asset_symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL CHECK(asset_type IN ('stock', 'crypto', 'forex')),
    transaction_type TEXT NOT NULL CHECK(transaction_type IN ('buy', 'sell')),
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    total_amount REAL NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    asset_symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    total_quantity REAL NOT NULL DEFAULT 0,
    avg_cost_basis REAL NOT NULL DEFAULT 0,
    UNIQUE(user_id, asset_symbol),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS price_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_symbol TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    asset_symbol TEXT NOT NULL,
    asset_type TEXT NOT NULL,
    hypothetical_date TEXT NOT NULL,
    hypothetical_amount REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""

@contextmanager
def get_db(db_path=None):
    path = db_path or DATABASE_URL
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db(db_path=None):
    with get_db(db_path) as conn:
        conn.executescript(SCHEMA)
        conn.commit()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO users (id, username, virtual_balance, currency) VALUES (1, 'default', ?, ?)",
            (DEFAULT_VIRTUAL_BALANCE, DEFAULT_CURRENCY)
        )
        conn.commit()
```

Kaynak: `InvestSim/backend/database.py:1-79`.

#### Şema açıklaması

| Tablo | Amaç | Önemli alanlar |
|---|---|---|
| `users` | Tek kullanıcı (şimdilik). Bakiye ve para birimi tutar. | `virtual_balance`, `currency` |
| `transactions` | Tüm al/sat işlemlerinin kaydı. | `asset_symbol`, `transaction_type`, `quantity`, `price`, `total_amount` |
| `portfolios` | Anlık portföy durumu. Her varlık için toplam miktar ve ortalama maliyet. | `total_quantity`, `avg_cost_basis` |
| `price_cache` | API'den çekilen fiyatların kalıcı önbelleği (şu an kullanılmıyor, ileride offline mod için). | `asset_symbol`, `price`, `fetched_at` |
| `scenarios` | Kaydedilmiş senaryolar (şu an DB'ye yazılmıyor, sadece şema hazır). | `hypothetical_date`, `hypothetical_amount` |

#### `CHECK` kısıtlamaları

```sql
asset_type TEXT NOT NULL CHECK(asset_type IN ('stock', 'crypto', 'forex'))
```

Bu, veritabanı seviyesinde veri bütünlüğü sağlar. Sadece bu üç değer kabul edilir; başka bir şey insert edilmeye çalışılırsa SQLite hata verir.

#### `@contextmanager` ve `get_db()`

```python
@contextmanager
def get_db(db_path=None):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
```

- `@contextmanager` → Fonksiyonu **context manager** yapar; `with` bloğuyla kullanılır.
- `conn.row_factory = sqlite3.Row` → Sonuçları dict benzeri `Row` objesi olarak döndürür; `row["column_name"]` şeklinde erişim sağlar.
- `yield conn` → `with` bloğuna bağlantıyı verir.
- `finally: conn.close()` → Blok bitince **her zaman** kapatır (hata da olsa).

Kullanımı:

```python
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
```

#### `init_db()`

- `conn.executescript(SCHEMA)` → Çoklu `CREATE TABLE` ifadelerini tek seferde çalıştırır.
- `INSERT OR IGNORE` → Eğer `id=1` kullanıcısı zaten varsa tekrar eklemez.
- Varsayılan kullanıcı: `username='default'`, `virtual_balance=100000.0`, `currency='USD'`.

**İlişkili dosyalar:** `backend/config.py`, `tests/conftest.py`, tüm router dosyaları.

---

## 7. Pydantic Şemalar

### 7.1. `backend/models/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime


class Asset(BaseModel):
    symbol: str
    name: str
    asset_type: Literal["stock", "crypto", "forex"]
    price: Optional[float] = None
    change_percent: Optional[float] = None


class OrderRequest(BaseModel):
    asset_symbol: str
    asset_type: Literal["stock", "crypto", "forex"]
    quantity: float = Field(gt=0)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    asset_symbol: str
    asset_type: str
    transaction_type: Literal["buy", "sell"]
    quantity: float
    price: float
    total_amount: float
    timestamp: datetime


class PortfolioItem(BaseModel):
    asset_symbol: str
    asset_type: str
    total_quantity: float
    avg_cost_basis: float
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None


class PerformanceMetrics(BaseModel):
    total_invested: float
    current_value: float
    total_return: float
    total_return_percent: float


class ScenarioRequest(BaseModel):
    name: str
    asset_symbol: str
    asset_type: Literal["stock", "crypto", "forex"]
    hypothetical_date: str  # ISO format YYYY-MM-DD
    hypothetical_amount: float = Field(gt=0)


class ScenarioResult(BaseModel):
    scenario_id: int
    name: str
    asset_symbol: str
    hypothetical_date: str
    hypothetical_amount: float
    current_price: Optional[float] = None
    hypothetical_value: Optional[float] = None
    gain_loss: Optional[float] = None
    gain_loss_percent: Optional[float] = None
```

Kaynak: `InvestSim/backend/models/schemas.py:1-65`.

Açıklama:

- **`BaseModel`** → Pydantic'in temel sınıfı. Bu sınıftan türetilen her model otomatik validation kazanır.
- **`Literal["stock", "crypto", "forex"]`** → Sadece bu üç string değerinden biri kabul edilir. Başka bir değer gelirse validation hatası.
- **`Optional[float] = None`** → Alan opsiyoneldir; verilmezse `None` olur.
- **`Field(gt=0)`** → `gt` = greater than. `quantity` ve `hypothetical_amount` 0'dan büyük olmalıdır.
- **`timestamp: datetime`** → ISO 8601 formatındaki string otomatik `datetime` objesine çevrilir.

Modellerin kullanım yerleri:

| Model | Kullanıldığı Yer | Amaç |
|---|---|---|
| `Asset` | `market.py` (döndürülen liste) | Varlık tanımı |
| `OrderRequest` | `orders.py` (request body) | Al/sat isteği doğrulama |
| `OrderResponse` | `orders.py` (response_model) | Al/sat sonucu döndürme |
| `PortfolioItem` | `portfolio.py` (döndürülen liste) | Portföy kalemi |
| `PerformanceMetrics` | `analytics.py` (döndürülen JSON) | Performans metrikleri |
| `ScenarioRequest` | `analytics.py` (request body) | Senaryo isteği doğrulama |
| `ScenarioResult` | `analytics.py` (döndürülen JSON) | Senaryo sonucu |

**İlişkili dosyalar:** `backend/models/schemas.py`, tüm `backend/routers/*.py`.

---

## 8. Konfigürasyon & Ortam

### 8.1. `backend/config.py`

```python
import os

DATABASE_URL = os.getenv("DATABASE_URL", "investsim.db")
DEFAULT_VIRTUAL_BALANCE = 100000.0
DEFAULT_CURRENCY = "USD"
```

Kaynak: `InvestSim/backend/config.py:1-5`.

Açıklama:
- `os.getenv("DATABASE_URL", "investsim.db")` → Ortam değişkeni `DATABASE_URL` tanımlıysa onu kullanır; yoksa varsayılan `"investsim.db"`.
- `DEFAULT_VIRTUAL_BALANCE` → Yeni kullanıcıya verilen sanal para miktarı.
- `DEFAULT_CURRENCY` → Varsayılan para birimi.

Bu dosya, uygulama boyunca sabit olan değerleri tek yerden yönetmeyi sağlar. Testlerde farklı bir DB dosyası vermek için `DATABASE_URL` ortam değişkeni kullanılabilir.

**İlişkili dosyalar:** `backend/config.py`, `backend/database.py`.

---

## 9. Servis Katmanı — Fiyat Çekme

### 9.1. `backend/services/price_fetcher.py`

```python
import requests
from enum import Enum


class AssetType(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"


def fetch_price(symbol: str, asset_type: AssetType) -> dict | None:
    try:
        if asset_type == AssetType.STOCK:
            return _fetch_yahoo(symbol)
        elif asset_type == AssetType.CRYPTO:
            return _fetch_coingecko(symbol)
        elif asset_type == AssetType.FOREX:
            return _fetch_forex(symbol)
    except Exception:
        return None
    return None


def _fetch_yahoo(symbol: str) -> dict | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data["chart"]["result"]
    if not result:
        return None
    meta = result[0]["meta"]
    price = meta.get("regularMarketPrice") or meta.get("previousClose")
    currency = meta.get("currency", "USD")
    if price is None:
        return None
    return {"price": float(price), "currency": currency}


def _fetch_coingecko(symbol: str) -> dict | None:
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if symbol not in data or "usd" not in data[symbol]:
        return None
    return {"price": float(data[symbol]["usd"]), "currency": "USD"}


def _fetch_forex(symbol: str) -> dict | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    result = data["chart"]["result"]
    if not result:
        return None
    meta = result[0]["meta"]
    price = meta.get("regularMarketPrice") or meta.get("previousClose")
    if price is None:
        return None
    return {"price": float(price), "currency": "USD"}
```

Kaynak: `InvestSim/backend/services/price_fetcher.py:1-64`.

Açıklama, fonksiyon fonksiyon:

#### `AssetType(str, Enum)`

Python `Enum`'u string tabanlıdır. Bu, `AssetType.STOCK` değerinin `"stock"` stringi olduğu anlamına gelir. FastAPI path parametrelerinde otomatik doğrulama sağlar.

#### `fetch_price(symbol, asset_type)`

- Giriş: sembol (örn. `"AAPL"`, `"bitcoin"`) ve tür.
- Çıkış: `{"price": float, "currency": str}` veya hata durumunda `None`.
- `try/except` bloğu → Herhangi bir ağ/parse hatasında `None` döner; uygulama çökmez.

#### `_fetch_yahoo(symbol)`

- Yahoo Finance v8 API'sine istek atar.
- `User-Agent` header'ı → Bazı API'ler bot isteklerini engeller; gerçek tarayıcıymış gibi görünür.
- `resp.raise_for_status()` → HTTP 4xx/5xx varsa `requests.HTTPError` atar.
- `data["chart"]["result"]` → Yahoo'nun JSON yapısı. `result` boş liste ise sembol bulunamamıştır.
- `regularMarketPrice` veya `previousClose` → Piyasa açıkken canlı fiyat, kapalıyken son kapanış.

#### `_fetch_coingecko(symbol)`

- CoinGecko API'sine istek atar.
- `ids={symbol}` → CoinGecko ID'si (örn. `bitcoin`, `ethereum`).
- `vs_currencies=usd` → USD cinsinden fiyat.
- Dönüş: `{"price": float, "currency": "USD"}`.

#### `_fetch_forex(symbol)`

- Forex çiftleri için de Yahoo Finance kullanılır (örn. `EURUSD=X`).
- Yapı `_fetch_yahoo` ile aynıdır; sadece `currency` sabit `"USD"` döner.

> **Not:** Harici API'lerden veri çekmek **bloklayıcı** (senkron) işlemdir. `requests.get(...)` cevap gelene kadar bekler. Bu proje küçük ölçekli olduğu için async'e geçiş yapılmamıştır; yüksek trafikte `httpx.AsyncClient` veya `aiohttp` tercih edilmelidir.

**İlişkili dosyalar:** `backend/services/price_fetcher.py`, `backend/services/cache.py`, `backend/routers/market.py`, `tests/test_price_fetcher.py`.

---

## 10. Servis Katmanı — Cache

### 10.1. `backend/services/cache.py`

```python
import time
from typing import Any


class PriceCache:
    def __init__(self, ttl_seconds: int = 300):
        self._store: dict[str, dict] = {}
        self._ttl = ttl_seconds

    def get(self, symbol: str) -> dict | None:
        entry = self._store.get(symbol)
        if entry is None:
            return None
        if time.time() - entry["timestamp"] > self._ttl:
            del self._store[symbol]
            return None
        return entry["data"]

    def set(self, symbol: str, data: dict[str, Any]) -> None:
        self._store[symbol] = {"timestamp": time.time(), "data": data}

    def clear(self) -> None:
        self._store.clear()


cache = PriceCache(ttl_seconds=300)
```

Kaynak: `InvestSim/backend/services/cache.py:1-26`.

Açıklama:

- **`PriceCache`** → Bellek içi (in-memory) basit bir önbellek. Uygulama yeniden başlayınca sıfırlanır.
- **`ttl_seconds`** → Time To Live. Varsayılan 300 saniye (5 dakika). 5 dakika sonra veri "eski" sayılır ve tekrar API'den çekilir.
- **`self._store`** → Sözlük (dict) yapısı. Anahtar: sembol, Değer: `{"timestamp": float, "data": dict}`.
- **`get(symbol)`** →
  1. `self._store` içinde sembol var mı bakar.
  2. Yoksa `None` döner.
  3. Varsa, `time.time() - timestamp > ttl` kontrolü yapar. Eski ise siler ve `None` döner.
  4. Güncelse `data` kısmını döner.
- **`set(symbol, data)`** → Mevcut zamanı `timestamp` olarak kaydeder, datayı saklar.
- **`clear()`** → Tüm önbelleği temizler.
- **`cache = PriceCache(...)`** → Modül yüklendiğinde oluşturulan **global singleton**. Tüm router'lar aynı instance'ı paylaşır.

Neden cache?
- Harici API'lerin **rate limit**'i vardır (özellikle CoinGecko ücretsiz planı).
- Aynı sembol için tekrar tekrar istek atmak gereksizdir.
- Her kullanıcı işlem yaptığında fiyatı tekrar çekmek yerine cache'den okumak daha hızlıdır.

**İlişkili dosyalar:** `backend/services/cache.py`, `tests/test_cache.py`, tüm router dosyaları.

---

## 11. Routerlar — Market

### 11.1. `backend/routers/market.py`

```python
from fastapi import APIRouter, HTTPException
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache
from backend.database import get_db

router = APIRouter(prefix="/market", tags=["market"])

ASSETS = [
    {"symbol": "AAPL", "name": "Apple Inc.", "asset_type": "stock"},
    {"symbol": "TSLA", "name": "Tesla Inc.", "asset_type": "stock"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "asset_type": "stock"},
    {"symbol": "bitcoin", "name": "Bitcoin", "asset_type": "crypto"},
    {"symbol": "ethereum", "name": "Ethereum", "asset_type": "crypto"},
    {"symbol": "EURUSD=X", "name": "EUR/USD", "asset_type": "forex"},
    {"symbol": "GBPUSD=X", "name": "GBP/USD", "asset_type": "forex"},
]

@router.get("/assets")
def list_assets():
    return ASSETS

@router.get("/price/{symbol}")
def get_price(symbol: str, asset_type: str = "stock"):
    cached = cache.get(symbol)
    if cached:
        return {"symbol": symbol, "price": cached["price"], "currency": cached["currency"], "source": "cache"}
    result = fetch_price(symbol, AssetType(asset_type))
    if result is None:
        raise HTTPException(status_code=404, detail=f"Price not found for {symbol}")
    cache.set(symbol, result)
    return {"symbol": symbol, "price": result["price"], "currency": result["currency"], "source": "api"}
```

Kaynak: `InvestSim/backend/routers/market.py:1-31`.

Açıklama:

- **`APIRouter(prefix="/market", tags=["market"])`** → Bu router'daki tüm endpoint'lerin önüne `/market` ekler. Swagger docs'ta "market" etiketi altında gruplar.
- **`ASSETS`** → Hardcoded (kod içinde sabit yazılmış) varlık listesi. Demo amaçlıdır; ileride veritabanından veya harici API'den çekilebilir.
- **`@router.get("/assets")`** → `GET /market/assets`. Herhangi bir parametre almaz; varlık listesini döner.
- **`@router.get("/price/{symbol}")`** → `GET /market/price/{symbol}`. `symbol` path parametresi, `asset_type` query parametresidir (varsayılan `"stock"`).
  1. Önce `cache.get(symbol)` ile cache'e bakar.
  2. Cache'de varsa `"source": "cache"` ile döner.
  3. Yoksa `fetch_price()` ile harici API'den çeker.
  4. API'den de gelmezse `HTTPException(status_code=404, ...)` atar.
  5. Başarılı ise cache'e yazar ve `"source": "api"` ile döner.

**Path vs Query Parametreleri:**

| Tür | Syntax | URL Örneği | Kullanım |
|---|---|---|---|
| Path | `{symbol}` | `/price/AAPL` | Zorunlu, URL'nin parçası |
| Query | `asset_type: str = "stock"` | `/price/AAPL?asset_type=stock` | Opsiyonel, `?key=value` şeklinde |

**İlişkili dosyalar:** `backend/routers/market.py`, `frontend/js/market.js`, `frontend/market.html`.

---

## 12. Routerlar — Emirler

### 12.1. `backend/routers/orders.py`

```python
from fastapi import APIRouter, HTTPException
from backend.database import get_db
from backend.models.schemas import OrderRequest, OrderResponse
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache

router = APIRouter(prefix="/orders", tags=["orders"])

def execute_buy(conn, user_id: int, symbol: str, asset_type: str, quantity: float, price: float):
    cursor = conn.cursor()
    total = quantity * price
    cursor.execute("SELECT virtual_balance FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    if row is None:
        raise ValueError("User not found")
    balance = row["virtual_balance"]
    if balance < total:
        raise ValueError("Insufficient balance")
    cursor.execute("UPDATE users SET virtual_balance=? WHERE id=?", (balance - total, user_id))
    cursor.execute(
        "INSERT INTO transactions (user_id, asset_symbol, asset_type, transaction_type, quantity, price, total_amount) VALUES (?,?,?,?,?,?,?)",
        (user_id, symbol, asset_type, "buy", quantity, price, total)
    )
    cursor.execute(
        "SELECT total_quantity, avg_cost_basis FROM portfolios WHERE user_id=? AND asset_symbol=?",
        (user_id, symbol)
    )
    port = cursor.fetchone()
    if port is None:
        cursor.execute(
            "INSERT INTO portfolios (user_id, asset_symbol, asset_type, total_quantity, avg_cost_basis) VALUES (?,?,?,?,?)",
            (user_id, symbol, asset_type, quantity, price)
        )
    else:
        old_qty = port["total_quantity"]
        old_cost = port["avg_cost_basis"]
        new_qty = old_qty + quantity
        new_cost = (old_qty * old_cost + quantity * price) / new_qty
        cursor.execute(
            "UPDATE portfolios SET total_quantity=?, avg_cost_basis=? WHERE user_id=? AND asset_symbol=?",
            (new_qty, new_cost, user_id, symbol)
        )
    conn.commit()

def execute_sell(conn, user_id: int, symbol: str, asset_type: str, quantity: float, price: float):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT total_quantity, avg_cost_basis FROM portfolios WHERE user_id=? AND asset_symbol=?",
        (user_id, symbol)
    )
    port = cursor.fetchone()
    if port is None or port["total_quantity"] < quantity:
        raise ValueError("Insufficient shares")
    total = quantity * price
    cursor.execute("SELECT virtual_balance FROM users WHERE id=?", (user_id,))
    balance = cursor.fetchone()["virtual_balance"]
    cursor.execute("UPDATE users SET virtual_balance=? WHERE id=?", (balance + total, user_id))
    cursor.execute(
        "INSERT INTO transactions (user_id, asset_symbol, asset_type, transaction_type, quantity, price, total_amount) VALUES (?,?,?,?,?,?,?)",
        (user_id, symbol, asset_type, "sell", quantity, price, total)
    )
    new_qty = port["total_quantity"] - quantity
    if new_qty <= 0:
        cursor.execute("DELETE FROM portfolios WHERE user_id=? AND asset_symbol=?", (user_id, symbol))
    else:
        cursor.execute(
            "UPDATE portfolios SET total_quantity=? WHERE user_id=? AND asset_symbol=?",
            (new_qty, user_id, symbol)
        )
    conn.commit()

@router.post("/buy", response_model=OrderResponse)
def buy(req: OrderRequest):
    with get_db() as conn:
        cached = cache.get(req.asset_symbol)
        if cached:
            price = cached["price"]
        else:
            fetched = fetch_price(req.asset_symbol, AssetType(req.asset_type))
            if fetched is None:
                raise HTTPException(status_code=404, detail="Price not available")
            price = fetched["price"]
            cache.set(req.asset_symbol, fetched)
        try:
            execute_buy(conn, 1, req.asset_symbol, req.asset_type, req.quantity, price)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1")
        row = dict(cursor.fetchone())
        return OrderResponse(**row)

@router.post("/sell", response_model=OrderResponse)
def sell(req: OrderRequest):
    with get_db() as conn:
        cached = cache.get(req.asset_symbol)
        if cached:
            price = cached["price"]
        else:
            fetched = fetch_price(req.asset_symbol, AssetType(req.asset_type))
            if fetched is None:
                raise HTTPException(status_code=404, detail="Price not available")
            price = fetched["price"]
            cache.set(req.asset_symbol, fetched)
        try:
            execute_sell(conn, 1, req.asset_symbol, req.asset_type, req.quantity, price)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 1")
        row = dict(cursor.fetchone())
        return OrderResponse(**row)
```

Kaynak: `InvestSim/backend/routers/orders.py:1-112`.

Açıklama, fonksiyon fonksiyon:

#### `execute_buy(conn, user_id, symbol, asset_type, quantity, price)`

Alım işleminin veritabanı mantığı (iş mantığı katmanı):

1. **Bakiye kontrolü** → Kullanıcının `virtual_balance`'ı yeterli mi? `total = quantity * price`. Yetersizse `ValueError("Insufficient balance")`.
2. **Bakiye düşürme** → `UPDATE users SET virtual_balance = balance - total`.
3. **İşlem kaydı** → `transactions` tablosuna yeni satır ekle.
4. **Portföy güncelleme** →
   - Eğer bu sembolde ilk alım: `portfolios` tablosuna yeni satır (`total_quantity = quantity`, `avg_cost_basis = price`).
   - Daha önce varsa: **Ağırlıklı ortalama maliyet** hesaplanır:
     ```
     new_cost = (old_qty * old_cost + new_qty * new_price) / (old_qty + new_qty)
     ```
   - `UPDATE portfolios SET total_quantity=?, avg_cost_basis=?`.
5. `conn.commit()` → Tüm değişiklikleri kalıcı yap.

#### `execute_sell(conn, user_id, symbol, asset_type, quantity, price)`

Satım işleminin veritabanı mantığı:

1. **Portföy kontrolü** → Kullanıcının yeterli hissesi var mı? Yoksa `ValueError("Insufficient shares")`.
2. **Bakiye artırma** → Satış tutarı `virtual_balance`'a eklenir.
3. **İşlem kaydı** → `transactions` tablosuna `"sell"` kaydı ekle.
4. **Portföy güncelleme** →
   - Yeni miktar `<= 0` ise: `DELETE FROM portfolios`.
   - Değilse: `UPDATE portfolios SET total_quantity = new_qty`.
   - **Not:** Satışta `avg_cost_basis` değişmez; maliyet ortalaması sadece alımda güncellenir.
5. `conn.commit()`.

#### `buy(req: OrderRequest)` ve `sell(req: OrderRequest)`

- FastAPI endpoint fonksiyonları.
- `response_model=OrderResponse` → Dönen dict otomatik `OrderResponse` modeline göre doğrulanır ve serileştirilir.
- `with get_db() as conn` → Veritabanı bağlantısını açar, işlem bitince kapatır.
- Fiyat önce cache'e bakılır; yoksa API'den çekilir ve cache'e yazılır.
- `try/except ValueError` → İş mantığı hatalarını (`Insufficient balance`, `Insufficient shares`) HTTP 400 (Bad Request) olarak döner.
- İşlem sonrası son kaydı `SELECT * FROM transactions ORDER BY id DESC LIMIT 1` ile çekip `OrderResponse(**row)` olarak döner.

> **Not:** `user_id` sabit `1` olarak hardcoded. Şu an tek kullanıcılı demo olduğu için auth yok.

**İlişkili dosyalar:** `backend/routers/orders.py`, `backend/models/schemas.py`, `backend/database.py`, `frontend/js/dashboard.js`, `tests/test_orders.py`.

---

## 13. Routerlar — Portföy

### 13.1. `backend/routers/portfolio.py`

```python
from fastapi import APIRouter
from backend.database import get_db
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache
from typing import List

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

def get_portfolio(conn, user_id: int) -> List[dict]:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    rows = cursor.fetchall()
    result = []
    for row in rows:
        item = dict(row)
        cached = cache.get(item["asset_symbol"])
        if cached:
            current_price = cached["price"]
        else:
            fetched = fetch_price(item["asset_symbol"], AssetType(item["asset_type"]))
            if fetched:
                current_price = fetched["price"]
                cache.set(item["asset_symbol"], fetched)
            else:
                current_price = None
        item["current_price"] = current_price
        if current_price is not None:
            item["unrealized_pnl"] = (current_price - item["avg_cost_basis"]) * item["total_quantity"]
        else:
            item["unrealized_pnl"] = None
        result.append(item)
    return result

def get_transaction_history(conn, user_id: int) -> List[dict]:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM transactions WHERE user_id=? ORDER BY timestamp DESC",
        (user_id,)
    )
    return [dict(row) for row in cursor.fetchall()]

@router.get("/")
def read_portfolio():
    with get_db() as conn:
        return get_portfolio(conn, 1)

@router.get("/history")
def read_history():
    with get_db() as conn:
        return get_transaction_history(conn, 1)

@router.get("/balance")
def read_balance():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT virtual_balance FROM users WHERE id=1")
        return {"balance": cursor.fetchone()["virtual_balance"]}
```

Kaynak: `InvestSim/backend/routers/portfolio.py:1-57`.

Açıklama:

- **`get_portfolio(conn, user_id)`** → Veritabanındaki `portfolios` tablosunu okur; her varlık için güncel fiyat çekerek **realize edilmemiş kar/zarar** (unrealized PnL) hesaplar.
  - `unrealized_pnl = (current_price - avg_cost_basis) * total_quantity`
  - Fiyat çekilemezse `current_price = None`, `unrealized_pnl = None`.
- **`get_transaction_history(conn, user_id)`** → `transactions` tablosunu `timestamp DESC` (en yeni önce) sıralar.
- **`read_portfolio()`** → `GET /portfolio/`. Mevcut pozisyonları döner.
- **`read_history()`** → `GET /portfolio/history`. İşlem geçmişini döner.
- **`read_balance()`** → `GET /portfolio/balance`. Sadece `{"balance": ...}` JSON'u döner.

> **Not:** `dict(row)` → `sqlite3.Row` objesini Python sözlüğüne çevirir; JSON serileştirme için gerekli.

**İlişkili dosyalar:** `backend/routers/portfolio.py`, `frontend/js/portfolio.js`, `frontend/js/dashboard.js`, `tests/test_portfolio.py`.

---

## 14. Routerlar — Analiz

### 14.1. `backend/routers/analytics.py`

```python
from fastapi import APIRouter
from backend.database import get_db
from backend.models.schemas import ScenarioRequest
from backend.services.price_fetcher import fetch_price, AssetType
from backend.services.cache import cache

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_performance_metrics(conn, user_id: int) -> dict:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(total_amount) as total_invested FROM transactions WHERE user_id=? AND transaction_type='buy'",
        (user_id,)
    )
    row = cursor.fetchone()
    total_invested = row["total_invested"] or 0.0
    cursor.execute("SELECT * FROM portfolios WHERE user_id=?", (user_id,))
    holdings = cursor.fetchall()
    current_value = 0.0
    for h in holdings:
        cached = cache.get(h["asset_symbol"])
        if cached:
            price = cached["price"]
        else:
            fetched = fetch_price(h["asset_symbol"], AssetType(h["asset_type"]))
            if fetched:
                price = fetched["price"]
                cache.set(h["asset_symbol"], fetched)
            else:
                price = 0.0
        current_value += price * h["total_quantity"]
    total_return = current_value - total_invested
    total_return_percent = (total_return / total_invested * 100) if total_invested > 0 else 0.0
    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "total_return": total_return,
        "total_return_percent": round(total_return_percent, 2)
    }

def calculate_scenario(symbol: str, asset_type: str, hypothetical_date: str, hypothetical_amount: float) -> dict:
    cached = cache.get(symbol)
    if cached:
        current_price = cached["price"]
    else:
        fetched = fetch_price(symbol, AssetType(asset_type))
        if fetched:
            current_price = fetched["price"]
            cache.set(symbol, fetched)
        else:
            current_price = None
    if current_price is None:
        return {
            "symbol": symbol,
            "hypothetical_date": hypothetical_date,
            "hypothetical_amount": hypothetical_amount,
            "current_price": None,
            "hypothetical_value": None,
            "gain_loss": None,
            "gain_loss_percent": None,
            "note": "Historical price lookup not available in v1"
        }
    shares = hypothetical_amount / current_price
    hypothetical_value = shares * current_price
    gain_loss = hypothetical_value - hypothetical_amount
    gain_loss_percent = (gain_loss / hypothetical_amount * 100) if hypothetical_amount > 0 else 0.0
    return {
        "symbol": symbol,
        "hypothetical_date": hypothetical_date,
        "hypothetical_amount": hypothetical_amount,
        "current_price": current_price,
        "hypothetical_value": round(hypothetical_value, 2),
        "gain_loss": round(gain_loss, 2),
        "gain_loss_percent": round(gain_loss_percent, 2)
    }

@router.get("/performance")
def read_performance():
    with get_db() as conn:
        return get_performance_metrics(conn, 1)

@router.post("/scenario")
def run_scenario(req: ScenarioRequest):
    result = calculate_scenario(req.asset_symbol, req.asset_type, req.hypothetical_date, req.hypothetical_amount)
    return result

@router.get("/diversification")
def read_diversification():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT asset_type, SUM(total_quantity * avg_cost_basis) as value FROM portfolios WHERE user_id=1 GROUP BY asset_type"
        )
        rows = cursor.fetchall()
        total = sum(r["value"] or 0 for r in rows)
        result = []
        for r in rows:
            value = r["value"] or 0
            result.append({
                "asset_type": r["asset_type"],
                "value": round(value, 2),
                "percentage": round(value / total * 100, 2) if total > 0 else 0
            })
        return result
```

Kaynak: `InvestSim/backend/routers/analytics.py:1-104`.

Açıklama:

#### `get_performance_metrics(conn, user_id)`

Portföy performansını hesaplar:

1. **`total_invested`** → Tüm `"buy"` işlemlerinin `total_amount` toplamı.
2. **`current_value`** → Her portföy varlığı için `current_price * total_quantity` toplamı.
3. **`total_return`** → `current_value - total_invested`.
4. **`total_return_percent`** → `(total_return / total_invested) * 100`. `total_invested == 0` ise `0.0`.

> **Not:** Satış işlemleri `total_invested`'dan düşürülmez; bu basit bir "toplam yatırılan - güncel değer" hesabıdır. Daha gelişmiş realizasyon hesaplaması ileride eklenebilir.

#### `calculate_scenario(symbol, asset_type, hypothetical_date, hypothetical_amount)`

"Ya öyle yapsaydım" senaryosu:

1. Güncel fiyatı çeker (cache/API).
2. Fiyat bulunamazsa `note` alanı ile bilgilendirici yanıt döner.
3. `shares = hypothetical_amount / current_price` → O tutarla kaç hisse alınabilirdi.
4. `hypothetical_value = shares * current_price` → Bugünkü değeri (aslında aynı tutar, çünkü anlık fiyat üzerinden).
5. `gain_loss = hypothetical_value - hypothetical_amount`.

> **Not:** `v1`'de tarihsel fiyat verisi yok. `hypothetical_date` şu an sadece kayıt amaçlı; hesaplama **bugünkü fiyat** üzerinden yapılır. Gelecekte tarihsel veri entegrasyonu eklenebilir.

#### `read_diversification()`

Portföyün varlık türüne göre dağılımı:

- SQL `GROUP BY asset_type` ile her türün maliyet değeri hesaplanır.
- `percentage` → Her türün toplam içindeki payı.
- Örnek: `%40 hisse, %30 kripto, %30 döviz`.

**İlişkili dosyalar:** `backend/routers/analytics.py`, `frontend/js/analytics.js`, `tests/test_analytics.py`.

---

## 15. Frontend Mimarisi

### 15.1. Genel yapı

Frontend, framework kullanmayan (vanilla) HTML/CSS/JS'den oluşur. Her sayfa kendi `.html`, `.js` dosyasına sahiptir. Ortak olanlar:

- **`frontend/css/styles.css`** → Tüm sayfalar için ortak koyu tema stili.
- **`frontend/js/api.js`** → Tüm backend API çağrılarını merkezi bir yerden yapan client.

### 15.2. `frontend/index.html`

```html
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InvestSim - Dashboard</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <nav class="navbar">
        <h1>InvestSim</h1>
        <div class="nav-links">
            <a href="index.html" class="active">Dashboard</a>
            <a href="market.html">Piyasa</a>
            <a href="portfolio.html">Portföy</a>
            <a href="analytics.html">Analiz</a>
        </div>
    </nav>
    <main class="container">
        <section class="summary-cards">
            <div class="card">
                <h3>Sanal Bakiye</h3>
                <p id="balance">Yükleniyor...</p>
            </div>
            <div class="card">
                <h3>Portföy Değeri</h3>
                <p id="portfolio-value">Yükleniyor...</p>
            </div>
            <div class="card">
                <h3>Toplam Getiri</h3>
                <p id="total-return">Yükleniyor...</p>
            </div>
        </section>
        <section class="quick-trade">
            <h2>Hızlı Al/Sat</h2>
            <form id="trade-form">
                <select id="trade-asset">
                    <option value="">Varlık seçin</option>
                </select>
                <input type="number" id="trade-qty" placeholder="Miktar" min="0.01" step="0.01">
                <button type="button" id="btn-buy">Al</button>
                <button type="button" id="btn-sell">Sat</button>
            </form>
            <p id="trade-msg"></p>
        </section>
        <section class="holdings">
            <h2>Portföyüm</h2>
            <table id="holdings-table">
                <thead><tr><th>Sembol</th><th>Tip</th><th>Miktar</th><th>Maliyet</th><th>Fiyat</th><th>K/Z</th></tr></thead>
                <tbody></tbody>
            </table>
        </section>
    </main>
    <script src="js/api.js"></script>
    <script src="js/dashboard.js"></script>
</body>
</html>
```

Kaynak: `InvestSim/frontend/index.html:1-57`.

Açıklama:
- **`<nav class="navbar">`** → Tüm sayfalarda ortak navigasyon. Aktif sayfaya `active` class'ı verilir.
- **`<section class="summary-cards">`** → Üç kartlık özet: bakiye, portföy değeri, getiri.
- **`id="balance"`**, **`id="portfolio-value"`**, **`id="total-return"`** → JavaScript'in dolduracağı yerler.
- **Hızlı Al/Sat** → Dropdown'dan varlık seçilir, miktar girilir, Al/Sat butonlarına tıklanır.
- **`<table id="holdings-table">`** → Portföy pozisyonları dinamik olarak doldurulur.
- **`<script>` sırası** → `api.js` önce yüklenir (çünkü `dashboard.js` ona bağımlı).

### 15.3. `frontend/css/styles.css`

```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #e2e8f0; }
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: #1e293b; border-bottom: 1px solid #334155; }
.nav-links a { color: #94a3b8; text-decoration: none; margin-left: 1.5rem; }
.nav-links a.active, .nav-links a:hover { color: #38bdf8; }
.container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
.summary-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
.card { background: #1e293b; padding: 1.5rem; border-radius: 0.5rem; }
.card h3 { color: #94a3b8; font-size: 0.875rem; margin-bottom: 0.5rem; }
.card p { font-size: 1.5rem; font-weight: 600; }
.positive { color: #4ade80; }
.negative { color: #f87171; }
.quick-trade, .holdings { background: #1e293b; padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 2rem; }
.quick-trade form { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.quick-trade select, .quick-trade input { padding: 0.5rem; border-radius: 0.25rem; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; }
.quick-trade button { padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; cursor: pointer; }
#btn-buy { background: #16a34a; color: white; }
#btn-sell { background: #dc2626; color: white; }
table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
th, td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #334155; }
th { color: #94a3b8; font-size: 0.875rem; }
#scenario-form { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 1rem; }
#scenario-form select, #scenario-form input { padding: 0.5rem; border-radius: 0.25rem; border: 1px solid #334155; background: #0f172a; color: #e2e8f0; }
#btn-scenario { padding: 0.5rem 1rem; border: none; border-radius: 0.25rem; cursor: pointer; background: #2563eb; color: white; }
#scenario-result { margin-top: 1rem; background: #1e293b; padding: 1rem; border-radius: 0.5rem; }
```

Kaynak: `InvestSim/frontend/css/styles.css:1-25`.

Açıklama:
- **CSS Reset** → `* { box-sizing: border-box; margin: 0; padding: 0; }`.
- **Koyu tema** → `background: #0f172a` (slate-900), `color: #e2e8f0` (slate-200).
- **Flexbox** → `.navbar` ve form elemanları `display: flex` ile hizalanır.
- **CSS Grid** → `.summary-cards` `grid` ile responsive kart düzeni (`auto-fit`, `minmax`).
- **Renk sınıfları** → `.positive` yeşil (#4ade80), `.negative` kırmızı (#f87171). JavaScript dinamik olarak bu class'ları ekler.
- **Responsive** → `flex-wrap: wrap` ve `grid-template-columns: repeat(auto-fit, ...)` sayesinde mobilde de düzgün görünür.

### 15.4. `frontend/js/api.js`

```javascript
const API_BASE = '';

async function apiGet(path) {
    const resp = await fetch(`${API_BASE}${path}`);
    if (!resp.ok) throw new Error(`GET ${path} failed: ${resp.status}`);
    return resp.json();
}

async function apiPost(path, body) {
    const resp = await fetch(`${API_BASE}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!resp.ok) {
        const err = await resp.text();
        throw new Error(`POST ${path} failed: ${resp.status} - ${err}`);
    }
    return resp.json();
}

const API = {
    assets: () => apiGet('/market/assets'),
    price: (symbol, type) => apiGet(`/market/price/${symbol}?asset_type=${type}`),
    buy: (body) => apiPost('/orders/buy', body),
    sell: (body) => apiPost('/orders/sell', body),
    portfolio: () => apiGet('/portfolio/'),
    history: () => apiGet('/portfolio/history'),
    balance: () => apiGet('/portfolio/balance'),
    performance: () => apiGet('/analytics/performance'),
    scenario: (body) => apiPost('/analytics/scenario', body),
    diversification: () => apiGet('/analytics/diversification'),
};
```

Kaynak: `InvestSim/frontend/js/api.js:1-33`.

Açıklama:

- **`API_BASE = ''`** → Göreceli URL kullanır; aynı origin'den (`localhost:8000`) istek atar.
- **`async/await`** → Asenkron işlemleri senkron-gibi yazmak için. `fetch()` Promise döner; `await` sonucu bekler.
- **`apiGet(path)`** → `GET` isteği atar. `resp.ok` → HTTP 200-299 arası. Değilse hata fırlatır.
- **`apiPost(path, body)`** → `POST` isteği atar. `body` JSON string'e çevrilir (`JSON.stringify`). `Content-Type: application/json` header'ı gönderilir.
- **`API` nesnesi** → Tüm endpoint'ler merkezi bir nesnede toplanır. Sayfa script'leri `API.portfolio()` gibi çağrılarla kullanır.

> **Not:** `API_BASE` boş string. Eğer frontend farklı bir sunucuda (örn. `localhost:3000`) çalışırsa, buraya `http://localhost:8000` yazılmalıdır. Şu an FastAPI aynı origin'den servis ettiği için gerekmez.

**İlişkili dosyalar:** `frontend/js/api.js`, tüm `frontend/js/*.js`, `frontend/*.html`.

---

## 16. Frontend Sayfaları

### 16.1. `frontend/js/dashboard.js`

```javascript
async function loadDashboard() {
    try {
        const perf = await API.performance();
        const bal = await API.balance();
        document.getElementById('balance').textContent = '$' + bal.balance.toFixed(2);
        document.getElementById('portfolio-value').textContent = '$' + perf.current_value.toFixed(2);
        const retEl = document.getElementById('total-return');
        retEl.textContent = (perf.total_return >= 0 ? '+' : '') + perf.total_return.toFixed(2) + ' (' + perf.total_return_percent + '%)';
        retEl.className = perf.total_return >= 0 ? 'positive' : 'negative';
    } catch (e) {
        console.error(e);
    }
    try {
        const holdings = await API.portfolio();
        const tbody = document.querySelector('#holdings-table tbody');
        tbody.innerHTML = '';
        holdings.forEach(h => {
            const tr = document.createElement('tr');
            const pnl = h.unrealized_pnl !== null ? h.unrealized_pnl.toFixed(2) : '-';
            const pnlClass = h.unrealized_pnl === null ? '' : (h.unrealized_pnl >= 0 ? 'positive' : 'negative');
            tr.innerHTML = `<td>${h.asset_symbol}</td><td>${h.asset_type}</td><td>${h.total_quantity}</td><td>$${h.avg_cost_basis.toFixed(2)}</td><td>$${h.current_price !== null ? h.current_price.toFixed(2) : '-'}</td><td class="${pnlClass}">${pnl}</td>`;
            tbody.appendChild(tr);
        });
    } catch (e) {
        console.error(e);
    }
}

async function loadAssets() {
    const assets = await API.assets();
    const select = document.getElementById('trade-asset');
    assets.forEach(a => {
        const opt = document.createElement('option');
        opt.value = JSON.stringify({symbol: a.symbol, type: a.asset_type});
        opt.textContent = `${a.symbol} (${a.asset_type})`;
        select.appendChild(opt);
    });
}

document.getElementById('btn-buy').addEventListener('click', async () => {
    const sel = document.getElementById('trade-asset').value;
    const qty = parseFloat(document.getElementById('trade-qty').value);
    if (!sel || !qty) return;
    const asset = JSON.parse(sel);
    try {
        await API.buy({asset_symbol: asset.symbol, asset_type: asset.type, quantity: qty});
        document.getElementById('trade-msg').textContent = 'Alım başarılı!';
        document.getElementById('trade-msg').className = 'positive';
        loadDashboard();
    } catch (e) {
        document.getElementById('trade-msg').textContent = e.message;
        document.getElementById('trade-msg').className = 'negative';
    }
});

document.getElementById('btn-sell').addEventListener('click', async () => {
    const sel = document.getElementById('trade-asset').value;
    const qty = parseFloat(document.getElementById('trade-qty').value);
    if (!sel || !qty) return;
    const asset = JSON.parse(sel);
    try {
        await API.sell({asset_symbol: asset.symbol, asset_type: asset.type, quantity: qty});
        document.getElementById('trade-msg').textContent = 'Satım başarılı!';
        document.getElementById('trade-msg').className = 'positive';
        loadDashboard();
    } catch (e) {
        document.getElementById('trade-msg').textContent = e.message;
        document.getElementById('trade-msg').className = 'negative';
    }
});

loadAssets();
loadDashboard();
```

Kaynak: `InvestSim/frontend/js/dashboard.js:1-73`.

Açıklama:

- **`loadDashboard()`** → İki bağımsız `try/catch` bloğu:
  1. Performans ve bakiye verilerini çeker; DOM elemanlarını günceller.
  2. Portföy listesini çeker; tabloya satır satır ekler.
- **`loadAssets()`** → Varlık listesini çeker; `<select>` dropdown'ını doldurur. Her option'un `value`'su JSON string'dir (`{"symbol": "AAPL", "type": "stock"}`); böylece sembol ve tip birlikte taşınır.
- **Event Listener'lar** → Al/Sat butonlarına tıklanınca:
  1. Dropdown'dan seçilen JSON parse edilir.
  2. Miktar `parseFloat` ile sayıya çevrilir.
  3. `API.buy()` veya `API.sell()` çağrılır.
  4. Başarılı ise yeşil mesaj + `loadDashboard()` yenileme.
  5. Hata ise kırmızı mesaj (backend'den gelen `detail` metni).
- **Sayfa yükleme** → En altta `loadAssets(); loadDashboard();` ile otomatik veri çekilir.

> **Not:** `toFixed(2)` → Sayıyı 2 ondalık basamağa yuvarlar (para birimi formatı).

### 16.2. `frontend/js/market.js`

```javascript
async function loadMarket() {
    const assets = await API.assets();
    const tbody = document.querySelector('#market-table tbody');
    tbody.innerHTML = '';
    for (const a of assets) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${a.symbol}</td><td>${a.name}</td><td>${a.asset_type}</td><td id="price-${a.symbol}">Yükleniyor...</td><td id="src-${a.symbol}">-</td>`;
        tbody.appendChild(tr);
        API.price(a.symbol, a.asset_type).then(data => {
            document.getElementById(`price-${a.symbol}`).textContent = '$' + data.price.toFixed(2);
            document.getElementById(`src-${a.symbol}`).textContent = data.source;
        }).catch(err => {
            document.getElementById(`price-${a.symbol}`).textContent = 'N/A';
            document.getElementById(`src-${a.symbol}`).textContent = 'Hata';
            console.error(`Price fetch failed for ${a.symbol}:`, err.message);
        });
    }
}
loadMarket();
```

Kaynak: `InvestSim/frontend/js/market.js:1-19`.

Açıklama:

- **`for...of` döngüsü** → Her varlık için tabloya bir satır ekler.
- **Asenkron fiyat çekme** → `API.price()` çağrısı `then/catch` ile paralel çalışır. Sayfa donmadan her sembol için ayrı ayrı fiyat güncellenir.
- **Hata yönetimi** → Bir sembolün fiyatı çekilemezse `N/A` ve `Hata` gösterilir; diğerleri çalışmaya devam eder.

> **Not:** Burada `async/await` yerine `then/catch` kullanılmıştır. Her iki yaklaşım da geçerlidir; `then/catch` paralel çağrıları zincirleme gerektirmeden yönetmek için tercih edilmiştir.

### 16.3. `frontend/js/portfolio.js`

```javascript
async function loadPortfolio() {
    const holdings = await API.portfolio();
    const tbody = document.querySelector('#portfolio-table tbody');
    tbody.innerHTML = '';
    holdings.forEach(h => {
        const tr = document.createElement('tr');
        const pnl = h.unrealized_pnl !== null ? h.unrealized_pnl.toFixed(2) : '-';
        const pnlClass = h.unrealized_pnl === null ? '' : (h.unrealized_pnl >= 0 ? 'positive' : 'negative');
        tr.innerHTML = `<td>${h.asset_symbol}</td><td>${h.asset_type}</td><td>${h.total_quantity}</td><td>$${h.avg_cost_basis.toFixed(2)}</td><td>$${h.current_price !== null ? h.current_price.toFixed(2) : '-'}</td><td class="${pnlClass}">${pnl}</td>`;
        tbody.appendChild(tr);
    });
    const history = await API.history();
    const htbody = document.querySelector('#history-table tbody');
    htbody.innerHTML = '';
    history.forEach(t => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${new Date(t.timestamp).toLocaleString()}</td><td>${t.transaction_type.toUpperCase()}</td><td>${t.asset_symbol}</td><td>${t.quantity}</td><td>$${t.price.toFixed(2)}</td><td>$${t.total_amount.toFixed(2)}</td>`;
        htbody.appendChild(tr);
    });
}
loadPortfolio();
```

Kaynak: `InvestSim/frontend/js/portfolio.js:1-21`.

Açıklama:

- İki tablo doldurulur: **Portföy** ve **İşlem Geçmişi**.
- **`new Date(t.timestamp).toLocaleString()`** → ISO timestamp'i yerel tarih/saat formatına çevirir.
- **`toUpperCase()`** → `"buy"` → `"BUY"`.

### 16.4. `frontend/js/analytics.js`

```javascript
async function loadAnalytics() {
    const perf = await API.performance();
    document.getElementById('perf-display').innerHTML = `
        <p>Yatırılan: $${perf.total_invested.toFixed(2)}</p>
        <p>Güncel Değer: $${perf.current_value.toFixed(2)}</p>
        <p>Getiri: <span class="${perf.total_return >= 0 ? 'positive' : 'negative'}">${perf.total_return.toFixed(2)} (${perf.total_return_percent}%)</span></p>
    `;
    const div = await API.diversification();
    const tbody = document.querySelector('#diversification-table tbody');
    tbody.innerHTML = '';
    div.forEach(d => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${d.asset_type}</td><td>$${d.value}</td><td>${d.percentage}%</td>`;
        tbody.appendChild(tr);
    });
}

async function loadAssets() {
    const assets = await API.assets();
    const select = document.getElementById('scenario-asset');
    assets.forEach(a => {
        const opt = document.createElement('option');
        opt.value = JSON.stringify({symbol: a.symbol, type: a.asset_type});
        opt.textContent = `${a.symbol} (${a.asset_type})`;
        select.appendChild(opt);
    });
}

document.getElementById('btn-scenario').addEventListener('click', async () => {
    const sel = document.getElementById('scenario-asset').value;
    const date = document.getElementById('scenario-date').value;
    const amount = parseFloat(document.getElementById('scenario-amount').value);
    if (!sel || !date || !amount) return;
    const asset = JSON.parse(sel);
    try {
        const result = await API.scenario({
            name: `${asset.symbol} senaryo`,
            asset_symbol: asset.symbol,
            asset_type: asset.type,
            hypothetical_date: date,
            hypothetical_amount: amount
        });
        const el = document.getElementById('scenario-result');
        if (result.current_price === null) {
            el.innerHTML = `<p class="negative">Fiyat verisi alınamadı.</p>`;
        } else {
            el.innerHTML = `
                <p>Güncel Fiyat: $${result.current_price.toFixed(2)}</p>
                <p>Varsayım Değeri: $${result.hypothetical_value}</p>
                <p>K/Z: <span class="${result.gain_loss === null ? '' : (result.gain_loss >= 0 ? 'positive' : 'negative')}">$${result.gain_loss} (${result.gain_loss_percent}%)</span></p>
            `;
        }
    } catch (e) {
        document.getElementById('scenario-result').textContent = e.message;
    }
});

loadAssets();
loadAnalytics();
```

Kaynak: `InvestSim/frontend/js/analytics.js:1-59`.

Açıklama:

- **`loadAnalytics()`** → Performans ve çeşitlendirme verilerini çeker; DOM'u günceller.
- **`loadAssets()`** → Senaryo formundaki dropdown'u doldurur.
- **Senaryo butonu** → Tarih ve tutar girildikten sonra `API.scenario()` çağrılır.
- `name` alanı otomatik oluşturulur: `"AAPL senaryo"`.
- Sonuçlar `scenario-result` div'ine yazılır. Fiyat bulunamazsa kırmızı uyarı gösterilir.

**İlişkili dosyalar:** Tüm `frontend/js/*.js`, `frontend/*.html`.

---

## 17. Test Kapsamı

### 17.1. Genel bakış

Testler `pytest` framework'üyle yazılır. Her test dosyası kendi geçici SQLite veritabanını kullanır (`tests/test_*.db`). Test öncesi veritabanı oluşturulur, test sonrası silinir.

### 17.2. `tests/conftest.py`

```python
import pytest
import sqlite3
import os

TEST_DB = "tests/test_investsim.db"

@pytest.fixture(autouse=True)
def clean_test_db():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_creates_tables():
    from backend.database import init_db
    init_db(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    assert "users" in tables
    assert "transactions" in tables
    assert "portfolios" in tables
    assert "price_cache" in tables
    assert "scenarios" in tables
```

Kaynak: `InvestSim/tests/conftest.py:1-27`.

Açıklama:
- **`@pytest.fixture(autouse=True)`** → Bu fixture **tüm test dosyalarında** otomatik çalışır. Her testten önce eski DB'yi siler, testten sonra temizler.
- **`yield`** → Fixture'in ortasındaki ayrım noktası. `yield`'den önce setup, sonra teardown.
- **`test_database_creates_tables()`** → `init_db`'nin tüm tabloları doğru oluşturduğunu doğrular.

> **Not:** `conftest.py`, pytest'in otomatik olarak bulduğu özel bir dosya adıdır. Aynı dizindeki tüm testler bu fixture'lara erişebilir.

### 17.3. Test dosyaları özeti

| Dosya | Test Edilen | Önemli Kontroller |
|---|---|---|
| `tests/test_price_fetcher.py` | Gerçek API entegrasyonu | Fiyat dict döner, fiyat > 0, geçersiz sembol → `None` |
| `tests/test_cache.py` | Bellek içi cache | Cache miss, set/get, TTL süresi dolunca temizleme, `clear()` |
| `tests/test_orders.py` | Al/sat iş mantığı | Bakiye düşer, portföy oluşur, yetersiz bakiye/bakiye hatası, satış sonrası bakiye artar |
| `tests/test_portfolio.py` | Portföy okuma | Pozisyon listesi, işlem geçmişi doğru sayıda döner |
| `tests/test_analytics.py` | Performans ve senaryo | Toplam yatırım doğru, senaryo sonucu gerekli alanları içerir |

### 17.4. `tests/test_orders.py` (örnek inceleme)

```python
import pytest
import os
from backend.database import init_db, get_db
from backend.routers.orders import execute_buy, execute_sell

TEST_DB = "tests/test_orders.db"

@pytest.fixture(autouse=True)
def setup():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_buy_reduces_balance():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        cursor = conn.cursor()
        cursor.execute("SELECT virtual_balance FROM users WHERE id=1")
        balance = cursor.fetchone()["virtual_balance"]
        assert balance == 100000.0 - 1500.0

def test_buy_creates_portfolio_entry():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolios WHERE user_id=1 AND asset_symbol='AAPL'")
        row = cursor.fetchone()
        assert row["total_quantity"] == 10.0
        assert row["avg_cost_basis"] == 150.0

def test_sell_insufficient_shares():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 5, 150.0)
        with pytest.raises(ValueError, match="Insufficient"):
            execute_sell(conn, 1, "AAPL", "stock", 10, 160.0)

def test_sell_updates_balance():
    with get_db(TEST_DB) as conn:
        execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)
        execute_sell(conn, 1, "AAPL", "stock", 5, 160.0)
        cursor = conn.cursor()
        cursor.execute("SELECT virtual_balance FROM users WHERE id=1")
        balance = cursor.fetchone()["virtual_balance"]
        assert balance == 99300.0
```

Kaynak: `InvestSim/tests/test_orders.py:1-47`.

Açıklama:
- **`@pytest.fixture(autouse=True)`** → Her test için ayrı temiz DB.
- **`execute_buy(conn, 1, "AAPL", "stock", 10, 150.0)`** → Doğrudan iş mantığı fonksiyonunu çağırır (HTTP katmanını atlar).
- **`assert balance == 100000.0 - 1500.0`** → Beklenen değeri doğrular.
- **`pytest.raises(ValueError, match="Insufficient")`** → Bu blok içinde `ValueError` atılmasını bekler; atılmazsa test fail olur. `match` ile hata mesajının `"Insufficient"` içerdiğini kontrol eder.

> **Not:** `test_price_fetcher.py` gerçek harici API'ye istek atar. API geçici olarak down olursa veya rate limit'e takılırsa test fail olabilir. CI/CD ortamında mock kullanımı tercih edilebilir.

**İlişkili dosyalar:** `tests/conftest.py`, `tests/test_*.py`, `backend/database.py`.

---

## 18. Tipik Geliştirici Akışları (Mini Tarifler)

### Tarif 1: Yeni endpoint ekleme (örn. `GET /market/search?q=Apple`)

1. `backend/routers/market.py`'ye yeni fonksiyon ekle:
   ```python
   @router.get("/search")
   def search_assets(q: str = ""):
       return [a for a in ASSETS if q.lower() in a["name"].lower()]
   ```
2. `frontend/js/api.js`'ye yeni metod ekle:
   ```javascript
   search: (q) => apiGet(`/market/search?q=${encodeURIComponent(q)}`),
   ```
3. İlgili HTML/JS'de kullan.
4. Test ekle: `tests/test_market.py` (isteğe bağlı).

### Tarif 2: Yeni frontend sayfası ekleme (örn. `ayarlar.html`)

1. `frontend/ayarlar.html` oluştur; navigasyona link ekle.
2. `frontend/js/ayarlar.js` oluştur; `api.js`'yi import et (`<script src="js/api.js"></script>` önce).
3. `backend/main.py`'de `StaticFiles` otomatik servis eder; ek konfigürasyon gerekmez.

### Tarif 3: Yeni veritabanı tablosu ekleme (örn. `watchlists` — izleme listesi)

1. `backend/database.py`'de `SCHEMA`'ya `CREATE TABLE` ekle:
   ```sql
   CREATE TABLE IF NOT EXISTS watchlists (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       asset_symbol TEXT NOT NULL,
       FOREIGN KEY (user_id) REFERENCES users(id)
   );
   ```
2. `init_db()` zaten `executescript(SCHEMA)` çalıştırır; tablo otomatik oluşur.
   > **Not:** Mevcut `.db` dosyası varsa tablo `CREATE TABLE IF NOT EXISTS` sayesinde güvenli şekilde eklenir.
3. Yeni router (`backend/routers/watchlist.py`) veya mevcut router'a endpoint ekle.
4. Pydantic şema ekle (`backend/models/schemas.py`).

### Tarif 4: Harici API entegrasyonu ekleme (örn. hisse haberleri)

1. `backend/services/` altına yeni dosya (örn. `news_fetcher.py`).
2. `requests.get(...)` ile istek at; `try/except` ile hata yönet.
3. Router'dan çağır; cache'e almak istersen `PriceCache`'e benzer bir `NewsCache` yaz.
4. Testte mock kullan:
   ```python
   from unittest.mock import patch
   
   @patch("backend.services.news_fetcher.requests.get")
   def test_news(mock_get):
       mock_get.return_value.json.return_value = {"articles": [...]}
       ...
   ```

### Tarif 5: Stil değişikliği (örn. tema rengi)

1. `frontend/css/styles.css`'te renk değişkenlerini güncelle.
2. Tarayıcıda sayfayı yenile (FastAPI `StaticFiles` canlı yenileme yapmaz; dosya değişince sayfayı yenilemen gerekir).

---

## 19. Hızlı Syntax Kartı

### 19.1. Python Type Hints

| Syntax | Anlam | Örnek |
|---|---|---|
| `def f() -> int` | Dönüş tipi int | `def add(a: int, b: int) -> int:` |
| `float \| None` | Union tip | `price: float \| None = None` |
| `list[dict]` | Liste içinde dict | `def foo() -> list[dict]:` |
| `Literal["a","b"]` | Sadece bu değerler | `x: Literal["buy","sell"]` |
| `Field(gt=0)` | 0'dan büyük | `qty: float = Field(gt=0)` |

### 19.2. FastAPI Decorator'ları

| Decorator | URL | HTTP Metodu | Parametre Türü |
|---|---|---|---|
| `@app.get("/x")` | `/x` | GET | — |
| `@app.post("/x")` | `/x` | POST | Request body |
| `@app.get("/x/{id}")` | `/x/5` | GET | Path parametresi |
| `@app.get("/x")` | `/x?q=abc` | GET | Query parametresi |

### 19.3. Pydantic Model

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str
    price: float = Field(gt=0)
```

- `Item(name="A", price=10)` → doğrulama + oluşturma.
- `Item(name="A", price=-1)` → `ValidationError`.

### 19.4. JavaScript Fetch / Await

```javascript
// GET
const data = await fetch('/api/x').then(r => r.json());

// POST
const resp = await fetch('/api/x', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({key: 'value'})
});
const result = await resp.json();
```

### 19.5. CSS Flex / Grid

```css
/* Flexbox */
.container { display: flex; gap: 1rem; flex-wrap: wrap; }

/* Grid - responsive kartlar */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; }
```

---

## 20. Sözlük ve Kısaltmalar

| Terim | Açıklama |
|---|---|
| **API** | Application Programming Interface — uygulamaların birbiriyle konuşma protokolü. |
| **ASGI** | Asynchronous Server Gateway Interface — Python async web sunucusu standardı. |
| **Cache** | Geçici bellek; sık erişilen veriyi hızlı sunmak için. |
| **CORS** | Cross-Origin Resource Sharing — farklı domain'den istek izni. |
| **CRUD** | Create, Read, Update, Delete — veritabanı temel işlemleri. |
| **CSS** | Cascading Style Sheets — web sayfası stil dili. |
| **DOM** | Document Object Model — HTML'in tarayıcıdaki programatik temsili. |
| **Endpoint** | API'deki belirli bir URL ve HTTP metod kombinasyonu. |
| **Enum** | Enumeration — sınırlı değer kümesi tanımlayan veri tipi. |
| **FastAPI** | Modern, hızlı Python web framework'ü. |
| **Fetch API** | Tarayıcının yerleşik HTTP istek API'si. |
| **Forex** | Foreign Exchange — döviz piyasası. |
| **HTTP** | HyperText Transfer Protocol — web istek protokolü. |
| **JSON** | JavaScript Object Notation — veri değişim formatı. |
| **PnL** | Profit and Loss — kar/zarar. |
| **Pydantic** | Python veri doğrulama kütüphanesi. |
| **pytest** | Python test framework'ü. |
| **REST** | Representational State Transfer — API mimari stili. |
| **Router** | FastAPI'de ilgili endpoint'leri gruplayan yapı. |
| **Schema** | Veritabanı veya API'deki veri yapısı tanımı. |
| **SQLite** | Sunucusuz, dosya tabanlı SQL veritabanı. |
| **Static Files** | Değişmeyen içerik (HTML, CSS, JS, resim). |
| **TTL** | Time To Live — cache'deki verinin geçerlilik süresi. |
| **Uvicorn** | Python ASGI sunucusu. |
| **Validation** | Verinin beklenen formata uygunluğunu kontrol etme. |
| **Vanilla JS** | Framework kullanılmayan pure JavaScript. |

---

## 21. İleri Adımlar / Önerilen Egzersizler

1. **Kullanıcı yönetimi ekle** → `users` tablosunu genişlet; giriş/çıkış (auth) sistemi kur. JWT token ile `user_id` dinamik hale getir.
2. **Tarihsel fiyat entegrasyonu** → Senaryo analizinde `hypothetical_date`'teki gerçek fiyatı çekmek için Yahoo Finance historical data API'sini kullan.
3. **WebSocket canlı fiyat akışı** → FastAPI `WebSocket` endpoint'i ile fiyatları frontend'e anlık gönder; sayfa yenilemeden güncelle.
4. **Grafik ekle** → `Chart.js` veya benzeri bir kütüphane ile portföy değeri zaman çizelgesi, çeşitlendirme pasta grafiği ekle.
5. **Daha fazla varlık türü** → Tahvil, emtia (altın, petrol) için yeni `AssetType` değerleri ve API entegrasyonları ekle.
6. **İşlem ücreti (komisyon)** → Al/sat işlemlerinde %0.1 komisyon kes; `execute_buy`/`execute_sell`'de `total * 0.001` kadar bakiyeden düş.
7. **Limit emirleri** → Piyasa emri yerine "X fiyatına düşerse al" mantığı ekle; arka planda periyodik kontrol.
8. **Dockerize et** → `Dockerfile` ve `docker-compose.yml` yaz; uygulamayı tek komutla çalıştırılabilir hale getir.
9. **Frontend framework'e geç** → Vanilla JS yerine Vue, React veya HTMX kullan; bileşen tabanlı yapıya geç.
10. **Test kapsamını artır** → Harici API çağrılarını `responses` veya `unittest.mock` ile mock'la; CI/CD pipeline'ına entegre et.

---

> Bu tutorial'ı okuduğunda InvestSim'in tüm katmanlarını anlamış oldun. Yeni bir özellik eklemek istediğinde:
> 1. Veritabanı şemasına ihtiyaç varsa → `backend/database.py`
> 2. API endpoint'i eklemek için → `backend/routers/*.py`
> 3. Veri doğrulama için → `backend/models/schemas.py`
> 4. Harici servis entegrasyonu için → `backend/services/*.py`
> 5. Frontend'de göstermek için → `frontend/*.html`, `frontend/js/*.js`
> 6. Test yazmak için → `tests/test_*.py`
>
> Başarılar!
