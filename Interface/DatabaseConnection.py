import mysql.connector
from datetime import datetime

# teammate code: db connection
connection = None

def connect():
    global connection
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="database28",
            database="Attandance_Tracker"
        )
    except mysql.connector.Error as e:
        print("Database connection error:", e)


def get_connection():
    global connection
    if connection is None or not connection.is_connected():
        connect()
    return connection 


# saves check ins to db or memory list if offline
session_attendance_list = []

def record_attendance(student_id, student_name=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "student_id": student_id,
        "student_name": student_name if student_name else f"Student #{student_id}",
        "time": now,
        "status": "Present"
    }
    session_attendance_list.append(entry)

    # connect here twin
    conn = get_connection()
    if conn and conn.is_connected():
        try:
            cursor = conn.cursor()
            sql = "INSERT INTO Attandance (student_id, student_confirmation, professor_confirmation) VALUES (%s, TRUE, TRUE)"
            cursor.execute(sql, (student_id,))
            conn.commit()
        except Exception as err:
            print("db insert error:", err)

    return entry
