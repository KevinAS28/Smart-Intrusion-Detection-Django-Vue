import os
import time
import json

import cv2
import torch
from torchvision.transforms import v2 as trfmv2
import onnxruntime as ort
import numpy as np

def get_ort_session(model_path):
    print('ONNX device:', ort.get_device())
    providers = ['CUDAExecutionProvider']
    sess_options = ort.SessionOptions()
    ort_session = ort.InferenceSession(model_path, sess_options=sess_options, providers=providers)
    return ort_session

def inference_imgs_onnx(ort_session, input_data, size):
    orig_target_sizes = torch.tensor([[size, size]])
    labels, boxes, scores = ort_session.run(None, {'images': input_data.data.numpy(), 'orig_target_sizes': orig_target_sizes.data.numpy()})
    return labels, boxes, scores

def isjson(json_content):
    try:
        return json.loads(json_content)
    except json.JSONDecodeError:
        return False
    


def line_to_box(line, img_shape, line_type='h', invert=False):
  line = list(line)
  if line_type=='h':
    if not invert:
      line.append(img_shape[0])
      line.append(img_shape[1])
    else:
      line.append(0)
      line.append(0)
  elif line_type=='v':
    if not invert:
      line.append(img_shape[0])
      line.append(img_shape[1])
    else:
      line.append(0)
      line.append(img_shape[0])
      
  else:
    raise ValueError(f'Line type {line_type} is not supported')  
  return line
                               
def rectangles_intersect(rect0, rect1, invert=False):
  
  if (rect0[0]**2+rect0[1]**2)**(1/2) < (rect1[0]**2+rect1[1]**2)**(1/2):
    conditions = (
      rect0[2]>=rect1[0] and rect0[3]>=rect1[1],
      rect1[2]>=rect0[0] and rect1[3]<=rect0[1],  
    )
  else:
    conditions = (
      rect1[2]>=rect0[0] and rect1[3]>=rect0[3],
      rect1[3]>=rect0[1] and rect1[2]>=rect0[0],
    )
  result = any(conditions)

  return not result if invert else result

def obj_crossed_line(obj_bbox, line, line_type='h', invert=False):
  def _algo():
    points = [obj_bbox[:2], obj_bbox[2:4], [obj_bbox[2], obj_bbox[1]], [obj_bbox[0], obj_bbox[3]]]

    # check vertical
    if line_type=='v':
      for pt in points:
        if pt[0]>line[0]:
          return True
      return False
    
    elif line_type=='h':
      for pt in points:
        if pt[1]>line[1]:
          return True
      
      return False
    
    else:
      raise 'line not supported'

  return _algo() and not invert

def add_overlay(img, rect, channel_index, color_value, alpha=0.5, invert=False):
    start_w, start_h, end_w, end_h = rect
    height, width, channels = img.shape

    new_colors = [0,0,0,alpha*255]
    new_colors[channel_index] = color_value

    if invert:
        overlay = np.full((height, width, 4), new_colors, dtype=np.uint8)
        overlay_rgb = overlay[..., :channels] 
        mask = np.ones_like(img, dtype=bool)
        mask[start_h:end_h, start_w:end_w] = False
        img = (1 - alpha) * img + alpha * overlay_rgb * mask.astype(np.float32)
        img = img.astype(np.uint8)
    else:
        overlay = np.full((end_h - start_h, end_w - start_w, 4), new_colors, dtype=np.uint8)
        overlay_rgb = overlay[..., :channels] 
        img[start_h:end_h, start_w:end_w] = (1 - alpha) * img[start_h:end_h, start_w:end_w] + alpha * overlay_rgb

    return img


def frame_overlay(lines, frame, invert=False):
    for ln in lines:
        ln_type, ln = ln[0], ln[1:]
        ln_bx = line_to_box(ln, frame.shape, ln_type, False)
        frame = add_overlay(frame, ln_bx, 0, 255, 0.25, invert)

    return frame

def object_warnings(lines, s, l, b, objects_to_warn=['person'], invert=False):
    for ln in lines:
        ln_type, ln = ln[0], ln[1:]    
        obj_crossed = False
        if l in objects_to_warn:
            obj_crossed = obj_crossed_line(b, ln, ln_type, invert)
            if obj_crossed:
                print(f'WARNING: OBJECT {l} HAS CROSSED THE LINE')      

