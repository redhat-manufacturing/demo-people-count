"""Contains class defintion of StreamChunker.
"""
import os
import shutil
import time
from threading import Thread, Lock, Event
import cv2 

from streamer.reader import VideoReader
from streamer.writer import VideoWriter
from streamer.utils.sys_colors import bcolors

import datetime 
from datetime import timedelta

class StreamChunker:
    """Read Live Stream and save them as chunks to be
    read later by the main thread. Use it if your pipeline's
    processing speed is significantly slower than input stream's FPS.
    It's an alternate to streamer.reader.VideoReaderThreaded, which saves
    streams frames in drive instead of RAM.
    """
    def __init__(self,
                 source,
                 width=None,
                 height=None,
                 fps=None,
                 pre_process=None,
                 save_pre_process=None,
                 skip_frames=1,
                 buffer_size=None,
                 chunk_size=5,
                 chunk_dir=None,
                 chunk_ext='mp4',
                 clean_chunks_before_exit=True,
                 clean_used_chunks=True,
                 wait_time=5,
                 restart_time=0,
                 force_decode=False,
                 picam=False):
        """Initiate Chunker
        Args:
            source (str): Path to video file or URL of video source/stream
            width (int, optional): Set Width of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.
            height (int, optional): Set Height of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.
            fps (int, optional): Set FPS of input stream,
            only works if source allows this setting.
            An error message will be shown if failed to set. Defaults to None.
            pre_process (function, optional): Function to be applied on the frame
            before returning it to user. Defaults to None.
            save_pre_process (function, optional): Function to be applied on the frame
            before chunks are saved. Can be used to optimize memory usage.
            Defaults to None.
            skip_frames (int, optional): Pick every nth frame and skip the n frames in
            between. Defaults to 1 means picking every frame.
            buffer_size (int, optional): Size of Buffer used by OpenCV, recommened
            to be set for USB Cams usage. Defaults to None.
            chunk_size (int, optional): Length of each chunk in seconds. Defaults to 5.
            chunk_dir (str, optional): Path to directory where chunks will be saved.
            Defaults to None, and in that case dir path is not given, a new directory
            derived from the stream name will be used.
            chunk_ext (str, optional): Extension of saved chunk vidoes. Defaults to 'mp4'.
            clean_chunks_before_exit (bool, optional): If True, then delete all the used/unused
            chunks before ending the process. Defaults to True.
            clean_used_chunks (bool, optional): delete chunk once it has been read by the main
            thread. Defaults to True.
            wait_time (int, optional): Amount of time (in seconds) to put the main thread to sleep
            in case there are no saved chunks left to read (i.e. stream chunkering thread is either
            failing to read from stream, restarting the stream, or simply running behind).
            Defaults to 5.
            restart_time (int, optional): Count of how many times Chunker should try to restart the
            stream in case of failiures (server-error, network-error, corrupted frames, etc.).
            Defaults to -1 means to always restart the stream.
            force_decode (bool, optional): Change decoding method to something universal,
            use it if you get multiple decoding error messages. Defaults to False.
            picam (bool, Optional): True if the input stream is from Pi Cam.
        Raises:
            Exception: Stream-Chunker Error, raised when it's failed to Start Chunker and the stream
            has already been restarted for the restart_time count
        """
        # picam bool
        self.__picam = picam

        # sanity init for del safety
        self.__stream_reader = None
        self.__last_reader = self.__stream_reader
        self.__chunk_reader = None
        self.__chunk_writer = None
        self.__clean_chunks_before_exit = clean_chunks_before_exit

        # chunk dir rename if live-stream or webcam
        if chunk_dir is None and (source.isnumeric()
                                  or source.startswith('rtsp')
                                  or source.startswith('http')):
            print(f'{bcolors.WARNING}[Stream-Chunker] Warning(0):',
                  f'No Chunk Dir name given for a live-stream/webcam source.',
                  f'Chunks will be saved at ./temp.{bcolors.ENDC}')
            chunk_dir = 'temp'

        self.__chunk_dir = chunk_dir if chunk_dir is not None \
            else f"{os.path.splitext(os.path.split(source)[1])[0]}_chunks"

        # init base video reader class
        self._stream_args = {
            'source': source,
            'pre_process': save_pre_process,
            'skip_frames': skip_frames,
            'buffer_size': buffer_size,
            'force_decode': force_decode,
            'fps': fps,
            'width': width,
            'height': height
        }
        print(self._stream_args)
        self.start_stream()
        print("chunker started stream")
        # if height is not None:
        #     self.__stream_reader.height = height
        # if width is not None:
        #     self.__stream_reader.width = width

        # chunk count
        self.__chunk_write_count = 0
        self.__chunk_read_count = 0
        self.__chunks_to_read = 0
        self.__chunk_size = chunk_size
        self.__chunk_ext = chunk_ext

        # chunk timestamp
        self.__chunks_timestamps= {}
        self.curr_time = None
        self.one_frame_eq_ms = 0

        # set props
        self.__clean_used_chunks = clean_used_chunks
        self.__count = 0
        self.__restart_time = restart_time
        self.__out_pre_process = pre_process

        # start thread to read from stream and write chunks
        self._stop_event = Event()
        self.__thread = Thread(target=self.__chunker, daemon=True)
        self.__lock = Lock()
        self.__thread.start()

        # set preprocessing if needed
        self.read_frame = self.__read_frame

        # set warnning counter.
        self.__warnnings = 0
        self.__wait_time = wait_time

        self.__current_chunk_name = None
        self.__chunk_frame_count=1

        # wait for first chunk to finish
        time.sleep(self.__wait_time)
        if self.__stream_reader is None and self.__chunks_to_read == 0:
            raise Exception(
                f'{bcolors.FAIL}Stream-Chunker Error: Failed to Start Chunker...{bcolors.ENDC}'
            )

        print(f'{bcolors.HEADER}[Stream-Chunker] Info:',
              f'Successfully started Chunker.{bcolors.ENDC}')

        # wait for first chunk to be finished
        if self.__chunks_to_read == 0:
            print(
                f'{bcolors.WARNING}[Stream-Chunker] Warning({self.__warnnings}):',
                f'First Chunk is still not ready. Putting main thread to sleep',
                f'for {self.__wait_time} seconds.{bcolors.ENDC}')
            time.sleep(self.__chunk_size)

    @property
    def height(self):
        """Returns height of stream
        Returns:
            int: height of stream
        """
        return self.__stream_reader.height if self.__stream_reader is not None else self.__last_reader.height

    @property
    def width(self):
        """Returns width of stream
        Returns:
            int: width of stream
        """
        return self.__stream_reader.width if self.__stream_reader is not None else self.__last_reader.width

    @property
    def fps(self):
        """Returns fps of stream
        Returns:
            int: fps of stream
        """
        return self.__stream_reader.fps if self.__stream_reader is not None else self.__last_reader.fps

    @property
    def count(self):
        """Returns number of frames already read
        Returns:
            count: number of frames read from stream so far
        """
        return self.__count

    @property
    def source(self):
        """Returns name/URL of stream
        Returns:
            str: name/ULR of the source stream
        """
        return self.__stream_reader.source if self.__stream_reader is not None else self.__last_reader.source

    @property
    def config(self):
        """Returns information about the stream
        Returns:
            dict: a dictionary containing info regarding
            backend, source, width, height and fps.
        """
        return self.__stream_reader.config if self.__stream_reader is not None else self.__last_reader.config

    @property
    def duration(self):
        """Returns number of seconds already read
        Returns:
            float: number of seconds read from stream so far
        """
        return self.__count / (self.__stream_reader.fps if self.__stream_reader
                               is not None else self.__last_reader.fps)

    @property
    def duration_minutes(self):
        """Returns number of minutes already read
        Returns:
            float: number of minutes read from stream so far
        """
        return self.duration / 60.

    @staticmethod
    def remove_dir(dname):
        """Delete Directory
        Args:
            dname (str): path of the directory to be deleted
        """
        if os.path.exists(dname):
            shutil.rmtree(dname)

    @staticmethod
    def remove_file(fname):
        """Delete File
        Args:
            fname (str): path of the file to be deleted
        """
        if os.path.exists(fname):
            os.remove(fname)

    @staticmethod
    def get_real_fps(source,num_frames=200):
        """
        To test out the real fps of the network stream only and to set fps based on that.
        num_frames is configurable
        """
        # Start default camera
        video = cv2.VideoCapture(source)

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

        # With webcam get(CV_CAP_PROP_FPS) does not work.
        # Let's see for ourselves.

        if int(major_ver)  < 3 :
            fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
            print("Frames per second without auto-set: {0}".format(fps))
        else :
            fps = video.get(cv2.CAP_PROP_FPS)
            print("Frames per second without auto-set : {0}".format(fps))

        # Number of frames to capture
        # num_frames = 50

        print("Capturing {0} frames to set real-time fps".format(num_frames))

        # Start time
        start = time.time()

        # Grab a few frames
        for i in range(0, num_frames) :
            ret, frame = video.read()

        # End time
        end = time.time()

        # Time elapsed
        seconds = end - start
        print ("Time taken : {0} seconds".format(seconds))

        # Calculate frames per second
        fps  = num_frames / seconds
        print ("Estimated frames per second : {0}".format(fps))
        int_fps= int(fps)
        print ("Considering FPS as {0}".format(int_fps))

        # Release video
        video.release()

        return int_fps

    def stop_chunking(self):
        self._stop_event.set()
        self.__thread.join()
        print(
                    f"{bcolors.OKGREEN}[Stream-Chunker] Info:",
                    f"Stopping the stream chunker Thread.{bcolors.ENDC}")
        self.__chunk_writer= None
        self.__stream_reader= None

    def start_stream(self):
        """Start/Restart the stream with the configurations given at
        StreamChunker initialization.
        """
        # check realtime fps and set fps based on that
        if not str(self._stream_args['source']).isnumeric() and self.__picam==False:
            real_fps= self.get_real_fps(self._stream_args['source']) 
        else:
            real_fps= self._stream_args['fps']
        # print(real_fps)
        if self.__picam:
            
            self.__stream_reader = PiCamReader(
                source=self._stream_args['source'],
                pre_process=self._stream_args['pre_process'],
                skip_frames=self._stream_args['skip_frames'],
                fps=real_fps,
                width=self._stream_args['width'],
                height=self._stream_args['height'])

        else:
            self.__stream_reader = VideoReader(
                source=self._stream_args['source'],
                pre_process=self._stream_args['pre_process'],
                skip_frames=self._stream_args['skip_frames'],
                buffer_size=self._stream_args['buffer_size'],
                force_decode=self._stream_args['force_decode'],
                fps=real_fps,
                width=self._stream_args['width'],
                height=self._stream_args['height'])

    def __create_writer(self):
        """Create a streamer.writer.VideoWriter object for
        writing a chunk of stream.
        Returns:
            VideoWriter: object to write a chunk to file system.
        """
        # save with start timestamp
        # current_time = datetime.datetime.now()

        try:
            if self.__chunk_write_count > 0:
                chunk_time = self.__chunks_timestamps[self.__chunk_write_count - 1]
                # chunk_name=chunk_name.strftime("%m%d%Y, %H")
                # chunk_timestamp_list = chunk_name.split('/')[1].split('_')[1].split('.')[0:2]
                # chunk_timestamp = chunk_timestamp_list[0]+'.'+chunk_timestamp_list[1]
                # chunk_time = datetime.datetime.strptime(chunk_timestamp, '%Y-%m-%d %H:%M:%S.%f')
                # delta = (1 / self.__chunk_reader.fps) * 1
                delta = self.__chunk_size
                current_time = chunk_time + timedelta(seconds=delta)
            else:
                current_time = datetime.datetime.now()

        except Exception as exp:
            print("Error in creating stream writer",exp)
            current_time = datetime.datetime.now()
        self.__chunks_timestamps[self.__chunk_write_count] = current_time
        fname = f"{self.__chunk_write_count}_{str(current_time)}.mp4"
        
        os.makedirs(self.__chunk_dir, exist_ok=True)
        if self.__picam:
            writer = PiCamWriter(source=self.__stream_reader,
                                 filename=fname,
                                 root_dir=self.__chunk_dir,
                                 ext=self.__chunk_ext,chunk_write=True)
        else:
            writer = VideoWriter(source=self.__stream_reader,
                                 filename=fname,
                                 root_dir=self.__chunk_dir,
                                 ext=self.__chunk_ext)

        # update chunk counter
        self.__chunk_write_count += 1

        return writer

    def __create_reader(self):
        """Create a streamer.reader.VideoReader object for
        read a saved chunk from the stream.
        Returns:
            VideoReader: object to read a chunk from the file system.
            self.__chunks_timestamps: dictionary of datetime.datetime.now objects which represent the start time of a chunk
        """
        print ("Reading from chunk")
        fname = f"{self.__chunk_read_count}_{self.__chunks_timestamps[self.__chunk_read_count]}.mp4"
        reader = VideoReader(source=os.path.join(self.__chunk_dir, fname),
                             pre_process=self.__out_pre_process)

        # update chunk counter
        self.__chunk_read_count += 1

        return reader, self.__chunks_timestamps[self.__chunk_read_count]

    def __chunker(self):
        """Read from live stream, and write chunks of videos in the file
        system that will be read by the main thread later. It also broadcasts
        the information of which chunks are ready to be read, and restarts the
        stream (if args given at initialization) in the case of failiure.
        """
        read_flag = False
        # try:
        for _, frame in self.__stream_reader:
            if self._stop_event.is_set():
                print(
                    f"{bcolors.OKGREEN}[Stream-Chunker] Info:",
                    f"Stopping the stream chunker Thread.{bcolors.ENDC}")
                return
            if (self.__stream_reader.duration % self.__chunk_size == 0
                    or self.__chunk_writer is None):
                if self.__chunk_writer is not None:
                    # close current writer
                    self.__chunk_writer.release()

                    # update counter of readable chunks
                    # number of chunks: read-write diff
                    self.__lock.acquire()
                    self.__chunks_to_read += 1
                    self.__lock.release()

                # start new stream
                self.__chunk_writer = self.__create_writer()

            # write frame
            self.__chunk_writer.write(frame)
            read_flag = True

            # nothing more to read; stream ended
            # pass

        # except Exception as error:
        #     # exception occured in reading from stream.
        #     print(error)

        # free resources
        # self.__stream_reader.release()
        # self.__chunk_writer.release()

        # self.__chunk_writer = None

        # number of chunks: read-write diff

        if self.__chunk_writer is not None:
            self.__chunk_writer.release()
            self.__chunk_writer = None

            if read_flag:
                self.__lock.acquire()
                self.__chunks_to_read += 1
                self.__lock.release()

        # release current
        self.__stream_reader.release()
        self.__last_reader = self.__stream_reader
        self.__stream_reader = None

        # restart streaming if needed
        if self.__restart_time != 0:

            # clean up
            self.__chunk_writer = None

            # incrm restart warnings
            self.__warnnings += 1
            print(
                f"{bcolors.WARNING}[Stream-Chunker] Warning({self.__warnnings}):",
                "Failed to Read from the Source Stream after.",
                f"Restarting the reader.{bcolors.ENDC}")

            # time.sleep(self.__wait_time)

            # restart
            restart_success_flag = False
            while self.__restart_time != 0:
                if self._stop_event.is_set():
                    print(
                        f"{bcolors.OKGREEN}[Stream-Chunker] Info:",
                        f"Stopping the stream chunker Thread.{bcolors.ENDC}")
                    return

                # decr restart count
                if self.__restart_time > 0:
                    self.__lock.acquire()
                    self.__restart_time -= 1
                    self.__lock.release()

                # try restart
                try:
                    self.start_stream()
                    restart_success_flag = True
                    print(f"{bcolors.OKGREEN}[Stream-Chunker] Info:",
                          f"Successfully Restarted the reader.{bcolors.ENDC}")
                    break
                except Exception as error:
                    self.__warnnings += 1
                    print(
                        f"{bcolors.FAIL}[Stream-Chunker] Error({self.__warnnings}):",
                        f"Failed to restart Stream Reader. {error}. Will Try Again in",
                        f"{self.__wait_time} seconds.{bcolors.ENDC}")
                    time.sleep(self.__wait_time)

            # start chunker again
            if restart_success_flag:
                self.__chunker()

    def __read_frame(self):
        """Read frame from available chunks which were saved in the file storage,
        and returns success flag and frame from chunks.
        Returns:
            tuple(bool, ndarray): flag denoting whether frame read was successful,
            and the latest frame read from the stream if flag is True else None.
        """
        # check for stream end
        if self.__chunk_reader is None and self.__chunks_to_read == 0 and self.__restart_time == 0 and self.__stream_reader is None:
            return False, None#,self.curr_time

        # initialize new reader of needed
        if self.__chunk_reader is None:

            # wait until there's chunk to read and stream is open
            while self.__chunks_to_read == 0 and self.__stream_reader is not None:
                self.__warnnings += 1
                print(
                    f"{bcolors.WARNING}[Stream-Chunker] Warning({self.__warnnings}):",
                    "All saved chunks already processed. Putting main thread to",
                    f"sleep for {self.__wait_time} seconds.{bcolors.ENDC}")
                time.sleep(self.__wait_time)

            # end stream; check needed to avoid
            # run conditions caused by threding
            if self.__stream_reader is None and self.__chunks_to_read == 0:
                return False, None#,self.curr_time

            # create new reader
            self.__chunk_reader, self.curr_time = self.__create_reader()

            # update counter of readable chunks
            # number of chunks: read-write diff
            self.__lock.acquire()
            self.__chunks_to_read -= 1
            self.__lock.release()

        ret, frame = self.__chunk_reader.read_frame()

        # # Micro seconds equivalent to one frame as per the fps
        # if self.one_frame_eq_ms ==0:
        #     self.one_frame_eq_ms = 1000000/self.__chunk_reader.fps
            
        # time_change = datetime.timedelta(microseconds=self.one_frame_eq_ms)
        
        # # add micro seconds difference to previous frame's time. 
        # self.curr_time = self.curr_time + time_change

        # free up current reader if needed
        if not ret:
            # remove used chunk
            if self.__clean_used_chunks:
                self.remove_file(self.__chunk_reader.source)

            # release reader
            self.__chunk_reader.release()
            self.__chunk_reader = None
            print(f'{bcolors.OKCYAN}[Stream-Chunker] Info:',
                  'Finised reading from current Chunk, switching',
                  f'to next chunk.{bcolors.ENDC}')
            return self.__read_frame()

        return ret, frame
        # , self.curr_time

    def __iter__(self):
        """Iterator for reading frames
        Returns:
            StreamChunker: can be used in next function or loops directly
        """

        return self

    def __next__(self):
        """Returns next flag and frame read from stream
        Raises:
            StopIteration: raised when there are no more frames to read or
            stream has stopped or frames are corrupted thus read method has failed.
        Returns:
            tuple(bool, ndarray): flag denoting whether frame read was successful,
            and the latest frame read from the stream if flag is True else None.
        """
        # ret, frame, curr_time = self.read_frame()
        ret, frame = self.read_frame()

        if not ret:
            raise StopIteration

        # incrm frame count
        self.__count += 1

        # get timestamp of current chunk
        chunk_name = self.__chunk_reader.source
        chunk_timestamp_list = chunk_name.split('/')[-1].split('_')[1].split('.')[0:2]
        chunk_timestamp = chunk_timestamp_list[0]+"."+chunk_timestamp_list[1]


        if self.__current_chunk_name is not None:
            self.__chunk_frame_count += 1
            if chunk_name != self.__current_chunk_name:
                self.__current_chunk_name = chunk_name
                self.__chunk_frame_count = 1
        else:
            self.__current_chunk_name = chunk_name
        
        chunk_time = datetime.datetime.strptime(chunk_timestamp, '%Y-%m-%d %H:%M:%S.%f')
        if self.__chunk_frame_count > 1:
            # delta = (1 / self.fps) * self.__chunk_frame_count
            delta = (1 / self.__chunk_reader.fps) * self.__chunk_frame_count

            chunk_time = chunk_time + timedelta(seconds=delta)
        return ret, frame, chunk_time
        # return ret, frame, curr_time

    def __del__(self):
        """Freeup resources and stream to avoid resource wastage and
        corruption of the stream. Deletes used/unused chunks if specified
        at the time of initialization.
        """
        self._stop_event.set()
        self.__thread.join()
        print(
            f'{bcolors.HEADER}[Stream-Chunker]: Releasing Resources.{bcolors.ENDC}'
        )
        # clean saved chunks
        if self.__clean_chunks_before_exit and self.__chunk_dir is not None:
            self.remove_dir(self.__chunk_dir)
            self.__chunk_dir = None

        # release stream reader if open
        if self.__stream_reader is not None:
            self.__stream_reader.release()
            self.__stream_reader = None

        # release chunk reader if open
        if self.__chunk_reader is not None:
            self.__chunk_reader.release()
            self.__chunk_reader = None

        # release chunk writer if open
        if self.__chunk_writer is not None:
            self.__chunk_writer.release()
            self.__chunk_writer = None

    def release(self):
        """Manually call del on the object to Freeup resources and
        stream to avoid resource wastage and corruption of the stream.
        """
        self.__del__()