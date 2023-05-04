from .people_count_config import PeopleCountConfig
# from .centroid_tracker_config import CentroidTrackerConfig


class Config:
    def __init__(self):
        #the variables that we want editable by the client are in the json , all other are hardcoded here
        self.pplct_config = PeopleCountConfig().config
        # self.ct_config = CentroidTrackerConfig()
        self.byte_tracker_config={}
        self.byte_tracker_config['conf']=None
        self.byte_tracker_config['nms']=None
        self.byte_tracker_config['track_thresh']=0.5 #how much should be the confidence be while tracking
        self.byte_tracker_config['track_buffer']=40 #after how many frames should track be removed for that id
        self.byte_tracker_config['match_thresh']=0.8 #how much should objects match to be recognised as the same obj while tracking
        self.byte_tracker_config['aspect_ratio_thresh']=1.6
        self.byte_tracker_config['min_box_area']=10
        self.byte_tracker_config['mot20']=False