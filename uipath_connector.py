# UiPath API connector
# Loads settings dynamically from the SQLite database or fallback to environment variables.

import requests
import os
import sqlite3
from dotenv import load_dotenv

load_dotenv()

def get_uipath_credentials() -> dict:
    org = ""
    tenant = ""
    access_token = ""
    
    # Try reading from SQLite settings first
    try:
        conn = sqlite3.connect("legalease.db")
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        conn.commit()
        
        c.execute("SELECT key, value FROM settings")
        rows = c.fetchall()
        conn.close()
        
        settings_dict = {row[0]: row[1] for row in rows}
        org = settings_dict.get("uipath_org", "")
        tenant = settings_dict.get("uipath_tenant", "")
        access_token = settings_dict.get("uipath_access_token", "")
    except Exception as e:
        print(f"Error reading settings from DB: {e}")

    # Fallback to .env if not found in DB
    if not org:
        org = os.getenv("UIPATH_ORG", "")
    if not tenant:
        tenant = os.getenv("UIPATH_TENANT", "")
    if not access_token:
        access_token = os.getenv("UIPATH_ACCESS_TOKEN", "")

    return {
        "org": org.strip(),
        "tenant": tenant.strip(),
        "access_token": access_token.strip()
    }

def create_case_in_maestro(case_id: str, issue_type: str, problem: str) -> dict:
    creds = get_uipath_credentials()
    
    if not creds["org"] or not creds["tenant"] or not creds["access_token"]:
        # Return a premium mock response simulating UiPath Orchestration Case flow
        return {
            "status": "mock",
            "case_id": case_id,
            "message": "Orchestrated in sandbox (no credentials set)",
            "uipath_link": "https://cloud.uipath.com/mock-tenant/maestro/cases"
        }

    headers = {
        "Authorization": f"Bearer {creds['access_token']}",
        "Content-Type": "application/json"
    }

    payload = {
        "title": f"LegalEase — {issue_type} | {case_id}",
        "description": problem,
        "customData": {
            "caseId": case_id,
            "issueType": issue_type
        }
    }

    try:
        response = requests.post(
            f"https://cloud.uipath.com/{creds['org']}/{creds['tenant']}/maestro_/api/Case/Create",
            headers=headers,
            json=payload
        )
        if response.status_code in (200, 201):
            res_json = response.json()
            res_json["status"] = "created"
            return res_json
        else:
            err_text = response.text
            if "<html>" in err_text.lower():
                import re
                title_match = re.search(r"<title>(.*?)</title>", err_text, re.IGNORECASE)
                if title_match:
                    err_text = title_match.group(1).strip()
                else:
                    err_text = "HTML Error Response"
            else:
                # Limit message size
                err_text = err_text[:120] + ("..." if len(err_text) > 120 else "")
                
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {err_text}"
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}