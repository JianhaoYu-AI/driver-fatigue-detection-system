# 基于 YOLO11 的疲劳检测系统

面向驾驶场景的毕业设计演示项目，使用 **Ultralytics YOLO11、OpenCV 和 Flask**，将眼部、嘴部状态检测与简化 PERCLOS 统计接入 Web 页面，提供图片检测、摄像头监控和疲劳事件统计。

> 本仓库包含应用源码、数据转换与训练脚本，以及通用 `yolo11n.pt` 预训练权重。**当前不包含疲劳专用训练权重或训练数据集**；通用权重的类别不能直接当作眼部、嘴部类别，需完成四类专用训练后才能用于对应检测。项目未附可核验的精度、召回率或帧率实验记录。

## 项目功能

- **图片检测**：上传图片，通过 `/detect` 返回目标框、类别、置信度和窗口统计结果。
- **摄像头监控**：后端 OpenCV 读取本机默认摄像头，经 YOLO 推理后以 MJPEG 视频流显示。
- **疲劳统计**：在 30 次输入窗口内累计出现闭眼检测的次数，计算闭眼比例并输出疲劳等级。
- **状态展示**：Web 页面展示最近统计结果、疲劳事件数和当前闭眼比例。
- **数据与训练流程**：提供 VOC XML 标注转换、YOLO 数据集配置、模型训练和合成图片推理演示脚本。

## 技术与实现

|模块|实现|
|---|---|
|目标检测|Ultralytics YOLO11，推理置信度阈值 `0.5`|
|图像处理|OpenCV、NumPy|
|Web 后端|Flask，默认端口 `5002`|
|Web 前端|HTML、原生 JavaScript、Bootstrap 5、Font Awesome|
|视频传输|MJPEG，`/video_feed`|
|模型训练|PyTorch，通过 Ultralytics 训练接口调用|
|疲劳判断|基于闭眼检测频次的简化 PERCLOS 统计|

### 四类检测标签

类别编号需要与训练数据、模型和应用保持一致：

|编号|标签|含义|
|---:|---|---|
|0|`open_eye`|睁眼|
|1|`closed_eye`|闭眼|
|2|`open_mouth`|张嘴|
|3|`closed_mouth`|闭嘴|

### 疲劳窗口与阈值

```text
闭眼比例 = 当前窗口中至少检测到一只闭眼的输入次数 / 窗口总输入次数
窗口大小 = 30 次输入
疲劳判定 = 闭眼比例 > 0.7
```

等级划分为：`> 0.8` 为高等级，`> 0.5` 为中等级，其余为低等级。窗口结束后计数归零，内存中最多保留 100 条历史窗口记录。

这里采用固定输入次数窗口，不是按时间或眼睑遮挡程度实现的完整 PERCLOS 测量。嘴部类别目前参与目标检测，但未参与疲劳判定；尚未实现头部姿态分析、打哈欠频率分析或声音告警。

## 目录结构

```text
driver-fatigue-detection-system/
├── fatigue_app.py                  # Flask 路由、模型推理、视频流与疲劳统计
├── quick_start.py                  # 交互式环境检查与启动脚本
├── convert_fatigue_voc_to_yolo.py   # VOC XML 转 YOLO 检测标注
├── train_fatigue.py                # 专用模型训练入口
├── test_fatigue_model.py           # 合成图片推理与结果图演示
├── fatigue_data.yaml              # 数据目录与四类标签配置
├── requirements.txt               # Python 依赖
├── yolo11n.pt                      # 通用预训练权重，非疲劳专用权重
├── templates/
│   └── fatigue_index.html          # 图片检测、摄像头与统计页面
├── static/css/style.css            # 样式资源，页面主要使用内嵌样式
└── README.md
```

旧电脑的 `Scripts/`、`pyvenv.cfg` 和 `.idea/` 属于环境或 IDE 文件，保留在本地，但不提交到仓库。运行时数据、训练产物和日志也由 `.gitignore` 排除。

## 安装与启动

建议使用 Python 3.10，并新建独立环境。以下命令均在仓库根目录执行。

### 1. 获取项目

```bash
git clone https://github.com/JianhaoYu-AI/driver-fatigue-detection-system.git
cd driver-fatigue-detection-system
```

### 2. 创建环境并安装依赖

Windows PowerShell：

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

如果使用 CUDA，请根据实际显卡与驱动选择相匹配的 PyTorch 安装方式。当前训练脚本显式使用 CPU，不会自动切换 GPU。

