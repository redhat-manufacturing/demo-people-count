from pipeline import Pipeline
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-stream_input','--stream_input')
parser.add_argument('-stream_fps','--stream_fps')
parser.add_argument('-stream_height','--stream_height')
parser.add_argument('-stream_width','--stream_width')
parser.add_argument('-stream_output','--stream_output')

parser_info= parser.parse_args()

pipe= Pipeline()

print("\npipeline test fps", parser_info.stream_fps)
pipe.run(source=parser_info.stream_input,
        fps=parser_info.stream_fps,
        width= parser_info.stream_width,
        height= parser_info.stream_height,
        output=parser_info.stream_output,
        frames_test=5
        )