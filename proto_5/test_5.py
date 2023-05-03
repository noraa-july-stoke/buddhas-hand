import psycopg2
from buddhas_hand_5 import Database, Table
from user_model import User

def is_not_email(value):
    if "@" in value:
        raise ValueError("Value must not be an email address")

def name_length_check(value):
    if len(value) < 3:
        raise ValueError("Name must be at least 3 characters long")

def is_string(value):
    if not isinstance(value, str):
        raise ValueError("Value must be a string")


def main():
    # Set up the database connection
    connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"
    db = Database(connection_string)
    User.set_database(db)

    # Create schema and register columns for the User model
    db.create_schema("buddhas_hand")


    User.register_columns([
        {
            "name": "name",
            "type": "TEXT",
            "validations": [is_not_email, name_length_check, is_string],
            "nullable": False,
        },
        {
            "name": "email",
            "type": "TEXT",
            "validations": [],
            "nullable": False,
        },
        {
            "name": "age",
            "type": "INTEGER",
            "validations": [],
            "nullable": False,
        },
    ])
    users_table = Table.from_model(User)
    db.create_table(users_table)


    # Create the users table


    user1 = User(name="John Doe", email="john@example.com", age=30)
    user2 = User(name="Jane Smith", email="jane@example.com", age=28)

    user1.insert()
    user2.insert()

    users = User.find_all()
    print("Inserted users:")
    for user in users:
        print(user.__dict__)

    user1.name = "John Updated"
    user1.age = 31
    user2.name = "Jane Updated"
    user2.age = 29

    user1.update()
    user2.update()

    users = User.find_all()
    print("Updated users:")
    for user in users:
        print(user.__dict__)

    user1.delete()
    user2.delete()

    db.drop_table(users_table.name, users_table.schema_name)
    db.drop_schema("buddhas_hand")

if __name__ == "__main__":
    main()
