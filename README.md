# search_recommend

### About

> This project is used to analysis user's browser url and calculate the relevance between queries and links based on the obtained data.
> 
> Both the acquired raw data and the calculated data are stored in MySql.
> 
> Finally, create a simple search engine. In this search engine, the url with the highest similarity will be found according to the given query.

> The user's browser installs the **chrome_extension**, javascript sends the browser url data to the server through http requests, and the server processes and calculates the correlation between each query and the url, and finally finds the highest correlation for the new query through the http server. web pages, avoiding the secondary screening work required by the use of search engines

### How to start

- build the operating environment
  
  python3.6+
  
  `pip install mysql`

- create databases
  
  ```sql
  create database raw_url;
  use raw_url;
  create table raw_url(
      id int auto_increment not null primary key,
      uid varchar(10) not null,
      url varchar(1000) not null,
      time varchar(13) not null,
      is_processed tinyint default 0
  );
  create database query;
  use query;
  create table query(
      id int auto_increment not null primary key,
      query varchar(100) not null,
      update_time timestamp default now()
  ) character set utf8;
  create database query_to_url;
  ```

- create user for each database and grant all on database for user
  
  sample
  
  ```sql
  create user user@'%' identified by 'passwd';
  grant all on raw_url.* to user@'%';
  grant all on query.* to user@'%';
  grant all on query_to_url.* to user@'%';
  ```

- modify server.json
  
  recv_server is used to accept user data
  
  web_server is used to build a http server for the simple search engine
  
  `python init.py`

- start server
  
  `python recv_data.py`
  
  > to accept user data
  
  `python recommend.py`
  
  > to build a http server
  
  `python analysis_data.py`
  
  > process the raw data from user browser


