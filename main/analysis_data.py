import pymysql
from urllib.request import unquote, quote
import time
import math
import os

class Url():
    def __init__(self):
        self.engines = [self.__bing, self.__baidu, self.__google, self.__sogou, self.__bilibili, self.__csdn]

    def __bing(self, url):
        template = "https://cn.bing.com/search?q="
        if (url[0 : len(template)] == template):
            lindex = len(template)
            rindex = url.find("&")
            query = url[lindex: rindex]
            return (query, 'bing')
        return  None

    def __baidu(self, url):
        template = "https://www.baidu.com/s?wd="
        if (url[0 : len(template)] == template):
            lindex = len(template)
            rindex = url.find("&")
            query = url[lindex: rindex]
            return (query, 'baidu')
        return  None

    def __google(self, url):
        template = "https://www.google.com/search?q="
        if (url[0 : len(template)] == template):
            lindex = len(template)
            rindex = url.find("&")
            query = url[lindex: rindex]
            return (query, 'google')
        return  None

    def __sogou(self, url):
        template = "https://www.sogou.com/web?query="
        if (url[0 : len(template)] == template):
            lindex = len(template)
            rindex = url.find("&")
            query = url[lindex: rindex]
            return (query, 'sougou')
        return  None

    def __bilibili(self, url):
        template = "https://search.bilibili.com/all?keyword="
        if (url[0 : len(template)] == template):
            lindex = len(template)
            rindex = url.find("&")
            query = url[lindex: rindex]
            return (query, 'bilibili')
        return  None

    def __csdn(self, url):
        template = "https://so.csdn.net/so/search/s.do"
        if (url[0 : len(template)] == template):
            lindex = url.find("&q=")
            rindex = url.find("&t=&u=")
            query = url[lindex: rindex]
            return (query, 'csdn')
        return  None

def extract_query(url : str) -> tuple:
    '''
    从url中提取query并识别搜索引擎\n
    (query, engine) or None
    '''
    engines = Url().engines
    url = unquote(url, encoding="utf-8")
    for engine in engines:
        query = engine(url)
        if query != None:
            return query
        else:
            return None

def log_msg(msg : str, status=True):
    '''记录日志'''
    os.system("")
    f = open("server.log", mode="a+", encoding="utf-8")
    f.write(time.strftime("[%Y-%m-%d %H:%M:%S] ") + msg + "\n")
    f.flush()
    f.close()
    if (status):
        print(time.strftime("\033[32m[%Y-%m-%d %H:%M:%S]\033[0m"), end=" ")
    else:
        print(time.strftime("\033[31m[%Y-%m-%d %H:%M:%S]\033[0m"), end=" ")
    print(msg)

def get_uid() -> list:
    '''查询数据库中所有未处理的url的uid'''
    db = raw_url_db
    cursor = db.cursor()
    sql = "select uid from raw_url where is_processed = 0 order by id;"
    cursor.execute(sql)
    uid_list = []
    for uid in cursor.fetchall():
        uid = uid[0]
        if uid not in uid_list:
            uid_list.append(uid)
    return uid_list

def get_url(uid : str) -> list:
    '''
    根据传入的uid查询url, time以及其处理状态\n
    [url, time, is_processed]
    '''
    db = raw_url_db
    cursor = db.cursor()
    sql = "select url, time, is_processed from raw_url where uid = '{}' order by time".format(uid)
    cursor.execute(sql)
    url_list = []
    for data in cursor.fetchall():
        url_list.append((unquote(data[0], encoding="utf8"), int(data[1]), data[2]))
    return url_list

def get_query_id(query : str) -> int:
    '''查询query对应的id'''
    db = query_db
    cursor = db.cursor()
    sql = "select id from query where query = '{}'".format(query)
    try:
        cursor.execute(sql)
        qid = cursor.fetchone()
        if (qid != None):
            return qid[0]
        else:
            log_msg("未找到query: [{}]".format(query), False)
            return None
    except:
        log_msg("查找query: [{}]失败".format(query), False)
        return None

