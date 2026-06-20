import os
from agent import classify_and_draft_notice
from document_generator import create_legal_notice_doc
from uipath_connector import create_case_in_maestro
from app import init_db, save_case, get_case_by_id

def run_tests():
    print("Initializing test database...")
    init_db()
    
    print("\nDrafting test notice using Groq API...")
    problem = "Bought a new smart TV for Rs. 45,000 from Alpha Electronics on 12th Jan 2026. Within 3 weeks, vertical green lines appeared on screen. Store manager refused warranty replacement claiming user physical damage, which is false as the TV was professionally wall-mounted."
    
    # Run agent
    result = classify_and_draft_notice(
        user_problem=problem,
        sender_name="Vikram Kumar",
        sender_address="12, Residency Road, Bangalore, Karnataka - 560025",
        recipient_name="Alpha Electronics Store Manager",
        recipient_address="Plot 5, Tech Park Outer Ring Road, Bangalore - 560037",
        extra_details="Invoice No: OR-9812A; Price: Rs. 45,000"
    )
    
    print(f"Detected Category: {result['issue_type']}")
    print("-" * 50)
    print(result['notice_text'][:300] + "\n...")
    print("-" * 50)
    
    print("\nGenerating styled legal document (.docx)...")
    case_id = "LE-TEST"
    doc_path = create_legal_notice_doc(result['notice_text'], case_id, result['issue_type'])
    print(f"Document created at: {doc_path}")
    
    print("\nSyncing case with UiPath Maestro sandbox...")
    sync_res = create_case_in_maestro(case_id, result['issue_type'], problem)
    print(f"Sync message: {sync_res['message']}")
    
    print("\nSaving case in local database...")
    save_case(
        case_id=case_id,
        sender_name="Vikram Kumar",
        sender_address="12, Residency Road, Bangalore",
        problem=problem,
        issue_type=result['issue_type'],
        notice_draft=result['notice_text'],
        recipient_name="Alpha Electronics Store Manager",
        recipient_address="Plot 5, Tech Park Outer Ring Road",
        extra_details="Invoice No: OR-9812A",
        recipient_email="test-opponent@yopmail.com",
        status="AI Processing Done"
    )
    
    print("\nVerifying case retrieval...")
    retrieved = get_case_by_id(case_id)
    if retrieved and retrieved["sender_name"] == "Vikram Kumar":
        print("[SUCCESS] Retrieved case details match.")
    else:
        print("[ERROR] Case mismatch or not found.")

if __name__ == "__main__":
    run_tests()
