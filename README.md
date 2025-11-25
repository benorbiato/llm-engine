Judicial Process Verification Engine

LLM-powered system for automated verification and eligibility assessment of judicial processes based on company business policies.

Table of Contents

- Project Overview
- Architecture
- Features
- Requirements
- Installation
- Local Execution
- API Documentation
- Configuration
- Deployment

Project Overview

This application automates the verification of judicial processes, determining if they should be approved, rejected, or marked as incomplete for credit purchase. The system uses Claude API (Large Language Model) to provide explainable decisions based on predefined business policies.

The system implements clean architecture principles and structured logging to ensure maintainability, testability, and observability.

Architecture

The project follows Clean Architecture with clear separation of concerns:

```
src/
├── core/                          # Core business logic
│   ├── domain/                    # Domain models and policies
│   │   ├── entities.py            # Judicial process entities
│   │   ├── policy.py              # Business policy rules
│   │   └── enums/                 # Domain enumerations
│   ├── application/               # Application services
│   │   └── services/              # Business logic services
│   └── infrastructure/            # Technical infrastructure
│       ├── config.py              # Configuration management
│       ├── logger_service.py      # Structured logging
│       └── llm_adapter.py         # Claude API integration
├── api/                           # API layer
│   ├── routers/                   # API endpoints
│   │   ├── health_router.py       # Health check endpoint
│   │   └── verification_router.py # Verification endpoint
│   └── schemas.py                 # Pydantic request/response models
├── entrypoints/                   # Application entry points
│   ├── main_api.py                # FastAPI application factory
│   └── main_ui.py                 # Streamlit UI
└── __init__.py
```

Key Design Decisions

- Layered Architecture: Separation between domain, application, and infrastructure layers
- Dependency Injection: Clean dependency management via FastAPI Depends
- Policy-Driven Verification: Business rules encapsulated in policy service
- Structured Logging: JSON-formatted logs for better observability
- Type Safety: Pydantic models for all request/response validation

Features

Verification Capabilities

- Automated analysis of judicial processes against company policies
- Multiple decision outcomes: approved, rejected, incomplete
- Clear justification with policy references for each decision
- Processing of complex process documents and movements

Business Policies Implemented

- POL-1: Only approved processes in final judgment (transitado em julgado) and execution phase
- POL-2: Require condemnation value to be informed
- POL-3: Reject if condemnation value < R$ 1,000
- POL-4: Reject labor sphere (trabalhista) processes
- POL-5: Reject if author died without inventory habitation
- POL-6: Reject delegation without reserve of powers
- POL-7: Require fees information when applicable
- POL-8: Mark incomplete if essential documents missing

API Features

- RESTful endpoints with FastAPI
- Automatic OpenAPI/Swagger documentation
- Health check endpoint
- Structured error handling
- Request/response validation with Pydantic

User Interface

- Streamlit-based web application
- Intuitive process data input forms
- Real-time verification results
- Visual decision indicators (approved/rejected/incomplete)
- Policy reference details

Observability

- Structured JSON logging with timestamps
- LangSmith integration ready
- Request tracking with process numbers
- Error logging and debugging information

Requirements

- Python 3.11+
- Docker and Docker Compose (for containerized execution)
- Anthropic API Key (for Claude LLM)
- Optional: LangSmith API Key (for enhanced monitoring)

Installation

Local Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd llm-engine
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure environment variables:

