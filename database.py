import sqlite3

connection = sqlite3.connect("smartcampus.db")

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Sessions(
    SessionID INTEGER PRIMARY KEY AUTOINCREMENT,
    TeacherID TEXT,
    Class TEXT,
    Division TEXT,
    Date TEXT,
    StartTime TEXT,
    EndTime TEXT,
    Duration INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Teachers(
    TeacherID TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Password TEXT NOT NULL,
    Department TEXT NOT NULL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO Teachers
VALUES
("T001", "Mrs. Joshi", "abc123", "Physics"),
("T002", "Mr. Patil", "xyz789", "Chemistry"),
("T003", "Mrs. Kulkarni", "pass123", "Mathematics")
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Students(
    StudentID TEXT PRIMARY KEY,
    Name TEXT NOT NULL,
    Password TEXT NOT NULL,
    Class TEXT NOT NULL,
    Division TEXT NOT NULL,
    RollNo INTEGER NOT NULL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO Students
VALUES
    ("S001","Jude","queen","12","A",1),
    ("S002","Jacks","apple","12","A",2),
    ("S003","Cardan","King","12","A",3),
    ("S004","Aaron","ella","12","A",2),
    ("S005","Kaine","enid","11","B",1)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS TeacherAttendance(
    AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    TeacherID TEXT NOT NULL,
    Date TEXT NOT NULL,
    CheckIn TEXT,
    CheckOut TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Attendance(
    AttendanceID INTEGER PRIMARY KEY AUTOINCREMENT,
    SessionID INTEGER NOT NULL,
    StudentID TEXT NOT NULL,
    TimeMarked TEXT NOT NULL
)
""")

connection.commit()

connection.close()
