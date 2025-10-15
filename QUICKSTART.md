# 🚦 QUICKSTART.md

## Quickstart for Nutrition Tracker v2.0


***

### 🐳 1. Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed (recommended)
- `git`, `curl`, and a browser

***

### 🍏 2. Get the code

```sh
git clone https://github.com/your-username/nutrition-tracker.git
cd nutrition-tracker
```


***

### ⚙️ 3. Configure

```sh
cp .env.example .env
# Edit .env with your PostgreSQL, Telegram and desired production settings
```

- At minimum set:  SECRET_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET

***

### 🚀 4. Start (Docker)

```sh
./scripts/quickstart.sh
```

- Or manually:

```sh
docker-compose -f docker-compose.telegram.yml up --build -d
```

- Check health:

```sh
curl http://localhost:5000/health
```


***

### 🌐 5. Open the app

Open http://localhost:5000 in your browser

***

### 🤖 6. Telegram Configuration

- Register your bot with @BotFather, copy TELEGRAM_BOT_TOKEN
- Set webhook URL via GitHub Actions (or manually: `/setWebhook` endpoint)

***

### 🧑‍💻 7. Development mode

```sh
make dev-setup
make run
```

- Hot reload with `docker-compose.override.yml` or use Flask dev server for rapid prototyping.

***

### 🛠️ 8. Admin Panel

- Ctrl+Alt+A or Triple-click page title for admin panel (backups, stats, export).
- Alt+1,2,3,N,S,B for keyboard shortcuts.

***

### 📋 9. Testing \& CI

```sh
make test
make lint
make format
```

- For full CI: push to develop/main and check Actions tab.

***

### 🛡️ 10. Notes

- For HTTPS, use Nginx + Let’s Encrypt; see `nginx.telegram.conf`.
- For production volumes: `data/`, `backups/`, `logs/`.
- Customize themes via `static/css/final-polish.css`.
- All documentation is available as Markdown in the project root and `docs/`.

***

**You’re ready! 🥗 Enjoy tracking, stay healthy, build securely!**

***