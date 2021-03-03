# -*- coding:utf-8 -*-
from os.path import exists
from os import sep, makedirs
from re import search
from configparser import RawConfigParser
from xml.etree.ElementTree import parse, ParseError
from shutil import copyfile


# 功能：得到有码车牌
# 参数：被大写后的视频文件名，素人车牌list
# 返回：发现的车牌
# 辅助：re.search
def find_num_lib(file_temp, list_suren_num):
    file_temp = file_temp.upper()
    if search(r'[^A-Z]?T28[-_ ]*\d\d+', file_temp):
        jav_pref = 'T-28'
        jav_suf = search(r'T28[-_ ]*(\d\d+)', file_temp).group(1)
    elif search(r'[^\d]?\d\dID[-_ ]*\d\d+', file_temp):
        video_numg = search(r'[^\d]?(\d\d)ID[-_ ]*(\d\d+)', file_temp)
        jav_pref = 'ID-' + video_numg.group(1)
        jav_suf = video_numg.group(2)
    elif search(r'[A-Z][A-Z]+[-_ ]*\d\d+', file_temp):
        video_numg = search(r'([A-Z][A-Z]+)[-_ ]*(\d\d+)', file_temp)
        jav_pref = video_numg.group(1)
        if jav_pref in list_suren_num or jav_pref in ['HEYZO', 'PONDO', 'CARIB', 'OKYOHOT']:
            return ''
        jav_pref = jav_pref + '-'
        jav_suf = video_numg.group(2)
    else:
        return ''
    # 去掉太多的0，avop00127
    if len(jav_suf) > 3:
        jav_suf = jav_suf[:-3].lstrip('0') + jav_suf[-3:]
    return jav_pref + jav_suf


# 功能：得到有码车牌
# 参数：被大写后的视频文件名，素人车牌list
# 返回：发现的车牌
# 辅助：re.search
def find_num_bus(file_temp, list_suren_num):
    if search(r'[^A-Z]?T28[-_ ]*\d\d+', file_temp):
        jav_pref = 'T28-'
        jav_suf = search(r'T28[-_ ]*(\d\d+)', file_temp).group(1)
    elif search(r'[^\d]?\d\dID[-_ ]*\d\d+', file_temp):
        video_numg = search(r'(\d\d)ID[-_ ]*(\d\d+)', file_temp)
        jav_pref = video_numg.group(1) + 'ID-'
        jav_suf = video_numg.group(2)
    elif search(r'[A-Z]+[-_ ]*\d\d+', file_temp):
        video_numg = search(r'([A-Z]+)[-_ ]*(\d\d+)', file_temp)
        jav_pref = video_numg.group(1)
        if jav_pref in list_suren_num or jav_pref in ['HEYZO', 'PONDO', 'CARIB', 'OKYOHOT']:
            return ''
        jav_pref = jav_pref + '-'
        jav_suf = video_numg.group(2)
    else:
        return ''
    # 去掉太多的0，avop00127
    if len(jav_suf) > 3:
        jav_suf = jav_suf[:-3].lstrip('0') + jav_suf[-3:]
    return jav_pref + jav_suf


# 功能：得到无码车牌
# 参数：被大写后的视频文件名，素人车牌list
# 返回：发现的车牌
# 辅助：re.search
def find_num_wuma(file_temp, list_suren_num):
    if search(r'[^A-Z]?N\d\d+', file_temp):
        jav_pref = 'N'
        jav_suf = search(r'N(\d\d+)', file_temp).group(1)
    elif search(r'\d+[-_ ]\d\d+', file_temp):
        video_numg = search(r'(\d+)[-_ ](\d\d+)', file_temp)
        jav_pref = video_numg.group(1) + '-'
        jav_suf = video_numg.group(2)
    elif search(r'[A-Z0-9]+[-_ ]?[A-Z0-9]+', file_temp):
        video_numg = search(r'([A-Z0-9]+)([-_ ]*)([A-Z0-9]+)', file_temp)
        jav_pref = video_numg.group(1)
        # print(jav_pref)
        if jav_pref in list_suren_num:
            return ''
        jav_pref = jav_pref + video_numg.group(2)
        jav_suf = video_numg.group(3)
    # elif search(r'[A-Z]+[-_ ]?\d+', file_temp):
    #     video_numg = search(r'([A-Z]+)([-_ ]?)(\d+)', file_temp)
    #     jav_pref = video_numg.group(1)
    #     if jav_pref in list_suren_num:
    #         return ''
    #     jav_pref = jav_pref + video_numg.group(2)
    #     jav_suf = video_numg.group(3)
    else:
        return ''
    # 去掉太多的0，avop00127
    # if len(jav_suf) > 3:
    #     jav_suf = jav_suf[:-3].lstrip('0') + jav_suf[-3:]
    return jav_pref + jav_suf


