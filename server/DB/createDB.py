import time
import mysql.connector
from mysql.connector import Error
import DBinfo

DB_IP = DBinfo.DB_IP
DB_USER = DBinfo.DB_USER
DB_PASSWD = DBinfo.DB_PASSWD
DB_NAME = DBinfo.DB_NAME
DROP_DP = True

try:
    connection = mysql.connector.connect(host=DB_IP, user=DB_USER, passwd=DB_PASSWD)
    try:
        cursor = connection.cursor()
        if DROP_DP:
            cursor.execute('DROP DATABASE IF EXISTS ' + DB_NAME)
        cursor.execute('CREATE DATABASE IF NOT EXISTS ' + DB_NAME)
        cursor.execute('USE ' + DB_NAME)

        f = open("createDB.sql", 'r')
        query = " ".join(f.readlines())
        cursor.execute(query)
    except Error as e:
        print('Error while creating DB: ' + str(e))
    finally:
        cursor.close()
        connection.close()

    time.sleep(5)
    connection = mysql.connector.connect(host=DB_IP, user=DB_USER, passwd=DB_PASSWD, db=DB_NAME)
    try:
        cursor = connection.cursor()
        cursor.execute('SHOW TABLES;')
        tables = cursor.fetchall()
        print("TABLES CREATED:")
        for t in tables:
            print(t)
    except Error as e:
        print('Error while querying DB: ' + str(e))
    finally:
        cursor.close()
        connection.close()

except Error as e:
    print('Error while connecting to DB: ' + str(e))
