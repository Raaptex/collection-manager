import json
import os

def reload():
    global config

    with open("./config.json","r") as f:
        config = json.loads(f.read())
        return config

def open_file():

    os.open("config.json")
    
def update(payload):
        
    with open("./config.json","w") as w:
        
        config.update(payload)
        w.write(json.dumps(config, indent=4))