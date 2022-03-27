import sys
import os
from time import sleep
import scanner
import config
import threading
import json
import csv_editor
import compare
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import *

class rootWindow(QWidget):
    
    def __init__(self, win, os_system):
        super().__init__()
        self.win = win
        self.os = os_system
        self.config = config.reload()
        
        self.height = 720
        self.width = 1080

        self.duplicates = []
        
    def build(self):
        self.win.setWindowTitle("File Scanner")
        self.win.setGeometry(100, 100, self.width, self.height)
        
        self.label = QLabel(self.win)
        self.label.setText("File Scanner")
        self.label.setGeometry(round(self.width/2 - 150/2), 10, 150, 30)
        self.label.setStyleSheet("font-size: 22px")
        
        self.scan_button = QPushButton('Scan', self.win)
        self.scan_button.setToolTip('Scan your files')
        self.scan_button.setGeometry(10, 10, 50, 30)
        self.scan_button.clicked.connect(self.scan)

        self.dup_button = QPushButton('Remove duplicates', self.win)
        self.dup_button.setToolTip('Remove all duplicates')
        self.dup_button.setGeometry(70, 10, 150, 30)
        self.dup_button.clicked.connect(self.remove_dup)

        self.exp_button = QPushButton('Export scan', self.win)
        self.exp_button.setToolTip('Export your scan to JSON file')
        self.exp_button.setGeometry(230, 10, 100, 30)
        self.exp_button.clicked.connect(self.export_scan)
        
        self.exp_button = QPushButton('Import JSON', self.win)
        self.exp_button.setToolTip('Import scan with JSON file')
        self.exp_button.setGeometry(340, 10, 100, 30)
        self.exp_button.clicked.connect(self.import_json)
        
        self.createTable(0)
        
    @pyqtSlot()
    def import_json(self):
        
        text, ok = QInputDialog.getText(self, 'Scan', 'Scan folder :')
        if not ok:
            return
        
        self.file_json = json.loads(open(text, "r").read())
        self.file_id = 0
        self.sha256 = []
        self.duplicates = []
        
        self.tableWidget.setRowCount(len(self.file_json) + 1)
        
        for file in self.file_json:
            
            self.file_id += 1
            self.setFile(file)
        
    @pyqtSlot()
    def scan(self):
        
        self.text, ok = QInputDialog.getText(self, 'Scan', 'Scan folder :')
        if not ok:
            return
        
        threading.Thread(target=self.scan_files).start()
        
    def scan_files(self):
        
        if self.text == "#folder":
            self.text = self.config["folder"]
        
        self.file_json = scanner.scan_files(self.text, self.os, self.config)
        self.file_id = 0
        self.sha256 = []
        self.duplicates = []
        missing = dict()

        if self.config["already_scanned"] != "":
            missing = compare.Comparator().get_missing_files(json.loads(open(self.config["already_scanned"], "r").read()), self.file_json)
            self.file_json.update(json.loads(open(self.config["already_scanned"], "r").read()))
        
        self.tableWidget.setRowCount(len(self.file_json) + 1)
        
        for file in self.file_json:
            
            self.file_id += 1
            self.setFile(self.file_json[file], self.file_id)
            
        print("\n------ Missing -------\n" + str(missing) + "\n---------------------\n")
            
        for miss in missing:
            
            self.file_id += 1
            self.setFile(missing[miss], self.file_id, True)
            
        sleep(1)
        print("----- SHA")
        scanner.get_files_sha(self, self.file_json)

    @pyqtSlot()
    def export_scan(self):
        
        try:
        
            with open("export.json", "w") as f:
                f.write(json.dumps(self.file_json, indent=4))
                
            csv_editor.CsvEditor().create_csv_with_json("export.csv", self.file_json)

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Success")
            dlg.setText('New file "export.json" was created')
            dlg.exec()
            
        except:
            
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Failed")
            dlg.setText('Make a new scan before')
            dlg.exec()

    @pyqtSlot()
    def remove_dup(self):
        
        if len(self.duplicates) > 0:

            for file_id in self.duplicates:

                cell = self.tableWidget.item(file_id, 5)
                print("remove > " + cell.text())
                os.remove(cell.text())
                print(self.duplicates)
                print(file_id)

        else:

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Remove duplicates")
            dlg.setText("No files are duplicated")
            dlg.exec()

    def setFile(self, meta, file_id, missing = False):
        
        print(meta)
                
        self.tableWidget.setItem(file_id, 0, QTableWidgetItem(meta["name"]))
        self.tableWidget.setItem(file_id, 1, QTableWidgetItem(meta["date"]))
        self.tableWidget.setItem(file_id, 2, QTableWidgetItem(meta["d_size"]))
        self.tableWidget.setItem(file_id, 3, QTableWidgetItem(meta["disk"]))
        self.tableWidget.setItem(file_id, 4, QTableWidgetItem(meta["folder"]))
        self.tableWidget.setItem(file_id, 5, QTableWidgetItem(meta["file_path"]))
        if "sha256" in meta:
            self.tableWidget.setItem(file_id, 6, QTableWidgetItem(meta["sha256"]))
            
            if not missing:
                for c in range(7):
                                
                    self.tableWidget.item(file_id, c).setBackground(QColor(200,255,200))
            
                if meta["sha256"] in self.sha256:

                    self.duplicates.append(file_id)
                    
                    for i in range(7):
                        self.tableWidget.item(file_id, i).setBackground(QColor(200,200,255))
            
                else:
                    self.sha256.append(meta["sha256"])
                    
            else:
                print("----= " + str(file_id))
                for i in range(7):
                    print("---- " + str(i))
                    self.tableWidget.item(file_id-1, i).setBackground(QColor(255,100,100))
                
        else:
            
            self.tableWidget.setItem(file_id, 6, QTableWidgetItem("..."))
            
            for c in range(7):
                print(c)
                self.tableWidget.item(file_id, c).setBackground(QColor(255,200,150))
                
        return True
        
    def createTable(self, files_count):
        
        self.tableWidget = QTableWidget(self.win)
        #self.tableWidget.cellClicked.connect(self.cellClick)
        
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
        
    """def cellClick(self, row, column):
        
        cell = self.tableWidget.item(row, column)
        
        if(column == 5):
            
            if self.os == "linux":

                os.system(f'xdg-open "{cell.text()}"')

            else:

                os.system(f'explorer /select, "{cell.text()}"')
            
        if(column == 6):
            
            if(cell.background().color() == QColor(200,200,255)):
                
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
                        
                        self.tableWidget.item(r, c).setBackground(QColor(255,255,255))"""
   
        
def start(os_system):
    app = QApplication(sys.argv)
    root = QWidget()
    print(os_system)
    rootWin = rootWindow(root, os_system)
    rootWin.build()
    
    root.show()
    
    sys.exit(app.exec_())