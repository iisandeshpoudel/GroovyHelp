from sqlalchemy import create_engine

# Connect to the database
engine = "mysql+pymysql://root:root@localhost:3306/groovydb"

# Test the connection
con = engine.connect()
