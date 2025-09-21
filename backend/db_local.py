import json, os
TICKETS_FILE = os.path.join(os.path.dirname(__file__), 'tickets.json')

def load_tickets():
    with open(TICKETS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tickets(tickets):
    with open(TICKETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tickets, f, indent=2, ensure_ascii=False)

def get_ticket(ticket_id):
    tickets = load_tickets()
    for t in tickets:
        if int(t.get('id')) == int(ticket_id):
            return t
    return None

def upsert_ticket(ticket):
    tickets = load_tickets()
    for i,t in enumerate(tickets):
        if int(t.get('id')) == int(ticket.get('id')):
            tickets[i] = ticket
            save_tickets(tickets)
            return
    tickets.append(ticket)
    save_tickets(tickets)
