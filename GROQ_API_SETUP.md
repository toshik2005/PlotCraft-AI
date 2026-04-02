# Groq API Setup Guide

## ⚠️ Current Issue

Your Groq API key is **not configured** or **invalid**. This is causing the "Empty response from Groq API" error.

## ✅ Step 1: Get Your API Key

1. Go to: **https://console.groq.com/keys**
2. Sign in with your Groq account (create one if needed - it's free)
3. Click "Create API Key"
4. Copy your API key (starts with `gsk_`)

## ✅ Step 2: Create .env File

In the project root directory (c:\Users\Dell\Downloads\Xebia Project\), create a file named `.env` with:

```env
GROQ_API_KEY=gsk_your_actual_key_here_replace_this
```

Replace `gsk_your_actual_key_here_replace_this` with your actual key.

**Example (don't use this!):**
```env
GROQ_API_KEY=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
```

## ✅ Step 3: Restart Backend Server

After creating/updating the .env file:

```powershell
# Stop current server (Ctrl+C in terminal)
# Then restart:
cd backend
python run.py
```

## ⚠️ IMPORTANT SECURITY NOTES

1. **NEVER hardcode API keys in source code** - We removed the hardcoded key from `groq_service.py`
2. **Keep your .env file PRIVATE** - Add it to `.gitignore`:
   ```
   echo ".env" >> .gitignore
   ```
3. **Don't commit .env to version control**

## 🔍 Verify It's Working

### Option 1: Check Status Endpoint
```bash
curl http://localhost:8000/api/v1/status/groq
```

Expected response if configured:
```json
{
  "configured": true,
  "model": "openai/gpt-oss-120b",
  "api_key_prefix": "gsk_...",
  "status": "ready",
  "available": true
}
```

### Option 2: Run Test
```bash
cd backend
python test_improved_groq.py
```

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY is not set"
- ✗ Problem: `.env` file doesn't exist or GROQ_API_KEY is not in it
- ✓ Solution: Create `.env` file with your key (see Step 2)

### Error: "Invalid API key format"
- ✗ Problem: Key doesn't start with `gsk_`
- ✓ Solution: Get a new key from https://console.groq.com/keys

### Error: "API key is invalid or expired"
- ✗ Problem: Key is wrong, expired, or account has no credits
- ✓ Solution: 
  1. Verify key in console: https://console.groq.com/keys
  2. Check account credits: https://console.groq.com/account
  3. Try a new key if needed

### Error: "Rate limit exceeded"
- ✗ Problem: Too many requests in short time
- ✓ Solution: Wait a moment and try again

### Error: "Groq API server temporarily unavailable"
- ✗ Problem: Groq service is down
- ✓ Solution: Check status at https://status.groq.com/ and try again later

## 📚 Models Available

Current model: **openai/gpt-oss-120b** (recommended)

Other options:
- `llama2-70b-4096` - Fast, good for general tasks
- `gemma-7b-it` - Lightweight
- `mixtral-8x7b-32768` - Balanced

To use a different model, add to `.env`:
```env
GROQ_MODEL=llama2-70b-4096
```

## 🎯 Next Steps

1. ✅ Get API key from https://console.groq.com/keys
2. ✅ Create `.env` file with your key
3. ✅ Restart backend server
4. ✅ Run test to verify: `python test_improved_groq.py`
5. ✅ Test character extraction and story generation endpoints

## 📖 Resources

- **Groq Documentation**: https://console.groq.com/docs
- **Available Models**: https://console.groq.com/docs/models
- **API Status**: https://status.groq.com/
- **Rate Limits**: https://console.groq.com/docs/rate-limiting

---

**Need more help?**
- Check `.env.template` for the file format
- Review error messages - they now include specific suggestions
- Check logs for detailed diagnostics
