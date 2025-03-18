# Telegram Bot Shop

Shop based on Telegram bot, made for async order processing, with admin panel for managing orders and items.

## Features
- Accepts orders via Telegram bot
- Stores orders in PostgreSQL via FastAPI
- Processes orders asynchronously with Redis
- Sends notifications to users on order updates
- Admin panel for managing orders

## Tech Stack
- **Bot:** Aiogram
- **API:** FastAPI + SQLAdmin for managing orders and items
- **Database:** PostgreSQL, stores orders and items
- **Message Broker:** RabbitMQ, for asynchronous processing of orders and item updates
- **Cache:** Redis, for storing user sessions

## Installation
### 1. Clone the Repository
```bash
git clone https://github.com/danielPashht/reseller_bot
open repo in IDE or terminal
```

### 2. Set Up Environment Variables
Create a `.env` in root file and add following environment variables:
```
TG_SECRET - used by bot to authenticate requests in backend
ADMIN_SECRET - used by admin panel to authenticate admin user
DB_USER
DB_PASSWORD
DB_HOST
DB_PORT
DB_NAME

RABBITMQ_USER
RABBITMQ_PASSWORD
RABBITMQ_HOST
RABBITMQ_PORT
BOT_TOKEN - telegram bot token from BotFather
ADMIN_API_URL - url to admin panel, for example: http://reseller_backend:8000
MANAGER_USER_ID - telegram userid of manager to receive notifications 
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Start Services
- Use docker compose to run all services, provide .env for it:
- From /docker: `docker-compose --env-file=.env up`

## API Endpoints
| Method | Endpoint           | Description |
|--------|--------------------|-------------|
| `GET`  | `/items/`          | Get all items |
| `GET`  | `/orders/` | Get all orders |
| `POST` | `/orders/` | Create a new order |

For requests provide header: `x-api-key: ADMIN_SECRET`

