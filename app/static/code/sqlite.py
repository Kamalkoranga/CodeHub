import sqlite3

# Connect to a database
conn = sqlite3.connect('customer.db')
# conn = sqlite3.connect(':memory:') ===> temporary database in memory

# Create a cursor
c = conn.cursor()

# Create a table
c.execute('''CREATE TABLE data (
    ))''')

# DATATYPES - NULL, INTEGER, REAL, TEXT, BLOB(MEDIA)


# commit our command
conn.commit()

# clsoe connection
conn.close()