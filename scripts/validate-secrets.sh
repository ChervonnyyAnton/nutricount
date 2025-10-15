#!/bin/bash
# Validate GitHub Secrets Configuration
# Usage: ./scripts/validate-secrets.sh

set -e

echo "🔐 Validating GitHub Secrets Configuration..."
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Required secrets for basic functionality
REQUIRED_SECRETS=(
    "SECRET_KEY"
    "TELEGRAM_BOT_TOKEN"
    "TELEGRAM_WEBHOOK_SECRET"
)

# Optional but recommended secrets
RECOMMENDED_SECRETS=(
    "TELEGRAM_BOT_TOKEN_STAGING"
    "PROD_HOST"
    "STAGING_HOST"
    "DOMAIN_NAME"
    "CERTBOT_EMAIL"
    "GRAFANA_PASSWORD"
)

# Production deployment secrets
PRODUCTION_SECRETS=(
    "PROD_USER"
    "PROD_SSH_KEY"
    "PRODUCTION_WEBHOOK_URL"
    "PRODUCTION_URL"
)

# Staging deployment secrets
STAGING_SECRETS=(
    "STAGING_USER"
    "STAGING_SSH_KEY"
    "STAGING_WEBHOOK_URL"
)

echo "📋 Checking configuration..."
echo ""

