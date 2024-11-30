
import dbbasic as db
from dbbasic import insertRobots

con=db.connect("test1.db")
#db.create_table_Robots(con)
#db.create_table_Availability(con)
#db.execute(con,"lol lmao")
#db.execute(con, "insert into robots values(12345, 'model1', 'typ1', '54321', '12543')")


db.insertRobots(con, "model1","sprzatanie","32819")
db.insertAvailability(con,  2, "git", "2024-06-06", 231)



