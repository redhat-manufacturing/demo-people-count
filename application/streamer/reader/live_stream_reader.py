from threading import Thread
from collections import deque
import time

import cv2

from .video_reader import VideoReader

class LiveStreamReader(VideoReader):
    def __init__(self, source, pre_process=None, skip_frame=None, wait_time=2):
        
        # init base video reader class
        super().__init__(source=source, pre_process=pre_process)
        
        # buffer(queue) to keep frames from live-stream
        self.__frames = deque()

        # check skip frame isn't 0
        assert skip_frame is None or skip_frame>0, 'Skip Frame cannot be less than 1'

        # guarantee first frame
        ret, frame = self._stream.read()  
        assert ret, f'Failed to Read from {source}'
        self.__frames.append(frame)

        # start thread to read from stream
        self.__thread = Thread(target=self.__read_from_stream, daemon=True)
        self.__thread.start()

        # set wait time to sleep when queue is empty
        self.__wait_time = wait_time

        # set warnning counter. 
        self.__warnnings = 0

        # wait for frame queue to get filled. 
        time.sleep(self.__wait_time)

    def _read_frame(self):
        while len(self.__frames)==0 and self._stream is not None:
            self.__warnnings +=1
            print(f'Warnning({self.__warnnings}): Frame Queue is Empty, putting main thread to sleep.')
            time.sleep(self.__wait_time)

        if self._stream is None and len(self.__frames)==0:
            return False, None
        
        self._count +=1
        return True, self.__frames.popleft()

    def __read_from_stream(self):
        while True:
            ret, frame = self._stream.read()
            if not ret:
                break
            self.__frames.append(frame)
        self._stream.release()
        self._stream = None
        print(f'Finished Reading Frames from {self.source} Stream.')

