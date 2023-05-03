# conn_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development?schema=buddhas_hand"
# db = Database(conn_string)

# import psycopg2
# from psycopg2.extras import RealDictCursor
# from prototypes.BH import User, Database

# def main():
#     # Connect to the database
#     connection_string = "host='localhost' dbname='local_development' user='postgres' password='C4melz!!'"
#     conn = psycopg2.connect(connection_string)
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     # Initialize the Database object
#     db = Database(connection_string)

#     # Create schema and table
#     schema_name = 'buddhas_hand'
#     table_name = 'users'
#     columns = [
#         "name VARCHAR(255) NOT NULL",
#         "email VARCHAR(255) UNIQUE NOT NULL"
#     ]
#     db.create_schema(schema_name)
#     db.create_table(table_name, schema_name, columns)

#     # Add a user named John Doe
#     user = User(name='John Doe', email='john.doe@example.com', id=None)
#     user.save(cur, conn)

#     # Find and print the user's info
#     users = User.find_all(cur, name="John Doe")
#     for user in users:
#         print(user.name)
#         print(user.email)

#     # Delete the user by name
#     User.delete_by(cur, conn, name="John Doe")

#     # Drop the table and schema
#     cur.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name} CASCADE;")
#     cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")

#     conn.commit()

#     # Recreate the table and schema
#     # db.create_schema(schema_name)
#     # db.create_table(table_name, schema_name, columns)

#     cur.close()
#     conn.close()

# if __name__ == '__main__':
#     main()



import psycopg2
from buddhas_hand import Database, Table, Column, User

# Define the database connection string
connection_string = "host='localhost' dbname='local_development' user='postgres' password='C4melz!!'"
# Create a new database object and connect to the database
db = Database(connection_string)

# Create a new schema called "buddhas_hand"
db.create_schema("buddhas_hand")

# Define the columns for the "users" table
columns = [
    # Column("id", "SERIAL"),
    Column("name", "VARCHAR(50)"),
    Column("email", "VARCHAR(50)")
]

# Create a new table called "users"
users_table = Table("users", "buddhas_hand", columns)
# db.drop_schema("buddhas_hand")
# db.drop_table("users", "buddhas_hand" )
db.create_table(users_table)

# Connect to the database and insert a new user
with psycopg2.connect(connection_string) as conn:
    with conn.cursor() as cur:
        # Create a new user
        user = User("John", "john@example.com")

        # Insert the user into the "users" table
        user.insert(cur, conn)

        # Retrieve the user from the database
        retrieved_user = User.get_by_id(cur, user.id)
        print(retrieved_user.__dict__)

        # Delete the user from the database
        retrieved_user.delete(cur, conn)

# # Drop the "users" table and the "buddhas_hand" schema
# db.drop_table("users", "buddhas_hand")
# db.drop_schema("buddhas_hand")
