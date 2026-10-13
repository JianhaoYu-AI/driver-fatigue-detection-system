from ultralytics import YOLO
from pathlib import Path

def train_model():
    """疲劳识别训练主函数"""
    print("开始训练疲劳检测模型...")
    
    # 检查数据集是否存在
    if not Path('fatigue_data.yaml').exists():
        print("错误：数据集配置文件不存在，请先运行 convert_fatigue_voc_to_yolo.py")
        return
    
    # 加载预训练模型
    model_path = 'models/yolo11n.pt' if Path('models/yolo11n.pt').exists() else 'yolo11n.pt'
    
    try:
        model = YOLO(model_path)
        
        # 开始训练
        results = model.train(
            data='fatigue_data.yaml',      # 数据集配置
            epochs=50,                     # 训练轮数（减少轮数以快速演示）
            imgsz=640,                     # 输入图像尺寸
            batch=16,                      # 批次大小
            device='cpu',                  # 使用CPU训练
            lr0=0.01,                      # 初始学习率
            patience=10,                   # 早停耐心值
            project='fatigue_results',     # 项目文件夹
            name='yolo11n_fatigue',        # 实验名称
            exist_ok=True                  # 覆盖已存在的结果
        )
        
        print("训练完成！")
        print(f"结果保存在: fatigue_results/")
        return results
        
    except Exception as e:
        print(f"训练失败: {e}")
        print("请确保数据集已正确准备")

if __name__ == '__main__':
    train_model()