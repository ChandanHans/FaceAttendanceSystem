import mysql.connector

class Database:
    def __init__(self, host, user, passwd, database):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.connect()

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host, user=self.user, passwd=self.passwd, database=self.database
        )
        self.cursor = self.conn.cursor()

    def fetch_data(self, query, params=()):
        """Fetch data from the database using a SELECT query."""
        if self.conn is None:
            self.connect()
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def execute_query(self, query, params=()):
        """Execute a given SQL query (INSERT, UPDATE, DELETE) and return True if successful."""
        if self.conn is None:
            self.connect()
        try:
            self.cursor.execute(query, params)
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