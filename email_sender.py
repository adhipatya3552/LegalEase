import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

import sqlite3

def get_gmail_credentials() -> tuple:
    sender = ""
    password = ""
    try:
        conn = sqlite3.connect("legalease.db")
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='gmail_address'")
        row_addr = c.fetchone()
        c.execute("SELECT value FROM settings WHERE key='gmail_app_password'")
        row_pass = c.fetchone()
        conn.close()
        if row_addr and row_addr[0].strip():
            sender = row_addr[0].strip()
        if row_pass and row_pass[0].strip():
            password = row_pass[0].strip()
    except Exception:
        pass
    
    if not sender:
        sender = os.getenv("GMAIL_ADDRESS", "")
    if not password:
        password = os.getenv("GMAIL_APP_PASSWORD", "")
        
    return sender, password

def send_legal_notice(recipient_email: str, case_id: str, issue_type: str, attachment_path: str) -> bool:
    
    sender, password = get_gmail_credentials()


    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient_email
    msg['Subject'] = f"Legal Notice — {issue_type} | Case ID: {case_id}"

    body = f"""Dear Sir/Madam,

Please find attached a formal legal notice regarding Case ID: {case_id}.

This notice has been sent via LegalEase, an AI-powered legal notice system.
Kindly respond within 15 days of receiving this notice.

Regards,
LegalEase System
"""
    msg.attach(MIMEText(body, 'plain'))

    # Attach Word document
    with open(attachment_path, "rb") as f:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename=LegalNotice_{case_id}.docx')
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False