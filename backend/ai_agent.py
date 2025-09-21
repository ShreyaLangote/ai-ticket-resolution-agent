import os, json, re
from dotenv import load_dotenv
load_dotenv()

#  AWS Setup 
import boto3

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

USE_AWS = bool(AWS_ACCESS_KEY and AWS_SECRET_KEY)

if USE_AWS:
    comprehend = boto3.client(
        "comprehend",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )
else:
    comprehend = None

# ---------------- OpenAI Setup ----------------
USE_OPENAI = os.getenv('USE_OPENAI', 'true').lower() in ('1', 'true', 'yes')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if USE_OPENAI and OPENAI_API_KEY:
    import openai
    openai.api_key = OPENAI_API_KEY
else:
    USE_OPENAI = False  # fallback if key missing


# ---------------- Utils ----------------
def parse_json_like(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r'(\{[\s\S]*\})', text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    return {'raw': text}


# ---------------- Classification ----------------
def classify_and_suggest(description: str):
    """Return dict: priority, confidence, suggestion, diagnostics"""

    # --- First try AWS Comprehend ---
    if USE_AWS and comprehend:
        try:
            lang = comprehend.detect_dominant_language(Text=description)
            lang_code = lang["Languages"][0]["LanguageCode"]

            sentiment = comprehend.detect_sentiment(Text=description, LanguageCode=lang_code)
            key_phrases = comprehend.detect_key_phrases(Text=description, LanguageCode=lang_code)

            priority = "P3"
            if sentiment["Sentiment"] == "NEGATIVE":
                priority = "P1"
            elif sentiment["Sentiment"] == "NEUTRAL":
                priority = "P2"

            return {
                "priority": priority,
                "confidence": 0.9,
                "suggestion": "Escalate immediately" if priority == "P1" else "Monitor and respond",
                "diagnostics": [kp["Text"] for kp in key_phrases["KeyPhrases"]]
            }
        except Exception as e:
            print(f"[WARN] AWS Comprehend failed: {e}")

    # --- Next try OpenAI ---
    if USE_OPENAI:
        try:
            prompt = (
                "Classify support tickets as P1, P2, or P3. "
                "Return ONLY JSON with keys: priority, confidence, suggestion, diagnostics."
                f"\nTicket: {description}\nOutput JSON:"
            )
            resp = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[{'role':'user','content':prompt}],
                max_tokens=200
            )
            parsed = parse_json_like(resp['choices'][0]['message']['content'])
            return {
                'priority': parsed.get('priority', 'P2'),
                'confidence': parsed.get('confidence', parsed.get('score', 0.6)),
                'suggestion': parsed.get('suggestion', parsed.get('raw')),
                'diagnostics': parsed.get('diagnostics', [])
            }
        except Exception as e:
            print(f"[WARN] OpenAI failed: {e}")

    # --- Finally, fallback rule-based ---
    return rule_based(description)


def rule_based(description: str):
    desc = description.lower()
    if 'vpn' in desc: 
        return {'priority':'P1','confidence':0.9,'suggestion':'Restart VPN service','diagnostics':['vpn_status']}
    if 'disk' in desc or 'storage' in desc: 
        return {'priority':'P1','confidence':0.92,'suggestion':'Free up disk','diagnostics':['disk_usage']}
    if 'password' in desc: 
        return {'priority':'P2','confidence':0.8,'suggestion':'Reset password','diagnostics':[]}
    return {'priority':'P3','confidence':0.5,'suggestion':'Requires human triage','diagnostics':[]}


# ---------------- Embeddings ----------------
def get_embedding(text: str):
    """Return embedding list using OpenAI, else fallback"""
    if USE_OPENAI:
        try:
            resp = openai.Embedding.create(model='text-embedding-3-small', input=text)
            return resp['data'][0]['embedding']
        except:
            pass
    # Fallback pseudo-embedding
    vec = [float((ord(c) % 10)/10.0) for c in text[:256]]
    vec += [0.0]*(1536-len(vec))
    return vec


# ---------------- Escalation ----------------
def generate_escalation_summary(ticket: dict, analysis: dict):
    """Return short escalation JSON"""
    if USE_OPENAI:
        try:
            prompt = (
                'Produce a short escalation JSON with keys: issue, ai_tried, next_steps.'
                f"\nTicket: {ticket.get('description','')}\nAnalysis: {json.dumps(analysis)}\nOutput JSON:"
            )
            resp = openai.ChatCompletion.create(
                model='gpt-4o-mini',
                messages=[{'role':'user','content':prompt}],
                max_tokens=200
            )
            parsed = parse_json_like(resp['choices'][0]['message']['content'])
            return {
                'issue': parsed.get('issue', ticket.get('description','')),
                'ai_tried': parsed.get('ai_tried', analysis.get('suggestion','')),
                'next_steps': parsed.get('next_steps', ['Investigate manually'])
            }
        except Exception:
            return rule_based_escalation(ticket, analysis)
    else:
        return rule_based_escalation(ticket, analysis)


def rule_based_escalation(ticket, analysis):
    return {
        'issue': ticket.get('description',''),
        'ai_tried': analysis.get('suggestion',''),
        'next_steps': ['Investigate logs', 'Reach out to engineer']
    }
