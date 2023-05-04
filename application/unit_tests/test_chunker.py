from streamer import StreamChunker, VideoWriter

source = '/home/akash/unit_testing/apparel_logo_microservices/ml_service/application/streamer/nike.mp4'
#declaring an object of class StreamChunker

output = "output.mp4"

print("Testing StreamChunker...")
#Testing methods of StreamChunker class
p = StreamChunker(source, chunk_size=5, chunk_dir='temp_chunks', fps=10,restart_time=-1,width=1280,height=720)

# test public method of class StreamChunker get_real_fps
r_fps = p.get_real_fps(source)
assert r_fps is not None

# test public method of class StreamChunker stop_chunking
r_stop_chunk = p.stop_chunking()

# test public method of class StreamChunker start_stream
r_start_stream = p.start_stream()

# test private method of class StreamChunker __Create_writer
r_c_writer = p._StreamChunker__create_writer

# test private method of class StreamChunker __create_reader
r_create_reader = p._StreamChunker__create_reader

# test private method of class StreamChunker __chunker
r_chunker = p._StreamChunker__chunker

# test private method of class StreamChunker __read_frame
p_r = p._StreamChunker__read_frame

#Checking methods of VideoWriter class
print("Testing VideoWriter...")
w = VideoWriter(p, filename=output, fps=r_fps)

# w_writer = w.write(p_r)

w_rel = w.release()