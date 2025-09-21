from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import os, datetime
from dotenv import load_dotenv

load_dotenv()

from db_local import load_tickets, save_tickets, get_ticket, upsert_ticket
from ai_agent import classify_and_suggest, generate_escalation_summary
from duplicate_detector import find_duplicate_groups
from diagnostics import run_local_diagnostics
from analytics import record_analysis, record_duplicate, record_escalation, get_analytics
from kb_agent import find_similar
from escalation_agent import send_slack, send_email   # ✅ this is your SendGrid-enabled file
from health_agent import latest_reports

app = FastAPI(title='PriorityOps Enhanced Backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

# -------------------- Root & Health --------------------
@app.get("/")
def root():
    return {"status": "PriorityOps Backend running"}

@app.get("/health")
def health():
    return {
        "status": "OK",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "API is running!"
    }

@app.get("/health-report")
def health_report():
    try:
        reports = latest_reports()
        return reports if reports else [{"status": "No reports yet"}]
    except Exception as e:
        return [{"status": "Error retrieving reports", "error": str(e)}]

# -------------------- Tickets --------------------
@app.get("/tickets")
def tickets():
    return load_tickets()

@app.post("/tickets")
async def create_ticket(req: Request):
    body = await req.json()
    tickets = load_tickets()
    new_id = max([t['id'] for t in tickets]) + 1 if tickets else 1
    ticket = {
        "id": new_id,
        "title": body.get("title",""),
        "description": body.get("description",""),
        "priority":"?"
    }
    tickets.append(ticket)
    save_tickets(tickets)
    return ticket

@app.get("/analyze/{ticket_id}")
def analyze(ticket_id: int):
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    try:
        analysis = classify_and_suggest(ticket.get("description",""))
        diags = run_local_diagnostics()
        analysis["diagnostics_sim"] = diags
        ticket["analysis"] = analysis
        upsert_ticket(ticket)
        record_analysis(analysis)
        return {"ticket": ticket, "analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# -------------------- Duplicates --------------------
@app.get("/duplicates")
def duplicates():
    tickets = load_tickets()
    try:
        groups = find_duplicate_groups(tickets)
        record_duplicate(len(groups))
        return {"duplicate_groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duplicate detection failed: {str(e)}")

# -------------------- Escalation --------------------
@app.post("/escalate/{ticket_id}")
def escalate(ticket_id: int):
    ticket = get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    analysis = ticket.get("analysis", {})
    try:
        esk = generate_escalation_summary(ticket, analysis)
        ticket["escalation"] = esk
        upsert_ticket(ticket)
        message = f"Escalation for Ticket {ticket['id']}: {esk.get('issue')} - Next steps: {esk.get('next_steps')}"

        # Slack safely
        try:
            slack_res = send_slack(message)
        except Exception as e:
            slack_res = {'ok': False, 'error': str(e)}

        # Email safely (now SendGrid-based)
        try:
            email_res = send_email(
                os.getenv("ALERT_EMAIL_TO") or "",
                f"Escalation: Ticket {ticket['id']}",
                message
            )
        except Exception as e:
            email_res = {'ok': False, 'error': str(e)}

        record_escalation()
        return {"escalation": esk, "slack": slack_res, "email": email_res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Escalation failed: {str(e)}")

# -------------------- Analytics --------------------
@app.get("/analytics")
def analytics():
    try:
        return get_analytics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics retrieval failed: {str(e)}")

# -------------------- Knowledge Base --------------------
@app.post("/kb/search")
async def kb_search(req: Request):
    body = await req.json()
    query = body.get("query","")
    if not query:
        raise HTTPException(status_code=400, detail="query required")
    try:
        results = find_similar(query)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"KB search failed: {str(e)}")

# -------------------- Test Alert --------------------
@app.post("/test-alert")
async def test_alert(req: Request):
    body = await req.json()
    message = body.get("message","This is a test alert")
    severity = body.get("severity","info")
    try:
        try: 
            slack_res = send_slack(f"[{severity.upper()}] {message}")
        except Exception as e: 
            slack_res = {'ok': False, 'error': str(e)}

        try: 
            email_res = send_email(
                os.getenv("ALERT_EMAIL_TO") or "",
                f"[{severity.upper()}] Test Alert", 
                message
            )
        except Exception as e: 
            email_res = {'ok': False, 'error': str(e)}

        return {
            "alert_received": True,
            "alert_message": message,
            "alert_severity": severity,
            "slack": slack_res,
            "email": email_res,
            "timestamp": datetime.datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test alert failed: {str(e)}")
