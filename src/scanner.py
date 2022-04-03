# coding: utf-8

from time import sleep
from videoprops import get_video_properties
from debug import Debug

import datetime
import os
import subprocess
import threading
import json
import time

Debug = Debug(json.loads(open("config.json", "r").read())["log"])
paused = False
end_scan = False

class ThreadManager:

    def __init__(self, t_func, max_threads) -> None:
        
        self.t_func = t_func
        self.current_queue = 0
        self.max_threads = max_threads
        self.queue = []

    def thread_ended(self):

        self.current_queue -= 1
        if len(self.queue) >= 1:
            self.start_thread(self.queue.pop(0))

    def start_thread(self, t_args):

        if self.current_queue < self.max_threads:

            self.current_queue += 1
            threading.Thread(target=self.t_func, args=t_args).start()
        
        else:

            self.queue.append(t_args)


def add_tag(path, filename, tag):

    if len(filename.split(".")) >= 2:
        if filename.split(".")[-2] != tag:

            new_name = ".".join(filename.split(".")[:-1]) + "." + tag + "." + filename.split(".")[-1]

            os.rename(path + folder_separator + filename, path + folder_separator + new_name)
            return new_name
        
        else:
            
            return filename
    else:
            
            return filename


def powershell(cmd):
    completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    return completed


