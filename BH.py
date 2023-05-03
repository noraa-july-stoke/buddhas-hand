import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Union, Optional


# class Database:
#     def __init__(self, connection_string: str):
#         self.connection_string = connection_string

#     def create_schema(self, schema_name: str) -> None:
#         conn = psycopg2.connect(self.connection_string)
#         cur = conn.cursor()
#         cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
#         conn.commit()
#         cur.close()
#         conn.close()

#     def create_table(self, table_name: str, schema_name, columns) -> None:
#         conn = psycopg2.connect(self.connection_string)
#         cur = conn.cursor()
#         columns_str = ", ".join(columns)
#         cur.execute(f"""
#             CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
#                 id SERIAL PRIMARY KEY,
#                 {columns_str}
#             );
#         """)
#         conn.commit()
#         cur.close()
#         conn.close()


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


# connection_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development"
# db = Database(connection_string)

# columns = ["name VARCHAR(255) NOT NULL", "email VARCHAR(255) UNIQUE NOT NULL"]
# db.create_schema('buddhas_hand')
# db.create_table('users', 'buddhas_hand', columns)

# conn = psycopg2.connect(connection_string)
# cur = conn.cursor(cursor_factory=RealDictCursor)

# user = User(name='John Doe', email='john.doe@examplee.com')
# user.save(cur, conn)

# cur.close()
# conn.close()


class Database:
    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string

    def create_schema(self, schema_name: str) -> None:
        conn: psycopg2.extensions.connection = psycopg2.connect(self.connection_string)
        cur: psycopg2.extensions.cursor = conn.cursor()
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
        conn.commit()
        cur.close()
        conn.close()

    def create_table(self, table_name: str, schema_name: str, columns: List[str]) -> None:
        conn: psycopg2.extensions.connection = psycopg2.connect(self.connection_string)
        cur: psycopg2.extensions.cursor = conn.cursor()
        columns_str = ", ".join(columns)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
                id SERIAL PRIMARY KEY,
                {columns_str}
            );
        """)
        conn.commit()
        cur.close()
        conn.close()

    def drop_schema(self, schema_name: str) -> None:
        conn: psycopg2.extensions.connection = psycopg2.connect(self.connection_string)
        cur: psycopg2.extensions.cursor = conn.cursor()
        cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
        conn.commit()
        cur.close()
        conn.close()

    def drop_table(self, table_name: str, schema_name: str) -> None:
        conn: psycopg2.extensions.connection = psycopg2.connect(self.connection_string)
        cur: psycopg2.extensions.cursor = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name};")
        conn.commit()
        cur.close()
        conn.close()


class BaseModel:
    table_name = None
    schema_name = None

    def __init__(self, id: Optional[int] = None):
        self.id = id


class User(BaseModel):
    table_name = 'users'
    schema_name = 'buddhas_hand'

    def __init__(self, name: str, email: str, id: Optional[int] = None):
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
        conn.commit()

    def delete(self, cur, conn):
        query = f"DELETE FROM {self.schema_name}.{self.table_name} WHERE id = %s;"
        cur.execute(query, (self.id))
        conn.commit()

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

    @classmethod
    def delete_by(cls, cur, conn, **kwargs):
        # Build the WHERE clause dynamically based on the kwargs
        # and their corresponding column names
        where_clause = " AND ".join(f"{k} = %s" for k in kwargs.keys())
        values = tuple(kwargs.values())

        query = f"DELETE FROM {cls.schema_name}.{cls.table_name} WHERE {where_clause};"
        cur.execute(query, values)
        conn.commit()

    def save(self, cur, conn):
        if self.id:
            self.update(cur, conn)
        else:
            self.insert(cur, conn)



# conn_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development?schema=buddhas_hand"
# db = Database(conn_string)
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
    cur.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name} CASCADE;")
    cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")

    conn.commit()

    # Recreate the table and schema
    # db.create_schema(schema_name)
    # db.create_table(table_name, schema_name, columns)

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
