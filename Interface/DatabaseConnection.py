import mysql.connector

connection= None

def connect():
    global connection
    try:
        connection = mysql.connector.connect(
            host= "localhost",
            user="root",
            password="database28",
            database="emr_data"
    )
    except mysql.connector.Error as e:
        print("Database connection error:", e)


def get_connection():
    global connection
    if connection is None or not connection.is_connected():
        connect()
    return connection 
