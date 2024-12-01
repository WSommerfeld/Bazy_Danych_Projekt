import sqlite3

#połączenie z bazą
def connect(name):
    conn = sqlite3.connect(name)
    return conn

#wykonanie zapytania
def execute(conn, query):
    try:
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
    except sqlite3.OperationalError as e1:
        if "syntax error" in e1.args[0]:
            print("Błąd w zapytaniu")
        if "already exists" in e1.args[0]:
            print("Tabela już istnieje!")

def get_robot_types(conn):
    try:
        cur = conn.cursor()
        # zapytanie zeby dostac typy robotow
        cur.execute("SELECT DISTINCT type FROM Robots")
        types = cur.fetchall()
        if types:
            return [robot_type[0] for robot_type in types]  
        else:
            return []  
    except sqlite3.OperationalError as e:
        print("Error retrieving robot types:", e)
        return []  





#SQLite nie obsluguje float zamiastr tego jest REAL

def create_table_Robots(conn):
    execute(conn, "CREATE TABLE IF NOT EXISTS Robots (robot_id INTEGER, model VARCHAR(50), type VARCHAR(50), serial_number VARCHAR(50), warranty_number VARCHAR(50))")
    conn.commit()

def create_table_Functionalities(conn):
    execute(conn, "CREATE TABLE IF NOT EXISTS Functionalities (functionality_id INTEGER PRIMARY KEY, model VARCHAR(50), functionality VARCHAR(100))")
    conn.commit()

def create_table_Availability(conn):
    execute(conn, "CREATE TABLE IF NOT EXISTS Availability (availability_id INTEGER PRIMARY KEY, robot_id INTEGER, status VARCHAR(50), end_date DATE, price REAL)")
    conn.commit()

def create_table_Users(conn):
    execute(conn, "CREATE TABLE IF NOT EXISTS Users (user_login VARCHAR(50) PRIMARY KEY, email VARCHAR(100), first_name VARCHAR(50), last_name VARCHAR(50), password_hash VARCHAR(255))")
    conn.commit()

def create_table_Offers(conn):
    execute(conn, "CREATE TABLE IF NOT EXISTS Offers (offer_id INTEGER PRIMARY KEY, model VARCHAR(50), available_quantity INTEGER, type VARCHAR(50), rental_price REAL)")
    conn.commit()

def create_table_Reservations(conn):
    execute(conn, "CREATE TABLE IF NOT EXISTS Reservations (reservation_id INTEGER PRIMARY KEY, customer_first_name VARCHAR(50), customer_last_name VARCHAR(50), customer_login VARCHAR(50), payment_status VARCHAR(50), robot_id INTEGER, start_date DATE, end_date DATE, income REAL)")
    conn.commit()







