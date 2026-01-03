# 🚀 Quick Reference - Agriculture Chatbot

## Essential Commands

### Setup (First Time)

```bash
# Unix/Mac
./setup.sh

# Windows
setup.bat

# Manual
python -m venv venv
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Environment

```bash
# Activate
source venv/bin/activate  # Unix
venv\Scripts\activate     # Windows

# Deactivate
deactivate

# Check Python
python --version  # Should be 3.9+
```

### Running the Server

```bash
# Method 1: Direct
python main.py

# Method 2: Uvicorn (recommended for dev)
uvicorn main:app --reload --port 8000

# Method 3: Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Testing

```bash
# Run test suite
python test_queries.py

# Health check
curl http://localhost:8000/health

# Test disease query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I prevent Citrus Canker?"}'

# Test scheme query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What subsidies are available?"}'

# Test hybrid query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Government schemes for pest control?"}'
```

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Root/welcome |
| `/health` | GET | System health |
| `/query` | POST | Main query endpoint |
| `/test-intent` | POST | Test intent detection |
| `/stats` | GET | System statistics |
| `/docs` | GET | Interactive API docs |

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-key-here

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-key
LANGCHAIN_PROJECT=agri-chatbot
```

### Deployment

```bash
# Render
git push origin main  # Auto-deploys

# Railway
railway login
railway up

# Docker
docker build -t agri-chatbot .
docker run -p 8000:8000 --env-file .env agri-chatbot
```

### Troubleshooting

```bash
# PDF not found error
ls *.pdf  # Check both PDFs exist

# Port already in use
lsof -i :8000  # Unix
netstat -ano | findstr :8000  # Windows

# OpenAI API error
cat .env | grep OPENAI  # Check key is set

# Import error
pip list  # Check all packages installed
pip install -r requirements.txt  # Reinstall

# Vector store error
rm -rf chroma_db/  # Delete and rebuild
python main.py  # Will regenerate
```

### Logs

```bash
# View logs (if using systemd)
journalctl -u agriculture-chatbot -f

# Render logs
# Dashboard → Your Service → Logs

# Local logs
tail -f logs/app.log  # If logging to file
```

### Git Commands

```bash
# Initial setup
git init
git add .
git commit -m "Initial commit"
git remote add origin <repo-url>
git push -u origin main

# Updates
git add .
git commit -m "Update feature"
git push
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Module not found" | `pip install -r requirements.txt` |
| "PDF not found" | Place PDFs in project root |
| "API key invalid" | Check `.env` file, regenerate key |
| "Port in use" | Change port or kill process |
| "Slow response" | Check OpenAI API status |
| "Out of memory" | Reduce `k` in retrieval (3 instead of 4) |

### Performance

```bash
# Check memory usage
ps aux | grep python

# Check disk space
df -h

# Monitor requests
watch -n 1 'curl -s http://localhost:8000/stats'
```

### Development

```bash
# Install dev dependencies
pip install pytest black flake8

# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

### Documentation

| Resource | Location |
|----------|----------|
| API Docs | `http://localhost:8000/docs` |
| README | `README.md` |
| Architecture | `ARCHITECTURE.md` |
| Deployment | `DEPLOYMENT.md` |
| Summary | `PROJECT_SUMMARY.md` |

### URLs (After Deployment)

```
# Local
http://localhost:8000
http://localhost:8000/docs

# Render (example)
https://agriculture-chatbot.onrender.com
https://agriculture-chatbot.onrender.com/docs
```

### Sample Queries

**Disease:**
- "My citrus leaves have yellow patches"
- "How to prevent Citrus Canker?"
- "Treatment for whitefly infestation"

**Scheme:**
- "Government schemes for citrus farmers"
- "Subsidies for drip irrigation"
- "Organic farming financial help"

**Hybrid:**
- "Schemes for managing Citrus Greening"
- "Government support for pest control"
- "Subsidy for disease prevention"

### Quick Health Check

```bash
# All-in-one check
curl http://localhost:8000/health && \
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "test"}' && \
echo "✓ System OK"
```

### Backup Commands

```bash
# Backup vector stores
tar -czf chroma_backup.tar.gz chroma_db/

# Restore
tar -xzf chroma_backup.tar.gz

# Backup .env (local only)
cp .env .env.backup
```

---

**Pro Tip**: Bookmark `http://localhost:8000/docs` for interactive API testing!
