\
import os, json, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from diagnostics import run_local_diagnostics

REPORT_FILE = os.path.join(os.path.dirname(__file__), 'health_reports.json')

def _append(report):
    arr = []
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE,'r',encoding='utf-8') as f:
            try:
                arr = json.load(f)
            except Exception:
                arr = []
    arr.insert(0, report)
    arr = arr[:20]  # keep last 20
    with open(REPORT_FILE,'w',encoding='utf-8') as f:
        json.dump(arr,f,indent=2)

def run_health_check():
    report = {
        'timestamp': datetime.datetime.utcnow().isoformat()+'Z',
        'issues': []
    }
    diags = run_local_diagnostics()
    report['issues'] = diags
    _append(report)
    print('Health check run, issues:', diags)

scheduler = BackgroundScheduler()
scheduler.add_job(run_health_check, 'interval', minutes=30, id='health_check')
scheduler.start()

def latest_reports():
    if os.path.exists(REPORT_FILE):
        with open(REPORT_FILE,'r',encoding='utf-8') as f:
            return json.load(f)
    return []