```bash
cp env-example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

Docker Setup

1. Build the Docker image:

```bash
docker build -t judicial-verification .
```

2. Run with docker-compose:

```bash
docker-compose up -d
```

This will start:
- API on http://localhost:8000
- UI on http://localhost:8501

Local Execution

Running the API Only

```bash
uvicorn src.entrypoints.main_api:app --host 0.0.0.0 --port 8000 --reload
```

Access the API documentation at: http://localhost:8000/api/docs

Running the UI Only

```bash
streamlit run src/entrypoints/main_ui.py
```

Access the UI at: http://localhost:8501

Running Both Services Locally

```bash
docker-compose up
```

API Documentation

Base URL

- Local: http://localhost:8000
- Docker: http://localhost:8000

Endpoints

Health Check

Endpoint: GET /health
Description: System health verification
Response: 200 OK

```json
{
  "status": "operational",
  "version": "1.0.0",
  "timestamp": "2024-11-24T10:30:00.000000"
}
```

Process Verification

Endpoint: POST /v1/verify
Description: Analyze and verify a judicial process
Content-Type: application/json

Request Body:

```json
{
  "process": {
    "numeroProcesso": "0001234-56.2023.4.05.8100",
    "classe": "Cumprimento de Sentença contra a Fazenda Pública",
    "orgaoJulgador": "19ª VARA FEDERAL - SOBRAL/CE",
    "ultimaDistribuicao": "2024-11-18T23:15:44.130Z",
    "assunto": "Rural (Art. 48/51)",
    "segredoJustica": false,
    "justicaGratuita": true,
    "siglaTribunal": "TRF5",
    "esfera": "Federal",
    "documentos": [
      {
        "id": "DOC-1-1",
        "dataHoraJuntada": "2023-09-10T10:12:05.000",
        "nome": "Sentença de Mérito",
        "texto": "PODER JUDICIÁRIO...",
      }
    ],
    "movimentos": [
      {
        "dataHora": "2024-01-20T11:22:33.000",
        "descricao": "Iniciado cumprimento definitivo de sentença."
      }
    ],
    "valorCondenacao": 67592,
    "honorarios": {
      "contratuais": 6000,
      "periciais": 1200,
      "sucumbenciais": 3000
    }
  }
}
```

Response: 200 OK

```json
{
  "decision": "approved",
  "rationale": "Process meets all eligibility criteria and is approved for acquisition.",
  "references": [
    {
      "policy_id": "POL-1",
      "explanation": "Process is in final judgment (transitado em julgado) and execution phase"
    },
    {
      "policy_id": "POL-2",
      "explanation": "Condemnation value is informed: R$ 67,592.00"
    }
  ],
  "process_number": "0001234-56.2023.4.05.8100"
}
```

API Documentation Interface

Access the interactive API documentation:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI Schema: http://localhost:8000/api/openapi.json

Configuration

Environment Variables

Create a .env file with the following variables:

```
ANTHROPIC_API_KEY=your_api_key_here
LLM_MODEL=claude-3-5-sonnet-20241022
LLM_TEMPERATURE=0.3
LLM_MAX_TOKENS=2048
LANGSMITH_API_KEY=optional_langsmith_key
LANGSMITH_PROJECT=judicial-process-verification
LANGSMITH_ENABLED=false
LOG_LEVEL=INFO
LOG_FORMAT=json
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

Configuration Management

Configuration is managed through Pydantic Settings (src/core/infrastructure/config.py):

- Loads from environment variables
- Validates types automatically
- Provides sensible defaults
- Can be extended for additional settings

Logging Configuration

The application uses structured JSON logging:

- All logs are formatted as JSON
- Includes timestamp, level, logger name, and message
- Extra fields for context information
- Suitable for log aggregation and monitoring

Log Output Example:

```json
{
  "timestamp": "2024-11-24T10:30:00.000000",
  "level": "INFO",
  "logger": "judicial_process_verification",
  "message": "Process verification completed",
  "module": "verification_service",
  "function": "execute",
  "line": 45,
  "extra_fields": {
    "process_number": "0001234-56.2023.4.05.8100",
    "decision": "approved"
  }
}
```

Deployment

Docker Deployment

Local Docker Build and Run

```bash
# Build image
docker build -t judicial-verification:latest .

# Run API
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key_here \
  judicial-verification:latest

# Run UI
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your_key_here \
  judicial-verification:latest \
  streamlit run src/entrypoints/main_ui.py
```

Docker Compose Full Stack

