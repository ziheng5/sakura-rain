from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QSize, QRect, QDateTime, QTimer
from PySide6.QtGui import QPainter, QPaintEvent, QIcon, QFont, QMouseEvent, QBrush, QPen, QRegion, QColor
import random
import webbrowser


class CustomTitleBar(QtWidgets.QWidget):
    """
    这是标题栏部件的设计
    """
    def __init__(self, word, parent=None):
        super().__init__(parent)

        self.setFixedHeight(30)
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.titleLabel = QtWidgets.QLabel(word)
        self.titleLabel.setStyleSheet("color: white; font-size: 15pt; font-weight: bold;")
        self.minimizeButton = QtWidgets.QPushButton("")
        self.minimizeButton.setFixedSize(30, 30)
        self.minimizeButton.setStyleSheet(
            "QPushButton{border-image:url('./images/min.png');background:#363636;border-radius:10px;}"  # 29c941
            "QPushButton:hover{background:#1ac033;}"
        )
        self.minimizeButton.clicked.connect(self.minimize)

        self.maximizeButton = QtWidgets.QPushButton("")
        self.maximizeButton.setFixedSize(30, 30)
        self.maximizeButton.setStyleSheet(
            "QPushButton{border-image:url('./images/max.png');background:#363636;border-radius:10px;}"
            "QPushButton:hover{background:#ecae27;}"
        )
        self.maximizeButton.clicked.connect(self.maximize_restore)

        self.closeButton = QtWidgets.QPushButton("")
        self.closeButton.setFixedSize(30, 30)
        self.closeButton.setStyleSheet(
            "QPushButton{border-image:url('./images/close.png');background:#363636;border-radius:10px;}"
            "QPushButton:hover{background:#eb4845;}"
        )
        self.closeButton.clicked.connect(self.close)

        layout.addWidget(self.titleLabel)
        layout.addStretch()
        layout.addWidget(self.minimizeButton)
        layout.addWidget(self.maximizeButton)
        layout.addWidget(self.closeButton)

        self.setLayout(layout)
        self.start = None
        self.pressing = False
        self._left_btn_pressed = False

    def minimize(self):
        # 界面最小化
        self.window().showMinimized()

    def maximize_restore(self):
        # 界面最大化
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def close(self):
        # 关闭界面
        self.window().close()

    def mousePressEvent(self, event: QMouseEvent):
        # 光标按下处理
        if event.button() == Qt.LeftButton:
            self.start = event.globalPos()
            self.pressing = True

    def mouseMoveEvent(self, event: QMouseEvent):
        # 光标移动处理
        if self.pressing:
            self.window().move(self.window().pos() + event.globalPos() - self.start)
            self.start = event.globalPos()

    def mouseReleaseEvent(self, event: QMouseEvent):
        # 光标松开处理
        self.pressing = False


