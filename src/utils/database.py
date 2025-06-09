# DB access logic (e.g., SQLite)
import sqlite3
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HTSDatabase:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize the HTS database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create HTS tariff table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS hts_tariffs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hts_number TEXT NOT NULL,
                    description TEXT,
                    general_rate TEXT,
                    special_rate TEXT,
                    column2_rate TEXT,
                    section TEXT,
                    chapter TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_hts_number 
                ON hts_tariffs(hts_number)
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def insert_hts_data(self, data: pd.DataFrame):
        """Insert HTS tariff data into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                data.to_sql('hts_tariffs', conn, if_exists='append', index=False)
                logger.info(f"Inserted {len(data)} HTS records")
        except Exception as e:
            logger.error(f"Error inserting HTS data: {e}")
            raise
    
    def get_hts_by_number(self, hts_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve HTS data by HTS number."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM hts_tariffs 
                    WHERE hts_number = ? OR hts_number LIKE ?
                    LIMIT 1
                """, (hts_number, f"{hts_number}%"))
                
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    return dict(zip(columns, result))
                return None
        except Exception as e:
            logger.error(f"Error retrieving HTS data: {e}")
            return None
    
    def search_hts_by_description(self, description: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search HTS entries by description."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM hts_tariffs 
                    WHERE description LIKE ?
                    LIMIT ?
                """, (f"%{description}%", limit))
                
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in results]
        except Exception as e:
            logger.error(f"Error searching HTS data: {e}")
            return []
    
    def get_all_hts_numbers(self) -> List[str]:
        """Get all HTS numbers in the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT DISTINCT hts_number FROM hts_tariffs")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error retrieving HTS numbers: {e}")
            return []