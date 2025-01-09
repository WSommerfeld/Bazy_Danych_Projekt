import GUI
import dbbasic as db

DATA_BASE = "data_base.db"
con=db.connect(DATA_BASE)
db.create_table_Robots(con)
db.create_table_Availability(con)
db.create_table_Offers(con)
db.create_table_Functionalities(con)
db.create_table_Reservations(con)
db.create_table_Users(con)
db.execute(con,"PRINT DISTINCT type FROM Robots")
GUI.start_gui()
