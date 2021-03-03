# -*- coding:utf-8 -*-
#  main开始
import datetime
import time
from logging import debug
import os,sys
import html
from os import getcwd
from requests import Session
from re import match,search, findall, DOTALL
from traceback import format_exc
import pyperclip
from PIL import Image
from functions_process import find_num_lib, replace_xml_win
from functions_requests import steal_library_header, get_library_html, download_pic
from vid_cache import VidCache
from function_db import my_db

sys.path.append(r'D:\work\Source\gitTest\autoSignIn')
from functions_networks import get_content, DEFAULT_PROXY

JPG_FILE_PATH = r'\\192.168.1.251\systemdata\jpg\temp'
WISH_LIST_FILE = 'wish.txt'

session = None
jav_url = 'http://www.b47w.com/ja/'
#jav_url = 'http://www.javlibrary.com/ja/'
search_keys = ['有码', '有碼','骑兵', '中文字幕→新片合集']
url = 'http://z3.xm1024p.biz/pw/thread.php?fid=83'
#url = 'https://k5.kcl20190711.rocks/pw/'
file_name = 'test' + time.strftime("%Y%m%d%H%M%S", time.localtime())  + '.txt'
start_page = 4
max_page_count = 4
max_get_count = 0 #测试用,0取全部
need_download_pic = True
header = {}

class mypage(object):
    def __init__(self):
        self.id = '' # id
        self.url = '' # url
        self.title = '' # title
        self.date = '' # date
        self.num_list = {}
        self.url_list = []

# 写文件
def write_file(file_name, level, msg):
    if file_name != None:
        with open(file_name, 'a+', encoding='utf-8') as f1:
            f1.write(datetime.datetime.now().isoformat() + ',' + level + ',' + msg + '\n')

# 取得车牌图片
def get_num_image(url, num, header, file_name = None, db = None, magnet_url = None):
    
    jpgfile = getcwd() +  '\\temp\\' + num + '.jpg'
    
    if os.path.exists(jpgfile):
        print('    >文件已经存在：' + num + '，\n')
        return
    title_get = None
    url_search_web = url + 'vl_searchbyid.php?keyword=' + num
    #print('url_search_web:' + url_search_web)
    html_web, header = get_library_html(url_search_web, header, DEFAULT_PROXY, url)
    titleg = search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_web)  # 匹配处理“标题”
    # 搜索结果就是AV的页面
    if titleg != None:
        title_get = titleg.group(1)
    else:   # 找“可能是多个结果的网页”上的所有“box”
        print(url)
        #print(html_web)
        list_search_results = findall(r'v=jav(.+?)" title="(.+?-\d+?[a-z]? .+?)"', html_web)     # 这个正则表达式可以忽略avop-00127bod，它是近几年重置的，信息冗余
        # 从这些搜索结果中，找到最正确的一个
        if list_search_results:
            # 默认用第一个搜索结果
            url_first_result = url + '?v=jav' + list_search_results[0][0]
            print(url)
            # 在javlibrary上搜索 SSNI-589 SNIS-459 这两个车牌，你就能看懂下面的if
            if len(list_search_results) > 1 and not list_search_results[1][1].endswith('ク）'):  # ク）是蓝光重置版
                # print(list_search_results)
                if list_search_results[0][1].endswith('ク）'):   # 排在第一个的是蓝光重置版，比如SSNI-589（ブルーレイディスク），它的封面不正常，跳过它
                    url_first_result = url + '?v=jav' + list_search_results[1][0]
                elif list_search_results[1][1].split(' ', 1)[0] == num:  # 不同的片，但车牌完全相同，比如id-020。警告用户，但默认用第一个结果。
                    print('    >警告！javlibrary搜索到同车牌的不同视频：' + num + '，\n')
                    write_file(file_name, 'Warning', '%s,javlibrary搜索到同车牌的不同视频' % num)
                # else: 还有一种情况，不同片，车牌也不同，但搜索到一堆，比如搜“AVOP-039”，还会得到“AVOP-390”，正确的肯定是第一个。
            # 打开这个jav在library上的网页
            print('    >获取信息：', url_first_result)
            html_web, header = get_library_html(url_first_result, header, DEFAULT_PROXY, url)
            # 找到标题，留着马上整理信息用
            title_get = search(r'<title>([A-Z].+?) - JAVLibrary</title>', html_web).group(1)
        # 第三种情况：搜索不到这部影片，搜索结果页面什么都没有
        else:
            print('    >失败！javlibrary找不到该车牌的信息：' + num + '，\n')
            write_file(file_name, 'Warning', '%s,javlibrary找不到该车牌的信息' % num)

    if (title_get != None):
        print('    >影片标题：', title_get)
        # 有大部分信息的html_web
        html_web = search(r'video_title"([\s\S]*?)favorite_edit', html_web, DOTALL).group(1)
        
        if db != None:
            # 发行日期
            premieredg = search(r'(\d\d\d\d-\d\d-\d\d)', html_web)
            if str(premieredg) != 'None':
                time_premiered = premieredg.group(1)
            else:
                time_premiered = '1970-01-01'
            print('    >发行年月日：', time_premiered)

            # 片长 <td><span class="text">150</span> 分钟</td>
            runtimeg = search(r'span class="text">(\d+?)</span>', html_web)
            if str(runtimeg) != 'None':
                runtime = runtimeg.group(1)
            else:
                runtime = '0'
            #print('    >片长：', runtime)

            # 导演
            directorg = search(r'director\.php.+?>(.+?)<', html_web)
            if str(directorg) != 'None':
                director = replace_xml_win(directorg.group(1))
            else:
                director = '有码导演'
            #print('    >导演：', director)

            # 片商 制作商
            studiog = search(r'maker\.php.+?>(.+?)<', html_web)
            if str(studiog) != 'None':
                studio = replace_xml_win(studiog.group(1))
            else:
                studio = ''
            #print('    >片商：', studio)

            # 演员们 和 # 第一个演员
            actors = findall(r'star\.php.+?>(.+?)<', html_web)
            if actors:
                actor = ','.join(actors)
            else:
                actor = '有码演员'
            #print('    >演员：', actor)

            # 特点
            genres = findall(r'category tag">(.+?)<', html_web)
            genre = ','.join(genres)
            #print('    >特点：', genre)

            # 评分
            scoreg = search(r'score">\((.+?)\)<', html_web)
            if str(scoreg) != 'None':
                float_score = float(scoreg.group(1))
                float_score = (float_score - 4) * 5 / 3     # javlibrary上稍微有人关注的影片评分都是6分以上（10分制），强行把它差距拉大
                if float_score >= 0:
                    score = '%.1f' % float_score
                else:
                    score = '0'
            else:
                score = '0'
            # 烂番茄评分 用上面的评分*10
            criticrating = str(float(score)*10)
            #print('    >评分：', criticrating)

            sql = 'INSERT INTO video (vid, title, actor, blurb, tag, mpaa, country, `release`, runtime, director, studio, rate, poster_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            db.execute(sql, (num, title_get, actor, '', genre, 'NC-17', '日本', time_premiered, runtime, director, studio, criticrating, magnet_url))

        # DVD封面cover
        coverg = search(r'src="(.+?)" width="600', html_web)  # 封面图片的正则对象
        if coverg != None:
            url_cover = coverg.group(1)
            if not url_cover.startswith('http'):
                url_cover = 'http:' + url_cover
            print('    >下载地址：', url_cover)
            try:
                download_pic(url_cover, getcwd() +  '\\temp\\' + num + '.jpg', DEFAULT_PROXY)
            except:
                print(sys.exc_info())

        else:
            url_cover = ''

        if db !=None:
            db.commit()

