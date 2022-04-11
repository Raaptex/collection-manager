import json


class Lang:
    
    def __init__(self) -> None:
        
        with open("config.json", "r") as c:
            c = json.loads(c.read())
            self.lang = c["lang"]
            
        self.dict = json.loads(open("assets/lang.json", "r").read())[self.lang]
            
    def get_string(self, string_name):
        
        if string_name in self.dict:
            
            return self.dict[string_name]
            
        else:
            
            return self.dict["not_assigned"]
        
    def string_to_font_size(self, string_name):
        
        if string_name in self.dict:
            
            return len(self.dict[string_name]) * 8
            
        else:
            
            return len(self.dict["not_assigned"]) * 8