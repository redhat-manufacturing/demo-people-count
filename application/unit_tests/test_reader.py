import cv2
from streamer import VideoReader, VideoWriter

source = '/home/akash/unit_testing/apparel_logo_microservices/ml_service/application/streamer/nike.mp4'

print("Testing VideoReader...")
#Testing methods of VideoReader class
r = VideoReader(source,pre_process=None)

# Testing start stream method
r_sstream = r.start_stream()

#Testing set_config method
new_width = 640
r_config = r._set_config("width",new_width,cv2.CAP_PROP_FRAME_WIDTH)
assert r.width==640

#Testing read_frame method
r_read = r._read_frame()

#Testing __next__ method
r.__next__
# assert r.count == old_c + 1
