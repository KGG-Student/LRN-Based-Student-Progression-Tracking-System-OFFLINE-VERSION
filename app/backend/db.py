import os
import sqlite3
from pathlib import Path

import mysql.connector
from werkzeug.security import generate_password_hash

SCHEMA_READY = False


def get_database_engine():
    return os.environ.get("APP_DB_ENGINE", "mysql").strip().lower()


def is_sqlite():
    return get_database_engine() == "sqlite"


class SQLiteCursor:
    def __init__(self, cursor, dictionary=False):
        self.cursor = cursor
        self.dictionary = dictionary

    def execute(self, query, params=None):
        query = self._translate_query(query)
        params = params or ()
        self.cursor.execute(query, params)
        return self

    def fetchone(self):
        row = self.cursor.fetchone()
        if row is None:
            return None
        return dict(row) if self.dictionary else tuple(row)

    def fetchall(self):
        rows = self.cursor.fetchall()
        if self.dictionary:
            return [dict(row) for row in rows]
        return [tuple(row) for row in rows]

    def close(self):
        self.cursor.close()

    def _translate_query(self, query):
        normalized = " ".join(query.split()).upper()

        if normalized.startswith("SET FOREIGN_KEY_CHECKS"):
            return "SELECT 1"

        if normalized.startswith("TRUNCATE TABLE "):
            table = query.split()[-1]
            return f"DELETE FROM {table}"

        if normalized.startswith("DELETE L FROM STUDENT_CHANGE_LOGS"):
            return """
                DELETE FROM student_change_logs
                WHERE lrn NOT IN (
                    SELECT lrn FROM student_records
                )
            """

        if normalized.startswith("DELETE S FROM STUDENTS"):
            return """
                DELETE FROM students
                WHERE lrn NOT IN (
                    SELECT lrn FROM student_records
                )
            """

        return query.replace("%s", "?")


class SQLiteConnection:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")

    def cursor(self, dictionary=False):
        return SQLiteCursor(self.connection.cursor(), dictionary=dictionary)

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_sqlite_path():
    configured_path = os.environ.get("SQLITE_DB_PATH")
    if configured_path:
        return Path(configured_path)

    app_data_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "LRNTrackingSystem"
    app_data_dir.mkdir(parents=True, exist_ok=True)
    return app_data_dir / "lrn_tracking.db"


