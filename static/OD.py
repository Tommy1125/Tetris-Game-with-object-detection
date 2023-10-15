import time

from ultralytics import YOLO
import torch
import cv2
from ultralytics.yolo.data.augment import LetterBox
from ultralytics.yolo.utils.plotting import Annotator, colors
from ultralytics.yolo.utils import ops
from copy import deepcopy
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import random
import threading
from flask_socketio import SocketIO


from queue import Queue

def OD(socketio):
    # Initialize the variables
    time_sta = time.perf_counter()
    object_counter = {}
    last_detection_time = {}
    object_counter1 = {}
    last_detection_time1 = {}
    #last_detection_time1 = []
    detection_enabled = True



    model = YOLO('static/OD/best.pt')
    # Start video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        return
    
    # カメラの映像の幅と高さを取得
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # 上下の境界を定義
    upper_boundary = height / 2
    
    # 上半分を2つのエリアに分けるための境界を定義
    middle_boundary = width / 2

    while True:
        ret, img = cap.read()

        origin = deepcopy(img)
        annotator = Annotator(origin, line_width=3, example=str(model.model.names))
        # Only do object detection and update object counter when detection_enabled is True
        if detection_enabled:
            img = preprocess(img)
            preds = model.model(img, augment=False)
            preds = postprocess(preds, img, origin)
            draw_bbox(preds[0], model.model.names, annotator,last_detection_time1,last_detection_time,object_counter,object_counter1,cap,socketio,upper_boundary, middle_boundary,width,height)

        y_offset = 30
        for idx, (label_name, count) in enumerate(object_counter.items()):
            text = f"{label_name}: {count}"
            cv2.putText(origin, text, (10, y_offset + idx*30), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 2)

        y_offset = 60
        for idx, (label_name, count) in enumerate(object_counter1.items()):
            text = f"{label_name}: {count}"
            cv2.putText(origin, text, (10, y_offset + idx*30), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 255, 0), 2)
        # Draw upper boundary line
        cv2.line(origin, (0, int(upper_boundary)), (int(width), int(upper_boundary)), (0, 255, 255), 5)

        # Draw middle boundary line (only in the upper half)
        cv2.line(origin, (int(middle_boundary), 0), (int(middle_boundary), int(upper_boundary)), (0, 255, 255), 5)

        #cv2.putText(origin, "Push 'q' to close this window", (890, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
   
        cap.set(cv2.CAP_PROP_BRIGHTNESS,100) 

        ret, jpeg = cv2.imencode('.jpg', origin)  # フレームをJPEGにエンコード
        img = jpeg.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
        
    cap.release()



def preprocess(img, size=640):
    img = LetterBox(size, True)(image=img)
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)  # contiguous
    img = torch.from_numpy(img)
    img = img.float()  # uint8 to fp16/32
    img /= 255  # 0 - 255 to 0.0 - 1.0
    return img.unsqueeze(0)

def postprocess(preds, img, orig_img):
    preds = ops.non_max_suppression(preds,
                                    0.3,#Threthold
                                    0.8,
                                    agnostic=False,
                                    max_det=100)

    for i, pred in enumerate(preds):
        shape = orig_img.shape
        pred[:, :4] = ops.scale_boxes(img.shape[2:], pred[:, :4], shape).round()

    return preds

# グローバル変数としてplayerを確認できるようにしておく必要があります。
global player

def draw_bbox(pred, names, annotator, last_detection_time1, last_detection_time, object_counter, object_counter1, cap,socketio,upper_boundary, middle_boundary,width,height):
    current_time = time.time()
    current_time1 = time.time()
    

    for *xyxy, conf, cls in reversed(pred):
        c = int(cls)
        label_name = names[c]

        # オブジェクトの中心位置を計算
        center_x = (xyxy[0] + xyxy[2]) / 2
        center_y = (xyxy[1] + xyxy[3]) / 2

            # オブジェクトが上半分にあるか判定
        if center_y < upper_boundary:
            # エリア判定
            if center_x < middle_boundary:
                # 左エリアのトリガー
                socketio.emit('move_right')  # 左に移動のWebSocketメッセージを送信
            else:
                # 右エリアのトリガー
                socketio.emit('move_left')  # 右に移動のWebSocketメッセージを送信
        else:
            # 下半分のトリガー
            socketio.emit('rotate')  # 回転のWebSocketメッセージを送信

        label = f'{names[c]} {conf:.2f}'
        annotator.box_label(xyxy, label, color=colors(c, True))

