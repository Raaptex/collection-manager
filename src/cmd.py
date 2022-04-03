import sys
import os
from colorama import Fore

print(sys.argv)

def remove_tag(path, filename, tag):
    
    try:

        if filename.split(".")[-2] == tag:

            new_name = ".".join(filename.split(".")[:-2]) + "." + filename.split(".")[-1]

            os.rename(path + "/" + filename, path + "/" + new_name)

            print(Fore.GREEN + "[-] " + new_name)
        
        else:

            print(Fore.WHITE + "[.] " + filename)
            
    except:
        
        print(Fore.RED + "[!] " + filename)

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

elif sys.argv[1] == "test_remove_tags":
    
    print(sys.argv[2].split(".")[:-2])
    print(".".join(sys.argv[2].split(".")[:-2]) + "." + sys.argv[2].split(".")[-1])

#/media/alex/DD-Films-1