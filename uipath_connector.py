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

def get_uipath_base_url(org: str) -> str:
    # If organization contains 'hackathon' or 'staging', default to staging.uipath.com
    if org and ("hackathon" in org.lower() or "staging" in org.lower()):
        return "https://staging.uipath.com"
    return "https://cloud.uipath.com"

def refresh_uipath_token() -> str:
    client_id = os.getenv("UIPATH_CLIENT_ID", "")
    client_secret = os.getenv("UIPATH_CLIENT_SECRET", "")
    
    if not client_id or not client_secret:
        return ""
        
    creds = get_uipath_credentials()
    base_url = get_uipath_base_url(creds.get("org", ""))
    url = f"{base_url}/identity_/connect/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            token = response.json().get("access_token", "")
            if token:
                # Update .env file dynamically
                env_path = ".env"
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        content = f.read()
                    import re
                    if "UIPATH_ACCESS_TOKEN=" in content:
                        new_content = re.sub(r"UIPATH_ACCESS_TOKEN=.*", f"UIPATH_ACCESS_TOKEN={token}", content)
                    else:
                        new_content = content.rstrip() + f"\nUIPATH_ACCESS_TOKEN={token}\n"
                    with open(env_path, "w") as f:
                        f.write(new_content)
                
                # Also save to SQLite settings
                try:
                    conn = sqlite3.connect("legalease.db")
                    c = conn.cursor()
                    c.execute("INSERT OR REPLACE INTO settings (key, value) VALUES ('uipath_access_token', ?)", (token,))
                    conn.commit()
                    conn.close()
                except Exception:
                    pass
                
                # Update environment variables for the current process
                os.environ["UIPATH_ACCESS_TOKEN"] = token
                return token
    except Exception:
        pass
    return ""

def create_case_in_maestro(case_id: str, issue_type: str, problem: str) -> dict:
    creds = get_uipath_credentials()
    base_url = get_uipath_base_url(creds.get("org", ""))
    
    if not creds["org"] or not creds["tenant"] or not creds["access_token"]:
        # Return a premium mock response simulating UiPath Orchestration Case flow
        return {
            "status": "mock",
            "case_id": case_id,
            "message": "Queued in sandbox (no credentials)",
            "uipath_link": f"{base_url}/mock-tenant/orchestrator_/queues"
        }

    # Load folder ID from env or fallback (makes it configurable for staging vs production)
    folder_id = os.getenv("UIPATH_FOLDER_ID", "7967241").strip()

    headers = {
        "Authorization": f"Bearer {creds['access_token']}",
        "Content-Type": "application/json",
        "X-UIPATH-OrganizationUnitId": folder_id
    }

    try:
        # Step 2: Post Case details to Orchestrator Queue "LegalEaseQueue"
        queue_url = f"{base_url}/{creds['org']}/{creds['tenant']}/orchestrator_/odata/Queues/UiPathODataSvc.AddQueueItem"
        payload = {
            "itemData": {
                "Name": "LegalEaseQueue",
                "Priority": "Normal",
                "SpecificContent": {
                    "CaseId": case_id,
                    "IssueType": issue_type,
                    "ProblemDescription": problem
                }
            }
        }

        response = requests.post(queue_url, headers=headers, json=payload, timeout=10)
        
        # If queue item post fails with 401, refresh token and retry
        if response.status_code == 401:
            new_token = refresh_uipath_token()
            if new_token:
                headers["Authorization"] = f"Bearer {new_token}"
                response = requests.post(queue_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in (200, 201):
            return {
                "status": "created",
                "message": "Queued in Orchestrator",
                "uipath_link": f"{base_url}/{creds['org']}/{creds['tenant']}/orchestrator_/queues"
            }
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
                err_text = err_text[:120] + ("..." if len(err_text) > 120 else "")
                
            return {
                "status": "error",
                "message": f"HTTP {response.status_code}: {err_text}"
            }
    except Exception as e:
        return {"status": "error", "message": f"Exception: {str(e)}"}
