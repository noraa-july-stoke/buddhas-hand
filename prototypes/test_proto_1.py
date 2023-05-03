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

# Drop the "users" table and the "buddhas_hand" schema
db.drop_table("users", "buddhas_hand")
db.drop_schema("buddhas_hand")
