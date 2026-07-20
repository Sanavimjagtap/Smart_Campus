import sqlite3
import time

from SmartCampus_AI.attendance_recognition import start_attendance
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "smartcampus.db")

connection = sqlite3.connect(DATABASE)
running_session = None

while True:

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT SessionID, Room
        FROM Sessions
        WHERE EndTime=""
        ORDER BY SessionID DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row:

        session_id = row[0]
        room = row[1]

        if running_session != session_id:

            print(f"Starting Session {session_id} in {room}")

            running_session = session_id

            start_attendance(session_id, room)

            running_session = None

    time.sleep(1)