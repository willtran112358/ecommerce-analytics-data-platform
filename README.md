# 🏪 Winmart Retail Analytics Platform

> Enterprise omnichannel retail analytics system for Winmart grocery chain with real-time POS, inventory optimization, demand forecasting, and supply chain intelligence.

Comprehensive omnichannel retail operations platform for Winmart grocery chain stores across Vietnam. Integrates real-time point-of-sale (POS), inventory management, customer analytics, and supply chain optimization to drive data-driven decisions across the store network.

## Overview

Enterprise retail analytics system purpose-built for Winmart grocery retail operations:
- Real-time POS transaction processing and reconciliation across all Winmart locations
- Multi-location inventory management with demand forecasting for grocery SKUs
- Customer segmentation and personalized offers for loyalty program members
- Store performance analytics and benchmarking across Winmart network
- Supply chain optimization and stock level predictions for perishables and dry goods
- Real-time shelf availability and out-of-stock alerts

## Tech Stack

- **Backend**: Python 3.10+ (FastAPI, SQLAlchemy)
- **Database**: PostgreSQL + TimescaleDB
- **Real-time**: Redis (caching), Kafka (event streaming)
- **Analytics**: dbt, Pandas, NumPy
- **ML**: Scikit-learn, LightGBM (forecasting)
- **Dashboard**: Streamlit + Plotly
- **Orchestration**: Airflow
- **Infrastructure**: Docker, Kubernetes, AWS S3
- **CI/CD**: GitHub Actions

## Architecture

```mermaid
flowchart TD
    subgraph SOURCES["📱 Data Sources"]
        A["🏪 Winmart POS<br/>Transaction Streams"]
        C["📦 Inventory<br/>Sensors"]
        D["🌐 External APIs<br/>Weather/Pricing"]
    end
    
    subgraph STREAM["⚡ Real-time Stream"]
        B["Kafka Event Stream<br/>Transaction Topics"]
    end
    
    subgraph LAYERS["🏗️ Data Medallion"]
        F["🔵 Bronze<br/>Raw Transactions<br/>Immutable Log"]
        G["🟢 Silver<br/>Cleaned & Validated<br/>Deduplicated"]
        H["⭐ Gold<br/>Aggregated KPIs<br/>ML Features"]
    end
    
    subgraph ANALYTICS["📊 Analytics & ML"]
        I["dbt Models<br/>Staging • Marts"]
        J["📈 Analytics Engine<br/>SQL Views"]
        L["🤖 ML Models<br/>LightGBM"]
    end
    
    subgraph OUTPUTS["🎯 Outputs"]
        K["📱 Streamlit<br/>Dashboards"]
        M["🔮 Demand<br/>Forecasting"]
        N["💡 Smart<br/>Recommendations"]
    end
    
    subgraph CONSUMERS["👥 Stakeholders"]
        O["👔 Store Managers"]
        P["🚚 Supply Chain"]
        Q["📢 Marketing Team"]
    end
    
    A --> B
    C --> B
    D --> B
    
    B --> F
    F --> G
    G --> H
    
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

## Key Modules

| Module | Description |
|--------|-------------|
| **POS Processing** | Transaction validation, reconciliation, payment processing |
| **Inventory Management** | Stock tracking, SKU management, reorder optimization |
| **Demand Forecasting** | Sales prediction per store/SKU with confidence intervals |
| **Customer Analytics** | Segment analysis, RFM scoring, purchase patterns |
| **Supply Chain** | Replenishment planning, optimal stock levels, warehouse allocation |
| **Store Performance** | KPI tracking, sales analysis, staff productivity metrics |

## Project Structure

```
retail/
├── data/
│   ├── samples/          # Sample transaction data
│   └── schemas/          # Data schema definitions
├── src/
│   ├── pos/
│   │   ├── transaction.py    # Transaction processing
│   │   ├── reconciler.py     # Daily reconciliation
│   │   └── validator.py      # Data validation
│   ├── inventory/
│   │   ├── manager.py        # Inventory operations
│   │   ├── reorder.py        # Reorder optimization
│   │   └── sku.py            # SKU management
│   ├── forecasting/
│   │   ├── demand.py         # Demand forecasting
│   │   ├── models.py         # ML models
│   │   └── evaluator.py      # Model evaluation
│   ├── analytics/
│   │   ├── customer.py       # Customer analytics
│   │   ├── store.py          # Store performance
│   │   └── metrics.py        # KPI calculations
│   ├── api/
│   │   ├── app.py            # FastAPI application
│   │   ├── routes.py         # API endpoints
│   │   └── schemas.py        # Request/response schemas
│   ├── stream/
│   │   ├── consumer.py       # Kafka consumer
│   │   └── processor.py      # Stream processing
│   └── dashboards/
│       ├── app.py            # Streamlit entry
│       └── pages/            # Dashboard pages
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   └── tests/
├── airflow/
│   └── dags/
├── tests/
├── docker-compose.yml
├── requirements.txt
└── .github/workflows/
```

## Sales Forecasting (VinMart / Winmart)

Store × SKU daily unit forecasts with **90% confidence intervals** via `SalesForecastPipeline` (LightGBM default, RandomForest fallback):

```bash
python scripts/demo_forecast.py
```

```python
from forecasting import SalesForecastPipeline
import pandas as pd

