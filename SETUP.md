# AtOdds Quick Setup Guide

## 🚀 5-Minute Setup

### 1. Install Dependencies
```bash
pip install -r requirements-web.txt
```
*Compatible with Python 3.11+ and 3.14*

### 2. Configure LLM (Optional)
```bash
# Copy template
Copy-Item .env.example .env

# Edit with your API key (or use mock)
notepad .env
```

For OpenAI (recommended):
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
```

For faster responses:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-your-actual-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### 3. Run Server
```bash
python -m apps.web.run_api
```

### 4. Open Browser
Visit http://localhost:8000 or http://localhost:8001

### 5. Test the App
1. Click "Load Sample Data"
2. Click "Analyze Odds"
3. View AI-powered insights
4. Try the chat interface

---

## 📖 Detailed Instructions

### Without API Key (Mock Mode)
The app works perfectly without an API key using the mock provider:
```env
LLM_PROVIDER=mock
```

### With OpenAI API Key
1. Get API key: https://platform.openai.com/api-keys
2. Add to `.env`:
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-proj-your-key-here
   ```
3. Verify connection:
   ```bash
   python test_llm_connection.py
   ```

### Port Conflicts?
If port 8000 is busy, the server automatically uses 8001. Or set it in `.env`:
```env
PORT=8001
```

---

## 🎯 What You'll See

- **Arbitrage opportunities** with profit margins
- **Value edges** vs consensus pricing
- **AI-generated summaries** (with LLM)
- **Interactive chat** about your data
- **Math proofs** for every finding
- **Sportsbook rankings** with quality scores

---

## 🆘 Troubleshooting

**"Port already in use"**
- The server will try port 8001 automatically
- Or set `PORT=8002` in `.env`

**"LLM not working"**
- Check `.env` has correct API key
- Run `python test_llm_connection.py` to verify
- Use `LLM_PROVIDER=mock` to test without API

**Sample data not loading**
- Ensure `data/sample_odds.json` exists
- Check server logs for errors

---

## 💡 Pro Tips

- **Budget-friendly**: Use `gpt-4o-mini` for ~$0.003 per analysis
- **Privacy**: Use mock mode if data is sensitive
- **Performance**: The app works offline with mock provider
- **Mobile**: Responsive design works on phones/tablets

---

## 📚 More Documentation

- **Full README**: [README.md](README.md)
- **API Docs**: http://localhost:8000/docs
- **Phase Plans**: [plans/](plans/) directory

---

**Ready to go!** 🎉 You now have a fully functional odds analysis system with AI-powered insights.
