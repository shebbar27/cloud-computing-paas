from picamera import PiCamera
import time

FILE_EXTENSION = ".h264"
FIlE_PREFIX = "video_"

class Camera:
    def __init__(self, resultion, contrast, flipFrames = True):
        self.camera = PiCamera()
        self.camera.resolution = resultion  
        self.camera.vflip = flipFrames
        self.camera.contrast = contrast

    def capture_video(self, capture_duration, recordings_folder):
        file_name = FIlE_PREFIX + str(time.time()) + FILE_EXTENSION
        file_path = recordings_folder + file_name
        self.camera.start_recording(file_path)
        self.camera.wait_recording(capture_duration)
        self.camera.stop_recording()
        return file_name