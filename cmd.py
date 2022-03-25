import sys
import os
from colorama import Fore

print(sys.argv)

def remove_tag(path, filename, tag):

    if filename.split(".")[-2] == tag:

        new_name = ".".join(filename.split(".")[:-3]) + "." + filename.split(".")[-1]

        os.rename(path + "/" + filename, path + "/" + new_name)

        print(Fore.GREEN + "[-] " + new_name)
    
    else:

        print(Fore.WHITE + "[.] " + filename)

def open_dir(path):
    
    for file in os.listdir(path):
        
        if os.path.isdir(path + "/" + file):
            
            open_dir(path + "/" + file)
        
        else:
            
            if os.path.isfile(path + "/" + file):
                
                if sys.argv[1] == "remove_tags":
                    remove_tag(path, file, sys.argv[3])
                
    return


if sys.argv[1] == "remove_tags":
    
    open_dir(sys.argv[2])

#/media/alex/DD-Films-1