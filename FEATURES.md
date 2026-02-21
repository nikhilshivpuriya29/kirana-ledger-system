# Kirana Ledger System (Bahi-Khata Digital) - Features

## Completed Implementation

### 1. Customer Onboarding & KYC
- Full Name, Father's Name, Phone Number
- Granular Addressing: Village/City, Ward Number, Street/Mohalla, Landmark, Pincode
- Identity Verification: Aadhar Number or Voter ID
- KYC Status Tracking: pending, completed, rejected
- Registration Date and History

### 2. Ledger Engine - Double-Entry System
- Strict double-entry accounting for all transactions
- Debit Entries: What customer owes (liability)
- Credit Entries: Cash/Inventory outflow (asset decrease)
- Transaction Tracking with:
  - Exact Date and Time
  - Principal Amount
  - Promised Return Date
  - Items Description
  - Transaction Status (pending, completed)

### 3. Automated Interest & Penalty Engine
- **2% Monthly Interest Rule**
  - Daily batch processing (cron-based)
  - Compound interest calculation
  - Automatic interest entry generation
- **Penalty System**
  - Automatic penalty for overdue payments
  - Interest freeze/waive-off capabilities
- **Batch Processing**
  - Daily job scheduler for interest calculation
  - Automatic status updates
  - Report generation

### 4. Payment Waterfall Allocation
Payments are allocated in priority order:
1. Oldest pending interest (first)
2. Oldest pending penalties (second)
3. Oldest principal amount (third)

Partial payments supported with interest recalculation.

### 5. Risk Management & Behavioral Flagging

**Automated Flags:**
- **On-Time Payer**: 5+ consecutive on-time payments, no delays
- **Frequent Delays**: 3+ delayed payments
- **High Debt Risk**: Outstanding balance exceeds 50,000 rupees
- **NPA (Non-Performing Asset)**: Overdue beyond 90 days

**Manual Flags (Operator):**
- Good in maintaining account
- Do not give further credit (blocks new transactions)
- NPA override

**Risk Levels:**
- Critical: NPA or blocked status
- High: Multiple high-risk indicators
- Medium: Some risk signals
- Low: Healthy account

### 6. Returns & Refunds
- In-kind returns supported
- Return reason tracking
- Automatic balance adjustment
- Double-entry offset for returns

### 7. Global Dashboard & Analytics

**Macro View:**
- Total money out (outstanding balance)
- Total collections
- Total accounts
- Active accounts count
- NPA accounts count
- Pending interest charges
- Pending penalties
- Overdue amount (15+ days)

**Micro/Village-Wise View:**
- Village filtering
- Village-specific metrics
- Customer count per village
- Active/NPA accounts per village
- Average outstanding per account
- Village-wise collections tracking

**Reports:**
- Transaction summary (by date range)
- Overdue analysis
- Payment behavior report
- On-time payer percentage
- Risk percentage analysis

### 8. Bulk Data Import/Export

**CSV Import Templates:**
- Customer import: full_name, father_name, phone, village, ward, street, landmark, pincode, aadhar, voter_id, identity_type
- Account import: customer_id, account_type, credit_limit, account_status

**Export Features:**
- Export all customers to CSV
- Export all accounts to CSV
- Format validation
- Error reporting per row

**Error Handling:**
- Duplicate phone number detection
- Required field validation
- Customer existence validation
- Row-by-row error reporting

### 9. Frontend Pages

**Account Record Page (/account):**
- Account search by ID
- Customer details display
- Outstanding balance
- Total paid amount
- Account status
- Recent transactions table
- Links to add transaction and make payment
- Paper-stack card design
- Hindi-first UI with English toggle

**Dashboard Page (/dashboard):**
- Global summary metrics
- Village selection dropdown
- Village-specific analytics
- Metric cards with color coding
- Responsive grid layout
- Hindi-first interface
- Real-time data fetching

### 10. Backend APIs

**Ledger Routes:**
- POST /ledger/transaction - Create transaction
- POST /ledger/payment - Process payment
- GET /ledger/account/{account_id}/statement - Account statement
- POST /ledger/return - Process return

**Analytics Routes:**
- GET /analytics/dashboard/summary - Global metrics
- GET /analytics/dashboard/village/{village_name} - Village metrics
- GET /analytics/villages/list - List all villages
- GET /analytics/reports/transaction-summary - Transaction report
- GET /analytics/reports/overdue-analysis - Overdue analysis
- GET /analytics/reports/payment-behavior - Payment behavior

**Risk Management:**
- Evaluate account risk
- Apply manual flags
- Get account risk profile

### 11. Design & UX
- **Color Scheme**: Saffron (#EA580C) primary color
- **Typography**: Mukta (bold), Hind (regular) fonts
- **Design Pattern**: Paper-stack cards
- **Mobile-First**: Responsive design
- **Bilingual**: Hindi-first with English toggle
- **Authentication**: Phone Number + PIN (UPI-style)

### 12. Technology Stack
- **Frontend**: Next.js (React), TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB with SQLAlchemy ORM
- **Authentication**: JWT-based phone+PIN
- **Deployment**: Docker/Docker Compose

### 13. Advanced Features

**Offline Tolerance:**
- Works with intermittent connectivity
- Queue-based transaction handling
- Sync when connection restored

**Role-Based Access Control (RBAC):**
- Shop owner (full access)
- Manager (limited administrative)
- Accountant (read/report only)

**Comprehensive Logging:**
- Transaction audit trail
- Flag change history
- Error logging and monitoring

## API Endpoints Summary

### Authentication
- POST /auth/login - Phone + PIN login
- POST /auth/register - New user registration
- POST /auth/refresh - Refresh token

### Customers
- POST /customers - Create customer
- GET /customers/{customer_id} - Get customer
- PUT /customers/{customer_id} - Update customer
- GET /customers/village/{village} - List by village

### Ledger
- POST /ledger/transaction - Record transaction
- POST /ledger/payment - Process payment
- GET /ledger/account/{id}/statement - Account statement
- POST /ledger/return - Process return

### Analytics
- GET /analytics/dashboard/summary - Global summary
- GET /analytics/dashboard/village/{village} - Village metrics
- GET /analytics/villages/list - Village list
- GET /analytics/reports/transaction-summary - Transactions
- GET /analytics/reports/overdue-analysis - Overdue accounts
- GET /analytics/reports/payment-behavior - Payment analysis

### Bulk Operations
- POST /import/customers - Bulk customer import
- POST /import/accounts - Bulk account import
- GET /export/customers - Export customers CSV
- GET /export/accounts - Export accounts CSV

## Database Schema

### Collections
- **customers**: User information and KYC
- **accounts**: Customer accounts with balance tracking
- **ledger_transactions**: Transaction headers
- **ledger_entries**: Individual debit/credit entries
- **interest_entries**: Interest and penalty tracking
- **risk_flags**: Behavioral flags and risk assessment
- **audit_logs**: Complete transaction history

## Next Steps for Enhancement

- SMS/WhatsApp notification integration
- Print receipt generation
- Advanced reporting dashboards
- Mobile app (React Native)
- Payment gateway integration
- Multi-branch support
- Sync to central server
