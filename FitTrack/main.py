import sqlite3
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QApplication, QDateEdit, QHBoxLayout, QLineEdit, QWidget, QLabel, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from sys import argv, exit

class FitTrack(QWidget):
    def __init__(self):
        super().__init__()
        self.Setting()
        self.initDB()  # Initialize the database first
        self.initUI()
        self.button_click()

    def Setting(self):
        self.setWindowTitle("FitTrack")
        self.setGeometry(100, 100, 800, 600)
        self.dark_mode = False

    def initUI(self):
        # Create the boxes
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.kal_box = QLineEdit()
        self.kal_box.setPlaceholderText("number of burned Calories.")
        self.distance_box = QLineEdit()
        self.distance_box.setPlaceholderText("The distance applied.")
        self.disc_box = QLineEdit()
        self.disc_box.setPlaceholderText("Enter a description")

        # Create the buttons
        self.sub_btn = QPushButton("Submit")
        self.add_btn = QPushButton("Add")
        self.del_btn = QPushButton("Delete")
        self.clear_btn = QPushButton("Clear")
        self.dark_check = QCheckBox("Dark Mode")

        # Create the tables and plots
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Date", "Calories", "Distance", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)

        # Design the layout
        self.master_layout = QHBoxLayout()
        self.col1 = QVBoxLayout()
        self.col2 = QVBoxLayout()

        self.sub_row1 = QHBoxLayout()
        self.sub_row2 = QHBoxLayout()
        self.sub_row3 = QHBoxLayout()
        self.sub_row4 = QHBoxLayout()

        self.sub_row1.addWidget(QLabel("Date:"))
        self.sub_row1.addWidget(self.date_box)
        self.sub_row2.addWidget(QLabel("Calories:"))
        self.sub_row2.addWidget(self.kal_box)
        self.sub_row3.addWidget(QLabel("Distance:"))
        self.sub_row3.addWidget(self.distance_box)
        self.sub_row4.addWidget(QLabel("Description:"))
        self.sub_row4.addWidget(self.disc_box)

        self.col1.addLayout(self.sub_row1)
        self.col1.addLayout(self.sub_row2)
        self.col1.addLayout(self.sub_row3)
        self.col1.addLayout(self.sub_row4)
        self.col1.addWidget(self.dark_check)

        self.btn_row1 = QHBoxLayout()
        self.btn_row2 = QHBoxLayout()

        self.btn_row1.addWidget(self.add_btn)
        self.btn_row1.addWidget(self.del_btn)
        self.btn_row2.addWidget(self.clear_btn)
        self.btn_row2.addWidget(self.sub_btn)

        self.col1.addLayout(self.btn_row1)
        self.col1.addLayout(self.btn_row2)

        self.col2.addWidget(self.canvas)
        self.col2.addWidget(self.table)

        self.master_layout.addLayout(self.col1, 35)
        self.master_layout.addLayout(self.col2, 65)
        self.setLayout(self.master_layout)
        self.loadTable()

    # Load tables
    def loadTable(self):
        self.table.setRowCount(0)
        self.cursor.execute("SELECT * FROM fittrack ORDER BY Date DESC")
        rows = self.cursor.fetchall()
        for row in rows:
            fit_id, date, calories, distance, description = row
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(fit_id)))
            self.table.setItem(row_position, 1, QTableWidgetItem(date))
            self.table.setItem(row_position, 2, QTableWidgetItem(str(calories)))
            self.table.setItem(row_position, 3, QTableWidgetItem(str(distance)))
            self.table.setItem(row_position, 4, QTableWidgetItem(description))
            row_position += 1

    # buttons click
    def button_click(self):
        self.add_btn.clicked.connect(self.addData)
        self.del_btn.clicked.connect(self.delData)
        self.sub_btn.clicked.connect(self.plotCalories)  # plot button
        self.dark_check.stateChanged.connect(self.darkMode)  # dark mode check box
        self.clear_btn.clicked.connect(self.clear)
    # delete button

    # Add data to the database
    def addData(self):
        date = self.date_box.date().toString("yyyy-MM-dd")
        calories = self.kal_box.text()
        distance = self.distance_box.text()
        description = self.disc_box.text()

        if calories and distance and description:
            self.cursor.execute("INSERT INTO fittrack (Date, Calories, Distance, Description) VALUES (?, ?, ?, ?)",
                                (date, calories, distance, description))
            self.conn.commit()
            self.loadTable()
        else:
            QMessageBox.warning(self, "Warning", "Please fill all the fields")

    # delete from the table
    def delData(self):
        row = self.table.currentRow()
        if row >= 0:
            fit_id = self.table.item(row, 0).text()
            confirm = QMessageBox.question(self, "Delete", "Are you sure you want to delete this record?", QMessageBox.Yes | QMessageBox.No)
            if confirm == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM fittrack WHERE ID=?", (fit_id,))
                self.conn.commit()
                self.loadTable()
        else:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")

    #Calculate calories in beautiful matplt betwwen distance and calories
    def plotCalories(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_title("Calories vs Distance")
        ax.set_xlabel("Distance")
        ax.set_ylabel("Calories")

        self.cursor.execute("SELECT Distance, Calories FROM fittrack")
        rows = self.cursor.fetchall()
        distance = [row[0] for row in rows]
        calories = [row[1] for row in rows]

        ax.plot(distance, calories, 'ro-')
        self.canvas.draw()
    
    # Dark mode
    def darkMode(self):
        if self.dark_mode:
            self.dark_mode = False
            self.setStyleSheet("")
        else:
            self.dark_mode = True
            self.setStyleSheet("background-color: #333; color: #fff;")

    # reset the canvas and input fields
    def clear(self):
        self.figure.clear()
        self.canvas.draw()
        self.kal_box.clear()
        self.distance_box.clear()
        self.disc_box.clear()

    def initDB(self):
        # Connect to SQLite database
        self.conn = sqlite3.connect('fittrack.db')
        self.cursor = self.conn.cursor()
        
        # Create the fitness table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS fittrack (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Date TEXT NOT NULL,
                Calories INTEGER NOT NULL,
                Distance REAL NOT NULL,
                Description TEXT NOT NULL
            );
        """)
        self.conn.commit()

if __name__ == "__main__":
    app = QApplication(argv)
    main = FitTrack()
    main.show()
    app.exec_()