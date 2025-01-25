from idlelib.help_about import AboutDialog

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, QLineEdit, QPushButton, \
    QMainWindow, QTableWidget, QTableWidgetItem, QDialog, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__() #initializing the super class, in this case QMainWindow
        self.setWindowTitle("Student Management System")
        self.setMinimumSize(800, 600)

        file_menu_item = self.menuBar().addMenu("&File") # &File is a convention, has to be done
        help_menu_item = self.menuBar().addMenu("&Help")
        edit_menu_item = self.menuBar().addMenu("&Edit")

        #Adding subitems to File menu
        add_student_action = QAction(QIcon("icons/add.png"), "Add Student",self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        #Adding About Menu
        about_action = QAction("About",self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        #Adding subitems to Edit Menu
        search_action = QAction(QIcon("icons/search.png"),"Search",self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)


        self.table = QTableWidget()
        self.table.setColumnCount(4) #Set the number of cols
        self.table.setHorizontalHeaderLabels(("Id","Name","Course","Mobile")) # Set the names for the columns
        self.table.verticalHeader().setVisible(False) #Removes the duplicate column showing the row numbers
        self.setCentralWidget(self.table)
        """ This will set what the central widget of the application is
        The central widget is the main area of the window where most of the application's content is displayed"""

        #Create toolbar and add toolbar elements, toolbar will have shortcuts for add students and search functionality
        toolbar = QToolBar()
        toolbar.setMovable(True) #User can move around the toolbar
        self.addToolBar(toolbar)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)

        #Create status bar and add status bar elements
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        #Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)


    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        #Clearing existing widgets before they are invoked again, to avoid duplicates
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        #Edit and delete button widgets are invoked here
        self.statusbar.addWidget(edit_button)
        self.statusbar.addWidget(delete_button)

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

    def search(self):
        dialog = SearchDialog() #Create instance of EditDialog() class
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created as an introduction to PyQt6 and SQLite3 libraries.
        Feel free to modify and reuse this app
        """
        self.setText(content)

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()  # Initializing the super class, in this case QDialog
        self.setWindowTitle("Update Student Data")
        self.setFixedWidth(300)
        self.setFixedWidth(300)

        layout = QVBoxLayout()
        #Get student name from current selected row
        index = main_window.table.currentRow()
        student_name = main_window.table.item(index, 1).text()

        #Get id from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Add student name widget
        self.student_name = QLineEdit(student_name)
        """Adding argument student_name in QLineEdit will make the default value the student_name
        in the text input of GUI, i.e. in this case the current student name in the current row
        """
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Get course name from current selected row
        course_name = main_window.table.item(index, 2).text()
        #Add combo box of courses
        self.course_name = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.course_name.addItems(courses)
        self.course_name.setCurrentText(course_name)
        layout.addWidget(self.course_name)

        #Get mobile number from current selected row
        mobile = main_window.table.item(index, 3).text()
        #Add mobile widget
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        #Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_student)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_student(self):
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
                       (self.student_name.text(),
                        self.course_name.itemText(self.course_name.currentIndex()),
                        self.mobile.text(),
                        self.student_id))
        connection.commit()
        cursor.close()
        connection.close()
        #Refresh the table after updating values
        main_window.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()  #Initializing the super class, in this case QDialog
        self.setWindowTitle("Delete Student Data")
        #Create instance of grid layout class and add yes/no option
        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")
        #Add widget position on layout
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)#Set the layout after adding widgets
        #Get index and student_id values from table
        index = main_window.table.currentRow()
        self.student_id = main_window.table.item(index, 0).text()
        # Add action if yes/no button is clicked
        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close)

    def delete_student(self):

        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?",
                       (self.student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        # Refresh the table after updating values
        main_window.load_data()
        #Close the delete dialog window
        self.close()
        #Showing deletion confirmation message
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfully")
        confirmation_widget.exec()

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
class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search Student")
        self.setFixedWidth(300)
        self.setFixedWidth(300)

        #Create layout and input widget
        layout = QVBoxLayout()
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        #Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM students WHERE name = ?", (name,))
        rows = list(result)
        print(rows)
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        #Qt.MatchFlag.MatchFixedString indicates that the search should match the exact string
        for item in items:
            print(item)
            main_window.table.item(item.row(),1).setSelected(True)

        cursor.close()
        connection.close()

app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec()) #Excecute the app
