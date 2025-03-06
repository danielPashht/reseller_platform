# TODO: rewrite 

# Telegram Bot Shop

A lightweight Telegram bot for order processing using Aiogram, FastAPI, Celery, Redis, and PostgreSQL.

## Features
- Accepts orders via Telegram bot
- Stores orders in PostgreSQL via FastAPI
- Processes orders asynchronously with Celery
- Sends notifications to users on order updates
- Admin panel for managing orders

## Tech Stack
- **Bot:** Aiogram (Python)
- **API:** FastAPI + SQLAdmin 
- **Database:** PostgreSQL
- **Task Queue:** Celery
- **Message Broker:** Redis

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/shop_bot.git
cd reseller_backend
```

### 2. Set Up Environment Variables
Create a `.env` file and add:
```
BOT_TOKEN=your_telegram_bot_token
API_KEY=your_api_key
DB_URL=postgresql+asyncph://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Services
- **Run Redis:** `docker run -d -p 6379:6379 redis`
- **Run Postgresql:** `docker run -d -p 3306:3306 -e POSTGRESQL_PASSWORD=root postgres`
- **Run Celery Worker:** `celery -A tasks worker --loglevel=info`
- **Run FastAPI:** `uvicorn main:app --reload`
- **Run Telegram Bot:** `python bot.py`

## API Endpoints
| Method | Endpoint | Description |
|--------|---------|-------------|
| `POST` | `/orders/` | Create an order |
| `PUT` | `/orders/{order_id}` | Update order status |

## Order Flow
1. User places an order via Telegram bot.
2. FastAPI stores the order in MySQL.
3. Celery processes the order in the background.
4. Admin updates order status.
5. User gets notified in Telegram via Redis Pub/Sub or direct API call.
