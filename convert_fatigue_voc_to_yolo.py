import os
import xml.etree.ElementTree as ET
from pathlib import Path

# 类别定义
classes = ['open_eye', 'closed_eye', 'open_mouth', 'closed_mouth']

def convert_annotation(xml_path, classes):
    """转换单个XML标注文件"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # 获取图像尺寸
    size = root.find('size')
    width = int(size.find('width').text)
    height = int(size.find('height').text)
    
    annotations = []
    
    for obj in root.findall('object'):
        class_name = obj.find('name').text
        if class_name not in classes:
            continue
            
        class_id = classes.index(class_name)
        
        # 获取边界框并转换为YOLO格式
        bbox = obj.find('bndbox')
        xmin, ymin = float(bbox.find('xmin').text), float(bbox.find('ymin').text)
        xmax, ymax = float(bbox.find('xmax').text), float(bbox.find('ymax').text)
        
        # 转换为YOLO格式 (x_center, y_center, width, height)
        x_center = (xmin + xmax) / 2.0 / width
        y_center = (ymin + ymax) / 2.0 / height
        w = (xmax - xmin) / width
        h = (ymax - ymin) / height
        
        annotations.append(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
    
    return annotations

def convert_dataset():
    """转换整个数据集"""
    # 创建输出目录
    output_dir = Path('fatigue_yolo_dataset')
    output_dir.mkdir(exist_ok=True)
    
    # 创建子目录
    (output_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
    (output_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)
    
    # 转换训练集
    train_images_dir = Path('Fatigue/JPEGImages')
    train_annotations_dir = Path('Fatigue/Annotations')
    
    if not train_images_dir.exists():
        print("警告：原始数据集目录不存在，请准备数据集")
        return
    
    # 处理所有XML文件
    xml_files = list(train_annotations_dir.glob('*.xml'))
    print(f"找到 {len(xml_files)} 个标注文件")
    
    for xml_file in xml_files:
        annotations = convert_annotation(xml_file, classes)
        if annotations:
            # 保存YOLO格式标注
            txt_path = output_dir / 'labels' / 'train' / f"{xml_file.stem}.txt"
            with open(txt_path, 'w') as f:
                f.write('\n'.join(annotations))
            
            # 复制对应的图片文件
            img_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            for ext in img_extensions:
                img_path = train_images_dir / f"{xml_file.stem}{ext}"
                if img_path.exists():
                    import shutil
                    shutil.copy2(img_path, output_dir / 'images' / 'train' / f"{xml_file.stem}{ext}")
                    break
    
    # 创建数据集配置文件
    yaml_content = f"""
# 疲劳检测数据集配置
path: fatigue_yolo_dataset
train: images/train
val: images/val
# 类别
nc: {len(classes)}
names: {classes}
"""
    
    with open('fatigue_data.yaml', 'w') as f:
        f.write(yaml_content.strip())
    
    print("数据集转换完成！")
    print(f"输出目录: {output_dir}")
    print(f"配置文件: fatigue_data.yaml")

if __name__ == '__main__':
    convert_dataset()