from config import Config
import unittest
from pipeline import Pipeline
from object_detection import ObjectDetection,ObjectTracking,Utilities
import numpy as np


source = '/home/akash/akash_people_count_monolith/people-count-monolith-podman/q.mp4'

class unit_test_usecase(unittest.TestCase):
    def test_pipeline(self,num_frames_test=60,chunk_size=3):
        pipe = Pipeline()
        pipe.run(source=source,
            frames_test=num_frames_test
        )
        # ground_dict = {}
        # for i in range(0,num_frames_test,chunk_size):
        #     ground_dict[i]=4
        # print(ground_dict)
        ground_dict = {0: 4, 3: 4, 6: 4, 9: 4, 12: 4, 15: 4, 18: 4, 21: 4, 24: 4, 27: 4, 30: 4, 33: 4, 36: 4, 39: 4, 42: 4, 45: 4, 48: 4, 51: 5, 54: 5, 57: 5} #Ground truth dictionary having number of people present in each frame with frame number as key
        data = pipe.pc_dict
        # print("Data: ",data)
        if data:
            for curr_frame in range(0,num_frames_test,chunk_size):
                self.assertEqual(data[curr_frame]['people_count']['head_count'],ground_dict[curr_frame]) # Testing if head count for 'n' frames is same
                self.assertEqual(data[curr_frame]['people_count']['head_count'],len(data[0]['tracker IDS'])) # Testing if number of people are equal as number of tracking IDS
                self.assertGreater(data[curr_frame]['people_count']['head_count'],-1) 
                self.assertGreater(data[curr_frame]['people_count']['enter'],-1)
                self.assertGreater(data[curr_frame]['people_count']['leave'],-1)


if __name__ == '__main__':
    unit_test_usecase.main()
