# UiMain.py
import time

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QSlider, QTableWidget,
                             QTableWidgetItem, QGroupBox, QComboBox,
                             QDoubleSpinBox, QSizeGrip, QToolButton)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import (QPixmap, QImage, QIcon, QColor)


class FramelessWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()


class UiMainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("译路畅行驾驶行为监测系统")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(1200, 750)  # 调整为更合理的窗口尺寸

        # 主窗口样式（科技感深色背景）
        self.setStyleSheet("""
            background: #0a0a12;
        """)

        # 主窗口容器（带发光边框）
        self.main_container = QWidget()
        self.main_container.setObjectName("mainContainer")
        self.main_container.setStyleSheet("""
            #mainContainer {
                background: #0a0a12;
                border: 2px solid #00c8ff;
                border-radius: 8px;
                box-shadow: 0 0 15px rgba(0, 200, 255, 0.3);
            }
        """)
        self.setCentralWidget(self.main_container)

        # 主布局
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(2, 2, 2, 2)
        self.main_layout.setSpacing(0)

        # 自定义标题栏（渐变背景）
        self.title_bar = QWidget()
        self.title_bar.setObjectName("titleBar")
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("""
            #titleBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0a0a12, stop:0.5 #0f1a24, stop:1 #0a0a12);
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid #00c8ff;
            }
        """)

        # 标题栏布局
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(12, 0, 8, 0)
        self.title_layout.setSpacing(8)

        # 标题图标
        self.title_icon = QLabel()
        self.title_icon.setPixmap(QIcon("icon.png").pixmap(20, 20))
        self.title_layout.addWidget(self.title_icon)

        # 标题文本（霓虹蓝）
        self.title_label = QLabel("译路畅行驾驶行为监测系统")
        self.title_label.setStyleSheet("""
            color: #00c8ff;
            font-size: 14px;
            font-weight: bold;
            letter-spacing: 1px;
        """)
        self.title_layout.addWidget(self.title_label)

        # 标题栏弹簧
        self.title_layout.addStretch()

        # 窗口控制按钮（科技感圆形按钮）
        self.minimize_btn = self.create_title_button("－", "#00c8ff")
        self.minimize_btn.clicked.connect(self.showMinimized)

        self.maximize_btn = self.create_title_button("□", "#00c8ff")
        self.maximize_btn.clicked.connect(self.toggle_maximize)

        self.close_btn = self.create_title_button("×", "#ff4a4a")
        self.close_btn.clicked.connect(self.close)

        self.title_layout.addWidget(self.minimize_btn)
        self.title_layout.addWidget(self.maximize_btn)
        self.title_layout.addWidget(self.close_btn)

        self.main_layout.addWidget(self.title_bar)

        # 内容区域
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background: transparent;")
        self.content_layout = QHBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        self.content_layout.setSpacing(15)
        self.main_layout.addWidget(self.content_widget)

        # 左侧面板 (图像显示)
        self.left_panel = QVBoxLayout()
        self.left_panel.setSpacing(15)
        self.content_layout.addLayout(self.left_panel, 65)  # 左侧占65%

        # 原始图像显示（带发光边框）
        self.original_image_group = QGroupBox("原始图像")
        self.original_image_group.setStyleSheet(self.get_groupbox_style())
        self.original_image_layout = QVBoxLayout()
        self.original_image_label = QLabel()
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setMinimumSize(640, 360)
        self.original_image_label.setStyleSheet("""
            background-color: #0f0f1a;
            border-radius: 6px;
            border: 1px solid #00c8ff;
        """)
        self.original_image_layout.addWidget(self.original_image_label)
        self.original_image_group.setLayout(self.original_image_layout)
        self.left_panel.addWidget(self.original_image_group)

        # 检测结果图像显示（带发光边框）
        self.result_image_group = QGroupBox("检测结果")
        self.result_image_group.setStyleSheet(self.get_groupbox_style())
        self.result_image_layout = QVBoxLayout()
        self.result_image_label = QLabel()
        self.result_image_label.setAlignment(Qt.AlignCenter)
        self.result_image_label.setMinimumSize(640, 360)
        self.result_image_label.setStyleSheet("""
            background-color: #0f0f1a;
            border-radius: 6px;
            border: 1px solid #00c8ff;
        """)
        self.result_image_layout.addWidget(self.result_image_label)
        self.result_image_group.setLayout(self.result_image_layout)
        self.left_panel.addWidget(self.result_image_group)

        # 右侧面板 (控制面板)
        self.right_panel = QVBoxLayout()
        self.right_panel.setSpacing(15)
        self.content_layout.addLayout(self.right_panel, 35)  # 右侧占35%

        # 模型选择（科技感样式）
        self.model_group = QGroupBox("模型设置")
        self.model_group.setStyleSheet(self.get_groupbox_style())
        self.model_layout = QVBoxLayout()
        self.model_layout.setSpacing(10)
        self.model_layout.setContentsMargins(12, 15, 12, 12)

        self.model_layout.addWidget(self.get_styled_label("选择模型:"))

        self.model_combo = QComboBox()
        self.model_combo.setStyleSheet(self.get_combo_style())
        self.model_combo.addItems(["best"])
        self.model_layout.addWidget(self.model_combo)

        self.model_group.setLayout(self.model_layout)
        self.right_panel.addWidget(self.model_group)

        # 检测参数（科技感滑块）
        self.params_group = QGroupBox("检测参数")
        self.params_group.setStyleSheet(self.get_groupbox_style())
        self.params_layout = QVBoxLayout()
        self.params_layout.setSpacing(10)
        self.params_layout.setContentsMargins(12, 15, 12, 12)

        # 置信度阈值
        self.confidence_label = self.get_styled_label("置信度阈值: 0.25")
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setStyleSheet(self.get_slider_style())
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(25)
        self.confidence_spinbox = QDoubleSpinBox()
        self.confidence_spinbox.setStyleSheet(self.get_spinbox_style())
        self.confidence_spinbox.setRange(0.0, 1.0)
        self.confidence_spinbox.setSingleStep(0.05)
        self.confidence_spinbox.setValue(0.25)

        # IoU阈值
        self.iou_label = self.get_styled_label("IoU阈值: 0.45")
        self.iou_slider = QSlider(Qt.Horizontal)
        self.iou_slider.setStyleSheet(self.get_slider_style())
        self.iou_slider.setRange(0, 100)
        self.iou_slider.setValue(45)
        self.iou_spinbox = QDoubleSpinBox()
        self.iou_spinbox.setStyleSheet(self.get_spinbox_style())
        self.iou_spinbox.setRange(0.0, 1.0)
        self.iou_spinbox.setSingleStep(0.05)
        self.iou_spinbox.setValue(0.45)

        self.params_layout.addWidget(self.confidence_label)
        self.params_layout.addWidget(self.confidence_slider)
        self.params_layout.addWidget(self.confidence_spinbox)
        self.params_layout.addWidget(self.iou_label)
        self.params_layout.addWidget(self.iou_slider)
        self.params_layout.addWidget(self.iou_spinbox)

        self.params_group.setLayout(self.params_layout)
        self.right_panel.addWidget(self.params_group)

        # 功能按钮（带悬停发光效果）
        self.buttons_group = QGroupBox("功能控制")
        self.buttons_group.setStyleSheet(self.get_groupbox_style())
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setSpacing(8)
        self.buttons_layout.setContentsMargins(12, 15, 12, 12)

        self.image_btn = self.create_button("图片检测", "#00c8ff")
        self.video_btn = self.create_button("视频检测", "#00a0c0")
        self.camera_btn = self.create_button("摄像头检测", "#00c8a0")
        self.stop_btn = self.create_button("停止检测", "#ff4a4a")
        self.save_btn = self.create_button("保存结果", "#a04aff")

        self.buttons_layout.addWidget(self.image_btn)
        self.buttons_layout.addWidget(self.video_btn)
        self.buttons_layout.addWidget(self.camera_btn)
        self.buttons_layout.addWidget(self.stop_btn)
        self.buttons_layout.addWidget(self.save_btn)

        self.buttons_group.setLayout(self.buttons_layout)
        self.right_panel.addWidget(self.buttons_group)

        # 检测结果表格（科技感表格）
        self.results_group = QGroupBox("检测结果详情")
        self.results_group.setStyleSheet(self.get_groupbox_style())
        self.results_layout = QVBoxLayout()
        self.results_layout.setContentsMargins(12, 15, 12, 12)

        self.results_table = QTableWidget()
        self.results_table.setStyleSheet(self.get_table_style())
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["类别", "置信度", "位置(x)", "位置(y)"])
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setColumnWidth(0, 120)
        self.results_table.setColumnWidth(1, 100)
        self.results_table.setColumnWidth(2, 100)
        self.results_table.setColumnWidth(3, 100)
        # 设置表格最小高度，增大结果区域
        self.results_table.setMinimumHeight(250)

        self.results_layout.addWidget(self.results_table)
        self.results_group.setLayout(self.results_layout)
        self.right_panel.addWidget(self.results_group)

        # 状态栏（科技感样式）
        self.status_bar = self.statusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: #0f0f1a;
                color: #00c8ff;
                border-top: 1px solid #00c8ff;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                font-size: 12px;
                padding-left: 10px;
                letter-spacing: 0.5px;
            }
        """)
        self.status_bar.showMessage("系统就绪 | 准备检测")

        # 添加窗口大小调整手柄（透明样式）
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("""
            QSizeGrip {
                width: 16px;
                height: 16px;
                background: transparent;
            }
        """)
        self.status_bar.addPermanentWidget(self.size_grip)

        # 连接信号和槽
        self.confidence_slider.valueChanged.connect(self.update_confidence)
        self.confidence_spinbox.valueChanged.connect(self.update_confidence_slider)
        self.iou_slider.valueChanged.connect(self.update_iou)
        self.iou_spinbox.valueChanged.connect(self.update_iou_slider)

    def create_title_button(self, text, color):
        btn = QToolButton()
        btn.setText(text)
        btn.setFixedSize(24, 24)
        btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }}
            QToolButton:hover {{
                background-color: {color};
                color: white;
                box-shadow: 0 0 8px {color};
            }}
            QToolButton:pressed {{
                background-color: {self.darken_color(color, 20)};
            }}
        """)
        return btn

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.showMaximized()
            self.maximize_btn.setText("❐")

    def get_groupbox_style(self):
        return """
            QGroupBox {
                background-color: #0f0f1a;
                border-radius: 8px;
                border: 1px solid #00c8ff;
                margin-top: 0px;
                padding-top: 12px;
                color: #00c8ff;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """

    def get_combo_style(self):
        return """
            QComboBox {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #00c8ff;
                border-radius: 5px;
                padding: 6px;
                min-width: 100px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(arrow_down.png);
                width: 10px;
                height: 10px;
            }
            QComboBox QAbstractItemView {
                background-color: #0f0f1a;
                color: #e0e0e0;
                selection-background-color: #00a0c0;
                border: 1px solid #00c8ff;
                border-radius: 5px;
                outline: none;
            }
        """

    def get_slider_style(self):
        return """
            QSlider::groove:horizontal {
                height: 6px;
                background: #1a1a2a;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00a0c0, stop:1 #00c8ff);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qradialgradient(
                    cx:0.5, cy:0.5, radius:0.5,
                    fx:0.5, fy:0.5,
                    stop:0 #00c8ff, stop:1 #0080a0
                );
                border: 1px solid #00e8ff;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
        """

    def get_spinbox_style(self):
        return """
            QDoubleSpinBox {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #00c8ff;
                border-radius: 5px;
                padding: 6px;
                font-size: 12px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 18px;
                border: none;
            }
            QDoubleSpinBox::up-arrow, QDoubleSpinBox::down-arrow {
                width: 7px;
                height: 7px;
            }
        """

    def get_table_style(self):
        return """
            QTableWidget {
                background-color: #0f0f1a;
                color: #e0e0e0;
                border: 1px solid #00c8ff;
                border-radius: 6px;
                gridline-color: #1a1a2a;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #1a1a2a;
            }
            QTableWidget::item:selected {
                background-color: #00a0c0;
                color: white;
            }
            QHeaderView::section {
                background-color: #1a1a2a;
                color: #00c8ff;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
            QScrollBar:vertical {
                background: #0f0f1a;
                width: 10px;
                margin: 0px;
                border: 1px solid #00c8ff;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #00a0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
        """

    def create_button(self, text, color):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
                min-height: 40px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color, 10)};
                color: white;
                border: 1px solid {self.lighten_color(color, 20)};
                box-shadow: 0 0 10px {color};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 10)};
                border: 1px solid {self.lighten_color(color, 30)};
            }}
            QPushButton:disabled {{
                background-color: #1a1a2a;
                color: #6a6a7a;
                border: 1px solid #3a3a4a;
            }}
        """)
        return btn

    def lighten_color(self, hex_color, percent):
        color = QColor(hex_color)
        return color.lighter(100 + percent).name()

    def darken_color(self, hex_color, percent):
        color = QColor(hex_color)
        return color.darker(100 + percent).name()

    def get_styled_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            color: #a0a0b0;
            font-size: 13px;
            padding: 2px 0;
            letter-spacing: 0.5px;
        """)
        return label

    def update_confidence(self, value):
        confidence = value / 100.0
        self.confidence_spinbox.setValue(confidence)
        self.confidence_label.setText(f"置信度阈值: {confidence:.2f}")

    def update_confidence_slider(self, value):
        self.confidence_slider.setValue(int(value * 100))

    def update_iou(self, value):
        iou = value / 100.0
        self.iou_spinbox.setValue(iou)
        self.iou_label.setText(f"IoU阈值: {iou:.2f}")

    def update_iou_slider(self, value):
        self.iou_slider.setValue(int(value * 100))

    def display_image(self, label, image):
        if image is not None:
            h, w, ch = image.shape
            bytes_per_line = ch * w
            q_img = QImage(image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            label.setPixmap(pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def clear_results(self):
        self.results_table.setRowCount(0)

    def add_detection_result(self, class_name, confidence, x, y):
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        items = [
            QTableWidgetItem(class_name),
            QTableWidgetItem(f"{confidence:.2f}"),
            QTableWidgetItem(f"{x:.1f}"),
            QTableWidgetItem(f"{y:.1f}")
        ]

        for i, item in enumerate(items):
            item.setTextAlignment(Qt.AlignCenter)
            item.setForeground(QColor("#ffffff"))
            self.results_table.setItem(row, i, item)

    def update_status(self, message):
        self.status_bar.showMessage(f"状态: {message} | 最后更新: {time.strftime('%H:%M:%S')}")


