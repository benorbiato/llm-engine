
# LLM Verification Engine

Automated judicial process verification system powered by LLM technology for intelligent decision-making based on company business policies.

**Live Deployment:** https://llm-engine.onrender.com

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)

## Overview

This application automates the verification and eligibility assessment of judicial processes against predefined business policies. The system leverages LLM technology through Groq API to provide intelligent analysis and transparent decision-making.

### Key Features

- Automated process analysis and verification
- Structured decision outcomes: approved, rejected, or incomplete
- Policy-driven verification with clear justifications
- Batch processing for multiple processes simultaneously
- Caching mechanism to optimize API usage
- Comprehensive analytics and monitoring
- RESTful API with automatic documentation
- Streamlit web interface for user interaction

### Architecture

```
app/
├── api/                    # API routes and middleware
│   ├── middleware/         # Logging and error handling
│   └── routes/            # Endpoint definitions
├── config.py              # Configuration management
├── domain/                # Business logic and policies
├── external/              # External service integrations
├── repositories/          # Data persistence
├── schemas/               # Request/response models
├── use_cases/             # Business use case implementations
└── utils/                 # Utilities (logging, caching)
```

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Groq API key (obtain at https://console.groq.com/)
- Docker and Docker Compose (optional, for containerized deployment)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd llm-engine
```

2. Create and activate virtual environment:
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
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

### Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=mixtral-8x7b-32768
MAX_TOKENS=2048
TEMPERATURE=0.3
LOG_LEVEL=INFO
ENVIRONMENT=development
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Running the Application

### API Only

```bash
python app/main.py
```

The API will be available at `http://localhost:8000`

Access API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Using Docker Compose

```bash
docker-compose up
```

Services will be available at:
- API: http://localhost:8000
- UI (Streamlit): http://localhost:8501

### Stopping the Application

```bash
docker-compose down
```

## API Endpoints

### Health & Monitoring

#### GET `/health`
Check application health status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-11-26T10:30:00.000000",
  "version": "1.0.0"
}
```

#### GET `/monitoring/api-status`
Get API configuration and service status.

**Response:**
```json
{
  "status": "operational",
  "api": {
    "provider": "Groq",
    "model": "mixtral-8x7b-32768",
    "api_key_configured": true,
    "max_tokens_per_request": 2048
  },
  "cache": {
    "total_entries": 125,
    "cache_hits": 450,
    "cache_misses": 50
  }
}
```

#### GET `/monitoring/cache-stats`
Get cache performance statistics.

**Response:**
```json
{
  "status": "success",
  "cache": {
    "total_entries": 125,
    "cache_hits": 450,
    "cache_misses": 50
  }
}
```

#### POST `/monitoring/cache/clear`
Clear all cached verification results.

**Response:**
```json
{
  "status": "success",
  "message": "Cache cleared successfully"
}
```

### Verification Endpoints

#### POST `/verify/`
Verify a single judicial process.

**Request Body:**
```json
{
  "numeroProcesso": "0001234-56.2023.4.05.8100",
  "classe": "Cumprimento de Sentença contra a Fazenda Pública",
  "orgaoJulgador": "19ª VARA FEDERAL - SOBRAL/CE",
  "ultimaDistribuicao": "2024-11-18T23:15:44.130Z",
  "assunto": "Rural (Art. 48/51)",
  "segredoJustica": false,
  "justicaGratuita": true,
  "siglaTribunal": "TRF5",
  "esfera": "Federal",
  "valorCondenacao": 67592,
  "documentos": [
    {
      "id": "DOC-1-1",
      "dataHoraJuntada": "2023-09-10T10:12:05.000",
      "nome": "Sentença de Mérito",
      "texto": "PODER JUDICIÁRIO..."
    }
  ],
  "movimentos": [
    {
      "dataHora": "2024-01-20T11:22:33.000",
      "descricao": "Iniciado cumprimento definitivo de sentença."
    }
  ],
  "honorarios": {
    "contratuais": 6000,
    "periciais": 1200,
    "sucumbenciais": 3000
  }
}
```

**Response (200 OK):**
```json
{
  "numeroProcesso": "0001234-56.2023.4.05.8100",
  "decision": "approved",
  "rationale": "Process meets all eligibility criteria and is approved for acquisition.",
  "citations": [
    {
      "policy_id": "POL-1",
      "explanation": "Process is in final judgment and execution phase"
    },
    {
      "policy_id": "POL-2",
      "explanation": "Condemnation value is informed: R$ 67,592.00"
    }
  ],
  "confidence": 0.95,
  "processingTimeMs": 234,
  "processedAt": "2024-11-26T10:30:00.000000"
}
```

#### POST `/verify/batch`
Verify multiple processes in a single batch request (up to 50 processes).

**Request Body:**
```json
{
  "processos": [
    {
      "numeroProcesso": "0001234-56.2023.4.05.8100",
      ...
    },
    {
      "numeroProcesso": "0001235-56.2023.4.05.8100",
      ...
    }
  ]
}
```

**Response:**
```json
{
  "batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "total": 2,
  "processados": 2,
  "erros": 0,
  "tempo_total_ms": 450,
  "resultados": [
    {
      "numeroProcesso": "0001234-56.2023.4.05.8100",
      "decision": "approved",
      "rationale": "...",
      "citations": [...],
      "confidence": 0.95
    },
    {
      "numeroProcesso": "0001235-56.2023.4.05.8100",
      "decision": "rejected",
      "rationale": "...",
      "citations": [...]
    }
  ]
}
```

### Process History

#### GET `/process/{numero_processo}`
Retrieve verification history for a specific process.

**Response:**
```json
{
  "numeroProcesso": "0001234-56.2023.4.05.8100",
  "ultimaVerificacao": "2024-11-26T10:30:00.000000",
  "verificacoes": 1,
  "ultimaDecisao": "approved",
  "historico": [
    {
      "numeroProcesso": "0001234-56.2023.4.05.8100",
      "decision": "approved",
      "rationale": "...",
      "citations": [...]
    }
  ]
}
```

#### GET `/process/`
List all verified processes with optional filtering.

**Query Parameters:**
- `decision` (optional): Filter by decision type (approved, rejected, incomplete)
- `limit` (default: 100): Maximum number of results (1-1000)
- `offset` (default: 0): Number of items to skip for pagination

**Response:**
```json
[
  {
    "numeroProcesso": "0001234-56.2023.4.05.8100",
    "decision": "approved",
    "rationale": "...",
    "citations": [...],
    "confidence": 0.95,
    "processingTimeMs": 234,
    "processedAt": "2024-11-26T10:30:00.000000"
  }
]
```

### Analytics

#### GET `/analytics/summary`
Get comprehensive analytics summary of all verifications.

**Response:**
```json
{
  "total_verificacoes": 150,
  "aprovados": 95,
  "rejeitados": 40,
  "incompletos": 15,
  "taxa_aprovacao_percentual": 63.33,
  "taxa_rejeicao_percentual": 26.67,
  "tempo_medio_processamento_ms": 245.50,
  "politicas_mais_citadas": [
    {
      "id": "POL-1",
      "titulo": "Final Judgment Status",
      "usos": 148
    }
  ],
  "timestamp": "2024-11-26T10:30:00.000000"
}
```

#### GET `/analytics/policies-usage`
Get usage statistics for each policy.

**Response:**
```json
{
  "POL-1": 148,
  "POL-2": 145,
  "POL-3": 89,
  "POL-4": 78,
  "POL-5": 23
}
```

#### GET `/analytics/decision-distribution`
Get distribution of decisions across all verifications.

**Response:**
```json
{
  "approved": 95,
  "rejected": 40,
  "incomplete": 15,
  "total": 150
}
```

#### GET `/analytics/processing-time`
Get processing time statistics.

**Response:**
```json
{
  "media_ms": 245.50,
  "minimo_ms": 120,
  "maximo_ms": 1200,
  "total_processamentos": 150
}
```

#### GET `/analytics/top-policies`
Get the most impactful policies.

**Query Parameters:**
- `limit` (default: 5): Number of policies to return (1-20)

**Response:**
```json
[
  {
    "id": "POL-1",
    "titulo": "Final Judgment Status",
    "categoria": "Process Status",
    "descricao": "Process must be in final judgment (transitado em julgado) phase",
    "usos": 148
  },
  {
    "id": "POL-2",
    "titulo": "Condemnation Value Required",
    "categoria": "Financial",
    "descricao": "Condemnation value must be informed",
    "usos": 145
  }
]
```

#### GET `/analytics/decision-by-sphere`
Get decision distribution by judicial sphere (Federal, State, Labor).

**Response:**
```json
{
  "Federal": {
    "approved": 80,
    "rejected": 30,
    "incomplete": 10
  },
  "Estadual": {
    "approved": 10,
    "rejected": 8,
    "incomplete": 3
  },
  "Trabalhista": {
    "approved": 5,
    "rejected": 2,
    "incomplete": 2
  }
}
```

## Configuration

### Groq API Setup

1. Create an account at https://console.groq.com/
2. Generate an API key
3. Add to `.env` file as `GROQ_API_KEY`
4. Monitor usage in the Groq console

### Logging

The application uses structured JSON logging. Logs are output to console and can be configured via the `LOG_LEVEL` environment variable:
- DEBUG: Verbose information
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages

## Docker Deployment

### Build Image

```bash
docker build -t llm-engine:latest .
```

### Run with Docker

```bash
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key_here \
  -e ENVIRONMENT=production \
  llm-engine:latest
