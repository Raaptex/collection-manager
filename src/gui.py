import sys
import os
import scanner
import config
import threading
import json
import csv_editor
import compare
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import *
from debug import Debug

class rootWindow(QWidget):
    
    def __init__(self, win, os_system):
        super().__init__()
        self.win = win
        self.os = os_system
        self.config = config.reload()
        
        self.height = 720
        self.width = 1080

        self.duplicates = []
        self.w = None
        
    def build(self):
        self.win.setWindowTitle("Collection Manager BETA-0.2")
        self.win.setGeometry(100, 100, self.width, self.height)
        
        self.label = QLabel(self.win)
        self.label.setText("Collection Manager")
        self.label.setGeometry(round(self.width/2 - 190/2), 10, 190, 30)
        self.label.setStyleSheet("font-size: 22px")
        
        self.scan_button = QPushButton('Scan', self.win)
        self.scan_button.setToolTip('Scan your files')
        self.scan_button.setGeometry(10, 10, 50, 30)
        self.scan_button.clicked.connect(self.scan)

        self.dup_button = QPushButton('Remove duplicates', self.win)
        self.dup_button.setToolTip('Remove all duplicates')
        self.dup_button.setGeometry(70, 10, 130, 30)
        self.dup_button.clicked.connect(self.remove_dup)

        self.exp_button = QPushButton('Export CSV', self.win)
        self.exp_button.setToolTip('Export your scan to CSV file')
        self.exp_button.setGeometry(210, 10, 100, 30)
        self.exp_button.clicked.connect(self.export_scan)
        
        self.imp_button = QPushButton('Clean the base', self.win)
        self.imp_button.setToolTip('Delete removed file in the base')
        self.imp_button.setGeometry(320, 10, 100, 30)
        self.imp_button.clicked.connect(self.clean_the_base)
        
        self.exp_button = QPushButton('Help', self.win)
        self.exp_button.setToolTip('Get help')
        self.exp_button.setGeometry(self.width - 50, 10, 40, 30)
        self.exp_button.clicked.connect(self.open_help)
        
        self.exp_button = QPushButton('⚙', self.win)
        self.exp_button.setToolTip('Open settings')
        self.exp_button.setGeometry(self.width - 90, 10, 30, 30)
        self.exp_button.clicked.connect(self.open_settings)
        
        self.createTable(0)
        
    def open_settings(self):
        
        if self.os == "windows":
            
            os.startfile("config.json")
            
        elif self.os == "linux":
            
            os.system("gnome-open config.json")
    
    def open_help(self):
        if self.w is None:
            self.w = helpWindow()
            self.w.build(self)
            self.w.show()

        else:
            self.w.close()
            self.w = None

        
    @pyqtSlot()
    def clean_the_base(self):
        
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Clean the base")
        dlg.setText("Are you sure you want to clean the base ?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button != QMessageBox.Yes:
            return
        
        with open("db.json", "r") as r:
            db = json.loads(r.read())
            missing = list()
            
            for k in db["collection"].keys():
                
                if "missing" in db["collection"][k]:
                    
                    missing.append(k)
            
            for k in missing:
                del db["collection"][k]
            
            with open("db.json", "w") as w:
                w.write(json.dumps(db, indent=4))
        
    @pyqtSlot()
    def scan(self):
        
        self.scan_folder = QFileDialog.getExistingDirectory(self, 'Select Folder')
        
        threading.Thread(target=self.scan_files).start()
        
    def scan_files(self):
        
        #if self.text == "#folder":
        #    self.text = self.config["folder"]
        
        self.file_json = scanner.scan_files(self.scan_folder, self.os, self.config)
        self.file_id = 0
        self.sha256 = []
        self.duplicates = []
        missing = dict()
        
        self.tableWidget.setRowCount(len(self.file_json) + 1)
        
        for file in self.file_json:
            
            self.file_id += 1
            self.setFile(self.file_json[file], self.file_id)
        
        scanner.get_files_sha(self, self.file_json)
        
        if self.config["already_scanned"] != "":
            missing = compare.Comparator().get_missing_files(json.loads(open("db.json", "r").read())["collection"], self.file_json)
            #self.file_json.update(json.loads(open(self.config["already_scanned"], "r").read()))
        
        self.tableWidget.setRowCount(len(self.file_json) + len(missing) + 1) 
        
        for miss in missing:
            
            self.file_id += 1
            missing[miss]["missing"] = True
            self.setFile(missing[miss], self.file_id, True)
            
        
        with open("db.json", "r") as r:
            db = json.loads(r.read())
            self.file_json.update(missing)
            db["collection"] = self.file_json
            with open("db.json", "w") as w:
                w.write(json.dumps(db, indent=4))

    @pyqtSlot()
    def export_scan(self):
        
        try:
                
            csv_editor.CsvEditor().create_csv_with_json("export.csv", self.file_json)

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Success")
            dlg.setText('Scan exported to "export.csv"')
            dlg.exec()
            
        except:
            
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Failed")
            dlg.setText('Make a new scan before')
            dlg.exec()

    @pyqtSlot()
    def remove_dup(self):
        
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Remove duplicates")
        dlg.setText("Are you sure you want to permanently delete files ?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        dlg.setIcon(QMessageBox.Question)
        button = dlg.exec()

        if button != QMessageBox.Yes:
            return
        
        if len(self.duplicates) > 0:

            for file_id in self.duplicates:

                cell = self.tableWidget.item(file_id, 5)
                os.remove(cell.text())
                Debug.Log("Removed > " + cell.text())

        else:

            dlg = QMessageBox(self)
            dlg.setWindowTitle("Remove duplicates")
            dlg.setText("No files are duplicated")
            dlg.exec()

    def setFile(self, meta, file_id, missing = False):
        
        Debug.Log("Set file : " + str(meta))
                
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
                for i in range(7):
                    self.tableWidget.item(file_id, i).setBackground(QColor(255,100,100))
                
        else:
            
            self.tableWidget.setItem(file_id, 6, QTableWidgetItem("..."))
            
            for c in range(7):
                self.tableWidget.item(file_id, c).setBackground(QColor(255,200,150))
                
        return True
        
    def createTable(self, files_count):
        
        self.tableWidget = QTableWidget(self.win)
        
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

class helpWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.height = 200
        self.width = 400
        
    def build(self, win):
        self.setWindowTitle("Collection Manager BETA-0.2")
        self.setGeometry(win.win.pos().x() + (win.width/2 - self.width/2), win.win.pos().y() + (win.height/2 - self.height/2), self.width, self.height)
        
        self.label = QLabel(self)
        self.label.setText("Collection Manager")
        self.label.setGeometry(round(self.width/2 - 190/2), 10, 190, 30)
        self.label.setStyleSheet("font-size: 22px")
        
        self.label = QLabel(self)
        self.label.setText("Version : BETA-0.2")
        self.label.setGeometry(round(self.width/2 - 190/2), 40, 190, 30)
        
        self.label = QLabel(self)
        self.label.setText("Version type : Testing")
        self.label.setGeometry(round(self.width/2 - 190/2), 55, 190, 30)
        
        self.label = QLabel(self)
        self.label.setText('<a href="https://github.com/Raaptex/collection-manager">Github page</a>')
        self.label.setGeometry(round(self.width/2 - 190/2), 70, 190, 30)
        
def start(os_system):
    global Debug
    
    Debug = Debug(json.loads(open("config.json").read())["log"])
    
    app = QApplication(sys.argv)
    root = QWidget()
    Debug.Info(os_system)
    rootWin = rootWindow(root, os_system)
    rootWin.build()
    
    root.show()
    
    sys.exit(app.exec_())