def get_files_sha(files_json : dict):
    global end_scan
    
    total_size = 0
    
    for file in files_json.keys():
        
        total_size += files_json[file]["size"]
    
    i = 0
    return_json = {}
    times = list()
    
    for file in files_json.keys():
        
        if paused:
            Debug.Log("Scan paused !")
        
        while paused:
            
            time.sleep(0.5)
            
            if not paused:
                Debug.Log("Scan resumed !")
        
        if end_scan:
            end_scan = False
            return files_json
        
        i+=1
        if "sha256" not in files_json[file]:
            start_time = time.time()
            sha = "Error"

            if system_os == "windows":
                sha = str(powershell(f'Get-FileHash "{file}" -Algorithm SHA256 | Format-List').stdout).encode("utf-8").decode("utf-8").split("\\n")[3].split(": ")[1].split("\\r")[0]
            elif system_os == "linux":
                sha = os.popen(f'sha256sum "{file}"').read().split(" ")[0]
            else:
                print("Error for SHA !")
                print(system_os)
            
            total_size -= files_json[file]["size"]
            
            if files_json[file]["size"] >= 1e+8:   
                
                sha_time = time.time() - start_time
                go_time = sha_time / files_json[file]["size"] * 1e+9
                Debug.Info(str(sha_time))
                Debug.Info(str(go_time))
                
                times.append(go_time)
                mean = sum(times)/len(times)
                est_time = round(total_size / 1e+9 * mean)
                
                payload = {
                    "d_time": str(est_time) + "s",
                    "h": 0,
                    "m": 0,
                    "s": est_time
                }
                
                if est_time >= 60:
                    
                    est_time = round(est_time / 60)
                    payload["d_time"] = str(est_time) + "m"
                    payload["m"] = est_time
                    payload["s"] = 0
                    
                if est_time >= 60:
                    
                    payload["d_time"] = str(est_time // 60) + "h" + str(est_time % 60) + "m"
                    payload["m"] = est_time % 60
                    payload["h"] = est_time // 60
                
                root.update_status(estimated_time = True, payload = payload)
            
            root.update_status(get_sha = True, i = i, i2 = len(files_json.keys()))
            
            return_json[file] = files_json[file]
            return_json[file]["sha256"] = sha
            return_json[file]["sha_date"] = str(datetime.datetime.now())
            root.setFile(return_json[file], i)

    end_scan = False
    return files_json


def d_size(size):
    
    if(size >= 1e+9):
        
        return str(round(size/1e+9, 2)) + "Go"
    
    if(size >= 1e+6):
        
        return str(round(size/1e+6, 2)) + "Mo"
    
    if(size >= 1000):
        
        return str(round(size/1000, 2)) + "Ko"
    
        
    return str(size) + "o"


def get_file_metadata(path, filename):
    
    file_metadata = dict()
    
    stat_file = os.stat(path + folder_separator + filename)
    
    file_metadata["size"] = stat_file.st_size 
    file_metadata["d_size"] = d_size(stat_file.st_size)
    file_metadata["name"] = filename
    file_metadata["date"] = str(datetime.datetime.fromtimestamp(os.path.getmtime(path + folder_separator + filename))).split(".")[0]
    if system_os == "windows":
        file_metadata["disk"] = path.split(folder_separator)[0]
    elif system_os == "linux":
        file_metadata["disk"] = path.split(folder_separator)[4]
    file_metadata["folder"] = path + folder_separator
    file_metadata["file_path"] = path + folder_separator + filename
    if(filename.split(".")[-1] in ["mp4", "avi", "mkv"]):
        
        try:
            props = get_video_properties(path + folder_separator + filename)

            file_metadata["codec"] = props['codec_name']
            file_metadata["resolution"] = str(props['width']) + "x" + str(props['height'])
            file_metadata["ratio"] = props['display_aspect_ratio']
            file_metadata["framerate"] = props['avg_frame_rate']
            
        except:
            
            file_metadata["codec"] = "Error"
            file_metadata["resolution"] = "Error"
            file_metadata["ratio"] = "Error"
            file_metadata["framerate"] = "Error"

    return file_metadata


def open_dir(path):
    
    for file in os.listdir(path):
        
        if os.path.isdir(path + folder_separator + file):
            
            open_dir(path + folder_separator + file)
        
        else:
            
            if os.path.isfile(path + folder_separator + file):
                
                thread_manager.start_thread((path, file,))
                
    return

def read_files_in_dir(path):
    
    for file in os.listdir(path):
        
        if os.path.isdir(path + folder_separator + file):
            
            read_files_in_dir(path + folder_separator + file)
        
        else:
            
            if os.path.isfile(path + folder_separator + file):
                
                out_json[path + folder_separator + file] = {
                    "name": file,
                    "file_path": path + folder_separator + file
                }
                
    return

def getFile(path, file):
    global completed_files
    
    if config["add_tag"] == True:
        file = add_tag(path, file, config["tag"])

    metadata = get_file_metadata(path, file)
    out_json[path + folder_separator + file] = metadata

    completed_files += 1
    #Debug.Log(f"[{completed_files}/{files_count}] " + path + folder_separator + file)
    root.update_status(get_meta_data = True, i = completed_files, i2 = files_count)

    thread_manager.thread_ended()


def countFiles(path):
    global files_count

    for file in os.listdir(path):
        
        if os.path.isdir(path + folder_separator + file):
            
            countFiles(path + folder_separator + file)
        
        else:
            
            if os.path.isfile(path + folder_separator + file):
                
                files_count += 1

                #Debug.Log(f"[{files_count}] " + path + folder_separator + file)

def get_files(path, s_os, config_):
    global files_path, out_json, system_os, folder_separator, config, files_count, completed_files, thread_manager, Debug
    
    root.update_status(get_files = True)
    
    if s_os == "linux":
        folder_separator = "/"
    elif s_os == "windows":
        folder_separator = "\\"
    else:
        return print("Error on scanning !")

    files_path = path.replace("/", folder_separator)
    out_json = dict()
    system_os = s_os
    config = config_
            
    read_files_in_dir(files_path)
        
    return out_json

def scan_files(path, s_os, config_):
    global files_path, out_json, system_os, folder_separator, config, files_count, completed_files, thread_manager, Debug
    
    if s_os == "linux":
        folder_separator = "/"
    elif s_os == "windows":
        folder_separator = "\\"
    else:
        return print("Error on scanning !")

    files_path = path.replace("/", folder_separator)
    out_json = dict()
    system_os = s_os
    config = config_
    files_count = 0
    completed_files = 0
    thread_manager = ThreadManager(getFile, config["scan_threads"])

    countFiles(files_path)
            
    open_dir(files_path)

    while completed_files < files_count:
        sleep(0.5)
        
    return out_json

def set_root(root_class):
    global root
    root = root_class