def run(url):

    print('脚本开始：')

    try:
        # db
        db = my_db()

        # 开始一个Session
        session = Session()

        # 取得http头信息
        header = steal_library_header(jav_url, DEFAULT_PROXY)

        # 打开主页
        rqs_content, url, cookies = get_content(url, session)
        #print(rqs_content)

        # 从主页中搜索链接
        url_for_search = search(r'<a href="(thread.php\?fid=\d)">最新合集</a>', rqs_content)

        if url_for_search == None:
            print('Warning:无法打开主页或无法取得列表页信息...')
            exit()
        else:
            # 取得需要访问的合集页列表
            search_list = []
            # 取得下载信息页列表
            bitpage_list = []
            # 需要查询的车牌
            bus_list = {}
            # 已经有的车牌
            getted_list = searchJpgFile(JPG_FILE_PATH)
            
            wish_list = get_wishlist()
            wish_list_magnet = []
            
            # 循环需要打开的页数
            for page_count in range(start_page, start_page - max_page_count, -1):
                # 打开指定页数的合集页列表页面
                print('读取第%d页信息...' % page_count)
                rqs_content, rqs_url, cookies = get_content(url + url_for_search.group(1) + '&page=' + str(page_count), session)
                #print(rqs_content)

                # 查找列表页面里所有合集页的地址
                url_for_titles = findall(r'<a href="(html_data/\d{1}/\d{4}/\d{7}.html)" id="a_ajax_(\d{7})">(.+?)</a>', rqs_content)

                if url_for_titles == None:
                    print('Warning:无法取得%d合集页信息...' % page_count)
                    exit()
                else:
                    # 循环找到合集页的URL
                    for title in url_for_titles:
                        # 提取日期，标题信息
                        title_info = search(r'.*?\[(\d{2}\.\d{2})\](.+)', title[2])
                        if title_info == None:
                            # 记录无法提取的标题
                            print('Warning:' + ' '.join(title))
                            write_file(file_name, 'Warning', ','.join(title) + ',无法提取日期，标题信息')
                        else:
                            temp_len = len(search_list)
                            title_date = title_info.group(1)
                            title_content = title_info.group(2)
                            #print(title_content)
                            for mykey in search_keys:
                                if title_content.find(mykey) >= 0:
                                    page = mypage()
                                    page.id = title[1]
                                    page.url = url + title[0]
                                    page.title = title_content
                                    page.date = title_date
                                    search_list.append(page)
                                    #print(page)
                                    break
                            if temp_len == len(search_list):
                                write_file(file_name, 'Warning', ','.join(title) + ',不包含需要读取的关键字')
                write_file(file_name, 'info', ',%s,第%d页共取得%d个链接，共读取了%d个合集链接' % (rqs_url, page_count, len(url_for_titles), len(search_list)))
            print('共有%d个合集页面需要搜索...' % len(search_list))

            # 循环所有提取出来需要访问的合集页
            for disp_page in search_list:
                temp_list = []
                print('打开合集页(%s)，查找下载页链接... ' % disp_page.title, end='')
                rqs_content, rqs_url, cookies = get_content(disp_page.url, session)
                torrent_url_list = findall(r'href="(https://((?!<).)+?/torrent/[A-Z0-9]+)"', rqs_content)
                if torrent_url_list == None:
                    print('Warning:当前页未找到链接...')
                for torrent_url in torrent_url_list:
                    print('*', end='', flush=True)
                    bitpage_list.append(torrent_url[0])
                    temp_list.append(torrent_url[0])
                disp_page.url_list = list(temp_list)
                print('当前页找到%d个链接' % len(torrent_url_list))
                write_file(file_name, 'info', ',%s,（%s）页面共找到（%d）个链接' % (disp_page.url, disp_page.title, len(disp_page.url_list)))

                #break #for debug

            print('循环所有的下载链接,共%d个链接' % len(bitpage_list))
            for disp_page in search_list:
                temp_numlist = {}
                print('处理合集页(%s)的(%d个)下载链接... ' % (disp_page.title, len(disp_page.url_list)), end='')
                for torrent_page in disp_page.url_list:
                    print('*', end='', flush=True)
                    # 记录所有下载页的url
                    # write_file(file_name, 'info', ',%s,%s,%s' % (torrent_page, disp_page.title, disp_page.url))
                    javnum, magnet_url = get_magnet(session, torrent_page, file_name)
                    if javnum == None:
                        continue
                    else:
                        if javnum in wish_list:
                            wish_list_magnet.append(magnet_url)
                        if (not bus_list.__contains__(javnum)) and (not getted_list.__contains__(javnum)):
                            bus_list[javnum] = magnet_url
                            temp_numlist[javnum] = magnet_url
                        else:
                            print('%s车牌已发车' % javnum)
                    # 测试用
                    if max_get_count != 0 and len(bus_list) >= max_get_count:
                        break
                    write_wishlist(wish_list_magnet)
                disp_page.num_list = dict(temp_numlist)
                print('')
            

            header = steal_library_header(jav_url, DEFAULT_PROXY)

            print('循环所有的车,共%d个' % len(bus_list))
            print(bus_list)
            count = 1
            for disp_page in search_list:
                print('处理合集页(%s)的(%d个)车牌... ' % (disp_page.title, len(disp_page.num_list)))
                for num, magnet_url in disp_page.num_list.items():
                    print('(' + str(count) + '/' + str(len(bus_list)) + ')' + str(num), end=',', flush=True)
                    count += 1
                    if need_download_pic:
                        get_num_image(jav_url, num, header, db = db, magnet_url = magnet_url)
                    write_file(file_name, 'info', '%s,%s,%s,%s' % (num, magnet_url, disp_page.title, disp_page.url))
            print('')

        db.close()

    except:
        print(sys.exc_info())
        print('Warning:打开网页失败，重新尝试...')

