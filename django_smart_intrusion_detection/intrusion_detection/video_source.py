from threading import Thread
import time
import cv2, numpy as np

class MultiVideoSourceFile(object):
    def __init__(self, video_paths=[]):
        self.video_paths = video_paths
        self.videos = [cv2.VideoCapture(path) for path in video_paths]
    
    def __del__(self):
        for vid in self.videos:
            vid.release()
            
    def multi_stream(self, repeat=True):
        frames = []
        for i, vid in enumerate(self.videos):
            ret, frame = vid.read()
            if not ret and repeat:
                self.videos[i] = cv2.VideoCapture(self.video_paths[i])
                ret, frame = self.videos[i].read()
            
            frames.append(cv2.imencode('.jpg', frame)[1])
        return frames
                 

class VideoSourceFile(object):
    def __init__(self, video_path='/home/kevin/django-vue-stream/smartdetectoralarm/out.mkv', read_all_frames=False, postprocessors=[lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)]):
        print('video_path:', video_path)
        self.video = cv2.VideoCapture(video_path)
        self.postprocessors = postprocessors
        self.frames = [np.zeros((640,640,3))]
        self.frame_index = 0
        if read_all_frames:    
            print('getting frames...')
            while True:
                success, image = self.video.read()
                if not success:
                    print('finish get frames')
                    break
                self.frames.append(image)
            self.get_frame = self.get_stored_frame
        else:
            self.video_path = video_path
            self.get_frame = self.get_live_frame
            
    def __del__(self):
        self.video.release()
    
    def get_stored_frame(self, postprocessor_index=0):
        image = self.frames[self.frame_index]
        image = self.postprocessors[postprocessor_index](image)
        ret, jpeg = cv2.imencode('.jpg', image)
        self.frame_index+=1
        if self.frame_index==len(self.frames):
            self.frame_index = 0
        return jpeg.tobytes()

    def get_live_frame(self, repeat=True, postprocessor_index=0, store=True):
        success, image = self.video.read()
        if not success:
            if repeat:
                self.video = cv2.VideoCapture(self.video_path)
                return self.get_live_frame(repeat)
            else:
                return False
        if store:
            self.frames = [image]
        return cv2.imencode('.jpg', self.postprocessors[postprocessor_index](image))[1].tobytes()

class SimulatedVideoSourceFile(object):
    def __init__(self, video_path='/home/kevin/django-vue-stream/smartdetectoralarm/out.mkv', fps=30, max_live_frame_stack=2, postprocessors=[lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)]):
        print('video_path:', video_path)
        self.postprocessors = postprocessors
        self.frame_index = 0
        self.video_path = video_path
        self.fps = fps
        self.max_live_frame_stack = max_live_frame_stack
        self.is_live_simulation_running = False
        self.is_live_simulation_stopped = False
        self.live_frames = [None]*max_live_frame_stack
        self.live_frame_index = 0
        Thread(target=self.simulate_live_video, args=[]).start()
    
    def __del__(self):
        self.is_live_simulation_running=False
        while not self.is_live_simulation_stopped:
            time.sleep(0.1)
        self.video.release()

    def simulate_live_video(self):
        self.video = cv2.VideoCapture(self.video_path)
        self.is_live_simulation_stopped = False
        self.is_live_simulation_running = True
        while self.is_live_simulation_running:
            success, image = self.video.read()    
            if not success:
                self.video = cv2.VideoCapture(self.video_path)
                success, image = self.video.read()    
            if not success:
                raise RuntimeError(f'Even after the video reinitialized, still cannot get the frame: {self.video_path}')
            self.live_frames[self.live_frame_index] = image
            self.live_frame_index += 1
            if self.live_frame_index==self.max_live_frame_stack:
                self.live_frame_index = 0
            time.sleep(1.0/self.fps)
        self.is_live_simulation_stopped = True
    
    def get_frames(self, postprocessor_index=0):
        postprocessed_frames = []
        for frame in self.live_frames:
            processed_frame = cv2.imencode('.jpg', self.postprocessors[postprocessor_index](frame))[1].tobytes()
            postprocessed_frames.append(processed_frame)
        return postprocessed_frames

    def get_live_frame(self,postprocessor_index=0):
        while self.live_frames[self.live_frame_index] is None:
            time.sleep(0.1)
        return cv2.imencode('.jpg', self.postprocessors[postprocessor_index](self.live_frames[self.live_frame_index]))[1].tobytes()
    
    def get_stored_frame(self, *args, **kwargs):
        return self.get_live_frame(*args, **kwargs)
    


class NotFoundSource(object):
    def __init__(self, text, size=640):
        font_scale, thickness = 1, 2
        img = np.zeros((size, size, 3))
        (height, width) = img.shape[:2]
        (text_width, text_height), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        text_x = int((width - text_width) / 2)
        text_y = int((height + text_height) / 2)
        self.img = cv2.putText(img, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX,
                    font_scale, (255,255,255), thickness)
    
    def get_frame(self, ):
        return cv2.imencode('.jpg', self.img)[1].tobytes()