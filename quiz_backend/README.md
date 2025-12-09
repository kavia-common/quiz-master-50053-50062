# Quiz Backend (Flask)

A simple, production-ready Flask backend for a quiz application. It exposes REST endpoints to fetch questions, submit answers, retrieve scores, and a health check. CORS is enabled for development. OpenAPI/Swagger docs are available.

- Base URL (when running locally): http://localhost:3001
- API Docs: http://localhost:3001/docs

## Run

```bash
# from the container root:
python run.py
```

The service listens on port 3001.

## Endpoints

### Health
GET /api/health

- Response: { "status": "ok" }
- 200 OK

Curl:
```bash
curl -s http://localhost:3001/api/health
```

### Get Questions
GET /api/questions

- Returns an array of questions without exposing correct answers.
- Shape:
  [
    {
      "id": number,
      "text": string,
      "options": [string, ...],
      "difficulty": string | null
    }
  ]

Curl:
```bash
curl -s http://localhost:3001/api/questions
```

### Submit Answers
POST /api/submit

- Request JSON:
  {
    "userId": "optional-string",
    "answers": [{ "questionId": number, "optionIndex": number }]
  }

- Response JSON:
  {
    "results": [{ "questionId": number, "correct": boolean }],
    "score": number,
    "total": number
  }

- Validation errors:
  { "error": "message" } with 400 status.

Curl:
```bash
curl -s -X POST http://localhost:3001/api/submit \
  -H "Content-Type: application/json" \
  -d '{
    "userId":"demo-user",
    "answers":[
      {"questionId":1,"optionIndex":2},
      {"questionId":2,"optionIndex":1}
    ]
  }'
```

### Get Score
GET /api/score?userId=demo-user

- Returns last computed score for the given user.
- If none recorded:
  { "message": "No score recorded for user.", "userId": "demo-user", "score": 0 }

Curl:
```bash
curl -s "http://localhost:3001/api/score?userId=demo-user"
```

## Notes

- This service uses an in-memory data store for questions and user scores. Data resets when the process restarts.
- For development, CORS is enabled for all origins.
- API documentation is powered by flask-smorest and available at /docs.
