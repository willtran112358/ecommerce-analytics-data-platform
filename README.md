# 🏪 Winmart Retail Analytics Platform

> Nền tảng phân tích bán lẻ đa kênh cho **Winmart**: **POS**, tồn kho, **demand forecasting** (`LightGBM`), chuỗi cung ứng.

**Repo demo:** `transaction.py` · `inventory.py` · `forecasting.py` · `scripts/demo_forecast.py`

## Bài toán

OOS, tồn cao (đặc biệt perishables), forecast Excel khó scale, lệch **POS**–tồn, khuyến mãi/giá đối thủ khó đo. Hệ thống chuẩn hóa dữ liệu và dự báo theo `store_id` × `SKU` có khoảng tin cậy.

## KPI chính

| KPI | Định nghĩa |
|-----|------------|
| **revenue** | Doanh thu từ `POS` |
| **units sold** | Bán theo ngày × cửa hàng × `SKU` |
| **OOS rate** | % `SKU` tồn = 0 |
| **MAPE** | Sai số forecast vs thực tế |
| **days of supply** | Tồn ÷ bán TB ngày |

## Tech Stack

`Python 3.10+` · `FastAPI` · `PostgreSQL` / `TimescaleDB` · `Redis` · `Kafka` · `dbt` · `LightGBM` · `Streamlit` · `Airflow` · `Docker` · `GitHub Actions`

## Kiến trúc

```mermaid
flowchart TD
    subgraph SOURCES["📱 Nguồn dữ liệu"]
        A["🏪 Winmart POS<br/>Luồng giao dịch"]
        C["📦 Inventory<br/>Cảm biến / ERP"]
        D["🌐 External APIs<br/>Thời tiết / Giá"]
    end

    subgraph STREAM["⚡ Real-time Stream"]
        B["Kafka Event Stream<br/>Transaction Topics"]
    end

    subgraph LAYERS["🏗️ Data Medallion"]
        F["🔵 Bronze<br/>Raw Transactions"]
        G["🟢 Silver<br/>Cleaned & Validated"]
        H["⭐ Gold<br/>KPIs & ML Features"]
    end

    subgraph ANALYTICS["📊 Analytics & ML"]
        I["dbt Models<br/>staging • marts"]
        J["📈 Analytics Engine<br/>SQL Views"]
        L["🤖 ML Models<br/>LightGBM"]
    end

    subgraph OUTPUTS["🎯 Đầu ra"]
        K["📱 Streamlit<br/>Dashboards"]
        M["🔮 Demand<br/>Forecasting"]
        N["💡 Smart<br/>Recommendations"]
    end

    subgraph CONSUMERS["👥 Stakeholder"]
        O["👔 Quản lý cửa hàng"]
        P["🚚 Supply Chain"]
        Q["📢 Marketing"]
    end

    A --> B
    C --> B
    D --> B
    B --> F --> G --> H
    H --> I
    H --> J
    H --> L
    I --> K
    J --> K
    L --> M
    L --> N
    K --> O
    M --> P
    N --> Q

    style SOURCES fill:#ffe6cc,stroke:#ff9900,stroke-width:2px
    style STREAM fill:#cce5ff,stroke:#0066cc,stroke-width:2px
    style LAYERS fill:#ccffcc,stroke:#00cc00,stroke-width:2px
    style ANALYTICS fill:#ffffcc,stroke:#ffcc00,stroke-width:2px
    style OUTPUTS fill:#ffccff,stroke:#cc00cc,stroke-width:2px
    style CONSUMERS fill:#ffcccc,stroke:#cc0000,stroke-width:2px
```

```mermaid
flowchart TB
    POS["POS bán hàng<br/>transaction.py"]
    INV["Cập nhật tồn<br/>inventory.py"]
    AGG["Tổng hợp bán theo ngày<br/>store × SKU"]
    FC["SalesForecastPipeline<br/>forecasting.py"]
    DEC["Quyết định đặt hàng<br/>& khuyến mãi"]

    POS --> INV
    POS --> AGG
    AGG --> FC
    FC --> DEC

    style POS fill:#e3f2fd,stroke:#1565c0
    style INV fill:#e8f5e9,stroke:#2e7d32
    style FC fill:#fff3e0,stroke:#ef6c00
    style DEC fill:#fce4ec,stroke:#c2185b
```

## Module

| Module | File |
|--------|------|
| POS | `transaction.py` |
| Inventory | `inventory.py` |
| Forecasting | `forecasting.py` |

## Cấu trúc repo

```
├── data/samples/daily_sales_sample.csv
├── scripts/demo_forecast.py
├── tests/
├── forecasting.py · inventory.py · transaction.py
└── requirements.txt
```

## Quick Start

```bash
git clone https://github.com/willtran112358/ecommerce-analytics-data-platform.git
cd ecommerce-analytics-data-platform
python -m venv venv && venv\Scripts\activate   # Windows
pip install -r requirements.txt
python scripts/demo_forecast.py
pytest tests/ -v
```

## API (production target)

`GET /stores` · `GET /stores/{store_id}/inventory` · `GET /stores/{store_id}/performance` · `POST /transactions` · `GET /analytics/forecast` · `GET /supply-chain/replenishment`

---

**Will Tran** — [@willtran112358](https://github.com/willtran112358)
