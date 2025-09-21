\
import json, os
ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), 'analytics.json')

def _read():
    with open(ANALYTICS_FILE,'r',encoding='utf-8') as f:
        return json.load(f)

def _write(data):
    with open(ANALYTICS_FILE,'w',encoding='utf-8') as f:
        json.dump(data,f,indent=2)

def record_analysis(analysis):
    data = _read()
    data['ai_analyses'] = data.get('ai_analyses',0) + 1
    prior = analysis.get('priority','P2')
    data['by_priority'][prior] = data['by_priority'].get(prior,0) + 1
    _write(data)

def record_duplicate(count=1):
    data = _read()
    data['duplicates'] = data.get('duplicates',0) + count
    _write(data)

def record_escalation():
    data = _read()
    data['escalations'] = data.get('escalations',0) + 1
    _write(data)

def get_analytics():
    return _read()
