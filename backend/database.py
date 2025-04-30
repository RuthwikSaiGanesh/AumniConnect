from flask_sqlalchemy import SQLAlchemy
from flask import current_app
import mysql.connector
from mysql.connector import Error

# Initialize SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """
    Initialize the database with the Flask app.
    """
    db.init_app(app)


def create_database_connection(host, user, password, db_name):
    """
    Create a connection to the MySQL database using mysql-connector.
    """
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            passwd=password,
            database=db_name
        )
        print("✅ Database connection successful...")
    except Error as e:
        print(f"❌ Error: {e}")
    return connection


# Initialize the raw database connection
db_conn = create_database_connection("localhost", "root", "252817", "Project_manager")


def read_table(query, connection=db_conn):
    """
    Execute a SELECT query and fetch results from the database.
    """
    if not connection:
        print("❌ No database connection.")
        return None

    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return [row for row in result]
    except Error as e:
        print(f"❌ Error: {e}")
        return None


def execute_query(query, connection=db_conn):
    """
    Execute an INSERT, UPDATE, DELETE, or other non-SELECT query.
    """
    if not connection:
        print("❌ No database connection.")
        return None

    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("✅ Query executed successfully...")
    except Error as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Test the database connection
    if db_conn:
        print("✅ Connected to the database!")

        # Test SELECT query
        select_query = "SHOW TABLES;"
        tables = read_table(select_query)
        if tables:
            print("📄 Tables in the database:")
            for table in tables:
                print(table)
        else:
            print("❌ No tables found or error occurred.")

        # Test INSERT query (if a `users` table exists)
        insert_query = """
        INSERT INTO users (name, email, password, role)
        VALUES ('Test User', 'testuser@example.com', 'hashed_password', 'student');
        """
        execute_query(insert_query)

        # Test DELETE query
        delete_query = "DELETE FROM users WHERE email = 'testuser@example.com';"
        execute_query(delete_query)
    else:
        print("❌ Failed to connect to the database.")