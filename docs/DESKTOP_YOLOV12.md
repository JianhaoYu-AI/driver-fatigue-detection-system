# YOLOv12 桌面版

该版本来自 `YOLOv12疲劳检测系统.zip`，使用 PyQt5 和 ZIP 中保留的 YOLOv12 兼容源码。

## 已保留

- `main.py`、`UiMain.py`、`LoginWindow.py` 和 `train.py`。
- 根目录的专用 `best.pt`，四类为 `Yawn`、`close`、`noYawn`、`open`。
- `ultralytics/` 模型与工具源码，包含 YOLOv12 所需的 `A2C2f` 模块。
- 两次实验的历史 CSV、训练参数和不含人像的评测曲线。

未导入原账号文件、个人检测结果、人像训练预览图、重复权重、通用 n/s/m/l/x 权重、IDE 设置和字节码缓存。原 ZIP 未修改。

## 启动

请按根 README 建立独立桌面环境，安装 `desktop_yolov12/requirements.txt`。从 `desktop_yolov12` 目录运行 `main.py`，首次运行注册本地账号。

`best.pt` 通过 ZIP 内 checkpoint 的静态结构检查确认包含四类标签和 YOLOv12 `A2C2f` 结构。本次检查未反序列化执行模型、未验证实时推理。

## 训练

1. 根据数据授权准备或解压数据到本地。
2. 修改 `data.yaml` 的 `path` 为数据集目录的**绝对路径**；该目录下应包含 `images` 与 `labels`。
3. 准备训练入口使用的 `yolov12s.pt` 初始化权重，或者在 `train.py` 中明确指定自己的初始化模型。
4. 在桌面目录运行 `python train.py`。

原训练脚本使用 100 个 epoch、batch 8、GPU `0`、workers 0，输出到 `runs/exp`。如需 CPU，修改 `device='0'`；训练前确认资源预算。通用初始化权重未随桌面版重复发布。

`data.yaml` 中提供示例相对路径，训练前须按步骤替换。原 ZIP 的旧电脑绝对路径已从发布版数据配置中移除；历史日志中的路径作为原记录保留。

## 界面与结果

- 默认模型选项为 `best`。
- 置信度默认 0.25，IoU 默认 0.45，可以在界面调整。
- 图片支持 JPG/JPEG/PNG/BMP，视频选择支持 MP4/AVI/MOV。
- `DetectionThread` 执行推理，通过 Qt 信号更新原图、检测图和类别表格。
- 结果写入 `results/`，该目录不纳入 Git。
- 摄像头默认设备 `0`，需要本机摄像头和设备访问权限。

代码中的 `time.sleep(0.03)` 是帧循环延时，不代表实际达到 30 FPS。

## 演示登录

发布时不包含现有 `accounts.json`。注册后会在本地自动创建该文件，并被 `.gitignore` 排除。当前账号以明文形式保存，适用于本地演示；不能据此声称具备安全的生产级用户认证。
