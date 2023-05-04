from typing import Any, Dict, List, Tuple, Union, Optional, Callable, Type
import psycopg2
import psycopg2.extensions


from typing import Any, Dict, List, Tuple, Union, Optional
import psycopg2


class Database:
    """
    Summary: Database class for interacting with a PostgreSQL database.

    """

    def __init__(self, connection_string: str):
        self.connection_string: str = connection_string

    def execute(self, query: str) -> Union[List[Dict[str, Any]], None]:
        with psycopg2.connect(self.connection_string) as conn:
            print(query)
            with conn.cursor() as cur:
                cur.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    column_names = [desc[0] for desc in cur.description]
                    results = [dict(zip(column_names, row)) for row in cur.fetchall()]
                else:
                    conn.commit()
                    results = None
                return results

    def create_schema(self, schema_name: str) -> None:
        """
        Creates a schema in the database if it does not already exist.
        """
        self.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")

    def create_table(self, table) -> None:
        """
        Creates a table in the database if it does not already exist.
        """
        columns_sql = []
        for column in table.columns:
            column_sql = f"{column.name} {column.type}"
            if not column.nullable:
                column_sql += " NOT NULL"
            if column.foreign_key:
                column_sql += f" REFERENCES {table.schema_name}.{column.foreign_key.reference_table} ({column.foreign_key.reference_column}) ON DELETE {column.foreign_key.on_delete}"
            columns_sql.append(column_sql)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table.schema_name}.{table.name} ({', '.join(columns_sql)});"
        self.execute(create_table_sql)

    def drop_schema(self, schema_name: str) -> None:
        self.execute(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;")

    def drop_table(self, table_name: str, schema_name: str) -> None:
        self.execute(f"DROP TABLE IF EXISTS {schema_name}.{table_name};")

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


class Table:
    def __init__(self, name: str, schema_name: str, columns: List):
        self.name = name
        self.schema_name = schema_name
        self.columns = columns

    @classmethod
    def from_model(cls, model) -> 'Table':
        columns = []
        for col_def in model.columns:
            primary_key = None
            if "PRIMARY KEY" in col_def.type:
                primary_key = "PRIMARY KEY"
            column = Column(
                id=col_def.id,
                name=col_def.name,
                type=col_def.type.split(" ")[0],
                nullable=col_def.nullable,
                primary_key=primary_key
            )
            columns.append(column)
        return cls(name=model.table_name, schema_name=model.schema_name, columns=columns)


class Column:
    def __init__(self, id: int, name, type, nullable=False, validations=[], foreign_key=None, primary_key=None):
        self.id = id
        self.name = name
        self.type = type
        self.nullable = nullable
        # Ensure validations is set to an empty list by default
        self.validations = validations
        self.foreign_key = foreign_key
        self.primary_key = primary_key


class ForeignKey:
    def __init__(self, reference_table, reference_column, on_delete):
        self.reference_table = reference_table
        self.reference_column = reference_column
        self.on_delete = on_delete


class BaseModel:
    table_name = None
    schema_name = None
    db = None
    columns: List = []
    relations = {}

    def __init__(self, id: Optional[int] = None, **kwargs):
        self.id = id
        for column in self.columns:
            setattr(self, column.name, kwargs.get(column.name))

    @classmethod
    def set_database(cls, db):
        cls.db = db

    @classmethod
    def register_columns(cls, columns: List[Dict[str, Any]], id_column_name: str = "id"):
        cls.columns = []
        cls.columns.append(Column(
            id=id_column_name,
            name=id_column_name,
            type="SERIAL",
            nullable=False,
            primary_key="PRIMARY KEY"
        ))
        for column in columns:
            name = column["name"]
            data_type = column["type"]
            nullable = column.get("nullable", True)
            validations = column.get("validations", [])

            if not isinstance(validations, list):
                validations = []

            cls.columns.append(Column(
                id=None,
                name=name,
                type=data_type,
                nullable=nullable,
                validations=validations,
                foreign_key=column.get("foreign_key", None),
                primary_key=None
            ))

    def _insert_values(self) -> Tuple[str, List[Union[str, int]]]:
        columns: List = []
        values: List = []
        for column in self.columns:
            if column.primary_key:
                continue
            value = getattr(self, column.name)
            for validation in column.validations:
                validation(value)
            columns.append(column.name)
            values.append(value)
        return ", ".join(columns), values

    @classmethod
    def _build_where_clause(cls, query_params):
        where_clause = ""
        if query_params:
            where_clause = "WHERE "
            for key, value in query_params.items():
                where_clause += f"{key} = %({key})s AND "
            where_clause = where_clause[:-5]  # remove the trailing " AND "
        return where_clause

    @classmethod
    def associate(cls, include: List[Any], many_to_many: Optional[Dict[str, Type['BaseModel']]] = None):
        join_conditions = []
        include_tables = []
        for model in include:
            if model in cls.relations:
                relation = cls.relations[model]
                join_condition = f"{cls.schema_name}.{cls.table_name}.{relation['foreign_key']} = {model.schema_name}.{model.table_name}.{relation['reference_key']}"
                join_conditions.append(join_condition)
        if many_to_many:
            for key, model in many_to_many.items():
                assoc_table = cls.relations[model]['assoc_table']
                join_condition1 = f"{cls.schema_name}.{cls.table_name}.id = {assoc_table.schema_name}.{assoc_table.table_name}.{cls.relations[model]['foreign_key']}"
                join_condition2 = f"{model.schema_name}.{model.table_name}.id = {assoc_table.schema_name}.{assoc_table.table_name}.{cls.relations[model]['reference_key']}"
                join_conditions.extend([join_condition1, join_condition2])
                include_tables.append(assoc_table)
        return include_tables, join_conditions





    def insert(self) -> None:
        with self.db as cur:
            columns_str, values_list = self._insert_values()
            print(columns_str, values_list, "COLUMN VALUES")
            placeholders = ', '.join(['%s'] * len(values_list))
            query = f"""
                INSERT INTO {self.schema_name}.{self.table_name} ({columns_str})
                VALUES ({placeholders})
                RETURNING id;
            """
            print(query)
            cur.execute(query, tuple(values_list))
            self.id = cur.fetchone()[0]
            self.db.conn.commit()

    def update(self) -> None:
        with self.db as cur:
            update_columns = ", ".join(
                f"{column.name} = %s" for column in self.columns)
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
    def find_all(cls, include: Optional[List[Type['BaseModel']]] = None, many_to_many: Optional[Dict[str, Type['BaseModel']]] = None) -> List['BaseModel']:
        if include:
            include_tables, join_conditions = cls.associate(include, many_to_many)
        else:
            include_tables = []
            join_conditions = ""

        if include_tables and join_conditions:
            query = f"SELECT * FROM {cls.schema_name}.{cls.table_name}"
            for idx, table in enumerate(include_tables):
                query += f" JOIN {cls.schema_name}.{table.table_name} ON {join_conditions[idx]}"
        else:
            query = f"SELECT * FROM {cls.schema_name}.{cls.table_name}"

        results = cls.db.execute(query)
        return [cls(**result) for result in results]





    @classmethod
    def get_by_id(cls, _id: int):
        query = f"""
            SELECT * FROM {cls.schema_name}.{cls.table_name}
            WHERE id = {_id};
        """
        result_dict = cls.db.execute(query)
        if result_dict:
            return cls(**result_dict[0])
        else:
            raise ValueError(f"User with id '{_id}' not found")
