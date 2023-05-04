import requests
import json
import time
from ml_api_functions import *
import unittest
# from config.config import Configuration
from datetime import datetime

headers = {
        'auth_token': "0",
        'sess_token': "5GQ0YlC3udC9yDdn"
    }

class unit_test_api(unittest.TestCase):
    def test_start_process(self):
        data = {
           "input":"q.mp4"
        }
        # Test start_process API with wrong auth_token
        w_headers = {
            'auth_token': "1",
            'sess_token': "5GQ0YlC3udC9yDdn"
        }
        resp = start_process(w_headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"224")

        # Test start_process API with no auth_token
        s_headers = {
            'auth_token': "0",
            'sess_token': "5GQ0YldC9yDdn"
        }
        resp = start_process(n_headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"441")

        # Test start_process API with no auth_token
        n_headers = {
            'sess_token': "5GQ0YlC3udC9yDdn"
        }
        resp = start_process(n_headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"223")

        #Testing start_process API with correct headers
        resp = start_process(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"100")


    def test_stop_process(self):
        data = {
        }
        #Testing stop_process API when a stream is being processed
        resp = stop_process(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"100")

        #Testing stop_process API when no stream is being processed
        time.sleep(120)
        resp = stop_process(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"111")

    def test_stream_status(self):
        data = {
        }
        #Testing stream status APi when no stream is being processed
        resp = stream_status(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"101")

         #Testing stream status APi when a stream is being processed
        resp = stream_status(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"102")

    def test_stop_stream(self):
        data = {
        }
        #Testing Stop stream API when no stream is being processed
        resp = stop_streaming(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"111")

        #Testing Stop stream API when Stream is stopped but processing is active
        resp = stop_streaming(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"112")

    def test_update_env(self):
        data = {
            "START":0,
            "STOP":10
        }
        resp = update_env(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],"100")

    def test_get_frame(self):
        data = {
           "input":"nike.mp4"
        }
        resp = get_frame(headers,data)
        self.assertIsNotNone(resp)
        self.assertEqual(resp["status_code"],100)


if __name__ == '__main__':
    unit_test_api.main()

