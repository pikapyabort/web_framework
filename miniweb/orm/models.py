from .fields import Field, IntegerField, StringField, BooleanField, FloatField, ForeignKey
import sqlite3

class ModelMeta(type):
    def __new__(metacls, name, bases, attrs):
        if name == 'Model':
            cls = super().__new__(metacls, name, bases, attrs)
            return cls
        fields = {}
        for key, val in list(attrs.items()):
            if isinstance(val, Field):
                fields[key] = val

        has_pk = any(f.primary_key for f in fields.values())
        if not has_pk:
            id_field = IntegerField(primary_key=True)
            fields['id'] = id_field
            attrs['id'] = id_field
        table_name = None
        meta = attrs.get('Meta')
        if meta:
            table_name = getattr(meta, 'table_name', None)
        if table_name is None:
            table_name = name.lower()
        cls = super().__new__(metacls, name, bases, attrs)
        cls._fields = fields
        pk_field = None
        pk_name = None
        for fname, f in fields.items():
            if f.primary_key:
                pk_field = f
                pk_name = fname
                break
        cls._primary_key = pk_field
        cls._primary_key_name = pk_name
        cls._table_name = table_name
        Model._registry.append(cls)
        Model._models_by_name[name] = cls
        return cls

class Model(metaclass=ModelMeta):
    _connection = None 
    _registry = []
    _models_by_name = {}

    def __init__(self, **kwargs):
        for fname, field in self._fields.items():
            if fname in kwargs:
                setattr(self, fname, kwargs[fname])
            else:
                if field.default is not None:
                    setattr(self, fname, field.default)
                else:
                    setattr(self, fname, None)

    @classmethod
    def connect(cls, db_path):
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cls._connection = conn
        return conn

    @classmethod
    def create_table(cls):
        if cls is Model:
            return
        columns = []
        for fname, field in cls._fields.items():
            col_name = field.column_name
            col_type = getattr(field, 'sql_type', 'TEXT')
            col_def = f'"{col_name}" {col_type}'
            if field.primary_key:
                if col_type.upper() == "INTEGER":
                    col_def += " PRIMARY KEY AUTOINCREMENT"
                else:
                    col_def += " PRIMARY KEY"
            columns.append(col_def)
        cols_joined = ", ".join(columns)
        sql = f'CREATE TABLE IF NOT EXISTS "{cls._table_name}" ({cols_joined});'
        cur = cls._connection.cursor()
        cur.execute(sql)
        cls._connection.commit()

    @classmethod
    def create_all(cls):
        for model_cls in cls._registry:
            model_cls.create_table()

    def save(self):
        pk_name = self._primary_key_name
        pk_field = self._fields.get(pk_name)
        if pk_name is None:
            raise Exception("No primary key defined.")
        pk_val = getattr(self, pk_name)
        cur = self._connection.cursor()
        if pk_val is None:
            field_names = []
            placeholders = []
            values = []
            for fname, field in self._fields.items():
                if field.primary_key:
                    continue
                field_names.append(field.column_name)
                if isinstance(field, ForeignKey):
                    values.append(self.__dict__.get(field.column_name))
                else:
                    values.append(getattr(self, fname))
                placeholders.append("?")
            col_list = ", ".join(f'"{name}"' for name in field_names)
            ph_list = ", ".join(placeholders)
            sql = f'INSERT INTO "{self._table_name}" ({col_list}) VALUES ({ph_list})'
            cur.execute(sql, values)
            new_id = cur.lastrowid
            setattr(self, pk_name, new_id)
        else:
            set_clauses = []
            values = []
            for fname, field in self._fields.items():
                if field.primary_key:
                    continue
                set_clauses.append(f'"{field.column_name}" = ?')
                if isinstance(field, ForeignKey):
                    values.append(self.__dict__.get(field.column_name))
                else:
                    values.append(getattr(self, fname))
            values.append(pk_val)
            set_clause_str = ", ".join(set_clauses)
            sql = f'UPDATE "{self._table_name}" SET {set_clause_str} WHERE "{pk_field.column_name}" = ?'
            cur.execute(sql, values)
        self._connection.commit()
        return self

    @classmethod
    def get(cls, pk):
        pk_field = cls._primary_key
        if pk_field is None:
            raise Exception("No primary key defined.")
        sql = f'SELECT * FROM "{cls._table_name}" WHERE "{pk_field.column_name}" = ?'
        cur = cls._connection.cursor()
        cur.execute(sql, (pk,))
        row = cur.fetchone()
        if not row:
            return None
        obj = cls()
        for fname, field in cls._fields.items():
            col = field.column_name
            if col in row.keys():
                setattr(obj, fname, row[col])
        return obj

    @classmethod
    def all(cls):
        """Возвращает список объектов (всех записей таблицы) для данной модели."""
        sql = f'SELECT * FROM "{cls._table_name}"'
        cur = cls._connection.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        objects = []
        for row in rows:
            obj = cls()
            for fname, field in cls._fields.items():
                col = field.column_name
                if col in row.keys():
                    setattr(obj, fname, row[col])
            objects.append(obj)
        return objects
