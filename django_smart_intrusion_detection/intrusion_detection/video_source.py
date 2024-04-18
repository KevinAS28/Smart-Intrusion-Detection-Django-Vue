import cv2, numpy as np

class VideoSourceFile(object):
    def __init__(self, video_path='/home/kevin/django-vue-stream/smartdetectoralarm/out.mkv', read_all_frames=False, postprocessor=lambda frame: frame):
        print('video_path:', video_path)
        self.video = cv2.VideoCapture(video_path)
        self.postprocessor = postprocessor
        
        if read_all_frames:    
            self.frames = []
            print('getting frames...')
            while True:
                success, image = self.video.read()
                if not success:
                    print('finish get frames')
                    break
                self.frames.append(image)
            self.frame_index = 0
            self.get_frame = self.get_stored_frame
        else:
            self.video_path = video_path
            self.get_frame = self.get_live_frame
            
    def __del__(self):
        self.video.release()

    def get_stored_frame(self):
        image = self.frames[self.frame_index]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)		
        ret, jpeg = cv2.imencode('.jpg', image)
        self.frame_index+=1
        if self.frame_index==len(self.frames):
            self.frame_index = 0
        return jpeg.tobytes()

    def get_live_frame(self, repeat=True):
        success, image = self.video.read()
        if not success:
            if repeat:
                self.video = cv2.VideoCapture(self.video_path)
                return self.get_live_frame(repeat)
            else:
                return False
        return cv2.imencode('.jpg', self.postprocessor(image))[1].tobytes()

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