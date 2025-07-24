from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt, QSize, QRect, QDateTime, QTimer
from PySide6.QtGui import QPainter, QPaintEvent, QIcon, QFont, QMouseEvent, QBrush, QPen, QRegion, QColor
from PySide6.QtCore import QThread, Signal, QObject
import requests
import re
import ffmpeg
import os
import time
from private_widgets import CustomTitleBar, MyDialog
from page_analysis import get_ep_url
from sakura_download import DownloadWorker


ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')


class Sakura_Frame(QtWidgets.QFrame):
    """
    樱花动漫部分功能主界面设计部分
    """
    def __init__(self):
        super().__init__()
        self.mode0 = '爬取单个视频'
        self.mode = 0
        self.bv = ''
        self.path = ''
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'Cookie': 'HWTOKEN=7d4e4f0a188bdc091c7b110582b3c02f3d524f6f61522e51f102fe191a4f864e1121a24925c15a758a27ee44a1554cffda875db4e62d4199f86fd1d4f8a45d3f; HWIDHASH=9299b36adfd65542d49a528d08c0c877; HWPID=EgyEb9-1UpWocy42ZYif2L7evaR1K1Ka5GMcXOLbl_E'
                }
        self.ep_memory = []
        self.ep_name = ''

        # 初始化
        self._left_btn_pressed = False

        title_Bar = CustomTitleBar('樱花小帮手   ฅ^•ω•^ฅ', self)
        centralWidget = QtWidgets.QWidget()

        # 食用指南那一行
        first_line = QtWidgets.QHBoxLayout()
        self.go_home = QtWidgets.QPushButton('🏠 主页面')
        guide = QtWidgets.QPushButton('❓ 番号怎么找')
        guide.setStyleSheet("QPushButton:hover{background:#774C5E;}")
        guide.clicked.connect(self.open_new_window)
        first_line.addWidget(self.go_home)
        first_line.addSpacing(10)
        first_line.addWidget(guide)

        # 输入BV号的那一行Layout
        BV_layout = QtWidgets.QHBoxLayout()
        tip_label = QtWidgets.QLabel('请输入番号：')
        tip_label.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        self.put_anime_index = QtWidgets.QLineEdit()
        self.put_anime_index.setPlaceholderText('形如 456870/153 喵')
        self.put_anime_index.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold; ')
        self.search_button = QtWidgets.QPushButton('查询')
        self.search_button.setStyleSheet("QPushButton:hover{background:#774C5E;}")
        BV_layout.addWidget(tip_label)
        BV_layout.addWidget(self.put_anime_index)
        BV_layout.addSpacing(10)
        BV_layout.addWidget(self.search_button)
        self.search_button.clicked.connect(self.search)
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
        download_tip = QtWidgets.QLabel('模式选择')
        download_tip.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        download_layout = QtWidgets.QVBoxLayout()
        self.button0 = QtWidgets.QComboBox()
        self.button0.addItems(['单集下载', '？？？'])
        self.button0.setStyleSheet('font-family: Microsoft Yahei; font-size: 10pt; font-weight: bold')
        self.button0.currentIndexChanged.connect(self.choose_mode0)

        # download layout
        self.download_stacked = QtWidgets.QStackedWidget()
        download_layout.addWidget(self.download_stacked)
        page1 = QtWidgets.QFrame()
        page1_layout = QtWidgets.QVBoxLayout(page1)
        page1_title = QtWidgets.QLabel('要下载第几集呢...')
        self.page1_input = QtWidgets.QLineEdit()
        self.page1_input.setPlaceholderText('输入一个数字')
        self.page1_download_button = QtWidgets.QPushButton('开始下载')
        self.page1_download_button.clicked.connect(self.download2)

        page1_layout.addSpacing(30)
        page1_layout.addWidget(page1_title)
        page1_layout.addWidget(self.page1_input)
        page1_layout.addSpacing(30)
        page1_layout.addWidget(self.page1_download_button)
        page1_layout.addSpacing(30)
        self.download_stacked.addWidget(page1)


        main_mode = QtWidgets.QVBoxLayout()
        main_mode.addWidget(self.button0)
        main_mode.addLayout(download_layout)

        # 进程窗口与进度条
        process_layout = QtWidgets.QVBoxLayout()
        bottom_layout = QtWidgets.QHBoxLayout()
        self.text_output = QtWidgets.QTextBrowser()
        h0 = QDateTime.currentDateTime()
        h0 = h0.toString('yyyy-MM-dd hh:mm:ss ')
        h0 = h0 + '\n【Tips】' + '\n在下番之前，请务必先对番名进行查询，以确保下载可以正常运行\n'
        self.text_output.append(h0)

        self.process = QtWidgets.QProgressBar()
        self.process.setRange(0, 100)
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
        download_layout.setContentsMargins(10, 0, 0, 0)

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

        self.dlg = MyDialog('sakura')
        # 显示对话框，代码阻塞在这里，
        # 等待对话框关闭后，才能继续往后执行
        self.dlg.exec()

    def choose_mode0(self):
        mode0 = self.button0.currentText()
        if mode0 == '单集下载':
            w = QDateTime.currentDateTime()
            w = w.toString('yyyy-MM-dd hh:mm:ss dddd')
            w = w + '\n选择了单集下载喵～\n'
            self.text_output.append(w)
        elif mode0 == '多集下载':
            w = QDateTime.currentDateTime()
            w = w.toString('yyyy-MM-dd hh:mm:ss dddd')
            w = w + '\n选择了多集下载喵～（施工中，暂不可用 🚧）\n'
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
        self.bv = self.put_anime_index.text()

    def search(self):
        h = QDateTime.currentDateTime()
        h = h.toString('yyyy-MM-dd hh:mm:ss ')
        h = h + '\n正在查询ing...'
        self.text_output.append(h)

        anime_index = self.put_anime_index.text()

        try:
            anime_title, ep_lis = get_ep_url(anime_index, headers=self.headers)
            self.ep_name = anime_title
            self.ep_memory = ep_lis
            print(ep_lis)
            self.text_output.append('查询成功喵～结果如下：')
            self.text_output.append('- 番名：{}'.format(anime_title))
            self.text_output.append('- 总集数：{}'.format(len(ep_lis)))
            self.text_output.append('(请在确认无误后，在左边选择下载剧集)\n')

        except:
            self.text_output.append('\n查询失败喵，苦路西...')

    def download1(self):
        self.process.reset()
        ep_index = self.page1_input.text()
        if ep_index == '':
            h = QDateTime.currentDateTime()
            h = h.toString('yyyy-MM-dd hh:mm:ss ')
            h = h + '\n忘记输入集数了哦～\n'
            self.text_output.append(h)
        else:
            if len(self.ep_memory) == 0:
                # 没有进行查询操作哦～
                h = QDateTime.currentDateTime()
                h = h.toString('yyyy-MM-dd hh:mm:ss ')
                h = h + '\n忘记进行查询了哦～\n'
                self.text_output.append(h)
            else:
                try:
                    # 开始下载
                    index = int(ep_index)
                    ep_url = self.ep_memory[index-1]

                    h = QDateTime.currentDateTime()
                    h = h.toString('yyyy-MM-dd hh:mm:ss ')
                    h = h + '\n正在下载第' + ep_index + '集喵...\n'
                    self.text_output.append(h)

                    # ===================
                    # 获取 index.m3u8 文件
                    html = requests.get(url=ep_url, headers=self.headers).text
                    print(html)
                    pattern = re.compile("dplayer/\?url=(.*?)'")
                    file_url = pattern.findall(html)[-1]

                    index = requests.get(url=file_url, headers=self.headers).text
                    print(index)
                    num_pattern = re.compile("00(.*?).ts")
                    num_lis = num_pattern.findall(index)
                    print(num_lis)
                    video_length = len(num_lis)
                    print(video_length)

                    base_url = file_url[:-10]
                    print(base_url)
                    full_video = b''
                    for i in range(video_length):
                        piece_url = base_url + '00' + num_lis[i] + '.ts'
                        piece = requests.get(url=piece_url, headers=self.headers).content
                        full_video = full_video + piece
                        processed = int(i / video_length * 100)
                        self.process.setValue(processed)

                    download_path = self.put_path.text() + '/' + self.ep_name + 'ep' + ep_index + '.ts'

                    with open(download_path, 'wb') as f:
                        f.write(full_video)
                        f.close()

                    h = QDateTime.currentDateTime()
                    h = h.toString('yyyy-MM-dd hh:mm:ss ')
                    h = h + '\n下载完成喵：{}\n'.format(download_path)
                    self.text_output.append(h)

                except:
                    h = QDateTime.currentDateTime()
                    h = h.toString('yyyy-MM-dd hh:mm:ss ')
                    h = h + '\n出错了喵～\n'
                    self.text_output.append(h)


    def download2(self):

        # 禁用按钮防止重复点击
        self.page1_download_button.setEnabled(False)
        self.go_home.setEnabled(False)
        self.search_button.setEnabled(False)
        self.process.setValue(0)

        ep_index = self.page1_input.text()
        if ep_index == '':
            h = QDateTime.currentDateTime()
            h = h.toString('yyyy-MM-dd hh:mm:ss ')
            h = h + '\n忘记输入集数了哦～\n'
            self.text_output.append(h)
        else:
            if len(self.ep_memory) == 0:
                # 没有进行查询操作哦～
                h = QDateTime.currentDateTime()
                h = h.toString('yyyy-MM-dd hh:mm:ss ')
                h = h + '\n忘记进行查询了哦～\n'
                self.text_output.append(h)
            else:
                # 开始下载
                index = int(ep_index)
                ep_url = self.ep_memory[index-1]

                h = QDateTime.currentDateTime()
                h = h.toString('yyyy-MM-dd hh:mm:ss ')
                h = h + '\n正在下载第' + ep_index + '集喵...\n'
                self.text_output.append(h)

                # # ===================
                # # 获取 mixed.m3u8 文件
                # html = requests.get(url=ep_url, headers=self.headers).text
                # pattern = re.compile("dplayer/\?url=(.*?)'")
                # file_url = pattern.findall(html)[-1]
                #
                # index = requests.get(url=file_url, headers=self.headers).text
                # processed_index = index.split('\n')[-1]
                # processed_tail = processed_index.replace('mixed.m3u8', '')
                # processed_file_url = file_url.replace('index.m3u8', processed_index)
                # real_index = requests.get(url=processed_file_url, headers=self.headers).text
                # num_lis = real_index.split('\n')
                # processed_num_lis = [i for i in num_lis if '.ts' in i]
                # print(processed_num_lis)
                #
                # video_length = len(processed_num_lis)
                #
                # base_url = file_url[:-10]
                # full_video = b''
                # for i in range(video_length):
                #     piece_url = base_url + processed_tail + processed_num_lis[i]
                #     print(piece_url)
                #     piece = requests.get(url=piece_url, headers=self.headers).content
                #     full_video = full_video + piece
                #     processed = int(i / video_length * 100)
                #     self.process.setValue(processed)
                #
                # download_path = self.put_path.text() + '/' + self.ep_name + 'ep' + ep_index + '.ts'
                #
                # with open(download_path, 'wb') as f:
                #     f.write(full_video)
                #     f.close()

                # 创建线程和工作对象
                self.download_thread = QThread()
                self.worker = DownloadWorker(ep_url, path=self.put_path.text(), ep_name=self.ep_name, ep_index=ep_index)
                self.worker.moveToThread(self.download_thread)

                # 连接信号
                self.worker.progress_updated.connect(self.update_progress)
                self.worker.download_finished.connect(self.on_download_finished)
                self.worker.error_occurred.connect(self.on_download_error)

                # 线程结束时自动清理
                self.download_thread.finished.connect(self.download_thread.deleteLater)

                # 启动线程
                self.download_thread.started.connect(self.worker.download)
                self.download_thread.start()



                # except:
                #     h = QDateTime.currentDateTime()
                #     h = h.toString('yyyy-MM-dd hh:mm:ss ')
                #     h = h + '\n出错了喵～\n'
                #     self.text_output.append(h)

    def update_progress(self, percent):
        """更新进度条"""
        self.process.setValue(percent)

    def on_download_error(self, error_msg):
        """下载错误处理"""
        h = QDateTime.currentDateTime()
        h = h.toString('yyyy-MM-dd hh:mm:ss ')
        h = h + '\n出错了喵～\n'
        self.text_output.append(h)

        self.page1_download_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.go_home.setEnabled(True)
        self.cleanup_thread()

    def cleanup_thread(self):
        """清理线程资源"""
        if self.download_thread:
            self.download_thread.quit()
            self.download_thread.wait()
            self.download_thread = None
            self.worker = None

    def stop_download(self):
        """停止下载"""
        if self.worker:
            self.worker.stop()
        self.cleanup_thread()
        self.page1_download_button.setEnabled(True)
        self.search_button.setEnabled(True)
        self.go_home.setEnabled(True)

    def closeEvent(self, event):
        """窗口关闭时确保线程停止"""
        self.stop_download()
        super().closeEvent(event)

    def on_download_finished(self, file_path):
        """下载完成处理"""
        download_path = self.put_path.text() + '/' + self.ep_name + 'ep' + self.page1_input.text() + '.ts'
        h = QDateTime.currentDateTime()
        h = h.toString('yyyy-MM-dd hh:mm:ss ')
        h = h + '\n下载完成喵：{}\n'.format(download_path)
        self.text_output.append(h)

        print(f"文件已下载到: {file_path}")
        self.page1_download_button.setEnabled(True)
        self.go_home.setEnabled(True)
        self.search_button.setEnabled(True)
        self.cleanup_thread()
