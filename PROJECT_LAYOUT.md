# PlotCraft-AI Project Layout & Backend Architecture

A full reference for every file, its purpose, functions, and dependencies.

---

## 1. Top-Level Project Structure

```
Xebia Project/
├── backend/                    # FastAPI + ML backend
├── frontend/                   # Next.js 15 frontend
├── docs/                       # PRD, Architecture, API docs
├── docker-compose.yml
├── requirements.txt            # Root Python deps (mirrors backend)
├── README.md
└── PROJECT_LAYOUT.md           # This file
```

---

## 2. Backend ASCII Architecture Chart

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              PLOTCRAFT-AI BACKEND                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  ENTRY POINT: run.py                                                                     │
│  ─────────────────────────────────────────────────────────────────────────────────────  │
│  • python run.py / python run.py serve  →  _run_server()  →  uvicorn(app.main:app)       │
│  • python run.py ml clean               →  _run_ml_clean()  (preprocessing)              │
│  • python run.py ml vocab               →  _run_ml_vocab()  (tokenizer)                  │
│  • python run.py ml train               →  _run_ml_train()  (LSTM training)              │
│  • python run.py ml all                 →  clean + vocab + train                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  FASTAPI APP: app/main.py                                                                │
│  ─────────────────────────────────────────────────────────────────────────────────────  │
│  • Creates FastAPI instance (title, version, description)                                │
│  • Adds CORS middleware (settings.CORS_ORIGINS)                                          │
│  • Mounts routers:                                                                       │
│      /api/story/*          routes_story                                                  │
│      /api/v1/story/*       routes_story                                                  │
│      /api/v1/genre/*       routes_genre                                                  │
│      /api/v1/score/*       routes_score                                                  │
│      /api/v1/twist/*       (routes_twist - if included)                                  │
│  • GET /                  →  root()                                                      │
│  • GET /health            →  health_check()                                              │
│  • Middleware: log_requests(request, call_next)                                          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                          │
          ┌───────────────────────────────┼───────────────────────────────┐
          ▼                               ▼                               ▼
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  API LAYER (app/api)│     │  SCHEMAS             │     │  CORE CONFIG        │
│  routes_story       │     │  story_schema.py     │     │  config.py          │
│  routes_genre       │     │  response_schema.py  │     │  constants.py       │
│  routes_score       │     │                      │     │                     │
│  routes_twist       │     │                      │     │                     │
└─────────┬───────────┘     └──────────┬──────────┘     └──────────┬──────────┘
          │                            │                           │
          ▼                            ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  SERVICE LAYER (app/services)                                                            │
│  ─────────────────────────────────────────────────────────────────────────────────────  │
│  story_service.py    │  genre_service.py   │  scoring_service.py  │  memory_service.py   │
│  twist_service.py    │                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────┘
          │                            │                           │
          ▼                            ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  MODEL LAYER (app/models)                                                                │
│  ─────────────────────────────────────────────────────────────────────────────────────  │
│  story_generator.py  │  genre_model.py     │  ner_model.py                                │
│  (HuggingFace)       │  (scikit-learn)     │  (spaCy + regex)                            │
└─────────────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│  PLOTCRAFT (optional custom LSTM)                                                        │
│  plotcraft/src/plotcraft_generator.py  →  GPT-2 style LSTM, genre-specific              │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend File-by-File Reference

### 3.1 Entry & Core

| File | Purpose | Key Functions / Classes | Libraries |
|------|---------|-------------------------|-----------|
| **run.py** | CLI entry point for server & ML pipeline | `main()`, `_run_server()`, `_run_ml_clean()`, `_run_ml_vocab()`, `_run_ml_train()`, `_run_ml_all()` | argparse, sys, pathlib, uvicorn |
| **app/main.py** | FastAPI app definition | `root()`, `health_check()`, `log_requests()` middleware | fastapi, logging |
| **app/core/config.py** | Environment-based settings | `Settings(BaseSettings)` → `settings` singleton | pydantic-settings |
| **app/core/constants.py** | Scoring weights, genre training data | `SCORING_WEIGHTS`, `GENRE_TRAINING_DATA` | — |

**config.py fields:** `API_V1_PREFIX`, `PROJECT_NAME`, `VERSION`, `SPACY_MODEL`, `TEXT_GENERATION_MODEL`, `MAX_STORY_LENGTH`, `CORS_ORIGINS`, `ENVIRONMENT`, `DEBUG`, `REQUEST_TIMEOUT`, `KEEP_ALIVE_TIMEOUT`, `GENERATION_TIMEOUT`

---

### 3.2 API Routes (app/api)

| File | Route Prefix | Endpoints | Purpose |
|------|--------------|-----------|---------|
| **routes_story.py** | `/api/story`, `/api/v1/story` | `POST /generate`, `POST /continue` | Story generation pipeline |
| **routes_genre.py** | `/api/v1/genre` | `POST /detect` | Genre detection |
| **routes_score.py** | `/api/v1/score` | `POST /story`, `POST /characters` | Score story, extract characters |
| **routes_twist.py** | `/api/v1/twist` | `POST /generate` | Twist generation |

**routes_story.py:**
- `generate_story(request)` → `generate_story_pipeline()` → `GenerateStoryResponse`
- `continue_story(request)` → `get_genre()`, `get_characters()`, `continue_story_pipeline()` → `StoryResponse`

**routes_genre.py:**
- `detect_genre(input_data)` → `GenreService.detect_genre()` → `APIResponse`

**routes_score.py:**
- `score_story(input_data)` → `ScoringService.score_story()` → `APIResponse`
- `extract_characters(input_data)` → `MemoryService.extract_characters()`, optional `save_session_characters()` → `APIResponse`

**routes_twist.py:**
- `generate_twist(input_data)` → `TwistService.generate_twist()` → `APIResponse`

---

### 3.3 Schemas (app/schemas)

| File | Classes | Purpose |
|------|---------|---------|
| **story_schema.py** | `GenerateStoryRequest`, `GenerateStoryResponse`, `StoryRequest`, `StoryResponse`, `GenreInput`, `GenreResponse`, `TwistInput`, `TwistResponse`, `ScoreInput`, `ScoreResponse`, `CharacterInput`, `CharacterResponse`, etc. | Request/response Pydantic models |
| **response_schema.py** | `APIResponse`, `ErrorResponse` | Generic API wrapper |

**Libraries:** pydantic, typing

---

### 3.4 Services (app/services)

| File | Purpose | Key Functions / Classes | Libraries |
|------|---------|-------------------------|-----------|
| **story_service.py** | Orchestrates full story pipeline | `generate_story_pipeline()`, `continue_story_pipeline()`, `_generate_with_plotcraft_fallback()`, `_refine_story()`, `_regenerate_for_character_focus()`, `_check_character_presence()` | app.models.*, app.services.*, app.utils.*, plotcraft (optional) |
| **genre_service.py** | Genre detection, maps to PlotCraft genres | `get_genre()`, `GenreService.detect_genre()`, `_map_to_plotcraft_genres()` | genre_model, validators, text_preprocessing |
| **scoring_service.py** | Story quality scoring | `calculate_score()`, `ScoringService.score_story()` | textblob, validators, constants |
| **memory_service.py** | Character extraction & per-user persistence | `get_characters()`, `save_user_characters()`, `get_user_characters()`, `clear_user_characters()`, `MemoryService.extract_characters()`, `MemoryService.save_session_characters()` | ner_model, validators, text_preprocessing |
| **twist_service.py** | Twist injection into prompts | `apply_twist_to_prompt()`, `TwistService.generate_twist()`, `TwistType` enum, `TWIST_INSTRUCTIONS` | validators, text_preprocessing |

---

### 3.5 Models (app/models)

| File | Purpose | Key Functions / Classes | Libraries |
|------|---------|-------------------------|-----------|
| **story_generator.py** | HuggingFace text generation | `StoryGenerator` (lazy load, `generate()`), `generate_story()` | transformers |
| **genre_model.py** | TF-IDF + LogisticRegression genre classifier | `GenreModel` (train, predict, predict_proba, save, load) | sklearn, joblib |
| **ner_model.py** | Character extraction (spaCy + regex) | `NERModel`, `_extract_characters_regex()`, `_extract_explicit_name_introductions()`, `_extract_names_after_prepositions()`, `_extract_name_lists_after_group_nouns()`, `_is_name_like_token()` | spacy, re |

---

### 3.6 Utils (app/utils)

| File | Purpose | Key Functions | Libraries |
|------|---------|---------------|-----------|
| **text_preprocessing.py** | Text normalization | `clean_text()`, `truncate_text()`, `count_words()` | re |
| **validators.py** | Input validation | `validate_story_text(text, min_length, max_length)` | — |

---

### 3.7 PlotCraft (backend/plotcraft)

```
plotcraft/
├── src/
│   ├── plotcraft_generator.py   # API-facing generator (generate_text)
│   ├── model.py                 # GPT-2 style model (build_model)
│   ├── train.py                 # Training loop
│   ├── build_dataset.py         # Build HF datasets from splits
│   ├── corpus_builder.py        # Build large corpus from cleaned text
│   ├── tokenizer_builder.py     # Build SentencePiece tokenizer
│   ├── split_builder.py         # Split corpus into train/val
│   ├── prepare_horror_corpus.py # Horror-specific corpus prep
│   ├── prepare_action_corpus.py # Action-specific corpus prep
│   ├── run_pipeline.py          # Full pipeline orchestration
│   └── generate.py              # Standalone generation
├── horror_train/run_pipeline_horror.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── splits/
├── tokenizer/{genre}/spm.model
├── checkpoints/{genre}/best_model/model.pt
└── datasets/{genre}/train_blocks, val_blocks
```

| File | Purpose | Key Functions | Libraries |
|------|---------|---------------|-----------|
| **plotcraft_generator.py** | Lazy-load genre models, generate text | `generate_text()`, `_ensure_loaded()`, `_normalize_model_name()`, `PlotCraftUnavailable` | torch, sentencepiece |
| **model.py** | GPT-2 config & model | `build_model(vocab_size, block_size)` | transformers |
| **train.py** | Train PlotCraft model | `train()`, `parse_args()` | torch, sentencepiece, datasets, tqdm |
| **build_dataset.py** | Create tokenized blocks | `main()` | sentencepiece, datasets, numpy |
| **corpus_builder.py** | Cap corpus size | `main()` | argparse |
| **tokenizer_builder.py** | Train SentencePiece | — | sentencepiece |
| **split_builder.py** | Split corpus train/val | — | — |
| **prepare_horror_corpus.py** | Horror corpus prep | — | — |
| **prepare_action_corpus.py** | Action corpus prep | — | — |

---

### 3.8 Tests (backend/tests)

| File | Purpose | Test Functions |
|------|---------|----------------|
| **test_story.py** | Story API tests | Story endpoints |
| **test_genre.py** | Genre API tests | Genre detection |
| **test_score.py** | Score & character extraction tests | `test_score_story_success()`, `test_extract_characters_success()`, `test_extract_characters_lowercase_named_and_with_patterns()` |

---

## 4. Data Flow (Story Generation)

```
1. Client POST /api/v1/story/generate
       │
       ▼
2. routes_story.generate_story(GenerateStoryRequest)
       │
       ▼
3. story_service.generate_story_pipeline(user_id, prompt, genre, ...)
       │
       ├─► memory_service.get_characters(prompt)  ──► ner_model.extract_characters()
       ├─► memory_service.save_user_characters()
       ├─► memory_service.get_user_characters()
       ├─► twist_service.apply_twist_to_prompt()  (if twist)
       ├─► _generate_with_plotcraft_fallback()
       │        ├─► plotcraft.generate_text()  (if available)
       │        └─► generate_story()  (transformers fallback)
       ├─► _refine_story()  (if refine)
       ├─► _check_character_presence() → _regenerate_for_character_focus() (if needed)
       └─► scoring_service.calculate_score()  (if measure)
       │
       ▼
4. GenerateStoryResponse
```

---

## 5. Dependencies (requirements.txt)

| Package | Use |
|---------|-----|
| fastapi | Web framework |
| uvicorn[standard] | ASGI server |
| spacy | NER for character extraction |
| transformers | HuggingFace text generation (fallback) |
| scikit-learn | Genre classification (TF-IDF + LogisticRegression) |
| textblob | Sentiment & sentence parsing for scoring |
| pydantic, pydantic-settings | Config & schemas |
| joblib | Model serialization |
| python-multipart, python-dotenv | Form data, env loading |
| torch | PlotCraft model (optional) |

---

## 6. Environment Variables (.env)

| Variable | Default | Purpose |
|----------|---------|---------|
| API_V1_PREFIX | /api/v1 | API prefix |
| SPACY_MODEL | en_core_web_sm | spaCy NER model |
| TEXT_GENERATION_MODEL | distilgpt2 | HuggingFace model |
| CORS_ORIGINS | ["http://localhost:3000", "http://localhost:5173"] | Allowed origins |
| ENVIRONMENT | development | Environment name |
| DEBUG | True | Reload, verbose logs |
| REQUEST_TIMEOUT | 300 | Seconds |
| KEEP_ALIVE_TIMEOUT | 600 | Seconds |
| GENERATION_TIMEOUT | 120 | Seconds |

---

## 7. API Endpoints Summary

| Method | Path | Purpose |
|--------|------|---------|
| GET | / | Root info |
| GET | /health | Health check |
| POST | /api/v1/story/generate | Full story pipeline (user_id, story, genre, twist, refine, measure) |
| POST | /api/v1/story/continue | Legacy continuation (story, genre?) |
| POST | /api/v1/genre/detect | Detect genre (text) |
| POST | /api/v1/score/story | Score story (text) |
| POST | /api/v1/score/characters | Extract characters (text, user_id?) |
| POST | /api/v1/twist/generate | Generate twist (text, twist_type) |

---

*Generated for PlotCraft-AI. Last updated for the current codebase.*
