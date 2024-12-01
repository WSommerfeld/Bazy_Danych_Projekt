import random

import dbbasic as db
from dbbasic import insertRobots, execute, select

con=db.connect("DATA.db")



row = db.select(con,"*", "robots")

for i in range(69):

    typ= ["sprzątanie","malowanie","rozrywka","muzyka","ogrodnictwo"]

    x=random.randint(0,4)
    y=random.randint(0,420)

    db.insertRobots(con,"model"+str(i),typ[x],"S-"+str(i)+"-R-"+str(y)+"-T")

db.printresult(select(con,"*","robots"))