def get_magnet(session, url, file_name = None):
    rqs_content, rqs_url, cookies = get_content(url, session)
    magnet_url = search(r'href="(magnet:\?xt=urn:[a-z0-9]+:[A-Z0-9]+.*)"', rqs_content)
    if magnet_url == None:
        print('Warning:url:%s无法找到下载链接...' % url)
        write_file(file_name, 'Warning', '%s, 无法找到磁力链接' % url)
        return None, None
    else:
        jav = search(r'\&amp;dn=([a-zA-Z0-9\-\_\.]+)\&amp;', magnet_url.group(1))
        if jav == None:
            print('Warning:url:%s无法找到车牌...' % magnet_url.group(1))
            write_file(file_name, 'Warning', '%s, 无法找到车牌' % magnet_url.group(1))
            return None, None
        else:
            javnum = find_num_lib(jav.group(1).strip(), [])
            if (javnum == None) or (len(javnum) == 0):
                print('Warning:url:%s无法找到车牌...' % magnet_url.group(1))
                write_file(file_name, 'Warning', '%s, 无法解析车牌' % magnet_url.group(1))
                return None, None
            # temp_name = checkRedisKey(javnum)
            # if (temp_name == None):
                # print('%s车牌已发车' % javnum)
                # write_file(file_name, 'Warning', '%s, %s车牌已经发车' % (magnet_url.group(1), javnum))
            return javnum, html.unescape(magnet_url.group(1))
    return None, None

