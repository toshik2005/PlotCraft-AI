# API Reference & Developer Guide

## Quick Start

### Installation
```bash
cd backend
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Running the Server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- **Interactive Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

---

## Main Endpoint: POST /api/v1/story/generate

### Request Body

```json
{
  "user_id": "string",
  "story": "string",
  "genre": "action|horror|scifi",
  "twist": "unexpected|reversal|revelation|betrayal|discovery|null",
  "refine": "boolean",
  "measure": "boolean",
  "temperature": "number (0.1-2.0)",
  "max_tokens": "number (50-1000)"
}
```

### Request Field Descriptions

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `user_id` | string | ✅ Yes | - | Unique user/session identifier (1-256 chars) |
| `story` | string | ✅ Yes | - | Story prompt (10-5000 chars) |
| `genre` | string | ⚠️ Opt | "scifi" | One of: action, horror, scifi |
| `twist` | string | ⚠️ Opt | null | Twist type or null for no twist |
| `refine` | boolean | ⚠️ Opt | false | Refine story for coherence |
| `measure` | boolean | ⚠️ Opt | true | Score the generated story |
| `temperature` | float | ⚠️ Opt | 0.8 | Creativity: 0.1≈focused, 2.0≈creative |
| `max_tokens` | int | ⚠️ Opt | 300 | Max generated tokens |

### Response Body

```json
{
  "genre": "string",
  "detected_characters": ["string"],
  "persisted_characters": ["string"],
  "twist_applied": "string|null",
  "generated_text": "string",
  "refined": "boolean",
  "score": "number|null",
  "character_focus_required": "boolean"
}
```

### Response Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `genre` | string | Genre used for generation |
| `detected_characters` | array | Characters detected in current prompt |
| `persisted_characters` | array | All characters for this user session |
| `twist_applied` | string\|null | Applied twist type if any |
| `generated_text` | string | The generated story continuation |
| `refined` | boolean | Whether story was refined |
| `score` | number\|null | Quality score (4.0-5.0 range) if measured |
| `character_focus_required` | boolean | Whether second-pass generation was needed |

### Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Story generated successfully |
| 400 | Bad Request | Missing user_id, invalid story length |
| 422 | Validation Error | Invalid genre, temperature out of range |
| 500 | Server Error | Model loading failed, generation timeout |

### cURL Examples

#### Basic Generation
```bash
curl -X POST "http://localhost:8000/api/v1/story/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "story": "Alice walked through the dark forest.",
    "genre": "horror",
    "refine": false,
    "measure": true
  }'
```

#### With Twist and Refinement
```bash
curl -X POST "http://localhost:8000/api/v1/story/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_123",
    "story": "The detective investigated the mysterious case.",
    "genre": "action",
    "twist": "revelation",
    "refine": true,
    "measure": true,
    "temperature": 0.85,
    "max_tokens": 400
  }'
```

---

## Service Layer API

### StoryService

```python
from app.services.story_service import generate_story_pipeline

result = generate_story_pipeline(
    user_id="user_123",
    prompt="Alice found a mysterious door",
    genre="horror",
    twist="revelation",
    refine=True,
    measure=True,
    temperature=0.8,
    max_tokens=300
)

print(result["generated_text"])
print(result["score"])
print(result["persisted_characters"])
```

### MemoryService

```python
from app.services.memory_service import (
    save_user_characters,
    get_user_characters,
    clear_user_characters,
    get_memory_stats
)

# Save characters for a user
save_user_characters("user_123", ["Alice", "Bob"])

# Retrieve characters
chars = get_user_characters("user_123")  # ["Alice", "Bob"]

# Clear session memory
clear_user_characters("user_123")

# Get stats
stats = get_memory_stats()  # {"active_users": 42, "total_characters": 156}
```

### TwistService

```python
from app.services.twist_service import (
    apply_twist_to_prompt,
    validate_twist_type,
    TwistService
)

# Apply twist to prompt
enhanced = apply_twist_to_prompt(
    "Once upon a time",
    "betrayal",
    "Alice"
)

# Validate twist type
if validate_twist_type("revelation"):
    print("Valid twist type")

# Get available twists
twists = TwistService.list_available_twists()
# {
#   "unexpected": "Introduce an unexpected twist...",
#   "reversal": "Include a reversal of expectations...",
#   ...
# }
```

### NERModel

```python
from app.models.ner_model import ner_model

# Extract characters
characters = ner_model.extract_characters("Alice and Bob met Sarah.")
# ["Alice", "Bob", "Sarah"]

# Extract all entities
entities = ner_model.extract_entities("Alice lives in New York.")
# {"PERSON": ["Alice"], "GPE": ["New York"]}
```

### PlotCraft Generator

```python
from plotcraft.src.plotcraft_generator import (
    generate_text,
    load_genre_model,
    get_cache_info,
    clear_model_cache
)

# Generate text directly
text = generate_text(
    "Once upon a time",
    genre="horror",
    max_tokens=200,
    temperature=0.8
)

# Check what's cached
info = get_cache_info()  # {"action": False, "horror": True, "scifi": True}

# Load a specific model
model, tokenizer, device = load_genre_model("scifi")

# Clear cache
clear_model_cache()
```

---

## Common Use Cases

### 1. Multi-Turn Story with Character Consistency

```python
# User's first message
result1 = generate_story_pipeline(
    user_id="alice_session",
    prompt="Alice discovers a magical portal in her attic.",
    genre="scifi"
)
# Returns: {"detected_characters": ["Alice"], ...}

