# LegalEase — AI-Powered Legal Notice System & UiPath Orchestration

<div align="center">

![LegalEase Badge](https://img.shields.io/badge/LegalEase-AI%20Notice%20Portal-red?style=for-the-badge&logo=gavel&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58.0-red?style=for-the-badge&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3-orange?style=for-the-badge)
![UiPath](https://img.shields.io/badge/UiPath-Maestro%20Sync-blue?style=for-the-badge&logo=uipath)
![SQLite](https://img.shields.io/badge/SQLite-Local%20DB-blue?style=for-the-badge&logo=sqlite)

**A co-founder quality legal tech portal enabling everyday citizens and SMBs in India to draft, review, edit, and dispatch legally binding notices for free — synchronized with UiPath Maestro.**

🚀 **[Live App Link on Streamlit Cloud](https://legalease-adhipatya.streamlit.app/)**

</div>

---

## 📋 Table of Contents

- [Project Description (Overview)](#-project-description-overview)
- [UiPath Agent Architecture & Details](#-uipath-agent-architecture--details)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup Instructions (Getting Started)](#-setup-instructions-getting-started)
- [Environment Variables](#-environment-variables)
- [How to Obtain Keys](#-how-to-obtain-keys)
- [How It Works](#-how-it-works)
- [Verification & Testing](#-verification--testing)
- [Deployment](#-deployment)
- [Roadmap](#-roadmap)

---

## ⚖️ Project Description (Overview)

**LegalEase** democratizes access to justice in India by enabling users to describe their grievances in plain, everyday language. The platform automatically classifies the issue and drafts a formal, legally binding notice citing exact sections of Indian Acts (such as the *Consumer Protection Act 2019*, *Indian Contract Act 1872*, *Negotiable Instruments Act 1881*, and *Transfer of Property Act 1882*). 

The notice lifecycle is synchronized with **UiPath Maestro Case Management (Track 1)** to coordinate backend automation, case tracking, human-in-the-loop validation, and resolution.

---

## 🤖 UiPath Agent Architecture & Details

### 🧩 UiPath Components Used
* **UiPath Maestro (Case Management - Track 1):** Coordinates case tracking, status transitions, human-in-the-loop audits, and resolution validation.
* **UiPath Orchestrator API (Maestro Sync):** Integrates via REST APIs to dynamically publish new cases and metadata into the Orchestrator.
* **UiPath Confidential Application (OAuth2):** Handles secure server-to-server authentication with tenant scope access credentials.
* **Maestro Case API Workflows:** Automates backend queue entries and case folder logging.

### 🏷️ Agent Type
* **Coded Agents:** This solution utilizes a **Coded Agent** pattern built entirely in Python. The AI legal agent connects to the Groq API (LLaMA-3.3-70B model) to dynamically classify disputes and draft legal compliance notices, which are directly synchronized programmatically with UiPath Orchestrator using RESTful OAuth2 integrations.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📝 **AI Notice Drafting** | Formulates professional, legally binding legal notices from plain English/Hindi inputs |
| ⚖️ **Indian Law Citations** | Accurately maps and cites relevant Acts & Sections (failsafes prevent invalid references) |
| ✏️ **Interactive Notice Editor** | Refine, customize, and preview notice drafts directly in the dashboard before dispatch |
| 📄 **Word Document Engine** | Generates clean, print-ready Word files (.docx) styled with formal law-firm margins |
| 📊 **Litigation Dashboard** | Track metrics, case logs, and transition statuses (Review ➔ Sent ➔ Resolved ➔ Escalated) |
| 📬 **Secure SMTP Dispatch** | Automatically emails notice documents to the opposing party using secure Gmail SSL |
| 🍊 **UiPath Maestro Sync** | Syncs case metadata and details with UiPath Maestro Case Management via Confidential Application OAuth2 |
| 🛠️ **Token Refresh Helper** | Built-in helper script (`get_token.py`) to handle automated OAuth2 token generation |
| 💾 **SQLite DB Store** | Stores case histories, client data, and status changes locally and securely |

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                             USER'S BROWSER                             │
│                                                                        │
│  ┌───────────────────────┐            ┌─────────────────────────────┐  │
│  │ 📝 File New Case      │            │ 📊 Case Tracker & Manager   │  │
│  │ Inputs & Drafting    │            │ Analytics & Metrics Log     │  │
│  └───────────────────────┘            └─────────────────────────────┘  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
                         ┌────────────────────┐
                         │    Streamlit UI    │
                         └──────────┬─────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│  Groq Cloud  │             │   Local DB   │             │    UiPath    │
│  LLaMA 3.3   │             │   (SQLite)   │             │   Maestro    │
└──────┬───────┘             └──────────────┘             └──────┬───────┘
       │                                                         │
       ▼                                                         ▼
┌──────────────┐                                          ┌──────────────┐
│  Word Engine │                                          │  Automation  │
│ python-docx  │                                          │  Case Flow   │
└──────┬───────┘                                          └──────────────┘
       │
       ▼
┌──────────────┐
│  SMTP Server │
│   (Gmail)    │
└──────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Responsive portal with premium dark HSL legal styling |
| **AI Backend** | Groq API (LLaMA-3.3-70B-versatile) | Context parsing, category classification, and legal notice drafting |
| **Doc Gen** | python-docx | Times New Roman, 1.25 spacing, 1-inch margins document compiler |
| **Database** | SQLite3 | Local storage of case Briefs and status configurations |
| **Email** | SMTP / smtplib (SSL Port 465) | Automated emailing of notice packages to opposing parties |
| **Orchestration** | UiPath Maestro API | Enterprise sync of cases to Case Management portal |
| **Auth Helper** | Requests | OAuth2 client credentials token generation |

---

## 📁 Project Structure

```
legalease/
│
├── app.py                  # Streamlit Web App (Forms, Analytics Dashboard, Layout CSS)
├── agent.py                # Groq LLM Agent (dispute parsing, Indian code citations, prompt logic)
├── document_generator.py   # Formats notices and compiles into standard law-firm .docx files
├── email_sender.py         # SMTP library managing secure Gmail SSL dispatch
├── uipath_connector.py     # Connects and synchronizes cases with UiPath Maestro
├── get_token.py            # OAuth2 command-line credentials & token generation helper
├── test_modules.py         # Verification test suite for local database, LLM, and doc generator
├── requirements.txt        # Package dependencies list
├── .gitignore              # Protects secrets (.env), sqlite (.db), and documents (.docx)
├── .env.example            # Environment variables template
└── legalease.db            # Local SQLite database (automatically generated on first run)
```

---

## 🚀 Setup Instructions (Getting Started)

### Prerequisites
* **Python 3.10+**
* A **Groq Console** API Key (Free tier available)
* A **Gmail Account** (with 2-Step Verification enabled)
* A **UiPath Automation Cloud** Account (for Maestro Sync)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and enter your keys (see instructions below):
```env
GROQ_API_KEY=gsk_your_groq_key_here
GMAIL_ADDRESS=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_16_character_app_password

# Optional: UiPath Integration Configuration
UIPATH_ORG=your_org_name
UIPATH_TENANT=your_tenant_name
UIPATH_ACCESS_TOKEN=your_access_token
```

### 3. Run Verification Tests
Verify all API integrations, document generators, and database connections work correctly:
```bash
python test_modules.py
```

### 4. Launch the Web Application
```bash
streamlit run app.py
```
Open **`http://localhost:8501`** in your browser to experience the LegalEase portal.

---

## 🔑 Environment Variables & Keys

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Key from [console.groq.com](https://console.groq.com) to query LLaMA-3.3 |
| `GMAIL_ADDRESS` | ✅ Yes | Your Gmail email address used for sending notice emails |
| `GMAIL_APP_PASSWORD` | ✅ Yes | 16-character Google App Password (not your primary password) |
| `UIPATH_ORG` | Optional | Logical organization name from your Automation Cloud URL |
| `UIPATH_TENANT` | Optional | Target tenant name (usually `DefaultTenant`) |
| `UIPATH_ACCESS_TOKEN` | Optional | JWT bearer token generated via OAuth2 client credentials |

---

## 🔑 How to Obtain Keys

### A. Groq API Key
1. Visit the [Groq Console](https://console.groq.com/).
2. Navigate to **API Keys** in the sidebar.
3. Click **Create API Key**, name it `LegalEase`, and copy the token.

### B. Gmail App Password
1. Go to your [Google Account Settings](https://myaccount.google.com/).
2. Select **Security** from the left-hand menu.
3. Under "How you sign in to Google", ensure **2-Step Verification** is turned ON.
4. Click on **2-Step Verification**, scroll to the very bottom, and select **App passwords**.
5. Give the app a name (e.g., `LegalEase App`) and click **Create**.
6. Copy the displayed 16-character code (remove spaces when pasting in `.env`).

### C. UiPath Integration Credentials
1. **Find `UIPATH_ORG`**: Log in to [UiPath Automation Cloud](https://cloud.uipath.com). Look at your browser URL: `https://cloud.uipath.com/YOUR_ORGANIZATION_NAME/...`. Your organization name is your `UIPATH_ORG` (e.g., `legaleaseorg`).
2. **Find `UIPATH_TENANT`**: Go to **Admin** > **Tenants** in the sidebar. Copy your tenant name (usually `DefaultTenant`).
3. **Generate `UIPATH_ACCESS_TOKEN`**:
   * Navigate to **Admin** > **External Applications** (left sidebar).
   * Click **Add Application** and choose **Confidential Application** as the application type.
   * Click **Add Scopes**, select the **Orchestrator** resource, click the **Application Scope(s)** tab, and tick **Select all** (or check `OR.Execution`, `OR.Folders`, `OR.Jobs`, and `OR.Queues`).
   * Click **Save** to create the application and copy the **App ID (Client ID)** and **App Secret**.
   * Run the helper script in your terminal to fetch the access token automatically:
     ```bash
     python get_token.py
     ```
   * Choose option `2`, paste your App ID and App Secret when prompted, and the script will automatically write the token into your `.env` file.

   > ⚠️ **Note on Token Expiration**: UiPath access tokens expire every **1 hour**. If you encounter authentication or connection errors when running the app later, simply re-run `python get_token.py` to quickly refresh your token.

---

## ⚙️ How It Works

### Step 1 — Case Intake
The client files a dispute description in plain language, entering contact details for both parties and setting claim specifics (e.g. refund requests, cheque numbers, invoices).

### Step 2 — AI Classification & Drafting
The backend triggers Groq (LLaMA-3.3). The system identifies the category of dispute and drafts a legal notice, mapping the grievance details to specific sections of Indian acts.

### Step 3 — UiPath Case Synchronization
If credentials are set, the portal calls the UiPath Maestro API, creating a matching case file directly inside your Orchestration tenant for human-in-the-loop audits.

### Step 4 — File Generation & Review
A formatted `.docx` file matching legal standards (1-inch margins, Times New Roman, center-aligned title) is created. The user reviews the draft on a visual editor and can overwrite paragraphs or regenerate documents instantly.

### Step 5 — Notice Dispatch
The notice can be downloaded as a document or emailed directly to the opposing party using Gmail SMTP with the document attached as an enclosure. The database updates the status to `"Notice Sent"`.

---

## 🧪 Verification & Testing

Verify code modules, AI agent prompts, doc generation, and DB structures programmatically:
```bash
python test_modules.py
```
**Expected Test Results:**
```text
Initializing test database...
Drafting test notice using Groq API...
Detected Category: Consumer Dispute
Generating styled legal document (.docx)...
Document created at: notice_LE-TEST.docx
Syncing case with UiPath Maestro sandbox...
Sync message: HTTP 405: 405 Not Allowed  # (Or "Created" if Maestro app is active)
Saving case in local database...
Verifying case retrieval...
[SUCCESS] Retrieved case details match.
```

---

## 🌐 Deployment

LegalEase is fully deployed and accessible live:
🚀 **[legalease-adhipatya.streamlit.app](https://legalease-adhipatya.streamlit.app/)**

For custom deployment on **Streamlit Community Cloud**:
1. Push your code to your GitHub repository.
2. Log in to [share.streamlit.io](https://share.streamlit.io) via GitHub.
3. Click **Create App** and connect your `LegalEase` repository.
4. Open **Advanced Settings** and paste the contents of your `.env` file directly into the **Secrets** box.
5. Click **Deploy**. Your site will compile and be online instantly.

---

## 🗺️ Roadmap

- [x] AI legal notice drafting (Groq LLaMA-3.3)
- [x] Law-firm standard Word document compiler
- [x] Case Tracker litigation metrics panel
- [x] Secure SMTP Gmail dispatch system
- [x] UiPath Maestro Case API synchronization
- [x] Automatic credentials and token generator script
- [x] Local SQLite database cache
- [x] Deep dark HSL legal visual design
- [x] Unified `.gitignore` credential protections
- [ ] Direct PDF export engine integration
- [ ] Regional language drafting support (Hindi, Tamil, Marathi)
- [ ] OCR intake scanner for invoices and tenancy agreements
- [ ] Multi-user lawyer dashboards

---

<div align="center">

Built with ❤️ for individuals and SMBs who deserve access to legal protection.

</div>
