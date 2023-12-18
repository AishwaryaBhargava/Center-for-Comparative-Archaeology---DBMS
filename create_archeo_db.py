import mysql.connector

archeodb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "UPITTdb73",
    auth_plugin='mysql_native_password'
)

my_cursor = archeodb.cursor()

my_cursor.execute("CREATE DATABASE archeological_db")
my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)