import socket
import time
import os
import threading
from urllib.request import unquote, quote
import pymysql

def log_data(data, status=True):
    '''记录数据'''
    os.system("")
    f = open("server.log", mode="a+", encoding="utf-8")
    f.write(time.strftime("[%Y-%m-%d %H:%M:%S] "))
    f.write(data['uid'] + " " + data['url'] + "\n")
    f.flush()
    f.close()
    if (status):
        print(time.strftime("\033[32m[%Y-%m-%d %H:%M:%S]\033[0m"), end=" ")
    else:
        print(time.strftime("\033[31m[%Y-%m-%d %H:%M:%S]\033[0m"), end=" ")
    print("\033[34m{}\033[0m".format(data['uid']), end=" ")
    print(data['url'])

def store_data(data, database):
    '''向sql数据库存储原始数据'''
    try:
        db = database
        cursor = db.cursor()
        # 数据库中储存编码后的url，防止出现特殊字符无法储存
        sql = "insert into raw_url(uid, time, url) values('{}', '{}', '{}')".format(data['uid'], data['time'], quote(data['url']))
        cursor.execute(sql)
        db.commit()
        return True
    except:
        db.rollback()
        return False

def recv(conn, addr, database):
    '''接受数据'''
    try:
        data = conn.recv(1024)
        req = data.decode().split("\n")[0]
        # 编码为utf-8
        req = unquote(req, encoding="utf-8")
        uid, utime, url = req.split(" ")[1:4]
        data = {"uid": uid[5:], "time": utime[6:], "url": url[5:]}
        if (store_data(data, database)):
            log_data(data)
        else:
            # 存储错误
            log_data(data, False)
    except:
        print(time.strftime("\033[31m[%Y-%m-%d %H:%M:%S]\033[0m"), end=" ")
        print("错误的连接")
        print(req)
    conn.close()

if __name__ == "__main__":
    host = "$host$"
    db_host = "$host$"
    port = "$port$"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))
    s.listen(5)
    database = pymysql.connect(host=db_host, user='$user$', passwd='$passwd$', database='$raw_url_db$')
    try:
        while (True):
            conn, addr = s.accept()
            thread = threading.Thread(target=recv, args=(conn, addr, database))
            thread.setDaemon(True)
            thread.start()
    except:
        s.close()
    database.close()