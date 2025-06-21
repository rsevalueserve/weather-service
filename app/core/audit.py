import os
import json
from datetime import datetime
from fastapi import Request

LOG_PATH = os.path.join(os.path.dirname(__file__), '../../logs/consultas.log')
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def audit_request(request: Request, endpoint: str, params: dict, ip_info: dict):
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "ip": ip_info.get("ip"),
        "ciudad": ip_info.get("ciudad"),
        "region": ip_info.get("region"),
        "pais": ip_info.get("pais"),
        "endpoint": endpoint,
        "params": params
    }
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
