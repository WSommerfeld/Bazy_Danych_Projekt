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





def create_table_Robots(conn):
    execute(conn,"CREATE TABLE Robots(robot_id INTEGER, model VARCHAR(50), type VARCHAR(50), serial_number VARCHAR(50), warranty_number VARCHAR(50))")
    conn.commit()





