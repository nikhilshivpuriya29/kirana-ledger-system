from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from typing import Optional

class MongoDB:
    client: Optional[MongoClient] = None
    db = None

    def connect_db(self):
        """Create database connection pool."""
        self.client = MongoClient(
            os.getenv("MONGODB_URL", "mongodb://mongodb:27017")
        )
        self.db = self.client[os.getenv("DB_NAME", "bahi_khata")]
        
    def close_db(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def get_database(self):
        """Get database instance."""
        return self.db

# Initialize MongoDB connection
db = MongoDB()

# Collection names
COLLECTIONS = {
    'users': 'users',
    'customers': 'customers',
    'transactions': 'transactions',
    'interest_calculations': 'interest_calculations',
    'payment_schedules': 'payment_schedules',
}
