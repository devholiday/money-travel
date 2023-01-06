import mysql.connector
import os

def connect():
    config = {
        'user': os.environ.get("DB_USER"),
        'password': os.environ.get("DB_PASSWORD"),
        'host': os.environ.get("DB_HOST"),
        'database': os.environ.get("DB_NAME"),
        'raise_on_warnings': True,
    }

    connection = mysql.connector.connect(**config)
    
    return connection

def insert_sql(query):
    try:
        connection = connect()

        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

        return cursor.lastrowid

    except mysql.connector.Error as error:
        print("Failed to insert record into Laptop table {}".format(error))

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

def fetchall_sql(query):
    try:
        connection = connect()

        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchall()
        return records
    except mysql.connector.Error as error:
        print("Error reading data from MySQL table", error)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

def fetchone_sql(query):
    try:
        connection = connect()

        cursor = connection.cursor()
        cursor.execute(query)
        records = cursor.fetchone()
        return records
    except mysql.connector.Error as error:
        print("Error reading data from MySQL table", error)
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")

def update_sql(query):
    try:
        connection = connect()

        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

        return cursor.lastrowid
    except mysql.connector.Error as error:
        print("Failed to update record to database: {}".format(error))
    finally:
        if connection.is_connected():
            connection.close()
            cursor.close()
            print("MySQL connection is closed")