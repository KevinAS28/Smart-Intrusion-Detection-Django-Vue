from django.db import models
from token_authentication import models as ta_model
# Create your models here.
class HomeSettings(models.Model):
    user = models.ForeignKey(ta_model.UserAuthentication, on_delete=models.DO_NOTHING)
    video_file = models.CharField(max_length=200, null=True, blank=True)


class InferenceSettings(models.Model):
    user = models.ForeignKey(ta_model.UserAuthentication, on_delete=models.DO_NOTHING)
    model_name = models.CharField(max_length=100, default='rtdetr_yolov9bb_ep27.onnx')
    objects_to_warn = models.CharField(max_length=300, default='person,bicycle')
    size = models.IntegerField(default=640)
    thrh = models.FloatField(default=0.55)
    overlay_line = models.CharField(max_length=50, null=True, blank=True, default='h_0_400_0') # Horizontal x0 y400 notinvert

    def get_lines(self, orient=False, inv=False):
        _, x, y, _ = self.overlay_line.split('_')
        line = []
        if orient:
            line.append(self.get_line_orientation())
        line.append(int(x))
        line.append(int(y))
        if inv:
            line.append(self.get_line_invert())
        return [line]

    def get_line_invert(self):
        _,_,_, invert = self.overlay_line.split('_')
        return bool(invert)
    
    def get_line_orientation(self):
        orientation, _,_,_ = self.overlay_line.split('_')
        return orientation    

class WarningNotification(models.Model):
    user = models.ForeignKey(ta_model.UserAuthentication, on_delete=models.DO_NOTHING)
    objs = models.CharField(max_length=200, default='')
    frame_path = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  