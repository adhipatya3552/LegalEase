# LegalEase — AI-Powered Legal Notice System & UiPath Orchestration

> **A co-founder quality legal tech portal enabling everyday citizens and SMBs in India to draft, review, edit, and dispatch legally binding notices for free.**
> 
> *Submitting to the UiPath AgentHack Hackathon (Track 1 — Maestro Case).*

---

## ⚖️ The Vision & Mission

In India, millions of people encounter everyday legal issues—such as warranty denials, security deposit withholdings, unpaid dues, and contract breaches—but cannot afford high lawyer consultation fees. They often end up forfeiting their rights. 

**LegalEase** democratizes legal protection by enabling users to describe their grievances in plain words. It uses LLMs to classify the issue and draft a formal legal notice quoting specific Indian Acts (like the *Consumer Protection Act 2019*, *Indian Contract Act 1872*, or *Negotiable Instruments Act 1881*). 

The notice lifecycle is synchronized with **UiPath Maestro Case** to manage and track the dispute from intake to resolution (Human-in-the-Loop review, dispatch, response, and closure).

---

## 🛠️ The Tech Stack

LegalEase is built entirely using high-quality, free-tier developer tools:

*   **Frontend UI:** Streamlit (injected with custom glassmorphic HSL styling, Outfit typography, and custom status indicators).
*   **AI Engine (Brain):** Groq API (running LLaMA-3.3-70B-versatile for legal citation and drafting accuracy).
*   **Database Store:** SQLite3 (stores case histories, edits, and system configuration keys locally).
*   **Document Generator:** python-docx (compiles notice texts into a clean, justified document matching standard law firm templates with 1-inch margins).
*   **SMTP Dispatcher:** Python smtplib with secure SSL (dispatches notices with the attached Word document via Gmail SMTP).
*   **Orchestration:** UiPath Orchestrator API (synchronizes cases under Track 1: Maestro Case workflows).

---

## ⚙️ Key Features

1.  **AI Legal Notice Drafting:** Analyzes disputes, maps them to the correct category, and generates formal notice documents.
2.  **Interactive Notice Editor:** Refine, customize, and edit notice drafts directly in the browser, with an expandable live markdown preview.
4.  **Word Document Engine:** Saves notice files with standard legal formatting (Times New Roman, 1.25 line spacing, justified text, proper legal sub-headers).
5.  **Litigation Control Panel:** View metrics, trace case histories, transition case statuses (Intake ➔ Review ➔ Dispatched ➔ Resolved ➔ Escalated), and download/email notices.
6.  **UiPath Integration Sandbox:** Automatically connects and syncs cases with UiPath Cloud, including a simulation sandbox mode.

---

## 📁 Repository Structure

```text
legalease/
│
├── app.py                  # Main Streamlit Dashboard & Litigation Portal
├── agent.py                # Groq API Agent (LLaMA-3.3 prompt & classification logic)
├── document_generator.py   # Compiles notice drafts into styled Word files (.docx)
├── email_sender.py         # SMTP SSL Gmail dispatch library
├── uipath_connector.py     # UiPath Cloud API wrapper & Sandbox connector
├── test_modules.py         # Programmatic validation test suite
├── requirements.txt        # PIP dependencies
├── .env.example            # Environment variables template
└── legalease.db            # SQLite database (auto-generated on launch)
```

---

## 🚀 Quick Setup & Run

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Install Dependencies
Clone the repository, activate your virtual environment, and run:
```bash
pip install -r requirements.txt
```

### 3. Create Environment Variables
Copy `.env.example` to `.env` and fill in your keys:
```env
GROQ_API_KEY=gsk_your_groq_key_here
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

# Optional: UiPath Integration Configuration
UIPATH_ORG=your_org_name
UIPATH_TENANT=your_tenant_name
UIPATH_ACCESS_TOKEN=your_access_token
```

#### 🔑 How to Obtain the Integration Keys:

##### A. Groq API Key
1. Go to the [Groq Developer Console](https://console.groq.com/).
2. Log in or create a free account.
3. Click on **API Keys** in the left sidebar.
4. Click **Create API Key**, name it `LegalEase`, and copy the generated key (`gsk_...`).

##### B. Gmail App Password (for automated email dispatch)
1. Go to your [Google Account Settings](https://myaccount.google.com/).
2. Select **Security** from the left-hand menu.
3. Under "How you sign in to Google", ensure **2-Step Verification** is turned ON.
4. Click on **2-Step Verification**, scroll to the very bottom, and select **App passwords**.
5. Give the app a name (e.g., `LegalEase Notice App`) and click **Create**.
6. Copy the displayed 16-character code (e.g., `abcd efgh ijkl mnop`). Paste it as `GMAIL_APP_PASSWORD` in your `.env` (remove any spaces).

##### C. UiPath Integration Credentials
1. **Find `UIPATH_ORG`**: Log in to [UiPath Automation Cloud](https://cloud.uipath.com). Look at your browser URL: `https://cloud.uipath.com/YOUR_ORGANIZATION_NAME/...`. Your organization name is your `UIPATH_ORG` (e.g., `legaleaseorg`).
2. **Find `UIPATH_TENANT`**: Go to **Admin** > **Tenants** in the sidebar. Copy your tenant name (usually `DefaultTenant`).
3. **Generate `UIPATH_ACCESS_TOKEN`**:
   * Navigate to **Admin** > **External Applications** (left sidebar).
   * Click **Add Application** and choose **Confidential Application** as the application type.
   * Click **Add Scopes**, select the **Orchestrator** resource, click the **Application Scope(s)** tab, and tick **Select all** (or check `OR.Execution`, `OR.Folders`, `OR.Jobs`, and `OR.Queues`).
   * Click **Save** to create the application and immediately copy the **App ID (Client ID)** and **App Secret**.
   * Run the helper script in your terminal to fetch the access token automatically:
     ```bash
     python get_token.py
     ```
   * Choose option `2`, paste your App ID and App Secret when prompted, and the script will automatically write the token into your `.env` file.

---

### 4. Run the Local Test Suite
To verify the database, AI engine, and document generation, execute:
```bash
python test_modules.py
```

### 5. Launch the Dashboard
Start the Streamlit application:
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to experience the portal.

---

## ⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.