```

### Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

## Cloud Deployment

### Render.com

1. Push code to GitHub repository
2. Create new Web Service on Render
3. Connect your GitHub repository
4. Set environment variables:
   - GROQ_API_KEY
   - ENVIRONMENT=production
   - LOG_LEVEL=INFO
5. Deploy

The application will be available at your Render service URL.

### Other Platforms (Railway, Heroku, etc.)

Similar process:
1. Connect GitHub repository
2. Set environment variables
3. Deploy with Dockerfile
4. Verify health endpoint: `/health`

## Troubleshooting

### API Connection Error

**Problem:** Cannot connect to API
**Solution:** Ensure the application is running and check if port 8000 is available.

```bash
# Check if port is in use
netstat -tuln | grep 8000
```

### Missing API Key

**Problem:** "GROQ_API_KEY not configured"
**Solution:** Add your Groq API key to `.env` file and restart the application.

### Port Already in Use

**Problem:** "Port 8000 is already in use"
**Solution:** Use a different port:

```bash
docker run -p 8001:8000 \
  -e GROQ_API_KEY=your_key_here \
  llm-engine:latest
```

### Cache Issues

**Problem:** Stale results from cache
**Solution:** Clear cache using the endpoint:

```bash
curl -X POST http://localhost:8000/monitoring/cache/clear
```

### High API Usage

**Problem:** Running out of Groq API credits
**Solution:**
1. Monitor usage at https://console.groq.com/
2. Enable caching to reduce API calls
3. Check cache statistics: `/monitoring/cache-stats`
4. Consider increasing refresh credits

## Performance

- Average verification processing time: 200-500ms
- Cache hit rate: 70-90% for repeated processes
- Batch processing: 50 processes in 5-10 seconds
- Concurrent requests: Supported with rate limiting

## Support and Resources

- API Documentation: http://localhost:8000/docs
- Groq Console: https://console.groq.com/
- Issues: Create an issue in the GitHub repository

## License

This project is licensed under the MIT License. See LICENSE file for details.
