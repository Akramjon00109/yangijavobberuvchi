"""
Database module for Neon PostgreSQL
Stores: Instagram session, processed comments, statistics
"""
import os
import json
from datetime import datetime
from typing import Optional

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False
    print("⚠️ psycopg2 not installed - database features disabled")


class Database:
    """PostgreSQL database handler for Neon DB"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "")
        self.conn = None
        self.enabled = False
        
        if not self.database_url:
            print("⚠️ DATABASE_URL kiritilmagan - lokal rejimda ishlaydi")
            return
        
        if not HAS_PSYCOPG2:
            return
        
        self._connect()
        if self.conn:
            self._create_tables()
            self.enabled = True
    
    def _connect(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.conn.autocommit = True
            print("✅ Neon DB ga ulandi!")
        except Exception as e:
            print(f"❌ Database ulanish xatosi: {e}")
            self.conn = None
    
    def _create_tables(self):
        """Create required tables if they don't exist"""
        try:
            with self.conn.cursor() as cur:
                # Session table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS instagram_session (
                        id SERIAL PRIMARY KEY,
                        session_data TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Processed comments table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS processed_comments (
                        id SERIAL PRIMARY KEY,
                        comment_id VARCHAR(50) UNIQUE NOT NULL,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Statistics table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS statistics (
                        id SERIAL PRIMARY KEY,
                        stat_date DATE DEFAULT CURRENT_DATE,
                        comments_processed INT DEFAULT 0,
                        dms_sent INT DEFAULT 0,
                        keywords_triggered INT DEFAULT 0,
                        UNIQUE(stat_date)
                    )
                """)
                
            print("✅ Database jadvallar tayyor!")
        except Exception as e:
            print(f"❌ Jadval yaratishda xatolik: {e}")
    
    # ==================== Session Methods ====================
    
    def save_session(self, session_data: dict) -> bool:
        """Save Instagram session to database"""
        if not self.enabled:
            return False
        
        try:
            session_json = json.dumps(session_data)
            with self.conn.cursor() as cur:
                # Delete old sessions and insert new one
                cur.execute("DELETE FROM instagram_session")
                cur.execute(
                    "INSERT INTO instagram_session (session_data) VALUES (%s)",
                    (session_json,)
                )
            print("💾 Session databazaga saqlandi")
            return True
        except Exception as e:
            print(f"❌ Session saqlashda xatolik: {e}")
            return False
    
    def load_session(self) -> Optional[dict]:
        """Load Instagram session from database"""
        if not self.enabled:
            return None
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT session_data FROM instagram_session ORDER BY updated_at DESC LIMIT 1")
                row = cur.fetchone()
                if row:
                    print("📥 Session databazadan yuklandi")
                    return json.loads(row['session_data'])
        except Exception as e:
            print(f"❌ Session yuklashda xatolik: {e}")
        return None
    
    # ==================== Processed Comments Methods ====================
    
    def is_comment_processed(self, comment_id: str) -> bool:
        """Check if a comment has been processed"""
        if not self.enabled:
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM processed_comments WHERE comment_id = %s",
                    (str(comment_id),)
                )
                return cur.fetchone() is not None
        except Exception as e:
            print(f"❌ Comment tekshirishda xatolik: {e}")
            return False
    
    def mark_comment_processed(self, comment_id: str) -> bool:
        """Mark a comment as processed"""
        if not self.enabled:
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO processed_comments (comment_id) VALUES (%s) ON CONFLICT DO NOTHING",
                    (str(comment_id),)
                )
            return True
        except Exception as e:
            print(f"❌ Comment saqlashda xatolik: {e}")
            return False
    
    def get_processed_comments(self) -> set:
        """Get all processed comment IDs"""
        if not self.enabled:
            return set()
        
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT comment_id FROM processed_comments")
                return {row[0] for row in cur.fetchall()}
        except Exception as e:
            print(f"❌ Commentlarni olishda xatolik: {e}")
            return set()
    
    # ==================== Statistics Methods ====================
    
    def increment_stat(self, stat_name: str, amount: int = 1) -> bool:
        """Increment a statistic for today"""
        if not self.enabled:
            return False
        
        if stat_name not in ['comments_processed', 'dms_sent', 'keywords_triggered']:
            return False
        
        try:
            with self.conn.cursor() as cur:
                cur.execute(f"""
                    INSERT INTO statistics (stat_date, {stat_name})
                    VALUES (CURRENT_DATE, %s)
                    ON CONFLICT (stat_date)
                    DO UPDATE SET {stat_name} = statistics.{stat_name} + %s
                """, (amount, amount))
            return True
        except Exception as e:
            print(f"❌ Statistika saqlashda xatolik: {e}")
            return False
    
    def get_today_stats(self) -> dict:
        """Get today's statistics"""
        if not self.enabled:
            return {}
        
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT comments_processed, dms_sent, keywords_triggered
                    FROM statistics WHERE stat_date = CURRENT_DATE
                """)
                row = cur.fetchone()
                if row:
                    return dict(row)
        except Exception as e:
            print(f"❌ Statistika olishda xatolik: {e}")
        return {'comments_processed': 0, 'dms_sent': 0, 'keywords_triggered': 0}
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()


# Singleton instance
db = Database()
