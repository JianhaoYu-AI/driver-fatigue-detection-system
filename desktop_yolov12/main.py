import sys

import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from ultralytics import YOLO
from UiMain import UiMainWindow
import time
import os
from PyQt5.QtWidgets import QDialog
from LoginWindow import LoginWindow

class DetectionThread(QThread):
    frame_received = pyqtSignal(np.ndarray, np.ndarray, list)  # 原始帧, 检测帧, 检测结果
    finished_signal = pyqtSignal()  # 线程完成信号

    def __init__(self, model, source, conf, iou, parent=None):
        super().__init__(parent)
        self.model = model
        self.source = source
        self.conf = conf
        self.iou = iou
        self.running = True

    def run(self):
        try:
            if isinstance(self.source, int) or self.source.endswith(('.mp4', '.avi', '.mov')):  # 视频或摄像头
                cap = cv2.VideoCapture(self.source)
                while self.running and cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    # 保存原始帧
                    original_frame = frame.copy()

                    # 检测
                    results = self.model(frame, conf=self.conf, iou=self.iou)
                    annotated_frame = results[0].plot()

                    # 提取检测结果
                    detections = []
                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls)
                            class_name = self.model.names[class_id]
                            confidence = float(box.conf)
                            x, y, w, h = box.xywh[0].tolist()
                            detections.append((class_name, confidence, x, y))

                    # 发送信号
                    self.frame_received.emit(
                        cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB),
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        detections
                    )

                    # 控制帧率
                    time.sleep(0.03)  # 约30fps

                cap.release()
            else:  # 图片
                frame = cv2.imread(self.source)
                if frame is not None:
                    original_frame = frame.copy()
                    results = self.model(frame, conf=self.conf, iou=self.iou)
                    annotated_frame = results[0].plot()

                    # 提取检测结果
                    detections = []
                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls)
                            class_name = self.model.names[class_id]
                            confidence = float(box.conf)
                            x, y, w, h = box.xywh[0].tolist()
                            detections.append((class_name, confidence, x, y))

                    self.frame_received.emit(
                        cv2.cvtColor(original_frame, cv2.COLOR_BGR2RGB),
                        cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB),
                        detections
                    )

        except Exception as e:
            print(f"Detection error: {e}")
        finally:
            self.finished_signal.emit()

    def stop(self):
        self.running = False


