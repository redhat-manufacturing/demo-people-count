import os
import cv2
import subprocess
import requests
import time
import signal
from datetime import datetime
from dotenv import *
import secrets
import base64
load_dotenv(override=True)
import json
from flask import make_response
from pickle import FRAME
from flask_cors import cross_origin
from flask import  request, jsonify
from flask import render_template, session, redirect, url_for, flash, request
import sys
from config import Config as conf
from pathlib import Path
from utils.utils import *
from . import app,DB
from utils.authenticate import token_required
from utils.logs import logger
from utils.utils import *
from lib_rlm.rlm import validate_license
from dashboard import DashboardData

PROCESS_STATE=None
STREAM_OUTPUT=''
STREAM_INPUT=''
NEW_DAY_STREAM='not started'
STREAM_STATUS="NOT_STOPPED"
LAST_START_HIT=''
CHUNK_DIR='application/temp_chunks'
MSG_DICT=read_msg_json()

IMG_WIDTH=1280
IMG_HEIGHT=720
FRAME_INPUT=''

@app.route("/")
def home():
	return app.send_static_file('index.html')

@app.route('/dashboard')
def dashboard_():
    return app.send_static_file('index.html')

@app.route('/pipeline')
def pipeline_():
	return app.send_static_file('index.html')

@app.route('/camera-angle')
def camera_angle():
	return app.send_static_file('index.html')

@app.route('/status')
def status():
	return app.send_static_file('index.html')

@app.route('/settings')
def settings_():
	return app.send_static_file('index.html')

@app.route('/lor')
def roi():
	return app.send_static_file('index.html')

def save_logs(dat,api_name):
	dat_copy = {}
	dat_copy['request'] = api_name
	dat_copy['status_code'] = dat['status_code']
	dat_copy['timestamp'] = dat['timestamp']
	dat_copy['msg'] = dat['msg']

	try:
		conn2 = DB.create_connection(DB.DBFILE)
		DB.insert_data(conn2,dat_copy,dat_copy['timestamp'],DB.LOG_TABLE,encode=True)
	except Exception as e:
		print("error:failed to save logs: ",e)

@app.after_request
def add_header(req):
    """
    Add headers to both force latest IE rendering or Chrome Frame,
    and also to cache the rendered page for 10 minutes
    """
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers["Cache-Control"] = "public, max-age=0"
    return req

@app.route("/dashboard_data", methods=["GET"])
@token_required
def dashboard_data():
	logger.info('/get_dashboard_data')
	try:
		dash_data = DashboardData()
		stats_output = dash_data.output()
		dat = {"msg":MSG_DICT["dashboard_data"]["225"],"status_code":"225","data":stats_output,"timestamp": str(datetime.now())}
	except Exception as e:
		print(e)
		dat ={"msg":"Fail to retrive dashboard data","data":None,"status_code":"226","timestamp": str(datetime.now())}
	return jsonify(dat)

