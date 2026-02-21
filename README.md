# Bahi-Khata Digital

**एक विश्वसनीय डिजिटल बही-खाता (Digital Ledger) प्रणाली ग्रामीण भारतीय खुदरा दुकानों के लिए।**

*A comprehensive double-entry ledger system for rural Indian retailers (Kirana shops).*

---

## 🎯 Project Overview

**Bahi-Khata Digital** is a **Hindi-first, mobile-first web application** designed to empower village shop owners (किराना दुकान वाले) to manage customer credit, track outstanding payments, and maintain financial records with **2% monthly interest calculation**.

### Core Features

✅ **Customer KYC & Onboarding**
- Full name, Father's name (critical for villages with common names)
- Phone, Village/Ward, Street, Landmark, Pincode
- Aadhaar/Voter ID verification with document upload
- Risk classification (Excellent, Average, High Risk, NPA)

✅ **Double-Entry Ledger Engine**
- Strict ACID-compliant transaction system
- Sale on Credit, Cash Payment, Interest Applied, NPA WriteOff
- Promised Return Date enforcement
- Retailer's own Accounts Payable module

✅ **Automated 2% Monthly Interest**
- Daily batch job (12:01 AM IST)
- Daily Rate = (Outstanding Principal * 0.02) / 30
- Payment waterfall algorithm (clears interest first, then principal)
- Manual freeze/waive-off override

✅ **Risk Management & Behavioral Flagging**
- Automated: On-Time Payer, Frequent Delays, High Debt Risk
- Manual: Good account, Do not give credit, NPA
- Behavioral scoring

✅ **Digital Receipts & WhatsApp Integration**
- Printable PDF receipts
- WhatsApp deep link sharing
- Transaction memo with balance summary

✅ **Global Dashboard & Analytics**
- Macro view: Total outstanding, interest accrued, NPA
- Micro: Village-wise, Ward-wise, Date-range filters
- Collection route planning

✅ **Bilingual Support**
- Hindi-first UI
- English toggle
- All labels, buttons, receipts in both languages

✅ **Bulk CSV Import/Export**
- Legacy data migration from paper ledgers
- Template-based import
- Error logging and reporting

✅ **Role-Based Access Control**
- Admin (Full access)
- Helper (Can log transactions, cannot delete/modify)
- Read-Only (Reporting only)

✅ **Offline-First Mobile App**
- localStorage queue for offline transaction creation
- Auto-sync when internet returns
- Works well on slow rural internet

---

## 🏗️ Tech Stack

### Frontend
- **React 18** with Vite
- **Tailwind CSS** with custom "Bahi-Khata" design system
- **Zustand** for state management
- **i18next** for bilingual support (Hindi/English)
- **Lucide React** for icons
- **Sonner** for notifications
- **Papaparse** for CSV handling

### Backend
- **FastAPI** (Python async framework)
- **MongoDB** for document storage
- **APScheduler** for daily interest batch job
- **Pydantic** for validation
- **PyJWT** for authentication

### Database
- **MongoDB**
  - Customer_Account collection (Master profiles)
  - Ledger_Transaction collection (Transaction headers)
  - Ledger_Entry collection (Double-entry lines)
  - Users collection (RBAC)
  - Communications_Log collection (WhatsApp/SMS history)

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.9+
- MongoDB 5.0+
- Git

### Setup

#### 1. Clone Repository
```bash
git clone https://github.com/nikhilshivpuriya29/kirana-ledger-system.git
cd kirana-ledger-system
```

#### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your MongoDB URI
python -m uvicorn main:app --reload
```

#### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### 4. Access Application
- Frontend: `http://localhost:5173`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

---

## 📊 Business Rules

### Rule 1: Double-Entry Integrity
Every transaction must have ≥2 lines (DR + CR) that balance.

### Rule 2: Daily 2% Interest Calculation
- **Batch Timing**: 12:01 AM IST
- **Daily Rate**: (Outstanding_Principal * 0.02) / 30
- **Scope**: Active accounts with Outstanding > 0, Promised_Date < TODAY, Freeze_Interest = false
- **Execution**: Posts automatic Interest_Applied transaction

### Rule 3: Payment Waterfall
1. Calculate Outstanding_Interest
2. Calculate Outstanding_Principal
3. If Payment ≤ Interest: Tag as Interest_Paid
4. Else: Clear Interest, reduce Principal
5. Only future interest on remaining Principal

### Rule 4: NPA WriteOff
- Creates NPA_WriteOff transaction header
- Posts DR Bad_Debt_Expense, CR Customer_Receivable
- Auto-sets Customer Risk_Category = NPA
- Do_Not_Give_Credit = true

### Rule 5: Item Return
- Creates Item_Return transaction
- Posts DR Sales_Returns, CR Customer_Receivable (Principal)
- Principal reduced automatically
- Interest recalculated on new principal

---

##📁 Project Structure

```
kirana-ledger-system/
├── frontend/                  # React Vite app
│   ├── src/
│   │   ├── pages/            # Login, Dashboard, Customers, etc.
│   │   ├── components/       # Reusable UI components
│   │   ├── stores/           # Zustand state
│   │   ├── services/         # API calls, Auth
│   │   ├── i18n/            # Hindi/English translations
│   │   └── utils/           # Helpers, formatters
│   └── package.json
│
├── backend/                   # FastAPI app
│   ├── app/
│   │   ├── models/          # Pydantic schemas
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Validators, formatters
│   │   └── schedulers.py    # Daily interest job
│   ├── requirements.txt
│   └── main.py
│
├── docs/                      # Documentation
│   ├── API_SPECIFICATION.md
│   ├── DATABASE_SCHEMA.md
│   ├── BUSINESS_RULES.md
│   └── DEPLOYMENT.md
│
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 🎨 Design System

**Theme**: "The Trusted Munim" (Digital Accountant)

- **Primary Color**: Saffron (#EA580C)
- **Secondary Color**: Green (#15803D)
- **Background**: Warm Cream (#FFF7ED)
- **Typography**: Mukta (Headers), Hind (Body)
- **Style**: Paper-stack cards, large touch targets (h-14 inputs), mobile-first

See `docs/design_guidelines.json` for complete design system.

---

## 🔐 Authentication

- **Phone Number + 6-digit PIN** (UPI-style)
- JWT tokens for API auth
- Secure session management
- Support for Admin/Helper roles

---

## 📝 Bulk Import Template

Download CSV template from the app:
```csv
Customer_Name,Father_Name,Phone_Number,Village_Ward,Aadhar,Legacy_Debt,Debt_As_Of_Date,Promised_Return_Date,Notes
हरि प्रसाद,रवि प्रसाद,9876543210,भारतपुर वार्ड 5,123456789012,5000,01/02/2026,15/02/2026,पुरानी डायरी से
```

---

## 📞 Support

For issues or feature requests, please create a GitHub Issue.

---

## 📜 License

MIT License - See LICENSE file

---

## 👥 Contributors

- **Nikhil Shivpuriya** (@hikhilshivpuriya29)

---

**Built with ❤️ for rural India. 🇮🇳**
