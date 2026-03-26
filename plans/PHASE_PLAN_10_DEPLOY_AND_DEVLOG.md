# PHASE_PLAN_10_DEPLOY_AND_DEVLOG.md
## Author: Chris Rafuse
## Phase: 10 — Deployment + DEVLOG Rewrite
## Entry Criteria: Phases 8 + 9 complete (LLM agent, math, rankings all working)
## Exit Criteria: Live deployed URL, final DEVLOG.md written

---

# 🎯 PHASE OBJECTIVES

1. **Deploy** the AtOdds app to a public URL (Railway primary, Fly.io fallback)
2. **DEVLOG.md** rewritten to reflect actual development journey including AI tool usage, prompt iterations, and tradeoffs — this is 20% of the assignment grade

This phase is documentation + ops, not new features. Every step here is a deliverable the reviewers will inspect directly.

---

# PART 1: DEPLOYMENT

## Target Platform: Railway (Primary)

Railway is the simplest path for a Python FastAPI app: connects to GitHub, auto-builds, auto-deploys.

### Files to Create

#### `railway.toml`
```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "python apps/web/run_api.py"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

#### `Procfile`
```
web: python apps/web/run_api.py
```

#### `nixpacks.toml`
```toml
[phases.setup]
nixPkgs = ["python313"]

[phases.install]
cmds = ["pip install -r requirements.txt -r requirements-web.txt"]

[start]
cmd = "python apps/web/run_api.py"
```

### Files to Modify

#### `apps/web/run_api.py`
**Change:** Read `PORT` from env (Railway sets this automatically):
```python
CR_port = int(os.environ.get("PORT", 8000))
CR_host = os.environ.get("HOST", "0.0.0.0")
```

#### `apps/web/api/config.py`
**Change:** All config reads from env vars (already mostly true — verify LLM keys load from env in Railway context). Add:
```python
ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "development")
```

#### `apps/web/api/main.py`
**Change:** CORS allowed origins should include the Railway URL. Add env-driven origin list:
```python
CR_cors_origins = os.environ.get(
    "CORS_ORIGINS",
    "http://localhost:3000,http://localhost:8000"
).split(",")
```

### Deployment Steps (Local → Railway)

Script: `scripts/deploy_railway.sh`
```bash
#!/usr/bin/env bash
# Deploy AtOdds to Railway from local environment
# Prerequisites: Railway CLI installed (npm install -g @railway/cli)

set -e

echo "🚀 AtOdds Railway Deployment"
echo "================================"

# 1. Check Railway CLI
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found."
    echo "   Install: npm install -g @railway/cli"
    exit 1
fi

# 2. Login check
echo "📋 Checking Railway auth..."
railway whoami || railway login

# 3. Link or init project
echo "🔗 Linking Railway project..."
railway link || railway init

# 4. Set environment variables
echo "⚙️  Setting environment variables..."
echo "   You'll need to set these in Railway dashboard or via CLI:"
echo "   railway variables set LLM_PROVIDER=openai"
echo "   railway variables set OPENAI_API_KEY=sk-..."
echo ""
read -p "Have you set your env vars in Railway? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "   Go to: https://railway.app → your project → Variables tab"
    exit 1
fi

# 5. Deploy
echo "🚢 Deploying..."
railway up --detach

echo ""
echo "✅ Deployment triggered!"
echo "   Check status: railway status"
echo "   View logs:    railway logs"
echo "   Open app:     railway open"
```

Script: `scripts/deploy_railway.ps1` (Windows PowerShell version)
```powershell
# Deploy AtOdds to Railway from Windows
# Prerequisites: npm install -g @railway/cli

Write-Host "🚀 AtOdds Railway Deployment"
Write-Host "================================"

# Check Railway CLI
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found."
    Write-Host "   Install: npm install -g @railway/cli"
    exit 1
}

# Login
Write-Host "📋 Checking Railway auth..."
railway whoami
if ($LASTEXITCODE -ne 0) { railway login }

# Link project
Write-Host "🔗 Linking Railway project..."
railway link

# Prompt for env vars
Write-Host ""
Write-Host "⚙️  Required environment variables for Railway dashboard:"
Write-Host "   LLM_PROVIDER = openai"
Write-Host "   OPENAI_API_KEY = sk-..."
Write-Host "   (or ANTHROPIC_API_KEY / GEMINI_API_KEY depending on provider)"
Write-Host ""
$confirm = Read-Host "Have you set env vars in Railway? (y/n)"
if ($confirm -ne "y") {
    Write-Host "   Set them at: https://railway.app → your project → Variables"
    exit 1
}

