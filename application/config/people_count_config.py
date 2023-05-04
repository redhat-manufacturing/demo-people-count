import json
import os

class PeopleCountConfig:
    def __init__(self):
        #the variables that we want editable by the client are in the json , all other are hardcoded here
        cwd=os.path.dirname(__file__)
        with open(os.path.join(cwd,"people_count_config.json"), "r") as f:
            self.config = json.load(f)
        
        self.config["skip_frame"] = 3
        self.config["classes"]=[0]
        self.config["db_write_frequency"]=20
        self.config["weights"]="application/weights/best_people_miap-fp16.tflite"
        self.config["imgsz"] = [384,384]
        self.config["iou_thresh"] = 0.45 #iou threshold for object detection
        self.config["conf_thresh"]=self.config["det_confidence_threshold"]#conf threshold for object detection