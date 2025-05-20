# from sqlalchemy import create_engine, text

# print("Starting database connection test...")  # Debugging log

# DATABASE_URI = 'mysql+mysqlconnector://root:252817@localhost:3306/Project_manager'

# try:
#     engine = create_engine(DATABASE_URI)
#     print("Engine created successfully!")  # Debugging log
#     connection = engine.connect()
#     print("✅ Database connection successful!")

#     # Test INSERT query
#     insert_query = text("""
#         INSERT INTO users (name, email, password, role)
#         VALUES ('Test User', 'testuser@example.com', 'hashed_password', 'student');
#     """)
#     connection.execute(insert_query)
#     connection.commit()
#     print("✅ Data inserted successfully!")

#     connection.close()
# except Exception as e:
#     print(f"❌ Error: {e}")


import mysql.connector
from mysql.connector import Error

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

execute_query("insert into users values(5, 'ruthwik', 'rk@gmail.com', 'somepassword', '', 'professor');", db_conn)
print(read_table("select * from users;", db_conn))

