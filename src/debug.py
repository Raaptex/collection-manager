import datetime

class Debug:
    
    def __init__(self, file_log : bool) -> None:
        
        self.colors = Colors()
        self.file_log = file_log
    
    def add_time(self, string):
        
        now = datetime.datetime.now()
        return f"[{now.hour}:{now.minute}:{now.second}] " + string
    
    def log_in_file(self, string):
        
        if self.file_log:
            
            with open("log.txt", "a") as f:
                f.write(string + "\n")
    
    def Log(self, string):
        
        string = self.add_time(string)
        
        print(self.colors.blue + string + self.colors.red)
        self.log_in_file(string)
        
    def Info(self, string):
        
        string = self.add_time(string)
        
        print(self.colors.info + string + self.colors.red)
        
class Colors:
    
    red = "\033[0m\033[31m"
    blue = "\033[0m\033[94m"
    green = "\033[0m\033[32m"
    info = "\033[0m\033[90m\x1B[3m"