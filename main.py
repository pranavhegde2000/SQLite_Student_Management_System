from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, \
    QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox
import sys
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() #initializing the super class, in this case QMainWindow
        self.setWindowTitle("Student Management System")

        file_menu_item = self.menuBar().addMenu("&File") # &File is a convention, has to be done
        help_menu_item = self.menuBar().addMenu("&Help")

        #Adding subitems to menu
        add_student_action = QAction("Add Student",self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction("About",self)
        help_menu_item.addAction(about_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4) #Set the number of cols
        self.table.setHorizontalHeaderLabels(("Id","Name","Course","Mobile")) # Set the names for the columns
        self.table.verticalHeader().setVisible(False) #Removes the duplicate column showing the row numbers
        self.setCentralWidget(self.table)
        """ This will set what the central widget of the application is
        The central widget is the main area of the window where most of the application's content is displayed"""

    def load_data(self):
        connection = sqlite3.connect('database.db')
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)
        for row_number ,row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    #The below function is for inserting new database records
    def insert(self):
        dialog = InsertDialog() #Create instance of InsertDialog() class
        dialog.exec()


# The below class is required to create a dialog window which will be a pop up window
class InsertDialog(QDialog):
    def __init__(self):
        super().__init__() #Initializing the super class, in this case QDialog
        self.setWindowTitle("Insert Student Data")
        self.setFixedWidth(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()

        #Add student name widget
        self.student_name = QLineEdit() #Adding self before student_name will make it an instance variable
        #So self.student_name can be accessed in other functions of the same class
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology","Math","Astronomy","Physics"]
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        #Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        #Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex()) #This is a combo box, so use itemText()
        # currentIndex() will return the currently selected option in the combo box
        mobile = self.mobile.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
                       (name, course, mobile))
        """cursor.execute will take both sql queries and the variables as arguments,
        (?, ?, ?) corresponds to name, course, mobile
        """
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()
        """ main_window is the instance of the MainWindow() class, load_data will 
        call load_data() method, so this will refresh the data window after we add new student
        data
        """

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec()) #Excecute the app
