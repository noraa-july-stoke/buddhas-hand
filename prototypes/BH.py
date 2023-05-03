import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Union, Optional

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

    def __init__(self, schema_name: str, table_name: str, id: Optional[int] = None):
        self.schema_name = schema_name
        self.table_name = table_name
        self.id = id

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
        cur.execute(query, (self.id,))
        conn.commit()

    @classmethod
    def find_all(cls, cur, **kwargs):
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



class User(BaseModel):

    def __init__(self, name: str, email: str, id: Optional[int] = None):
        super().__init__(id=id)
        self.name = name
        self.email = email
