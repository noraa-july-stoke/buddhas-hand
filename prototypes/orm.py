import psycopg2
from psycopg2.extras import RealDictCursor

class BaseModel:
    table_name = None

    @classmethod
    def get_by_id(cls, id, cur):
        query = f"SELECT * FROM {cls.table_name} WHERE id = %s;"
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

    def insert(self, cur, conn):
        raise NotImplementedError("Subclasses must implement the 'insert' method.")

    def update(self, cur, conn):
        raise NotImplementedError("Subclasses must implement the 'update' method.")

    def delete(self, cur, conn):
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        cur.execute(query, (self.id,))
        conn.commit()


class User(BaseModel):
    table_name = 'users'

    def __init__(self, name, email, id=None):
        self.id = id
        self.name = name
        self.email = email

    def insert(self, cur, conn):
        query = '''
            INSERT INTO users (name, email)
            VALUES (%s, %s)
            RETURNING id;
        '''
        cur.execute(query, (self.name, self.email))
        result = cur.fetchone()
        self.id = result['id']
        conn.commit()

    def update(self, cur, conn):
        query = '''
            UPDATE users
            SET name = %s, email = %s
            WHERE id = %s;
        '''
        cur.execute(query, (self.name, self.email, self.id))
        conn.commit()

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="local_development",
    user="postgres",
    password="C4melz!!"
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# Alternate way to connect to the database
# Define connection string
# conn_string = "postgresql://postgres:C4melz!!@localhost:5432/local_development?schema=note_garden_sequelize"

# Connect to the database
# conn = psycopg2.connect(conn_string)



# Example usage
user = User(name='John Doe', email='john.doe@example.com')
user.save(cur, conn)