# 功能：得到素人车牌
# 参数：被大写后的视频文件名，素人车牌list
# 返回：发现的车牌
# 辅助：re.search
def find_num_suren(file_temp, list_suren_num):
    jav_numg = search(r'([A-Z][A-Z]+)[-_ ]*(\d\d+)', file_temp)  # 匹配字幕车牌
    if str(jav_numg) != 'None':
        jav_pref = jav_numg.group(1)
        if jav_pref not in list_suren_num and '三二一' not in file_temp:
            return ''
        jav_suf = jav_numg.group(2)
        # 去掉太多的0，avop00127
        if len(jav_suf) > 3:
            jav_suf = jav_suf[:-3].lstrip('0') + jav_suf[-3:]
        return jav_pref + '-' + jav_suf
    else:
        return ''


# 功能：根据“原文件名”“旧nfo”判断是否有“中字”/无码流出
# 参数：当前jav所处文件夹路径，jav文件名，判断文件名中的字词list, ‘中文字幕’/‘无码流出’
# 返回：True
# 辅助：os.path.exists，xml.etree.ElementTree.parse，xml.etree.ElementTree.ParseError
def check_subt_divulge(root, jav_name, list_subt_divulge, str_subt_divulge):  #
    # 原文件名包含“-c、-C、中字”这些字符
    name_no_cd = jav_name.upper().replace('-CD', '').replace('-CARIB', '')
    for i in list_subt_divulge:
        if i in name_no_cd:
            return True
    # 先前的nfo中的“标签”有 ‘中文字幕’/‘无码流出’
    path_nfo = root + sep + jav_name + '.nfo'
    if exists(path_nfo):
        try:
            tree = parse(path_nfo)
        except ParseError:  # nfo可能损坏
            return False
        for child in tree.getroot():
            if child.text == str_subt_divulge:
                return True
    return False


# 功能：为当前jav收集演员头像到“.actors”文件夹中
# 参数：可演员们list，jav当前所处文件夹路径
# 返回：无
# 辅助：os.path.exists，os.makedirs, configparser.RawConfigParser
def collect_sculpture(actors, root_now):
    for each_actor in actors:
        path_exist_actor = '演员头像' + sep + each_actor[0] + sep + each_actor  # 事先准备好的演员头像路径
        if exists(path_exist_actor + '.jpg'):
            pic_type = '.jpg'
        elif exists(path_exist_actor + '.png'):
            pic_type = '.png'
        else:
            config_actor = RawConfigParser()
            config_actor.read('【缺失的演员头像统计For Kodi】.ini', encoding='utf-8-sig')
            try:
                each_actor_times = config_actor.get('缺失的演员头像', each_actor)
                config_actor.set("缺失的演员头像", each_actor, str(int(each_actor_times) + 1))
            except:
                config_actor.set("缺失的演员头像", each_actor, '1')
            config_actor.write(open('【缺失的演员头像统计For Kodi】.ini', "w", encoding='utf-8-sig'))
            continue
        # 已经收录了这个演员头像
        root_dest_actor = root_now + sep + '.actors' + sep  # 头像的目标文件夹
        if not exists(root_dest_actor):
            makedirs(root_dest_actor)
        # 复制一份到“.actors”
        copyfile(path_exist_actor + pic_type, root_dest_actor + each_actor + pic_type)
        print('    >演员头像收集完成：', each_actor)


# 功能：去除xml文档不允许的特殊字符 &<>
# 参数：（文件名、简介、标题）str
# 返回：str
# 辅助：无
def replace_xml(name):
    # 替换xml中的不允许的特殊字符 .replace('\'', '&apos;').replace('\"', '&quot;')
    # .replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')  nfo基于xml，xml中不允许这5个字符，但实际测试nfo只不允许左边3个
    return name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                .replace('\n', '').replace('\t', '').replace('\r', '').rstrip()


# 功能：去除xml文档和windows路径不允许的特殊字符 &<>  \/:*?"<>|
# 参数：（文件名、简介、标题）str
# 返回：str
# 辅助：无
def replace_xml_win(name):
    # 替换windows路径不允许的特殊字符 \/:*?"<>|
    return name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')\
                .replace('\n', '').replace('\t', '').replace('\r', '')\
                .replace("\\", "#").replace("/", "#").replace(":", "：").replace("*", "#")\
                .replace("?", "？").replace("\"", "#").replace("|", "#").rstrip()