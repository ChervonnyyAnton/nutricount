#!/bin/bash
# Telegram Bot Setup Script

set -e

echo "🤖 Nutrition Tracker - Telegram Bot Setup"
echo "========================================="

# Load environment variables
if [ -f .env ]; then
    source .env
else
    echo "❌ .env file not found. Please create it from .env.example"
    exit 1
fi

# Check required variables
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set in .env"
    exit 1
fi

if [ -z "$TELEGRAM_WEBHOOK_SECRET" ]; then
    echo "❌ TELEGRAM_WEBHOOK_SECRET not set in .env"
    exit 1
fi

# Get webhook URL
WEBHOOK_URL=${PRODUCTION_WEBHOOK_URL:-"https://your-domain.com/telegram/webhook"}
echo "📡 Webhook URL: $WEBHOOK_URL"

# Set webhook
echo "🔧 Setting Telegram webhook..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -H "Content-Type: application/json" \
  -d "{
    \"url\": \"$WEBHOOK_URL\",
    \"secret_token\": \"$TELEGRAM_WEBHOOK_SECRET\",
    \"allowed_updates\": [\"message\", \"web_app_data\"],
    \"drop_pending_updates\": true
  }")

# Check response
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Webhook set successfully!"
    echo "$RESPONSE" | jq .
else
    echo "❌ Failed to set webhook:"
    echo "$RESPONSE" | jq .
    exit 1
fi

# Get webhook info
echo ""
echo "📋 Current webhook info:"
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo" | jq .

# Set bot commands
echo ""
echo "⚙️ Setting bot commands..."
COMMANDS_RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setMyCommands" \
  -H "Content-Type: application/json" \
  -d '{
    "commands": [
      {"command": "start", "description": "🥗 Start nutrition tracking"},
      {"command": "help", "description": "❓ Get help and instructions"},
      {"command": "webapp", "description": "📱 Open Nutrition Tracker Web App"},
      {"command": "stats", "description": "📊 View daily statistics"},
      {"command": "log", "description": "📝 Quick log food entry"}
    ]
  }')

if echo "$COMMANDS_RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Bot commands set successfully!"
else
    echo "⚠️  Failed to set bot commands, but webhook is working"
fi

echo ""
echo "🎉 Telegram bot setup completed!"
echo ""
echo "Next steps:"
echo "1. Test your bot by sending /start"
echo "2. Add your bot to a group or use it privately"
echo "3. Use /webapp command to open the web app"
echo ""
echo "Bot username: @$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe" | jq -r '.result.username')"
