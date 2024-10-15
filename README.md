# **SEIM Security Event Log Analyzer**

This **PyQt5-based GUI application** helps analyze security event logs by fetching, updating, and visualizing **system, security, and application logs**. It also provides the ability to store data in an **SQL Server database**.

## **Features**

- **Fetch Event Logs**: Fetch logs from **System**, **Security**, and **Application** event logs using PowerShell.
- **Load CSV Data**: Load security event logs from a **CSV file**.
- **Real-Time Log Updates**: Continuously update logs with the latest data.
- **Pie Chart Visualization**: Display pie charts showing the proportions of different event types.
- **Top Log Entries**: Display the most frequent event IDs.
- **Database Storage**: Store log entries in an **SQL Server database**.

## **Requirements**

- **Python 3.7+**
- **PyQt5**: Used for creating the GUI.
- **Matplotlib**: For pie chart visualization.
- **PyODBC**: To connect with SQL Server.
- **Powershell**: To fetch logs from the system.

## **Installation**

1. Clone this repository:

   ```bash
   git clone https://github.com/yourusername/seim-security-log-analyzer.git
   cd seim-security-log-analyzer
Install the required Python libraries:
 ```bash
pip install PyQt5 pyodbc matplotlib

Ensure that you have PowerShell installed and have the necessary permissions to execute PowerShell scripts.

Set up your SQL Server and update the connection string in the code with your credentials.
Usage
Run the Application:

Start the application by running:


Main Functionalities:

Fetch Logs: Press the "Fetch Logs" button to retrieve logs from your system.
Load CSV: Load a pre-existing security_event_log.csv file to view in the table.
Update Logs: Continuously update logs in real-time by clicking "Update Logs".
Store to Database: Store fetched logs into an SQL Server database.
Viewing Logs: The logs are displayed in a table, and top entries are displayed in a list view. You can view a pie chart visualizing the distribution of logs by their types (Security, Application, System).

CSV File Format
Logs are exported into a CSV file with the following columns:

EventID
MachineName
Data
Category
EntryType
Message
Source
ReplacementStrings
InstanceID
TimeGenerated
TimeWritten
UserName
Make sure your CSV file follows this format to be correctly processed by the application.

PowerShell Command Used
The application uses PowerShell to fetch event logs:

 ```bash
Start-Process powershell.exe -Verb runAs -ArgumentList "-Command", "Get-EventLog -LogName System -After 00:00:00 -Before 23:59:59 | Export-Csv -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation; Get-EventLog -LogName Security -After 00:00:00 -Before 23:59:59 | Export-Csv -Append -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation; Get-EventLog -LogName Application -After 00:00:00 -Before 23:59:59 | Export-Csv -Append -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation"

Database Storage
Logs are inserted into an SQL Server database with the following schema:


CREATE TABLE SecurityEventLog (
    EventID INT,
    MachineName NVARCHAR(255),
    Data NVARCHAR(MAX),
    Category NVARCHAR(255),
    EntryType NVARCHAR(50),
    Message NVARCHAR(MAX),
    Source NVARCHAR(255),
    ReplacementStrings NVARCHAR(MAX),
    InstanceID INT,
    TimeGenerated DATETIME,
    TimeWritten DATETIME,
    UserName NVARCHAR(255)
);
Update the self.connection_string in the application to connect to your database:


self.connection_string = 'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=SEIM;Trusted_Connection=yes;'
