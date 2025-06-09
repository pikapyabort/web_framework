class Field:
    def __init__(self, primary_key=False, default=None):
        self.primary_key = primary_key
        self.default = default
        self.name = None
        self.column_name = None
        self.model_class = None

    def __set_name__(self, owner, name):
        self.name = name
        if self.column_name is None:
            self.column_name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.column_name, self.default)

    def __set__(self, instance, value):
        instance.__dict__[self.column_name] = value

class IntegerField(Field):
    def __init__(self, primary_key=False, default=None):
        super().__init__(primary_key=primary_key, default=default)
        self.sql_type = "INTEGER"

class StringField(Field):
    def __init__(self, default=None):
        super().__init__(primary_key=False, default=default)
        self.sql_type = "TEXT"

class BooleanField(Field):
    def __init__(self, default=None):
        super().__init__(primary_key=False, default=default)
        self.sql_type = "INTEGER"

class FloatField(Field):
    def __init__(self, default=None):
        super().__init__(primary_key=False, default=default)
        self.sql_type = "REAL"

class ForeignKey(Field):
    def __init__(self, related_model, default=None):
        super().__init__(primary_key=False, default=default)
        if isinstance(related_model, str):
            self._related_model_name = related_model
            self._related_model = None
        else:
            self._related_model_name = related_model.__name__
            self._related_model = related_model
        self.sql_type = "INTEGER"

    def __set_name__(self, owner, name):
        self.name = name
        if self.column_name is None:
            self.column_name = name + "_id"
        self.model_class = owner

    @property
    def related_model(self):
        if self._related_model is None:
            from .models import Model
            if hasattr(Model, "_models_by_name"):
                self._related_model = Model._models_by_name.get(self._related_model_name)
        return self._related_model

    def __get__(self, instance, owner):
        if instance is None:
            return self
        related_id = instance.__dict__.get(self.column_name, self.default)
        if related_id is None:
            return None
        model_cls = self.related_model
        if model_cls is None:
            return related_id
        return model_cls.get(related_id)

    def __set__(self, instance, value):
        col = self.column_name
        if value is None:
            instance.__dict__[col] = None
        else:
            from .models import Model
            if isinstance(value, Model):
                instance.__dict__[col] = getattr(value, "id", None)
            else:
                instance.__dict__[col] = value
