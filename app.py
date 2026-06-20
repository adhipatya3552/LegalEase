import streamlit as st
import sqlite3
import uuid
import pandas as pd
import os
from datetime import datetime
from dotenv import load_dotenv
from agent import classify_and_draft_notice
from document_generator import create_legal_notice_doc
from email_sender import send_legal_notice
from uipath_connector import create_case_in_maestro, get_uipath_credentials

load_dotenv()

# ── Database setup ──────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    # Create main cases table with all metadata
    c.execute('''CREATE TABLE IF NOT EXISTS cases (
        case_id           TEXT PRIMARY KEY,
        sender_name       TEXT,
        sender_address    TEXT,
        problem           TEXT,
        issue_type        TEXT,
        notice_draft      TEXT,
        status            TEXT,
        created_at        TEXT,
        recipient_name    TEXT,
        recipient_address TEXT,
        extra_details     TEXT,
        recipient_email   TEXT
    )''')
    
    # Run dynamic SQLite migrations to add missing columns in older databases
    c.execute("PRAGMA table_info(cases)")
    columns = [col[1] for col in c.fetchall()]
    new_cols = {
        "sender_address": "TEXT",
        "recipient_name": "TEXT",
        "recipient_address": "TEXT",
        "extra_details": "TEXT"
    }
    for col_name, col_type in new_cols.items():
        if col_name not in columns:
            try:
                c.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Migration error for {col_name}: {e}")

    # Create settings table for persistence
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key   TEXT PRIMARY KEY,
        value TEXT
    )''')
    conn.commit()
    conn.close()

def save_case(case_id, sender_name, sender_address, problem, issue_type, notice_draft, recipient_name, recipient_address, extra_details, recipient_email, status):
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO cases (
        case_id, sender_name, sender_address, problem, issue_type, notice_draft, 
        status, created_at, recipient_name, recipient_address, extra_details, recipient_email
    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
              (case_id, sender_name, sender_address, problem, issue_type, notice_draft,
               status, datetime.now().strftime("%d-%m-%Y %H:%M"), recipient_name, recipient_address, extra_details, recipient_email))
    conn.commit()
    conn.close()

def update_status(case_id, new_status):
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    c.execute("UPDATE cases SET status=? WHERE case_id=?", (new_status, case_id))
    conn.commit()
    conn.close()

def get_all_cases():
    conn = sqlite3.connect("legalease.db")
    df = pd.read_sql("SELECT case_id, sender_name, issue_type, status, created_at FROM cases ORDER BY created_at DESC", conn)
    conn.close()
    return df

def get_case_by_id(case_id):
    conn = sqlite3.connect("legalease.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE case_id=?", (case_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "case_id": row[0],
        "sender_name": row[1],
        "sender_address": row[2] if len(row) > 2 else "",
        "problem": row[3] if len(row) > 3 else "",
        "issue_type": row[4] if len(row) > 4 else "",
        "notice_draft": row[5] if len(row) > 5 else "",
        "status": row[6] if len(row) > 6 else "",
        "created_at": row[7] if len(row) > 7 else "",
        "recipient_name": row[8] if len(row) > 8 else "",
        "recipient_address": row[9] if len(row) > 9 else "",
        "extra_details": row[10] if len(row) > 10 else "",
        "recipient_email": row[11] if len(row) > 11 else ""
    }

# ── Streamlit Initialization & Styling ────────────────────────
init_db()
st.set_page_config(page_title="LegalEase — AI Notice & UiPath Case System", page_icon="⚖️", layout="wide")

# Inject Custom HSL theme CSS for visual excellence
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Typography */
    html, body, [class*="css"], .stApp {
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* App background */
    .stApp {
        background: radial-gradient(circle at 10% 20%, #0c0f16 0%, #151a24 100%);
        color: #e2e8f0;
    }
    
    /* Title text gradient */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B6B 0%, #C82333 50%, #8B0000 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }
    
    /* Premium Styled Card Container & Native Bordered Containers */
    .card, div[data-testid="stVerticalBlockBorder"] {
        background: rgba(22, 27, 38, 0.65) !important;
        border: 1px solid rgba(255, 255, 255, 0.07) !important;
        border-radius: 14px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
        backdrop-filter: blur(12px) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    
    .card:hover, div[data-testid="stVerticalBlockBorder"]:hover {
        border-color: rgba(139, 0, 0, 0.5) !important;
        box-shadow: 0 12px 35px rgba(139, 0, 0, 0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Colored Status Badges */
    .status-badge {
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.82rem;
        display: inline-block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .status-new {
        background-color: rgba(52, 152, 219, 0.15);
        color: #3498db;
        border: 1px solid rgba(52, 152, 219, 0.4);
    }
    
    .status-review {
        background-color: rgba(241, 196, 15, 0.15);
        color: #f1c40f;
        border: 1px solid rgba(241, 196, 15, 0.4);
    }
    
    .status-sent {
        background-color: rgba(46, 204, 113, 0.15);
        color: #2ecc71;
        border: 1px solid rgba(46, 204, 113, 0.4);
    }
    
    .status-closed {
        background-color: rgba(149, 165, 166, 0.15);
        color: #bdc3c7;
        border: 1px solid rgba(149, 165, 166, 0.4);
    }
    
    .status-escalated {
        background-color: rgba(231, 76, 60, 0.15);
        color: #e74c3c;
        border: 1px solid rgba(231, 76, 60, 0.4);
    }
    
    /* Premium visual text style */
    .legal-label {
        font-weight: 600;
        color: #C82333;
        margin-right: 8px;
    }
    
    /* Custom buttons style override */
    .stButton>button {
        background: linear-gradient(135deg, #8B0000 0%, #C82333 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 15px rgba(139, 0, 0, 0.25) !important;
        transition: all 0.25s ease !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #C82333 0%, #E03E3E 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(139, 0, 0, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/scales.png", width=80)
st.sidebar.title("⚖️ LegalEase Control")
st.sidebar.markdown("*Empowering individuals and SMBs with automated, affordable legal protections under Indian Law.*")
st.sidebar.divider()
page = st.sidebar.radio("Navigate Navigation", ["📝 File New Case", "📊 Case Tracker & Manager"])
st.sidebar.divider()
st.sidebar.info("💡 **Bonus Track Info:** Uses Groq LLaMA-3.3-70B model & integrates with UiPath Maestro Case API.")

# ══════════════════════════════════════════════════════════════
# PAGE 1 — File New Case
# ══════════════════════════════════════════════════════════════
if page == "📝 File New Case":
    st.markdown('<div class="main-header">⚖️ File a New Case</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Describe your legal grievance in simple words. Our AI legal agent will draft a ready-to-send notice.</div>', unsafe_allow_html=True)
    st.divider()

    # Form structure wrapped in native containers
    col_left, col_right = st.columns(2)
    
    with col_left:
        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0;'>👤 Client / Sender Details</h3>", unsafe_allow_html=True)
            sender_name = st.text_input("Full Name (Sender)", placeholder="e.g. Adhipatya Saxena")
            sender_email = st.text_input("Email Address", placeholder="e.g. adhipatya.saxena@gmail.com")
            sender_address = st.text_area("Mailing Address", placeholder="e.g. E-7/801, Ashoka Apartment, Arera Colony, Bhopal, MP - 462016", height=95)
        
    with col_right:
        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0;'>🎯 Opposing Party / Recipient</h3>", unsafe_allow_html=True)
            recipient_name = st.text_input("Name / Company Name", placeholder="e.g. XYZ E-Commerce Retail Pvt. Ltd.")
            recipient_email = st.text_input("Opponent's Email Address", placeholder="e.g. grievance@xyzecommerce.in")
            recipient_address = st.text_area("Mailing Address", placeholder="e.g. Block C, Sector 62, Noida, Uttar Pradesh - 201301", height=95)

    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0;'>📝 Dispute Details & Claims</h3>", unsafe_allow_html=True)
        problem = st.text_area(
            "Describe the dispute/problem in plain English or Hindi:",
            placeholder="Example: I purchased a laptop on 10 April 2026. It stopped booting on 25 May 2026. I reached out to service center but they refused to honor the 1-year product warranty, stating cosmetic wear and tear, and are demanding ₹15,000 for repair.",
            height=140
        )
        extra_details = st.text_input("Additional specific facts (e.g. Claim amount, Contract Date, Cheque details, Invoice number)", placeholder="e.g. Invoice No. INV-90812; Product value ₹54,990; Cheque bounce date 12-05-2026")

    if st.button("🚀 Draft Legal Notice & Sync Case", use_container_width=True):
        if not all([sender_name, sender_email, recipient_name, recipient_email, problem]):
            st.error("⚠️ All core fields (Sender Name/Email, Opponent Name/Email, and Dispute Description) are mandatory!")
        else:
            with st.spinner("AI Legal Expert is analyzing dispute facts and drafting notice according to Indian legal acts..."):
                # Unique Case ID
                case_id = f"LE-{str(uuid.uuid4())[:8].upper()}"
                
                # AI Agent drafts
                result = classify_and_draft_notice(
                    user_problem=problem,
                    sender_name=sender_name,
                    sender_address=sender_address if sender_address else "Bhopal, MP",
                    recipient_name=recipient_name,
                    recipient_address=recipient_address if recipient_address else "India",
                    extra_details=extra_details
                )
                
                issue_type = result["issue_type"]
                notice_text = result["notice_text"]
                
                # Sync into UiPath Maestro connector
                uipath_response = create_case_in_maestro(case_id, issue_type, problem)
                
                # Generate Styled docx
                doc_path = create_legal_notice_doc(notice_text, case_id, issue_type)
                
                # Save into local SQLite DB
                save_case(
                    case_id=case_id,
                    sender_name=sender_name,
                    sender_address=sender_address,
                    problem=problem,
                    issue_type=issue_type,
                    notice_draft=notice_text,
                    recipient_name=recipient_name,
                    recipient_address=recipient_address,
                    extra_details=extra_details,
                    recipient_email=recipient_email,
                    status="AI Processing Done"
                )
                
                # Cache parameters in session state for instant review
                st.session_state.current_case_id = case_id
                st.session_state.notice_draft = notice_text
                st.session_state.issue_type = issue_type
                st.session_state.doc_path = doc_path
                st.session_state.recipient_email = recipient_email
                st.session_state.uipath_msg = uipath_response.get("message", "Logged")
                st.session_state.uipath_status = uipath_response.get("status", "Created")
                
                st.success(f"🎉 Case Registered! Case ID: {case_id}")
                st.rerun()

    # If case has been created, display Review and Disptach Editor
    if "current_case_id" in st.session_state:
        st.divider()
        st.markdown(f'<div class="main-header" style="font-size:2rem;">📄 Review Notice: {st.session_state.current_case_id}</div>', unsafe_allow_html=True)
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Dispute Category Detected", st.session_state.issue_type)
        col_m2.metric("UiPath Sync Action", st.session_state.uipath_msg)
        
        # Interactive Text Editor
        notice_edited = st.text_area("Edit Drafted Notice (Make modifications directly below):", value=st.session_state.notice_draft, height=420)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Save Edits & Rebuild Notice File", use_container_width=True):
                # Update SQLite
                conn = sqlite3.connect("legalease.db")
                c = conn.cursor()
                c.execute("UPDATE cases SET notice_draft=? WHERE case_id=?", (notice_edited, st.session_state.current_case_id))
                conn.commit()
                conn.close()
                
                # Regenerate Document
                doc_path = create_legal_notice_doc(notice_edited, st.session_state.current_case_id, st.session_state.issue_type)
                
                st.session_state.notice_draft = notice_edited
                st.session_state.doc_path = doc_path
                st.success("💾 Notice updated successfully! Word Document rebuilt.")
                
        with col_btn2:
            with st.expander("👁️ Quick Layout Preview"):
                st.markdown(notice_edited.replace("\n", "\n\n"))
                
        st.divider()
        st.markdown("<h3>📬 Dispatch Notice Options</h3>", unsafe_allow_html=True)
        col_act1, col_act2 = st.columns(2)
        
        with col_act1:
            if st.button("📤 Send Notice via Email", use_container_width=True):
                with st.spinner("Dispatching notice with attached Word document to opponent..."):
                    sent = send_legal_notice(
                        st.session_state.recipient_email,
                        st.session_state.current_case_id,
                        st.session_state.issue_type,
                        st.session_state.doc_path
                    )
                if sent:
                    update_status(st.session_state.current_case_id, "Notice Sent")
                    st.success(f"✅ Legal notice successfully emailed to {st.session_state.recipient_email}!")
                else:
                    st.error("❌ Email failed. Please check SMTP app credentials in 'System Settings'.")
                    
        with col_act2:
            with open(st.session_state.doc_path, "rb") as f:
                st.download_button(
                    label="📥 Download Notice as Styled Word File",
                    data=f,
                    file_name=f"LegalNotice_{st.session_state.current_case_id}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

# ══════════════════════════════════════════════════════════════
# PAGE 2 — Case Tracker & Manager
# ══════════════════════════════════════════════════════════════
elif page == "📊 Case Tracker & Manager":
    st.markdown('<div class="main-header">📊 Litigation Control Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Manage workflow statuses, print notices, and dispatch communications for active cases.</div>', unsafe_allow_html=True)
    st.divider()

    df = get_all_cases()
    
    if df.empty:
        st.info("No cases registered yet. Go to 'File New Case' to log your first dispute.")
    else:
        # Metrics Cards
        total_cases = len(df)
        sent_cases = len(df[df['status'] == 'Notice Sent'])
        processing_cases = len(df[df['status'] == 'AI Processing Done'])
        closed_cases = len(df[df['status'].isin(['Closed', 'Closed / Resolved'])])
        escalated_cases = len(df[df['status'] == 'Escalated'])

        col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)
        col_kpi1.metric("Total Cases Registered", total_cases)
        col_kpi2.metric("Notices Sent", sent_cases)
        col_kpi3.metric("Under Review", processing_cases)
        col_kpi4.metric("Cases Resolved", closed_cases)
        col_kpi5.metric("Escalated", escalated_cases)

        st.divider()

        # Selector Dropdown to manage specific cases
        st.markdown("<h3>📂 Legal Brief Viewer & Case Operations</h3>", unsafe_allow_html=True)
        case_id_list = df['case_id'].tolist()
        selected_case_id = st.selectbox("Select Case ID to inspect and modify:", case_id_list)
        
        if selected_case_id:
            case = get_case_by_id(selected_case_id)
            if case:
                # Custom HSL styled card layout
                with st.container(border=True):
                    st.markdown(f"<h3 style='margin-top:0;'>Case File: {case['case_id']}</h3>", unsafe_allow_html=True)
                    
                    # Badge matching status class
                    st_class = "status-new"
                    status_lower = case['status'].lower()
                    if "sent" in status_lower:
                        st_class = "status-sent"
                    elif "done" in status_lower or "review" in status_lower:
                        st_class = "status-review"
                    elif "closed" in status_lower or "resolved" in status_lower:
                        st_class = "status-closed"
                    elif "escalated" in status_lower:
                        st_class = "status-escalated"
                        
                    st.markdown(f"**Current Status:** <span class='status-badge {st_class}'>{case['status']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Dispute Type:** {case['issue_type']} | **Logged At:** {case['created_at']}")
                    
                    # Grid details
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                    col_det1, col_det2 = st.columns(2)
                    
                    with col_det1:
                        st.markdown(f"**Client / Sender:** {case['sender_name']}")
                        st.write(f"Address: {case['sender_address']}")
                    with col_det2:
                        st.markdown(f"**Opposing Party:** {case['recipient_name']}")
                        st.write(f"Address: {case['recipient_address']}")
                        st.write(f"Email: {case['recipient_email']}")
                    
                    st.markdown("<hr style='border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
                    st.markdown(f"**Problem Context:** {case['problem']}")
                    if case['extra_details']:
                        st.markdown(f"**Claim Particulars:** {case['extra_details']}")

                # Expandable notice editor
                with st.expander("📝 Edit notice content text"):
                    txt_area_id = f"text_{case['case_id']}"
                    edited_notice_txt = st.text_area("Notice Draft Text:", value=case['notice_draft'], height=320, key=txt_area_id)
                    
                    if st.button("Update Notice Text", key=f"up_btn_{case['case_id']}"):
                        conn = sqlite3.connect("legalease.db")
                        c = conn.cursor()
                        c.execute("UPDATE cases SET notice_draft=? WHERE case_id=?", (edited_notice_txt, case['case_id']))
                        conn.commit()
                        conn.close()
                        
                        # Rebuild Word doc
                        create_legal_notice_doc(edited_notice_txt, case['case_id'], case['issue_type'])
                        st.success("Draft updated and document rebuilt successfully!")
                        st.rerun()

                # Action Operations
                st.markdown("#### ⚙️ Case Operations")
                col_act1, col_act2, col_act3 = st.columns(3)
                
                with col_act1:
                    if st.button("📧 Send/Resend Email Notice", key=f"re_email_{case['case_id']}", use_container_width=True):
                        doc_path = f"notice_{case['case_id']}.docx"
                        if not os.path.exists(doc_path):
                            create_legal_notice_doc(case['notice_draft'], case['case_id'], case['issue_type'])
                        
                        with st.spinner("Resending notice..."):
                            sent = send_legal_notice(case['recipient_email'], case['case_id'], case['issue_type'], doc_path)
                        if sent:
                            update_status(case['case_id'], "Notice Sent")
                            st.success("Notice emailed successfully!")
                            st.rerun()
                        else:
                            st.error("SMTP delivery failed. Verify credentials in Settings.")
                            
                with col_act2:
                    doc_path = f"notice_{case['case_id']}.docx"
                    if not os.path.exists(doc_path):
                        create_legal_notice_doc(case['notice_draft'], case['case_id'], case['issue_type'])
                        
                    with open(doc_path, "rb") as f:
                        st.download_button(
                            label="📥 Download Word Notice Document",
                            data=f,
                            file_name=f"LegalNotice_{case['case_id']}.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            key=f"dl_dashboard_{case['case_id']}",
                            use_container_width=True
                        )
                        
                with col_act3:
                    workflow_stages = ["AI Processing Done", "Notice Sent", "Closed / Resolved", "Escalated"]
                    try:
                        current_stage_idx = workflow_stages.index(case['status'])
                    except ValueError:
                        current_stage_idx = 0
                        
                    selected_stage = st.selectbox(
                        "Transition Case Status:",
                        workflow_stages,
                        index=current_stage_idx,
                        key=f"stage_sel_{case['case_id']}"
                    )
                    
                    if selected_stage != case['status']:
                        update_status(case['case_id'], selected_stage)
                        st.success(f"Case status changed to '{selected_stage}'")
                        st.rerun()

        st.divider()
        st.markdown("### 📋 Complete Registry Log")
        st.dataframe(df, use_container_width=True)
