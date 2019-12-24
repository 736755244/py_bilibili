# author: 墨染子柒
# date: 2019/12/24
import requests
from bs4 import BeautifulSoup
import time
import datetime
import random
import json
import pandas as pd
from urllib.parse import quote
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import csv

# 浏览器代理头
user_agent = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'
]

# 随机选取用户代理
def get_ua():
    au = random.choice(user_agent)
    return au

cok="buvid3=18CAA93F-09B8-4C84-A9AC-18D018939B4B48997infoc; LIVE_BUVID=AUTO1415545514726164; sid=adc30vha; CURRENT_FNVAL=16; rpdid=|(k|lmlJ~~Yk0J'ullY|uYu)u; im_notify_type_12785174=0; fts=1559281178; gr_user_id=cb4ec50c-5dbc-4f1f-96c5-bbdf17b4d62b; grwng_uid=50d021d4-37d9-48c1-a14f-19ac90b8fbe5; _ga=GA1.2.915253955.1563533793; _uuid=37E9E38A-9681-BDC1-2506-B5EFFC40169335351infoc; CURRENT_QUALITY=80; laboratory=1-1; hasstrong=2; stardustvideo=1; DedeUserID=12785174; DedeUserID__ckMd5=8504032bdc292fc1; SESSDATA=886176fc%2C1579067883%2C41dfe0c1; bili_jct=02619b6b62b303696be27c928e416e4c; bp_t_offset_12785174=335734075954987657; INTVER=1"

#  获取指定页码的视频列表
def get_vd_list(name,n):
    listUrl='https://api.bilibili.com/x/web-interface/search/type?context=&page={}&order=&keyword={}&duration=&tids_1=&tids_2=&__refresh__=true&search_type=video&highlight=1&single_column=0&jsonp=jsonp&callback=__jp8'
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        'Host': 'api.bilibili.com',
        'Connection': 'keep-alive',
        'Cookie': cok,
        'Referer': 'https://search.bilibili.com/all?keyword={}&from_source=nav_search&spm_id_from=333.851.b_696e7465726e6174696f6e616c486561646572.11'.format(quote(name))
    }
    res = requests.get(listUrl.format(n,quote(name)), headers=headers)
    res.encoding = 'utf-8'
    time.sleep(1)
    # 总页数
    totalpage = re.findall('"numPages":.*?,', res.text)[0]
    numPages = totalpage.split(':')[1].split(',')[0]
    # 当前页码
    curpage = re.findall('"page":.*?,', res.text)[0]
    page = curpage.split(':')[1].split(',')[0]
    # 视频页数
    print('视频共%s页'%numPages)
    print('当前是%s页' % page)
    #截取视频列表信息
    datalen=len(res.text)
    mydata = res.text[6:datalen-1]
    # 转josn格式
    jsonlist=json.loads(mydata)['data']['result']
    # 视频列表
    v_list =[]
    for i,v in enumerate(jsonlist):
        video_info = {}
        video_info['id'] = v['id']
        video_info['title'] = v['title'].replace('<em class="keyword">','').replace('</em>','')
        print('视频编号：%d  视频名称：%s'%(i+1,video_info['title']))
        v_list.append(video_info)
    return v_list

# 获取日期范围
def get_days(n):
    before_n_days = []
    for i in range(0, n)[::-1]:
        before_n_days.append(str(datetime.date.today() - datetime.timedelta(days=i)))
    return before_n_days

# 获取视频oid
def get_oid(id):
    headers = {
        'User-Agent':get_ua(),
        'Host': 'api.bilibili.com',
        'Connection': 'keep-alive',
        'Cookie':cok
    }
    getoid_url = 'https://api.bilibili.com/x/player/pagelist?aid={}&jsonp=jsonp'
    res = requests.get(getoid_url.format(id), headers=headers)
    video_info=json.loads(res.text)
    return video_info['data'][0]['cid']

# 根据日期范围获取评论
def get_dm_info(dmUrl):
    headers = {
        'User-Agent': get_ua(),
        'Host': 'api.bilibili.com',
        'Connection': 'keep-alive',
        'Cookie': cok
    }
    res = requests.get(dmUrl, headers=headers)
    if res.status_code == 200:
        print('*********爬取成功*******')
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    print("=============")
    print(soup)
    print('*********解析成功*******')
    # soup = BeautifulSoup(res.text.encode(res.encoding).decode('utf8'), 'lxml')
    return getText(soup)

# 解析网页
def getText(soup):
    result = soup.select('d')
    if len(result) == 0:
        return result
    all_list = []
    print(result)
    for item in result:
        info = item.get('p').split(",")
        info.append(item.string)
        info[4] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(info[4])))
        all_list.append(info)
    return all_list

# 生成词云
def get_wcloud(name):
    # 词云
    fp = open(r'%s.csv'%name, 'r', encoding='gbk').read()
    jieba.load_userdict('scel_to_text.txt')
    # jieba.add_word()  # 可以添加自定义词典
    # 将文件中所有文字分词
    words_list = jieba.lcut(fp)
    # 用空格分隔词语
    tokenstr = ' '.join(words_list)
    mywc1 = WordCloud().generate(tokenstr)
    # 显示词云
    plt.imshow(mywc1)
    plt.axis('off')
    plt.show()
    mywc1.to_file('%s.png'%name)  # 生成词云图片

    # 是否生成词频统计
    time.sleep(3)
    issum = input('是否生成词频统计(Y/N)?')
    if issum == 'Y':
        word_dict = {}
        # set:无序非重对象
        words_set = set(words_list)
        for w in words_set:
            # 高频词大于一个字的，当然这里可以自定义取值规则
            if len(w) > 1:
                word_dict[w] = words_list.count(w)
        words_sort = sorted(word_dict.items(), key=lambda x: x[1], reverse=True)
        # 输出词频TOP20
        words_sort1 = words_sort[:20]
        pd.DataFrame(data=words_sort1).to_csv('统计数据.csv', encoding='utf-8')

def main():
    video_name = input('请输入想查看的视频名称：')
    # 第一页视频列表
    v_list = get_vd_list(video_name,1)
    if len(v_list) == 0:
        print('暂未查找到视频资源')
        return
    else:
        # 视频id
        vid = int(input('请输入要爬取的视频编号：'))
        aid = v_list[vid - 1]['id']
        # 获取视频oid
        oid = get_oid(aid)
        # 文件名称
        file_name = "{}.csv".format(video_name)
        n = int(input('请输入要爬取的页数：'))
        tableheader = ['弹幕出现时间', '弹幕格式', '弹幕字体', '弹幕颜色', '弹幕时间戳', '弹幕池', '用户ID', 'rowID', '弹幕信息']

        with open(file_name, 'a', newline='', errors='ignore') as fd:
            writer = csv.writer(fd)
            writer.writerow(tableheader)
            for date in get_days(n):
                dmUrl = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid={}&date={}'.format(oid, date)
                final_list = get_dm_info(dmUrl)
                print(final_list)
                if final_list:
                    for row in final_list:
                        writer.writerow(row)
                del (final_list)
                time.sleep(random.random() * 5)
        print('准备生成词云统计')
        get_wcloud(video_name)


if __name__ == '__main__':
    main()