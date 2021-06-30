from typing import List, Union

from exel_to_database.sql_enums import TypeEnum as TE, ConstraintEnum as CE


class SQLAttribute:
    def __init__(self, index: int, name: str):
        self.index = index
        self.name = name
        self.constraints = []
        self.fk_table = ''
        self.fk_atr = ''
        self.atr_type = TE.varchar
        self.char_count = 50

    def change_name(self, name: str):
        self.name = name.strip()

    def change_type(self, atr_type: Union[TE, str], char_count: int = 50):
        self.char_count = char_count

        if type(atr_type) is TE:
            self.atr_type = atr_type
        elif type(atr_type) is str:
            at = TE.get_by_str(atr_type)
            if at is not None:
                self.atr_type = at

    def change_constraint(self, constraint: Union[CE, str]):
        if type(constraint) is CE:
            if constraint in self.constraints:  # del
                self.constraints.remove(constraint)
            else:
                self.constraints.append(constraint)  # add

        cons = CE.get_by_str(constraint)
        if cons is not None:
            if cons in self.constraints:  # del
                self.constraints.remove(cons)
            else:
                self.constraints.append(cons)  # add

    def change_foreign_key(self, foreign_key_table: str, foreign_key_atr: str):
        if foreign_key_table is None:
            pass
        elif foreign_key_table.strip() == '':
            self.fk_table = ''
        else:
            self.fk_table = foreign_key_table

        if foreign_key_atr is None:
            pass
        elif foreign_key_atr.strip() == '':
            self.fk_atr = ''
        else:
            self.fk_atr = foreign_key_atr


class SQLTableDescriptor:
    def __init__(self, table_index, table_name, attributes: List[str]):
        super().__init__()
        self.index = table_index
        self.name = table_name

        self.attributes = {}
        for i, atr in enumerate(attributes):
            self.attributes[i] = SQLAttribute(i, atr)

    def __getitem__(self, item):
        if item in self.attributes.keys():
            return self.attributes[item]

    def change_atr_index(self, old_index: int, new_index: int):
        if old_index in self.attributes.keys() and new_index not in self.attributes.keys():
            self.attributes[new_index] = self.attributes.pop(old_index)
            self.attributes[new_index].index = new_index

    def change_atr_name(self, index: int, name: str):
        if index in self.attributes.keys():
            self.attributes[index].change_name(name)

    def change_atr_type(self, index: int, atr_type: str, varchar_num: int):
        if index in self.attributes.keys():
            self.attributes[index].change_type(atr_type, varchar_num)

    def change_atr_constraint(self, index: int, constraint: str):
        if index in self.attributes.keys():
            self.attributes[index].change_constraint(constraint)

    def change_atr_foreign_key(self, index: int, fk_table: str, fk_atr: str):
        if index in self.attributes.keys():
            self.attributes[index].change_foreign_key(fk_table, fk_atr)

    def delete_atr(self, index: int):
        if index in self.attributes.keys():
            self.attributes.pop(index, None)

    def generate_command(self, map_class) -> str:
        command = ''
        primary_key = ''
        fk_command = ''
        auto_inc = False
        for i in self.attributes.keys():
            atr = self.attributes[i]
            command += ",\n \'" + atr.name + "\'"  # add attribute
            command += ' ' + map_class.get_type(atr.atr_type, atr.char_count)  # with type

            for con in atr.constraints:  # and constraints
                if con == CE.auto_inc:
                    command += ' PRIMARY KEY AUTOINCREMENT'
                    auto_inc = True
                elif con == CE.primary_key and not auto_inc:
                    primary_key += "'" + atr.name + "',\n "  # create primary key
                elif con == CE.foreign_key:  # create foreign_key
                    if atr.fk_table != '' and atr.fk_atr != '':
                        fk_command = ',\n FOREIGN KEY ( %s ) REFERENCES %s(%s) ON DELETE CASCADE ON UPDATE NO ACTION' \
                                     % (atr.name, atr.fk_table, atr.fk_atr)
                else:
                    command += ' ' + con.value

        command = command[3:]
        if not primary_key == '' and not auto_inc:
            command += ', PRIMARY KEY ( %s )' % (primary_key[:-3])

        command += fk_command

        command = "CREATE TABLE '%s' \n (\n %s \n)" % (self.name, command)

        return command
