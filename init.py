import json

with open("server.json", mode="rt", encoding="utf-8") as f:
    conf = json.load(f)

with open("chrome_extension/background.js", mode="r+", encoding="utf-8") as f:
    data = f.read()

with open("chrome_extension/background.js", mode="w", encoding="utf-8") as f:
    data = data.replace("$host$", conf['recv_server']['host'])
    data = data.replace("$port$", str(conf['recv_server']['port']))
    f.write(data)
    f.flush()


with open("main/analysis_data.py", mode="r+", encoding="utf-8") as f:
    data = f.read()

with open("main/analysis_data.py", mode="w", encoding="utf-8") as f:
    data = data.replace("$host1$", conf["raw_url_db"]['host'])
    data = data.replace("$host2$", conf["query_db"]['host'])
    data = data.replace("$host3$", conf["query_to_url_db"]['host'])

    data = data.replace("$user1$", conf["raw_url_db"]['user'])
    data = data.replace("$user2$", conf["query_db"]['user'])
    data = data.replace("$user3$", conf["query_to_url_db"]['user'])

    data = data.replace("$passwd1$", conf["raw_url_db"]['passwd'])
    data = data.replace("$passwd2$", conf["query_db"]['passwd'])
    data = data.replace("$passwd3$", conf["query_to_url_db"]['passwd'])

    data = data.replace("$raw_url_db$", conf["raw_url_db"]['database'])
    data = data.replace("$query_db$", conf["query_db"]['database'])
    data = data.replace("$query_to_url_db$", conf["query_to_url_db"]['database'])
    f.write(data)
    f.flush()


with open("main/recv_data.py", mode="r+", encoding="utf-8") as f:
    data = f.read()

with open("main/recv_data.py", mode="w", encoding="utf-8") as f:
    data = data.replace("$host$", conf["recv_server"]['host'])
    data = data.replace('"$port$"', str(conf["recv_server"]['port']))
    data = data.replace("$db_host$", conf["raw_url_db"]['host'])
    data = data.replace("$user$", conf["raw_url_db"]['user'])
    data = data.replace("$passwd$", conf["raw_url_db"]['passwd'])
    data = data.replace("$raw_url_db$", conf["raw_url_db"]['database'])
    f.write(data)
    f.flush()


with open("main/recommend.py", mode="r+", encoding="utf-8") as f:
    data = f.read()

with open("main/recommend.py", mode="w", encoding="utf-8") as f:
    data = data.replace("$host2$", conf["query_db"]['host'])
    data = data.replace("$host3$", conf["query_to_url_db"]['host'])

    data = data.replace("$user2$", conf["query_db"]['user'])
    data = data.replace("$user3$", conf["query_to_url_db"]['user'])

    data = data.replace("$passwd2$", conf["query_db"]['passwd'])
    data = data.replace("$passwd3$", conf["query_to_url_db"]['passwd'])

    data = data.replace("$query_db$", conf["query_db"]['database'])
    data = data.replace("$query_to_url_db$", conf["query_to_url_db"]['database'])

    data = data.replace("$host$", conf["web_server"]['host'])
    data = data.replace('"$port$"', str(conf["web_server"]['port']))
    f.write(data)
    f.flush()