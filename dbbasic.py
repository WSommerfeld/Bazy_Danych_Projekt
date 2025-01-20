import sqlite3
import os
import shutil
import time
import threading

'''
Moduł dbbasic zawiera podstawowe funkcje do operowania
bazą danych oraz funkcje związane z tworzeniem kopii
zapasowych i realizacją skryptu disaster recovery
'''


'''
Zmienne używane przy zarządzaniu
kopiami zapasowymi    
'''
BACKUP_FOLDER = "backups" #folder na backupy
MAX_BACKUPS = 5  # Maksymalna liczba backupów

'''
Połączenie z bazą danych
'''
def connect(name):
    conn = sqlite3.connect(name)
    return conn

'''
Wykonanie zapytania SQL przy 
zadanym połączeniu z bazą danych
'''
def execute(conn, query, params=None):
    """
    Wykonuje zapytanie SQL z opcjonalnymi parametrami i zatwierdza zmiany w bazie danych.
    """
    try:
        cur = conn.cursor()  # Tworzenie kursora do wykonania zapytania SQL
        if params:
            # Jeśli przekazano parametry, wykonaj zapytanie z użyciem placeholderów (?)
            result = cur.execute(query, params)
        else:
            # Jeśli nie ma parametrów, wykonaj zapytanie bez nich
            result = cur.execute(query)
        conn.commit()  # Zatwierdzenie zmian w bazie danych (np. INSERT, UPDATE, DELETE)
        return result  # Zwrócenie obiektu kursora (przydatne dla SELECT)
    except sqlite3.OperationalError as e1:
        # Obsługa błędów SQL, np. błędów składni lub brakujących tabel
        if "syntax error" in e1.args[0]:
            print("Błąd w zapytaniu SQL. Sprawdź składnię zapytania.")
        elif "already exists" in e1.args[0]:
            print("Tabela już istnieje w bazie danych.")
        else:
            print(f"Błąd operacyjny SQLite: {e1.args[0]}")
        return None  # Zwrócenie None w przypadku błędu

'''
Tworzenie kluczowych indeksów
'''
def indexmaker(conn):
    execute(conn, "CREATE UNIQUE INDEX robot_id1 ON Robots(id)")
    execute(conn, "CREATE  INDEX robot_id2 ON Availability(robot_id)")
    execute(conn, "CREATE INDEX robot_id3 ON Reservations(robot_id)")


'''
Utworzenie pustej bazy danych
i zwrócenie połączenia do niej
'''
def DataBaseInit(name):
    connection = connect(name)
    create_table_Models(connection)
    create_table_Robots(connection)
    create_table_Availability(connection)
    create_table_Functionalities(connection)
    create_table_Users(connection)
    create_table_Customers(connection)
    create_table_Reservations(connection)
    return connection

'''
Drukowanie tabeli zwróconych
przez execute
'''
def printresult(result):
    for result in result:
        print(result)


'''
Utworzenie tabeli Models
'''
def create_table_Models(conn):
    execute(conn, "CREATE TABLE Models"
                  "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                  "name VARCHAR(50) NOT NULL,"
                  "type VARCHAR(50) NOT NULL CHECK(type IN('Industrial', 'Household', 'Garden')))")

'''
Utworzenie tabeli Robots
'''
def create_table_Robots(conn):
    execute(conn,"CREATE TABLE Robots"
                 " (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 " model_id INTEGER NOT NULL, "
                 " serial_number VARCHAR(50) UNIQUE NOT NULL,"
                 " warranty_number VARCHAR(50),"
                 " FOREIGN KEY (model_id) REFERENCES Models(id))")


'''
Utworzenie tabeli Availability
'''
def create_table_Availability(conn):
    execute(conn, "CREATE TABLE Availability(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  " robot_id INTEGER NOT NULL, "
                  " status VARCHAR(50) NOT NULL CHECK (status IN ('Available', 'Unavailable', 'Reserved')),"
                  " end_date DATE, "
                  "price DECIMAL(10, 2) NOT NULL,"
                  " FOREIGN KEY (robot_id) REFERENCES Robots(id))")

'''
Utworzenie tabeli Functionalities
'''
def create_table_Functionalities(conn):
    execute(conn,"CREATE TABLE Functionalities "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "model_id INTEGER NOT NULL,"
                 " name VARCHAR(50) NOT NULL,"
                 "FOREIGN KEY (model_id) REFERENCES Models(id) )")


'''
Utworzenie tabeli Reservations
'''
def create_table_Reservations(conn):
    execute(conn,"CREATE TABLE Reservations "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 " customer_id INTEGER NOT NULL, "
                 " robot_id INTEGER NOT NULL,"
                 " payment_status VARCHAR(50) NOT NULL CHECK (payment_status IN ('Paid', 'Pending', 'Failed')),"
                 "start_date DATE NOT NULL,"
                 "end_date DATE NOT NULL,"
                 "FOREIGN KEY (customer_ID) REFERENCES Customers(id),"
                 "FOREIGN KEY (robot_id) REFERENCES Robots(id))")

'''
Utworzenie tabeli Users
'''
def create_table_Users(conn):
    execute(conn,"CREATE TABLE Users "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "login VARCHAR(50) UNIQUE NOT NULL,"
                 "email VARCHAR(100) NOT NULL,"
                 "first_name VARCHAR(50) NOT NULL,"
                 "last_name VARCHAR(50) NOT NULL,"
                 "password_hash VARCHAR(255) NOT NULL,"
                 "role VARCHAR(50) NOT NULL)")

'''
Utworzenie tabeli Customers
'''
def create_table_Customers(conn):
    execute(conn,"CREATE TABLE Customers "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "email VARCHAR(100) UNIQUE NOT NULL,"
                 "telephone VARCHAR(50) UNIQUE NOT NULL,"
                 "first_name VARCHAR(50) NOT NULL,"
                 "last_name VARCHAR(50) NOT NULL)")

'''
Zwrócenie typów robotów
'''
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

'''
Utworzenie kopii zapasowej bazy danych
'''
def create_backup(db_name):
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)

    # Tworzenie nowego backupu
    backup_file = os.path.join(BACKUP_FOLDER, f"{db_name}_backup_{int(time.time())}.db")
    shutil.copyfile(db_name, backup_file)
    print(f"Backup utworzony: {backup_file}")

    # Zarządzanie liczbą backupów
    backups = sorted(
        [os.path.join(BACKUP_FOLDER, f) for f in os.listdir(BACKUP_FOLDER) if f.startswith(db_name)],
        key=os.path.getctime
    )

    if len(backups) > MAX_BACKUPS:
        oldest_backup = backups[0]  # Najstarszy backup
        os.remove(oldest_backup)  # Usunięcie najstarszego backupu
        print(f"Usunięto najstarszy backup: {oldest_backup}")

'''
Zarządzanie tworzeniem kopii zapasowych
'''
def backup_scheduler(db_name):
    while True:
        create_backup(db_name)
        time.sleep(600)  # 10 minut w sekundach

'''
Odtworzenie bazy danych z kopii zapasowej
'''
def disaster_recovery(db_name):
    backups = [f for f in os.listdir(BACKUP_FOLDER) if f.startswith(db_name)]
    if not backups:
        print("Brak backupów do przywrócenia.")
        return

    backups.sort(reverse=True)  # Najnowszy backup
    latest_backup = os.path.join(BACKUP_FOLDER, backups[0])

    try:
        shutil.copyfile(latest_backup, db_name)
        print(f"Baza danych przywrócona z backupu: {latest_backup}")
    except Exception as e:
        print(f"Błąd podczas przywracania bazy danych: {e}")