def update_query(query : str):
    '''储存query和创建相应的url表单'''
    if ("'" in query or "#" in query):
        log_msg("query: [{}] 不合法".format(query), False)
        return
    db1 = query_db
    db2 = query_url_db
    cursor1 = db1.cursor()
    cursor3 = db2.cursor()
    # 获取所有已记录的query
    sql = "select query from query order by id;"
    cursor1.execute(sql)
    query_list = []
    for q in cursor1.fetchall():
        query_list.append(q[0])
    if query not in query_list:
        # 获取目前最大的query编号，确定新插入的query的编号
        sql1 = "select max(id) from query;"
        cursor1.execute(sql1)
        index = cursor1.fetchall()[0][0]
        if (index == None):
            index = 1
        else:
            index = index + 1
        # 新插入一个query，为新的query创建相似表单和url表单
        sql2 = "insert into query(query) values('{}')".format(query)
        sql4 = "create table q{}(\
            url varchar(1000) not null,\
            relevance float default 0) character set utf8;".format(index)
        try:
            cursor1.execute(sql2)
            cursor3.execute(sql4)
            db1.commit()
            db2.commit()
            log_msg("插入一条query: [{}]".format(query))
        except:
            db1.rollback()
            db2.rollback()
            log_msg("插入query: [{}] 时发生错误".format(query), False)
    else:
        log_msg("query: [{}] 已存在".format(query), False)

def update_url(uid : str, utime : int) -> bool:
    '''更新url在raw_url中的处理状态'''
    db = raw_url_db
    cursor = db.cursor()
    sql = "update raw_url set is_processed = 1 where uid = '{}' and time = '{}'".format(uid, utime)
    try:
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        log_msg("raw_url数据状态更新失败: [{}, {}]".format(uid, utime), False)
        return False

def update_query_rel(query : str, url_list : list) -> bool:
    '''更新query与url的relevance'''
    db = query_url_db
    cursor = db.cursor()
    index = get_query_id(query)
    url_ls = []
    sql1 = "select url, relevance from q{};".format(index)
    try:
        cursor.execute(sql1)
        for url, relevance in cursor.fetchall():
            url_ls.append((unquote(url, encoding="utf8"), relevance))
    except:
        log_msg("查询query: [{}] 下的url记录失败".format(query), False)
    for url, relevance in url_list:
        tmp = url_ls
        for u, rel in tmp:
            if url == u:
                relevance = math.sqrt(relevance + rel - relevance * rel)
                url_ls.remove((u, rel))
        url_ls.append((url, relevance))
    url_ls.sort(key=lambda x : x[1], reverse=True)
    if (len(url_ls) > 5):
        url_ls = url_ls[0:5]
    sql2 = "delete from q{};".format(index)
    try:
        cursor.execute(sql2)
        db.commit()
    except:
        db.rollback()
        log_msg("删除query: [{}] 下的url记录失败".format(query), False)
    for url, relevance in url_ls:
        sql3 = "insert into q{}(url, relevance) values('{}', {});".format(index, quote(url), relevance)
        try:
            cursor.execute(sql3)
            db.commit()
        except:
            db.rollback()
            log_msg("更新query: [{}] 与url: [{}] 相关度失败".format(query, url), False)
            return False
    return True

def get_query_rel(query : str) -> list:
    '''
    查询已储存的与query相关的url\n
    [(url, relevance)...]
    '''
    db = query_url_db
    cursor = db.cursor()
    index = get_query_id(query)
    sql = "select url, relevance from q{};".format(index)
    try:
        cursor.execute(sql)
        ret = []
        for data in cursor.fetchall():
            ret.append((data[0], data[1]))
        return ret
    except:
        log_msg("查询query: [{}] 对应的相关url失败".format(query), False)
        return []

def official_web(url : str) -> str:
    '''获取一个url的官网'''
    try:
        ls = url.split('/')
        of_web = ls[0] + '/' + ls[1] + '/' + ls[2] + '/'
        return of_web
    except:
        return ""

def is_of_web(url : str) -> bool:
    '''判断url是否为官网url'''
    return url == official_web(url)

def is_video_web(url : str) -> bool:
    '''判断url是否为视频网站'''
    of_web = official_web(url)
    web_list = ["https://www.bilibili.com/"]
    for web in web_list:
        if (of_web == web):
            return True
    return False

