import MySQLdb
from decouple import config

host = config('MYSQL_HOST', default='localhost')
port = config('MYSQL_PORT', cast=int, default=3306)
user = config('MYSQL_USER', default='root')
password = config('MYSQL_PASSWORD', default='')

print("Connecting to MySQL...")

try:
    connection = MySQLdb.connect(
        host=host,
        port=port,
        user=user,
        passwd=password
    )
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS catalog_db;")
    cursor.execute("CREATE DATABASE IF NOT EXISTS auth_db;")
    print("✅ Success! Databases 'catalog_db' and 'auth_db' created successfully!")
    connection.close()
except Exception as e:
    print(f"❌ Error creating databases: {e}")