import sys
import os
import scanner
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import *

class rootWindow(QWidget):
    
    def __init__(self, win):
        super().__init__()
        self.win = win
        
        self.height = 720
        self.width = 1080
        
    def build(self):
        self.win.setWindowTitle("File Scanner")
        self.win.setGeometry(100, 100, self.width, self.height)
        
        self.label = QLabel(self.win)
        self.label.setText("File Scanner")
        self.label.setGeometry(round(self.width/2 - 150/2), 10, 150, 30)
        self.label.setStyleSheet("font-size: 22px")
        
        self.scan_button = QPushButton('Scan', self.win)
        self.scan_button.setToolTip('Scan your files')
        self.scan_button.setGeometry(10, 10, 150, 30)
        self.scan_button.clicked.connect(self.scan)
        
        self.createTable(0)
        
    @pyqtSlot()
    def scan(self):
        
        text, ok = QInputDialog.getText(self, 'Scan', 'Scan folder :')
        if not ok:
            return
        
        self.file_json = scanner.scan(text)
        self.file_id = 0
        self.sha256 = []
        
        self.tableWidget.setRowCount(len(self.file_json) + 1)
        
        for file in self.file_json:
            
            self.file_id += 1
            self.setFile(file)
            
    def setFile(self, file):
        
        meta = self.file_json[file]
        
        self.tableWidget.setItem(self.file_id, 0, QTableWidgetItem(meta["name"]))
        self.tableWidget.setItem(self.file_id, 1, QTableWidgetItem(meta["date"]))
        self.tableWidget.setItem(self.file_id, 2, QTableWidgetItem(meta["d_size"]))
        self.tableWidget.setItem(self.file_id, 3, QTableWidgetItem(meta["disk"]))
        self.tableWidget.setItem(self.file_id, 4, QTableWidgetItem(meta["folder"]))
        self.tableWidget.setItem(self.file_id, 5, QTableWidgetItem(meta["file_path"]))
        self.tableWidget.setItem(self.file_id, 6, QTableWidgetItem(meta["sha256"]))
        
        if meta["sha256"] in self.sha256:
            
            for i in range(7):
                self.tableWidget.item(self.file_id, i).setBackground(QColor(255,200,200))
        
        else:
            self.sha256.append(meta["sha256"])
        
    def createTable(self, files_count):
        
        self.tableWidget = QTableWidget(self.win)
        self.tableWidget.cellClicked.connect(self.cellClick)
        
        self.tableWidget.setRowCount(files_count + 1) 
        self.tableWidget.setColumnCount(7)  
        
        self.tableWidget.setGeometry(10, 50, self.width-20, self.height-60)
        
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Name"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("Date"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("Size"))
        self.tableWidget.setItem(0, 3, QTableWidgetItem("Disk"))
        self.tableWidget.setItem(0, 4, QTableWidgetItem("Folder"))
        self.tableWidget.setItem(0, 5, QTableWidgetItem("File Path"))
        self.tableWidget.setItem(0, 6, QTableWidgetItem("SHA256"))
        
        self.tableWidget.setColumnWidth(0, 250)
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 5)
        self.tableWidget.setColumnWidth(4, 200)
        self.tableWidget.setColumnWidth(5, 350)
        self.tableWidget.setColumnWidth(6, 450)
        
    def cellClick(self, row, column):
        
        cell = self.tableWidget.item(row, column)
        
        if(column == 5):
            
            os.system(f'explorer /select, "{cell.text()}"')
            
        if(column == 6):
            
            if(cell.background().color() == QColor(255,200,200)):
                
                print("yes")
                
                for r in range(len(self.file_json)):
                    
                    if self.tableWidget.item(r, column).text() == cell.text() and r != row:
                        
                        for c in range(7):
                            
                            self.tableWidget.item(r, c).setBackground(QColor(200,200,255))
                            
            else:
                
                for r in range(len(self.file_json)):
                    
                    if self.tableWidget.item(r, column).background().color() == QColor(200,200,255):
                            
                        for c in range(7):
                            
                            self.tableWidget.item(r, c).setBackground(QColor(255,255,255))
                
        else:
            for r in range(len(self.file_json)):
                    
                if self.tableWidget.item(r, column).background().color() == QColor(200,200,255):
                        
                    for c in range(7):
                        
                        self.tableWidget.item(r, c).setBackground(QColor(255,255,255))
   
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    root = QWidget()
    rootWin = rootWindow(root)
    rootWin.build()
    
    root.show()
    
    sys.exit(app.exec_())