from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QImage
from gundam import find_gundam
from PyQt5 import uic
import webbrowser
import requests
import sys, os

# Define function to import external files when using PyInstaller.
def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# progress updater class to update progress bar
class ProgressUpdater(QObject):
    updateProgress = pyqtSignal(int)

# worker thread class to hold seperate thread that handles web scraping operations
class WorkerThread(QThread):
    result_signal = pyqtSignal(list)

    def __init__(self, item_name, num_values, progress_updater, includeInSearch):
        super(WorkerThread, self).__init__()
        self.item_name = item_name
        self.num_values = num_values
        self.progress_updater = progress_updater
        self.includeInSearch = includeInSearch

    def run(self):
        result = find_gundam(self.item_name, self.num_values, self.progress_updater, self.includeInSearch)
        self.result_signal.emit(result)

# search window class that prompts user with item name, filters, num values, etc.
class SearchWindow(QMainWindow):
    def __init__(self):
        super(SearchWindow, self).__init__()
        uic.loadUi(resource_path("search_window.ui"), self)
        self.show()

        self.pushButton.clicked.connect(self.searchGundams)
        self.search_results_window = None

    def searchGundams(self):
        if self.lineEdit.text() != "":
            radioButtons = [self.radioButton, self.radioButton_2, self.radioButton_3, self.radioButton_4]
            hobbyStores = ["Panda Hobby", "Canadian Gundam", "Argama Hobby", "Toronto Gundam"]
            includeInSearch = []

            for radioButton in radioButtons:
                for hobbyStore in hobbyStores:
                    if radioButton.isChecked():
                        if radioButton.text() == hobbyStore:
                            includeInSearch.append(hobbyStore)

            self.search_results_window = SearchResultsWindow()
            self.pushButton.setEnabled(False)
            self.search_results_window.setSearchWindow(self)
            self.search_results_window.searchGundams(self.lineEdit.text(), self.spinBox.value(), includeInSearch)
            self.search_results_window.show()
        else:
            message = QMessageBox()
            message.setText("Input item name to search!")
            message.exec_()

    def enableButton(self):
        self.pushButton.setEnabled(True)

# search results class that displays table of results
class SearchResultsWindow(QMainWindow):
    enable_button_signal = pyqtSignal()

    def __init__(self):
        super(SearchResultsWindow, self).__init__()
        uic.loadUi(resource_path("list_window.ui"), self)
        self.show()

        self.pushButton.clicked.connect(self.showSearchWindow)

        self.worker_thread = None
        self.search_window = None
        self.more_info_window = None

        self.enable_button_signal.connect(self.enableButtonSignal)

        self.progress_updater = ProgressUpdater()

        self.progress_updater.updateProgress.connect(self.updateProgressBar)

        self.tableWidget.setVisible(False)
        self.pushButton.setVisible(False)

    def setSearchWindow(self, search_window):
        self.search_window = search_window

    def searchGundams(self, item_name, num_values, includeInSearch):
        if self.worker_thread is None or not self.worker_thread.isRunning():
            self.progressBar.setValue(0) 
            self.worker_thread = WorkerThread(item_name, num_values, self.progress_updater, includeInSearch)
            self.worker_thread.result_signal.connect(self.displaySearchResult)
            self.worker_thread.finished.connect(self.enableButtonSignal)
            self.worker_thread.start()

    def displaySearchResult(self, result):
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)

        column_headers = ["Store", "Name", "Price", "Status", " "]
        self.tableWidget.setHorizontalHeaderLabels(column_headers)

        for store_data in result:
            for gundam_info in store_data:
                if gundam_info is not None:
                    self.tableWidget.insertRow(self.tableWidget.rowCount())
                    self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 0, QTableWidgetItem(gundam_info.store))
                    self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 1, QTableWidgetItem(gundam_info.name))
                    self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 2, QTableWidgetItem(gundam_info.price))
                    self.tableWidget.setItem(self.tableWidget.rowCount() - 1, 3, QTableWidgetItem(gundam_info.status))

                    # Add a "More" button to the table
                    more_button = QPushButton("More")
                    more_button.clicked.connect(lambda _, info=gundam_info: self.showMoreInfo(info))
                    self.tableWidget.setCellWidget(self.tableWidget.rowCount() - 1, 4, more_button)

        
        for i in range(self.tableWidget.columnCount()):
            if i == 1:
                    self.tableWidget.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:
                self.tableWidget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.progressBar.setVisible(False)
        self.tableWidget.setVisible(True)
        self.pushButton.setVisible(True)

    def showMoreInfo(self, gundam_info):
        # Use the existing MoreInfoWindow if it exists
        if self.more_info_window is None:
            self.more_info_window = MoreInfoWindow()

        # Disconnect the signal before connecting it again
        self.more_info_window.pushButton.disconnect()

        self.more_info_window.updateInfo(gundam_info)
        self.more_info_window.show()

    def enableButtonSignal(self):
        if self.search_window is not None:
            self.search_window.enableButton()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def showSearchWindow(self):
        if self.search_window is not None:
            self.search_window.show()
        self.close()

# more info class that displays additional info on each gundam
class MoreInfoWindow(QMainWindow):
    def __init__(self):
        super(MoreInfoWindow, self).__init__()
        uic.loadUi(resource_path("more_information.ui"), self)
        self.show()

    def updateInfo(self, gundam_info):
        try:
            self.label_store.setText(gundam_info.store)
            self.label_name.setText(gundam_info.name)
            self.label_price.setText(gundam_info.price)
            self.label_status.setText(gundam_info.status)
            self.pushButton.clicked.connect(lambda: webbrowser.open(gundam_info.href))

            # Load and display the image
            print(gundam_info.image)
            image = QImage()
            image.loadFromData(requests.get(gundam_info.image).content)
            pixmap = QPixmap(image)

            if pixmap.isNull():
                print("Error loading image:", gundam_info.image)
            else:
                self.label_image.setPixmap(pixmap)
                self.label_image.setScaledContents(True)  # Ensure the image scales with the label size
        except Exception as e:
            print("Error in updateInfo:", e)

def main():
    app = QApplication([])
    search_window = SearchWindow()
    app.exec_()

if __name__ == '__main__':
    main()