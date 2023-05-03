from typing import List, Optional
import psycopg2
from proto_2 import Database, Column, Table, BaseModel, User

# Assuming you've already defined the classes (Database, Column, Table, BaseModel, and User) here

def main():
    # conn string can also look like this: "dbname=mydatabase user=myuser password=mypassword host=localhost port=5432"
    connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"
    db = Database(connection_string)

    # Create schema "buddhas_hand"
    db.create_schema("buddhas_hand")

    # Create users table
    users_columns = [
        Column("name", "VARCHAR(100)"),
        Column("email", "VARCHAR(100)")
    ]

    users_table = Table("users", "buddhas_hand", users_columns)
    db.create_table(users_table)

    # Create user John Doe
    user = User("John Doe", "john.doe@example.com")
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            user.insert(cur, conn)

    # Retrieve and print John Doe
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            john_doe = User.get_by_id(cur, user.id)
            print("John Doe:", john_doe.name, john_doe.email)

    # Change name John Doe to Jane Doe
    user.name = "Jane Doe"
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            user.update(cur, conn)

    # Retrieve and print Jane Doe
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            jane_doe = User.get_by_id(cur, user.id)
            print("Jane Doe:", jane_doe.name, jane_doe.email)

    # Delete Jane Doe
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            user.delete(cur, conn)

    # Drop the table and schema
    db.drop_table("users", "buddhas_hand")
    db.drop_schema("buddhas_hand")

if __name__ == "__main__":
    main()
