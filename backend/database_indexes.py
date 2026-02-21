"""
MongoDB Index Creation Script
Implements all critical indexes for optimal query performance
Run this script once to create indexes on all collections
"""

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING, TEXT
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "bahi_khata_db")


async def create_all_indexes():
    """
    Creates all necessary indexes for the Bahi-Khata Digital system
    Based on CODE_ANALYSIS_AND_TESTING.md index blueprint
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    
    print("Starting MongoDB Index Creation...")
    
    # ============================================
    # 1. USERS COLLECTION
    # ============================================
    print("\n[1/5] Creating indexes for 'users' collection...")
    users = db.users
    
    # Unique index on phone (critical for login)
    await users.create_index(
        [("phone", ASCENDING)],
        unique=True,
        name="idx_phone_unique"
    )
    print("  ✓ Created unique index on phone")
    
    # Index on retailer_id for filtering
    await users.create_index(
        [("retailer_id", ASCENDING)],
        name="idx_retailer_id"
    )
    print("  ✓ Created index on retailer_id")
    
    # Compound index for active status queries
    await users.create_index(
        [("is_active", ASCENDING), ("created_at", DESCENDING)],
        name="idx_active_created"
    )
    print("  ✓ Created compound index on is_active + created_at")
    
    # ============================================
    # 2. CUSTOMERS COLLECTION
    # ============================================
    print("\n[2/5] Creating indexes for 'customers' collection...")
    customers = db.customers
    
    # Primary query: filter by retailer
    await customers.create_index(
        [("retailer_id", ASCENDING)],
        name="idx_retailer_id"
    )
    print("  ✓ Created index on retailer_id")
    
    # Compound index: retailer + risk classification (critical for dashboard)
    await customers.create_index(
        [("retailer_id", ASCENDING), ("risk_classification", ASCENDING)],
        name="idx_retailer_risk"
    )
    print("  ✓ Created compound index on retailer_id + risk_classification")
    
    # Compound index: retailer + village (for village-wise filtering)
    await customers.create_index(
        [("retailer_id", ASCENDING), ("village", ASCENDING)],
        name="idx_retailer_village"
    )
    print("  ✓ Created compound index on retailer_id + village")
    
    # Phone search
    await customers.create_index(
        [("phone", ASCENDING)],
        name="idx_phone"
    )
    print("  ✓ Created index on phone")
    
    # Text search on name and father_name
    await customers.create_index(
        [("full_name", TEXT), ("father_name", TEXT)],
        name="idx_text_search",
        default_language="english"
    )
    print("  ✓ Created text index on full_name + father_name")
    
    # ============================================
    # 3. LEDGER_ENTRIES COLLECTION
    # ============================================
    print("\n[3/5] Creating indexes for 'ledger_entries' collection...")
    ledger = db.ledger_entries
    
    # Most critical: customer's transaction history
    await ledger.create_index(
        [("customer_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_customer_created"
    )
    print("  ✓ Created compound index on customer_id + created_at (DESC)")
    
    # Retailer-level reporting
    await ledger.create_index(
        [("retailer_id", ASCENDING), ("created_at", DESCENDING)],
        name="idx_retailer_created"
    )
    print("  ✓ Created compound index on retailer_id + created_at (DESC)")
    
    # Transaction type filtering
    await ledger.create_index(
        [("retailer_id", ASCENDING), ("entry_type", ASCENDING), ("created_at", DESCENDING)],
        name="idx_retailer_type_created"
    )
    print("  ✓ Created compound index on retailer_id + entry_type + created_at")
    
    # Outstanding balance queries (interest calculation)
    await ledger.create_index(
        [("customer_id", ASCENDING), ("outstanding_balance", DESCENDING)],
        name="idx_customer_outstanding"
    )
    print("  ✓ Created compound index on customer_id + outstanding_balance")
    
    # ============================================
    # 4. INTEREST_LOGS COLLECTION
    # ============================================
    print("\n[4/5] Creating indexes for 'interest_logs' collection...")
    interest_logs = db.interest_logs
    
    # Customer-wise interest history
    await interest_logs.create_index(
        [("customer_id", ASCENDING), ("applied_date", DESCENDING)],
        name="idx_customer_date"
    )
    print("  ✓ Created compound index on customer_id + applied_date (DESC)")
    
    # Date-based queries (batch job monitoring)
    await interest_logs.create_index(
        [("applied_date", DESCENDING)],
        name="idx_applied_date"
    )
    print("  ✓ Created index on applied_date (DESC)")
    
    # Retailer-level interest reporting
    await interest_logs.create_index(
        [("retailer_id", ASCENDING), ("applied_date", DESCENDING)],
        name="idx_retailer_date"
    )
    print("  ✓ Created compound index on retailer_id + applied_date")
    
    # ============================================
    # 5. BEHAVIORAL_FLAGS COLLECTION
    # ============================================
    print("\n[5/5] Creating indexes for 'behavioral_flags' collection...")
    flags = db.behavioral_flags
    
    # Customer-specific flags
    await flags.create_index(
        [("customer_id", ASCENDING), ("flag_type", ASCENDING)],
        name="idx_customer_flag"
    )
    print("  ✓ Created compound index on customer_id + flag_type")
    
    # Active flags monitoring
    await flags.create_index(
        [("is_active", ASCENDING), ("created_at", DESCENDING)],
        name="idx_active_created"
    )
    print("  ✓ Created compound index on is_active + created_at")
    
    # Retailer-level flag analysis
    await flags.create_index(
        [("retailer_id", ASCENDING), ("flag_type", ASCENDING), ("is_active", ASCENDING)],
        name="idx_retailer_flag_active"
    )
    print("  ✓ Created compound index on retailer_id + flag_type + is_active")
    
    print("\n" + "="*60)
    print("✓ ALL INDEXES CREATED SUCCESSFULLY")
    print("="*60)
    
    # List all indexes for verification
    print("\n📊 Index Summary:\n")
    collections = ["users", "customers", "ledger_entries", "interest_logs", "behavioral_flags"]
    
    for coll_name in collections:
        coll = db[coll_name]
        indexes = await coll.index_information()
        print(f"\n{coll_name}:")
        for idx_name, idx_info in indexes.items():
            if idx_name != "_id_":
                keys = idx_info.get('key', [])
                unique = " [UNIQUE]" if idx_info.get('unique', False) else ""
                print(f"  • {idx_name}: {keys}{unique}")
    
    client.close()
    print("\n✓ Database connection closed")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║   Bahi-Khata Digital - MongoDB Index Creator        ║
    ║   Production-Ready Database Optimization            ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    asyncio.run(create_all_indexes())
    
    print("\n✅ Index creation complete. Run this script again to verify indexes.")
    print("💡 Next steps:")
    print("   1. Restart FastAPI server to benefit from new indexes")
    print("   2. Run performance benchmarks to verify improvements")
    print("   3. Monitor query execution times in production\n")
