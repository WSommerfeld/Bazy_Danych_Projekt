
import dbbasic as db


con=db.connect("test1.db")
db.create_table_Robots(con)
db.execute(con,"lol lmao")