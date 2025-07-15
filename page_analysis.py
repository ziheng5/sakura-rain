import requests
import re


def get_ep_url(anime_index, headers):

    url = 'https://www.yhmv.cc/v/' + anime_index
    # url = 'https://www.yhmv.cc/v/456870/153'

    page = requests.get(url=url, headers=headers).text

    pattern0 = re.compile('a href="(.*?)" class="hide"')
    pattern1 = re.compile('<a class="swiper-slide">')
    title_pattern = re.compile('<h1 class="slide-info-title hide">(.*?)</h1>')
    ep_lis = re.findall(pattern0, page)
    route_lis = re.findall(pattern1, page)
    anime_title = re.findall(title_pattern, page)[0]

    num_ep = len(ep_lis) // len(route_lis)

    for i in range(num_ep):
        # 整合得到每一集的 url
        ep_lis[i] = 'https://www.yhmv.cc' + ep_lis[i]

    # print("该番共有{0}集".format(num_ep))
    return anime_title, ep_lis[:num_ep]

