import sqlite3
import os
import shutil
import time
import threading


BACKUP_FOLDER = "backups"
MAX_BACKUPS = 5  # Maksymalna liczba backupów

#połączenie z bazą
def connect(name):
    conn = sqlite3.connect(name)
    return conn

#wykonanie zapytania
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


def indexmaker(conn):
    execute(conn, "CREATE UNIQUE INDEX robot_id1 ON Robots(id)")
    execute(conn, "CREATE  INDEX robot_id2 ON Availability(robot_id)")
    execute(conn, "CREATE INDEX robot_id3 ON Reservations(robot_id)")

def availabilityrefresher(conn):
    execute(conn, "UPDATE Availability "
                  "SET status = 'Available', end_date = DATE(CURRENT_DATE, '6 month') WHERE status = 'Unavailable' "
                  "AND end_date<CURRENT_DATE")
    execute(conn, "UPDATE Availability "
                  "SET status = 'Unavailable', end_date = DATE(CURRENT_DATE, '1 month') WHERE status = 'Available' "
                  "AND end_date<CURRENT_DATE")
#utworzenie bazy
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
#print tabela
def printresult(result):
    for result in result:
        print(result)



def create_table_Models(conn):
    execute(conn, "CREATE TABLE Models"
                  "(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                  "name VARCHAR(50) NOT NULL,"
                  "type VARCHAR(50) NOT NULL CHECK(type IN('Industrial', 'Household', 'Garden')))")

#robots create
def create_table_Robots(conn):
    execute(conn,"CREATE TABLE Robots"
                 " (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 " model_id INTEGER NOT NULL, "
                 " serial_number VARCHAR(50) UNIQUE NOT NULL,"
                 " warranty_number VARCHAR(50),"
                 " FOREIGN KEY (model_id) REFERENCES Models(id))")


#Availability create
def create_table_Availability(conn):
    execute(conn, "CREATE TABLE Availability(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                  " robot_id INTEGER NOT NULL, "
                  " status VARCHAR(50) NOT NULL CHECK (status IN ('Available', 'Unavailable', 'Reserved')),"
                  " end_date DATE, "
                  "price DECIMAL(10, 2) NOT NULL,"
                  " FOREIGN KEY (robot_id) REFERENCES Robots(id))")

#Functionalities create
def create_table_Functionalities(conn):
    execute(conn,"CREATE TABLE Functionalities "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "model_id INTEGER NOT NULL,"
                 " name VARCHAR(50) NOT NULL,"
                 "FOREIGN KEY (model_id) REFERENCES Models(id) )")


#Reservations
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

#Users
def create_table_Users(conn):
    execute(conn,"CREATE TABLE Users "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "login VARCHAR(50) UNIQUE NOT NULL,"
                 "email VARCHAR(100) NOT NULL,"
                 "first_name VARCHAR(50) NOT NULL,"
                 "last_name VARCHAR(50) NOT NULL,"
                 "password_hash VARCHAR(255) NOT NULL,"
                 "role VARCHAR(50) NOT NULL)")

#propozycja dodania tabeli klientów
#wtedy trzeba zmienić foreign key w rezerwacjach
def create_table_Customers(conn):
    execute(conn,"CREATE TABLE Customers "
                 "(id INTEGER PRIMARY KEY AUTOINCREMENT, "
                 "email VARCHAR(100) UNIQUE NOT NULL,"
                 "telephone VARCHAR(50) UNIQUE NOT NULL,"
                 "first_name VARCHAR(50) NOT NULL,"
                 "last_name VARCHAR(50) NOT NULL)")
#select
def select(conn, col, table):
    cur = conn.cursor()
    try:
        res = cur.execute("SELECT " + col + " FROM " + table)

    except sqlite3.OperationalError as e:
        if "no such column" in e.args[0]:
            print("Nie ma takiej kolumny")

    #zwraca tablice wszystkich rekordów
    try:
        return res.fetchall()
    except UnboundLocalError:
        return None

#select where
def selectWhere(conn, col, table, where):
    cur = conn.cursor()
    try:
        res = cur.execute("SELECT " + col + " FROM " + table+" WHERE " + where)

    except sqlite3.OperationalError as e:
        if "no such column" in e.args[0]:
            print("Nie ma takiej kolumny")

    #zwraca tablice wszystkich rekordów where where
    try:
        return res.fetchall()
    except UnboundLocalError:
        return None


#robots insert
def insertRobots(conn, model, type, warranty_number):
    execute(conn,"insert into robots values("+str(nextid(conn,"Robots")) +", '" +model + "', '" +type+ "', '"+ str(serialnumber(conn))+"', '"+warranty_number+"')")

#oblicznie id
def nextid(conn,table):
    #można to udprawnić o cofanie numerów ale nwm czy jest sens
    if(table == "Robots"):
        if(select(conn,"count(robot_id)",table)[0][0]>0):
            id = select(conn, "max(robot_id)", table)[0][0]+1
        else:
            id=0
    if(table == "Availability"):
        if (select(conn, "count(robot_id)",table)[0][0] != None):
            id = select(conn, "max(availability_id)", table)[0][0]+1
        else:
            id = 0
    return id

#symulacja nr seryjnego
def serialnumber(conn):
    #tymczasowo
    #wsm to można by to ręcznie wprowadzać ale do testowania aktualnie to
    #zbyt duży ból w dupie
    if select(conn, "count(robot_id)", "Robots")[0][0]>0:
        num = select(conn, "max(robot_id)", "Robots")[0][0] + 2137420+1
    else:
        num=2137420
    return num

#model
def RgetModel(conn, id):
    model = execute(conn,"select model from Robots where robot_id="+ str(id)).fetchone()[0]
    return model

# typ
def RgetType(conn, id):
    type = execute(conn,"select type from Robots where robot_id=" + str(id)).fetchone()[0]
    return type

# numer seryjny
def RgetSerial(conn, id):
    serial = execute(conn,"select serial_number from Robots where robot_id=" + str(id)).fetchone()[0]
    return serial

#numer gwarancji
def RgetWarranty(conn, id):
    warranty=execute(conn,"select warranty_number from Robots where robot_id=" + str(id)).fetchone()[0]
    return warranty

#ilosc robotów
def RgetQuantity(conn):
    q=select(conn, "count(robot_id)","Robots")
    return q[0][0]

#usun robota
def DeleteRobot(conn, id):
    execute(conn,"delete from Robots where robot_id=" + str(id))
#znajdz id robotów o col == value
def RgetWhere(conn, col,value,):
    if type(value) == str:
        result = execute(conn,"select robot_id from Robots where "+col+"="+"'"+value+"'")
    else:
        result = execute(conn,"select robot_id from Robots where "+col+"="+str(value))
    return result
#ilosc robotów o zadanym parametrze
def RgetQWhere(conn, col,value,):
    if type(value) == str:
        res = execute(conn,"select count(robot_id) from (select robot_id from Robots where "+col+"="+"'"+value+"')")
    else:
        res = execute(conn,"select count(robot_id) from (select robot_id from Robots where "+col+"="+str(value))

    return res.fetchone()[0]

#wyczyszczenie tabeli Robots
def ClearRobots(conn):
    for i in range(RgetQuantity(conn)):
        DeleteRobot(conn,i)


def insertAvailability(conn, robot_id, status, end_date, price):
    execute(conn, "insert into Availability values("+str(nextid(conn, "Availability"))+", "+str(robot_id)+", '"+status+"', "+end_date+ ", "+str(price)+") ")


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


def backup_scheduler(db_name):
    while True:
        create_backup(db_name)
        time.sleep(600)  # 10 minut w sekundach


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
