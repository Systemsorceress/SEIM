from flask import Flask
import pyodbc

app = Flask(__name__)

# Connection parameters
server = '192.168.100.82'
database = 'SEIM'
username = 'SuperAdmin'
password = 'SuperAdmin'

# Construct the connection string
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def fetch_security_logs():
    try:
        # Connect to the SQL Server
        connection = pyodbc.connect(connection_string)

        # Fetch data from the SecurityEventLogs table
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM SecurityEventLog")
        logs = cursor.fetchall()

        # Close the connection
        connection.close()

        return logs
    except Exception as e:
        print("Error fetching logs:", e)
        return None

@app.route('/')
def index():
    # Fetch security logs
    logs = fetch_security_logs()
    if logs:
        # Convert logs to string format
        logs_str = '\n'.join([', '.join(map(str, log)) for log in logs])
        return f"<pre>{logs_str}</pre>"
    else:
        return "Error fetching logs from the database"

if __name__ == '__main__':
    app.run(debug=True)
