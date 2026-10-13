import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']

class FatigueDetector:
    def __init__(self):
        self.closed_eye_count = 0
        self.frame_count = 0
        self.classes = ['open_eye', 'closed_eye', 'open_mouth', 'closed_mouth']
        
    def detect_fatigue(self, detections):
        """基于PERCLOS算法检测疲劳状态"""
        closed_eyes = sum(1 for d in detections if d['class'] == 'closed_eye')
        self.frame_count += 1
        
        if closed_eyes > 0:
            self.closed_eye_count += 1
            
        if self.frame_count >= 30:  # 每30帧计算一次
            perclos = self.closed_eye_count / self.frame_count
            is_fatigue = perclos > 0.7
            
            # 重置计数器
            self.closed_eye_count = 0
            self.frame_count = 0
            
            return {
                'is_fatigue': is_fatigue,
                'perclos': perclos,
                'fatigue_level': 'high' if perclos > 0.8 else 'medium' if perclos > 0.5 else 'low'
            }
        return None

def test_model():
    """测试疲劳检测模型"""
    print("开始测试疲劳检测模型...")
    
    # 查找训练好的模型
    model_path = None
    for path in Path('fatigue_results').rglob('best.pt'):
        model_path = str(path)
        break
    
    if not model_path:
        print("警告：未找到训练好的模型，使用预训练模型")
        model_path = 'yolo11n.pt'
    
    try:
        model = YOLO(model_path)
        detector = FatigueDetector()
        
        # 创建测试图片（使用合成图片）
        test_image = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(test_image, "测试图片 - 疲劳检测系统", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # 保存测试图片
        cv2.imwrite('test_sample.jpg', test_image)
        
        # 进行检测
        results = model(test_image, conf=0.5)
        
        # 处理检测结果
        detections = []
        for result in results:
            if result.boxes is not None:
                for box in result.boxes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = box.conf[0].cpu().numpy()
                    class_id = int(box.cls[0].cpu().numpy())
                    
                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': float(confidence),
                        'class': detector.classes[class_id] if class_id < len(detector.classes) else f'class_{class_id}'
                    })
        
        # 疲劳状态检测
        fatigue_result = detector.detect_fatigue(detections)
        
        # 显示结果
        print(f"\n检测结果:")
        print(f"检测到 {len(detections)} 个目标")
        for det in detections:
            print(f"类别: {det['class']}, 置信度: {det['confidence']:.2f}")
        
        if fatigue_result:
            print(f"\n疲劳状态: {'疲劳' if fatigue_result['is_fatigue'] else '正常'}")
            print(f"PERCLOS值: {fatigue_result['perclos']:.2f}")
        
        # 绘制结果图
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 原图
        ax1.imshow(cv2.cvtColor(test_image, cv2.COLOR_BGR2RGB))
        ax1.set_title('测试图片')
        ax1.axis('off')
        
        # 检测结果
        result_img = test_image.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            cv2.rectangle(result_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(result_img, f"{det['class']}:{det['confidence']:.2f}", 
                       (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        ax2.imshow(cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB))
        ax2.set_title('检测结果')
        ax2.axis('off')
        
        plt.tight_layout()
        plt.savefig('test_result.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("\n测试完成！结果已保存到 test_result.png")
        
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == '__main__':
    test_model()