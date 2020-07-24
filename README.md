# Daliy Arxiv Paper Crawler

## Overview

This repo is a automation arxiv paper crawler.

## Setup
Please install package before start building this repo. 

If you had already build elasticsearch server. you can skip last step, just set config and run main.py.

* Install [docker CE (Comunity Edition)](https://docs.docker.com/install/)

* Set config.ini

```

you can add or remove category. 

parameter:
------------------------------------------------------

crawl_category  : specific crawl paper category.

default crawl arxiv category: 
['cs.AI', 'cs.IR', 'cs.CL', 'cs.LG', 'cs.SI', 'cs.CV']

min_sleep : random sleep min time setting.
max_sleep : random sleep max time setting.

------------------------------------------------------

es_host : elastisearch server host ip
es_port : elastisearch server port
es_index : specific es index, such as sql database
doc_type : specific index doc type.


------------------------------------------------------

schedule_time : scheduler jobs time. 


```


* build environment
```
docker-compose up
```


## Crawl results


![image](https://github.com/gen3111620/Arxiv_Paper_DaliyCrawler/blob/master/picture/es1.jpg)


![image](https://github.com/gen3111620//blob/master/picture/es2.jpg)

![image](https://github.com/gen3111620//blob/master/picture/es3.jpg)
