# coding: utf-8

from time import sleep

import datetime
import os
import subprocess
import threading

def powershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed

def getSHA(path, filename):
    
    sha = str(powershell(f'Get-FileHash "{path}\\{filename}" -Algorithm SHA256 | Format-List').stdout).encode("utf-8").decode("utf-8").split("\\n")[3].split(": ")[1].split("\\r")[0]
    
    return sha

def d_size(size):
    
    if(size >= 1e+9):
        
        return str(round(size/1e+9, 2)) + " Go"
    
    if(size >= 1e+6):
        
        return str(round(size/1e+6, 2)) + " Mo"
    
    if(size >= 1000):
        
        return str(round(size/1000, 2)) + " Ko"
    
        
    return str(size) + " o"

def get_file_metadata(path, filename):
    
    file_metadata = dict()
    
    stat_file = os.stat(path + "\\" + filename)
    
    file_metadata["size"] = stat_file.st_size 
    file_metadata["d_size"] = d_size(stat_file.st_size)
    file_metadata["name"] = filename
    file_metadata["date"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(path + "\\" + filename))).split(".")[0]
    file_metadata["disk"] = path.split("\\")[0]
    file_metadata["folder"] = path + "\\"
    file_metadata["file_path"] = path + "\\" + filename
    file_metadata["sha256"] = getSHA(path, filename)

    return file_metadata

def open_dir(path):
    
    for file in os.listdir(path):
        
        print(path + "\\" + file)
        
        if os.path.isdir(path + "\\" + file):
            
            open_dir(path + "\\" + file)
        
        else:
            
            if os.path.isfile(path + "\\" + file):
                
                threading.Thread(target=getFile, args=(path, file,)).start()
                sleep(0.5)
                
    return

def getFile(path, file):
    metadata = get_file_metadata(path, file)
    out_json[path + "\\" + file] = metadata

def scan(path):
    global files_path, out_json
    
    files_path = path.replace("/", "\\")
    out_json = dict()
            
    open_dir(files_path)
        
    return out_json