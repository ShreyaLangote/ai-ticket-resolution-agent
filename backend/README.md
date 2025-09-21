# PriorityOps Enhanced Backend

This enhanced backend adds:
- Knowledge-base agent (kb_agent.py) with embedding-based similarity search (RAG-lite)
- Analytics tracking (analytics.py)
- Health-check agent (health_agent.py) that runs scheduled simulated checks and saves reports
- Escalation agent to send Slack notifications or SMTP emails (escalation_agent.py)
- AI agent (ai_agent.py) using OpenAI fallback; Bedrock code hooks included

## Quick start
1. Python 3.10+
2. Copy `.env.example` to `.env` and set keys (recommended: OPENAI_API_KEY)
3. Install deps: `pip install -r requirements.txt`
4. Run: `uvicorn app:app --reload --port 8000`

Endpoints:
- GET / -> health
- GET /tickets -> list tickets
- POST /tickets -> create
- GET /analyze/{id} -> analyze ticket with AI, diagnostics, records analytics
- GET /duplicates -> run duplicate detection
- POST /escalate/{id} -> escalate (sends Slack/email if configured)
- GET /analytics -> view analytics
- GET /health-report -> latest health reports
- POST /kb/search -> {"query":"..."} returns similar KB articles
