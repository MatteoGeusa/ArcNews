import sqlite3

class DatabaseManager:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.connection.execute("PRAGMA foreign_keys = 1")
        self.cursor = self.connection.cursor()
        
    def link_exists(self, url):
        self.cursor.execute("SELECT 1 FROM news WHERE url = ?", (url,))
        result = self.cursor.fetchone()
        return result is not None

    def apply_migration(self):
        query = """
        CREATE TABLE IF NOT EXISTS news (
            url TEXT PRIMARY KEY,
            date TIME,
            title TEXT,
            content TEXT,
            photos_json TEXT,
            checksum TEXT
        );
        """
        self.cursor.executescript(query)
        self.connection.commit()

    def upsert_news(self, checksum_id, date, title, url, content, photos_json):
        self.cursor.execute("SELECT checksum FROM news WHERE url = ?", (url,))
        result = self.cursor.fetchone()
        
        if result is None: # Nuova notizia trovata
            query = """
            INSERT INTO news (url, date, title, content, photos_json, checksum)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(query, (url, date, title, content, photos_json, checksum_id))
            self.connection.commit()
            return True

        else:
            old_checksum = result[0]
            
            if old_checksum != checksum_id: # Notizia esistente
                query = """
                UPDATE news 
                SET date = ?, title = ?, content = ?, photos_json = ?, checksum = ?
                WHERE url = ?
                """
                self.cursor.execute(query, (date, title, content, photos_json, checksum_id, url))
                self.connection.commit()
                return True
            else:
                return False
        
    def close(self):
        self.connection.close()