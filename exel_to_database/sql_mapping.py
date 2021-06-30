from abc import abstractmethod
from exel_to_database.sql_enums import TypeEnum as TE


class SQLMapClass:
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def get_extension():
        pass

    @staticmethod
    @abstractmethod
    def get_type(data_type: TE, char_count: int = None):
        pass


class SQLiteMapClass(SQLMapClass):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_extension():
        return '.db'

    @staticmethod
    def get_type(data_type: TE, char_count: int = None):
        if data_type == TE.varchar:
            return 'VARCHAR (%s)' % (char_count if 0 < char_count < 256 else 50)
        else:
            return data_type.value


class MySQLMapClass(SQLMapClass):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_extension():
        return '.db'

    @staticmethod
    def get_type(data_type: TE, char_count: int = None):
        if data_type == TE.varchar:
            return 'VARCHAR (%s)' % (char_count if 0 < char_count < 256 else 50)
        elif data_type == TE.real:
            return 'FLOAT'
        else:
            return data_type.value