# Deploy
Write-Host "🚢 Deploying..."
railway up --detach

Write-Host ""
Write-Host "✅ Done! Commands:"
Write-Host "   railway status   → check deploy status"
Write-Host "   railway logs     → view live logs"
Write-Host "   railway open     → open in browser"
```

## Fallback Platform: Fly.io

If Railway deployment fails, use Fly.io as fallback.

#### `fly.toml`
```toml
app = "atodds"
primary_region = "sea"

[build]
  [build.args]
    PYTHON_VERSION = "3.13"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

#### `Dockerfile`
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt requirements-web.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-web.txt

COPY . .

EXPOSE 8000

CMD ["python", "apps/web/run_api.py"]
```

Script: `scripts/deploy_fly.ps1`
```powershell
# Deploy AtOdds to Fly.io from Windows
# Prerequisites: winget install -e --id Flyctl.Flyctl

Write-Host "🚀 AtOdds Fly.io Deployment"

if (-not (Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Host "❌ flyctl not found. Install: winget install -e --id Flyctl.Flyctl"
    exit 1
}

fly auth login
fly launch --no-deploy --name atodds

# Set secrets
Write-Host "Setting secrets..."
fly secrets set LLM_PROVIDER=openai
$key = Read-Host "Enter your OpenAI API key"
fly secrets set OPENAI_API_KEY=$key

fly deploy
Write-Host "✅ Deployed! URL: https://atodds.fly.dev"
```

---

# PART 2: DEVLOG.md REWRITE

The existing `docs/DEVLOG.md` covers architecture decisions well but is missing what Betstamp explicitly asks for:
- **How AI tools were used during development**
- **Prompt iterations** — how the agent's system prompt evolved
- **What AI got wrong** that was fixed
- **Specific delegation decisions**

The DEVLOG rewrite happens **after all phases are complete** so it accurately reflects the full development journey.

### Template: `docs/DEVLOG.md` (to be filled in after Phase 8+9 implementation)

```markdown
# DEVLOG.md
## Author: Chris Rafuse
## Project: Betstamp Odds Intelligence Agent
## Version: 2.0 (Phases 8-10 complete)

---

# HOW I USED AI TOOLS

## Tools Used
- **Windsurf (Cascade/Claude)**: Primary coding assistant for code generation, 
  debugging, and architecture review
- **Reasoning**: Used for spec writing, tradeoff analysis

## What I Delegated to AI
- Boilerplate for adapter pattern (LLM provider base class + 3 adapters)
- CSS for chat UI and rankings table
- JSON schema generation for tool definitions
- Test scaffolding for new modules

## What I Wrote Myself
- All deterministic math logic (odds_math.py, detectors.py)
- System prompt design and iteration
- Sportsbook ranking formula (quality score)
- Deployment configuration
- Math proof format for each finding type

## What AI Got Wrong (And How I Fixed It)
[Fill in during Phase 8-9 implementation — capture real examples]
Examples to document:
- Adapter pattern initially mixed sync/async → fixed to consistent async
- Tool schema initially missing required fields → corrected after 422 errors
- Mock provider returned wrong structure → fixed to match CR_LLMResponse

---

# SYSTEM PROMPT ITERATIONS

## Iteration 1 (Initial)
"You are an odds agent. Analyze the data."
Problem: LLM dumped raw analysis without calling tools.

## Iteration 2
"You must use tools for all calculations. Never do math yourself."
Problem: LLM called tools but ignored results, synthesized its own summary.

## Iteration 3
"After each tool call, record the finding. Do not proceed to the next tool
until the previous result is incorporated."
Problem: Better, but briefing structure was inconsistent.

## Iteration 4 (Final)
[Document actual final prompt from Phase 8 implementation]
Added explicit briefing section order, evidence requirement, refusal instruction.

---

# KEY DECISIONS

## Why Adapter Pattern for LLM
Three providers have different APIs (OpenAI function_call, Anthropic tool_use, 
Gemini function declarations). Adapter pattern lets the agent loop stay unchanged 
while swapping providers via one env var. Alternative was to pick one provider 
and hardcode — rejected because the assignment doesn't specify one.

## Why Keep Deterministic Fallback
If no API key is set, the system still returns correct results via the 
deterministic pipeline. This means local dev and CI don't require API keys.
The mock provider tests the full pipeline without cost.

## Why Quality Score Formula
Vig weighted at 40% because it's the most directly measurable indicator of 
bookmaker value to a bettor. Best-line frequency at 40% because it shows 
real-world competitiveness. Freshness and accuracy at 10% each as supporting 
signals. Calibrated against real sportsbook reputation expectations.

## Why Railway over Vercel
FastAPI is not a serverless-first framework. Vercel requires adapter layers
for Python. Railway runs the exact same command as local dev. Less config, 
less risk of environment-specific bugs during review.

---

# WHAT I'D IMPROVE WITH MORE TIME

1. **Streaming LLM responses** — Live typing in chat instead of wait-then-render.
   Implementation: Switch from `chat_with_tools()` to `stream_with_tools()` in 
   each adapter, use Server-Sent Events to push tokens to the browser.

2. **Pinnacle as sharp anchor** — Use Pinnacle's lines as the consensus reference 
   instead of simple average. Pinnacle is the most efficient market. This would 
   make value edge detection significantly more meaningful.

3. **Line movement tracking** — Store snapshots over time, alert when lines move 
   significantly. This converts the system from point-in-time to temporal analysis.

4. **Confidence calibration** — The current 0-1 confidence scores are heuristic. 
   With historical data, they could be calibrated to actual outcome rates.

5. **Eval harness** — Automated scoring of briefing quality: did the agent find 
   all seeded anomalies? Did it flag false positives? Right now this is manual.

---

# TRADEOFFS MADE

| Area | Decision | Tradeoff |
|------|-----------|---------|
| LLM model | gpt-4o-mini / haiku | Cost vs. quality — mini/haiku sufficient for structured output |
| Chat grounding | Tool-only answers | Prevents hallucination, limits open-ended Q&A |
| Deployment | Railway | Simple setup, less control than EC2/GCP |
| Math display | Inline in findings | Adds verbosity but makes verification trivial |
| Sportsbook ranking | Simple weighted formula | Fast and explainable vs. ML-based |
```

---

# PART 3: README FINAL UPDATE

After Phase 10 deployment, update `README.md`:
- Add deployed URL at the top
- Update Quick Start to point to live URL first
- Add "Set your LLM API key" step to setup instructions
- Update architecture section to include `packages/llm/`

---

# 📋 TASK CHECKLIST

## Deployment
- [ ] Create `railway.toml`
- [ ] Create `Procfile`
- [ ] Create `nixpacks.toml`
- [ ] Create `Dockerfile` (Fly.io fallback)
- [ ] Create `fly.toml` (Fly.io fallback)
- [ ] Create `scripts/deploy_railway.ps1`
- [ ] Create `scripts/deploy_railway.sh`
- [ ] Create `scripts/deploy_fly.ps1`
- [ ] Update `apps/web/run_api.py` to read PORT from env
- [ ] Update `apps/web/api/main.py` CORS to use env-driven origins
- [ ] Test local Docker build before deploy
- [ ] Deploy to Railway, verify live URL responds to `/health`
- [ ] Verify LLM integration works on deployed instance
- [ ] Add deployed URL to README.md

## DEVLOG
- [ ] Document all AI tool usage from Phases 8-9 implementation
- [ ] Document prompt iterations (capture real iterations, not hypothetical)
- [ ] Document what AI got wrong during implementation
- [ ] Document key architectural decisions with reasoning
- [ ] Document "what I'd improve" list (specific, not vague)
- [ ] Write tradeoffs table
- [ ] Replace placeholder sections in template above with real content
- [ ] Verify DEVLOG.md reads as genuine, not AI-generated filler

---

# ✅ EXIT CRITERIA

- Live URL accessible (Railway or Fly.io)
- `/health` endpoint returns 200 at live URL
- `/` serves frontend at live URL
- Analysis runs end-to-end on live deployment
- DEVLOG.md contains real AI usage log, real prompt iterations, real tradeoffs
- README.md shows deployed URL prominently

---

**Phase 10 Status**: Ready to implement after Phase 9
**Dependencies**: Phases 8 + 9 complete
**Final State**: Full submission package ready