# User's second message - Alice should persist
result2 = generate_story_pipeline(
    user_id="alice_session",
    prompt="She steps through and finds a futuristic city.",
    genre="scifi"
)
# Returns: {"persisted_characters": ["Alice"], ...}
```

### 2. Horror Story with Twist

```python
result = generate_story_pipeline(
    user_id="horror_fan",
    prompt="The old mansion was eerily quiet. Sarah entered cautiously.",
    genre="horror",
    twist="betrayal",  # Inject dramatic betrayal
    refine=True,       # Polish the narrative
    measure=True       # Score quality
)

print(f"Twist applied: {result['twist_applied']}")
print(f"Story score: {result['score']}")
```

### 3. Action Story with High Creativity

```python
result = generate_story_pipeline(
    user_id="action_writer",
    prompt="The spy infiltrated the enemy base.",
    genre="action",
    temperature=1.2,    # Highly creative
    max_tokens=500,     # Longer output
    refine=True         # Coherent narrative
)

print(result["generated_text"])
```

---

## Error Handling

### HTTP Exceptions

```python
from fastapi import HTTPException

# Bad Request (400)
raise HTTPException(
    status_code=400,
    detail="user_id is required"
)

# Validation Error (422)
raise HTTPException(
    status_code=422,
    detail="Invalid genre. Must be: action, horror, scifi"
)

# Server Error (500)
raise HTTPException(
    status_code=500,
    detail="Model loading failed: GPU out of memory"
)
```

### Handling in Client

```python
try:
    response = await client.post(
        '/api/v1/story/generate',
        json=payload
    )
    result = response.json()
except HTTPException as e:
    if e.status_code == 400:
        print(f"Input error: {e.detail}")
    elif e.status_code == 500:
        print(f"Server error: {e.detail}")
```

---

## Configuration

### Environment Variables

Create `.env` file in `backend/`:

```env
# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=PlotCraft-AI
VERSION=1.0.0
ENVIRONMENT=production
DEBUG=False

# Model Configuration
SPACY_MODEL=en_core_web_sm
TEXT_GENERATION_MODEL=distilgpt2

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Optional: Redis Configuration (future)
# REDIS_URL=redis://localhost:6379/0
```

### Model Paths

Make sure these directories exist:

```
backend/plotcraft/
├── checkpoints/
│   ├── action/best_model/model.pt
│   ├── horror/best_model/model.pt
│   └── scifi/best_model/model.pt
└── tokenizer/
    ├── action/spm.model
    ├── horror/spm.model
    └── scifi/spm.model
```

---

## Debugging & Troubleshooting

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in code:
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

### Common Issues

#### "spaCy model not found"
```bash
python -m spacy download en_core_web_sm
```

#### "Model checkpoint not found at..."
- Check model file exists at `backend/plotcraft/checkpoints/<genre>/best_model/model.pt`
- Check tokenizer exists at `backend/plotcraft/tokenizer/<genre>/spm.model`

#### "GPU out of memory"
- Reduce `max_tokens` (default: 300)
- Clear model cache: `clear_model_cache()`
- Reduce batch size if using batched requests

#### "Character detection not working"
- spaCy fallback will use regex if spaCy unavailable
- Check if prompt contains proper nouns
- Minimum prompt length: 10 characters

---

## Performance Optimization

### Model Caching
Models are automatically cached after first load:
```python
# First request: loads model (~5s)
result1 = generate_story_pipeline(...)

# Subsequent requests: uses cache (~0.5s)
result2 = generate_story_pipeline(...)
```

### Token Limits
- Input: Max 500 chars (truncated automatically)
- Output: Max 300 (configurable) tokens
- Context: 512 tokens total (input + output)

### Temperature Tuning
- **0.1** = Very focused, repetitive
- **0.8** = Balanced (default)
- **1.5** = Creative but less coherent
- **2.0** = Very random

---

## Testing

### Unit Test Example

```python
import pytest
from app.services.story_service import generate_story_pipeline

@pytest.mark.asyncio
async def test_generate_story():
    result = generate_story_pipeline(
        user_id="test_user",
        prompt="Alice walked through the forest",
        genre="horror"
    )
    
    assert result["genre"] == "horror"
    assert "Alice" in result["detected_characters"]
    assert len(result["generated_text"]) > 0
    assert result["score"] is not None
```

### Running Tests

```bash
pytest backend/tests/ -v
pytest backend/tests/ --cov=app  # With coverage
```

---

## Version History

### v1.0.0 (Current)
- ✅ Multi-genre story generation (action, horror, scifi)
- ✅ Character persistence
- ✅ Twist injection
- ✅ Story refinement
- ✅ Quality scoring
- ✅ PlotCraft integration
- ✅ Transformers fallback

### Future Versions (Planned)
- [ ] v1.1.0: Redis backend for memory
- [ ] v1.2.0: User authentication & sessions
- [ ] v2.0.0: Multi-modal input (images, audio)
- [ ] v2.1.0: Extended genre support
- [ ] v3.0.0: Real-time streaming generation

---

## Support & Contributing

For issues, questions, or contributions:
1. Check this documentation first
2. Review logs: `docker logs <container>`
3. Check implementation_summary.md
4. Open an issue with:
   - Your request/response
   - Error logs
   - Steps to reproduce

---

## License & Attribution

This implementation uses:
- FastAPI (MIT)
- PyTorch (BSD)
- spaCy (MIT)
- Transformers (Apache 2.0)

See individual packages for full license details.
