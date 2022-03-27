class CsvEditor:
    
    def create_csv_with_json(self, file_name, json_ : dict):
        
        csv = open(file_name, "w")
        l = []
        
        for item in json_[list(json_.keys())[0]]:
            
            l.append(item)
            
        string_csv = ",".join(l) + "\n"
        
        for item in json_:
            
            l = []
            
            for item_ in json_[item]:
            
                l.append(str(json_.get(item).get(item_)))
                
            string_csv += ",".join(l) + "\n"
            
        csv.write(string_csv)