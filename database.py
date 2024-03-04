import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

class MGPTDatabase:
    SERVER =  os.getenv('SERVER_URL')
    DB_NAME =  os.getenv('DB_NAME')
    USER =  os.getenv('DB_USER')
    PASSWORD =  os.getenv('DB_PASSWORD')

    def __init__(self):
        self.connection = None
        self.cursor = None

    def __enter__(self):
        try:
            self.connection = mysql.connector.connect(host=self.SERVER,
                                                      database=self.DB_NAME,
                                                      user=self.USER,
                                                      password=self.PASSWORD)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                return self  # Returns an instance of the class to be used with the with statement
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor is not None:
            self.cursor.close()
        if self.connection.is_connected():
            self.connection.close()
        if exc_val:
            raise

    def get_db_tables(self):
        try:
            self.cursor.execute("SHOW TABLES")
            print("List of tables in the database:")
            for table_name in self.cursor:
                print(table_name[0])
        except Error as e:
            print(f"Error fetching tables: '{e}'")

    def execute_query(self, query, params=None):
            
        try:
            if not query.strip().lower().startswith("select"):
                raise ValueError("Only SELECT queries are allowed in read-only mode.")

            self.cursor.execute(query, params) if params else self.cursor.execute(query)
            
            return self.cursor.fetchall() 
        except Error as e:
            print(f"Error executing query: '{e}'")
            return None
        except ValueError as e:
            print(e)
            return None
        
    def execute_from_file(self, alias):
        """
        Execute a SQL query from a file based on the alias.

        :param alias: Alias name for the SQL file (without .sql extension)
        :return: The result of the query execution.
        """
        file_path = f"./sql/{alias}.sql"
        if not os.path.exists(file_path):
            print(f"SQL file for alias '{alias}' does not exist.")
            return None

        with open(file_path, 'r') as file:
            query = file.read()

        # Assuming all queries are read-only SELECTs for this example
        # You might want to add logic here to handle other types of queries depending on your application's needs
        return self.execute_query(query)
