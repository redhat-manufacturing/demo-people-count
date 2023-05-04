import cv2 
import os
from datetime import datetime
import time 
from streamer.utils.sys_colors import bcolors
class ReadVideo():
    def __init__(self,source):
        self.source =source
        self.stop_flag=False
        self._stream = cv2.VideoCapture(source)
        assert self._stream.isOpened(), f'Failed to open {source}'

        self._width = int(self._stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._fps= int(self._stream.get(cv2.CAP_PROP_FPS))
        self.count=0
        print(f"{bcolors.OKCYAN}VideaReader Initialized{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}height set to ", self._width,f"{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Width set to ", self._height,f"{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}FPS set to ", self._fps,f"{bcolors.ENDC}")
    
    def __iter__(self):
        return self

    def __next__(self):
        ret, frame = self._stream.read()
        if not ret or self.stop_flag:
            raise StopIteration
        self.count += 1
        if self.count%500==0:
            print(f"{bcolors.OKCYAN}Processed ",self.count, f" frames{bcolors.ENDC}")
        chunk_time = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
        return ret, frame, chunk_time

    def release(self):
        if self._stream is not None:
            self._stream.release()
            self.stop_flag=True
            self._stream = None

    def stop_chunking(self):
        self.stop_flag=True

    @property
    def config(self):
        """Returns information about the stream
        Returns:
            dict: a dictionary containing info regarding
            backend, source, width, height and fps.
        """
        self._config = {
            'backend': 'opencv',
            'source': self.source,
            'width': self._width,
            'height': self._height,
            'fps': self._fps
        }
        return self._config
