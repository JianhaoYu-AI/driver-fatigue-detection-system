# LoginWindow.py
import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("译路畅行驾驶行为监测系统-用户登录")
        self.setWindowIcon(QIcon("icon.png"))
        self.resize(400, 500)
        self.setup_ui()
        self.load_accounts()

    def setup_ui(self):
        self.setStyleSheet("""
            background: #0a0a12;
            color: #e0e0e0;
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel("译路畅行驾驶行为监测系统登录")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #00c8ff;
            padding-bottom: 10px;
            border-bottom: 1px solid #00c8ff;
        """)
        title_label.setAlignment(Qt.AlignCenter)

        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: #0f0f1a;
                border-radius: 8px;
                border: 1px solid #00c8ff;
                padding: 20px;
            }
        """)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)

        username_label = QLabel("用户名:")
        username_label.setStyleSheet("font-size: 14px; color: #a0a0b0;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("请输入用户名")
        self.username_input.setStyleSheet("""
            QLineEdit {
                background: #1a1a2a;
                border: 1px solid #00a0c0;
                border-radius: 4px;
                padding: 10px;
                color: #ffffff;
                font-size: 14px;
            }
        """)

        password_label = QLabel("密码:")
        password_label.setStyleSheet("font-size: 14px; color: #a0a0b0;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.username_input.styleSheet())

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.login_btn = QPushButton("登录")
        self.login_btn.setStyleSheet(self.get_button_style("#00c8ff"))
        self.login_btn.setFixedHeight(40)

        self.register_btn = QPushButton("注册")
        self.register_btn.setStyleSheet(self.get_button_style("#00a0c0"))
        self.register_btn.setFixedHeight(40)

        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.register_btn)

        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_input)
        form_layout.addLayout(button_layout)
        form_frame.setLayout(form_layout)

        main_layout.addWidget(title_label)
        main_layout.addWidget(form_frame)
        main_layout.addStretch()

        self.setLayout(main_layout)

        self.login_btn.clicked.connect(self.handle_login)
        self.register_btn.clicked.connect(self.handle_register)

    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: transparent;
                color: {color};
                border: 1px solid {color};
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
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
        """

    def lighten_color(self, hex_color, percent):
        color = QColor(hex_color)
        return color.lighter(100 + percent).name()

    def darken_color(self, hex_color, percent):
        color = QColor(hex_color)
        return color.darker(100 + percent).name()

    def load_accounts(self):
        self.accounts = {}
        if os.path.exists("accounts.json"):
            try:
                with open("accounts.json", "r") as f:
                    self.accounts = json.load(f)
            except:
                pass

    def save_accounts(self):
        with open("accounts.json", "w") as f:
            json.dump(self.accounts, f)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空！")
            return

        if username in self.accounts and self.accounts[username] == password:
            self.accept()  # 关闭对话框并返回QDialog.Accepted
        else:
            QMessageBox.warning(self, "错误", "用户名或密码错误！")

    def handle_register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空！")
            return

        if username in self.accounts:
            QMessageBox.warning(self, "警告", "用户名已存在！")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "警告", "密码长度至少为6位！")
            return

        self.accounts[username] = password
        self.save_accounts()
        QMessageBox.information(self, "成功", "注册成功！")