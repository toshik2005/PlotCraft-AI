# Architecture Documentation
## PlotCraft-AI

### System Architecture

```
┌─────────────┐         ┌─────────────┐
│   React     │  HTTP   │   FastAPI   │
│  Frontend   │ ◄─────► │   Backend   │
└─────────────┘         └─────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  ML Models      │
                    │  - GPT-2        │
                    │  - spaCy        │
                    │  - scikit-learn │
                    └─────────────────┘
```

### Backend Architecture

#### Layer Structure
1. **API Layer** (`app/api/`)
   - FastAPI routes
   - Request/response handling
   - Input validation

2. **Service Layer** (`app/services/`)
   - Business logic
   - Orchestration
   - Error handling

3. **Model Layer** (`app/models/`)
   - ML model wrappers
   - Model loading
   - Inference

4. **Utils Layer** (`app/utils/`)
   - Text preprocessing
   - Validation
   - Helpers

5. **Schema Layer** (`app/schemas/`)
   - Pydantic models
   - Request/response schemas

### Frontend Architecture

#### Component Structure
- **Pages**: Main page components
- **Components**: Reusable UI components
- **Services**: API communication
- **Styles**: CSS files

### Data Flow

1. User inputs story text
2. Frontend sends request to API
3. API validates input
4. Service layer processes request
5. Model layer generates output
6. Response sent back to frontend
7. Frontend displays results

### Technology Stack

**Backend:**
- FastAPI: Web framework
- Transformers: Text generation
- spaCy: NLP and NER
- scikit-learn: Genre classification
- Pydantic: Data validation

**Frontend:**
- React: UI framework
- Axios: HTTP client
- CSS: Styling

### API Design

**RESTful endpoints:**
- `POST /api/v1/story/continue`
- `POST /api/v1/genre/detect`
- `POST /api/v1/twist/generate`
- `POST /api/v1/score/story`
- `POST /api/v1/score/characters`

**Response format:**
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Security Considerations
- Input validation
- CORS configuration
- Error handling
- Rate limiting (future)

### Scalability
- Stateless API design
- Model lazy loading
- Caching (future)
- Horizontal scaling (future)
