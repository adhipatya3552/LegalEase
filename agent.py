import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_groq_api_key() -> str:
    try:
        conn = sqlite3.connect("legalease.db")
        c = conn.cursor()
        c.execute("SELECT value FROM settings WHERE key='groq_api_key'")
        row = c.fetchone()
        conn.close()
        if row and row[0].strip():
            return row[0].strip()
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")

def classify_and_draft_notice(
    user_problem: str, 
    sender_name: str, 
    sender_address: str = "Not Provided", 
    recipient_name: str = "Not Provided", 
    recipient_address: str = "Not Provided",
    extra_details: str = ""
) -> dict:
    current_date_str = datetime.now().strftime("%d %B %Y")
    
    api_key = get_groq_api_key()
    client = Groq(api_key=api_key)

    
    prompt = f"""
You are a senior Indian legal expert with 20 years of experience drafting legal notices for the Supreme Court and High Courts of India.
A client has approached you with a legal dispute and wants to send a formal legal notice.

Details provided:
- Date of Notice: {current_date_str}
- Sender Name (Client): {sender_name}
- Sender Address: {sender_address}
- Recipient Name (Opposite Party): {recipient_name}
- Recipient Address: {recipient_address}
- Additional Details/Claim Info: {extra_details}
- Client's Problem Description: 
{user_problem}

Your tasks:
1. Identify the ISSUE TYPE from this list only:
   - Consumer Dispute
   - Contract Breach
   - Non-Payment of Dues
   - Property Dispute
   - Deficiency of Service
   - Harassment
   - Other

2. Draft a formal, legally binding legal notice under the relevant laws of India.
   The notice MUST be drafted in a professional, firm, and formal legal tone.
   You must cite specific Indian Acts and Sections with extreme accuracy. Citing incorrect section numbers will invalidate the document. Match your citations to the specific dispute context as follows:
   - Product Defects (Physical Goods like faulty screens, bad appliances, TV failures): Cite Section 2(10) of the Consumer Protection Act, 2019 (defines "defect" in goods).
   - Deficiency of Service (Refusal to honor warranty, poor repairs, customer service failures, delays): Cite Section 2(11) of the Consumer Protection Act, 2019 (defines "deficiency" in services).
   - Right to Safety (Protection against marketing of hazardous goods/services): Cite Section 2(9)(i) of the Consumer Protection Act, 2019 (defines "consumer rights" including safety).
   - Non-Payment of Dues / General Contract Breach: Cite Section 73 of the Indian Contract Act, 1872.
   - Cheque Bouncing: Cite Section 138 of the Negotiable Instruments Act, 1881.
   - Property / Tenancy Disputes (Withholding of security deposits, lease termination): Cite Section 106 of the Transfer of Property Act, 1882.
   - Harassment / Defamation: Appropriate sections under the Indian Penal Code (IPC) / Bharatiya Nyaya Sanhita (BNS).

   CRITICAL LEGAL RULE: Under the Consumer Protection Act, 2019, Section 12 relates only to administrative vacancies and must NEVER be cited as a consumer right or safety provision. Always use Section 2(9)(i) for consumer rights, Section 2(10) for product defects, and Section 2(11) for service deficiencies.


   The structure of the notice must be:
   - Heading: "LEGAL NOTICE" (Centered)
   - Date and Place
   - "To," block followed by Recipient Name and Address
   - "Under Instructions from my Client..." block (representing the Sender)
   - Detailed facts of the case (summarizing the problem clearly and professionally)
   - Legal grounds and liabilities of the recipient
   - The Demand / Relief sought (specifically what they must do, e.g., pay an amount, replace a product, stop harassment)
   - A strict 15-day rectification/compliance period
   - Warning of legal action (civil/criminal) at the recipient's risk and cost if they fail to comply
   - Closing: "Yours faithfully, / For [Sender Name]"

Reply in EXACTLY this format, nothing else:
ISSUE_TYPE: [write issue type here]
LEGAL_NOTICE:
[write full legal notice here]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
        temperature=0.25
    )

    raw = response.choices[0].message.content
    
    # Robust parsing using regular expressions
    import re
    raw_clean = raw.replace("\r", "")
    
    issue_type = "Other"
    notice_text = ""
    
    # Search for ISSUE_TYPE: [text] (case-insensitive, optional asterisks/headers)
    match_issue = re.search(r'(?:^|\n)\s*(?:\*\*|###|#)*\s*ISSUE[-_ ]TYPE\s*(?:\*\*|:)*\s*([^\n]+)', raw_clean, re.IGNORECASE)
    if match_issue:
        raw_issue = match_issue.group(1).replace("**", "").replace("*", "").strip()
        valid_types = [
            "Consumer Dispute", "Contract Breach", "Non-Payment of Dues", 
            "Property Dispute", "Deficiency of Service", "Harassment", "Other"
        ]
        # Find match from our category list
        for vt in valid_types:
            if vt.lower() in raw_issue.lower():
                issue_type = vt
                break
                
    # Search for LEGAL_NOTICE: heading and extract all text following it
    match_notice = re.search(r'(?:^|\n)\s*(?:\*\*|###|#)*\s*LEGAL[-_ ]NOTICE\s*(?:\*\*|:)*\s*(?:\n|$)', raw_clean, re.IGNORECASE)
    if match_notice:
        notice_text = raw_clean[match_notice.end():].strip()
    else:
        # Fallback: if no keyword matched, treat everything after the first line as notice
        lines = raw_clean.split("\n")
        start_line = 1 if len(lines) > 0 and "issue" in lines[0].lower() else 0
        if start_line == 1 and len(lines) > 2 and not lines[1].strip():
            start_line = 2
        notice_text = "\n".join(lines[start_line:]).strip()

    # Strip codeblock wrappers (e.g. ```text ... ```) if the model returned them
    if notice_text.startswith("```"):
        notice_text = re.sub(r'^```[a-zA-Z]*\n', '', notice_text)
        notice_text = re.sub(r'\n```$', '', notice_text)

    return {
        "issue_type": issue_type,
        "notice_text": notice_text.strip()
    }
