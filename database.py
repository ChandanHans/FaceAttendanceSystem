import mysql.connector

class Database:
    def __init__(self, host, user, passwd, database, wait_timeout=28800, interactive_timeout=28800):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.wait_timeout = wait_timeout
        self.interactive_timeout = interactive_timeout
        self.connect()

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host, user=self.user, passwd=self.passwd, database=self.database
        )
        self.execute_query("SET time_zone = '+05:30';")
        self.set_session_timeouts()

    def set_session_timeouts(self):
        """Set session-specific timeout values for the MySQL connection."""
        query = "SET SESSION wait_timeout = %s, SESSION interactive_timeout = %s"
        params = (self.wait_timeout, self.interactive_timeout)
        with self.conn.cursor() as cursor:
            cursor.execute(query, params)

    def fetch_data(self, query, params=()):
        """Fetch data from the database using a SELECT query."""
        try:
            if self.conn is None:
                self.connect()
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
            return result
        except Exception as e:
            print(e)
            return []

    def execute_query(self, query, params=()):
        """Execute a given SQL query (INSERT, UPDATE, DELETE) and return True if successful."""
        if self.conn is None:
            self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, params)
            self.conn.commit()
            return True  # Indicates that the query and commit were successful
        except Exception as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()  # Roll back the transaction on error
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()