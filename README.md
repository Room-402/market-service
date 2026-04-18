# Market Service

A FastAPI-based microservice that provides **Market Item CRUD** operations and **live Nifty 50 stock data** from the National Stock Exchange (NSE) via Yahoo Finance.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Tech Stack](#tech-stack)

---

## Prerequisites

- **Python 3.10+** — [Download](https://www.python.org/downloads/)
- **pip** — comes bundled with Python
- **Git** — to clone the repository

---

## Quick Start

```bash
git clone <repository-url>
cd market-service
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The server will be available at **http://127.0.0.1:8000**. See below for detailed steps.

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd market-service
```

### 2. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 3. Activate the Virtual Environment

| OS            | Command                        |
| ------------- | ------------------------------ |
| **macOS / Linux** | `source .venv/bin/activate`    |
| **Windows**       | `.venv\Scripts\activate`       |

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Verify Installation

```bash
python -c "import fastapi; print(f'FastAPI {fastapi.__version__} installed successfully')"
```

### 6. Deactivate the Virtual Environment (when done)

```bash
deactivate
```

> **Important:** You must **re-activate** the virtual environment (`source .venv/bin/activate`) every time you open a new terminal session before running the server.

---

## Configuration

The service uses **environment variables** for configuration (loaded via `pydantic-settings`).

Create a `.env` file in the project root (optional — sensible defaults are provided):

```env
APP_NAME=Market Service
APP_VERSION=1.0.0
DEBUG=False
```

| Variable        | Default            | Description                          |
| --------------- | ------------------ | ------------------------------------ |
| `APP_NAME`      | `Market Service`   | Name shown in docs & health check    |
| `APP_VERSION`   | `1.0.0`            | API version string                   |
| `DEBUG`         | `False`            | Enable/disable debug mode            |

---

## Running the Server

> **Prerequisite:** Make sure the virtual environment is activated before running any commands below.
>
> ```bash
> source .venv/bin/activate      # macOS / Linux
> .venv\Scripts\activate          # Windows
> ```

### Development (with auto-reload)

```bash
uvicorn main:app --reload
```

The server starts at **http://127.0.0.1:8000** by default.

### Custom Host & Port

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Verify the Server is Running

Open your browser or use `curl`:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{
  "status": "ok",
  "service": "Market Service"
}
```

### Interactive API Docs

FastAPI auto-generates interactive documentation:

| Docs         | URL                                      |
| ------------ | ---------------------------------------- |
| **Swagger UI** | http://127.0.0.1:8000/docs             |
| **ReDoc**      | http://127.0.0.1:8000/redoc            |

---

## Project Structure

```
market-service/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (optional)
├── .watchfilesignore                # Files ignored by watchfiles (reload)
└── app/
    ├── __init__.py
    ├── core/
    │   ├── config.py                # Settings via pydantic-settings
    │   └── constants.py             # Nifty 50 ticker symbols
    ├── api/
    │   └── v1/
    │       └── routes/
    │           ├── market.py        # Market item CRUD endpoints
    │           └── stock.py         # Stock / Nifty 50 endpoints
    ├── schemas/
    │   ├── market.py                # Market item Pydantic models
    │   └── stock.py                 # Stock data Pydantic models
    ├── services/
    │   ├── market_service.py        # Market business logic
    │   └── stock_service.py         # Stock data fetching & caching
    └── repositories/
        ├── market_repository.py     # In-memory market item store
        └── stock_repository.py      # NSE CSV data fetcher
```

---

## API Reference

### Health Check

| Method | Endpoint | Description             |
| ------ | -------- | ----------------------- |
| `GET`  | `/`      | Returns service status  |

---

### Markets — `/api/v1/markets`

| Method   | Endpoint                  | Description                 |
| -------- | ------------------------- | --------------------------- |
| `GET`    | `/api/v1/markets/`        | List all market items       |
| `GET`    | `/api/v1/markets/{id}`    | Get a single item by ID     |
| `POST`   | `/api/v1/markets/`        | Create a new market item    |
| `DELETE` | `/api/v1/markets/{id}`    | Delete an item by ID        |

#### Create Item — Request Body

```json
{
  "name": "Tomato",
  "price": 45.50,
  "quantity": 100
}
```

#### Create Item — Response `201`

```json
{
  "id": 1,
  "name": "Tomato",
  "price": 45.50,
  "quantity": 100
}
```

> **Note:** Market items are stored **in-memory** and will be lost on server restart.

---

### Stocks — `/api/v1/stocks`

| Method | Endpoint                | Description                           |
| ------ | ----------------------- | ------------------------------------- |
| `GET`  | `/api/v1/stocks/nifty50` | Fetch live Nifty 50 stock data       |

#### Nifty 50 — Response `200`

```json
{
  "stocks": [
    {
      "symbol": "RELIANCE",
      "company_name": "Reliance Industries Limited",
      "price": 2945.30,
      "change": 12.50
    }
  ]
}
```

> **Note:** Stock data is fetched live from Yahoo Finance and cached for **10 minutes** via an in-memory TTL cache.

---

## Tech Stack

| Technology                                                      | Purpose                          |
| --------------------------------------------------------------- | -------------------------------- |
| [FastAPI](https://fastapi.tiangolo.com/)                        | Web framework                    |
| [Uvicorn](https://www.uvicorn.org/)                             | ASGI server                      |
| [Pydantic](https://docs.pydantic.dev/)                          | Data validation & serialization  |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | Environment config management |
| [yfinance](https://github.com/ranaroussi/yfinance)              | Yahoo Finance stock data         |
| [cachetools](https://cachetools.readthedocs.io/)                 | In-memory TTL caching            |
| [httpx](https://www.python-httpx.org/)                           | Async HTTP client (NSE CSV)      |
