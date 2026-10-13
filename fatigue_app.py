from flask import Flask, render_template, request, jsonify, Response
from ultralytics import YOLO
import cv2
import numpy as np
import threading
import time
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 全局变量
model = None
camera = None
output_frame = None
lock = threading.Lock()

# 类别定义
classes = ['open_eye', 'closed_eye', 'open_mouth', 'closed_mouth']

class FatigueDetector:
    def __init__(self):
        self.closed_eye_count = 0
        self.frame_count = 0
        self.fatigue_history = []
        
    def detect_fatigue(self, detections):
        """基于PERCLOS算法检测疲劳状态"""
        closed_eyes = sum(1 for d in detections if d['class'] == 'closed_eye')
        self.frame_count += 1
        
        if closed_eyes > 0:
            self.closed_eye_count += 1
            
        if self.frame_count >= 30:  # 每30帧计算一次
            perclos = self.closed_eye_count / self.frame_count
            is_fatigue = perclos > 0.7
            
            # 确定疲劳等级
            if perclos > 0.8:
                fatigue_level = 'high'
            elif perclos > 0.5:
                fatigue_level = 'medium'
            else:
                fatigue_level = 'low'
            
            # 记录历史
            self.fatigue_history.append({
                'timestamp': time.time(),
                'perclos': perclos,
                'is_fatigue': is_fatigue,
                'fatigue_level': fatigue_level
            })
            
            # 保持最近100条记录
            if len(self.fatigue_history) > 100:
                self.fatigue_history.pop(0)
            
            # 重置计数器
            self.closed_eye_count = 0
            self.frame_count = 0
            
            return {
                'is_fatigue': is_fatigue,
                'perclos': perclos,
                'fatigue_level': fatigue_level
            }
        return None

# 初始化疲劳检测器
fatigue_detector = FatigueDetector()

def load_model():
    """加载YOLO模型"""
    global model
    try:
        # 查找训练好的模型
        model_path = None
        for path in Path('fatigue_results').rglob('best.pt'):
            model_path = str(path)
            break
        
        if model_path and Path(model_path).exists():
            model = YOLO(model_path)
            logger.info(f"成功加载模型: {model_path}")
        else:
            # 使用预训练模型
            model = YOLO('yolo11n.pt')
            logger.warning("使用预训练模型，疲劳检测功能可能不准确")
            
    except Exception as e:
        logger.error(f"模型加载失败: {e}")
        model = None

def detect_in_frame(frame):
    """在帧中进行检测"""
    if model is None:
        return frame, []
    
    try:
        results = model(frame, conf=0.5)
        detections = []
        
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    if class_id < len(classes):
                        class_name = classes[class_id]
                        detections.append({
                            'bbox': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class': class_name
                        })
                        
                        # 绘制边界框
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                        cv2.putText(frame, f"{class_name}:{confidence:.2f}", 
                                  (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return frame, detections
    except Exception as e:
        logger.error(f"检测失败: {e}")
        return frame, []

def generate_frames():
    """生成视频流帧"""
    global camera, output_frame, lock
    
    while True:
        if camera is None:
            time.sleep(0.1)
            continue
            
        success, frame = camera.read()
        if not success:
            continue
            
        # 进行检测
        frame, detections = detect_in_frame(frame)
        
        # 疲劳检测
        fatigue_result = fatigue_detector.detect_fatigue(detections)
        
        # 显示疲劳状态
        if fatigue_result:
            status_text = f"疲劳状态: {'疲劳' if fatigue_result['is_fatigue'] else '正常'} | PERCLOS: {fatigue_result['perclos']:.2f}"
            color = (0, 0, 255) if fatigue_result['is_fatigue'] else (0, 255, 0)
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # 编码为JPEG
        with lock:
            ret, buffer = cv2.imencode('.jpg', frame)
            if ret:
                output_frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + output_frame + b'\r\n')

@app.route('/')
def index():
    return render_template('fatigue_index.html')

@app.route('/detect', methods=['POST'])
def detect():
    """处理疲劳检测请求"""
    try:
        file = request.files['image']
        file_bytes = file.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if model is None:
            load_model()
        
        # 进行检测
        img, detections = detect_in_frame(img)
        
        # 疲劳状态检测
        fatigue_result = fatigue_detector.detect_fatigue(detections)
        
        return jsonify({
            'success': True,
            'detections': detections,
            'count': len(detections),
            'fatigue_result': fatigue_result
        })
        
    except Exception as e:
        logger.error(f"检测请求处理失败: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/video_feed')
def video_feed():
    """视频流路由"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_camera')
def start_camera():
    """启动摄像头"""
    global camera
    try:
        if camera is None:
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return jsonify({'success': False, 'error': '无法打开摄像头'})
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stop_camera')
def stop_camera():
    """停止摄像头"""
    global camera
    try:
        if camera is not None:
            camera.release()
            camera = None
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stats')
def get_stats():
    """获取统计信息"""
    return jsonify({
        'total_detections': len(fatigue_detector.fatigue_history),
        'fatigue_events': sum(1 for h in fatigue_detector.fatigue_history if h['is_fatigue']),
        'recent_history': fatigue_detector.fatigue_history[-10:] if fatigue_detector.fatigue_history else []
    })

if __name__ == '__main__':
    # 启动时加载模型
    load_model()
    
    # 启动应用
    app.run(debug=True, host='0.0.0.0', port=5002)