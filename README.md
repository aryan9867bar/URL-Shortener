# 🔗 URL Shortener

A high-performance URL shortening service built with **FastAPI**, **PostgreSQL**, and **Redis**. It uses Snowflake IDs for unique code generation and Base62 encoding to produce compact, collision-free short codes. Redis is used as a caching layer with a distributed lock mechanism to prevent cache stampedes.

---

## 🏗️ Architecture

```
Client → FastAPI → Redis Cache (hit) → Return URL
                 → Redis Cache (miss) → PostgreSQL → Cache result → Return URL
```

- **FastAPI** — Async REST API framework
- **PostgreSQL** — Persistent storage for URL mappings
- **Redis** — In-memory caching with TTL + distributed locking
- **Snowflake ID** — Globally unique, time-sortable numeric IDs
- **Base62** — Compact alphanumeric short codes

---

## 📋 Prerequisites

- Python 3.10+
- Docker & Docker Compose (for PostgreSQL and Redis)
- `pip`

---

## 🚀 Quick Start

### Step 1 — Clone / Extract the project

```bash
# If you have the zip:
unzip URL-Shortener-main.zip
cd URL-Shortener-main
```

### Step 2 — Start PostgreSQL and Redis via Docker

```bash
docker-compose up -d
```

This starts:
- PostgreSQL on `localhost:5432` (db: `url_shortener`, user: `postgres`, password: `password`)
- Redis on `localhost:6379`

Verify containers are running:
```bash
docker-compose ps
```

### Step 3 — Create a virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Step 4 — Configure environment variables

The `.env.local` file is already included with defaults for local development:

```env
ENV=local
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/url_shortener
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_SSL=false
```

Edit this file if your PostgreSQL or Redis credentials differ.

### Step 5 — Create database tables

```bash
python db.py
```

You should see:
```
✅ Tables created successfully.
```

```bash
# list all databases
psql -h localhost -U postgres -p 5432 -l

# connect to your DB
psql -h localhost -U postgres -p 5432 -d url_shortener

# list tables
\dt
```

### Step 6 — Run the server

```bash
uvicorn main:app --reload
```

The API is now running at **http://127.0.0.1:8000**

Interactive API docs: **http://127.0.0.1:8000/docs**

---

## 📡 API Endpoints

### `POST /shorten` — Shorten a URL

**Request:**
```bash
curl -X POST http://127.0.0.1:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/some/very/long/path"}'
```

**Response:**
```json
{
  "message": "Short URL created",
  "code": "aB3xZ9",
  "url": "https://www.example.com/some/very/long/path"
}
```

---

### `GET /{code}` — Resolve a short code

**Request:**
```bash
curl http://127.0.0.1:8000/aB3xZ9
```

**Response:**
```json
{
  "message": "Cache HIT",
  "url": "https://www.example.com/some/very/long/path"
}
```

---

## ⚙️ Rate Limits

| Endpoint    | Limit       |
|-------------|-------------|
| `POST /shorten` | 1 req/second |
| `GET /{code}`   | 5 req/second |

---

## 🗂️ Project Structure

```
URL-Shortener-main/
├── main.py            # FastAPI app, route handlers
├── config.py          # Environment settings via pydantic-settings
├── db.py              # Async SQLAlchemy engine + session factory
├── models.py          # SQLAlchemy ORM model + Pydantic request model
├── redis_client.py    # Redis connection
├── utils.py           # Base62 encoding utility
├── init_db.py         # One-time DB table creation script
├── docker-compose.yml # PostgreSQL + Redis services
├── requirements.txt   # Python dependencies
└── .env.local         # Local environment variables
```

---

## 🛑 Stopping the Services

```bash
# Stop Docker containers
docker-compose down

# To also remove the database volume (wipes all data)
docker-compose down -v
```

---

## 🌐 Production Deployment Notes

For production, update `.env.local` (or set real environment variables):

```env
ENV=prod
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<dbname>
REDIS_HOST=<your-redis-host>
REDIS_PORT=6380
REDIS_USERNAME=<your-redis-username>
REDIS_PASSWORD=<your-redis-password>
REDIS_SSL=true
```

Run without `--reload` in production:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 🧰 Troubleshooting

| Problem | Solution |
|---|---|
| `Connection refused` on PostgreSQL | Ensure Docker containers are running: `docker-compose ps` |
| `Redis connection error` | Check Redis is up: `docker exec -it url_shortener_redis redis-cli ping` |
| `ModuleNotFoundError` | Make sure your venv is activated and `pip install -r requirements.txt` ran successfully |
| Port already in use | Stop conflicting services or change the port in `docker-compose.yml` |
