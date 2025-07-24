import requests
import re
import time
from PySide6.QtCore import QObject, Signal


class DownloadWorker(QObject):
    """
    下载工作线程，处理文件下载和进度更新
    """

    progress_updated = Signal(int)  # 下载进度百分比信号
    download_finished = Signal(str)  # 下载完成信号（返回文件路径）
    error_occurred = Signal(str)  # 错误信号

    def __init__(self, ep_url, path, ep_name, ep_index):
        super().__init__()
        self.ep_url = ep_url
        self.headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
                'Cookie': 'HWTOKEN=7d4e4f0a188bdc091c7b110582b3c02f3d524f6f61522e51f102fe191a4f864e1121a24925c15a758a27ee44a1554cffda875db4e62d4199f86fd1d4f8a45d3f; HWIDHASH=9299b36adfd65542d49a528d08c0c877; HWPID=EgyEb9-1UpWocy42ZYif2L7evaR1K1Ka5GMcXOLbl_E'
                }

        self.ts_headers = {
            'Referer': ep_url,
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Origin': 'https://jx.wujinkk.com',
            'Sec-Ch-Ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'Sec-Ch-Ua-Platform': '"Linux"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Priority': 'u=1, i',
            'authority': 'v.cdnlz22.com',
            'scheme': 'https'
        }
        self.path = path
        self.ep_name = ep_name
        self.ep_index = ep_index
        self._is_running = True

    def download(self):
        # ===================
        # 获取 mixed.m3u8 文件
        html = requests.get(url=self.ep_url, headers=self.headers).text
        pattern = re.compile("dplayer/\?url=(.*?)'")
        file_url = pattern.findall(html)[-1]

        index = requests.get(url=file_url, headers=self.headers).text
        processed_index = index.split('\n')[-1]
        processed_tail = processed_index.replace('mixed.m3u8', '')
        processed_file_url = file_url.replace('index.m3u8', processed_index)
        real_index = requests.get(url=processed_file_url, headers=self.headers).text
        num_lis = real_index.split('\n')
        processed_num_lis = [i for i in num_lis if '.ts' in i]
        print(processed_num_lis)

        video_length = len(processed_num_lis)

        base_url = file_url[:-10]
        full_video = b''
        for i in range(video_length):
            piece_url = base_url + processed_tail + processed_num_lis[i]
            print(piece_url)
            piece = requests.get(url=piece_url, headers=self.ts_headers).content
            full_video = full_video + piece
            processed = int(i / video_length * 100)
            self.progress_updated.emit(processed)


        download_path = self.path + '/' + self.ep_name + 'ep' + self.ep_index + '.ts'

        with open(download_path, 'wb') as f:
            f.write(full_video)
            f.close()

        self.download_finished.emit(self.path)

    def stop(self):
        """停止下载"""
        self._is_running = False


def get_episode(ep_url, headers, ep_name='video', directory='./'):
    """
    该函数用来下载指定的某一集
    :param ep_url:
    :param ep_name:
    :param directory:
    :return:
    """
    # 在此填入 url
    url = ep_url

    # 获取 index.m3u8 文件
    html = requests.get(url=url, headers=headers).text
    pattern = re.compile("dplayer/\?url=(.*?)'")
    file_url = pattern.findall(html)[-1]

    index = requests.get(url=file_url, headers=headers).text
    processed_index = index.split('\n')[-1]
    processed_file_url = file_url.replace('index.m3u8', processed_index)
    real_index = requests.get(url=processed_file_url, headers=headers).text
    num_lis = real_index.split('\n')
    processed_num_lis = [i for i in num_lis if '.ts' in i]

    video_length = len(processed_num_lis)

    base_url = file_url[:-10]
    full_video = b''
    for i in range(video_length):
        piece_url = base_url + processed_num_lis[i] + '.ts'
        piece = requests.get(url=piece_url, headers=headers).content
        full_video = full_video + piece
        print('Downloading: ', i/video_length)

    download_folder = directory + ep_name + '.ts'

    with open(download_folder, 'wb') as f:
        f.write(full_video)
        f.close()

    print('Done!')


