import requests
import json
from dotenv import *
import os
load_dotenv(override=True)

def start_process(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/start_process'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/start_process'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("start_process - unable to send request to db_service: "+str(e))
    order = response.json()
    print("login::",order)
    return order

def stream_status(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/stream_status'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/stream_status'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("stream_status - unable to send request to db_service: "+str(e))
    order = response.json()
    print("stream status::",order)
    return order

def get_inp_stream(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/get_inp_stream'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/get_inp_stream'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("get_inp_stream - unable to send request to db_service: "+str(e))
    order = response.json()
    # print("input stream::",order)
    return order

def chk_new_day(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/chk_new_day'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/chk_new_day'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("check new day- unable to send request to db_service: "+str(e))
    order = response.json()
    print("check new day::",order)
    return order

def stop_process(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/stop_process'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/stop_process'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("Stop process- unable to send request to db_service: "+str(e))
    order = response.json()
    # print("stop process::",order)
    return order

def stop_streaming(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/stop_streaming'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/stop_streaming'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("Stop Stream- unable to send request to db_service: "+str(e))
    order = response.json()
    # print("stop streaming::",order)
    return order

def update_env(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/update_env'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/update_env'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("update env- unable to send request to db_service: "+str(e))
    order = response.json()
    # print("update env::",order)
    return order

def give_curr_settings(headers):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/give_curr_settings'
        response = requests.request(method="GET", url=url,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/give_curr_settings'
            response = requests.request(method="GET", url=url,headers=headers)
        except Exception as e:
            print("give current settings - unable to send request to db_service: "+str(e))
    order = response.json()
    print("give current settings::",order)
    return order

def get_frame(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/get_frame'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/get_frame'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("Get frames- unable to send request to db_service: "+str(e))
    order = response.json()
    # print("get current frame::",order)
    return order


def save_first_frame(headers,data):
    
    try:
        url = f'http://127.0.0.1:{os.environ["SPORT"]}/save_first_frame'
        response = requests.request(method="POST", url=url,data=data,headers=headers)
    except Exception as e:
        print(e)
        try:
            url = f'http://people_count:{os.environ["SPORT"]}/save_first_frame'
            response = requests.request(method="POST", url=url,data=data,headers=headers)
        except Exception as e:
            print("Save first frame- unable to send request to db_service: "+str(e))
    order = response.json()
    # print("Save first frame::",order)
    return order