def searchJpgFile(root_choose):
    # jpg_list = []
    cache = VidCache()
    cache.add_jpgfile_dir(root_choose)
    #for root, dirs, files in os.walk(root_choose):
    #    if not files:
    #        continue
    #    for file_raw in files:
    #        if file_raw.endswith('.jpg'):
    #            #print(file_raw[:len(file_raw)-4])
    #            jpg_list.append(file_raw[:len(file_raw)-4])
    return cache.getlist()

def display_info():
    try:
        db = my_db()
        sql = '''
        SELECT vid, title, actor, tag, `release`, rate, poster_path FROM video WHERE vid LIKE '%%%%%s%%%%' ORDER BY vid
        '''
        while True:
            id = input('输入查询VID:')
            if (id.lower() == 'q'):
                break
            recoders = db.execute(sql % id.upper()).fetchall()
            result_dict = {}
            for (vid, title, actor, tag, release, rate, path) in recoders:
                result_dict[vid] = {'vid':vid, 'title':title, 'actor':actor, 'tag':tag, 'release':release, 'rate':rate, 'path':path}
            if (len(result_dict) == 0):
                print('没有找到数据')
            elif (len(result_dict) > 1):
                print_vinfo(result_dict)
                while True:
                    id = input('输入查询ID:')
                    if (id.lower() == 'q'):
                        break
                    else:
                        print_vinfo(result_dict, list(result_dict.keys())[int(id)-1])
            else:
                print_vinfo(result_dict, id.upper())
                
        db.close()
    except:
        print(format_exc())

def print_vinfo(result_dict, vid = None):
    if vid == None:
        count = 1
        for key,a in result_dict.items():
            print('%d). \t%s【%s】(%s)\t%2.1f' % (count, a['title'], a['actor'], a['release'], a['rate']))
            count += 1
    else:
        pic_path = ''
        print('%s【%s】(%s)\n\t%s\t%2.1f' % (result_dict[vid]['title'], result_dict[vid]['actor'], result_dict[vid]['release'], result_dict[vid]['tag'], result_dict[vid]['rate']))
        pic_path = result_dict[vid]['path']
        if (pic_path.find('magnet:?') == 0):
            pyperclip.copy(pic_path)
            pic_path = JPG_FILE_PATH + os.sep + vid + '.jpg'
        elif pic_path != '':
            pic_path = pic_path + os.sep + result_dict[vid]['title'] + '-fanart.jpg'
        id = input('显示图片？(y/n):')
        if (id.lower() == 'y'):
            print('图片:' + pic_path)
            pil_im = Image.open(pic_path)
            pil_im.show()

def get_wishlist():
    wish_list = []
    with open(WISH_LIST_FILE, 'r') as f1:
        wish_list = f1.readlines()
    for i in range(0, len(wish_list)):
        wish_list[i] = wish_list[i].rstrip('\n')
    return wish_list

def write_wishlist(wishlist):
    with open(WISH_LIST_FILE, 'a+', encoding='utf-8') as f1:
        f1.write('\n'.join(wishlist))    

if __name__ == "__main__":
    # print(sys.argv)
    if (len(sys.argv) > 1):
        cmd = sys.argv[1]
        if cmd == 'getimg':
            if (len(header) == 0):
                header = steal_library_header(jav_url, DEFAULT_PROXY)
            for i in range(2, len(sys.argv)):
                get_num_image(jav_url, sys.argv[i], header)
        elif cmd == 'getmagnet':
            for i in range(2, len(sys.argv)):
                print(get_magnet(None, sys.argv[i]))
        elif cmd == 'getmagnetwithimg':
            if (len(header) == 0):
                header = steal_library_header(jav_url, DEFAULT_PROXY)
            for i in range(2, len(sys.argv)):
                num, magnet_url = get_magnet(None, sys.argv[i])
                if num != None:
                    get_num_image(jav_url, num, header)
                    print(num, magnet_url)
        elif cmd == 'getlisted':
            print(searchJpgFile(JPG_FILE_PATH))
        elif cmd == 'page':
            if len(sys.argv) == 4:
                start_page = int(sys.argv[2])
                max_page_count = int(sys.argv[3])
                run(url)
        elif cmd == 'getinfo':
            display_info()
    else:
        run(url)