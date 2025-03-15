# Telegram Bot Shop

A lightweight Telegram bot for order processing using Aiogram, FastAPI, Redis, RabbitMQ and PostgreSQL.

## Features
- Accepts orders via Telegram bot
- Stores orders in PostgreSQL via FastAPI
- Processes orders asynchronously with Redis
- Sends notifications to users on order updates
- Admin panel for managing orders

## Tech Stack
- **Bot:** Aiogram (Python)
- **API:** FastAPI + SQLAdmin 
- **Database:** PostgreSQL
- **Message Broker:** RabbitMQ
- **Cache:** Redis

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/danielPashht/reseller_bot
cd reseller_backend
```

### 2. Set Up Environment Variables
Create a `.env` file and add following environment variables:
```
TG_SECRET, ADMIN_SECRET
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DB_NAME

RABBITMQ_USER
RABBITMQ_PASSWORD
RABBITMQ_HOST
RABBITMQ_PORT
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Services
- Use docker compose to run all services, provide .env for it:
- From /docker: `docker-compose --env-file ../.env up`

## API Endpoints
| Method | Endpoint           | Description |
|--------|--------------------|-------------|
| `GET`  | `/items/`          | Get all items |
| `GET`  | `/orders/` | Get all orders |
| `POST` | `/orders/` | Create a new order |

For requests provide header: `x-api-key: ADMIN_SECRET`

