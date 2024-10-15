# SEIM Security Event Log Viewer
This project is a Security Information and Event Management (SEIM) tool built with PyQt5. It enables users to visualize, filter, and manage security event logs from the system, security, and application logs on a Windows machine. Logs can be loaded from a CSV file or pulled directly using PowerShell, then displayed in a table format, and stored in a database for further analysis.

Features
Load Security Event Logs:

The application loads security event logs from a CSV file (security_event_log.csv) and displays them in a table.
Event logs include System, Security, and Application logs, which can be pulled using PowerShell.
Filter Logs:

Filter logs based on specific events, event categories, and sources. The app supports categorization of logs (Application, Security, and System).
Event Log Analysis:

Event Count: The application counts the total number of events for Application, Security, and System logs and displays them in a text area.
Top 5 Events: It also shows the top 5 most frequent event entries.
Entry Type Count: Displays the count of entry types in a list view.
Pie Charts for Event Distribution:

The application provides pie charts based on event distributions and categories, using Matplotlib for visualization.
Update Logs and Perform Real-time Monitoring:

Automatically fetches and updates logs in real-time from the system with the latest logs, using Get-EventLog PowerShell commands.
Database Storage:

The app stores event log data into a SQL Server database, allowing for future analysis and archiving of events.
Requirements
To run the application, you'll need the following:

Python 3.x
PyQt5
pyodbc
Matplotlib
SQL Server (with a database named SEIM and a table named SecurityEventLog for log storage)
You can install the required Python packages using the following command:

bash
Copy code
pip install pyqt5 pyodbc matplotlib
Usage
Run the Application:

Run the script using Python to open the PyQt5 interface:
bash
Copy code
python main.py
Loading Event Logs:

Click on Load Logs to load the event logs from the CSV file into the table view.
Real-Time Log Fetching:

Click on Update Logs to fetch real-time logs from the system, security, and application logs using PowerShell commands.
Viewing Logs:

Use the table view to browse through logs. The top 5 most frequent events and event counts can be viewed in the side panels.
Storing Logs in SQL Database:

You can store the event log data in a SQL Server database by clicking on the Store Data button. Ensure that your SQL Server instance is configured, and the SEIM database exists.
PowerShell Commands
The application leverages PowerShell commands to fetch logs:

System Logs
Security Logs
Application Logs
The logs are saved in security_event_log.csv and appended with new logs when needed.

Database Configuration
Ensure you have a database setup as follows:

SQL Server
Table: SecurityEventLog
Sample SQL Table Structure:

sql
Copy code
CREATE TABLE SecurityEventLog (
    EventID INT,
    MachineName VARCHAR(255),
    Data VARCHAR(MAX),
    Category VARCHAR(255),
    EntryType VARCHAR(255),
    Message VARCHAR(MAX),
    Source VARCHAR(255),
    ReplacementStrings VARCHAR(MAX),
    InstanceID INT,
    TimeGenerated DATETIME,
    TimeWritten DATETIME,
    UserName VARCHAR(255)
);
