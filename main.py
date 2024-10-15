from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import subprocess
from subprocess import Popen, CREATE_NO_WINDOW
import csv
import datetime
from collections import Counter
from Agent1 import Ui_MainWindow
import pyodbc
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class MainApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.show_page)
        self.ui.pushButton.clicked.connect(self.pushButtonClicked)
        self.ui.pushButton_2.clicked.connect(self.pushButton2Clicked)
        self.ui.pushButton_3.clicked.connect(self.load_csv_data)
        self.ui.pushButton_4.clicked.connect(self.update_logs_and_count)
        self.ui.pushButton_4.clicked.connect(self.update_pie_chart)
        self.ui.pushButton_5.clicked.connect(self.store_data_to_database)

        self.connection_string = 'DRIVER={SQL Server};SERVER=localhost\\SQLEXPRESS;DATABASE=SEIM;Trusted_Connection=yes;'
        self.connection = pyodbc.connect(self.connection_string)

    def show_page(self):
        self.ui.stackedWidget.setCurrentIndex(0)

    def pushButtonClicked(self):
        if self.ui.pushButton.isChecked():
            self.ui.pushButton_2.setChecked(False)
        else:
            self.ui.pushButton.setChecked(True)

    def pushButton2Clicked(self):
        if self.ui.pushButton_2.isChecked():
            self.ui.pushButton.setChecked(False)
        else:
            self.ui.pushButton_2.setChecked(True)
       
        self.run_powershell_command()

    def load_csv_data(self):
        file_path = "E:\\SEIM\\security_event_log.csv"
        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                model = QtGui.QStandardItemModel()
                for row in csv_reader:
                    items = [QtGui.QStandardItem(field) for field in row]
                    model.appendRow(items)
                self.ui.tableView.setModel(model)
                self.count_event_ids()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', str(e))

    def run_powershell_command(self):
        try:
            powershell_command = '''
            Start-Process powershell.exe -Verb runAs -ArgumentList "-Command",
                "Get-EventLog -LogName System -After 00:00:00 -Before 23:59:59 | Export-Csv -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation;
                Get-EventLog -LogName Security -After 00:00:00 -Before 23:59:59 | Export-Csv -Append -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation;
                Get-EventLog -LogName Application -After 00:00:00 -Before 23:59:59 | Export-Csv -Append -Path 'E:\\SEIM\\security_event_log.csv' -NoTypeInformation"
            '''
            p = Popen(["powershell.exe", "-Command", powershell_command], creationflags=CREATE_NO_WINDOW, stdout=subprocess.PIPE)
            output, _ = p.communicate()
            print(output.decode('utf-8'))
        except Exception as e:
            print("Error executing PowerShell command:", e)

    def update_logs_and_count(self):
        file_path = "E:\\SEIM\\security_event_log.csv"
        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                last_row = None
                for row in csv_reader:
                    last_row = row
                if last_row:
                    timestamp = last_row[11]
                    after_parameter = f'-After {timestamp}'
                    current_time = datetime.datetime.now()
                    before_parameter = f'-Before {current_time.strftime("%H:%M:%S")}'

                    powershell_command = f'Get-EventLog -LogName System {after_parameter} {before_parameter} | Export-Csv -Append -Path "E:\\SEIM\\security_event_log.csv" -NoTypeInformation'

                    p = Popen(["powershell.exe", "-Command", powershell_command], creationflags=CREATE_NO_WINDOW)
                    p.communicate()

                    self.load_csv_data()
                    self.count_event_ids()
                    self.display_top_entries()
                    self.display_entry_counts()

                    QtWidgets.QMessageBox.information(self, 'Logs updated successfully', 'Logs updated successfully. Click Show.')
                else:
                    QtWidgets.QMessageBox.warning(self, 'Error', 'CSV file is empty.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', str(e))

    def count_event_ids(self):
        model = self.ui.tableView.model()
        if model:
            event_id_column = 0
            source_column = 7
            event_ids = []
            for row in range(2, model.rowCount()):
                event_id = model.index(row, event_id_column).data()
                source = model.index(row, source_column).data().lower()
                if 'security id' in source:
                    event_ids.append('Security')
                elif 'application' in source:
                    event_ids.append('Application')
                else:
                    event_ids.append('System')

            counter = Counter(event_ids)
            self.event_id_counter = counter

            application_logs_count = counter['Application']
            security_logs_count = counter['Security']
            system_logs_count = counter['System']

            event_id_count = sum(counter.values())
            text = f'No of events: {event_id_count}\n'
            text += f'Application logs: {application_logs_count}\n'
            text += f'Security logs: {security_logs_count}\n'
            text += f'System logs: {system_logs_count}'
            self.ui.textEdit.setText(text)
            self.ui.textEdit.setFont(QtGui.QFont("Arial", 5))
        else:
            self.ui.textEdit.setText('No data available')

    def update_pie_chart(self):
        model = self.ui.listView_2.model()
        if model:
            counts = []
            labels = []
            for row in range(model.rowCount()):
                item = model.item(row)
                if item:
                    text = item.text()
                    entry, count = text.split(':')
                    labels.append(entry.strip())
                    counts.append(int(count.strip()))

            fig, ax = plt.subplots(figsize=(4, 4))
            ax.pie(counts, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')

            canvas = FigureCanvas(fig)
            canvas.draw()
            width, height = fig.get_size_inches() * fig.get_dpi()
            pixmap = QtGui.QPixmap(canvas.grab().toImage())
            self.ui.label_10.setPixmap(pixmap)

            self.create_pie_chart_from_text()
        else:
            self.ui.label_10.clear()

    def create_pie_chart_from_text(self):
        text = self.ui.textEdit.toPlainText()
        lines = text.split('\n')
        data = {}
        for line in lines:
            if line:
                key, value = line.split(':')
                data[key.strip()] = int(value.strip())
       
        if data:
            fig, ax = plt.subplots(figsize=(3, 3))
            ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
            ax.axis('equal')

            canvas = FigureCanvas(fig)
            canvas.draw()
            width, height = fig.get_size_inches() * fig.get_dpi()
            pixmap = QtGui.QPixmap(canvas.grab().toImage())
            self.ui.label_3.setPixmap(pixmap)
        else:
            self.ui.label_3.clear()

    def display_top_entries(self):
        model = self.ui.tableView.model()
        if model:
            event_id_column = 0
            event_ids = [model.index(row, event_id_column).data() for row in range(2, model.rowCount())]
            header = model.headerData(event_id_column, QtCore.Qt.Horizontal)
            event_ids = [event_id for event_id in event_ids if event_id != header]
            counter = Counter(event_ids)
            top_entries = counter.most_common(5)
            model_2 = QtGui.QStandardItemModel()
            for entry, count in top_entries:
                item = QtGui.QStandardItem(f'{entry}: {count}')
                model_2.appendRow(item)
            self.ui.listView.setModel(model_2)

    def display_entry_counts(self):
        model = self.ui.tableView.model()
        if model:
            column = 6
            entries = [model.index(row, column).data() for row in range(2, model.rowCount())]
            counter = Counter(entries)
            model_2 = QtGui.QStandardItemModel()
            for entry, count in counter.items():
                item = QtGui.QStandardItem(f'{entry}: {count}')
                model_2.appendRow(item)
            self.ui.listView_2.setModel(model_2)

    def store_data_to_database(self):
        try:
            cursor = self.connection.cursor()
            
            model = self.ui.tableView.model()
            if model:
                for row in range(2, model.rowCount()):
                    event_id = model.index(row, 0).data()
                    machine_name = model.index(row, 1).data()
                    data = model.index(row, 2).data()
                    category = model.index(row, 4).data()
                    entry_type = model.index(row, 6).data()
                    message = model.index(row, 7).data()
                    source = model.index(row, 8).data()
                    replacement_strings = model.index(row, 9).data()
                    instance_id = model.index(row, 10).data()
                    time_generated = model.index(row, 11).data()
                    time_written = model.index(row, 12).data()
                    user_name = model.index(row, 13).data()

                    sql_query = '''
                        INSERT INTO SecurityEventLog (EventID, MachineName, Data, Category, EntryType, Message, Source, ReplacementStrings, InstanceID, TimeGenerated, TimeWritten, UserName)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    '''
                    cursor.execute(sql_query, (event_id, machine_name, data, category, entry_type, message, source, replacement_strings, instance_id, time_generated, time_written, user_name))

            self.connection.commit()
            QtWidgets.QMessageBox.information(self, 'Success', 'Data stored successfully in the database.')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, 'Error', f'An error occurred: {str(e)}')
            self.connection.rollback()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())
