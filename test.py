import pyodbc

# Connection parameters
server =  '192.168.121.79,1433'
database = 'SEIM'
username = 'SuperAdmin'
password = 'SuperAdmin'

# Construct the connection string
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

try:
    # Attempt to connect to the SQL Server
    connection = pyodbc.connect(connection_string)
    print("Connection successful!")
    connection.close()
except Exception as e:
    print("Error:", e)
