import time
import time
from utils.utils import letterbox
import numpy as np
from utils.utils import ( check_img_size, non_max_suppression)
class ObjectDetection():
    '''This class has all the utilities and surrounding functions that are used in loading yolov5-v6 object detection model'''

    def __init__(self):

        self.writer_init_flag=True
        self.skip_frame_counter= -1

        self.start_time= time.time()
        self.tflite=True
        self.vid_writer=None
        self.device = 'cpu'
        
    def load_model(self,weights,device,dnn,imgsz):
        '''load yolo model
           :param weights(str):the path of yolo obj detection weight
           :param device(str):cuda,cpu etc
           :param dnn: use opencv dnn or not
           :param imgsz: the image size that is set in pipeline
        '''
        if weights.split(".")[-1]=="tflite":
            from tflite_runtime.interpreter import Interpreter
            self.interpreter = Interpreter(model_path=weights)
            self.interpreter.allocate_tensors()
            self.input_details = self.interpreter.get_input_details()  # inputs
            self.output_details = self.interpreter.get_output_details()  # outputs
            self.imgsz = imgsz
            self.stride = 32
            self.pt=False

    def pre_process(self,im0s):
        ''' preprocess image to set required shape 
            :param im0s(ndarray):the input image which one wants to preprocess
            :return: Image after preprocessing
        '''
        im = letterbox(im0s, self.imgsz, stride=self.stride, auto=self.pt)[0]#convert to necessary shape
        im = im[:, :, ::-1]
        im = np.ascontiguousarray(im)
        return im
    
    def pre_process_inference(self,im,half):
        ''' preprocess image to make it yolo inference compatible
            :param im(ndarray): the input image which is to be preprocessed
            :param half(bool): quantization
            :return: image after preprocessing
        '''
        im = im.astype(np.float32)
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = np.expand_dims(im,0)  # expand for batch dim

        return im

    def predict(self,im,conf_thres,iou_thres,classes,max_det):
        n,h,w,c=im.shape
        agnostic_nms=False
        input, output = self.input_details[0], self.output_details[0]
        self.interpreter.set_tensor(input['index'], im)
        self.interpreter.invoke()
        pred = self.interpreter.get_tensor(output['index'])
        pred[..., :4] *= [w, h, w, h]
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        #use nms to discard unrequired Bounding box
        return pred
        