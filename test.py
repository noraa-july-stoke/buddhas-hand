# import psycopg2
# from psycopg2.extras import RealDictCursor
# # from BH import Database, BaseModel


# def get_all_records(connection_string, schema_name, table_name):
#     conn = psycopg2.connect(connection_string)
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     query = f"SELECT * FROM {schema_name}.{table_name};"
#     cur.execute(query)
#     records = cur.fetchall()

#     cur.close()
#     conn.close()

#     return records

# connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"
# schema_name = "buddhas_hand"
# table_name = "users"

# records = get_all_records(connection_string, schema_name, table_name)
# print(records)


# import psycopg2
# from psycopg2.extras import RealDictCursor


# class BaseModel:
#     table_name = None
#     schema_name = None

#     @classmethod
#     def get_by_id(cls, id, cur):
#         query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE id = %s;"
#         cur.execute(query, (id,))
#         result = cur.fetchone()
#         if result:
#             return cls(**result)
#         return None

#     def save(self, cur, conn):
#         if self.id:
#             self.update(cur, conn)
#         else:
#             self.insert(cur, conn)

#     def insert(self, cur, conn):
#         raise NotImplementedError("Subclasses must implement the 'insert' method.")

#     def update(self, cur, conn):
#         raise NotImplementedError("Subclasses must implement the 'update' method.")

#     def delete(self, cur, conn):
#         query = f"DELETE FROM {self.schema_name}.{self.table_name} WHERE id = %s;"
#         cur.execute(query, (self.id,))
#         conn.commit()


# class User(BaseModel):
#     table_name = 'users'
#     schema_name = 'buddhas_hand'

#     def __init__(self, name, email, id=None):
#         self.id = id
#         self.name = name
#         self.email = email

#     def insert(self, cur, conn):
#         query = f'''
#             INSERT INTO {self.schema_name}.{self.table_name} (name, email)
#             VALUES (%s, %s)
#             RETURNING id;
#         '''
#         cur.execute(query, (self.name, self.email))
#         result = cur.fetchone()
#         self.id = result['id']
#         conn.commit()

#     def update(self, cur, conn):
#         query = f'''
#             UPDATE {self.schema_name}.{self.table_name}
#             SET name = %s, email = %s
#             WHERE id = %s;
#         '''
#         cur.execute(query, (self.name, self.email, self.id))
#         conn.commit()



# def create_table(conn, schema_name, table_name):
#     cur = conn.cursor()
#     cur.execute(f"""
#         CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
#             id SERIAL PRIMARY KEY,
#             name VARCHAR(255) NOT NULL,
#             email VARCHAR(255) UNIQUE NOT NULL
#         );
#     """)
#     conn.commit()
#     cur.close()

# def get_all_records(connection_string, schema_name, table_name):
#     conn = psycopg2.connect(connection_string)
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     query = f"SELECT * FROM {schema_name}.{table_name};"
#     cur.execute(query)
#     records = cur.fetchall()

#     cur.close()
#     conn.close()

#     return records

# # Example usage
# conn = psycopg2.connect(
#     host="localhost",
#     database="local_development",
#     user="postgres",
#     password="C4melz!!"
# )

# cur = conn.cursor(cursor_factory=RealDictCursor)
# connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"

# schema_name = "buddhas_hand"
# table_name = "users"

# create_table(conn, schema_name, table_name)

# user = User(name='John Doe', email='john.doe@exampleeeee.com')
# user.save(cur, conn)



# records = get_all_records(connection_string, schema_name, table_name)

# # Connect to the database

# print(records)
import psycopg2
from psycopg2.extras import RealDictCursor


class BaseModel:
    table_name = None
    schema_name = None

    def __init__(self, id=None):
        self.id = id

    def insert(self, cur, conn):
        raise NotImplementedError("Subclasses must implement the 'insert' method.")

    def update(self, cur, conn):
        raise NotImplementedError("Subclasses must implement the 'update' method.")

    def delete(self, cur, conn):
        query = f"DELETE FROM {self.schema_name}.{self.table_name} WHERE id = %s;"
        cur.execute(query, (self.id,))
        conn.commit()


class User(BaseModel):
    table_name = 'users'
    schema_name = 'buddhas_hand'

    def __init__(self, name, email, id=None):
        super().__init__(id=id)
        self.name = name
        self.email = email

    def insert(self, cur, conn):
        query = f'''
            INSERT INTO {self.schema_name}.{self.table_name} (name, email)
            VALUES (%s, %s)
            RETURNING id;
        '''
        cur.execute(query, (self.name, self.email))
        result = cur.fetchone()
        self.id = result['id']
        conn.commit()

    def update(self, cur, conn):
        query = f'''
            UPDATE {self.schema_name}.{self.table_name}
            SET name = %s, email = %s
            WHERE id = %s;
        '''
        cur.execute(query, (self.name, self.email, self.id))
        conn.commit

    @classmethod
    def find_all(cls, cur, **kwargs):
        # Build the WHERE clause dynamically based on the kwargs
        # and their corresponding column names
        where_clause = " AND ".join(f"{k} = %s" for k in kwargs.keys())
        values = tuple(kwargs.values())

        query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE {where_clause};"
        cur.execute(query, values)
        results = cur.fetchall()
        return [cls(**row) for row in results]

    @classmethod
    def get_by_id(cls, cur, id):
        query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE id = %s;"
        cur.execute(query, (id,))
        result = cur.fetchone()
        if result:
            return cls(**result)
        return None

    def save(self, cur, conn):
        if self.id:
            self.update(cur, conn)
        else:
            self.insert(cur, conn)




# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="local_development",
    user="postgres",
    password="C4melz!!"
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Example usage
user1 = User(name='John Doe', email='john.doe@example.com')
user1.save(cur, conn)

user2 = User(name='Jane Doe', email='jane.doe@example.com')
user2.save(cur, conn)

# Get user by ID
user = User.get_by_id(1, cur)
print(user.name)
print(user.email)

# Modify and save an existing user
user.name = 'Jonathan Doe'
user.save(cur, conn)
user = User.get_by_id(1, cur)
print(user.name)

# Find all users with the name "John Doe"
users = User.find_all(cur, name="John Doe")

for user in users:
    print(user.name)
    print(user.email)

# Close the cursor and connection
cur.close()
conn.close()
