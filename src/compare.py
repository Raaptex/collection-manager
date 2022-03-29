import os

os.system("cls")

class Comparator:
    
    def compare_two_json(self, json_1 : dict, json_2 : dict):
        
        compared = dict()
        
        for key in json_1.keys():
                
            for key_2 in json_2.keys():
                
                if json_1[key]["sha256"] == json_2[key_2]["sha256"] and key != key_2:
                    
                    compared[key] = json_1[key]
                    print("\n--------------- File renamed ---------------\n" + str(json_1[key]))
                
            if key in compared: continue
                    
            if key not in json_2:
            
                compared[key] = json_1[key]
                print("\n--------------- Missing key ---------------\n" + str(json_1[key]))
                continue
                
            if json_1[key]["sha256"] != json_2[key]["sha256"]:
            
                compared[key] = json_1[key]
                print("\n--------------- File edited ---------------\n" + str(json_1[key]))
                continue
                
        return compared
     
    def get_missing_files(self, json_1 : dict, json_2 : dict):
        
        compared = dict()
        files_sha = list()
        
        for val in json_2.values():
            files_sha.append(val["sha256"])
        
        for key in json_1.keys():
                    
            if json_1[key]["sha256"] not in files_sha:
            
                compared[key] = json_1[key]
                print("\n--------------- Missing key ---------------\n" + str(json_1[key]))
                
        return compared