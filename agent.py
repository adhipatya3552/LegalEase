import os
import sqlite3
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
from legal_reference import get_legal_reference_block, is_known_category

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

    legal_reference = get_legal_reference_block()

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

   You must cite specific Indian Acts and Sections with extreme accuracy. Below is a
   VERIFIED REFERENCE TABLE. You are ONLY permitted to cite a section number if it
   appears in this table for the matching issue type. Do not cite any section number
   that is not listed below, even if you believe it might be correct — if unsure,
   describe the legal wrong in plain factual language instead of guessing a citation.

   --- VERIFIED LEGAL REFERENCE TABLE (FOLLOW STRICTLY) ---
{legal_reference}
   --- END OF REFERENCE TABLE ---

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

    notice_text = notice_text.strip()

    # Safety-net validation: catch known hallucination patterns even if the
    # prompt rules were not followed perfectly. This does NOT block sending —
    # it flags warnings so the Human Review stage knows to look closer.
    warnings = validate_legal_notice(notice_text, issue_type)

    return {
        "issue_type": issue_type,
        "notice_text": notice_text,
        "warnings": warnings
    }


def validate_legal_notice(notice_text: str, issue_type: str = "") -> list:
    """
    Lightweight safety-net check for known hallucination patterns.
    This is NOT a substitute for human/lawyer review — it only catches a
    small set of specific, known mistakes so they can be flagged before
    a notice is sent. Returns a list of warning strings (empty if none found).
    """
    warnings = []
    text_lower = notice_text.lower()

    # Out-of-database check: if the AI's classified issue type does not match
    # any category in our verified legal_reference.py table, its citations
    # were NOT restricted to a verified source — flag this clearly so the
    # human reviewer knows to double check every section number by hand.
    if not is_known_category(issue_type):
        warnings.append(
            f"This case was classified as '{issue_type}', which is OUTSIDE our verified "
            "legal reference database (legal_reference.py covers Consumer Disputes, "
            "Contract Breach, Cheque Bounce, Property/Tenancy, and Harassment/Defamation "
            "only). Any law or section number cited in this draft was NOT checked against "
            "a verified source. Please manually verify every citation before sending, or "
            "consult a lawyer for this specific case type."
        )

    # Known incorrect citation: Section 12 is an administrative provision,
    # not a consumer-rights provision. Flag if it appears near "consumer".
    if "section 12" in text_lower and "consumer" in text_lower:
        warnings.append(
            "Possible incorrect citation: 'Section 12' was mentioned. Section 12 of "
            "the Consumer Protection Act, 2019 is an administrative provision, not a "
            "consumer rights provision. Verify this citation before sending."
        )

    # Criminal action threatened in what is likely a civil/consumer matter
    if "criminal action" in text_lower or "criminal proceedings" in text_lower:
        if "138" not in notice_text:  # Section 138 (cheque bounce) genuinely has criminal consequences
            warnings.append(
                "This notice threatens 'criminal action'. Most consumer/contract disputes "
                "are civil matters only. Verify this is appropriate before sending, or "
                "change it to reference civil remedies (Consumer Forum / District Court)."
            )

    if not warnings:
        return []
    return warnings
