from sqlalchemy import create_engine, text

print("Starting database connection test...")  # Debugging log

DATABASE_URI = 'mysql+mysqlconnector://root:252817@localhost:3306/Project_manager'

try:
    engine = create_engine(DATABASE_URI)
    print("Engine created successfully!")  # Debugging log
    connection = engine.connect()
    print("✅ Database connection successful!")

    # Test INSERT query
    insert_query = text("""
        INSERT INTO users (name, email, password, role)
        VALUES ('Test User', 'testuser@example.com', 'hashed_password', 'student');
    """)
    connection.execute(insert_query)
    connection.commit()
    print("✅ Data inserted successfully!")

    connection.close()
except Exception as e:
    print(f"❌ Error: {e}")