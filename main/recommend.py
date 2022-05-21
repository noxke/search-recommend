import socket
import time
import os
import threading
from urllib.request import unquote, quote
import pymysql

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

def query_similarity(query1 : str = "", query2: str = "") -> float:
    '''计算两个query的相似度'''
    query1 = query1.lower()
    query2 = query2.lower()
    len1 = len(query1)
    len2 = len(query2)
    dp = [[0 for j in range(len1 + 1)] for i in range(len2 + 1)]
    for i in range(1, len2 + 1):
        for j in range(1, len1 + 1):
            if (query1[j - 1] == query2[i - 1]):
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    lcs_len = dp[-1][-1]
    if (len1 * len2 == 0):
        if (len1 == 0 and len2 == 0):
            return 1.0
        else:
            return 0
    return (lcs_len * lcs_len) / (len1 * len2)

def get_rel_url(query : str) -> tuple:
    '''
    查询与query相似度最高的url\n
    (url, relevance)
    '''
    cursor1 = query_db.cursor()
    cursor2 = query_url_db.cursor()
    sql1 = "select query, id from query;"
    query_list = []
    try:
        cursor1.execute(sql1)
        for data in cursor1.fetchall():
            query_list.append(data)
    except:
        log_msg("查询query列表失败", False)
    rel_query_index = []  # 储存相关度最高的三个query
    for q, index in query_list:
        rel = query_similarity(query, q)
        rel_query_index.append((rel, index))
        rel_query_index.sort(key=lambda x : x[0], reverse=True)
        if (len(rel_query_index) > 3):
            rel_query_index.pop()
    url = ""
    relevance = 0
    for rel, index in rel_query_index:
        sql2 = "select url, relevance from q{} order by relevance desc limit 1;".format(index)
        try:
            cursor2.execute(sql2)
            data = cursor2.fetchone()
            if (data == None):
                u = ""
                r = 0
            else:
                u, r = data
            if (r * rel > relevance):
                relevance = r * rel
                url = u
        except:
            log_msg("查询query: [{}]对应的url失败".format(index), False)
        url = unquote(url, encoding="utf8")
    return (url, "{:.02f}%".format(relevance * 100))

def response(conn, addr):
    data = conn.recv(1024)
    req = data.decode().split("\n")[0]
    req = req.split(" ")
    method = req[0]
    src = unquote(req[1], encoding="utf8")
    if (method == "GET"):
        reg_content = 'HTTP/1.x 200 ok\r\nContent-Type: text/html\r\n\r\n'
        try:
            if (src == "/"):
                reg_content += index_page
                conn.sendall(reg_content.encode())
            elif (src[0:4] == "/?q="):
                query = src[4:]
                reg_content += content_page
                url, relevance = get_rel_url(query)
                reg_content = reg_content.replace("$query$", query)
                reg_content = reg_content.replace("$url$", url)
                reg_content = reg_content.replace("$relevance$", relevance)
                conn.sendall(reg_content.encode())
                log_msg("query: [{}], url: [{}], relevance: [{}]".format(query, url, relevance))
        except:
            log_msg("错误的请求: [{}]".format(src), False)
    conn.close()

if __name__ == "__main__":
    db_host2 = "$host2$"
    db_host3 = "$host3$"
    query_db = pymysql.connect(host=db_host2, user="$user2$", passwd="$passwd2$", database="$query_db$")
    query_url_db = pymysql.connect(host=db_host3, user="$user3$", passwd="$passwd3$", database="$query_to_url_db$")

    with open("index.html", mode="rt", encoding="utf-8") as f:
        index_page = f.read()
    with open("content.html", mode="rt", encoding="utf-8") as f:
        content_page = f.read()

    host="$host$"
    port="$port$"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    try:
        while (True):
            conn, addr = server.accept()
            thread = threading.Thread(target=response, args=(conn, addr))
            thread.setDaemon(True)
            thread.start()
    except:
        server.close()
    query_db.close()
    query_url_db.close()