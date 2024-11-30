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




#robots create
def create_table_Robots(conn):
    execute(conn,"CREATE TABLE Robots"
                 " (robot_id INTEGER PRIMARY KEY,"
                 " model VARCHAR(50) NOT NULL, "
                 "type VARCHAR(50) NOT NULL,"
                 " serial_number VARCHAR(50) UNIQUE NOT NULL,"
                 " warranty_number VARCHAR(50) NOT NULL)")


#Availability create
def create_table_Availability(conn):
    execute(conn, "CREATE TABLE Availability(availability_id INTEGER PRIMARY KEY, "
                  "robot_id INTEGER,"
                  " status VARCHAR(50) NOT NULL,"
                  " end_date DATE, "
                  "price DECIMAL(10, 2),"
                  " FOREIGN KEY (robot_id) REFERENCES Robots(robot_id))")

#Functionalities create
#def create_table_Functionalities(conn):

#Offers
#def create_table_Offers(conn):

#Reservations
#def create_table_Reservations(conn):

#Users
#def create_table_Users(conn):



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


#robots insert
def insertRobots(conn, model, type, warranty_number):
    execute(conn,"insert into robots values("+str(nextid(conn,"Robots")) +", '" +model + "', '" +type+ "', '"+ str(serialnumber(conn))+"', '"+warranty_number+"')")

def nextid(conn,table):
    id = select(conn, "count(robot_id)", table)[0][0]+1
    return id

def serialnumber(conn):
    #tymczasowo
    #wsm to można by to ręcznie wprowadzać ale do testowania aktualnie to
    #zbyt duży ból w dupie
    if select(conn, "count(serial_number)", "Robots")==None:
        num=2137420
    else:
        num = select(conn, "count(serial_number)", "Robots")[0][0] + 2137420
    return num


def insertAvailability(conn, robot_id, status, end_date, price):
    execute(conn, "insert into Availability values("+str(nextid(conn, "Availability"))+", "+str(robot_id)+", '"+status+"', "+end_date+ ", "+str(price)+") ")
#def insertFunctionalities(conn, data):
#def insertOffers(conn, data):
#def insertReservations(conn, data):
#def insertOffers(conn, data):





