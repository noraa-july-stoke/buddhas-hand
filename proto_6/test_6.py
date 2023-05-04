import psycopg2
from buddhas_hand_6 import Database, Table, BaseModel, ForeignKey
from user import User
from role import Role
from user_role import UserRole



import psycopg2
from buddhas_hand_6 import Database, Table, BaseModel, ForeignKey
from user import User
from role import Role
from user_role import UserRole

def test_many_to_many():
    db = Database("postgresql://postgres:C4melz!!@localhost:5432/local_development")
    User.set_database(db)
    Role.set_database(db)
    UserRole.set_database(db)

    # Establish many-to-many relationship
    User.many_to_many(Role, UserRole, "user_id", "role_id")
    Role.many_to_many(User, UserRole, "role_id", "user_id")

    # Create schema and tables
    db.create_schema("buddhas_hand")
    db.create_table(Table.from_model(User))
    db.create_table(Table.from_model(Role))
    db.create_table(Table.from_model(UserRole))

    # Create users and roles
    user1 = User(username="JohnDoe", email="john@example.com")
    user2 = User(username="JaneDoe", email="jane@example.com")
    user1.insert()
    user2.insert()
    role1 = Role(name="Admin")
    role2 = Role(name="User")
    role1.insert()
    role2.insert()

    # Assign roles to users
    user_role1 = UserRole(user_id=user1.id, role_id=role1.id)
    user_role2 = UserRole(user_id=user1.id, role_id=role2.id)
    user_role3 = UserRole(user_id=user2.id, role_id=role2.id)
    user_role1.insert()
    user_role2.insert()
    user_role3.insert()

    # Retrieve users with roles
    users = User.find_all(many_to_many={"Role": Role})
    for user in users:
        print(user.username, user.email, user)
        roles = [role for role in user.roles]
        for role in roles:
            print("  -", role.name)

    # Clean up
    db.drop_table("buddhas_hand.user_roles")
    db.drop_table("buddhas_hand.users")
    db.drop_table("buddhas_hand.roles")
    db.drop_schema("buddhas_hand")

test_many_to_many()
