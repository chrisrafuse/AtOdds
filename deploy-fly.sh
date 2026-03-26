#!/usr/bin/env bash
# Deploy AtOdds to Fly.io from your local machine or a private GitHub repo.
#
# Prerequisites:
#   1. Install flyctl: https://fly.io/docs/hands-on/install-flyctl/
#      curl -L https://fly.io/install.sh | sh
#   2. fly auth login
#   3. Copy .env.example to .env and fill in your API keys
#
# Usage:
#   First deploy:  ./deploy-fly.sh --launch
#   Re-deploy:     ./deploy-fly.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 AtOdds — Fly.io Deployment"
echo "================================"

# Check flyctl is installed
if ! command -v fly &>/dev/null; then
    echo "❌ flyctl not found. Install: curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Load .env if present
ENV_FILE="$REPO_ROOT/.env"
if [[ -f "$ENV_FILE" ]]; then
    echo "📄 Loading .env variables..."
    set -o allexport
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +o allexport
fi

# First launch: create the app and set fly.toml
if [[ "${1:-}" == "--launch" ]]; then
    echo "🔧 Launching new Fly.io app..."
    fly launch --no-deploy --copy-config --name atodds
fi

# Push secrets to Fly.io from .env
echo "🔐 Setting secrets on Fly.io..."

[[ -n "${LLM_PROVIDER:-}" ]] && fly secrets set "LLM_PROVIDER=${LLM_PROVIDER}"

if [[ -n "${OPENAI_API_KEY:-}" && "${OPENAI_API_KEY}" != "sk-..." ]]; then
    fly secrets set "OPENAI_API_KEY=${OPENAI_API_KEY}"
    echo "  ✓ OPENAI_API_KEY set"
fi

if [[ -n "${ANTHROPIC_API_KEY:-}" && "${ANTHROPIC_API_KEY}" != "sk-ant-..." ]]; then
    fly secrets set "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
    echo "  ✓ ANTHROPIC_API_KEY set"
fi

if [[ -n "${GEMINI_API_KEY:-}" && "${GEMINI_API_KEY}" != "AI..." ]]; then
    fly secrets set "GEMINI_API_KEY=${GEMINI_API_KEY}"
    echo "  ✓ GEMINI_API_KEY set"
fi

echo "📦 Deploying to Fly.io..."
fly deploy --remote-only

echo ""
echo "✅ Deployment complete!"
echo "   View logs:  fly logs"
echo "   Open app:   fly open"
echo "   Status:     fly status"
