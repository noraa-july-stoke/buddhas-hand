from typing import Any, Dict, List, Tuple, Union, Optional, Callable
import psycopg2
import psycopg2.extensions


from typing import Any, Dict, List, Tuple, Union, Optional
import psycopg2


class Database:
    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string

    def create_schema(self, schema_name: str) -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")
                conn.commit()

    def create_table(self, table: 'Table') -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                columns_str = ", ".join(f"{col.name} {col.data_type} {'NOT NULL' if not col.nullable else ''}".strip() for col in table.columns)
                columns_str = columns_str.rstrip(",").strip()
                query = f"""
                    CREATE TABLE IF NOT EXISTS {table.schema_name}.{table.name} (
                        id SERIAL PRIMARY KEY,
                        {columns_str}
                    );
                """
                print(query)
                cur.execute(query)
                conn.commit()


    def drop_schema(self, schema_name: str) -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")
                conn.commit()

    def drop_table(self, table_name: str, schema_name: str) -> None:
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name};")
                conn.commit()

    def __enter__(self):
        self.conn = psycopg2.connect(self.connection_string)
        self.cur = self.conn.cursor()
        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            if exc_type is not None:
                self.conn.rollback()
            self.conn.close()



class Column:
    def __init__(self, name: str, data_type: str, validations: List[Callable], nullable: bool):
        self.name = name
        self.data_type = data_type
        self.validations = validations
        self.nullable = nullable


class Table:
    def __init__(self, name: str, schema_name: str, columns: List[Column]):
        self.name = name
        self.schema_name = schema_name
        self.columns = columns

    @classmethod
    def from_model(cls, model):
        return cls(model.table_name, model.schema_name, model.columns)


class BaseModel:
    table_name = None
    schema_name = None
    db = None
    columns: List = []


    def __init__(self, id: Optional[int] = None, **kwargs):
        self.id = id
        for column in self.columns:
            setattr(self, column.name, kwargs.get(column.name))

    @classmethod
    def set_database(cls, db):
        cls.db = db

    @classmethod
    def register_columns(cls, columns: List[Dict[str, Any]]):
        for column in columns:
            name = column["name"]
            data_type = column["type"]
            nullable = column.get("nullable", True)
            validations = column.get("validations", [])

            cls.columns.append(Column(name, data_type, validations, nullable))
            print(cls.columns)


    def _insert_values(self) -> Tuple[str, List[Union[str, int]]]:
        columns: List = []
        values: List = []
        for column in self.columns:
            value = getattr(self, column.name)
            for validation in column.validations:
                validation(value)
            columns.append(column.name)
            values.append(value)
        return ", ".join(columns), values


    def _build_where_clause(cls, query_params):
        where_clause = ""
        if query_params:
            where_clause = "WHERE "
            for key, value in query_params.items():
                where_clause += f"{key} = %({key})s AND "
            where_clause = where_clause[:-5]  # remove the trailing " AND "
        return where_clause

    def insert(self) -> None:
        with self.db as cur:
            columns_str, values_list = self._insert_values()
            placeholders = ', '.join(['%s'] * len(values_list))
            query = f"""
                INSERT INTO {self.schema_name}.{self.table_name} ({columns_str})
                VALUES ({placeholders})
                RETURNING id;
            """
            cur.execute(query, tuple(values_list))
            self.id = cur.fetchone()[0]
            self.db.conn.commit()

    def update(self) -> None:
        with self.db as cur:
            update_columns = ", ".join(f"{column.name} = %s" for column in self.columns)
            values = []
            for column in self.columns:
                value = getattr(self, column.name)
                for validation in column.validations:
                    validation(value)
                values.append(value)
            query = f'''
                UPDATE {self.schema_name}.{self.table_name}
                SET {update_columns}
                WHERE id = %s;
            '''
            values = tuple(values) + (self.id,)
            cur.execute(query, values)
            self.db.conn.commit()

    def delete(self) -> None:
        with self.db as cur:
            query = f"DELETE FROM {self.schema_name}.{self.table_name} WHERE id = %(id)s;"
            cur.execute(query, {'id': self.id})

    @classmethod
    def find_all(cls):
        with cls.db as cur:
            cur.execute(f"SELECT * FROM {cls.schema_name}.{cls.table_name}")

            results = cur.fetchall()
            column_names = [column.name for column in cls.columns]

            return [cls(**dict(zip(column_names, row))) for row in results]


    @classmethod
    def get_by_id(cls, id):
        with cls.db as cur:
            query = f"SELECT * FROM {cls.schema_name}.{cls.table_name} WHERE id = %s;"
            cur.execute(query, (id,))
            result = cur.fetchone()
            if result:
                result_dict = {
                    'id': result[0],
                    'name': result[1],
                    'email': result[2]
                }
                return cls(**result_dict)
            return None
