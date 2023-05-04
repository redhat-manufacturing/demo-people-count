# from config.config import Configuration 
# conf=Configuration()
from tracker import BYTETracker
from .person import People, Person
import time
import datetime
class ObjectTracking():
    
    def __init__(self,conf):


        self.__updated_person_ids=[]#to get info about persons whose tracking info has got updated
        self.__byte_person_ids=[]
        self.__byte_person_objects={}#to get all the required tracking info stored with key as tracking id

        self.__conf=conf
        self.__byte_tracker=BYTETracker(self.__conf.byte_tracker_config)#initialise bytetracker obj

        self.__entry_count=0
        self.__exit_count=0
        self.__y_line = None#reference line position




    def make_proper_int(self,box):
        """ Checks boundaries and fixes face detection to integers
        Arguments
            box (list): bounding box of a face
        Returns
            integer values and boundary checked box
        """
        int_box=[0,0,0,0]
        for i in range(4):
            if box[i]<0:
                int_box[i]=0
            else:
                int_box[i]=int(box[i])

        return int_box


    def update_movement_info(self,person_object):

        line_cross = person_object.check_line_cross(self.__y_line)#check if person has crossed line or not
        if(line_cross):
            direction=person_object.get_direction()
            
            if(direction):
                self.__entry_count+=1
                bbox_color = "GREEN"
            else:
                self.__exit_count+=1
                bbox_color = "RED"
        else:
            bbox_color = "WHITE"
        
        person_object.update_box_color(bbox_color)
        return bbox_color

    def perform_tracking_people_count(self,im0s,det,shp,curr_chunk_time,Do,y_line):
        '''perform tracking and the counting of people
           :param im0s(ndarray): the image 
           :param det(array): the prediction of the object detection model
           :param shp(list): the image size
           :param curr_chunk_time(str): the current time of the chunk being processed
           :param Do(object): the utility object used for drawing analytics
           :param y_line(integer): the position of reference line
           :return: data as json to insert into DB containing analytics
        '''
        st=time.time()
        persons=self.__byte_tracker.update(det, [shp[0], shp[1]],shp[:2])
        self.__updated_person_ids=[]
        self.__y_line = y_line 

        total_tracks = len(persons)
        st=time.time()
        people_enter_ids = []
        people_exit_ids = []
        for person_track in persons:
            box = person_track.tlwh
            id_ = person_track.track_id
            box = self.make_proper_int(box)#make coordinates of bounding box compatible

            if(id_ not in self.__byte_person_ids):
                person_object =  People(box,id_)
                self.__byte_person_objects[id_]=person_object 
                self.__byte_person_ids.append(id_)
                self.__updated_person_ids.append(id_)
            else:
                person_object=self.__byte_person_objects[id_]
                person_object.update_position(box)
                self.__updated_person_ids.append(id_)   


            startX,startY,endX,endY= box[0], box[1], box[0]+box[2], box[1]+box[3]
            bbox_color = self.update_movement_info(person_object)
            # print(bbox_color)
            if bbox_color=="GREEN":
                people_enter_ids.append(id_)
            elif bbox_color=="RED":
                people_exit_ids.append(id_)
            # print(people_tracking)
            if(self.__conf.pplct_config["save_video"]):
                Do.draw_bbox(im0s,str(id_),startX,startY,endX,endY,"person",person_object.box_color)#draw bbox

        data={
            "people_count":{
            "enter":self.__entry_count,
            "leave":self.__exit_count
            },
            "tracker IDS":self.__updated_person_ids,
            "people_enter_ids":people_enter_ids,
            "people_leave_ids":people_exit_ids
        }

        return data
