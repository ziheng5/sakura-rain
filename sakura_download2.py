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