daily = pd.read_csv("data/samples/daily_sales_sample.csv", parse_dates=["date"])
pipe = SalesForecastPipeline(backend="lightgbm")
pipe.fit(daily)
forecast_df = pipe.to_dataframe(pipe.predict_horizon(daily, horizon_days=7))
```

## Quick Start

### Setup

```bash
git clone https://github.com/willtran112358/ecommerce-analytics-data-platform.git
cd ecommerce-analytics-data-platform

# Create environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

### Run Services

```bash
# Start Docker containers
docker-compose up -d

# Initialize database
python src/pos/setup_db.py

# Run data models
cd dbt && dbt run && cd ..

# Start API server
uvicorn src.api.app:app --reload

# Launch dashboard
streamlit run src/dashboards/app.py
```

### Example Usage

```python
from src.pos.transaction import TransactionProcessor
from src.inventory.manager import InventoryManager

# Process Winmart transaction
processor = TransactionProcessor()
result = processor.process_transaction({
    "store_id": "WINMART_HCM_001",  # Winmart store in Ho Chi Minh City
    "transaction_id": "TXN_20240513_12345",
    "items": [
        {"sku": "WM_RICE_01", "quantity": 2, "price": 89.99},  # Rice
        {"sku": "WM_MILK_02", "quantity": 1, "price": 45.50}   # Dairy
    ],
    "timestamp": "2024-05-13T10:30:00Z",
    "payment_method": "cash"
})

# Update Winmart store inventory
inv_manager = InventoryManager()
inv_manager.adjust_stock("WINMART_HCM_001", "WM_RICE_01", -2)
inv_manager.adjust_stock("WINMART_HCM_001", "WM_MILK_02", -1)
```

## API Endpoints

```
GET  /stores                          # List all Winmart store locations
GET  /stores/{store_id}/inventory     # Get Winmart store inventory
GET  /stores/{store_id}/performance   # Winmart store KPIs and metrics
POST /transactions                    # Record POS transaction
GET  /analytics/forecast              # Demand forecast across Winmart network
GET  /analytics/planogram             # Shelf optimization for Winmart stores
GET  /customers/{id}/analytics        # Loyalty customer analytics
GET  /supply-chain/replenishment      # Replenishment recommendations
```

## Performance

- POS transaction processing: <100ms
- Dashboard refresh: Real-time
- Demand forecast latency: ~5 minutes (daily retraining)
- API p95 latency: <200ms

## Testing

```bash
pytest tests/ -v
pytest tests/integration/ --markers integration
```

## Contributing

1. Fork repository
2. Create feature branch
3. Implement changes + tests
4. Submit pull request

## License

MIT License

## Author

**WillTran** — [@willtran112358](https://github.com/willtran112358)
