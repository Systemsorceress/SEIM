#SEIM Security Event Log Analyzer
This PyQt5-based GUI application helps analyze security event logs by fetching, updating, and visualizing system, security, and application logs. It also provides the ability to store data in an SQL Server database.

#Features
Fetch Event Logs: Fetch logs from System, Security, and Application event logs using PowerShell.
Load CSV Data: Load security event logs from a CSV file.
Real-Time Log Updates: Continuously update logs with the latest data.
Pie Chart Visualization: Display pie charts showing the proportions of different event types.
Top Log Entries: Display the most frequent event IDs.
Database Storage: Store log entries in an SQL Server database.
#Requirements
Python 3.7+
PyQt5: Used for creating the GUI.
Matplotlib: For pie chart visualization.
PyODBC: To connect with SQL Server.
Powershell: To fetch logs from the system.
#Installation
Clone this repository:
