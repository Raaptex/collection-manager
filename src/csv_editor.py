class CsvEditor:
    
    def create_csv_with_json(self, file_name, json_ : dict):
        
        csv = open(file_name, "w", encoding="utf-16")
        l = []
        
        for item in json_[list(json_.keys())[0]]:
            
            l.append(item)
            
        string_csv = "|;|".join(l) + "\n"
        
        for item in json_:
            
            l = []
            
            for item_ in json_[item]:
            
                l.append(str(json_.get(item).get(item_)))
                
            string_csv += "|;|".join(l) + "\n"
            
        csv.write(string_csv)
    
    def csv_to_json(self, file_path):
        
        json = {}
        csv_lines = []
        
        for l in open(file_path, "r", encoding="utf-16").readlines(): 
            csv_lines.append(l.replace('\n', '').replace('\r', ''))
        data = csv_lines[1:]
        keys = csv_lines[0].split("|;|")
        
        for d in data:
            
            if d == "": continue
        
            json[d.split("|;|")[0]] = {}
            
            for i, k  in enumerate(keys):
                
                json[d.split("|;|")[0]][k] = d.split("|;|")[i]
        
        print(json)
        return json