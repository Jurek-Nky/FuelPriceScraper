import sqlite3

db = sqlite3.connect("priceScraper.db")
cur = db.cursor()
cur.execute(
    '''CREATE TABLE gasstations(gs_id varchar PRIMARY KEY ,name varchar , brand varchar, street varchar, housenumber integer, postcode integer ,place varchar, lat number, lng number)''')
cur.execute(
    '''CREATE TABLE prices(p_id integer PRIMARY KEY autoincrement, gasstation varchar, e5 number, e10 number, diesel number, time_stamp timestam, FOREIGN KEY (gasstation) REFERENCES gasstations(gs_id))''')
db.commit()
db.close()
