from flask import Flask, render_template, redirect, url_for, flash
import subprocess

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

@app.route('/')
def index():
    return render_template('export_event_log.html')

@app.route('/export-event-log', methods=['POST'])
def export_event_log():
    try:
        # Define the PowerShell command
        powershell_command = '''
            Start-Process powershell.exe -WindowStyle Hidden -Verb runAs -ArgumentList "-Command",
                "Get-EventLog -LogName Security -After 00:00:00 -Before 23:59:59 |
                 Select-Object EventID, MachineName, Data, Category, CategoryNumber, EntryType, Message, Source, ReplacementStrings, InstanceId, TimeGenerated, TimeWritten, UserName |
                 Export-Csv -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation;
                 Get-EventLog -LogName System -After 00:00:00 -Before 23:59:59 |
                 Select-Object EventID, MachineName, Data, Category, CategoryNumber, EntryType, Message, Source, ReplacementStrings, InstanceId, TimeGenerated, TimeWritten, UserName |
                 Export-Csv -Append -Path 'E:\\SEIM\\system_event_log.csv' -NoTypeInformation;
                 Get-EventLog -LogName Application -After 00:00:00 -Before 23:59:59 |
                 Select-Object EventID, MachineName, Data, Category, CategoryNumber, EntryType, Message, Source, ReplacementStrings, InstanceId, TimeGenerated, TimeWritten, UserName |
                 Export-Csv -Append -Path 'E:\\SEIM\\application_event_log.csv' -NoTypeInformation;"
        '''
        
        # Run the PowerShell command
        result = subprocess.run(["powershell.exe", "-Command", powershell_command], check=True, capture_output=True, text=True)
        flash('Event logs exported successfully!', 'success')
    except subprocess.CalledProcessError as e:
        flash(f"An error occurred while exporting the event logs: {e.stderr}", 'danger')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
