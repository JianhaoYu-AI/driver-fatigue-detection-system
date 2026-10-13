#!/usr/bin/env python3
"""
疲劳检测系统 - 智能启动脚本
一键检查环境并启动应用
"""

import os
import sys
import subprocess
import pkg_resources
from pathlib import Path
import webbrowser
import time

def check_python_version():
    """检查Python版本"""
    print("🔍 检查Python版本...")
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要3.8或更高版本")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True

def check_dependencies():
    """检查依赖包"""
    print("\n📦 检查依赖包...")
    
    required_packages = {
        'ultralytics': '8.3.0',
        'flask': '3.0.0',
        'opencv-python': '4.8.1.78',
        'numpy': '1.24.3',
        'lxml': '4.9.3',
        'pillow': '10.0.1',
        'torch': '2.7.1',
        'torchvision': '0.18.1'
    }
    
    missing_packages = []
    for package, version in required_packages.items():
        try:
            installed = pkg_resources.get_distribution(package)
            print(f"✅ {package}: {installed.version}")
        except pkg_resources.DistributionNotFound:
            missing_packages.append(f"{package}=={version}")
            print(f"❌ {package}: 未安装")
    
    if missing_packages:
        print(f"\n📥 正在安装缺失的依赖包...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✅ 依赖包安装完成")
    
    return True

def check_model_files():
    """检查模型文件"""
    print("\n🤖 检查模型文件...")
    
    # 检查训练好的模型
    model_paths = list(Path('.').rglob('best.pt'))
    if model_paths:
        print(f"✅ 找到训练好的模型: {model_paths[0]}")
        return str(model_paths[0])
    
    # 检查预训练模型
    if Path('models/yolo11n.pt').exists():
        print("✅ 找到预训练模型: models/yolo11n.pt")
        return 'models/yolo11n.pt'
    
    print("⚠️  未找到训练好的模型，将使用YOLO11预训练模型")
    return None

def create_directories():
    """创建必要的目录"""
    print("\n📁 创建目录结构...")
    
    directories = [
        'models',
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'Fatigue/JPEGImages',
        'Fatigue/Annotations',
        'fatigue_yolo_dataset/images/train',
        'fatigue_yolo_dataset/images/val',
        'fatigue_yolo_dataset/labels/train',
        'fatigue_yolo_dataset/labels/val',
        'fatigue_results',
        'detection_results'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {directory}")

def setup_environment():
    """设置环境"""
    print("\n⚙️  设置环境...")
    
    # 创建简单的测试数据
    create_test_data()
    
    print("✅ 环境设置完成")

def create_test_data():
    """创建测试数据"""
    print("📝 创建测试数据...")
    
    # 创建疲劳数据配置文件
    yaml_content = """
# 疲劳检测数据集配置
path: ./fatigue_yolo_dataset
train: images/train
val: images/val

# 类别
nc: 4
names: ['open_eye', 'closed_eye', 'open_mouth', 'closed_mouth']
"""
    
    with open('fatigue_data.yaml', 'w', encoding='utf-8') as f:
        f.write(yaml_content.strip())
    
    print("✅ 创建配置文件: fatigue_data.yaml")

def start_application():
    """启动应用"""
    print("\n🚀 启动疲劳检测系统...")
    
    # 检查端口是否被占用
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', 5002))
    sock.close()
    
    if result == 0:
        print("❌ 端口5002已被占用")
        return False
    
    print("✅ 端口5002可用")
    
    # 启动Flask应用
    print("\n🌐 正在启动Web服务...")
    print("📱 访问地址: http://localhost:5002")
    print("\n🎯 使用说明:")
    print("   1. 上传图片进行疲劳检测")
    print("   2. 启动摄像头进行实时监控")
    print("   3. 查看实时统计信息")
    
    # 延迟打开浏览器
    time.sleep(2)
    webbrowser.open('http://localhost:5002')
    
    # 启动应用
    subprocess.run([sys.executable, 'fatigue_app.py'])

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 疲劳检测系统 - 智能启动脚本")
    print("=" * 60)
    
    try:
        # 检查环境
        if not check_python_version():
            return
        
        check_dependencies()
        check_model_files()
        create_directories()
        setup_environment()
        
        # 询问用户是否启动
        print("\n" + "=" * 60)
        response = input("🚀 是否立即启动应用? (y/n): ").strip().lower()
        
        if response in ['y', 'yes', '']:
            start_application()
        else:
            print("\n✅ 环境准备完成")
            print("📋 手动启动命令: python fatigue_app.py")
            print("🌐 访问地址: http://localhost:5002")
    
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("💡 请检查错误信息并重新运行")

if __name__ == '__main__':
    main()