# Define SQL Server connection parameters
$server_name = 'DESKTOP-LUGE14R\SQLEXPRESS'
$database_name = 'SEIM'
$connectionString = "Server=$server_name;Database=$database_name;Integrated Security=True;"

# Retrieve event log data
$events = Get-EventLog -LogName System -After (Get-Date).Date -Before (Get-Date).AddDays(1) 

# Import the SQL Server module
Import-Module SqlServer

# Establish connection to SQL Server
$connection = New-Object System.Data.SqlClient.SqlConnection($connectionString)
$connection.Open()

# Create a SQL command to insert data into the database
$cmd = $connection.CreateCommand()

# Extract properties from the first event to dynamically create table columns
$properties = $events[0].PSObject.Properties | ForEach-Object { "$($_.Name) NVARCHAR(MAX)" }
$columns = [string]::Join(',', $properties)

# Create a table to store the event log data
$tableCreationQuery = "CREATE TABLE SecurityEventLog ($columns)"
$createTableCmd = $connection.CreateCommand()
$createTableCmd.CommandText = $tableCreationQuery
$createTableCmd.ExecuteNonQuery()

foreach ($event in $events) {
    # Extract property values from the event
    $values = $event.PSObject.Properties | ForEach-Object { "'$($_.Value)'" }
    $columnValues = [string]::Join(',', $values)
    
    # Define the SQL query to insert data into the table
    $insertQuery = "INSERT INTO SecurityEventLog VALUES ($columnValues)"
    
    # Execute the SQL query
    $cmd.CommandText = $insertQuery
    $cmd.ExecuteNonQuery()
}

# Close connection
$connection.Close()
