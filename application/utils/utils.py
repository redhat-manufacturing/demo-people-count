import json
import os
import io
import math
import time
from pathlib import Path
from typing import Optional
import inspect
import numpy as np
import cv2
from base64 import b64encode    
from PIL import Image

config_path = os.path.dirname(os.path.dirname(__file__))

def read_env_json():
	with open(os.path.join(config_path,'config/.config_env.json')) as json_file:
		data = json.load(json_file)
	return data

def read_sess_json():
	with open(os.path.join(config_path,'config/session_config.json')) as json_file:
		data = json.load(json_file)
	return data

def write_sess_json(key_list,new_val_list):
	data=read_sess_json()
	for key,new_val in zip(key_list,new_val_list):
		data[key]=new_val
	with open(os.path.join(config_path,'config/session_config.json'), 'w') as f:
		json.dump(data, f)

def write_env_json(key_list,new_val_list):
	data=read_env_json()
	for key,new_val in zip(key_list,new_val_list):
		data[key]=new_val
	with open(os.path.join(config_path,'config/.config_env.json'), 'w') as f:
		json.dump(data, f)


def write_config_json(new_val,key):
	with open(os.path.join(config_path,'config/people_count_config.json')) as json_file:
		data = json.load(json_file)
	data[key]=new_val
	with open(os.path.join(config_path,'config/people_count_config.json'),"w") as f:
		json.dump(data, f)

def read_config_json():
	with open(os.path.join(config_path,'config/people_count_config.json')) as json_file:
		data = json.load(json_file)
	return data


def read_json(json_file):
    with open(json_file, "r") as filename:
        j = json.load(filename)
    return  j

def read_msg_json():
	with open(os.path.join(config_path,'config/msg.json')) as json_file:
		data = json.load(json_file)
	return data

def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    # Resize and pad image while meeting stride-multiple constraints
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)

def xywh2xyxy(x):
    """Convert nx4 boxes from [x, y, w, h] to [x1, y1, x2, y2] where xy1=top-left, xy2=bottom-right
    y = x.clone() if isinstance(x, torch.Tensor) else np.copy(x)"""
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2  # top left x
    y[:, 1] = x[:, 1] - x[:, 3] / 2  # top left y
    y[:, 2] = x[:, 0] + x[:, 2] / 2  # bottom right x
    y[:, 3] = x[:, 1] + x[:, 3] / 2  # bottom right y
    return y

def make_divisible(x, divisor):
    """Returns nearest x divisible by divisor
    if isinstance(divisor, torch.Tensor):
        divisor = int(divisor.max())  # to int"""
    return math.ceil(x / divisor) * divisor

def check_img_size(imgsz, s=32, floor=0):
    """Verify image size is a multiple of stride s in each dimension"""
    if isinstance(imgsz, int):  # integer i.e. img_size=640
        new_size = max(make_divisible(imgsz, int(s)), floor)
    else:  # list i.e. img_size=[640, 480]
        imgsz = list(imgsz)  # convert to list if tuple
        new_size = [max(make_divisible(x, int(s)), floor) for x in imgsz]
    # if new_size != imgsz:
        # LOGGER.warning(f'WARNING: --img-size {imgsz} must be multiple of max stride {s}, updating to {new_size}')
    return new_size

def print_args(args: Optional[dict] = None, show_file=True, show_fcn=False):
    """Print function arguments (optional args dict)"""
    x = inspect.currentframe().f_back  # previous frame
    file, _, fcn, _, _ = inspect.getframeinfo(x)
    if args is None:  # get args automatically
        args, _, _, frm = inspect.getargvalues(x)
        args = {k: v for k, v in frm.items() if k in args}
    s = (f'{Path(file).stem}: ' if show_file else '') + (f'{fcn}: ' if show_fcn else '')
    