def analysis_data(uid, url_list):
    '''对于每个uid的所有访问数据进行处理'''
    query_dict= {}  # {index : query}
    link_dict = {}  # {index : (time_dif, url)}
    for index, data in enumerate(url_list):
        url = data[0]
        query = extract_query(url)
        if (query != None):
            query_dict[index] = query[0]
            update_query(query[0])
        else:
            if (index + 1 >= len(url_list)):    # 数据表中最后一个数据，默认时间差为60秒
                time_dif = 60 * 1000
            else:
                time_dif = url_list[index + 1][1] - url_list[index][1]
            if (is_video_web(url)): # 视频网站降低时间差权重
                time_dif = time_dif / 1000
            link_dict[index] = time_dif

    # todo
    # 更新每个url和query之间的relevance
    query_index_ls = [i for i in query_dict]
    for k, index in enumerate(query_index_ls):
        query = query_dict[index]
        rel_dict = {}   # {index: relevance}
        rel_list = []   # [(index, relevance)]
        lr = {-3: 0, -2: 0.1, -1: 0.4, 0: 1, 1: 0.6, 2: 0.3, 3: 0}
        for i, time_dif in link_dict.items():
            url = url_list[i]
            rel = 0
            if (i < index): # url在query之前
                if (k == 0):
                    l = -1
                elif (i > query_index_ls[k - 1]):
                    l = -1
                else:
                    if (k - 1 == 0):
                        l = -2
                    elif (i > query_index_ls[k - 2]):
                        l = -2
                    else:
                        l = -3
            else:   # url位于query之后
                if (k == len(query_index_ls) - 1):
                    l = 0
                elif (k < query_index_ls[k + 1]):
                    l = 0
                else:
                    if (k + 1 == len(query_index_ls) - 1):
                        l = 1
                    elif (i < query_index_ls[k + 2]):
                        l = 1
                    else:
                        if (k + 2 == len(query_index_ls) - 1):
                            l = 2
                        elif (i < query_index_ls[k + 3]):
                            l = 2
                        else:
                            l = 3
            rel = lr[l] * (1 - math.pow(math.e, -0.00008 * time_dif))
            rel_dict[i] = rel

        if (k == len(query_index_ls) - 1):
                rindex = len(url_list) - 1
        else:
            rindex = query_index_ls[k + 1] - 1
        for i in range(index + 1, rindex + 1):
            rel = rel_dict[i]
            lindex = i + 1
            url = url_list[i][0]
            if (is_of_web(url)):
                of_web = official_web(url)
            else:
                of_web = ""
            for j in range(lindex, rindex + 1):
                rel2 = rel_dict[j]
                url2 = url_list[j][0]
                if (official_web(url2) == of_web):
                    rel = math.sqrt(rel + rel2 - rel * rel2)
                else:
                    if (rel2 <= 0.2):
                        wi = 1
                    elif (rel2 <= 0.4):
                        wi = 0.95
                    elif (rel2 <= 0.6):
                        wi = 0.9
                    elif (rel2 <= 0.8):
                        wi = 0.85
                    else:
                        wi = 0.8
                    rel = rel* wi
            rel_list.append((i, rel))

        # 将url按照相关性排序插入到对应的query表单中，只插入前五条
        rel_list.sort(key=lambda x : x[1], reverse=True)
        if (len(rel_list) > 5):
            rel_list = rel_list[0 : 5]
        url_ls = []
        for i, r in rel_list:
            url = url_list[i][0]
            url_ls.append((url, r))
        update_query_rel(query, url_ls)
        # if (query == "bilibili"):
        #     print(query, url_ls)
            # for data in url_list:
            #     url = data[0]
            #     print(url, is_video_web(url))
    # 将处理过的数据的is_processed全部标记为1
    for data in url_list:
        update_url(uid, data[1])


if __name__ == "__main__":
    host1 = "$host1$"
    host2 = "$host2$"
    host3 = "$host3$"
    user1 = "$user1$"
    user2 = "$user2$"
    user3 = "$user3$"
    passwd1 = "$passwd1$"
    passwd2 = "$passwd2$"
    passwd3 = "$passwd3$"
    raw_url_db = pymysql.connect(host=host1, user=user1, passwd=passwd1, database='$raw_url_db$')
    query_db = pymysql.connect(host=host2, user=user2, passwd=passwd2, database='$query_db$')
    query_url_db = pymysql.connect(host=host3, user=user3, passwd=passwd3, database='$query_to_url_db$')
    while (True):
        uid_list = get_uid()
        cnt = 0
        for uid in uid_list:
            url_list = get_url(uid)
            analysis_data(uid, url_list)
            cnt += len(url_list)
        log_msg("处理了: {} 条新的url".format(cnt))
        time.sleep(60)
    raw_url_db.close()
    query_db.close()
    query_url_db.close()