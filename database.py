from mysql.connector import pooling

class Database:
    def __init__(self, host, user, passwd, database, pool_name="mypool", pool_size=3):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
        self.pool_name = pool_name
        self.pool_size = pool_size
        self.create_pool()

    def create_pool(self):
        self.pool = pooling.MySQLConnectionPool(
            pool_name=self.pool_name,
            pool_size=self.pool_size,
            pool_reset_session=True,
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            database=self.database
        )

    def fetch_data(self, query, params=()):
        conn = self.pool.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.close()
            return []

    def execute_query(self, query, params=()):
        conn = self.pool.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            conn.rollback()
        finally:
            conn.close()

    def close(self):
        """Close all connections in the pool."""
        self.pool.close()