def scale_coords(img1_shape, coords, img0_shape, ratio_pad=None):
    """Rescale coords (xyxy) from img1_shape to img0_shape """
    if ratio_pad is None:  # calculate from img0_shape
        gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])  # gain  = old / new
        pad = (img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2  # wh padding
    else:
        gain = ratio_pad[0][0]
        pad = ratio_pad[1]

    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    clip_coords(coords, img0_shape)
    return coords

def clip_coords(boxes, img_shape):
    """Clip bounding xyxy bounding boxes to image shape (height, width) """
    boxes[:, 0].clip(0, img_shape[1])  # x1
    boxes[:, 1].clip(0, img_shape[0])  # y1
    boxes[:, 2].clip(0, img_shape[1])  # x2
    boxes[:, 3].clip(0, img_shape[0])  # y2
    
def non_max_suppression(prediction, conf_thres=0.25, iou_thres=0.45, classes=1, agnostic=False, multi_label=False,
                    labels=(), max_det=300):
    """Runs Non-Maximum Suppression (NMS) on inference results
    Returns:
        list of detections, on (n,6) tensor per image [xyxy, conf, cls]
    """
    nc = prediction.shape[2] - 5  # number of classes
    xc = prediction[..., 4] > conf_thres  # candidates
    # Checks
    assert 0 <= conf_thres <= 1, f'Invalid Confidence threshold {conf_thres}, valid values are between 0.0 and 1.0'
    assert 0 <= iou_thres <= 1, f'Invalid IoU {iou_thres}, valid values are between 0.0 and 1.0'
    # Settings
    min_wh, max_wh = 2, 4096  # (pixels) minimum and maximum box width and height
    max_nms = 30000  # maximum number of boxes into torchvision.ops.nms()
    time_limit = 10.0  # seconds to quit after
    redundant = True  # require redundant detections
    multi_label &= nc > 1  # multiple labels per box (adds 0.5ms/img)
    merge = False  # use merge-NMS
    t = time.time()
    output = [np.zeros((0, 6))] * prediction.shape[0]
    for xi, x in enumerate(prediction):  # image index, image inference
        # Apply constraints
        # x[((x[..., 2:4] < min_wh) | (x[..., 2:4] > max_wh)).any(1), 4] = 0  # width-height
        x = x[xc[xi]]  # confidence
        # Cat apriori labels if autolabelling
        if labels and len(labels[xi]):
            l = labels[xi]
            v = np.zeros((len(l), nc + 5), device=x.device)
            v = np.zeros((len(l), nc + 5))
            v[:, :4] = l[:, 1:5]  # box
            v[:, 4] = 1.0  # conf
            v[range(len(l)), l[:, 0].long() + 5] = 1.0  # cls
            x = np.concatenate((x, v), 0)
        # If none remain process next image
        if not x.shape[0]:
            continue
        # Compute conf
        x[:, 5:] *= x[:, 4:5]  # conf = obj_conf * cls_conf
        # Box (center x, center y, width, height) to (x1, y1, x2, y2)
        box = xywh2xyxy(x[:, :4])
        # Detections matrix nx6 (xyxy, conf, cls)
        if multi_label:
            i, j = (x[:, 5:] > conf_thres).nonzero(as_tuple=False).T
            x = np.concatenate((box[i], x[i, j + 5, None], j[:, None].float()), 1)
        else:  # best class only
            # conf, j = x[:, 5:].max(1, keepdim=True)
            conf = x[:, 5:].max(1)
            j = np.argmax(x[:, 5:],1)
        conf=np.expand_dims(conf,axis=1)
        j=np.expand_dims(j,axis=1)
        x = np.concatenate((box, conf,j.astype(float) ), 1)[conf.reshape(-1) > conf_thres]
        # Filter by class
        if classes is not None:
            x = x[(x[:,5:6]==np.array(classes)).any(1)]
        # Check shape
        n = x.shape[0]  # number of boxes\
        if not n:  # no boxes
            continue
        elif n > max_nms:  # excess boxes
            x = x[x[:, 4].argsort(descending=True)[:max_nms]]  # sort by confidence
        # Batched NMS
        c = x[:, 5:6] * (0 if agnostic else max_wh)  # classes
        boxes, scores = x[:, :4] + c, x[:, 4]  # boxes (offset by class), scores
        # print(boxes,scores,iou_thres)
        nms_threshold=0.5
        i = cv2.dnn.NMSBoxes(boxes, scores, iou_thres,nms_threshold)  # NMS
        if i.shape[0] > max_det:  # limit detections
            i = i[:max_det]
        output[xi] = x[i]
        if (time.time() - t) > time_limit:
            break  # time limit exceeded
    
    return output

def FrameCapture(path):   
	if(path == "0" ):
		path = 0
	if(path=="1"):
		path=1
	vidObj = cv2.VideoCapture(path)
	# checks whether frames were extracted
	success=0
	count=1
	while not success:
	# vidObj object calls read
	# function extract frames
		success, image = vidObj.read()
		print("frame capture success : ", success)
		if (count%10==0):
			return ""
		count+=1

		try:
			image =  cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
			img = Image.fromarray(image.astype("uint8"))
			rawBytes = io.BytesIO()
			img.save(rawBytes, "JPEG")
			rawBytes.seek(0)
			img_base64 = b64encode(rawBytes.read())
		except:
			img_base64=""
	return str(img_base64.decode('utf-8'))

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

def orientation(p, q, r):
		val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
		if (val > 0):
			return 1
		elif (val < 0):
			return 2
		else:
			return 0

def onSegment(p, q, r):
	if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and
		(q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
		return True
	return False

def doIntersect(p1,p2,p3,p4):
	o1 = orientation(p1, p2, p3)
	o2 = orientation(p1, p2, p4)
	o3 = orientation(p3, p4, p1)
	o4 = orientation(p3, p4, p2)
	if ((o1 != o2) and (o3 != o4)):
		return True
	if ((o1 == 0) and onSegment(p1, p3, p2)):
		return True
	if ((o2 == 0) and onSegment(p1, p4, p2)):
		return True
	if ((o3 == 0) and onSegment(p3, p1, p4)):
		return True
	if ((o4 == 0) and onSegment(p3, p2, p4)):
		return True
	return False

def is_not_complex_quad(aoi_box):
	a1, a2, a3, a4 = aoi_box
	p1 = Point(a1["x"], a1["y"])
	p2 = Point(a2["x"], a2["y"])
	p3 = Point(a3["x"], a3["y"])
	p4 = Point(a4["x"], a4["y"])

	val1 = doIntersect(p1,p2,p3,p4)
	val2 = doIntersect(p1,p4,p2,p3)
	
	if val1 == False and val2 == False:
		return True
	else:
		return False