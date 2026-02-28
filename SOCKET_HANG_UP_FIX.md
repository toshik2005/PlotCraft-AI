# Socket Hang Up Error Fix - Troubleshooting Guide

## Error Details
- **Error**: `Failed to proxy http://localhost:8000/api/v1/story/continue [Error: socket hang up]`
- **Code**: `ECONNRESET`
- **Cause**: Backend server not responding, crashing, or connection timeout

---

## ✅ Quick Fix Steps

### Step 1: Ensure Backend is Running
```bash
cd backend
python run.py
```

**Expected output:**
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete [uvicorn]
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Test Backend Health
```bash
python debug_test.py
```

This will test connectivity and endpoints.

### Step 3: Check System Resources
- **RAM**: Story generation requires ~2GB RAM
- **Disk Space**: Ensure at least 1GB free
- **CPU**: Check if CPU is maxed out

### Step 4: Verify CORS Configuration

The frontend rewrites requests to the backend. Make sure:

1. **Frontend** (`next.config.ts`):
```typescript
async rewrites() {
  return [
    { source: "/api/v1/:path*", destination: `${backendUrl}/api/v1/:path*` },
  ];
}
```

2. **Backend** (`app/core/config.py`):
```python
CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
```

---

## 🔍 Understanding the Changes Made

### 1. **Increased Timeouts** (`config.py`)
- **REQUEST_TIMEOUT**: 120s → 300s (5 minutes)
  - ML operations need more time
- **KEEP_ALIVE_TIMEOUT**: 300s → 600s (10 minutes)
  - Prevents premature connection drops
- **GENERATION_TIMEOUT**: Added 120s timeout
  - Prevents indefinite hangs

### 2. **Better Error Handling** (`routes_story.py`)
- ✅ Input validation before processing
- ✅ Try-catch blocks around genre detection
- ✅ Try-catch blocks around character extraction
- ✅ Proper error responses (400, 500, 504)
- ✅ Differentiated error messages

### 3. **Improved Generation** (`story_service.py`)
- ✅ Log success/failure at each step
- ✅ Better fallback mechanism
- ✅ Raised RuntimeError if all methods fail
- ✅ Clear error messages for debugging

### 4. **Enhanced Logging** (`main.py`)
- ✅ Request logging for debugging
- ✅ Exception logging with stack traces
- ✅ Health check endpoint

### 5. **Server Configuration** (`run.py`)
- ✅ Added reload_dirs to avoid conflicts
- ✅ Configured shutdown timeouts
- ✅ Added interface auto-detection

---

## 🐛 Common Issues & Solutions

### Issue 1: "Connection refused" or "Cannot connect to localhost:8000"
**Solution:** Backend is not running
```bash
cd backend
python run.py
```

### Issue 2: "socket hang up" after 30-120 seconds
**Solution:** Request timing out
- The story generation might be slow
- Check if models are loading properly
- Try with a shorter input text
- Increase `GENERATION_TIMEOUT` in `config.py`

### Issue 3: "502 Bad Gateway" from Next.js
**Solution:** Backend crashed
- Check console output for Python errors
- Run `debug_test.py` to identify failing endpoint
- Check logs for specific ML model errors

### Issue 4: Models not loading
**Check prerequisites:**
```bash
# Verify spaCy model
python -c "import spacy; spacy.load('en_core_web_sm')"

# Verify transformers
python -c "from transformers import pipeline; p = pipeline('text-generation')"

# Check PlotCraft
python -c "from plotcraft.src.plotcraft_generator import generate_text"
```

### Issue 5: Out of Memory (OOM)
**Solutions:**
- Reduce `max_tokens` parameter
- Close other applications
- Use a machine with more RAM

---

## 📊 Monitoring

### Check Backend Status
```bash
curl http://localhost:8000/health
```

### View Real-time Logs
Backend logs are printed to console when running `python run.py`

### Test Story Continuation
```bash
curl -X POST http://localhost:8000/api/v1/story/continue \
  -H "Content-Type: application/json" \
  -d '{
    "story": "Once upon a time, there was a girl who found a door.",
    "genre": "horror"
  }'
```

---

## 🚀 Performance Tuning

### For faster responses:
1. **Reduce max_tokens** in API request
   - Default: 800 tokens
   - Try: 300-500 tokens

2. **Lower temperature** for focused generation
   - Default: 0.8
   - Try: 0.5-0.7

3. **Use shorter input text**
   - Shorter prompts generate faster
   - Max recommended: 500 characters

### For more stable connections:
1. **Increase KEEP_ALIVE_TIMEOUT** in `config.py`
2. **Add connection pooling** on frontend
3. **Monitor system resources**

---

## 📝 Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG = False` in `config.py`
- [ ] Update `CORS_ORIGINS` with actual frontend URL
- [ ] Increase `limit_concurrency` in `run.py` based on expected load
- [ ] Set up proper logging to a file
- [ ] Configure environment-specific timeouts
- [ ] Test with production-like load
- [ ] Monitor memory and CPU usage
- [ ] Set up graceful shutdown handlers

---

## 📞 Still Having Issues?

1. **Run diagnostic**: `python debug_test.py`
2. **Check logs**: Look at console output from `python run.py`
3. **Test endpoints**: Use curl or Postman to test individually
4. **Review changes**: See "Understanding the Changes Made" section above

---

## 📚 Reference URLs

- FastAPI Docs: http://localhost:8000/docs
- API Health: http://localhost:8000/health
- Frontend: http://localhost:3000
