import requests
import re

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
    print(html)
    pattern = re.compile("dplayer/\?url=(.*?)'")
    file_url = pattern.findall(html)[-1]
    print(file_url)

    index = requests.get(url=file_url, headers=headers).text
    print(index)
    num_pattern = re.compile("00(.*?).ts")
    num_lis = num_pattern.findall(index)
    video_length = len(num_lis)

    base_url = file_url[:-10]
    full_video = b''
    for i in range(video_length):
        piece_url = base_url + '00' + num_lis[i] + '.ts'
        piece = requests.get(url=piece_url, headers=headers).content
        full_video = full_video + piece
        print('Downloading: ', i/video_length)

    download_folder = directory + ep_name + '.ts'

    with open(download_folder, 'wb') as f:
        f.write(full_video)
        f.close()

    print('Done!')