### 3. 准备专用权重

将已训练的四类检测权重放在以下位置，例如：

```text
fatigue_results/yolo11n_fatigue/weights/best.pt
```

应用会查找 `fatigue_results/` 下遇到的第一个 `best.pt`。若存在多个实验，请明确保留或选择要使用的模型；当前程序没有模型切换界面。没有专用权重时，程序回退到根目录的通用 `yolo11n.pt`，只能用于流程演示，不能保证疲劳类别正确。

### 4. 启动应用

Windows：

```powershell
.\.venv\Scripts\python.exe fatigue_app.py
```

macOS / Linux：

```bash
.venv/bin/python fatigue_app.py
```

浏览器访问 **http://127.0.0.1:5002**。页面样式依赖在线 CDN，完整样式加载需要联网。

`quick_start.py` 是备用交互入口，会检查并安装缺失依赖、创建目录、重写数据集配置，再询问是否启动。它使用 `pkg_resources`，且内置依赖版本与 `requirements.txt` 不完全一致，因此推荐按上述步骤显式安装并启动。

## 使用说明

### 图片检测

上传 JPG、PNG 或 BMP 图片，查看检测结果数量及窗口完成时的疲劳状态。单张图片通常返回 `fatigue_result: null`，因为疲劳统计需要累计 30 次输入。

### 实时监控

点击“启动监控”，后端打开运行应用机器的默认摄像头 `0`；点击“停止监控”释放摄像头。这里使用的是**服务器本机摄像头**，并非浏览器客户端摄像头。

### HTTP 接口

|方法|路径|用途|
|---|---|---|
|GET|`/`|Web 页面|
|POST|`/detect`|上传检测图片，表单字段为 `image`|
|GET|`/start_camera`|打开本机默认摄像头|
|GET|`/stop_camera`|释放摄像头|
|GET|`/video_feed`|MJPEG 视频流|
|GET|`/stats`|返回最近 10 条窗口记录及统计数量|

`/stats` 中的 `total_detections` 实际统计已完成的窗口记录数，最多为 100，并非累计检测帧数。统计与摄像头状态为进程内全局对象，图片请求和视频流会共享统计状态；当前更适合本机单用户演示。

## 数据准备与模型训练

### 1. 准备 VOC 数据

自行准备有使用授权的眼部、嘴部数据，并按四类标签标注：

```text
Fatigue/
├── JPEGImages/    # 与 XML 文件同名的图片
└── Annotations/   # VOC XML 标注，包含图片尺寸和目标框
```

### 2. 转换标注并划分数据

```bash
python convert_fatigue_voc_to_yolo.py
```

转换后的布局：

```text
fatigue_yolo_dataset/
├── images/train/
├── images/val/
├── labels/train/
└── labels/val/
```

转换脚本只填充训练集目录，**不会自动划分验证集**。训练前需将配对的图片和标签分别划分到 `train` 与 `val`，检查标签编号及 `fatigue_data.yaml` 中的路径。

### 3. 训练

```bash
python train_fatigue.py
```

默认参数：50 个 epoch、输入尺寸 640、batch 16、初始学习率 0.01、早停耐心值 10、CPU 训练，输出目录为 `fatigue_results/yolo11n_fatigue/`。脚本设置 `exist_ok=True`，重复运行时需留意同名实验输出。

### 4. 合成图片演示

```bash
python test_fatigue_model.py
```

脚本会生成 `test_sample.jpg` 与 `test_result.png`，用于检查推理与绘图流程。它不是模型精度评测，也不包含真实疲劳测试集。

## 已知限制与改进方向

- 补充专用模型权重、训练数据说明和独立验证记录后，才能报告检测精度与运行速度。
- 当前没有区分“未检测到眼睛”与“确认睁眼”，可能影响闭眼比例。
- 统计记录仅保存在内存，程序重启后清空；多用户会共享检测状态。
- 服务使用 Flask 开发模式，默认监听 `0.0.0.0`；如需正式上线，应先处理认证、输入校验、会话隔离和服务部署配置。
- 后续可完善时间窗口统计、验证集划分、模型类别校验及疲劳告警功能。

## Web 版检查状态

已检查 Python 语法、数据配置和简化疲劳统计逻辑；未在本次整理中训练模型、打开摄像头或测量真实检测性能。源代码中的单帧推理结果及合成图片演示不能替代真实数据集验证。