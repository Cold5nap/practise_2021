from enum import Enum


class TypeEnum(Enum):
    text = 'TEXT'
    int = 'INTEGER'
    real = 'REAL'
    varchar = 'VARCHAR'
    date = 'DATE'

    @staticmethod
    def all_types_list():
        return [TypeEnum.text, TypeEnum.int, TypeEnum.real, TypeEnum.varchar, TypeEnum.date]

    @staticmethod
    def get_by_str(type_str: str):
        if type_str == 'TEXT':
            return TypeEnum.text
        elif type_str == 'INTEGER':
            return TypeEnum.int
        elif type_str == 'REAL':
            return TypeEnum.real
        elif type_str == 'VARCHAR':
            return TypeEnum.varchar
        elif type_str == 'DATE':
            return TypeEnum.date
        else:
            return None


class ConstraintEnum(Enum):
    primary_key = 'PRIMARY KEY'
    unique = 'UNIQUE'
    not_null = 'NOT NULL'
    foreign_key = 'FOREIGN KEY'
    auto_inc = 'AUTOINCREMENT'

    @staticmethod
    def all_constraints_list():
        return [ConstraintEnum.primary_key, ConstraintEnum.unique, ConstraintEnum.not_null, ConstraintEnum.auto_inc]

    @staticmethod
    def get_by_str(con_str: str):
        if con_str == 'PRIMARY KEY':
            return ConstraintEnum.primary_key
        elif con_str == 'UNIQUE':
            return ConstraintEnum.unique
        elif con_str == 'NOT NULL':
            return ConstraintEnum.not_null
        elif con_str == 'FOREIGN KEY':
            return ConstraintEnum.foreign_key
        elif con_str == 'AUTOINCREMENT':
            return ConstraintEnum.auto_inc
        else:
            return None
