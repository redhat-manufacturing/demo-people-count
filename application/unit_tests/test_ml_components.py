import unittest
import time
from pipeline import Pipeline
from object_detection import ObjectDetection,ObjectTracking,Utilities
import threading
import cv2
import numpy as np
from config.config import Configuration

class unit_test(unittest.TestCase):
    
    def test_object_detector(self):
        obj_det = ObjectDetection()
        
        '''test logo model'''
        imgsz = 640
        # path='/home/janvi/apparel_logo_janvi/ml_service/application/weights/best_84-fp16.tflite'
        path='/home/ubuntu/akash_test/akash-apparel-logo/ml_service/application/weights/best_84-fp16.tflite'

        obj_det.load_model(path,device='cpu',dnn=False,imgsz=imgsz)
        self.assertIsNotNone(obj_det.interpreter)
        self.assertListEqual(list(obj_det.input_details[0]['shape']),[1,640,640,3])
        
        img0 = np.ones([1200,640,3])
        img = obj_det.pre_process(img0)
        img = obj_det.pre_process_inference(img,half=False)
        self.assertListEqual(list(img.shape),[1,imgsz,imgsz,3])

        conf_thres,iou_thres,classes,max_det = 0.5,0.5,None,1000
        nms_pred = obj_det.predict(img,conf_thres,iou_thres,classes,max_det)
        self.assertIsNotNone(obj_det.pred) #predictions not None
        self.assertIsNotNone(nms_pred) #NMS_predictions not None
        self.assertEqual(len(np.array(nms_pred).shape),3) #prediction shape
        self.assertLess(np.array(nms_pred).shape[-1],max_det+1) #bbox detection limit
        self.assertGreater(np.array(nms_pred).all(),0) #check the bbox coordinates 
        self.assertLess(np.array(nms_pred).all(),imgsz) #check the bbox coordinates
        
        '''test people model'''
        imgsz = 384
        # path='/home/janvi/apparel_logo_janvi/ml_service/application/weights/best_people-fp16.tflite'
        path = '/home/ubuntu/akash_test/akash-apparel-logo/ml_service/application/weights/best_people-fp16.tflite'
        obj_det.load_model(path,device='cpu',dnn=False,imgsz=imgsz)
        self.assertIsNotNone(obj_det.interpreter)
        self.assertListEqual(list(obj_det.input_details[0]['shape']),[1,384,384,3])

        img0 = np.ones([1200,640,3])
        img = obj_det.pre_process(img0)
        img = obj_det.pre_process_inference(img,half=False)
        self.assertListEqual(list(img.shape),[1,imgsz,imgsz,3])

        conf_thres,iou_thres,classes,max_det = 0.5,0.5,None,1000
        nms_pred = obj_det.predict(img,conf_thres,iou_thres,classes,max_det)
        self.assertIsNotNone(obj_det.pred) #predictions not None
        self.assertIsNotNone(nms_pred) #NMS_predictions not None
        self.assertEqual(len(np.array(nms_pred).shape),3) #prediction shape
        self.assertLess(np.array(nms_pred).shape[-1],max_det+1) #bbox detection limit
        self.assertGreater(np.array(nms_pred).all(),0) #check the bbox coordinates 
        self.assertLess(np.array(nms_pred).all(),imgsz) #check the bbox coordinates
        
    def test_pipeline(self):
        pipe = Pipeline()

        self.assertEqual(pipe.conf_thres,Configuration.dwell_config["det_thresh_person"])
        self.assertEqual(pipe.conf_thres_apparel,Configuration.dwell_config["det_thresh_logo"])
        self.assertEqual(pipe.weights.split('/')[-1].split('.')[-1],"tflite")
        self.assertEqual(pipe.weights_logo.split('/')[-1].split('.')[-1],"tflite")
        self.assertIsNotNone(pipe.stream_fps)
        self.assertIsNotNone(pipe.stream_width)
        self.assertIsNotNone(pipe.stream_height)
        # self.assertIsNotNone(pipe.object_detect.interpreter)
        # self.assertIsNotNone(pipe.apparel_logo_detect.interpreter)
        if Configuration.dwell_config["save_video"]:
            self.assertIsNotNone(pipe.output_s)
        # source='/home/janvi/apparel_logo_janvi/ml_service/nike.mp4'
        source = '/home/ubuntu/akash_test/akash-apparel-logo/ml_service/q.mp4'
        thread = threading.Thread(target=pipe.run, kwargs={'source':source}, daemon=True)
        thread.start()
        time.sleep(120)
        
        s_time=time.time() #check the output data
        while not pipe.wait_data:
            if abs(s_time-time.time())>60:
                break
        data = pipe.wait_data
        if data:
            data_keys = data.keys()
            self.assertListEqual(list(data_keys),['people','total_num_logos','logos_distribution'])
            self.assertEqual(data["total_num_logos"],len(data["logos_distribution"]))
            self.assertGreater(data['people'],-1)
            self.assertGreater(data['total_num_logos'],-1)
            self.assertIsInstance(data['logos_distribution'],dict)

        self.assertIsNotNone(pipe.vid)
        pipe.stop_run()
        self.assertIsNone(pipe.vid)

        """If source doesn't exist"""
        pipe = Pipeline()
        # source='/home/janvi/apparel_logo_janvi/ml_service/random.mp4'
        source = '/home/ubuntu/akash_test/akash-apparel-logo/ml_service/1.mp4'
        thread = threading.Thread(target=pipe.run, kwargs={'source':source}, daemon=True)
        thread.start()

if __name__ == '__main__':
    unittest.main()



    

    