class RTDETROnnxDeploy(object):
    def __init__(self, model_path, size=640, classes_labels='inference_class_labels.json', encoder='XVID', thrh=0.65, out_video_path='', draw_obj_name=True, draw_obj_conf=True, overlay='h_0_450_0', objects_to_warn=['person', 'bicycle'], sample_img=None):
        self.model_path = model_path
        self.size = size
        self.classes_labels = classes_labels
        self.thrh = thrh
        self.out_video_path = out_video_path
        self.draw_obj_name = draw_obj_name
        self.draw_obj_conf = draw_obj_conf
        self.objects_to_warn = objects_to_warn
        
        self.set_classes_labels(classes_labels)      
        self.set_overlay_line(overlay)
        self.set_additional_postprocessor(self.lines, self.invert_line)
        self.set_obj_warning(objects_to_warn)
        self.set_inference_engine('onnx')
        self.set_model(model_path)

        # self.save_video_output = len(out_video_path)>0
        # if self.save_video_output:
        #     if os.path.isfile(self.save_video_output):
        #         os.remove(self.save_video_output)
        #     fourcc_code = cv2.VideoWriter_fourcc(*encoder)
        #     self.video_writer = cv2.VideoWriter(out_video_path, fourcc_code, 25.0, (size, size))  # Adjust FPS if needed
        
        self.start_time = time.time()
        self.total_inference_time = 0
        self.frame_count = 1
        self.eplased_time = 1
        self.fps = 0
        self.avg_inference_time = 0

        self.preprocess_transformations = trfmv2.Compose([
        trfmv2.ToImage(),
        trfmv2.ToDtype(torch.float32, scale=True),    
        trfmv2.Resize(size=(size, size), antialias=True),
        ])
        
        if not (sample_img is None):
          self.inference_frame(sample_img)
        
    def inference_frame(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        preprocessed_frame = self.preprocess_transformations(frame)
        stacked_frames = torch.stack([preprocessed_frame]) 

        self.inference_start_time = time.time()
        labels, boxes, scores = self.inference_engine(stacked_frames, self.size)
        inference_time = time.time()-self.inference_start_time
        self.total_inference_time += inference_time
        
        img_index = 0
                
        postprocessed_frame = cv2.cvtColor(cv2.resize(frame, (self.size, self.size)), cv2.COLOR_BGR2RGB)
        postprocessed_frame = self.additional_postprocessor(postprocessed_frame)
        self.frame_count += 1
        self.fps = self.frame_count / self.eplased_time        
        
        scr = scores[img_index]
        lab = labels[img_index]
        boxes = boxes[img_index]        
        
        if len(lab)>0:
            for s, l, b in zip(scr, lab, boxes):
                if s<=self.thrh:
                    continue

                s, l = float(s), int(l)
                b = [int(j) for j in b]
                # print('s l b', s, l, b)

                lab_str = str(self.classes_labels[l]) if self.draw_obj_name else ''
                scr_str = (('-' if self.draw_obj_name or self.draw_obj_conf else '') + str(round(s*100, 1))+'%') if self.draw_obj_conf else ''
                
                postprocessed_frame = cv2.rectangle(postprocessed_frame, tuple(b[:2]), tuple(b[2:4]), color=(0, 0, 255), thickness=2) 
                postprocessed_frame = cv2.putText(postprocessed_frame, f"{lab_str}{scr_str}", tuple(b[:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)  
                # if type(self.obj_warning) is str:
                #   print("OBJ WARNING: ", self.obj_warning)
                # else:
                self.obj_warning(s, lab_str, b)
                self.detected_class_frame[self.classes_labels[l]] += 1        
                                            
        postprocessed_frame = cv2.putText(postprocessed_frame, f"FPS: {self.fps:.2f}", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)  
        # if self.save_video_output:
        #     self.video_writer.write(postprocessed_frame)        
        self.eplased_time = time.time()-self.start_time
        self.avg_inference_time = self.total_inference_time/self.frame_count
        return postprocessed_frame
    def get_parameters(self, key=None):
        if key is None:
          all_params = ['model_path', 'size', 'classes_labels', 'thrh', 'out_video_path', 'objects_to_warn', 'lines', 'invert_line', ]
          return {
            param: getattr(self, param)
            for param in all_params
          }
        else:
          if hasattr(self, key):
            return getattr(self, key)
          else:
            return None
          
    def update_parameters(self, dict_params:dict):
        special_params = {
          'model_path': self.set_model,
          'inference_engine': self.set_inference_engine,
          'objects_to_warn': self.set_obj_warning,
          'overlay_line': self.set_overlay_line
        }
        
        for param_key, param_val in dict_params.items():
            print(f'update inference param {param_key} with {param_val}')
            if param_key in special_params:
                special_params[param_key](param_val)
            else:
                setattr(self, param_key, param_val)
    
        return self
    
    def set_obj_warning(self, objects_to_warn):
        if type(objects_to_warn)==str:
            self.objects_to_warn = objects_to_warn.split(',')
        else:
            self.objects_to_warn = objects_to_warn
        self.obj_warning = lambda s,l,b: object_warnings(self.lines, s, l, b, objects_to_warn, invert=self.invert_line)        
        
    def set_model(self, model_path):
        print(f'Loading the model from {model_path}')
        self.model_path = model_path
        self.ort_session = get_ort_session(model_path)
        self.set_inference_engine('onnx')
    
    def set_inference_engine(self, inference_engine='onnx'):
        if inference_engine=='onnx':
            self.inference_engine = lambda stacked_imgs, size: inference_imgs_onnx(self.ort_session, stacked_imgs, self.size)
        else:
            raise ValueError(f'Unknown inference engine: {inference_engine}')
    
    def set_additional_postprocessor(self, lines, invert_line):
        self.additional_postprocessor = lambda frame: frame_overlay(lines, frame, invert_line)

    def set_classes_labels(self, classes_labels):
        if os.path.isfile(classes_labels):
            with open(classes_labels, 'r') as cd_file:
                self.classes_labels = json.loads(cd_file.read())
        elif isjson(classes_labels):
            self.classes_labels = json.loads(self.classes_labels)
        else:
            raise ValueError('Invalid JSON classes labels')
        self.classes_labels = {v:k for k, v in self.classes_labels.items()}        
        self.detected_class_frame = {
            name:0 for name in self.classes_labels.values()
        }
        
    def set_overlay_line(self, overlay_line):
        line = overlay_line.split('_')
        line_coord = [int(i) for i in line[1:3]]
        line_invert = bool(int(line[-1]))
        line_orientation = line[0]
        self.lines = [[line_orientation, *line_coord]]
        self.invert_line = line_invert
        self.set_additional_postprocessor(self.lines, self.invert_line)
        self.set_obj_warning(self.objects_to_warn)
    
    
    def __del__(self):
        print('Saving video...')
        if hasattr(self, 'save_video_output'):
          if self.save_video_output:
              self.video_writer.release()
            
