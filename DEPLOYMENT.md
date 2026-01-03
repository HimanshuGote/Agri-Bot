# 🚀 Deployment Guide - Agriculture Chatbot

Complete step-by-step guide for deploying to **Render** (recommended platform).

---

## 📋 Pre-Deployment Checklist

- [ ] All code tested locally
- [ ] PDFs placed in project root
- [ ] `.env.example` configured
- [ ] `requirements.txt` up to date
- [ ] Git repository initialized
- [ ] OpenAI API key obtained
- [ ] Render account created

---

## 🌐 Deploy to Render (Recommended)

### Why Render?

- ✅ Free tier available
- ✅ Auto-detects Python/FastAPI
- ✅ Environment variable management
- ✅ Automatic HTTPS
- ✅ Easy GitHub integration
- ✅ Health checks built-in

### Step 1: Prepare Repository

```bash
# Initialize git (if not already)
git init

# Add files
git add .

# Commit
git commit -m "Initial commit - Agriculture Chatbot"

# Create GitHub repo and push
git remote add origin https://github.com/yourusername/agriculture-chatbot.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repos

### Step 3: Create New Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Render will auto-detect settings from `render.yaml`

### Step 4: Configure Service

**If `render.yaml` not auto-detected, manually configure:**

| Setting | Value |
|---------|-------|
| Name | `agriculture-chatbot` |
| Environment | `Python 3` |
| Region | `Oregon (US West)` or nearest |
| Branch | `main` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | `Free` |

### Step 5: Set Environment Variables

In Render dashboard, go to **Environment** tab and add:

```
OPENAI_API_KEY=sk-your-actual-openai-key-here
PYTHON_VERSION=3.9.18
ENVIRONMENT=production
```

**Optional (for LangSmith tracing):**
```
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-key
LANGCHAIN_PROJECT=agriculture-chatbot-prod
```

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will:
   - Clone your repo
   - Install dependencies
   - Build the application
   - Start the server

**Build time:** 3-5 minutes

### Step 7: Verify Deployment

Once deployed, you'll get a URL like:
```
https://agriculture-chatbot.onrender.com
```

Test endpoints:
```bash
# Health check
curl https://agriculture-chatbot.onrender.com/health

# Test query
curl -X POST https://agriculture-chatbot.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I prevent Citrus Canker?"}'
```

### Step 8: Access Documentation

Visit:
```
https://agriculture-chatbot.onrender.com/docs
```

You'll see the interactive Swagger UI.

---

## ⚠️ Important Notes for Render

### Cold Starts

**Issue:** Free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30-60 seconds.

**Solutions:**
1. **Upgrade to paid tier** ($7/month) - no cold starts
2. **Keep-alive ping**: Use a service like [UptimeRobot](https://uptimerobot.com) to ping `/health` every 10 minutes
3. **Accept cold starts**: Inform users first query may be slow

### Disk Persistence

**Issue:** Render's free tier may reset disk on re-deploys.

**Solution:** 
- Chroma DB (`chroma_db/`) should be committed to git
- On startup, app checks if vector stores exist
- If not, rebuilds them from PDFs (adds 2-3 min to startup)

**To commit Chroma DB:**
```bash
# Remove from .gitignore if present
# Then:
git add chroma_db/
git commit -m "Add pre-built vector stores"
git push
```

### Environment Variable Security

**Never commit** `.env` file to git!

Always use Render's environment variable dashboard for secrets.

---

## 🐳 Alternative: Docker Deployment

### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Build and Run Locally

```bash
# Build image
docker build -t agriculture-chatbot .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your-key \
  agriculture-chatbot
```

### Deploy to Docker Hub + Render

```bash
# Tag image
docker tag agriculture-chatbot yourusername/agriculture-chatbot:latest

# Push to Docker Hub
docker push yourusername/agriculture-chatbot:latest
```

Then in Render:
- Choose **"Docker"** as environment
- Specify: `yourusername/agriculture-chatbot:latest`

---

## ☁️ Alternative: Railway Deployment

### Step 1: Install Railway CLI

```bash
npm install -g @railway/cli

# Or with Homebrew
brew install railway
```

### Step 2: Login and Init

```bash
railway login
railway init
```

### Step 3: Set Environment Variables

```bash
railway variables set OPENAI_API_KEY=your-key
```

### Step 4: Deploy

```bash
railway up
```

Railway will auto-detect Python and deploy.

---

## 🔧 Post-Deployment

### Monitor Logs

**Render:**
- Dashboard → Your Service → Logs tab

**Railway:**
```bash
railway logs
```

### Update Deployment

```bash
# Make changes locally
git add .
git commit -m "Update feature"
git push

# Render auto-deploys on push
# Railway: run `railway up` again
```

### Domain Configuration

**Render:**
- Dashboard → Settings → Custom Domain
- Add your domain (e.g., `api.yourfarm.com`)
- Follow DNS instructions

---

## 📊 Monitoring & Maintenance

### Health Checks

Set up automated monitoring:

1. **UptimeRobot** (free)
   - Monitor: `https://your-app.onrender.com/health`
   - Alert: Email/SMS on downtime

2. **Render Built-in**
   - Health check path: `/health`
   - Already configured in `render.yaml`

### Performance Optimization

**If response times > 5 seconds:**

1. **Upgrade Render plan** (more RAM/CPU)
2. **Optimize retrieval:**
   ```python
   # In document_processor.py, reduce k
   search_kwargs={"k": 3}  # Instead of 4
   ```
3. **Cache common queries** (add Redis)
4. **Use smaller embedding model**

### Cost Management

**Free Tier Limits (Render):**
- 750 hours/month
- 512 MB RAM
- Shared CPU
- No custom domains

**Upgrade triggers:**
- Need 24/7 uptime
- >1000 requests/day
- Response time critical

---

## 🆘 Troubleshooting

### Build Fails: "Requirements not installed"

**Fix:**
```bash
# Ensure requirements.txt has no typos
pip install -r requirements.txt  # Test locally first
```

### Runtime Error: "PDFs not found"

**Fix:**
```bash
# Ensure PDFs are in git
git add *.pdf
git commit -m "Add PDF files"
git push
```

### Error: "OpenAI API key invalid"

**Fix:**
- Verify key in Render environment variables
- Check key hasn't expired
- Regenerate key if needed

### Timeout on First Request

**This is normal** for cold starts on free tier.

**Fix:**
- Upgrade to paid tier, OR
- Set up keep-alive pings

---

## ✅ Deployment Verification Checklist

After deployment, verify:

- [ ] Health endpoint returns 200: `/health`
- [ ] Swagger docs load: `/docs`
- [ ] Disease query works
- [ ] Scheme query works
- [ ] Hybrid query works
- [ ] Response time < 5 seconds (warm)
- [ ] Logs show no errors
- [ ] Environment variables set correctly

---

## 🎉 Success!

Your Agriculture Chatbot is now live and helping farmers!

**Share your deployment:**
- API Endpoint: `https://your-app.onrender.com`
- Docs: `https://your-app.onrender.com/docs`

---

## 📞 Need Help?

- Render Support: [render.com/docs](https://render.com/docs)
- Railway Support: [docs.railway.app](https://docs.railway.app)
- OpenAI Issues: [platform.openai.com/docs](https://platform.openai.com/docs)