class MyDialog(QtWidgets.QDialog):
    """
    食用指南界面的设计部分
    """
    def __init__(self, typ):
        super().__init__()
        self.setWindowTitle('食用指南')
        self.resize(500, 400)
        self.setWindowOpacity(0.9)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self._left_btn_pressed = False
        self.typ = typ

        self.setMinimumSize(QSize(300, 100))
        
        if self.typ == 'bili':
            titleBar = CustomTitleBar('❓ 食用指南', self)

            self.second_layout = QtWidgets.QVBoxLayout(self)
            tips1 = QtWidgets.QLabel('a. 本工具可以通过输入BV号，直接获取相应的B站音视频资源喵')
            tips2 = QtWidgets.QLabel('b. 在获取视频资源之前，请务必先输入下载位置喵（填入绝对路径）')
            tips3 = QtWidgets.QLabel('   【可以右键想要使用的文件夹，点击复制文件地址，粘贴到框里】')
            tips4 = QtWidgets.QLabel('c. 爬取时有四种模式喵：')
            tips5 = QtWidgets.QLabel('   1. 模式一：仅下载音频')
            tips6 = QtWidgets.QLabel('   2. 模式二：仅下载视频画面')
            tips7 = QtWidgets.QLabel('   3. 模式三：分别下载音频和视频画面')
            tips8 = QtWidgets.QLabel('   4. 模式四：下载完整的视频')
            tips9 = QtWidgets.QLabel('d. 做完以上工作，就可以开始获取视频了喵~')
            tips10 = QtWidgets.QLabel('【如需定制软件或小工具可联系作者本人：2199325776（QQ号）】')


            tips1.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips2.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips3.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips4.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips5.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips6.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips7.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips8.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips9.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
            tips10.setStyleSheet('font-family: Microsoft Yahei; font-size: 11pt; font-weight: bold')

            do_not_click = QtWidgets.QPushButton('不要点我喵')
            do_not_click.setStyleSheet("QPushButton:hover{background:#774C5E;}")
            do_not_click.clicked.connect(self.dont_click)
            do_not_click.resize(50, 30)

            self.second_layout.addWidget(titleBar)
            self.second_layout.addWidget(tips1)
            self.second_layout.addWidget(tips2)
            self.second_layout.addWidget(tips3)
            self.second_layout.addWidget(tips4)
            self.second_layout.addWidget(tips5)
            self.second_layout.addWidget(tips6)
            self.second_layout.addWidget(tips7)
            self.second_layout.addWidget(tips8)
            self.second_layout.addWidget(tips9)
            self.second_layout.addWidget(tips10)
            # self.second_layout.addWidget(tips11)

            dont = QtWidgets.QHBoxLayout(self)
            dont.addWidget(do_not_click)

            self.second_layout.addLayout(dont)
            self.second_layout.setContentsMargins(20, 20, 20, 20)

        elif self.typ == 'sakura':
            titleBar = CustomTitleBar("❓ 食用指南", self)
            self.page_layout = QtWidgets.QVBoxLayout(self)

            tip1 = QtWidgets.QLabel("请参考仓库主页的 README.md 文件喵")
            tip2 = QtWidgets.QLabel("（小生最近比较忙，暂时没空出时间折腾这个💦）")
            
            tip1.setStyleSheet('font-family: Microsoft Yahei; font-size: 11pt; font-weight: bold')
            tip2.setStyleSheet('font-family: Microsoft Yahei; font-size: 11pt; font-weight: bold')

            self.page_layout.addWidget(titleBar)
            self.page_layout.addWidget(tip1)
            self.page_layout.addWidget(tip2)

            self.page_layout.setContentsMargins(20, 20, 20, 20)

            
            

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the rounded rectangle background
        rect = self.rect()
        # color = QColor(255, 255, 255)  # Set the desired background color
        # painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 20, 20)

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
    #         event.accept()
    #
    # def mouseMoveEvent(self, event):
    #     if event.buttons() & Qt.LeftButton:
    #         self.move(event.globalPosition().toPoint() - self.drag_position)
    #         event.accept()

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


    def dont_click(self):


        play = random.randint(1, 7)

        if play == 6:
            x = random.randint(0, 800)
            y = random.randint(0, 500)
            self.window().move(x, y)

        if play == 5:
            self.anim = QtCore.QPropertyAnimation(self.window(), b'geometry')
            self.anim.setDuration(400)
            x = self.window().x()
            y = self.window().y()
            self.anim.setStartValue(QtCore.QRect(x, y, 500, 400))
            self.anim.setEndValue(QtCore.QRect(x-50, y, 500, 400))
            self.anim.start()

        if play == 4:
            self.anim = QtCore.QPropertyAnimation(self.window(), b'geometry')
            self.anim.setDuration(400)
            x = self.window().x()
            y = self.window().y()
            self.anim.setStartValue(QtCore.QRect(x, y, 500, 400))
            self.anim.setEndValue(QtCore.QRect(x, y+50, 500, 400))
            self.anim.start()

        if play == 3:
            self.anim = QtCore.QPropertyAnimation(self.window(), b'geometry')
            self.anim.setDuration(400)
            x = self.window().x()
            y = self.window().y()
            self.anim.setStartValue(QtCore.QRect(x, y, 500, 400))
            self.anim.setEndValue(QtCore.QRect(x+50, y, 500, 400))
            self.anim.start()

        if play == 2:
            self.anim = QtCore.QPropertyAnimation(self.window(), b'geometry')
            self.anim.setDuration(400)
            x = self.window().x()
            y = self.window().y()
            self.anim.setStartValue(QtCore.QRect(x, y, 500, 400))
            self.anim.setEndValue(QtCore.QRect(x, y-50, 500, 400))
            self.anim.start()

        if play == 1:
            url = "https://www.bilibili.com/video/BV1GJ411x7h7"
            webbrowser.open(url, new=0, autoraise=True)
