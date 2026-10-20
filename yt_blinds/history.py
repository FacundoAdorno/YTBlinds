import sqlite3
import os
import re
from datetime import datetime

def sanitize_filename(name):
    """Elimina todos los caracteres no válidos en Windows y los reemplaza por un espacio."""
    if not name:
        return "download"
    # Caracteres prohibidos en Windows: < > : " / \ | ? * y caracteres de control (0-31)
    clean = re.sub(r'[<>:"/\\|?*\x00-\x1f]', ' ', name)
    # Colapsar espacios múltiples en uno solo y limpiar extremos
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean if clean else "download"

class DownloadHistoryManager:
    def __init__(self, db_path=None):
        if not db_path:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(base_dir, "data")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "default.db")

        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    path TEXT NOT NULL,
                    date TEXT NOT NULL,
                    type TEXT DEFAULT 'video',
                    UNIQUE(video_id, type)
                )
            """)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(downloads)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'video_id' not in columns:
                conn.execute("ALTER TABLE downloads ADD COLUMN video_id TEXT DEFAULT ''")
            conn.commit()

    def add_download(self, video_id, title, path, download_type='video'):
        sanitized_title = sanitize_filename(title)
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO downloads (video_id, title, path, date, type)
                VALUES (?, ?, ?, ?, ?)
                """,
                (video_id, sanitized_title, path, date_str, download_type)
            )
            conn.commit()

    def check_and_cleanup_missing_file(self, video_id, download_type, expected_dir):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT path, title FROM downloads WHERE video_id = ? AND type = ?", (video_id, download_type))
            row = cursor.fetchone()
            if row:
                saved_path, title = row
                file_exists = False
                if os.path.isfile(saved_path) and os.path.exists(saved_path):
                    file_exists = True
                else:
                    sanitized_title = sanitize_filename(title)
                    check_dir = saved_path if os.path.isdir(saved_path) else expected_dir
                    if os.path.exists(check_dir):
                        for f in os.listdir(check_dir):
                            if sanitized_title.lower() in f.lower() or video_id in f:
                                file_exists = True
                                break

                if not file_exists:
                    conn.execute("DELETE FROM downloads WHERE video_id = ? AND type = ?", (video_id, download_type))
                    conn.commit()
                    return False
                return True
            return False

    def get_history(self, download_type=None, filter_query=""):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = "SELECT title, path, date, type, video_id FROM downloads WHERE 1=1"
            params = []
            if download_type:
                query += " AND type = ?"
                params.append(download_type)
            if filter_query:
                query += " AND title LIKE ?"
                params.append(f"%{filter_query}%")
            query += " ORDER BY id DESC"
            cursor.execute(query, params)
            return cursor.fetchall()

history_manager = DownloadHistoryManager()
