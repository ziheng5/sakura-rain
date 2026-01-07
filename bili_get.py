from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QSize, QRect, QDateTime, QTimer
from PySide6.QtGui import QPainter, QPaintEvent, QIcon, QFont, QMouseEvent, QBrush, QPen, QRegion, QColor
import requests
import re
import ffmpeg
import os
import time
from private_widgets import CustomTitleBar, MyDialog


ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')

class Bili_Frame(QtWidgets.QFrame):
    """
    B 站部分功能主界面设计部分
    """
    def __init__(self):
        super().__init__()
        self.mode0 = '爬取单个视频'
        self.mode = 0
        self.bv = ''
        self.path = ''

        # 初始化
        self._left_btn_pressed = False

        title_Bar = CustomTitleBar('B站小帮手   ฅ^•ω•^ฅ', self)
        centralWidget = QtWidgets.QWidget()

        # 食用指南那一行
        first_line = QtWidgets.QHBoxLayout()
        self.go_home = QtWidgets.QPushButton('🏠 主页面')
        guide = QtWidgets.QPushButton('📖 食用指南')
        guide.setStyleSheet("QPushButton:hover{background:#774C5E;}")
        guide.clicked.connect(self.open_new_window)
        first_line.addWidget(self.go_home)
        first_line.addSpacing(10)
        first_line.addWidget(guide)

        # 输入BV号的那一行Layout
        BV_layout = QtWidgets.QHBoxLayout()
        tip_label = QtWidgets.QLabel('请输入BV号：')
        tip_label.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        self.put_BV = QtWidgets.QLineEdit()
        self.put_BV.setPlaceholderText('在此输入BV号喵')
        self.put_BV.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold; ')
        self.search_button = QtWidgets.QPushButton('开始获取')
        self.search_button.setStyleSheet("QPushButton:hover{background:#774C5E;}")
        BV_layout.addWidget(tip_label)
        BV_layout.addWidget(self.put_BV)
        BV_layout.addSpacing(10)
        BV_layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.start)
        tip_label.setStyleSheet("""
                        QLabel {
                            font-family: Microsoft Yahei;
                            font-size: 10pt;
                            font-weight: bold;
                        }
                    """)

        # 输入文件路径的那一行的Layout
        path_layout = QtWidgets.QHBoxLayout()
        self.path_tip = QtWidgets.QLabel('请输入下载路径：')
        self.path_tip.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        self.put_path = QtWidgets.QLineEdit()
        self.put_path.setPlaceholderText('在此输入下载路径喵')
        self.put_path.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        path_layout.addWidget(self.path_tip)
        path_layout.addWidget(self.put_path)

        # 爬取方式选择
        mode_tip = QtWidgets.QLabel('模式选择')
        mode_tip.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        mode_layout = QtWidgets.QVBoxLayout()
        self.button0 = QtWidgets.QComboBox()
        self.button0.addItems(['爬取单个视频', '（施工中）'])
        self.button0.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        self.button0.currentIndexChanged.connect(self.choose_mode0)

        # 模式选择单选按钮
        self.buttongroup = QtWidgets.QButtonGroup()
        button1 = QtWidgets.QRadioButton('模式1', centralWidget)
        button1.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        button2 = QtWidgets.QRadioButton('模式2', centralWidget)
        button2.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        button3 = QtWidgets.QRadioButton('模式3', centralWidget)
        button3.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        button4 = QtWidgets.QRadioButton('模式4', centralWidget)
        button4.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        self.buttongroup.addButton(button1, 1)
        self.buttongroup.addButton(button2, 2)
        self.buttongroup.addButton(button3, 3)
        self.buttongroup.addButton(button4, 4)
        mode_layout.addWidget(button1)
        mode_layout.addWidget(button2)
        mode_layout.addWidget(button3)
        mode_layout.addWidget(button4)
        self.buttongroup.buttonClicked.connect(self.choose_mode)
        main_mode = QtWidgets.QVBoxLayout()
        main_mode.addWidget(self.button0)
        main_mode.addLayout(mode_layout)

        # 进程窗口与进度条
        process_layout = QtWidgets.QVBoxLayout()
        bottom_layout = QtWidgets.QHBoxLayout()
        self.text_output = QtWidgets.QTextBrowser()
        self.process = QtWidgets.QProgressBar()
        self.process.setRange(0, 4)
        process_layout.addWidget(self.text_output)
        process_layout.addWidget(self.process)
        self.process.setStyleSheet(u"QProgressBar::chunk\n"
                                    "{\n"
                                    "border-radius:11px;\n"
                                    "background:qlineargradient(spread:pad,x1:0,y1:0,x2:1,y2:0,stop:0 #FFCCE5,stop:1  #FFCCE5);\n"
                                    "}\n"
                                    "QProgressBar#progressBar\n"
                                    "{\n"
                                    "height:22px;\n"
                                    "text-align:center;/*\u6587\u672c\u4f4d\u7f6e*/\n"
                                    "font-size:14px;\n"
                                    "color:white;\n"
                                    "border-radius:11px;\n"
                                    "background: #000000 ;\n"
                                    "}")
        bottom_layout.addLayout(main_mode)
        bottom_layout.addLayout(process_layout)
        main_mode.setContentsMargins(0, 0, 10, 0)
        mode_layout.setContentsMargins(10, 0, 0, 0)

        # 创建主Layout
        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(title_Bar)
        self.block_line = QtWidgets.QLabel('')
        main_layout.addWidget(self.block_line)
        main_layout.addLayout(first_line)
        main_layout.addLayout(path_layout)
        main_layout.addLayout(BV_layout)
        main_layout.addLayout(bottom_layout)
        main_layout.setContentsMargins(20, 15, 20, 15)

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
        # rect = self.rect()
        # color = QColor(255, 255, 255)  # Set the desired background color
        # painter.setBrush(QBrush(color))
        # painter.setPen(Qt.NoPen)
        # painter.drawRoundedRect(rect, 20, 20)



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

    def open_new_window(self):
        # 实例化一个对话框类

        self.dlg = MyDialog('bili')
        # 显示对话框，代码阻塞在这里，
        # 等待对话框关闭后，才能继续往后执行
        self.dlg.exec()

    def choose_mode0(self):
        mode0 = self.button0.currentText()
        if mode0 == '爬取单个视频':
            w = QDateTime.currentDateTime()
            w = w.toString('yyyy-MM-dd hh:mm:ss dddd')
            w = w + '\n切换模式：爬取单个视频\n'
            self.text_output.append(w)
        elif mode0 == '爬取视频合集':
            w = QDateTime.currentDateTime()
            w = w.toString('yyyy-MM-dd hh:mm:ss dddd')
            w = w + '\n切换模式：爬取视频合集\n'
            self.text_output.append(w)

    def choose_mode(self, item):
        choice = int(item.text()[-1])
        self.mode = choice
        a = QDateTime.currentDateTime()
        a = a.toString('yyyy-MM-dd hh:mm:ss dddd')
        a = a + '\n选择了模式' + str(choice) + '喵~\n'
        self.text_output.append(a)

    def get_path(self):
        path = self.put_path.text()
        self.path = path.replace('"', '')
        self.path = path.replace('\\', '/')
        self.bv = self.put_BV.text()
        # print(self.path)
        # print(self.bv)

    def start(self):
        self.process.reset()
        # self.pro = progress_page()
        # self.pro.exec()

        if self.mode == 0:
            # print('请选择模式喵！')
            q = '请选择模式喵！\n'
            self.text_output.append(q)


        else:
            path = self.put_path.text()
            self.path = path.replace('"', '')
            self.path = path.replace('\\', '/')
            self.bv = self.put_BV.text()

            if self.bv == '':
                self.text_output.append('请输入BV号喵！\n')
                return

            if path == '':
                self.text_output.append('请输入下载路径喵！\n')
                return

            b = QDateTime.currentDateTime()
            b = b.toString('yyyy-MM-dd hh:mm:ss dddd')
            b = b + '\n正在初始化喵~\n'
            self.text_output.append(b)

            headers = {
                'Referer': 'https://www.bilibili.com/',
                'Cookie': 'buvid3=F2C086D6-980D-4B08-2039-90451B86FC5503334infoc; b_nut=1706971003; CURRENT_FNVAL=4048; _uuid=27EA6B36-B49E-10495-7266-22AEF10B445BA04197infoc; buvid4=AF72FD25-BDBA-85A0-81DA-0ED41CCBC43604473-024020314-rnWmI1GPxhMVnt9%2Fucqn7Pyj8YqnYHfkGc7OH4Iju7OsT2P%2BCb4vmMfNTHqQwYYh; rpdid=0zbfVHh5Qc|16Cmid9l|3wc|3w1Rwh8p; hit-dyn-v2=1; enable_web_push=DISABLE; header_theme_version=CLOSE; DedeUserID=1386461614; DedeUserID__ckMd5=044cac87dfcee9c0; FEED_LIVE_VERSION=V8; CURRENT_QUALITY=64; buvid_fp_plain=undefined; fingerprint=cd288fc41c970be741e38da4c6248870; buvid_fp=cd288fc41c970be741e38da4c6248870; home_feed_column=5; PVID=2; b_lsid=CDDF7293_18FF1A8458D; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; bp_t_offset_1386461614=940200665075941396; browser_resolution=1920-302; SESSDATA=b2e74371%2C1733298294%2C6fa87%2A61CjDz4czyXoBL_KyF_Xo4uYNBdr7CWi_iXAd9Bk0vBfbBlR96Qe8onvgbPc7-tQthIxASVjdZYzMwMGtRYVBTdVNaQmJla05QNU9XcFZRVlNvLU1VRTd4Ui0zWENfcXUxVDBOajZZc05WemNaVV8zdFZpV0NZT2FvanlCck9PaHhpSXFaNDlQekl3IIEC; bili_jct=632ff8691d5cdfdb4fc2d576eac35376; sid=qejryjq2',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
            }

            url = 'https://www.bilibili.com/video/' + self.bv + '/?spm_id_from=333.788.recommend_more_video.0&vd_source=e019291aba8990e4938de7d22ea58de3'
            direct = requests.get(url, headers=headers).text
            pattern = re.compile('"baseUrl":"(.*?)"')
            pattern1 = re.compile('"title":"(.*?)",')
            lis = pattern.findall(direct)
            lis0 = pattern1.findall(direct)
            title = lis0[0].replace(' ', '_')

            videoU = lis[0]
            audioU = lis[-1]

            c = QDateTime.currentDateTime()
            c = c.toString('yyyy-MM-dd hh:mm:ss dddd')
            c = c + '\n初始化完成喵~\n'
            self.text_output.append(c)
            self.process.setValue(1)
            time.sleep(1)


            if self.mode > 2:

                video = requests.get(videoU, headers=headers).content
                audio = requests.get(audioU, headers=headers).content

                if self.mode == 4:

                    try:
                        # print(time.ctime(), "模式四开始运行喵~")
                        d = QDateTime.currentDateTime()
                        d = d.toString('yyyy-MM-dd hh:mm:ss dddd')
                        d = d + '\n模式四开始运行，请稍等喵~\n'
                        self.process.setValue(2)
                        self.text_output.append(d)
                        time.sleep(1)

                        with open(self.path + '/' + 'audio.mp3', 'wb') as f:
                            f.write(audio)
                            f.close()
                        with open(self.path + '/' + 'video.mp4', 'wb') as f:
                            f.write(video)
                            f.close()

                        audio = ffmpeg.input(f'{self.path}/audio.mp3')
                        video = ffmpeg.input(f'{self.path}/video.mp4')
                        # print(time.ctime(), "正在合并音视频喵~\n")
                        e = QDateTime.currentDateTime()
                        e = e.toString('yyyy-MM-dd hh:mm:ss dddd')
                        e = e + "\n正在合并音视频，请稍等喵~\n"
                        self.text_output.append(e)
                        self.process.setValue(3)
                        time.sleep(1)

                        out = ffmpeg.output(video, audio, f'{self.path}/{title}.mp4', vcodec='libx264', acodec='aac', video_bitrate='5000k', crf=18)
                        out.run()
                        # video_clip = VideoFileClip(f'{self.path}/video.mp4')
                        # audio_clip = AudioFileClip(f'{self.path}/audio.mp3')
                        # print(time.ctime(), "正在合并音视频喵~")
                        # e = time.ctime() + "  正在合并音视频，请稍等喵~"
                        # self.text_output.append(e)
                        #
                        # video_clip = video_clip.set_audio(audio_clip)
                        # video_clip.write_videofile(self.path + '/' + title + ".mp4")

                        os.remove(self.path + '/' + 'audio.mp3')
                        os.remove(self.path + '/' + 'video.mp4')

                        # print(time.ctime(), '视频下载成功了喵~')
                        f = QDateTime.currentDateTime()
                        f = f.toString('yyyy-MM-dd hh:mm:ss dddd')
                        f = f + '\n视频下载成功了喵~\n'
                        self.text_output.append(f)
                        self.process.setValue(4)

                    except:

                        # print(time.ctime(), '出错了喵QAQ')
                        g = QDateTime.currentDateTime()
                        g = g.toString('yyyy-MM-dd hh:mm:ss dddd')
                        g = g + '\n出错了喵QAQ\n'
                        self.text_output.append(g)

                else:

                    try:

                        # print(time.ctime(), '模式三开始运行喵~')
                        h = QDateTime.currentDateTime()
                        h = h.toString('yyyy-MM-dd hh:mm:ss ')
                        h = h + '\n模式三开始运行喵~\n'
                        self.text_output.append(h)
                        self.process.setValue(2)
                        time.sleep(1)

                        with open(self.path + '/' + title + '_audio.mp3', 'wb') as f:
                            f.write(audio)
                            f.close()
                        with open(self.path + '/' + title + '_video.mp4', 'wb') as f:
                            f.write(video)
                            f.close()
                        # print(time.ctime(), '音频和画面下载成功了喵！')
                        i = QDateTime.currentDateTime()
                        i = i.toString('yyyy-MM-dd hh:mm:ss dddd')
                        i = i + '\n音频和画面下载成功了喵！\n'
                        self.text_output.append(i)
                        self.process.setValue(4)

                    except:

                        # print(time.ctime(), '出错了喵QAQ')
                        j = QDateTime.currentDateTime()
                        j = j.toString('yyyy-MM-dd hh:mm:ss dddd')
                        j = j + '\n出错了喵QAQ\n'
                        self.text_output.append(j)

            else:

                if self.mode == 2:

                    try:

                        # print(time.ctime(), '模式二开始运行喵~')
                        k = QDateTime.currentDateTime()
                        k = k.toString('yyyy-MM-dd hh:mm:ss dddd')
                        k = k + '\n模式二开始运行喵~\n'
                        self.text_output.append(k)
                        self.process.setValue(2)
                        time.sleep(1)

                        video = requests.get(videoU, headers=headers).content
                        with open(self.path + '/' + title + '_video.mp4', 'wb') as f:
                            f.write(video)
                            f.close()
                        # print(time.ctime(), '画面下载成功了喵！')
                        l = QDateTime.currentDateTime()
                        l = l.toString('yyyy-MM-dd hh:mm:ss dddd')
                        l = l + '\n画面下载成功了喵！\n'
                        self.text_output.append(l)
                        self.process.setValue(4)


                    except:

                        # print(time.ctime(), '出错了喵QAQ')
                        m = QDateTime.currentDateTime()
                        m = m.toString('yyyy-MM-dd hh:mm:ss dddd')
                        m = m + '\n出错了喵QAQ\n'
                        self.text_output.append(m)

                elif self.mode == 1:

                    try:

                        # print(time.ctime(), '模式一开始运行喵~')
                        n = QDateTime.currentDateTime()
                        n = n.toString('yyyy-MM-dd hh:mm:ss dddd')
                        n = n + '\n模式一开始运行喵~\n'
                        self.text_output.append(n)
                        self.process.setValue(2)
                        time.sleep(1)

                        audio = requests.get(audioU, headers=headers).content
                        with open(self.path + '/' + title + '_audio.mp3', 'wb') as f:
                            f.write(audio)
                            f.close()
                        # print(time.ctime(), '音频下载成功了喵！')
                        o = QDateTime.currentDateTime()
                        o = o.toString('yyyy-MM-dd hh:mm:ss dddd')
                        o = o + '\n音频下载成功了喵！\n'
                        self.text_output.append(o)
                        self.process.setValue(4)

                    except:

                        # print(time.ctime(), '出错了喵QAQ')
                        p = QDateTime.currentDateTime()
                        p = p.toString('yyyy-MM-dd hh:mm:ss dddd')
                        p = p + '\n出错了喵QAQ\n'
                        (self
                         .text_output.append(p))
