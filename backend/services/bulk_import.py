import csv
import io
from datetime import datetime
from typing import List, Dict
from sqlalchemy.orm import Session
from models import Customer, Account

class BulkImportService:
    """
    Bulk data import/export for customers and accounts.
    
    CSV Template for Customer Import:
    full_name,father_name,phone,village,ward,street,landmark,pincode,aadhar,voter_id,identity_type
    
    CSV Template for Account Import:
    customer_id,account_type,credit_limit,account_status
    """
    
    CUSTOMER_REQUIRED_FIELDS = ['full_name', 'phone', 'village']
    ACCOUNT_REQUIRED_FIELDS = ['customer_id', 'account_type']
    
    @staticmethod
    def import_customers(csv_content: str, db: Session) -> Dict:
        """
        Import customers from CSV.
        
        Format: full_name, father_name, phone, village, ward, street, landmark, pincode, aadhar, voter_id, identity_type
        """
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            imported = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):  # start=2 because first row is header
                try:
                    # Validate required fields
                    for field in BulkImportService.CUSTOMER_REQUIRED_FIELDS:
                        if not row.get(field) or not row[field].strip():
                            errors.append(f"Row {row_num}: Missing required field '{field}'")
                            continue
                    
                    # Check if customer already exists (by phone)
                    existing = db.query(Customer).filter(
                        Customer.phone == row['phone']
                    ).first()
                    
                    if existing:
                        errors.append(f"Row {row_num}: Customer with phone {row['phone']} already exists")
                        continue
                    
                    # Create new customer
                    customer = Customer(
                        customer_id=f"CUST-{datetime.now().timestamp()}",
                        full_name=row['full_name'],
                        father_name=row.get('father_name'),
                        phone=row['phone'],
                        village=row['village'],
                        ward=row.get('ward'),
                        street=row.get('street'),
                        landmark=row.get('landmark'),
                        pincode=row.get('pincode'),
                        aadhar_number=row.get('aadhar'),
                        voter_id=row.get('voter_id'),
                        identity_type=row.get('identity_type', 'aadhar'),
                        registration_date=datetime.now(),
                        kyc_status="pending"
                    )
                    
                    db.add(customer)
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            db.commit()
            
            return {
                "status": "success",
                "imported": imported,
                "errors": errors,
                "total_errors": len(errors),
                "message": f"Successfully imported {imported} customers"
            }
        
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def import_accounts(csv_content: str, db: Session) -> Dict:
        """
        Import accounts from CSV.
        
        Format: customer_id, account_type, credit_limit, account_status
        """
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            imported = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    # Validate required fields
                    for field in BulkImportService.ACCOUNT_REQUIRED_FIELDS:
                        if not row.get(field) or not row[field].strip():
                            errors.append(f"Row {row_num}: Missing required field '{field}'")
                            continue
                    
                    # Check if customer exists
                    customer = db.query(Customer).filter(
                        Customer.customer_id == row['customer_id']
                    ).first()
                    
                    if not customer:
                        errors.append(f"Row {row_num}: Customer {row['customer_id']} not found")
                        continue
                    
                    # Create account
                    account = Account(
                        account_id=f"ACC-{datetime.now().timestamp()}",
                        customer_id=row['customer_id'],
                        account_type=row.get('account_type', 'credit'),
                        credit_limit=float(row.get('credit_limit', 0)) if row.get('credit_limit') else 0,
                        account_status=row.get('account_status', 'active'),
                        account_opened_date=datetime.now(),
                        outstanding_balance=0,
                        total_paid=0
                    )
                    
                    db.add(account)
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            db.commit()
            
            return {
                "status": "success",
                "imported": imported,
                "errors": errors,
                "total_errors": len(errors),
                "message": f"Successfully imported {imported} accounts"
            }
        
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def export_customers(db: Session) -> str:
        """
        Export all customers to CSV format.
        """
        try:
            customers = db.query(Customer).all()
            
            output = io.StringIO()
            fieldnames = [
                'customer_id', 'full_name', 'father_name', 'phone', 'village',
                'ward', 'street', 'landmark', 'pincode', 'aadhar_number',
                'voter_id', 'kyc_status', 'registration_date'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for customer in customers:
                writer.writerow({
                    'customer_id': customer.customer_id,
                    'full_name': customer.full_name,
                    'father_name': customer.father_name,
                    'phone': customer.phone,
                    'village': customer.village,
                    'ward': customer.ward,
                    'street': customer.street,
                    'landmark': customer.landmark,
                    'pincode': customer.pincode,
                    'aadhar_number': customer.aadhar_number,
                    'voter_id': customer.voter_id,
                    'kyc_status': customer.kyc_status,
                    'registration_date': customer.registration_date.isoformat() if customer.registration_date else ''
                })
            
            return output.getvalue()
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def export_accounts(db: Session) -> str:
        """
        Export all accounts to CSV format.
        """
        try:
            accounts = db.query(Account).all()
            
            output = io.StringIO()
            fieldnames = [
                'account_id', 'customer_id', 'account_type', 'credit_limit',
                'outstanding_balance', 'total_paid', 'account_status',
                'account_opened_date', 'last_transaction_date'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            for account in accounts:
                writer.writerow({
                    'account_id': account.account_id,
                    'customer_id': account.customer_id,
                    'account_type': account.account_type,
                    'credit_limit': account.credit_limit,
                    'outstanding_balance': account.outstanding_balance,
                    'total_paid': account.total_paid,
                    'account_status': account.account_status,
                    'account_opened_date': account.account_opened_date.isoformat() if account.account_opened_date else '',
                    'last_transaction_date': account.last_transaction_date.isoformat() if hasattr(account, 'last_transaction_date') and account.last_transaction_date else ''
                })
            
            return output.getvalue()
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    @staticmethod
    def validate_csv_format(csv_content: str, import_type: str) -> Dict:
        """
        Validate CSV format before import.
        """
        try:
            csv_file = io.StringIO(csv_content)
            reader = csv.DictReader(csv_file)
            
            if not reader.fieldnames:
                return {"valid": False, "error": "CSV file is empty or invalid"}
            
            required_fields = (
                BulkImportService.CUSTOMER_REQUIRED_FIELDS if import_type == "customers"
                else BulkImportService.ACCOUNT_REQUIRED_FIELDS
            )
            
            missing_fields = [f for f in required_fields if f not in reader.fieldnames]
            
            if missing_fields:
                return {
                    "valid": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            row_count = sum(1 for _ in reader)
            
            return {
                "valid": True,
                "fieldnames": list(reader.fieldnames),
                "row_count": row_count,
                "message": f"CSV is valid with {row_count} records"
            }
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def get_import_template(import_type: str) -> str:
        """
        Return CSV template for the specified import type.
        """
        if import_type == "customers":
            return "full_name,father_name,phone,village,ward,street,landmark,pincode,aadhar,voter_id,identity_type\n" \
                   "Raj Kumar,Hari Kumar,9876543210,VillageName,Ward1,Main Street,near temple,400001,123456789012,ABC123,aadhar\n"
        elif import_type == "accounts":
            return "customer_id,account_type,credit_limit,account_status\n" \
                   "CUST-123456,credit,50000,active\n"
        else:
            return "Unknown import type"
