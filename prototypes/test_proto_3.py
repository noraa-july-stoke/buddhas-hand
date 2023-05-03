import psycopg2
from proto_3 import Database, Table, User


def main():
    # Set up the database connection
    connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"
    db = Database(connection_string)
    db = Database(connection_string)

    # Create schema and register columns for the User model
    db.create_schema("buddhas_hand")
    User.register_columns(name='TEXT', email='TEXT', age='INTEGER')

    # Create the users table
    users_table = Table.from_model(User)
    db.create_table(users_table)

    user1 = User(name="John Doe", email="john@example.com", age=30)
    user2 = User(name="Jane Smith", email="jane@example.com", age=28)

    with db as cur:
        user1.insert(cur, db.conn)
        user2.insert(cur, db.conn)

    with db as cur:
        users = User.find_all(cur)
        print("Inserted users:")
        for user in users:
            print(user.__dict__)

    user1.name = "John Updated"
    user1.age = 31
    user2.name = "Jane Updated"
    user2.age = 29

    with db as cur:
        user1.update(cur, db.conn)
        user2.update(cur, db.conn)

    with db as cur:
        users = User.find_all(cur)
        print("Updated users:")
        for user in users:
            print(user.__dict__)

    with db as cur:
        user1.delete(cur, db.conn)
        user2.delete(cur, db.conn)

    db.drop_table(users_table.name, users_table.schema_name)
    db.drop_schema("buddhas_hand")


if __name__ == "__main__":
    main()
