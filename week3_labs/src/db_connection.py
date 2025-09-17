import mysql.connector
from mysql.connector import Error

def connect_db():
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = "",
        database = "fletapp"
    )