def get_db_connection():
    if is_sqlite():
        return SQLiteConnection(get_sqlite_path())

    config = {
        "host": os.environ.get("DB_HOST", "db"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", "root"),
        "database": os.environ.get("DB_NAME", "mydb"),
    }

    ssl_disabled = os.environ.get("DB_SSL_DISABLED", "").lower() in {"1", "true", "yes"}
    ssl_ca = os.environ.get("DB_SSL_CA")
    if not ssl_disabled and config["host"] != "db":
        config["ssl_disabled"] = False
        if ssl_ca:
            config["ssl_ca"] = ssl_ca

    return mysql.connector.connect(**config)


def ensure_schema():
    global SCHEMA_READY

    if SCHEMA_READY:
        return

    conn = get_db_connection()
    cursor = conn.cursor()

    if is_sqlite():
        ensure_sqlite_schema(cursor)
        conn.commit()
        cursor.close()
        conn.close()
        SCHEMA_READY = True
        return

    schema_updates = [
        "ALTER TABLE students ADD COLUMN gender VARCHAR(10)",
        "ALTER TABLE students ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        "ALTER TABLE student_records ADD COLUMN remarks TEXT",
        "ALTER TABLE student_records ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
        "ALTER TABLE student_records ADD INDEX idx_student_records_lrn (lrn)",
        "ALTER TABLE student_records DROP INDEX unique_student_year_grade",
        "ALTER TABLE student_records ADD UNIQUE KEY unique_student_year (lrn, school_year)",
        "ALTER TABLE student_change_logs ADD COLUMN changed_by VARCHAR(80)",
    ]

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            lrn VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255),
            gender VARCHAR(10),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_records (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lrn VARCHAR(20),
            school_year VARCHAR(20),
            grade_level INT,
            gender VARCHAR(10),
            status VARCHAR(50),
            remarks TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_student_year (lrn, school_year),
            INDEX idx_student_records_lrn (lrn),
            FOREIGN KEY (lrn) REFERENCES students(lrn)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_change_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            lrn VARCHAR(20),
            field_name VARCHAR(100),
            old_value TEXT,
            new_value TEXT,
            school_year VARCHAR(20),
            grade_level INT,
            changed_by VARCHAR(80),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lrn) REFERENCES students(lrn)
        )
        """
    )

    cursor.execute(
        """
        DELETE r1
        FROM student_records r1
        JOIN student_records r2
            ON r1.lrn = r2.lrn
            AND r1.school_year = r2.school_year
            AND r1.id < r2.id
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'admin',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    for statement in schema_updates:
        try:
            cursor.execute(statement)
        except mysql.connector.Error as error:
            if error.errno not in (1060, 1061, 1062, 1091):
                raise

    cursor.execute(
        """
        UPDATE student_records
        SET remarks = ''
        WHERE LOWER(TRIM(remarks)) = 'nan'
        """
    )

    cursor.execute(
        """
        UPDATE student_records
        SET status = CASE
            WHEN UPPER(COALESCE(remarks, '')) LIKE '%PENDING TI%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%PENDING T/I%'
                THEN 'PENDING_TRANSFER_IN'
            WHEN UPPER(COALESCE(remarks, '')) LIKE '%T/O%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%T-O%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER OUT%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFERRED OUT%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER-OUT%'
                THEN 'TRANSFER_OUT'
            WHEN UPPER(COALESCE(remarks, '')) LIKE '%T/I%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%T-I%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER IN%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFERRED IN%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER-IN%'
                THEN 'TRANSFER_IN'
            ELSE 'ENROLLED'
        END
        """
    )

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0] or 0
    if user_count == 0:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            """,
            ("admin", generate_password_hash("admin123"), "admin"),
        )

    conn.commit()
    cursor.close()
    conn.close()
    SCHEMA_READY = True


def ensure_sqlite_schema(cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            lrn TEXT PRIMARY KEY,
            name TEXT,
            gender TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lrn TEXT,
            school_year TEXT,
            grade_level INTEGER,
            gender TEXT,
            status TEXT,
            remarks TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (lrn, school_year),
            FOREIGN KEY (lrn) REFERENCES students(lrn)
        )
        """
    )

    cursor.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_student_records_lrn
        ON student_records (lrn)
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS student_change_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lrn TEXT,
            field_name TEXT,
            old_value TEXT,
            new_value TEXT,
            school_year TEXT,
            grade_level INTEGER,
            changed_by TEXT,
            changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lrn) REFERENCES students(lrn)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'admin',
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        DELETE FROM student_records
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM student_records
            GROUP BY lrn, school_year
        )
        """
    )

    cursor.execute(
        """
        UPDATE student_records
        SET remarks = ''
        WHERE LOWER(TRIM(COALESCE(remarks, ''))) = 'nan'
        """
    )

    cursor.execute(
        """
        UPDATE student_records
        SET status = CASE
            WHEN UPPER(COALESCE(remarks, '')) LIKE '%PENDING TI%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%PENDING T/I%'
                THEN 'PENDING_TRANSFER_IN'
            WHEN UPPER(COALESCE(remarks, '')) LIKE '%T/O%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%T-O%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER OUT%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFERRED OUT%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER-OUT%'
                THEN 'TRANSFER_OUT'
            WHEN UPPER(COALESCE(remarks, '')) LIKE '%T/I%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%T-I%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER IN%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFERRED IN%'
                OR UPPER(COALESCE(remarks, '')) LIKE '%TRANSFER-IN%'
                THEN 'TRANSFER_IN'
            ELSE 'ENROLLED'
        END
        """
    )

    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0] or 0
    if user_count == 0:
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
            """,
            ("admin", generate_password_hash("admin123"), "admin"),
        )