@app.route("/start_process", methods=["POST"])
@token_required
def start_process():
	logger.info(":/start_process")
	#use global keyword to make sure you are referencing the global variable
	global PROCESS_STATE
	global STREAM_OUTPUT
	global STREAM_INPUT
	global STREAM_STATUS
	global LAST_START_HIT
	global IMG_HEIGHT
	global IMG_WIDTH
	
	
	if 'input' in request.form:
		STREAM_INPUT=request.form['input']
	else:
		STREAM_INPUT="nike.mp4"

	if('fps' in request.form):
		stream_fps=int(request.form['fps'])
	else:
		stream_fps=10
	if('height' in request.form):
		IMG_HEIGHT=int(request.form['height'])
	else:
		IMG_HEIGHT=720
	if('width' in request.form):
		IMG_WIDTH=int(request.form['width'])
	else:
		IMG_WIDTH=1280
	if('output' in request.form):
		STREAM_OUTPUT=request.form['output']
		if(STREAM_OUTPUT==""):
			STREAM_OUTPUT = "output.mp4"
	else:
		STREAM_OUTPUT='output.mp4'

	if(PROCESS_STATE is not None and PROCESS_STATE.poll() is None):
			dat = {"msg": MSG_DICT["start_process"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
	else:
		#test it
		test=subprocess.Popen(['python3','application/pipeline_test.py','-stream_input',STREAM_INPUT,'-stream_output',STREAM_OUTPUT,'-stream_fps',str(stream_fps),'-stream_width',str(IMG_WIDTH),'-stream_height',str(IMG_HEIGHT)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		out,err=test.communicate()
		if(test.returncode==0):
			l=['python3','application/pipeline.py','--source',STREAM_INPUT,'--output',STREAM_OUTPUT, '--fps',str(stream_fps),'--height',str(IMG_HEIGHT),'--width',str(IMG_WIDTH),]
			if(PROCESS_STATE is not None and PROCESS_STATE.poll() is None):
				dat = {"msg": MSG_DICT["start_process"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
			else:
				STREAM_STATUS='NOT_STOPPED'
				LAST_START_HIT=str(datetime.now())
				PROCESS_STATE=subprocess.Popen(l)
				
				if(PROCESS_STATE is not None and PROCESS_STATE.poll() is None):
					time.sleep(20.0)
					dat = {"msg": MSG_DICT["start_process"]["100"], "status_code": "100", "timestamp": str(datetime.now())}
				else:
					dat = {"msg": MSG_DICT["start_process"]["110"], "status_code": "110", "timestamp": str(datetime.now())}
		else:
			print(err.decode('utf-8').strip())
			dat = {"msg": MSG_DICT["start_process"]["110"], "status_code": "110", "timestamp": str(datetime.now())}

	save_logs(dat,"start_process")
	return jsonify(dat)

@app.route("/stream_status", methods=["GET"])
@token_required
def status_stream():
	logger.info("/stream_status")
	global PROCESS_STATE
	global STREAM_INPUT
	global STREAM_STATUS
	global LAST_START_HIT
	load_dotenv(override=True)
	
	size=0
	Folderpath=CHUNK_DIR #size of temp chink folder
	if(os.path.exists(Folderpath)):
		for ele in os.scandir(Folderpath):
			size+=os.path.getsize(ele)
	try:
		RET_STREAM_INPUT = STREAM_INPUT.split("/")[-1]
		if(PROCESS_STATE is not None and PROCESS_STATE.poll() is None):
			if(STREAM_STATUS=='STOPPED'):
				dat = {"msg": MSG_DICT["stream_status"]["103"], "status_code": "103","camera_source":RET_STREAM_INPUT,"timestamp": str(datetime.now())}
			else:
				dat = {"msg": MSG_DICT["stream_status"]["102"], "status_code": "102","camera_source":RET_STREAM_INPUT,"timestamp": str(datetime.now())}
		elif(PROCESS_STATE is None or PROCESS_STATE.returncode==0):
			dat = {"msg": MSG_DICT["stream_status"]["101"], "status_code": "101","camera_source":'N/A',"timestamp": str(datetime.now())}
		elif(PROCESS_STATE is not None and STREAM_STATUS=='STOPPED'):
			dat = {"msg": MSG_DICT["stream_status"]["101"], "status_code": "101","camera_source":'N/A',"timestamp": str(datetime.now())}
		else:
			dat = {"msg": MSG_DICT["stream_status"]["110"],"status_code" : "110","camera_source":'N/A' ,"timestamp": str(datetime.now())}
	except Exception as e:
		print(e)
		dat = {"msg": MSG_DICT["stream_status"]["110"],"status_code" : "110" ,"camera_source":'N/A',"timestamp": str(datetime.now())}

	save_logs(dat,"stream_status")
	return jsonify(dat)

@app.route("/get_inp_stream", methods=["POST"])
@token_required
def get_input_stream():
	global STREAM_INPUT
	global NEW_DAY_STREAM
	if(STREAM_INPUT!=''):
		NEW_DAY_STREAM='started'
	return jsonify({'inp':STREAM_INPUT})

@app.route("/chk_new_day", methods=["POST"])
def chk_new_day():
	global NEW_DAY_STREAM
	return jsonify({'status':NEW_DAY_STREAM})


@app.route("/stop_process", methods=["POST"])
@token_required
def stop_process():
	logger.info("/stop_process")
	global PROCESS_STATE
	global STREAM_OUTPUT
	
	flag_msg = False
	if PROCESS_STATE is None:
		dat = {"msg": MSG_DICT["stop_process"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
		flag_msg = True

	elif(PROCESS_STATE.returncode==0 and flag_msg == False):
		PROCESS_STATE=None
		dat = {"msg": MSG_DICT["stop_process"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
		flag_msg = True
	
	if (flag_msg == False):
		PROCESS_STATE.send_signal(signal.SIGINT)
		PROCESS_STATE=None
		if(STREAM_OUTPUT==''):
			dat = {"msg": MSG_DICT["stop_process"]["100"], "status_code": "100", "timestamp": str(datetime.now())}
		else:
			dat = {"msg": MSG_DICT["stop_process"]["100"], "status_code": "100", "timestamp": str(datetime.now())}


	save_logs(dat,"stop_process")
	return jsonify(dat)


@app.route("/stop_streaming", methods=["POST"])
@token_required
def stop_streaming():
	logger.info("/stop_streaming")
	global PROCESS_STATE
	global STREAM_STATUS
	
	flag_msg = False
	if PROCESS_STATE is None and flag_msg == False:
		dat = {"msg": MSG_DICT["stop_streaming"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
		flag_msg = True

	elif(PROCESS_STATE.returncode==0 and flag_msg == False):
		PROCESS_STATE=None
		dat = {"msg": MSG_DICT["stop_streaming"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
		flag_msg = True

	elif(PROCESS_STATE is not None and PROCESS_STATE.poll() is None and flag_msg == False):
			if(STREAM_STATUS=='STOPPED'):
				dat = {"msg": MSG_DICT["stop_streaming"]["112"], "status_code": "112", "timestamp": str(datetime.now())}
				flag_msg = True

	elif(PROCESS_STATE is not None and STREAM_STATUS=='STOPPED' and flag_msg == False):
		dat = {"msg": MSG_DICT["stop_streaming"]["111"], "status_code": "111", "timestamp": str(datetime.now())}
		flag_msg = True

	else:
		dat = {"msg": MSG_DICT["stop_streaming"]["111"], "status_code": "111", "timestamp": str(datetime.now())}

	if(flag_msg == False):
		PROCESS_STATE.send_signal(signal.SIGUSR1)
		# PROCESS_STATE=None
		STREAM_STATUS='STOPPED'
		dat = {"msg": MSG_DICT["stop_streaming"]["101"], "status_code": "101", "timestamp": str(datetime.now())}
		flag_msg = True

	save_logs(dat,"stop_streaming")
	return jsonify(dat)

@app.route("/get_roi", methods=["POST"])
@token_required
def get_lor():
	logger.info("/get_lor")
	global IMG_HEIGHT
	global IMG_WIDTH
	config_data = read_config_json()
	y=config_data["ref_line_start"][1]
	data={
		"data":[]
	}

	data["data"].append({
		"h":IMG_HEIGHT,
		"w":IMG_WIDTH,
		"y":int(y),
	})

	return jsonify({
		    "msg":"Retrieved LOR data",
			"coords": data["data"],
			"status_code": 100,
			"timestamp": str(datetime.now())
	})


@app.route("/set_roi", methods=["POST"])
@token_required
def set_lor():
	logger.info("/set_lor")
	global IMG_HEIGHT
	global IMG_WIDTH

	data = eval(request.form['data'])
	box=[]
	box.append([0,data[0]['y']])
	box.append([IMG_WIDTH,data[0]['y']])
	
	if PROCESS_STATE != None:
		ip=os.getenv('SIP')
		port=os.getenv('SPORT')
		url='http://'+str(ip)+':'+str(port)+'/stop_process'#if a process is running then it will stopped and after updation a fresh server will be started
		headers={
			'auth_token':request.headers['auth_token'],
			'sess_token':request.headers['sess_token']
			}
		r_chk=requests.post(url,data={},headers=headers)
	
	write_config_json(box[0],'ref_line_start')
	write_config_json(box[1],'ref_line_end')

	config_data = read_config_json()
	y=config_data["ref_line_start"][1]
	data={
		"data":[]
	}

	data["data"].append({
		"h":IMG_HEIGHT,
		"w":IMG_WIDTH,
		"y":int(y),
	})

	dat =  {
		"msg": MSG_DICT["set_roi"]["100"],
		"coords": data["data"],
		"height": IMG_HEIGHT,
		"width": IMG_WIDTH,
		"status_code":100,
		"timestamp": str(datetime.now())
	}
	save_logs(dat,"set_roi")
	return jsonify(dat)

@app.route("/update_env", methods=["POST"])
@token_required
def env_update():
	logger.info("/update_env")
	load_dotenv(override=True)
	dotenv_file = find_dotenv()
	print(request.form)
	if "START" in request.form:
		os.environ['START']=request.form['START']
		set_key(dotenv_file, "START", os.environ["START"])
	if "END" in request.form:
		os.environ['END']=request.form['END']
		set_key(dotenv_file, "END", os.environ["END"])
	
	if "DET_THRESH" in request.form:
		write_config_json(float(request.form['DET_THRESH_PERSON']),'det_thresh_person')
	
	if "SAVE_VIDEO" in request.form:
		if(request.form['SAVE_VIDEO']=='false' or request.form['SAVE_VIDEO']=='False' or request.form==False):
			save_video=False
		else:
			save_video=True
		write_config_json(save_video,'save_video')

	ip=os.getenv('SIP')
	port=os.getenv('SPORT')
	url='http://'+str(ip)+':'+str(port)+'/stop_process'
	headers={
		'auth_token':request.headers['auth_token'],
		'sess_token':request.headers['sess_token']
	}
	r_chk=requests.post(url,data={},headers=headers)

	dat = {"msg": MSG_DICT["update_env"]["100"],"status_code": "100", "timestamp": str(datetime.now())}
	save_logs(dat,'update_env')

	return jsonify(dat)


@app.route("/give_curr_settings", methods=["GET"])
@token_required
def curr_settings():
	logger.info("/give_curr_settings")
	load_dotenv(override=True)
	start=os.getenv('START')
	end=os.getenv('END')
	data=read_config_json()
	det_thresh=data['det_confidence_threshold']
	save_vid=data['save_video']
	return jsonify({'START':start,"END":end,"DET_THRESH":det_thresh,"SAVE_VIDEO":save_vid})

@app.route("/get_frame", methods=["POST"])
@token_required
def get_frame():
	logger.info("/get_frame")
	global FRAME_INPUT
	global STREAM_INPUT
	
	no_stream_flag = False
	if 'input' in request.form:
		FRAME_INPUT=request.form['input']
		
		if STREAM_INPUT!='' and request.form['input']=='':
			FRAME_INPUT=STREAM_INPUT

	if STREAM_INPUT=='' and FRAME_INPUT=='':
		dat = {"msg": MSG_DICT["get_frame"]["111"], "status_code": 111, "timestamp": str(datetime.now())}
		no_stream_flag=True

	if not no_stream_flag:
		print("\n FRAME INPUT:", FRAME_INPUT)
		data=FrameCapture(FRAME_INPUT)

		if(len(data)==0):
			status_code = 110
			msg= MSG_DICT["get_frame"]["110"]
		else:
			status_code = 100
			msg= MSG_DICT["get_frame"]["100"]

		dat =  {
				"frame": str(data),
				"status_code": status_code,
				"msg": msg,
				"timestamp": str(datetime.now())
			}

	save_logs(dat,"get_frame")
	return jsonify(dat)

@app.route("/logs", methods=["GET"])
@token_required
def fetch_logs(): 
	logger.info("/logs")
	try:
		conn = DB.create_connection(DB.DBFILE)
		rd=DB.get_data(conn,DB.LOG_TABLE)
		dat ={"msg":MSG_DICT["save_logs"]["225"],"status_code":"225","logs":rd,"timestamp": str(datetime.now())}
		return jsonify(dat)
	except Exception as e:
		logger.info("routes.py : Unable to fetch logs."+ str(e))
		dat ={"msg":MSG_DICT["save_logs"]["226"],"status_code":"226","logs":{},"timestamp": str(datetime.now())}
		return jsonify(dat)

@app.route("/data_fetch", methods=["GET"])
@token_required
def data_fetch(): 
	logger.info("/data_fetch")
	try:
		conn = DB.create_connection(DB.DBFILE)
		rd=DB.get_data(conn,DB.TABLE)
		dat ={"msg":MSG_DICT["data_fetch"]["100"],"status_code":"100","data":rd,"timestamp": str(datetime.now())}
		return jsonify(dat)
	except Exception as e:
		logger.info("Unable to fetch data."+ str(e))
		dat ={"msg":MSG_DICT["data_fetch"]["110"],"status_code":"110","data":{},"timestamp": str(datetime.now())}
		return jsonify(dat)


@app.route("/activate_license", methods=["POST"])
def activate_license_rlm():
	logger.info("/activate_license")
	global ACTIVATE_LICENSE
	if "ACTIVATION_KEY" in request.form:
		act_key=request.form['ACTIVATION_KEY']
		try:
			data_dict=read_env_json()
			ACTIVATE_LICENSE=bool(data_dict['ACTIVATE_LICENSE'])
			if(ACTIVATE_LICENSE==False):
				act = validate_license(act_key)
				print("act:",act)
				if(act!=-1):
					AUTH_TOKEN=secrets.token_urlsafe(20)#generate auth token
					encoded_token = base64.urlsafe_b64encode(AUTH_TOKEN.encode()).decode()
					ACTIVATE_LICENSE=True
					write_env_json(["AUTH_TOKEN","ACTIVATE_LICENSE"],[encoded_token,bool(ACTIVATE_LICENSE)])
					dat = {"msg": MSG_DICT["activate_license"]["220"],"auth_token":AUTH_TOKEN.strip(), "status_code": "220", "timestamp": str(datetime.now())}	
				else:
					dat = {"msg": MSG_DICT["activate_license"]["221"], "status_code": "221", "timestamp": str(datetime.now())}
			else:
				dat = {"msg": MSG_DICT["activate_license"]["222"], "status_code": "222", "timestamp": str(datetime.now())}

		except Exception as err:
			print("Error: ",err)
			dat = {"msg": MSG_DICT["activate_license"]["221"], "status_code": "221", "timestamp": str(datetime.now())}
	else:
		dat = {"msg": MSG_DICT["activate_license"]["225"], "status_code": "225", "timestamp": str(datetime.now())}
	return jsonify(dat)

@app.route("/give_usecase", methods=["POST"])
def usecase_give():
	logger.info("/give_usecase")
	if "auth_token" in request.form:
		api_auth_token=request.form['auth_token']
	else:
		return jsonify({"msg": 'Please enter the auth token to proceed', "status_code": "223", "timestamp": str(datetime.now())})
	
	if "sess_token" in request.headers:
		api_sess_token=request.headers['sess_token']
		SESSION_TOKEN = api_sess_token
	else:
		return jsonify({"msg": "session token is missing", "status_code": "234", "timestamp": str(datetime.now())})
	
	data_dict=read_env_json()
	AUTH_TOKEN=base64.urlsafe_b64decode(data_dict['AUTH_TOKEN'].encode()).decode()
	
	if(AUTH_TOKEN!='' and api_auth_token==AUTH_TOKEN):
		if(SESSION_TOKEN!='' and api_sess_token==SESSION_TOKEN):
			use_case_l=['people-count']
			write_sess_json(["SESS_TOKEN"],[SESSION_TOKEN])	
			return jsonify({"use_case":use_case_l,"status_code":"100","timestamp": str(datetime.now())})
		else:
			return make_response(jsonify({"msg": "A valid auth token is missing!"}), 401)	
	else:
		return jsonify({"msg": "Please enter the correct auth token to proceed.", "status_code": "224", "timestamp": str(datetime.now())})