# Function to check if a secret looks valid
check_secret_format() {
    local secret_name=$1
    local secret_value=$2
    
    case $secret_name in
        "SECRET_KEY")
            if [ ${#secret_value} -lt 32 ]; then
                echo -e "${YELLOW}⚠️  WARNING: SECRET_KEY should be at least 32 characters${NC}"
            fi
            ;;
        "TELEGRAM_BOT_TOKEN"|"TELEGRAM_BOT_TOKEN_STAGING")
            if [[ ! $secret_value =~ ^[0-9]+:[a-zA-Z0-9_-]+$ ]]; then
                echo -e "${YELLOW}⚠️  WARNING: $secret_name format may be invalid${NC}"
            fi
            ;;
        "TELEGRAM_WEBHOOK_SECRET")
            if [ ${#secret_value} -lt 16 ]; then
                echo -e "${YELLOW}⚠️  WARNING: TELEGRAM_WEBHOOK_SECRET should be at least 16 characters${NC}"
            fi
            ;;
        "*_URL")
            if [[ ! $secret_value =~ ^https:// ]]; then
                echo -e "${YELLOW}⚠️  WARNING: $secret_name should use HTTPS${NC}"
            fi
            ;;
    esac
}

# Check required secrets
echo -e "${BLUE}Required Secrets:${NC}"
missing_required=0
for secret in "${REQUIRED_SECRETS[@]}"; do
    if [ -n "${!secret}" ]; then
        echo -e "  ${GREEN}✅ $secret${NC} - configured"
        check_secret_format "$secret" "${!secret}"
    else
        echo -e "  ${RED}❌ $secret${NC} - MISSING (required for basic functionality)"
        missing_required=$((missing_required + 1))
    fi
done

# Check recommended secrets
echo ""
echo -e "${BLUE}Recommended Secrets:${NC}"
missing_recommended=0
for secret in "${RECOMMENDED_SECRETS[@]}"; do
    if [ -n "${!secret}" ]; then
        echo -e "  ${GREEN}✅ $secret${NC} - configured"
        check_secret_format "$secret" "${!secret}"
    else
        echo -e "  ${YELLOW}⚠️  $secret${NC} - missing (recommended for full functionality)"
        missing_recommended=$((missing_recommended + 1))
    fi
done

# Check production secrets
echo ""
echo -e "${BLUE}Production Deployment Secrets:${NC}"
missing_production=0
for secret in "${PRODUCTION_SECRETS[@]}"; do
    if [ -n "${!secret}" ]; then
        echo -e "  ${GREEN}✅ $secret${NC} - configured"
        check_secret_format "$secret" "${!secret}"
    else
        echo -e "  ${YELLOW}⚠️  $secret${NC} - missing (needed for production deployment)"
        missing_production=$((missing_production + 1))
    fi
done

# Check staging secrets
echo ""
echo -e "${BLUE}Staging Deployment Secrets:${NC}"
missing_staging=0
for secret in "${STAGING_SECRETS[@]}"; do
    if [ -n "${!secret}" ]; then
        echo -e "  ${GREEN}✅ $secret${NC} - configured"
        check_secret_format "$secret" "${!secret}"
    else
        echo -e "  ${YELLOW}⚠️  $secret${NC} - missing (needed for staging deployment)"
        missing_staging=$((missing_staging + 1))
    fi
done

# Summary
echo ""
echo "📊 Summary:"
echo "==========="
echo -e "Required secrets missing: ${RED}$missing_required${NC}"
echo -e "Recommended secrets missing: ${YELLOW}$missing_recommended${NC}"
echo -e "Production secrets missing: ${YELLOW}$missing_production${NC}"
echo -e "Staging secrets missing: ${YELLOW}$missing_staging${NC}"

# Check .env file
echo ""
echo -e "${BLUE}Environment File Check:${NC}"
if [ -f .env ]; then
    echo -e "  ${GREEN}✅ .env file exists${NC}"
    
    # Check if .env has required variables
    env_missing=0
    while IFS= read -r secret; do
        if ! grep -q "^${secret}=" .env; then
            echo -e "  ${YELLOW}⚠️  $secret not found in .env${NC}"
            env_missing=$((env_missing + 1))
        fi
    done <<< "$(printf '%s\n' "${REQUIRED_SECRETS[@]}")"
    
    if [ $env_missing -eq 0 ]; then
        echo -e "  ${GREEN}✅ All required variables found in .env${NC}"
    fi
else
    echo -e "  ${RED}❌ .env file not found${NC}"
    echo -e "  ${BLUE}💡 Run: cp .env.example .env${NC}"
fi

# Check GitHub repository secrets (if in GitHub Actions)
if [ -n "$GITHUB_ACTIONS" ]; then
    echo ""
    echo -e "${BLUE}GitHub Actions Environment:${NC}"
    echo -e "  ${GREEN}✅ Running in GitHub Actions${NC}"
    echo -e "  ${BLUE}ℹ️  Secret values are masked in logs${NC}"
fi

# Generate commands to set missing secrets
if [ $missing_required -gt 0 ] || [ $missing_recommended -gt 0 ]; then
    echo ""
    echo -e "${BLUE}Quick Setup Commands:${NC}"
    echo "======================"
    echo ""
    echo "# Generate a secure secret key:"
    echo "python3 -c \"import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))\""
    echo ""
    echo "# Generate webhook secret:"
    echo "python3 -c \"import secrets; print('TELEGRAM_WEBHOOK_SECRET=' + secrets.token_urlsafe(16))\""
    echo ""
    echo "# Create Telegram bot:"
    echo "# 1. Message @BotFather on Telegram"
    echo "# 2. Send /newbot and follow instructions"
    echo "# 3. Copy the bot token to TELEGRAM_BOT_TOKEN"
    echo ""
    echo "# Set up domain:"
    echo "# 1. Point your domain to your server"
    echo "# 2. Set DOMAIN_NAME=your-domain.com"
    echo "# 3. Set CERTBOT_EMAIL=your-email@domain.com"
fi

# Final status
echo ""
if [ $missing_required -eq 0 ]; then
    echo -e "${GREEN}🎉 Basic configuration is complete!${NC}"
    echo -e "${BLUE}ℹ️  You can run the application locally${NC}"
    
    if [ $missing_production -eq 0 ] && [ $missing_staging -eq 0 ]; then
        echo -e "${GREEN}🚀 Production deployment ready!${NC}"
    elif [ $missing_production -gt 0 ] || [ $missing_staging -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Some deployment secrets missing${NC}"
        echo -e "${BLUE}ℹ️  Configure them for automated deployments${NC}"
    fi
else
    echo -e "${RED}❌ Configuration incomplete${NC}"
    echo -e "${BLUE}ℹ️  Configure required secrets to run the application${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📚 For detailed setup instructions, see:${NC}"
echo -e "${BLUE}   • GITHUB_SECRETS.md${NC}"
echo -e "${BLUE}   • QUICKSTART.md${NC}"
echo -e "${BLUE}   • README.md${NC}"
