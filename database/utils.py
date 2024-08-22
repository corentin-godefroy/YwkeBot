import os
from sqlite3 import Connection
from enum import IntEnum

class LogType(IntEnum):
    CREATE = 1
    MODIFY = 2
    DELETE = 3
    READ = 4


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def connect():
    conn = Connection(database=os.path.join(os.getcwd(), "var/ywke_database"))
    conn.row_factory = dict_factory
    return conn