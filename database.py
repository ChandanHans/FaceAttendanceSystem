import sys
import mysql.connector
from mysql.connector import Error
import logging
from utility import get_config

config = get_config()

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("output.log", mode="w"),  # Log to this file
        logging.StreamHandler()  # Log to console (optional, remove if not needed)
    ]
)
class PrintLogger:
    """Logger that captures print statements and redirects them to logging."""
    def write(self, message):
        # Only log if there is a message (not just a new line)
        if message.rstrip() != "":
            logging.info(message.rstrip())
    
    def flush(self):
        # This flush method is required for file-like object
        pass

# Redirect standard output to PrintLogger
sys.stdout = PrintLogger()


class Database:
    def __init__(
        self,
        host=config["HOST"],
        user=config["USER"],
        passwd=config["PASSWD"],
        database=config["DB"],
        wait_timeout=28800,
        interactive_timeout=28800,
    ):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.wait_timeout = wait_timeout
        self.interactive_timeout = interactive_timeout
        self.conn = None
        self.connect()

    def connect(self):
        try:
            if not self.conn or not self.conn.is_connected():
                self.conn = mysql.connector.connect(
                    host=self.host, user=self.user, passwd=self.passwd, database=self.database
                )
                logging.info("Database connection established.")
                self.execute_query("SET time_zone = '+05:30';")
                self.set_session_timeouts()
        except Exception as e:
            print(e)


    def set_session_timeouts(self):
        """Set session-specific timeout values for the MySQL connection."""
        query = "SET SESSION wait_timeout = %s, SESSION interactive_timeout = %s"
        params = (self.wait_timeout, self.interactive_timeout)
        self.execute_query(query, params)

    def fetch_data(self, query, params=()):
        """Fetch data from the database using a SELECT query."""
        if self.conn and self.conn.is_connected():
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params)
                    result = cursor.fetchall()
                return result
            except Exception as e:
                print(e)
                return []
        self.connect()

    def execute_query(self, query, params=()):
        """Execute a given SQL query (INSERT, UPDATE, DELETE) and return True if successful."""
        if self.conn and self.conn.is_connected():
            try:
                with self.conn.cursor() as cursor:
                    cursor.execute(query, params)
                self.conn.commit()
                return True
            except Exception as e:
                print(e)
                if self.conn and self.conn.is_connected():
                    self.conn.rollback()
                return False
        self.connect()
        
    def close(self):
        """Close the database connection."""
        if self.conn and self.conn.is_connected():
            self.conn.close()
            logging.info("Database connection closed.")