```bash
# Create .env file with your API key
cp env-example .env
echo "ANTHROPIC_API_KEY=your_key_here" >> .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Cloud Deployment (Railway, Render, Heroku)

General Steps

1. Push code to GitHub
2. Connect repository to hosting platform
3. Set environment variables:
   - ANTHROPIC_API_KEY
   - LLM_MODEL
   - LOG_LEVEL
4. Deploy using Dockerfile
5. Verify health endpoint

Railway Deployment

1. Create new project on Railway
2. Connect GitHub repository
3. Add environment variables in project settings
4. Railway auto-detects Dockerfile
5. Deploy and access via provided URL

Render Deployment

1. Create new Web Service on Render
2. Connect GitHub repository
3. Specify start command: uvicorn src.entrypoints.main_api:app --host 0.0.0.0 --port 8000
4. Set environment variables
5. Deploy

Monitoring and Observability

LangSmith Integration

To enable LangSmith monitoring:

1. Set LANGSMITH_ENABLED=true in .env
2. Add LANGSMITH_API_KEY
3. Set LANGSMITH_PROJECT name

LangSmith will automatically track:
- LLM calls
- Latency
- Token usage
- Errors and exceptions

Health Monitoring

The application includes a health check endpoint that can be used with container orchestration:

```bash
curl http://localhost:8000/health
```

Docker Health Check

The Dockerfile includes HEALTHCHECK directive for monitoring container health.

Testing

Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=src
```

Testing the API

Using curl:

```bash
curl -X POST http://localhost:8000/v1/verify \
  -H "Content-Type: application/json" \
  -d @test_process.json
```

Using the Streamlit UI

1. Navigate to http://localhost:8501
2. Fill in process information
3. Submit for verification
4. View results

Development

Project Structure Explanation

- Domain Layer: Contains business entities, enumerations, and policies
- Application Layer: Contains business logic services and use cases
- Infrastructure Layer: Contains technical implementations (logging, LLM adapter, config)
- API Layer: Contains HTTP endpoints and request/response schemas
- Entrypoints: Application entry points for API and UI

Key Design Patterns

- Repository Pattern: Abstracts data access (extensible for databases)
- Service Pattern: Encapsulates business logic
- Adapter Pattern: Integrates external services (Claude API)
- Dependency Injection: Manages dependencies cleanly
- Policy Pattern: Encapsulates business rules

Adding New Policies

1. Add policy rule to src/core/domain/policy.py
2. Implement verification logic in PolicyVerificationService
3. Add corresponding tests
4. Update documentation

Extending the Application

1. Add new domain entities in src/core/domain/entities.py
2. Create new services in src/core/application/services/
3. Add new endpoints in src/api/routers/
4. Update schemas in src/api/schemas.py

Error Handling

The application implements comprehensive error handling:

- Validation errors return 422 with details
- Business logic errors return appropriate HTTP status codes
- Unhandled exceptions return 500 with generic message
- All errors are logged with full context

LLM Integration Details

Claude API Usage

- Model: claude-3-5-sonnet-20241022 (configurable)
- Temperature: 0.3 (low temperature for consistent decisions)
- Max Tokens: 2048 (sufficient for detailed analysis)

The application uses Claude for:
- Detailed process analysis (optional, currently using deterministic rules)
- Generating explanations
- Handling complex edge cases

Error Handling

API errors are handled gracefully:

- Connection errors logged and reported
- Rate limiting respected with backoff
- Fallback to policy-based decisions if LLM fails

Troubleshooting

Common Issues

API Connection Error

Problem: "Connection Error: Cannot reach API at http://localhost:8000"
Solution: Ensure API is running with: uvicorn src.entrypoints.main_api:app --host 0.0.0.0 --port 8000

Missing ANTHROPIC_API_KEY

Problem: "APIError: Invalid API key provided"
Solution: Set ANTHROPIC_API_KEY in .env file with valid Anthropic API credentials

Docker Port Conflict

Problem: "Port 8000 is already in use"
Solution: Use different port: docker run -p 8001:8000 ...

Performance Considerations

- Typical verification latency: < 1 second
- Concurrent requests: Limited by LLM rate limits
- Memory usage: ~500MB per container
- Disk space: ~200MB for image and dependencies

Contributing

To contribute:

1. Fork the repository
2. Create feature branch (git checkout -b feature/improvement)
3. Make changes following code style
4. Add tests for new functionality
5. Commit changes (git commit -am 'Add improvement')
6. Push to branch (git push origin feature/improvement)
7. Create Pull Request

License

This project is licensed under the MIT License. See LICENSE file for details.

Support

For issues or questions:

1. Check the troubleshooting section
2. Review API documentation at http://localhost:8000/api/docs
3. Check application logs: docker-compose logs api
4. Create an issue in the GitHub repository

Changelog

Version 1.0.0 (2024-11-24)

- Initial release
- Policy-based process verification
- FastAPI REST endpoints
- Streamlit UI
- Structured logging
- Docker deployment
- Claude API integration
