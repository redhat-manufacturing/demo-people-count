import argparse
import os
import sys
from pathlib import Path
import time
import json
import cv2
import signal
import datetime
import shutil
import numpy as np
from config import Config 
from sqlitedb import DataBase
from utils.utils import ( print_args, scale_coords, )
from utils.utils import read_sess_json,read_env_json
from utils.logs import logger
import base64
from streamer import StreamChunker, VideoWriter,VideoReader#PiCamWriter
from streamer.test_video import ReadVideo
from object_detection import ObjectDetection,ObjectTracking,Utilities

FILE = Path(__file__).resolve()
IMG_FORMATS = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']  # acceptable image suffixes
VID_FORMATS = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']  # acceptable video suffixes
data_dict=read_env_json()

class Pipeline():
    '''This class has all the functions related to running the main pipeline'''
    def __init__(self):
        self.vid = None
        self.stop_flag=False
        try:
            signal.signal(signal.SIGUSR1, self.sig_handler)#signal handler for stopping only chunking and not processing
        except:
            pass
        self.__pplct_utils=Utilities()#utilities having common functions
        self.__config=Config()#config has all the configurable variables
        self.__object_tracker=ObjectTracking(self.__config)#load according to config
        self.__object_detect=ObjectDetection()#define obj detection module for person to load and preprocess model
        self.DB = DataBase()
        self.pc_data=None
        self.pc_dict = None
        self.conn = self.DB.create_connection(self.DB.DBFILE)

    def sig_handler(self,signum,frame):
        if(signum==10):#only if the signal is SIGUSR1
            self.stop_chunk()

    def stop_chunk(self):
        self.vid.stop_chunking()

    # @torch.no_grad()
    def run(self,
			source='nike.mp4',  # file/dir/URL/glob, 0 for webcam
			output="output.mp4",
			fps=10,
			width=1280,
			height=720,
			frames_test=0,
			chunk=5
            ):
            
        
        source = str(source)
        is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
        is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
        webcam = source.isnumeric() or source.endswith('.txt') or (is_url and not is_file)
        conf_thres=self.__config.pplct_config["conf_thresh"]
        imgsz=self.__config.pplct_config["imgsz"]
        iou_thres=self.__config.pplct_config["iou_thresh"]
        weights=self.__config.pplct_config["weights"]
        classes=self.__config.pplct_config["classes"]
        max_det=1000
        dnn=False
        device=''
        half=False
        
        #To send request to db-service
        AUTH_TOKEN=base64.urlsafe_b64decode(data_dict['AUTH_TOKEN'].encode()).decode()
        SESSION_TOKEN = read_sess_json()['SESS_TOKEN']

        
        #loading model
        self.__object_detect.load_model(weights,device,dnn,imgsz)
        start_time=time.time()
        
        test_num_frames=False
        if(frames_test!=0):#to check whether to test or not
            test_num_frames=True

        stream_fps=fps
        stream_width=width
        stream_height=height

        if os.path.isfile(source) and not is_url and not webcam:
            self.vid = ReadVideo(source)
        else:
            if stream_fps is not None:
                stream_fps=int(stream_fps)
            
            if stream_height is not None:
                stream_height=int(stream_height)
            
            if stream_width is not None:
                stream_width=int(stream_width)
             
            self.vid = StreamChunker(source, chunk_size=5, chunk_dir='temp_chunks', fps=stream_fps,restart_time=-1,width=stream_width,height=stream_height)
        if(self.__config.pplct_config["save_video"] and source!='picamera'):#initialise writer for saving output video
            if(fps is not None):
                fps=int(fps)
            output_s = VideoWriter(self.vid, filename=output, fps=fps)
        print("Time Diff : ", time.time() - start_time)
        try:
            end_time=int(os.getenv("END",default='21')) #to check the stop time of scheduling of streaming
            time_to_check=datetime.time(end_time,0,0)#convert end time to datetime obj to compare with current time
            checked_time=False
            save_frame=True
            prev={'enter':0,'leave':0}
            s_time=time.time()
            count=0
            self.pc_dict = {}
            for flag, im0s,curr_chunk_time in self.vid: 
                if self.stop_flag:
                    break                   
                self.__object_detect.skip_frame_counter+=1
                if self.__object_detect.skip_frame_counter%self.__config.pplct_config["skip_frame"]==0:
                    count+=1
                    im=self.__object_detect.pre_process(im0s)               
                    im=self.__object_detect.pre_process_inference(im,half)#preprocess according to YOLO 

                    pred=self.__object_detect.predict(im,conf_thres,iou_thres,classes,max_det)
                    for i, det in enumerate(pred):  # per image
                        if len(det):
                            if self.__object_detect.tflite:
                                det[:, :4] = scale_coords(im.shape[1:], det[:, :4], im0s.shape).round()
                            else:
                                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0s.shape).round()
                            
                            shp=im0s.shape
                            self.pc_data = self.__object_tracker.perform_tracking_people_count(im0s,det,shp,curr_chunk_time,self.__pplct_utils,self.__config.pplct_config["ref_line_start"][-1])
                            self.pc_data['people_count']["head_count"] = len(det)
                            print(self.pc_data)
                            self.pc_dict[self.__object_detect.skip_frame_counter] = self.pc_data
                            try:
                                if(self.pc_data!=prev):
                                    self.DB.insert_data(self.conn,self.pc_data,curr_chunk_time,self.DB.TABLE,encode=True)
                                    prev=self.pc_data
                                    if save_frame:#to save first processed frame
                                        try:
                                            file_path='application/static/first_frame.jpg'
                                            cv2.imwrite(file_path,im0s)
                                            save_frame=False
                                            logger.info("pipeline.py: saved first processed frame")
                                        except Exception as e:
                                            save_frame=False
                                            logger.error("pipeline.py: couldn't save first frame."+str(e))
                            except Exception as e:
                                print("failed to insert data into the db")
                                logger.error("MLservice - pipeline.py: Unable to insert data."+ str(e))
                                print(e)                            

                            if(self.__config.pplct_config["save_video"]):#write to video
                                self.__pplct_utils.draw_analytics_people_count(im0s,self.pc_data['people_count']["enter"],self.pc_data['people_count']["leave"])#draw anayltics like enter or left people
                                self.__pplct_utils.draw_line(im0s,self.__config.pplct_config["ref_line_start"],self.__config.pplct_config["ref_line_end"])#draw reference line according to roi
                                output_s.write(im0s)
           

                if(checked_time==False and datetime.datetime.now().hour==int(end_time)):#to check if time to stop streaming has come
                    print("Stopping at stop_time")
                    self.vid.stop_chunking()
                    checked_time=True
                if(test_num_frames):#for testing purposes
                    if(self.vid.count==frames_test):
                        break

            e_time=time.time()
            print("Total time:",abs(e_time-s_time))
            print("Total Frames:",self.__object_detect.skip_frame_counter)
            print("FPS ",self.__object_detect.skip_frame_counter/abs(e_time-s_time))
        except KeyboardInterrupt:
            print("keyboard interuppted")

        if(self.vid is not None):
            self.vid.release()
        if(self.__config.pplct_config["save_video"]):
            output_s.release()

    def parse_opt(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--source', type=str, default='data/vid3_15.mp4', help='file/dir/URL/glob, 0 for webcam')
        parser.add_argument('--output', default='output.mp4', help='save the inference as an output file. Make sure to enable saving a video in the configuration')
        parser.add_argument('--fps', default='10', help='fps of input')
        parser.add_argument('--height', default='720', help='height of input')
        parser.add_argument('--width', default='1280', help='width of input')
        parser.add_argument("-c", "--chunk", default=5, help="chunk size for streamer module")

        opt = parser.parse_args()
        print_args(FILE.stem, opt)
        return opt
    
if __name__ == "__main__":
    pipe=Pipeline()
    opt = pipe.parse_opt()
    print(opt)
    pipe.run(**vars(opt))