# TODO 目前该文件还需要完成的工作包括：
## 1. 目前遇到一个严重的功能问题：樱花动漫每隔一段时间会改变 .ts 文件的前缀以及引导 .ts 文件的文件，目前的想法是：长期观察，看该规律是否循环
## --> 新线索，老的 .ts 引导文件中包含了新的 .ts 引导文件的后缀
## 2. 另一个思路：采用 drissionpage 直接锁定网页元素，看是否可以正确定位

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QMainWindow, QVBoxLayout, QFrame
from PySide6.QtCore import Qt, QSize, QRect, QDateTime, QTimer
from PySide6.QtGui import QPainter, QPaintEvent, QIcon, QFont, QMouseEvent, QBrush, QPen, QRegion, QColor, QPixmap
from qt_material import apply_stylesheet
import sys
from utils.bili_get import *
from utils.sakura_get import Sakura_Frame


# from sakura_get import *


class welcome_Window(QtWidgets.QMainWindow):
    """
    Sakura Rain 的欢迎界面
    """
    def __init__(self):
        super().__init__()

        # 初始化
        self.window().setStyleSheet(u"color:white; border-radius: 5px")
        self.setWindowTitle('Sakura Rain')
        self.setWindowFlags(Qt.FramelessWindowHint)    # 隐藏原版标题栏
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(450, 500)
        self._left_btn_pressed = False

        title_Bar = CustomTitleBar('Sakura Rain', self)
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        self.stackedWidget = QtWidgets.QStackedWidget()

        # 在这里创建 Sakura Rain 的 logo
        image_label = QLabel()
        pixmap = QPixmap('./src/logo.png')
        scaled_pixmap = pixmap.scaled(200, 200)
        image_label.setPixmap(scaled_pixmap)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建欢迎界面
        welcome_page = QtWidgets.QFrame()
        welcome_layout = QtWidgets.QVBoxLayout(welcome_page)

        # 创建欢迎界面标题
        welcome_title = QLabel("樱  之  雨")
        welcome_title.setAlignment(Qt.AlignCenter)
        welcome_title.setStyleSheet('font-size: 24px')

        # 在这里创建页面选择的按钮
        sakura_get_button = QtWidgets.QPushButton('樱花动漫（施工中🚧）')
        bili_get_button = QtWidgets.QPushButton('B站')
        sakura_get_button.setStyleSheet("QPushButton:hover{background:#774C5E;}")
        bili_get_button.setStyleSheet("QPushButton:hover{background:#774C5E;}")


        button_line_1 = QtWidgets.QHBoxLayout()
        button_line_1.addSpacing(20)
        button_line_1.addWidget(sakura_get_button)
        button_line_1.addSpacing(20)
        button_line_1.addWidget(bili_get_button)
        button_line_1.addSpacing(30)
    
        main_button_layout = QtWidgets.QVBoxLayout()
        main_button_layout.addLayout(button_line_1)

        # 创建主Layout
        main_layout = QtWidgets.QVBoxLayout(centralWidget)
        welcome_layout.addWidget(title_Bar)
        welcome_layout.addSpacing(30)
        welcome_layout.addWidget(image_label)
        welcome_layout.addWidget(welcome_title)
        welcome_layout.addSpacing(30)
        welcome_layout.addLayout(main_button_layout)
        # 在底部添加可拉伸空间，将内容推到上方
        welcome_layout.addStretch()

        # 其他界面
        bili_page = Bili_Frame()
        sakura_page = Sakura_Frame()
        self.stackedWidget.addWidget(welcome_page)
        self.stackedWidget.addWidget(bili_page)
        self.stackedWidget.addWidget(sakura_page)

        bili_get_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(bili_page))
        bili_page.go_home.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(welcome_page))
        sakura_get_button.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(sakura_page))
        sakura_page.go_home.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(welcome_page))

        # 插入 stacked widget
        main_layout.addWidget(self.stackedWidget)

        # 设置页边距
        welcome_layout.setContentsMargins(20, 15, 20, 15)

        # 启动动画
        self.anim = QtCore.QPropertyAnimation(self.window(), b'geometry')
        self.anim.setDuration(100)
        x = 550
        y = 200
        self.anim.setStartValue(QtCore.QRect(x, y, 450, 500))
        self.anim.setEndValue(QtCore.QRect(x, y-50, 450, 500))
        self.anim.start()


    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the rounded rectangle background
        rect = self.rect()
        color = QColor(255, 255, 255)  # Set the desired background color
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 20, 20)



    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._left_btn_pressed = True

            # 如果支持 QWindow::startSystemMove，就调用
            # 先拿到 QWindow 对象
            window_handle = self.windowHandle()
            if window_handle is not None:
                window_handle.startSystemMove()

            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._left_btn_pressed = False
            event.accept()

    def mouseMoveEvent(self, event):
        # 如果不支持 startSystemMove，就回退到手动移动的方式
        if self._left_btn_pressed:
            # 手动更新位置的逻辑
            # 可能需要考虑 Wayland 环境下 globalPos() 不正确的问题
            pass
        event.accept()



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_pink.xml')

    # ['dark_amber.xml',
    #  'dark_blue.xml',
    #  'dark_cyan.xml',
    #  'dark_lightgreen.xml',
    #  'dark_pink.xml',
    #  'dark_purple.xml',
    #  'dark_red.xml',
    #  'dark_teal.xml',
    #  'dark_yellow.xml',
    #  'light_amber.xml',
    #  'light_blue.xml',
    #  'light_cyan.xml',
    #  'light_cyan_500.xml',
    #  'light_lightgreen.xml',
    #  'light_pink.xml',
    #  'light_purple.xml',
    #  'light_red.xml',
    #  'light_teal.xml',
    #  'light_yellow.xml']

    window = welcome_Window()
    window.show()
    app.exec()
