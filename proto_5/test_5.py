import psycopg2
from buddhas_hand_5 import Database, Table
from user_model import User
from pet_model import Pet

def main():
    # Set up the database connection
    connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"
    db = Database(connection_string)
    db.create_schema("buddhas_hand")

    User.set_database(db)
    Pet.set_database(db)
    # Create schema

    # Create the users and pets tables
    users_table = Table.from_model(User)
    pets_table = Table.from_model(Pet)
    db.create_table(users_table)
    db.create_table(pets_table)

    # Create and insert users
    user1 = User(name="John Doe", email="john@example.com", age=30)
    user2 = User(name="Jane Smith", email="jane@example.com", age=28)
    user1.insert()
    user2.insert()

    # Create and insert pets
    pet1 = Pet(name="Buddy", species="Dog", owner_id=user1.id)
    pet2 = Pet(name="Mittens", species="Cat", owner_id=user2.id)
    pet1.insert()
    pet2.insert()

    pets = Pet.find_all(include=[User])
    print("Inserted pets:")
    for pet in pets:
        user = User.get_by_id(pet.owner_id)
        print(f"{pet.name} belongs to {user.name}")

    # Update pet details
    pet1.name = "Buddy Updated"
    pet2.name = "Mittens Updated"
    pet1.update()
    pet2.update()

    pets = Pet.find_all(include=[User])
    print("Updated pets:")
    for pet in pets:
        user = User.get_by_id(pet.owner_id)
        print(f"{pet.name} belongs to {user.name}")

    # Delete pets
    pet1.delete()
    pet2.delete()

    # Drop tables and schema
    db.drop_table(pets_table.name, pets_table.schema_name)
    db.drop_table(users_table.name, users_table.schema_name)
    db.drop_schema("buddhas_hand")


if __name__ == "__main__":
    main()