class MainWindow(UiMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化模型
        self.model = None
        self.detection_thread = None
        self.current_image = None
        self.current_result = None
        self.video_writer = None
        self.is_camera_running = False
        self.is_video_running = False
        self.last_detection_result = None  # 新增：保存最后一次检测结果

        # 连接按钮信号
        self.image_btn.clicked.connect(self.detect_image)
        self.video_btn.clicked.connect(self.detect_video)
        self.camera_btn.clicked.connect(self.detect_camera)
        self.stop_btn.clicked.connect(self.stop_detection)
        self.save_btn.clicked.connect(self.save_result)

        # 初始化模型
        self.load_model()

    def load_model(self):
        try:
            model_name = self.model_combo.currentText()
            self.model = YOLO(f"{model_name}.pt")  # 自动下载或加载本地模型
            self.update_status(f"模型 {model_name} 加载成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型加载失败: {str(e)}")
            self.update_status("模型加载失败")

    def detect_image(self):
        if self.detection_thread and self.detection_thread.isRunning():
            QMessageBox.warning(self, "警告", "请先停止当前检测任务")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "", "图片文件 (*.jpg *.jpeg *.png *.bmp)")

        if file_path:
            self.clear_results()
            self.current_image = cv2.imread(file_path)
            self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            self.display_image(self.original_image_label, self.current_image)

            # 创建检测线程
            conf = self.confidence_spinbox.value()
            iou = self.iou_spinbox.value()
            self.detection_thread = DetectionThread(self.model, file_path, conf, iou)
            self.detection_thread.frame_received.connect(self.on_frame_received)
            self.detection_thread.finished_signal.connect(self.on_detection_finished)
            self.detection_thread.start()

            self.update_status(f"正在检测图片: {os.path.basename(file_path)}")

    def detect_video(self):
        if self.detection_thread and self.detection_thread.isRunning():
            QMessageBox.warning(self, "警告", "请先停止当前检测任务")
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择视频", "", "视频文件 (*.mp4 *.avi *.mov)")

        if file_path:
            self.clear_results()
            self.is_video_running = True

            # 初始化视频写入器
            cap = cv2.VideoCapture(file_path)
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()

            # 创建保存路径
            save_dir = "results"
            os.makedirs(save_dir, exist_ok=True)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            save_path = os.path.join(save_dir, f"result_{timestamp}.mp4")

            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(save_path, fourcc, fps, (frame_width, frame_height))

            # 创建检测线程
            conf = self.confidence_spinbox.value()
            iou = self.iou_spinbox.value()
            self.detection_thread = DetectionThread(self.model, file_path, conf, iou)
            self.detection_thread.frame_received.connect(self.on_frame_received)
            self.detection_thread.finished_signal.connect(self.on_detection_finished)
            self.detection_thread.start()

            self.update_status(f"正在检测视频: {os.path.basename(file_path)}")

    def detect_camera(self):
        if self.detection_thread and self.detection_thread.isRunning():
            QMessageBox.warning(self, "警告", "请先停止当前检测任务")
            return

        self.clear_results()
        self.is_camera_running = True

        # 创建检测线程 (默认使用摄像头0)
        conf = self.confidence_spinbox.value()
        iou = self.iou_spinbox.value()
        self.detection_thread = DetectionThread(self.model, 0, conf, iou)
        self.detection_thread.frame_received.connect(self.on_frame_received)
        self.detection_thread.finished_signal.connect(self.on_detection_finished)
        self.detection_thread.start()

        self.update_status("正在从摄像头检测...")

    def stop_detection(self):
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.stop()
            self.detection_thread.quit()
            self.detection_thread.wait()

        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None

        self.is_camera_running = False
        self.is_video_running = False
        self.update_status("检测已停止")

    def on_frame_received(self, original_frame, result_frame, detections):
        # 更新原始图像和结果图像
        self.display_image(self.original_image_label, original_frame)
        self.display_image(self.result_image_label, result_frame)

        # 保存当前结果帧用于后续保存
        self.last_detection_result = result_frame  # 新增：保存检测结果

        # 更新表格
        self.clear_results()
        for class_name, confidence, x, y in detections:
            self.add_detection_result(class_name, confidence, x, y)

        # 保存视频帧
        if self.video_writer:
            self.video_writer.write(cv2.cvtColor(result_frame, cv2.COLOR_RGB2BGR))

    def on_detection_finished(self):
        if self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.update_status("视频检测完成，结果已保存")
        elif self.is_camera_running:
            self.update_status("摄像头检测已停止")
        else:
            self.update_status("图片检测完成")

    def save_result(self):
        if not hasattr(self, 'last_detection_result') or self.last_detection_result is None:
            QMessageBox.warning(self, "警告", "没有可保存的检测结果")
            return

        save_dir = "results"
        os.makedirs(save_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        if self.is_camera_running or self.is_video_running:
            # 保存当前帧为图片
            save_path = os.path.join(save_dir, f"snapshot_{timestamp}.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(self.last_detection_result, cv2.COLOR_RGB2BGR))
            self.update_status(f"截图已保存: {save_path}")
        else:
            # 保存图片检测结果
            save_path = os.path.join(save_dir, f"result_{timestamp}.jpg")
            cv2.imwrite(save_path, cv2.cvtColor(self.last_detection_result, cv2.COLOR_RGB2BGR))
            self.update_status(f"检测结果已保存: {save_path}")

    def closeEvent(self, event):
        self.stop_detection()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 设置应用程序样式
    app.setStyle("Fusion")

    # 创建并显示登录窗口
    login_window = LoginWindow()

    # 如果登录成功
    if login_window.exec_() == QDialog.Accepted:
        # 创建并显示主窗口
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)