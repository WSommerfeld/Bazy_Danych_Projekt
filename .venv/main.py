import GUI
import dbbasic as db

DATA_BASE = "data_base13.db"
con=db.connect(DATA_BASE)

db.create_table_Models(con)




#GUI.start_gui()
