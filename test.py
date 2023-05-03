# conn_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development?schema=buddhas_hand"
# db = Database(conn_string)

import psycopg2
from psycopg2.extras import RealDictCursor
from BH import User, Database

def main():
    # Connect to the database
    connection_string = "host='localhost' dbname='local_development' user='postgres' password='C4melz!!'"
    conn = psycopg2.connect(connection_string)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Initialize the Database object
    db = Database(connection_string)

    # Create schema and table
    schema_name = 'buddhas_hand'
    table_name = 'users'
    columns = [
        "name VARCHAR(255) NOT NULL",
        "email VARCHAR(255) UNIQUE NOT NULL"
    ]
    db.create_schema(schema_name)
    db.create_table(table_name, schema_name, columns)

    # Add a user named John Doe
    user = User(name='John Doe', email='john.doe@example.com')
    user.save(cur, conn)

    # Find and print the user's info
    users = User.find_all(cur, name="John Doe")
    for user in users:
        print(user.name)
        print(user.email)

    # Delete the user by name
    User.delete_by(cur, conn, name="John Doe")

    # Drop the table and schema
    # cur.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name} CASCADE;")
    # cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")

    conn.commit()

    # Recreate the table and schema
    # db.create_schema(schema_name)
    # db.create_table(table_name, schema_name, columns)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
