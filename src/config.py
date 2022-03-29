import json
import os

def reload():

    with open("./config.json","r") as f:
        return json.loads(f.read())

def open_file():

    os.open("config.json")