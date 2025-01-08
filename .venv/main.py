
import dbbasic as db
import GUI
from dbbasic import insertRobots, execute, select

con=db.connect("DATA.db")
GUI.start_gui()
#db.create_table_Robots(con)
#db.create_table_Availability(con)
#db.execute(con,"lol lmao")
#db.execute(con, "insert into robots values(12345, 'model1', 'typ1', '54321', '12543')")




