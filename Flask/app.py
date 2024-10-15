from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pyodbc
import subprocess
import os
import csv
import logging

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Connection parameters
server = '  192.168.100.172'
database = 'SEIM'
username = 'SuperAdmin'
password = 'SuperAdmin'

# Construct the connection string
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Login WHERE username = ? AND password = ?", (username, password))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if count > 0:
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('index'))
    except pyodbc.Error as e:
        flash(f'Error connecting to database: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/load_data')
def load_data():
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM SecurityEventLogs")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [{'MachineName': row.MachineName, 'Data': row.Data, 'EntryType': row.EntryType, 'Message': row.Message, 'Source': row.Source, 'ReplacementStrings': row.ReplacementStrings, 'TimeGenerated': row.TimeGenerated, 'TimeWritten': row.TimeWritten, 'UserName': row.UserName} for row in rows]

        return jsonify(data)
    except pyodbc.Error as e:
        return jsonify({'error': str(e)}), 500

def import_csv_to_db(file_path):
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                cursor.execute('''
                    INSERT INTO SecurityEventLogs (EventID, MachineName, Data, EntryType, Message, Source, ReplacementStrings, TimeGenerated, TimeWritten, UserName)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (row['EventID'], row['MachineName'], row['Data'], row['EntryType'], row['Message'], row['Source'], row['ReplacementStrings'], row['TimeGenerated'], row['TimeWritten'], row['UserName']))

        conn.commit()
        cursor.close()
        conn.close()
    except pyodbc.Error as e:
        print(f'Error importing CSV to database: {e}')

@app.route('/open_powershell', methods=['POST'])
def open_powershell():
    try:
        csv_path = 'E:\\SEIM\\log.csv'
        powershell_command = f'''
            Start-Process powershell -Verb RunAs -ArgumentList "-Command",
                "Get-EventLog -LogName Security -After 00:00:00 -Before 23:59:59 |",
                "Select-Object EventID, MachineName, Data, EntryType, Message, Source, ReplacementStrings, TimeGenerated, TimeWritten, UserName |",
                "Export-Csv -Path '{csv_path}' -NoTypeInformation;",
                "Get-EventLog -LogName System -After 00:00:00 -Before 23:59:59 |",
                "Select-Object EventID, MachineName, Data, EntryType, Message, Source, ReplacementStrings, TimeGenerated, TimeWritten, UserName |",
                "Export-Csv -Append -Path '{csv_path}' -NoTypeInformation;",
                "Get-EventLog -LogName Application -After 00:00:00 -Before 23:59:59 |",
                "Select-Object EventID, MachineName, Data, EntryType, Message, Source, ReplacementStrings, TimeGenerated, TimeWritten, UserName |",
                "Export-Csv -Append -Path '{csv_path}' -NoTypeInformation;"
        '''
        subprocess.run(["powershell.exe", "-Command", powershell_command], check=True)
        
        # Import the generated CSV file into the database
        import_csv_to_db(csv_path)
        
        return jsonify({'message': 'PowerShell command executed and data imported successfully'}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/refresh_data')
def refresh_data():
    logging.debug("refresh_data endpoint called")
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Fetch total logs
        cursor.execute("SELECT COUNT(*) AS TotalEntries FROM SecurityEventLogs;")
        total_logs_result = cursor.fetchone()
        total_logs = total_logs_result.TotalEntries if total_logs_result else 0

        # Fetch entry levels count
        cursor.execute("SELECT EntryType, COUNT(*) AS NumberOfEntries FROM SecurityEventLogs GROUP BY EntryType;")
        entry_levels_results = cursor.fetchall()
        entry_levels = {row.EntryType: row.NumberOfEntries for row in entry_levels_results}

        cursor.close()
        conn.close()
        
        return jsonify({'total_logs': total_logs, 'entry_levels': entry_levels}), 200

    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error'}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Unexpected error'}), 500

@app.route('/refresh_entry_levels')
def refresh_entry_levels():
    logging.debug("refresh_entry_levels endpoint called")
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Execute the query to get entry levels count
        cursor.execute("SELECT EntryType, COUNT(*) AS NumberOfEntries FROM SecurityEventLogs GROUP BY EntryType;")
        results = cursor.fetchall()

        # Format the results as a dictionary
        entry_levels = {row.EntryType: row.NumberOfEntries for row in results}

        cursor.close()
        conn.close()
        
        return jsonify(entry_levels), 200

    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error'}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Unexpected error'}), 500

@app.route('/refresh_logs_by_type')
def refresh_logs_by_type():
    logging.debug("refresh_logs_by_type endpoint called")
    query = """
    SELECT
        CASE
            WHEN Message LIKE '%logon%' OR Message LIKE '%logoff%' OR Message LIKE '%authentication%' 
              OR Message LIKE '%privilege use%' OR Message LIKE '%access%' OR Message LIKE '%audit%' 
              OR Message LIKE '%policy change%' THEN 'Security Log'
            WHEN Message LIKE '%boot%' OR Message LIKE '%shutdown%' OR Message LIKE '%driver%' 
              OR Message LIKE '%service start/stop%' OR Message LIKE '%hardware%' OR Message LIKE '%disk errors%' THEN 'System Log'
            ELSE 'Application Log'
        END AS LogType,
        COUNT(*) AS LogCount
    FROM
        SecurityEventLogs
    GROUP BY
        CASE
            WHEN Message LIKE '%logon%' OR Message LIKE '%logoff%' OR Message LIKE '%authentication%' 
              OR Message LIKE '%privilege use%' OR Message LIKE '%access%' OR Message LIKE '%audit%' 
              OR Message LIKE '%policy change%' THEN 'Security Log'
            WHEN Message LIKE '%boot%' OR Message LIKE '%shutdown%' OR Message LIKE '%driver%' 
              OR Message LIKE '%service start/stop%' OR Message LIKE '%hardware%' OR Message LIKE '%disk errors%' THEN 'System Log'
            ELSE 'Application Log'
        END;
    """
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        log_counts = {row.LogType: row.LogCount for row in results}
        
        return jsonify(log_counts), 200

    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error'}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Unexpected error'}), 500
@app.route('/refresh_chart_data')
def refresh_chart_data():
    logging.debug("refresh_chart_data endpoint called")
    query = """
    SELECT
        CASE
            WHEN Message LIKE '%logon%' OR Message LIKE '%logoff%' OR Message LIKE '%authentication%' 
              OR Message LIKE '%privilege use%' OR Message LIKE '%access%' OR Message LIKE '%audit%' 
              OR Message LIKE '%policy change%' THEN 'Security Log'
            WHEN Message LIKE '%boot%' OR Message LIKE '%shutdown%' OR Message LIKE '%driver%' 
              OR Message LIKE '%service start/stop%' OR Message LIKE '%hardware%' OR Message LIKE '%disk errors%' THEN 'System Log'
            ELSE 'Application Log'
        END AS LogType,
        COUNT(*) AS LogCount
    FROM
        SecurityEventLogs
    GROUP BY
        CASE
            WHEN Message LIKE '%logon%' OR Message LIKE '%logoff%' OR Message LIKE '%authentication%' 
              OR Message LIKE '%privilege use%' OR Message LIKE '%access%' OR Message LIKE '%audit%' 
              OR Message LIKE '%policy change%' THEN 'Security Log'
            WHEN Message LIKE '%boot%' OR Message LIKE '%shutdown%' OR Message LIKE '%driver%' 
              OR Message LIKE '%service start/stop%' OR Message LIKE '%hardware%' OR Message LIKE '%disk errors%' THEN 'System Log'
            ELSE 'Application Log'
        END;
    """
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        log_counts = {row.LogType: row.LogCount for row in results}
        
        return jsonify(log_counts), 200

    except pyodbc.Error as e:
        logging.error(f"Database error: {e}")
        return jsonify({'error': 'Database error'}), 500

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return jsonify({'error': 'Unexpected error'}), 500    

if __name__ == "__main__":
    app.run(debug=True)
